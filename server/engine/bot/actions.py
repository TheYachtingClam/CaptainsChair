"""The Bot's versions of the actions (CLAUDE.md "Bot actions"; requirements/22-solo-mode.md §6 to §12).

An Automated Command row receives a `BotActions` holding exactly the actions in its `uses` list, like card code. The
names match the CLAUDE.md action list; what they do follows the Bot rules: *gain* puts a card in the Bot Discard pile,
*take* puts it on top of the Bot deck, every choice picks by value, and so on. Parts that the human resolves (the bold
text on the card) ask the human through the usual Ask, so they pause and replay like any card operation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from engine import ops
from engine.content import MARKET_SUITS, content
from engine.ops import A, Actions, Ctx, Gen, UndeclaredActionError, raise_event, take_out
from engine.state import GameState, Inst, OpRef, Player

TRACKS = ("research", "influence", "military")  # the Bot's tie order: topmost first (REQ-SOLO-85)
SUITS = ("Person", "Cargo", "Ship", "Ally", "Encounter", "Incident", "Location", "Directive")


def _card(inst: Inst):
    return content().cards[inst.card]


def _name(inst: Inst) -> str:
    return _card(inst).name


def card_matches(inst: Inst, token: str) -> bool:
    """One term of a gain description: a suit, "[Research]" (a Skill icon, Any Skill included), "[Research Focus]" (a
    Focus icon, Best included) or a trait. Printed data only: the Bot ignores card text (REQ-SOLO-80)."""
    card = _card(inst)
    if token in SUITS:
        return card.suit == token
    if token == "Any Species excluding Human":
        from engine.ops import SPECIES

        return bool(set(card.traits) & (SPECIES - {"Human"}))
    if token.startswith("[") and token.endswith(" Focus]"):
        focus = token[1:-len(" Focus]")]
        return card.focus in (focus, "Best")
    if token.startswith("[") and token.endswith("]"):
        skill = token[1:-1]
        return skill in card.skills or "Any" in card.skills
    return token in card.traits or "Wildcard" in card.traits


def parse_wanted(text: str) -> list[list[str]]:
    """'A > B / C' as precedence groups: [['A'], ['B', 'C']]. '>' binds before '/' (REQ-SOLO-140 to -142)."""
    return [[term.strip() for term in group.split("/") if term.strip()] for group in text.split(">")]


class BotActions:
    """The actions an Automated Command row declared, and only those (CLAUDE.md "Card effects are code")."""

    def __init__(self, ctx: Ctx, uses: Iterable[str], this: Inst, resolve: Callable[[Inst], Gen]):
        self.ctx = ctx
        self.state: GameState = ctx.state
        self.bot: Player = ctx.me
        self.human: Player | None = ctx.opponent
        self.uses = set(uses)
        self.this = this  # "this card": the card being resolved (REQ-SOLO-86)
        self._resolve = resolve
        self.continued = False
        # Human-facing questions and the attack check reuse the ordinary actions, with the Bot as "me".
        self._ui = Actions(ctx, [A.ATTACK, A.FORCE])

    # ------------------------------------------------------------------ bookkeeping
    def _use(self, action: str) -> None:
        if action not in self.uses:
            raise UndeclaredActionError(f"Bot row for {_name(self.this)} did not declare {action}")

    def emit(self, text: str, **kw) -> None:
        self.state.emit(text, seat=self.bot.seat, **kw)

    @property
    def duty_officer(self) -> Inst | None:
        return self.bot.duty[0] if self.bot.duty else None

    def is_(self, suit: str) -> bool:
        """Whether this card has the suit, as printed (REQ-SOLO-80)."""
        return _card(self.this).suit == suit

    def track(self, name: str) -> int:
        return self.bot.tracks[name]

    # ------------------------------------------------------------------ the Bot deck (REQ-SOLO-60 to -62)
    def _top(self) -> Inst | None:
        from engine.bot import draw_card

        return draw_card(self.state, self.bot)

    def discard_top(self, n: int = 1) -> Gen:
        """Discard the top n cards of the Bot deck. Returns them."""
        self._use(A.DISCARD)
        out = []
        for _ in range(n):
            inst = self._top()
            if inst is None:
                break
            self.bot.discard.append(inst)
            out.append(inst)
            self.emit(f"{self.bot.name} discards {_name(inst)} from the top of its deck.", irreversible=True)
        return out
        yield  # pragma: no cover

    def discard_deck(self) -> Gen:
        """Discard the entire Bot deck; it reshuffles the next time the Bot needs a card (REQ-SOLO-60)."""
        self._use(A.DISCARD)
        n = len(self.bot.draw)
        self.bot.discard.extend(self.bot.draw)
        self.bot.draw = []
        self.emit(f"{self.bot.name} discards its entire deck ({n} cards).", irreversible=True)
        return
        yield  # pragma: no cover

    def peek_top(self) -> Gen:
        """Look at the top card of the Bot deck, reshuffling first if it is empty (REQ-SOLO-60). It stays there."""
        self._use(A.PEEK)
        from engine.game import cycle_deck

        if not self.bot.draw and not cycle_deck(self.state, self.bot):
            return None
        top = self.bot.draw[0]
        self.emit(f"The top card of {self.bot.name}'s deck is {_name(top)}.", irreversible=True)
        return top
        yield  # pragma: no cover

    def log_top(self, n: int = 1) -> Gen:
        """Log the top n cards of the Bot deck. An Incident is returned instead (REQ-SOLO-110); a Crew's special
        rule may discard some cards instead (Soval: Path of Surak; Freeman: Lower Decker)."""
        from engine.bot import LOG_TOP_DISCARDS

        self._use(A.LOG)
        spared = LOG_TOP_DISCARDS.get(self.bot.bot.crew, ())
        for _ in range(n):
            inst = self._top()
            if inst is None:
                break
            if any(t in _card(inst).traits for t in spared):
                self.bot.discard.append(inst)
                self.emit(f"{self.bot.name} discards {_name(inst)} instead of logging it (special rule).",
                          irreversible=True)
            else:
                self.emit(f"{self.bot.name} reveals {_name(inst)} from the top of its deck.", irreversible=True)
                self._log(inst)
        return
        yield  # pragma: no cover

    def resolve_top(self) -> Gen:
        """Resolve the top card of the Bot deck at once; it costs no Bot action (REQ-SOLO-100, -101)."""
        self._use(A.RESOLVE_CARD)
        inst = self._top()
        if inst is not None:
            yield from self._resolve_now(inst)

    def resolve_supplement_top(self) -> Gen:
        """Resolve the top card of the Supplement deck at once (REQ-SOLO-100)."""
        self._use(A.RESOLVE_CARD)
        if self.bot.reserve:
            inst = self.bot.reserve.pop(0)
            yield from self._resolve_now(inst)
            return inst
        return None

    def _resolve_now(self, inst: Inst) -> Gen:
        self.bot.staging.append(inst)
        self.emit(f"{self.bot.name} resolves {_name(inst)} at once.", irreversible=True)
        yield from self._resolve(inst)

    def _from_discard(self, token: str, pred: Callable[[Inst], bool] | None = None) -> Inst | None:
        """The topmost card of the Bot Discard pile matching `token` ("Cargo / Ship" allows either) (REQ-SOLO-96)."""
        terms = parse_wanted(token)[0]
        return next((i for i in reversed(self.bot.discard)
                     if any(card_matches(i, t) for t in terms) and (pred is None or pred(i))), None)

    def in_discard(self, token: str) -> bool:
        """Whether the Bot Discard pile has a matching card ("If a Helmet is in Bot Discard pile")."""
        return self._from_discard(token) is not None

    def return_incident_from_discard(self) -> Gen:
        """Return the topmost Incident of the Bot Discard pile, if able. Returns True if it did."""
        self._use(A.RETURN_INCIDENT)
        incident = self._from_discard("Incident")
        if incident is None:
            return False
        yield from self.return_incident(incident)
        return True

    def destroy(self, inst: Inst | None = None) -> Gen:
        """Return a card to the box."""
        self._use(A.DESTROY)
        inst = inst or self.this
        if ops.locate(self.state, inst.uid) is not None:
            take_out(self.state, inst)
            self.emit(f"{self.bot.name} destroys {_name(inst)}.")
        return
        yield  # pragma: no cover

    def resolve_from_discard(self, token: str) -> Gen:
        """Resolve the topmost matching card of the Bot Discard pile, if able (REQ-SOLO-96, -100). Returns it."""
        self._use(A.RESOLVE_CARD)
        inst = self._from_discard(token)
        if inst is None:
            return None
        self.bot.discard.remove(inst)
        yield from self._resolve_now(inst)
        return inst

    def promote_from_discard(self, token: str = "Person", pred: Callable[[Inst], bool] | None = None) -> Gen:
        """Promote the topmost matching Person of the Bot Discard pile, if able. Returns it."""
        inst = self._from_discard(token, lambda i: _card(i).suit == "Person" and (pred is None or pred(i)))
        if inst is None:
            self._use(A.PROMOTE)
            return None
        yield from self.promote(inst)
        return inst

    def deploy_from_discard(self) -> Gen:
        """Deploy the topmost Ship of the Bot Discard pile, if able. Returns it."""
        ship = self._from_discard("Ship")
        if ship is None:
            self._use(A.DEPLOY)
            return None
        yield from self.deploy(ship)
        return ship

    def log_from_discard(self, pred: Callable[[Inst], bool]) -> Gen:
        """Log the topmost matching card of the Bot Discard pile, if able. Returns it."""
        self._use(A.LOG)
        inst = next((i for i in reversed(self.bot.discard) if pred(i)), None)
        if inst is not None:
            self._log(inst)
        return inst
        yield  # pragma: no cover

    def log_deployed_ship(self) -> Gen:
        """Log a deployed Ship, if able: the most recently deployed (REQ-SOLO-166). Returns it."""
        self._use(A.LOG)
        ships = [s for s in self.bot.fleet if _card(s).suit == "Ship" or _card(s).ship_token]
        if not ships:
            return None
        self._log(ships[-1])
        return ships[-1]
        yield  # pragma: no cover

    def away_teams_on_board(self) -> int:
        return sum(loc.away.get(self.bot.seat, 0) for loc in [*self.state.neutral, *self.bot.locations])

    def can_log_location_and_remove_two(self) -> bool:
        """"If able to do both, log a controlled Location and remove 2 [Away Team]" (Directive rows)."""
        return bool(self.bot.locations) and self.away_teams_on_board() >= 2

    def log_controlled_location(self) -> Gen:
        """Log one of the Bot's controlled Locations: the least valuable to it, keeping the best in play."""
        self._use(A.LOG)
        from engine.bot import least_valuable

        loc = least_valuable(self.state, self.bot.locations, self.bot)
        if loc is not None:
            self._log(loc)
        return loc
        yield  # pragma: no cover

    def discard_supplement_top(self) -> Gen:
        self._use(A.DISCARD)
        if self.bot.reserve:
            inst = self.bot.reserve.pop(0)
            self.bot.discard.append(inst)
            self.emit(f"{self.bot.name} discards {_name(inst)} from the top of its Supplement deck.",
                      irreversible=True)
        return
        yield  # pragma: no cover

    def put_on_top(self, inst: Inst) -> Gen:
        self._use(A.PUT)
        take_out(self.state, inst)
        self.bot.draw.insert(0, inst)
        self.emit(f"{self.bot.name} puts {_name(inst)} on top of its deck.")
        return
        yield  # pragma: no cover

    def topmost_in_discard(self, suit_or_trait: str) -> Inst | None:
        """The most recently discarded matching card in the Bot Discard pile (REQ-SOLO-96)."""
        return next((i for i in reversed(self.bot.discard) if card_matches(i, suit_or_trait)), None)

    # ------------------------------------------------------------------ moving cards
    def _log(self, inst: Inst) -> None:
        """Log a card, returning an Incident instead (REQ-SOLO-110). Logging the Duty Officer flips SUITS back."""
        loose = ops.locate(self.state, inst.uid) is None  # taken off the top of the Bot deck
        if _card(inst).suit == "Incident":
            if not loose:
                take_out(self.state, inst)
            inst.res.clear()
            self.state.incident.append(inst)
            self.emit(f"{self.bot.name} returns {_name(inst)} to the Incident deck instead of logging it.")
            return
        if loose:
            self.bot.log.append(inst)
            self.emit(f"{self.bot.name} logs {_name(inst)}.")
            raise_event(self.state, "log", self.bot.seat, inst.uid, by=self.bot.seat)
            return
        was_officer = inst in self.bot.duty
        Actions(self.ctx, [A.LOG])._log(inst)
        if was_officer:
            self._flip_back()

    def log(self, inst: Inst | None = None) -> Gen:
        """Log this card, or another card (the Duty Officer, a controlled Location)."""
        self._use(A.LOG)
        inst = inst or self.this
        if ops.locate(self.state, inst.uid) is not None:
            self._log(inst)
        return
        yield  # pragma: no cover

    def log_duty_officer(self) -> Gen:
        self._use(A.LOG)
        if self.duty_officer is not None:
            self._log(self.duty_officer)
        return
        yield  # pragma: no cover

    def dismiss_duty_officer(self) -> Gen:
        """Dismiss the Bot's Duty Officer to its Discard pile and flip SUITS back (REQ-SOLO-93)."""
        self._use(A.DISMISS)
        officer = self.duty_officer
        if officer is not None:
            self.bot.duty.remove(officer)
            self.bot.discard.extend(officer.beamed)
            officer.beamed = []
            self.bot.discard.append(officer)
            self.emit(f"{self.bot.name} dismisses its Duty Officer, {_name(officer)}.")
            self._flip_back()
        return
        yield  # pragma: no cover

    def _flip_back(self) -> None:
        if not self.bot.duty and self.bot.bot.suits_side != "no_duty_officer":
            self.bot.bot.suits_side = "no_duty_officer"
            self.emit(f"{self.bot.name} flips its SUITS card to WITH NO DUTY OFFICER.")

    def promote(self, inst: Inst | None = None) -> Gen:
        """Promote a Person to the Bot's one Duty Officer slot; a previous one goes to the Bot Discard pile
        (REQ-SOLO-91, -92). Flips SUITS to WITH DUTY OFFICER."""
        self._use(A.PROMOTE)
        inst = inst or self.this
        if _card(inst).suit != "Person" or ops.locate(self.state, inst.uid) is None:
            return
        for old in list(self.bot.duty):
            self.bot.duty.remove(old)
            self.bot.discard.extend(old.beamed)
            old.beamed = []
            self.bot.discard.append(old)
            self.emit(f"{_name(old)} leaves duty for {self.bot.name}'s Discard pile.")
        take_out(self.state, inst)
        self.bot.duty.append(inst)
        self.emit(f"{self.bot.name} promotes {_name(inst)} to Duty Officer.")
        raise_event(self.state, "promote", self.bot.seat, inst.uid)
        if self.bot.bot.suits_side != "with_duty_officer":
            self.bot.bot.suits_side = "with_duty_officer"
            self.emit(f"{self.bot.name} flips its SUITS card to WITH DUTY OFFICER.")
        return
        yield  # pragma: no cover

    def return_incident(self, inst: Inst | None = None) -> Gen:
        """Return this card (an Incident) to the bottom of the Incident deck."""
        self._use(A.RETURN_INCIDENT)
        inst = inst or self.this
        if ops.locate(self.state, inst.uid) is not None:
            take_out(self.state, inst)
            inst.res.clear()
            self.state.incident.append(inst)
            self.emit(f"{self.bot.name} returns {_name(inst)} to the Incident deck.")
        return
        yield  # pragma: no cover

    # ------------------------------------------------------------------ gaining and taking (REQ-SOLO-140 to -149)
    def gain_card(self, wanted: str, *, take: bool = False, from_junk: bool = False, including_junk: bool = False,
                  label: str | None = None) -> Gen:
        """Gain (to the Bot Discard pile) or `take` (onto the Bot deck) the most valuable faceup card matching
        `wanted`, written as on the card: "Human > Person", "Scientist / Telepath > Ship > Ally". Nothing if no card
        matches ("if able"). Returns the card."""
        self._use(A.GAIN_CARD)
        from engine.bot import most_valuable

        market = [] if from_junk else [i for s in MARKET_SUITS if (i := self.state.market.get(s)) is not None]
        junk = list(reversed(self.state.junk)) if (from_junk or including_junk) else []  # most recent first
        pool = market + junk  # on a tie the Market card, then the most recent Junk card (REQ-SOLO-145, -146)
        chosen = None
        for group in parse_wanted(wanted):
            matching = [i for i in pool if any(card_matches(i, term) for term in group)]
            chosen = most_valuable(self.state, matching, self.bot)
            if chosen is not None:
                break
        if chosen is None:
            self.emit(f"{self.bot.name} finds no {label or wanted} to {'take' if take else 'gain'}.")
            return None
        return self._gain_exact(chosen, take=take)
        yield  # pragma: no cover

    def gain_most_glory(self) -> Gen:
        """Gain the Market card with the most [Glory] on it (Kirk). Ties: the most valuable, then the leftmost."""
        self._use(A.GAIN_CARD)
        from engine.bot import market_cards, most_valuable

        cards = market_cards(self.state)
        if not cards:
            return None
        most = max(i.res.get("glory", 0) for i in cards)
        target = most_valuable(self.state, [i for i in cards if i.res.get("glory", 0) == most], self.bot)
        return self._gain_exact(target)
        yield  # pragma: no cover

    def _gain_exact(self, chosen: Inst, *, take: bool = False) -> Inst:
        """Move a faceup Market or Junk card to the Bot: gained to its Discard pile, or taken onto its deck, with any
        tokens on it (REQ-SOLO-147, -149). The Market slot refills."""
        from engine.setup import refill_market

        suit = next((s for s, i in self.state.market.items() if i is chosen), None)
        if suit is not None:
            self.state.market[suit] = None
        else:
            self.state.junk.remove(chosen)
        for kind, n in sorted(chosen.res.items()):
            setattr(self.bot, kind, getattr(self.bot, kind) + n)
            self.emit(f"{self.bot.name} also gains {n} {kind.capitalize()} from {_name(chosen)}.")
        chosen.res.clear()
        if take:
            self.bot.draw.insert(0, chosen)
        else:
            self.bot.discard.append(chosen)
        where = "onto its deck" if take else "to its Discard pile"
        self.emit(f"{self.bot.name} {'takes' if take else 'gains'} {_name(chosen)} {where}.", irreversible=True)
        raise_event(self.state, "gain", self.bot.seat, chosen.uid, to="top" if take else "discard")
        if suit is not None:
            refill_market(self.state, suit)
        return chosen

    def gain_resources_from_market(self) -> Gen:
        """Gain all resources from a Market card: the one with the most, then the leftmost (Archer's Attack row)."""
        self._use(A.GAIN_RESOURCE)
        from engine.bot import market_cards

        cards = [i for i in market_cards(self.state) if i.res]
        if not cards:
            self.emit("No Market card has resources.")
            return None
        target = max(cards, key=lambda i: (sum(i.res.values()), -cards.index(i)))
        for kind, n in sorted(target.res.items()):
            setattr(self.bot, kind, getattr(self.bot, kind) + n)
            self.emit(f"{self.bot.name} gains {n} {kind.capitalize()} from {_name(target)}.")
        target.res.clear()
        return target
        yield  # pragma: no cover

    def gain_top_of_deck(self, suit: str) -> Gen:
        """Gain the top card of a Market deck, unseen (REQ-SOLO-144: only when a row says so)."""
        self._use(A.GAIN_CARD)
        deck = self.state.market_decks.get(suit) or []
        if not deck:
            self.emit(f"The {suit} deck is empty.")
            return None
        inst = deck.pop(0)
        self.bot.discard.append(inst)
        self.emit(f"{self.bot.name} gains {_name(inst)} from the top of the {suit} deck.", irreversible=True)
        raise_event(self.state, "gain", self.bot.seat, inst.uid, to="discard")
        return inst
        yield  # pragma: no cover

    def gain_incident(self) -> Gen:
        """A row that *gains* an Incident puts it in the Bot Discard pile (REQ-SOLO-147)."""
        self._use(A.TAKE_INCIDENT)
        yield from self._incident(to_deck=False)

    def take_incident(self) -> Gen:
        """*Take* an Incident: onto the Bot deck (REQ-SOLO-147)."""
        self._use(A.TAKE_INCIDENT)
        yield from self._incident(to_deck=True)

    def _incident(self, *, to_deck: bool) -> Gen:
        from engine.game import burn

        if not self.state.incident:
            burn(self.state)
            return None
        inst = self.state.incident.pop(0)
        if to_deck:
            self.bot.draw.insert(0, inst)
        else:
            self.bot.discard.append(inst)
        self.emit(f"{self.bot.name} {'takes' if to_deck else 'gains'} an Incident, {_name(inst)}.", irreversible=True)
        raise_event(self.state, "take_incident", self.bot.seat, inst.uid)
        if not self.state.incident:
            burn(self.state)
        return inst
        yield  # pragma: no cover

    def take_encounter(self, *, gain: bool = False) -> Gen:
        """Take the top Encounter onto the Bot deck, or `gain` it to the Bot Discard pile (REQ-SOLO-147)."""
        self._use(A.TAKE_ENCOUNTER)
        if self.state.encounter:
            inst = self.state.encounter.pop(0)
            if gain:
                self.bot.discard.append(inst)
                self.emit(f"{self.bot.name} gains the Encounter {_name(inst)} to its Discard pile.", irreversible=True)
            else:
                self.bot.draw.insert(0, inst)
                self.emit(f"{self.bot.name} takes the Encounter {_name(inst)} onto its deck.", irreversible=True)
        return
        yield  # pragma: no cover

    def junk(self) -> Gen:
        """Junk the Market card most valuable to the human, ignoring cards with tokens (REQ-SOLO-150)."""
        self._use(A.JUNK)
        from engine.bot import market_cards, most_valuable
        from engine.setup import refill_market

        if self.human is None:
            return
        target = most_valuable(self.state, [i for i in market_cards(self.state) if not i.res], self.human)
        if target is None:
            return
        suit = next(s for s, i in self.state.market.items() if i is target)
        self.state.market[suit] = None
        self.state.junk.append(target)
        self.emit(f"{self.bot.name} junks {_name(target)}, the Market card most valuable to {self.human.name}.")
        refill_market(self.state, suit)
        return
        yield  # pragma: no cover

    # ------------------------------------------------------------------ resources and tracks
    def gain_glory(self, n: int = 1, *, supply: bool = False) -> Gen:
        """Glory from the Stardate card, or the supply after a Resolution (REQ-SOLO-151); `supply=True` is Glory
        "from the supply", which never touches the Stardate card."""
        self._use(A.GAIN_RESOURCE)
        from engine.game import gain_glory

        if supply:
            self.bot.glory += n
        else:
            gain_glory(self.state, self.bot, n)
        self.emit(f"{self.bot.name} gains {n} Glory{' from the supply' if supply else ''}.")
        return
        yield  # pragma: no cover

    def gain_specialty(self, track: str, n: int = 1) -> Gen:
        self._use(A.GAIN_SPECIALTY)
        yield from Actions(self.ctx, [A.GAIN_SPECIALTY]).gain_specialty(track, n)

    def gain_lowest(self, *tracks: str, n: int = 1) -> Gen:
        """Gain on whichever of the tracks is lowest; ties go to the topmost (REQ-SOLO-85)."""
        tracks = tracks or TRACKS
        yield from self.gain_specialty(min(tracks, key=lambda t: (self.track(t), TRACKS.index(t))), n)

    def gain_highest(self, *tracks: str, n: int = 1) -> Gen:
        tracks = tracks or TRACKS
        yield from self.gain_specialty(min(tracks, key=lambda t: (-self.track(t), TRACKS.index(t))), n)

    # ------------------------------------------------------------------ the Neutral Zone (REQ-SOLO-160 to -170)
    def _tokens(self, loc: Inst, player: Player | None) -> int:
        from engine.game import tokens_at

        return tokens_at(self.state, loc, player.seat) if player is not None else 0

    def _more_than_enough(self, loc: Inst) -> bool:
        """REQ-SOLO-161, -162: 4 or more Bot tokens and 3 or more ahead of the human."""
        mine, theirs = self._tokens(loc, self.bot), self._tokens(loc, self.human)
        return mine >= 4 and mine - theirs >= 3

    def _pick_location(self, locations: list[Inst], key: Callable[[Inst], int]) -> Inst | None:
        """The Location with the highest key; ties go to the one most valuable to the Bot."""
        from engine.bot import value

        if not locations:
            return None
        return max(locations, key=lambda loc: (key(loc), value(self.state, loc, self.bot), -locations.index(loc)))

    def deploy(self, ship: Inst | None = None) -> Gen:
        """Move a Ship card to the Control Area, its token on the card; deployment order is kept (REQ-SOLO-163)."""
        self._use(A.DEPLOY)
        ship = ship or self.this
        take_out(self.state, ship)
        ship.at = None
        self.bot.fleet.append(ship)
        self.emit(f"{self.bot.name} deploys {_name(ship)}.")
        raise_event(self.state, "deploy", self.bot.seat, ship.uid)
        return
        yield  # pragma: no cover

    def _warp(self, ship: Inst, loc: Inst | None, how: str) -> None:
        if loc is None:
            self.emit(f"{_name(ship)} has nowhere to {how}.")
            return
        ship.at = loc.uid
        self.emit(f"{_name(ship)} {how}s to {_name(loc)}.")
        raise_event(self.state, "warp", self.bot.seat, ship.uid, location=loc.uid)

    def _warp_targets(self) -> list[Inst]:
        return [loc for loc in self.state.neutral if not self._more_than_enough(loc)]

    def explore(self, ship: Inst | None = None) -> Gen:
        """Warp to the neutral Location with the fewest tokens, preferring empty ones (REQ-SOLO-164)."""
        self._use(A.EXPLORE)
        ship = ship or self.this
        total = lambda loc: self._tokens(loc, self.bot) + self._tokens(loc, self.human)  # noqa: E731
        self._warp(ship, self._pick_location(self._warp_targets(), lambda loc: -total(loc)), "explore")
        return
        yield  # pragma: no cover

    def engage(self, ship: Inst | None = None) -> Gen:
        """Warp to the neutral Location where the human has the most tokens (REQ-SOLO-164)."""
        self._use(A.ENGAGE)
        ship = ship or self.this
        self._warp(ship, self._pick_location(self._warp_targets(), lambda loc: self._tokens(loc, self.human)),
                   "engage")
        return
        yield  # pragma: no cover

    def _ships(self, loc: Inst, player: Player | None) -> int:
        from engine import cards as registry

        if player is None:
            return 0
        return sum(registry.SHIP_WEIGHT.get(s.card, 1) for s in player.fleet if s.at == loc.uid)

    def can_send_to(self, loc: Inst, *, ignore_ships: bool = False) -> bool:
        """Neutral, not where the human has more Ships unless told to ignore them (REQ-SOLO-168), and not already
        more than enough (REQ-SOLO-161)."""
        return (loc in self.state.neutral and not self._more_than_enough(loc)
                and (ignore_ships or self._ships(loc, self.human) <= self._ships(loc, self.bot)))

    def send_away_team(self, prefer: str | None = None, *, target: Inst | None = None, ignore_ships: bool = False,
                       where: Callable[[Inst], bool] | None = None) -> Gen:
        """Send an Away Team to the neutral Location where the Bot has the most tokens; a trait preference such as
        "Xindi / Tellarite" comes first; ties go to the most valuable (REQ-SOLO-167 to -170). Returns the Location,
        or None if it could not."""
        self._use(A.SEND_AWAY_TEAM)
        if target is not None:
            loc = target if self.can_send_to(target, ignore_ships=ignore_ships) else None
        else:
            choices = [loc for loc in self.state.neutral
                       if self.can_send_to(loc, ignore_ships=ignore_ships) and (where is None or where(loc))]
            if prefer:
                # "Xindi / Tellarite" allows only those; "Xindi / Tellarite > Location" prefers them, else any.
                picked: list[Inst] = []
                for group in parse_wanted(prefer):
                    picked = choices if group == ["Location"] else [
                        loc for loc in choices if any(card_matches(loc, term) for term in group)]
                    if picked:
                        break
                choices = picked
            loc = self._pick_location(choices, lambda loc: self._tokens(loc, self.bot))
        if loc is None:
            self.emit(f"{self.bot.name} cannot send an Away Team there.")
            return None
        if self.bot.away_pool <= 0 and not self._recover_away_team(exclude=loc):
            self.emit(f"{self.bot.name} has no Away Team to send.")
            return None
        self.bot.away_pool -= 1
        loc.away[self.bot.seat] = loc.away.get(self.bot.seat, 0) + 1
        self.emit(f"{self.bot.name} sends an Away Team to {_name(loc)}.")
        raise_event(self.state, "send_away_team", self.bot.seat, loc.uid, location=loc.uid, controlled=False,
                    neutral=True)
        return loc
        yield  # pragma: no cover

    def _recover_away_team(self, exclude: Inst | None = None) -> bool:
        """With none on its Captain, the Bot takes an Away Team from the Location where it has the fewest tokens;
        ties go to the least valuable one (REQ-SOLO-170)."""
        from engine.bot import value

        places = [loc for loc in [*self.state.neutral, *self.bot.locations]
                  if loc.away.get(self.bot.seat) and loc is not exclude]
        if not places:
            return False
        source = min(places, key=lambda loc: (self._tokens(loc, self.bot), value(self.state, loc, self.bot),
                                               places.index(loc)))
        source.away[self.bot.seat] -= 1
        if not source.away[self.bot.seat]:
            del source.away[self.bot.seat]
        self.bot.away_pool += 1
        self.emit(f"{self.bot.name} takes back an Away Team from {_name(source)}.")
        return True

    def add_away_team(self, maximum: int = 6) -> Gen:
        """Add an Away Team from the supply to the Bot Captain, up to `maximum` in all (Archer). Returns True if
        added."""
        self._use(A.ADD_AWAY_TEAM)
        total = self.bot.away_pool + self.away_teams_on_board()
        if total >= maximum:
            self.emit(f"{self.bot.name} already has {maximum} Away Teams.")
            return False
        self.bot.away_pool += 1
        self.emit(f"{self.bot.name} adds an Away Team from the supply to its Captain.")
        return True
        yield  # pragma: no cover

    def remove_away_team(self, n: int = 1) -> Gen:
        """Remove the Bot's own Away Teams: from where it has the fewest tokens (REQ-SOLO-170)."""
        self._use(A.REMOVE_AWAY_TEAM)
        removed = 0
        for _ in range(n):
            if not self._recover_away_team():
                break
            removed += 1
        return removed
        yield  # pragma: no cover

    def take_control(self, loc: Inst) -> Gen:
        """Take control of a neutral Location, then resolve it with the Automated Command cards (REQ-SOLO-52)."""
        self._use(A.TAKE_CONTROL)
        from engine.game import take_control

        take_control(self.state, self.bot, loc, run_control=False)
        yield from self._resolve(loc)

    # ------------------------------------------------------------------ the human's part (REQ-SOLO-180 to -185)
    def attack(self, *, removes_away_teams: bool = False) -> Gen:
        """The bold red parts are an attack on the human: their "when attacked" Reactions apply (REQ-SOLO-182).
        Returns False when the human cancelled it; only the red parts are skipped (REQ-SOLO-184)."""
        self._use(A.ATTACK)
        if self.human is None:
            return False
        return (yield from self._ui.attack(removes_away_teams=removes_away_teams))

    def human_removes_away_team(self, where: Callable[[Inst], bool]) -> Gen:
        """Attack part "You remove an [Away Team] ...": the human picks which (REQ-SOLO-183). Returns the Location, or
        None if they had none there."""
        self._use(A.REMOVE_AWAY_TEAM)
        human = self.human
        if human is None:
            return None
        places = [loc for loc in [*self.state.neutral, *human.locations] if loc.away.get(human.seat) and where(loc)]
        loc = yield from self._ui.pick_card("Remove one of your Away Teams (Bot attack). From which Location?",
                                            places, seat=human.seat)
        if loc is None:
            self.emit(f"{human.name} has no Away Team to remove.")
            return None
        loc.away[human.seat] -= 1
        if not loc.away[human.seat]:
            del loc.away[human.seat]
        human.away_pool += 1
        self.state.emit(f"{human.name} removes an Away Team from {_name(loc)}.", seat=human.seat)
        return loc

    def _human_actions(self, *uses: str) -> Actions:
        """Actions for a bold part the human resolves themselves, as if it were their own effect."""
        return Actions(Ctx(self.state, OpRef(mode="auto", seat=self.human.seat)), uses)

    def human_discards(self) -> Gen:
        """Bold "you discard a card": the human discards a card of their choice."""
        self._use(A.DISCARD)
        if self.human is not None and self.human.hand:
            yield from self._human_actions(A.DISCARD).discard(1, label="a card (Bot attack)")

    def human_dismisses_duty_officer(self) -> Gen:
        """Bold "you dismiss a Duty Officer": the human picks one of theirs. Returns True if they could."""
        self._use(A.DISMISS)
        human = self.human
        if human is None or not human.duty:
            return False
        officer = yield from self._ui.pick_card("Dismiss one of your Duty Officers (Bot attack).", list(human.duty),
                                                seat=human.seat)
        self._human_actions(A.DISMISS)._dismiss(officer)
        return True

    def human_takes_incident(self) -> Gen:
        """Bold "you take an Incident"."""
        self._use(A.TAKE_INCIDENT)
        from engine.game import take_incident

        if self.human is not None:
            take_incident(self.state, self.human)
        return
        yield  # pragma: no cover

    def human_removes_all_away_teams(self, where: Callable[[Inst], bool]) -> Gen:
        """Bold "you remove all your [Away Team] from a Location ...": the human picks the Location. Returns it, or
        None if they had no Away Team at any such Location."""
        self._use(A.REMOVE_AWAY_TEAM)
        human = self.human
        if human is None:
            return None
        places = [loc for loc in self.state.neutral if loc.away.get(human.seat) and where(loc)]
        loc = yield from self._ui.pick_card("Remove all your Away Teams from which Location (Bot attack)?", places,
                                            seat=human.seat)
        if loc is None:
            return None
        n = loc.away.pop(human.seat)
        human.away_pool += n
        self.state.emit(f"{human.name} removes {n} Away Team(s) from {_name(loc)}.", seat=human.seat)
        return loc

    def human_exhausts_location(self) -> Gen:
        """Bold "you exhaust a controlled Location": the human picks one of their ready Locations."""
        self._use(A.EXHAUST)
        human = self.human
        if human is None:
            return None
        ready = [loc for loc in human.locations if not loc.exhausted]
        loc = yield from self._ui.pick_card("Exhaust one of your controlled Locations (Bot attack).", ready,
                                            seat=human.seat)
        if loc is not None:
            yield from self._human_actions(A.EXHAUST).exhaust(loc)
        return loc

    def human_dismisses_ship_or_takes_incident(self) -> Gen:
        """Bold "you either dismiss one of [your Ships at a neutral Location] OR take an Incident" (Riker): the human
        chooses (REQ-SOLO-183)."""
        self._use(A.DISMISS)
        self._use(A.TAKE_INCIDENT)
        from engine.game import take_incident

        human = self.human
        if human is None:
            return
        neutral = {loc.uid for loc in self.state.neutral}
        ships = [s for s in human.fleet if s.at in neutral]
        choice = yield from self._ui.choose("The Bot attacks: dismiss one of your Ships at a neutral Location, or take "
                                            "an Incident?", [("dismiss", "Dismiss a Ship"), ("incident", "Take an Incident")],
                                            human.seat)
        if choice == "dismiss" and ships:
            ship = yield from self._ui.pick_card("Dismiss which Ship?", ships, seat=human.seat)
            self._human_actions(A.DISMISS)._dismiss(ship)
        else:
            take_incident(self.state, human)

    def human_logs_ship(self) -> Gen:
        """Bold "you log a Ship either from your hand, Discard pile, or in play" (Rebner): the human picks."""
        self._use(A.LOG)
        human = self.human
        if human is None:
            return None
        hctx = Ctx(self.state, OpRef(mode="auto", seat=human.seat))
        ships = [i for i in human.hand + human.discard + hctx.in_play() if card_matches(i, "Ship")]
        ship = yield from self._ui.pick_card("Log one of your Ships (Bot attack).", ships, seat=human.seat)
        if ship is not None:
            self._human_actions(A.LOG)._log(ship)
        return ship

    def human_ships(self) -> list[Inst]:
        """The human's Ships in their hand, Discard pile or play."""
        if self.human is None:
            return []
        hctx = Ctx(self.state, OpRef(mode="auto", seat=self.human.seat))
        return [i for i in self.human.hand + self.human.discard + hctx.in_play() if card_matches(i, "Ship")]

    def bot_in_play(self) -> list[Inst]:
        """The Bot's cards in play: its Control Area and Staging Area, beamed cards included."""
        return self.ctx.in_play()

    def has_skill_icon(self, inst: Inst | None = None) -> bool:
        return bool(_card(inst or self.this).skills)

    def human_has(self, trait: str) -> bool:
        """Whether the human has a card with the trait in play."""
        if self.human is None:
            return False
        hctx = Ctx(self.state, OpRef(mode="auto", seat=self.human.seat))
        return hctx.count_in_play(lambda i: card_matches(i, trait)) > 0

    def human_may_return_incident(self) -> Gen:
        """Bold "You may return an Incident from your hand or Discard pile": the human decides. Returns True if they
        did."""
        self._use(A.RETURN_INCIDENT)
        human = self.human
        if human is None:
            return False
        hctx = Ctx(self.state, OpRef(mode="auto", seat=human.seat))
        incidents = hctx.hand_incidents("discard")
        incident = yield from self._ui.pick_card("You may return an Incident (from the Bot's card).", incidents,
                                                 optional=True, seat=human.seat, none_label="Do not return one")
        if incident is None:
            return False
        take_out(self.state, incident)
        incident.res.clear()
        self.state.incident.append(incident)
        self.state.emit(f"{human.name} returns {_name(incident)} to the Incident deck.", seat=human.seat)
        raise_event(self.state, "return_incident", human.seat, incident.uid)
        return True

    def human_secured(self, loc: Inst) -> bool:
        from engine.game import secured_by

        return self.human is not None and secured_by(self.state, loc, self.human.seat)

    # ------------------------------------------------------------------ resolution flow (REQ-SOLO-120)
    def continue_resolution(self) -> Gen:
        """Stop this row; the next matching row resolves (REQ-SOLO-120). The row returns right after."""
        self._use(A.CONTINUE_RESOLUTION)
        self.continued = True
        return
        yield  # pragma: no cover

