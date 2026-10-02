"""The card operation runtime.

A card operation is a generator `fn(ctx, actions)`. Every action is a generator too, called with
`yield from`; when an action needs a player's choice it yields an `Ask`, and the runtime turns it
into a Decision. The answer is sent back into the generator.

Generators cannot be copied or stored, so the runtime never keeps one. It stores a snapshot of the
state from when the operation started, plus the answers given so far. To continue, it restores the
snapshot and runs the operation again from the start, feeding the recorded answers. The engine is
deterministic, so this reproduces the same state, and then asks the next question.

The actions object only offers the actions the operation declared in `uses`; anything else raises
UndeclaredActionError (CLAUDE.md, rule 3). `choose` and `may` are always available.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass, field
from typing import Any

from engine import cards as registry
from engine.content import MARKET_SUITS, Card, content
from engine.state import Decision, GameState, Inst, OpRef, Option, Player, Running

SPECIES = {
    "Alien", "Aenar", "Andorian", "Android", "Bajoran", "Betazoid", "Borg", "Breen", "Cardassian", "Changeling",
    "Ferengi", "Human", "Hirogen", "Jem'Hadar", "Kazon", "Kelpien", "Klingon", "Orion", "Pakled", "Reman",
    "Romulan", "Synthetic", "Talaxian", "Tellarite", "Transcendent", "Trill", "Vau N'Akat", "Vorta", "Vulcan",
    "XB", "Xindi",
}
SPECIALTIES = ("research", "influence", "military")


class A:
    """Action names, as listed in CLAUDE.md."""

    DRAW = "DRAW"; DRAW_FROM_DISCARD = "DRAW_FROM_DISCARD"; DISCARD = "DISCARD"; DISMISS = "DISMISS"
    RECALL = "RECALL"; DESTROY = "DESTROY"; LOG = "LOG"; BEAM = "BEAM"; PROMOTE = "PROMOTE"; DEPLOY = "DEPLOY"
    PUT = "PUT"; GIVE = "GIVE"; TAKE_INCIDENT = "TAKE_INCIDENT"; TAKE_ENCOUNTER = "TAKE_ENCOUNTER"
    RETURN_INCIDENT = "RETURN_INCIDENT"; JUNK = "JUNK"; GAIN_CARD = "GAIN_CARD"; SCAN = "SCAN"
    SCAN_FOR = "SCAN_FOR"; FIND = "FIND"; ENLIST_RESERVE = "ENLIST_RESERVE"
    ENLIST_DEVELOPMENT = "ENLIST_DEVELOPMENT"; FREE_PLAY = "FREE_PLAY"; DUPLICATE = "DUPLICATE"
    REVEAL = "REVEAL"; PEEK = "PEEK"; GAIN_RESOURCE = "GAIN_RESOURCE"; SPEND = "SPEND"
    PLACE_RESOURCES = "PLACE_RESOURCES"; STEAL = "STEAL"; GAIN_ACTION = "GAIN_ACTION"
    GAIN_SPECIALTY = "GAIN_SPECIALTY"; WARP = "WARP"; SEND_AWAY_TEAM = "SEND_AWAY_TEAM"
    REMOVE_AWAY_TEAM = "REMOVE_AWAY_TEAM"; TAKE_CONTROL = "TAKE_CONTROL"; TRIGGER_CONTROL = "TRIGGER_CONTROL"
    EXHAUST = "EXHAUST"; REFRESH = "REFRESH"; FORCE = "FORCE"; ATTACK = "ATTACK"


class UndeclaredActionError(RuntimeError):
    pass


@dataclass
class Ask:
    seat: int
    prompt: str
    options: list[tuple[str, str]]
    cards: list[Inst] = field(default_factory=list)  # cards to show with the question


Gen = Generator[Ask, str, Any]


# =========================================================================== card and zone helpers


def card(inst: Inst) -> Card:
    return content().cards[inst.card]


def name(inst: Inst) -> str:
    return card(inst).name


def zones(p: Player) -> dict[str, list[Inst]]:
    return {"hand": p.hand, "draw": p.draw, "discard": p.discard, "reserve": p.reserve, "development": p.development,
            "staging": p.staging, "fleet": p.fleet, "locations": p.locations, "duty": p.duty, "log": p.log,
            "status": p.status}


def _beamed_parent(inst: Inst, uid: str) -> Inst | None:
    for b in inst.beamed:
        if b.uid == uid:
            return inst
        found = _beamed_parent(b, uid)
        if found:
            return found
    return None


@dataclass
class Where:
    zone: str  # hand, draw, ..., beamed, captain, neutral, market, junk
    owner: Player | None
    container: list[Inst] | None
    parent: Inst | None = None


def locate(state: GameState, uid: str) -> Where | None:
    for p in state.players:
        if p.captain.uid == uid:
            return Where("captain", p, None)
        for zname, zone in zones(p).items():
            for inst in zone:
                if inst.uid == uid:
                    return Where(zname, p, zone)
                parent = _beamed_parent(inst, uid)
                if parent:
                    return Where("beamed", p, parent.beamed, parent)
    for loc in state.neutral:
        if loc.uid == uid:
            return Where("neutral", None, state.neutral)
    for suit, inst in state.market.items():
        if inst is not None and inst.uid == uid:
            return Where("market", None, None)
    if any(i.uid == uid for i in state.junk):
        return Where("junk", None, state.junk)
    return None


def find_inst(state: GameState, uid: str) -> Inst | None:
    for p in state.players:
        if p.captain.uid == uid:
            return p.captain
        for zone in zones(p).values():
            for inst in zone:
                if inst.uid == uid:
                    return inst
                parent = _beamed_parent(inst, uid)
                if parent:
                    return next(b for b in parent.beamed if b.uid == uid)
    for inst in [*state.neutral, *state.junk, *[i for i in state.market.values() if i]]:
        if inst.uid == uid:
            return inst
    return None


def take_out(state: GameState, inst: Inst) -> Where:
    where = locate(state, inst.uid)
    if where is None:
        raise ValueError(f"{inst.uid} is not on the table")
    if where.container is not None:
        where.container.remove(inst)
    elif where.zone == "market":
        for suit, i in state.market.items():
            if i is not None and i.uid == inst.uid:
                state.market[suit] = None
    return where


def flatten_beamed(inst: Inst) -> list[Inst]:
    out = []
    for b in inst.beamed:
        out.append(b)
        out.extend(flatten_beamed(b))
        b.beamed = []
    inst.beamed = []
    return out


def table_cards(p: Player) -> list[Inst]:
    return [p.captain, *p.status, *p.fleet, *p.locations, *p.duty]


def is_khan(p: Player) -> bool:
    return p.captain.card in {"2KHA01A", "2KHA01B"}


# =========================================================================== context


class Ctx:
    """Read-only queries for card code (CLAUDE.md rule 7)."""

    def __init__(self, state: GameState, ref: OpRef):
        self.state = state
        self.ref = ref
        self.me = state.player(ref.seat)
        self.opponent = state.opponent(ref.seat)
        self.event = ref.event or {}

    @property
    def virtual_opponent(self) -> bool:
        """Cadet Training: `opponent` is None and a virtual opponent with one of everything stands in (REQ-CTM-12)."""
        return self.state.mode == "cadet"

    # ------------------------------------------------------------ cards
    @property
    def this_card(self) -> Inst | None:
        return find_inst(self.state, self.ref.uid) if self.ref.uid else None

    def card(self, inst: Inst) -> Card:
        return card(inst)

    def name(self, inst: Inst) -> str:
        return name(inst)

    def suit(self, inst: Inst) -> str:
        return card(inst).suit

    def traits(self, inst: Inst) -> set[str]:
        return set(card(inst).traits)

    def has(self, inst: Inst, trait: str) -> bool:
        return trait in self.traits(inst)

    def species(self, inst: Inst) -> set[str]:
        return self.traits(inst) & SPECIES

    def skills(self, inst: Inst, owner: Player | None = None) -> list[str]:
        printed = list(card(inst).skills)
        owner = owner or self.me
        modifier = registry.SKILLS.get(inst.card)
        if modifier and inst in table_cards(owner):
            return modifier(self.state, owner, inst)
        return [s for s in printed if s != "Variable"]

    def has_specialty_icon(self, inst: Inst, specialty: str) -> bool:
        """Skill or Focus icon of the Specialty, or Any Skill / Best Focus (REQ-SP-12)."""
        sp = specialty.capitalize()
        return sp in self.skills(inst) or "Any" in self.skills(inst) or card(inst).focus in (sp, "Best")

    # ------------------------------------------------------------ zones
    def in_play(self, player: Player | None = None, *, beamed: bool = True) -> list[Inst]:
        player = player or self.me
        cards = [*table_cards(player), *player.staging]
        if beamed:
            for inst in list(cards):
                cards.extend(_all_beamed(inst))
        return cards

    def on_table(self, inst: Inst, player: Player | None = None) -> bool:
        return inst in table_cards(player or self.me)

    def count_in_play(self, pred: Callable[[Inst], bool], player: Player | None = None, *, beamed: bool = True) -> int:
        return sum(1 for i in self.in_play(player, beamed=beamed) if pred(i))

    def controlled_locations(self, player: Player | None = None) -> list[Inst]:
        return list((player or self.me).locations)

    def all_locations(self) -> list[Inst]:
        return [*self.me.locations, *self.state.neutral, *(self.opponent.locations if self.opponent else [])]

    def ships_at(self, loc: Inst, player: Player | None = None) -> list[Inst]:
        return [s for s in (player or self.me).fleet if s.at == loc.uid]

    def away_at(self, loc: Inst, player: Player | None = None) -> int:
        return loc.away.get((player or self.me).seat, 0)

    def location_of(self, ship: Inst) -> Inst | None:
        return next((loc for loc in self.all_locations() if loc.uid == ship.at), None) if ship.at else None

    def track(self, specialty: str, player: Player | None = None) -> int:
        return (player or self.me).tracks[specialty]

    def actions_left(self) -> int:
        return self.me.actions


def _all_beamed(inst: Inst) -> list[Inst]:
    out = []
    for b in inst.beamed:
        out.append(b)
        out.extend(_all_beamed(b))
    return out


# =========================================================================== costs


class Cost:
    label = ""

    def can_pay(self, ctx: Ctx) -> bool:
        return True

    def pay(self, actions: "Actions") -> Gen:
        return
        yield  # pragma: no cover


def can_afford(player: Player, dilithium: int = 0, latinum: int = 0, glory: int = 0) -> bool:
    short_l = max(0, latinum - player.latinum)
    short_d = max(0, dilithium - player.dilithium)
    return player.glory >= glory + short_l + math.ceil(short_d / 2)


def pay_resources(player: Player, dilithium: int = 0, latinum: int = 0, glory: int = 0) -> None:
    """Spend resources, substituting Glory where needed: 1 Glory = 1 Latinum or 2 Dilithium (KW-SPEND-02)."""
    use_l = min(latinum, player.latinum)
    use_d = min(dilithium, player.dilithium)
    player.latinum -= use_l
    player.dilithium -= use_d
    player.glory -= glory + (latinum - use_l) + math.ceil((dilithium - use_d) / 2)


@dataclass
class Spend(Cost):
    dilithium: int = 0
    latinum: int = 0
    glory: int = 0

    def can_pay(self, ctx):
        return can_afford(ctx.me, self.dilithium, self.latinum, self.glory)

    def pay(self, actions):
        pay_resources(actions.ctx.me, self.dilithium, self.latinum, self.glory)
        actions.ctx.state.emit(f"{actions.ctx.me.name} spends {_res_text(self.dilithium, self.latinum, self.glory)}.",
                               seat=actions.ctx.me.seat)
        return
        yield  # pragma: no cover


def _res_text(d=0, l=0, g=0) -> str:
    parts = [f"{n} {k}" for n, k in ((d, "Dilithium"), (l, "Latinum"), (g, "Glory")) if n]
    return ", ".join(parts) or "nothing"


@dataclass
class DiscardFromHand(Cost):
    n: int = 1
    pred: Callable[[Ctx, Inst], bool] | None = None
    label: str = "a card"

    def candidates(self, ctx):
        this = ctx.this_card
        return [i for i in ctx.me.hand if i is not this and (self.pred is None or self.pred(ctx, i))]

    def can_pay(self, ctx):
        return len(self.candidates(ctx)) >= self.n

    def pay(self, actions):
        for _ in range(self.n):
            inst = yield from actions.pick_card(f"Discard {self.label} (cost).", self.candidates(actions.ctx))
            actions._discard(inst)
            actions.paid.append(inst)


@dataclass
class TakeIncidentCost(Cost):
    n: int = 1

    def can_pay(self, ctx):
        return len(ctx.state.incident) >= 1

    def pay(self, actions):
        for _ in range(self.n):
            yield from actions.take_incident(_cost=True)


@dataclass
class PutOnDeck(Cost):
    n: int = 1

    def can_pay(self, ctx):
        this = ctx.this_card
        return len([i for i in ctx.me.hand if i is not this]) >= self.n

    def pay(self, actions):
        for _ in range(self.n):
            this = actions.ctx.this_card
            inst = yield from actions.pick_card("Put a card on top of your deck (cost).",
                                                [i for i in actions.ctx.me.hand if i is not this])
            take_out(actions.ctx.state, inst)
            actions.ctx.me.draw.insert(0, inst)
            actions.paid.append(inst)


@dataclass
class LogFromHand(Cost):
    pred: Callable[[Ctx, Inst], bool] | None = None
    label: str = "a card"

    def candidates(self, ctx):
        this = ctx.this_card
        return [i for i in ctx.me.hand if i is not this and (self.pred is None or self.pred(ctx, i))]

    def can_pay(self, ctx):
        return bool(self.candidates(ctx))

    def pay(self, actions):
        inst = yield from actions.pick_card(f"Log {self.label} from your hand (cost).", self.candidates(actions.ctx))
        actions._log(inst)
        actions.paid.append(inst)


@dataclass
class DismissDutyOfficer(Cost):
    """Dismiss one of your own Duty Officers, even your only one (Kir'Shara ruling)."""

    def can_pay(self, ctx):
        return bool(ctx.me.duty)

    def pay(self, actions):
        inst = yield from actions.pick_card("Dismiss one of your Duty Officers (cost).", list(actions.ctx.me.duty))
        actions._dismiss(inst)


@dataclass
class RemoveOwnAwayTeam(Cost):
    """Remove one of your Away Teams from any Location; it returns to your Captain."""

    def locations(self, ctx):
        return [loc for loc in ctx.all_locations() if ctx.away_at(loc) > 0]

    def can_pay(self, ctx):
        return bool(self.locations(ctx))

    def pay(self, actions):
        loc = yield from actions.pick_card("Remove one of your Away Teams from which Location?", self.locations(actions.ctx))
        loc.away[actions.ctx.me.seat] -= 1
        if not loc.away[actions.ctx.me.seat]:
            del loc.away[actions.ctx.me.seat]
        actions.ctx.me.away_pool += 1
        actions.ctx.state.emit(f"{actions.ctx.me.name} removes an Away Team from {name(loc)}.", seat=actions.ctx.me.seat)


# =========================================================================== actions


class Actions:
    """The actions an operation declared, and only those (CLAUDE.md rule 3)."""

    def __init__(self, ctx: Ctx, uses: Iterable[str]):
        self.ctx = ctx
        self.state = ctx.state
        self.uses = set(uses)
        self.paid: list[Inst] = []  # cards used to pay costs, e.g. the discarded card

    def _use(self, action: str) -> None:
        if action not in self.uses:
            raise UndeclaredActionError(f"{action} is not in this operation's uses list")

    def emit(self, text: str, **kw) -> None:
        self.state.emit(text, seat=self.ctx.me.seat, **kw)

    # ------------------------------------------------------------ choices (always available)
    def choose(self, prompt: str, options: list[tuple[str, str]], seat: int | None = None, *,
               show: list[Inst] | None = None) -> Gen:
        """Ask a player. `show` lists cards the player needs to see to answer."""
        seat = self.ctx.me.seat if seat is None else seat
        if seat != self.ctx.me.seat:
            self.state.emit(f"{self.state.player(seat).name} must choose: {prompt}", irreversible=True)
        answer = yield Ask(seat, prompt, options, [i.model_copy(deep=True) for i in show or []])
        return answer

    def may(self, prompt: str, seat: int | None = None) -> Gen:
        answer = yield from self.choose(prompt, [("yes", "Yes"), ("no", "No")], seat)
        return answer == "yes"

    def pick_card(self, prompt: str, cards: list[Inst], *, optional: bool = False, seat: int | None = None,
                  none_label: str = "None") -> Gen:
        if not cards:
            return None
        options = [(c.uid, f"{name(c)}") for c in cards]
        if optional:
            options.append(("none", none_label))
        answer = yield from self.choose(prompt, options, seat, show=cards)
        return None if answer == "none" else next(c for c in cards if c.uid == answer)

    def pick_cards(self, prompt: str, cards: list[Inst], *, maximum: int, minimum: int = 0) -> Gen:
        chosen: list[Inst] = []
        remaining = list(cards)
        while remaining and len(chosen) < maximum:
            done_ok = len(chosen) >= minimum
            options = [(c.uid, name(c)) for c in remaining] + ([("done", "Done")] if done_ok else [])
            answer = yield from self.choose(f"{prompt} ({len(chosen)} chosen)", options)
            if answer == "done":
                break
            pick = next(c for c in remaining if c.uid == answer)
            chosen.append(pick)
            remaining.remove(pick)
        return chosen

    # ------------------------------------------------------------ cards
    def draw(self, n: int = 1, player: Player | None = None) -> Gen:
        self._use(A.DRAW)
        return (yield from self._draw(n, player))

    def _draw(self, n: int, player: Player | None = None) -> Gen:
        player = player or self.ctx.me
        drawn = 0
        for _ in range(n):
            if not player.draw:
                ok = yield from self._cycle(player)
                if not ok:
                    break
            player.hand.append(player.draw.pop(0))
            drawn += 1
        if drawn:
            self.state.emit(f"{player.name} draws {drawn} card(s).", seat=player.seat, irreversible=True)
        return drawn

    def _cycle(self, player: Player) -> Gen:
        """Deck cycling with enlisting (REQ-DK-01, -02, -10)."""
        if not player.discard:
            return False
        player.draw, player.discard = player.discard, []
        self.state.shuffle(player.draw)
        self.state.emit(f"{player.name} shuffles their Discard pile into a new deck.", seat=player.seat, irreversible=True)
        if is_khan(player):
            return True
        if player.reserve:
            player.draw.insert(0, player.reserve.pop(0))
            self.state.emit(f"{player.name} enlists a Reserve.", seat=player.seat)
        elif player.seat == self.ctx.me.seat and _payable_developments(self.ctx):
            if (yield from self.may("Your Reserve deck is empty. Enlist a Development?")):
                yield from self._enlist_development(free=False)
        return True

    def draw_from_discard(self, pred: Callable[[Inst], bool] | None = None, label: str = "a card",
                          optional: bool = False) -> Gen:
        self._use(A.DRAW_FROM_DISCARD)
        cards = [i for i in reversed(self.ctx.me.discard) if pred is None or pred(i)]
        inst = yield from self.pick_card(f"Take {label} from your Discard pile.", cards, optional=optional)
        if inst:
            self.ctx.me.discard.remove(inst)
            self.ctx.me.hand.append(inst)
            self.emit(f"{self.ctx.me.name} takes {name(inst)} from their Discard pile.")
        return inst

    def discard(self, n: int = 1, pred: Callable[[Inst], bool] | None = None, label: str = "a card",
                optional: bool = False) -> Gen:
        self._use(A.DISCARD)
        out = []
        for _ in range(n):
            this = self.ctx.this_card
            cards = [i for i in self.ctx.me.hand if i is not this and (pred is None or pred(i))]
            inst = yield from self.pick_card(f"Discard {label}.", cards, optional=optional)
            if not inst:
                break
            self._discard(inst)
            out.append(inst)
        return out

    def _discard(self, inst: Inst) -> None:
        owner = locate(self.state, inst.uid).owner
        take_out(self.state, inst)
        owner.discard.append(inst)
        self.emit(f"{owner.name} discards {name(inst)}.")

    def discard_top(self) -> Gen:
        self._use(A.DISCARD)
        if not self.ctx.me.draw and not (yield from self._cycle(self.ctx.me)):
            return None
        inst = self.ctx.me.draw.pop(0)
        self.ctx.me.discard.append(inst)
        self.emit(f"{self.ctx.me.name} discards {name(inst)} from the top of their deck.", irreversible=True)
        return inst

    def dismiss(self, inst: Inst) -> Gen:
        self._use(A.DISMISS)
        self._dismiss(inst)
        return
        yield  # pragma: no cover

    def _dismiss(self, inst: Inst) -> None:
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        if card(inst).suit == "Location":
            self._clear_location(inst)
        inst.at = None
        inst.exhausted = False
        inst.res.clear()
        owner.discard.extend(flatten_beamed(inst))
        owner.discard.append(inst)
        self.state.emit(f"{name(inst)} is dismissed.", seat=owner.seat)

    def _clear_location(self, loc: Inst) -> None:
        for p in self.state.players:
            p.away_pool += loc.away.pop(p.seat, 0)
            for ship in [s for s in p.fleet if s.at == loc.uid]:
                self._dismiss(ship)

    def recall(self, inst: Inst) -> Gen:
        self._use(A.RECALL)
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        inst.at = None
        inst.exhausted = False
        inst.res.clear()
        owner.hand.extend(flatten_beamed(inst))
        owner.hand.append(inst)
        self.state.emit(f"{owner.name} recalls {name(inst)}.", seat=owner.seat)
        return
        yield  # pragma: no cover

    def log(self, inst: Inst) -> Gen:
        self._use(A.LOG)
        self._log(inst)
        return
        yield  # pragma: no cover

    def _log(self, inst: Inst) -> None:
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        if card(inst).suit == "Location":
            self._clear_location(inst)
        inst.at = None
        inst.exhausted = False
        inst.res.clear()
        owner.log.extend(flatten_beamed(inst))
        owner.log.append(inst)
        self.state.emit(f"{owner.name} logs {name(inst)}.", seat=owner.seat)

    def beam(self, inst: Inst, onto: Inst) -> Gen:
        self._use(A.BEAM)
        where = take_out(self.state, inst)
        onto.beamed.append(inst)
        self.emit(f"{self.ctx.me.name} beams {name(inst)} to {name(onto)}.")
        if where.zone in ("hand", "discard"):
            put_into_play(self.state, self.ctx.me, inst)
        return
        yield  # pragma: no cover

    def promote(self, inst: Inst) -> Gen:
        self._use(A.PROMOTE)
        where = take_out(self.state, inst)
        self.ctx.me.duty.append(inst)
        self.emit(f"{self.ctx.me.name} promotes {name(inst)} to Duty Officer.")
        if where.zone in ("hand", "discard"):
            put_into_play(self.state, self.ctx.me, inst)
        limit = duty_limit(self.state, self.ctx.me)
        while len(self.ctx.me.duty) > limit:
            extra = yield from self.pick_card("You have too many Duty Officers. Dismiss one.", list(self.ctx.me.duty))
            self._dismiss(extra)

    def deploy(self, inst: Inst) -> Gen:
        self._use(A.DEPLOY)
        take_out(self.state, inst)
        inst.at = None
        self.ctx.me.fleet.append(inst)
        self.emit(f"{self.ctx.me.name} deploys {name(inst)}.")
        raise_event(self.state, "deploy", self.ctx.me.seat, inst.uid)
        return
        yield  # pragma: no cover

    def put_on_deck(self, inst: Inst) -> Gen:
        self._use(A.PUT)
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        owner.draw.insert(0, inst)
        self.emit(f"{owner.name} puts {name(inst)} on top of their deck.")
        return
        yield  # pragma: no cover

    def take_incident(self, player: Player | None = None, *, opponent: bool = False, _cost: bool = False) -> Gen:
        """Take the top Incident. `opponent=True` makes the opponent take it instead."""
        if not _cost:
            self._use(A.TAKE_INCIDENT)
        from engine import game

        if opponent:
            if self.ctx.opponent is None:
                if self.ctx.virtual_opponent:
                    # The virtual opponent skips the Incident and you gain 1 Glory (REQ-CTM-13).
                    self.emit("The virtual opponent skips the Incident.")
                    gain(self.state, self.ctx.me, "glory", 1)
                return None
            player = self.ctx.opponent
        return game.take_incident(self.state, player or self.ctx.me)
        yield  # pragma: no cover

    def return_incident(self, inst: Inst) -> Gen:
        self._use(A.RETURN_INCIDENT)
        take_out(self.state, inst)
        inst.res.clear()
        self.state.incident.append(inst)
        self.emit(f"{self.ctx.me.name} returns {name(inst)} to the Incident deck.")
        return
        yield  # pragma: no cover

    def take_encounter(self, look: int = 1) -> Gen:
        self._use(A.TAKE_ENCOUNTER)
        if not self.state.encounter:
            return None
        top = self.state.encounter[:look]
        if len(top) == 1:
            chosen = top[0]
        else:
            self.state.emit(f"{self.ctx.me.name} looks at the top {len(top)} Encounter cards.", irreversible=True)
            chosen = yield from self.pick_card("Take which Encounter?", top)
            other = [c for c in top if c is not chosen]
            for c in other:
                self.state.encounter.remove(c)
                self.state.encounter.append(c)
        self.state.encounter.remove(chosen)
        self.ctx.me.hand.append(chosen)
        self.emit(f"{self.ctx.me.name} takes the Encounter {name(chosen)}.", irreversible=True)
        return chosen

    def junk(self) -> Gen:
        self._use(A.JUNK)
        cards = [i for i in self.state.market.values() if i is not None and not i.res]
        inst = yield from self.pick_card("Junk a card from the Market.", cards)
        if inst:
            suit = card(inst).suit
            self.state.market[suit] = None
            self.state.junk.append(inst)
            self.emit(f"{self.ctx.me.name} junks {name(inst)}.")
            _refill(self.state, suit)
        return inst

    # ------------------------------------------------------------ gaining cards (KW-GAIN, KW-SCAN, KW-FIND)
    def gain_card(self, suits: Iterable[str] | None = None, pred: Callable[[Inst], bool] | None = None,
                  label: str = "a card", *, from_junk: bool = False, to_hand: bool = False) -> Gen:
        """Gain [suit] (faceup Market card or unseen top of its deck) or gain [trait] (faceup cards only)."""
        self._use(A.GAIN_CARD)
        options: list[tuple[str, str]] = []
        if suits is not None:
            for suit in suits:
                inst = self.state.market.get(suit)
                if inst is not None and (pred is None or pred(inst)):
                    options.append((f"market:{suit}", f"{name(inst)} (faceup {suit})"))
                if pred is None and self.state.market_decks.get(suit):
                    options.append((f"deck:{suit}", f"Top card of the {suit} deck (unseen)"))
        else:
            for suit, inst in self.state.market.items():
                if inst is not None and (pred is None or pred(inst)):
                    options.append((f"market:{suit}", f"{name(inst)} ({suit})"))
        if from_junk:
            for inst in reversed(self.state.junk):
                if (suits is None or card(inst).suit in suits) and (pred is None or pred(inst)):
                    options.append((f"junk:{inst.uid}", f"{name(inst)} (from the Junk)"))
        if not options:
            self.emit(f"No {label} can be gained.")
            return None
        answer = yield from self.choose(f"Gain {label}.", options)
        inst = self._take_gained(answer)
        yield from self._place_gained(inst, to_hand)
        return inst

    def _take_gained(self, answer: str) -> Inst:
        kind, key = answer.split(":", 1)
        if kind == "market":
            inst = self.state.market[key]
            self.state.market[key] = None
            if inst.res.get("glory"):
                self.ctx.me.glory += inst.res["glory"]
                self.emit(f"{self.ctx.me.name} also gains {inst.res['glory']} Glory from it.")
            inst.res.clear()
            _refill(self.state, key)
        elif kind == "deck":
            inst = self.state.market_decks[key].pop(0)
            self.state.emit(f"{self.ctx.me.name} gains the top card of the {key} deck.", irreversible=True)
        else:
            inst = next(i for i in self.state.junk if i.uid == key)
            self.state.junk.remove(inst)
        return inst

    def _place_gained(self, inst: Inst, to_hand: bool) -> Gen:
        if to_hand:
            self.ctx.me.hand.append(inst)
            where = "into their hand"
        else:
            answer = yield from self.choose(f"Put {name(inst)} where?", [("top", "On top of your deck"), ("discard", "In your Discard pile")],
                                            show=[inst])
            (self.ctx.me.draw.insert(0, inst) if answer == "top" else self.ctx.me.discard.append(inst))
            where = "on top of their deck" if answer == "top" else "into their Discard pile"
        self.emit(f"{self.ctx.me.name} gains {name(inst)} {where}.")
        raise_event(self.state, "gain", self.ctx.me.seat, inst.uid)

    def _scans_junk(self) -> bool:
        return any(i.card in registry.SCANS_INCLUDE_JUNK for i in table_cards(self.ctx.me))

    def scan(self, n: int, suits: Iterable[str], *, include_junk: bool = False) -> Gen:
        """Scan # of [suit] (KW-SCAN-01)."""
        self._use(A.SCAN)
        suits = [s for s in suits if self.state.market.get(s) is not None or self.state.market_decks.get(s)]
        if not suits:
            return None
        suit = suits[0] if len(suits) == 1 else (yield from self.choose("Scan which suit?", [(s, s) for s in suits]))
        deck = self.state.market_decks[suit]
        looked = deck[:n]
        del deck[:n]
        self.state.emit(f"{self.ctx.me.name} looks at {len(looked)} {suit} card(s).", irreversible=True)
        options = [(f"look:{i.uid}", f"{name(i)} (from the deck)") for i in looked]
        if self.state.market.get(suit) is not None:
            options.append((f"market:{suit}", f"{name(self.state.market[suit])} (faceup)"))
        if include_junk or self._scans_junk():
            options += [(f"junk:{i.uid}", f"{name(i)} (from the Junk)") for i in self.state.junk if card(i).suit == suit]
        shown = looked + [i for i in self.state.junk if card(i).suit == suit and (include_junk or self._scans_junk())]
        answer = (yield from self.choose(f"Gain which {suit}?", options, show=shown)) if options else None
        inst = None
        if answer and answer.startswith("look:"):
            inst = next(i for i in looked if i.uid == answer[5:])
            looked.remove(inst)
        elif answer:
            inst = self._take_gained(answer)
        deck.extend(looked)  # the rest go to the bottom
        if inst:
            yield from self._place_gained(inst, False)
        return inst

    def scan_for(self, pred: Callable[[Inst], bool], label: str, *, include_junk: bool = False) -> Gen:
        """Scan for [trait / icon] (KW-SCAN-05)."""
        self._use(A.SCAN_FOR)
        faceup = [(f"market:{s}", f"{name(i)} (faceup)") for s, i in self.state.market.items() if i is not None and pred(i)]
        junk = [(f"junk:{i.uid}", f"{name(i)} (from the Junk)") for i in self.state.junk if pred(i)] \
            if (include_junk or self._scans_junk()) else []
        if faceup or junk:
            answer = yield from self.choose(f"Gain {label}.", faceup + junk)
            inst = self._take_gained(answer)
            yield from self._place_gained(inst, False)
            return inst
        remaining = [s for s in MARKET_SUITS if self.state.market_decks.get(s)]
        while remaining:
            suit = remaining[0] if len(remaining) == 1 else (
                yield from self.choose(f"No faceup {label}. Search which deck?", [(s, f"{s} deck") for s in remaining]))
            remaining.remove(suit)
            deck = self.state.market_decks[suit]
            revealed: list[Inst] = []
            found = None
            while deck:
                inst = deck.pop(0)
                if pred(inst):
                    found = inst
                    break
                revealed.append(inst)
            self.state.emit(f"{self.ctx.me.name} reveals {len(revealed) + (1 if found else 0)} {suit} card(s).",
                            irreversible=True)
            deck.extend(revealed)
            self.state.shuffle(deck)
            if found:
                yield from self._place_gained(found, False)
                return found
        self.ctx.me.glory += 2  # compensation (KW-SCAN-05)
        self.emit(f"No {label} anywhere: {self.ctx.me.name} gains 2 Glory as compensation.")
        return None

    def find(self, pred: Callable[[Inst], bool], label: str, *, exclude_reserve: bool = False,
             zones_: Iterable[str] = ("hand", "draw", "discard", "reserve"), optional: bool = False) -> Gen:
        """Find [card] (KW-FIND). Returns (card, zone it came from) or (None, None)."""
        self._use(A.FIND)
        me = self.ctx.me
        searched = [z for z in zones_ if not (exclude_reserve and z == "reserve")]
        pools = {"hand": me.hand, "draw": me.draw, "discard": me.discard, "reserve": me.reserve}
        this = self.ctx.this_card
        candidates = [(z, i) for z in searched for i in pools[z] if i is not this and pred(i)]
        options = [(f"{z}:{i.uid}", f"{name(i)} ({'your ' + {'draw': 'Draw deck', 'reserve': 'Reserve deck', 'discard': 'Discard pile', 'hand': 'hand'}[z]})")
                   for z, i in candidates]
        if optional:
            options.append(("none", "Find nothing"))
        found, zone = None, None
        if options:
            self.state.emit(f"{me.name} searches for {label}.", irreversible=True)
            answer = yield from self.choose(f"Find {label}.", options, show=[i for _, i in candidates])
            if answer != "none":
                zone, uid = answer.split(":", 1)
                found = next(i for z, i in candidates if i.uid == uid)
                if zone != "hand":
                    pools[zone].remove(found)
                    me.hand.append(found)
                self.emit(f"{me.name} finds {name(found)}.")
        else:
            self.emit(f"{me.name} finds no {label}.")
        for z in ("draw", "reserve"):
            if z in searched and pools[z]:
                self.state.shuffle(pools[z])
        return found, zone

    def enlist_reserve(self) -> Gen:
        self._use(A.ENLIST_RESERVE)
        if self.ctx.me.reserve:
            self.ctx.me.draw.insert(0, self.ctx.me.reserve.pop(0))
            self.emit(f"{self.ctx.me.name} enlists a Reserve.")
        return
        yield  # pragma: no cover

    def enlist_development(self, *, free: bool = False, pred: Callable[[Inst], bool] | None = None) -> Gen:
        self._use(A.ENLIST_DEVELOPMENT)
        return (yield from self._enlist_development(free=free, pred=pred))

    def _enlist_development(self, *, free: bool, pred: Callable[[Inst], bool] | None = None) -> Gen:
        cards = [i for i in _payable_developments(self.ctx, free=free) if pred is None or pred(i)]
        if not cards:
            self.emit("No Development can be enlisted.")
            return None
        inst = yield from self.pick_card("Enlist which Development?", cards)
        if not free:
            for cost in registry.DEV_COSTS[inst.card]:
                yield from cost.pay(self)
        self.ctx.me.development.remove(inst)
        self.ctx.me.draw.insert(0, inst)
        self.emit(f"{self.ctx.me.name} enlists {name(inst)}{' for free' if free else ''}.")
        return inst

    def free_play(self, inst: Inst) -> Gen:
        """Play a card without spending an action (KW-FREE). Other costs still apply."""
        self._use(A.FREE_PLAY)
        return (yield from play_inline(self.ctx, inst, free=True, parent=self))

    def free_play_candidates(self, pred: Callable[[Inst], bool]) -> list[Inst]:
        return [i for i in self.ctx.me.hand if pred(i) and playable_indexes(self.state, self.ctx.me, i, free=True)]

    # ------------------------------------------------------------ resources, actions, tracks
    def gain_resource(self, kind: str, n: int = 1) -> Gen:
        self._use(A.GAIN_RESOURCE)
        gain(self.state, self.ctx.me, kind, n)
        return
        yield  # pragma: no cover

    def spend(self, dilithium: int = 0, latinum: int = 0, glory: int = 0) -> Gen:
        self._use(A.SPEND)
        if not can_afford(self.ctx.me, dilithium, latinum, glory):
            return False
        pay_resources(self.ctx.me, dilithium, latinum, glory)
        self.emit(f"{self.ctx.me.name} spends {_res_text(dilithium, latinum, glory)}.")
        return True
        yield  # pragma: no cover

    def gain_action(self, n: int = 1) -> Gen:
        self._use(A.GAIN_ACTION)
        self.ctx.me.actions += n
        self.emit(f"{self.ctx.me.name} gains {n} action(s).")
        return
        yield  # pragma: no cover

    def gain_specialty(self, track: str, n: int = 1, player: Player | None = None) -> Gen:
        self._use(A.GAIN_SPECIALTY)
        player = player or self.ctx.me
        if is_khan(player) or n == 0:
            return
        player.tracks[track] = max(0, min(15, player.tracks[track] + n))
        player.highest[track] = max(player.highest[track], player.tracks[track])
        self.state.emit(f"{player.name} gains {n} {track.capitalize()} (now {player.tracks[track]}).", seat=player.seat)
        if n > 0:
            raise_event(self.state, "gain_specialty", player.seat, None, track=track, amount=n)
        return
        yield  # pragma: no cover

    # ------------------------------------------------------------ board
    def warp(self, ship: Inst) -> Gen:
        self._use(A.WARP)
        destinations = [loc for loc in [*self.ctx.me.locations, *self.state.neutral] if loc.uid != ship.at]
        dest = yield from self.pick_card(f"Warp {name(ship)} to which Location?", destinations)
        if dest is None:
            return None
        ship.at = dest.uid
        self.emit(f"{self.ctx.me.name} warps {name(ship)} to {name(dest)}.")
        raise_event(self.state, "warp", self.ctx.me.seat, ship.uid, location=dest.uid)
        return dest

    def away_targets(self, where: Callable[[Inst], bool] | None = None) -> list[Inst]:
        """Locations an Away Team may be sent to (KW-SEND-03)."""
        opp = self.ctx.opponent
        out = list(self.ctx.me.locations)
        for loc in self.state.neutral:
            mine = len(self.ctx.ships_at(loc))
            theirs = len(self.ctx.ships_at(loc, opp)) if opp else 0
            if theirs <= mine:
                out.append(loc)
        return [loc for loc in out if where is None or where(loc)]

    def send_away_team(self, n: int = 1, where: Callable[[Inst], bool] | None = None, *,
                       same_location: bool = False, target: Inst | None = None) -> Gen:
        self._use(A.SEND_AWAY_TEAM)
        me = self.ctx.me
        sent_to = target
        for _ in range(n):
            if sent_to is None or not same_location:
                targets = self.away_targets(where) if target is None else [target]
                if not targets:
                    self.emit("There is nowhere to send an Away Team.")
                    return sent_to
                sent_to = targets[0] if len(targets) == 1 else (
                    yield from self.pick_card("Send an Away Team to which Location?", targets))
            if me.away_pool > 0:
                me.away_pool -= 1
            else:
                sources = [loc for loc in self.ctx.all_locations() if loc is not sent_to and self.ctx.away_at(loc) > 0]
                if not sources:
                    self.emit(f"{me.name} has no Away Team to send.")
                    return sent_to
                src = yield from self.pick_card("No Away Teams left on your Captain. Move one from which Location?", sources)
                src.away[me.seat] -= 1
                if not src.away[me.seat]:
                    del src.away[me.seat]
            sent_to.away[me.seat] = sent_to.away.get(me.seat, 0) + 1
            self.emit(f"{me.name} sends an Away Team to {name(sent_to)}.")
        return sent_to

    def remove_away_team(self, loc: Inst, player: Player) -> Gen:
        self._use(A.REMOVE_AWAY_TEAM)
        if loc.away.get(player.seat):
            loc.away[player.seat] -= 1
            if not loc.away[player.seat]:
                del loc.away[player.seat]
            player.away_pool += 1
            self.state.emit(f"An Away Team of {player.name} is removed from {name(loc)}.", seat=player.seat)
        return
        yield  # pragma: no cover

    def take_control(self, loc: Inst) -> Gen:
        self._use(A.TAKE_CONTROL)
        from engine import game

        if loc in self.state.neutral:
            game.take_control(self.state, self.ctx.me, loc, run_control=False)
            put_into_play(self.state, self.ctx.me, loc)
        else:
            # A Crew Location played from hand: its PLAY raises "put into play" once it resolves.
            take_out(self.state, loc)
            self.ctx.me.locations.append(loc)
            self.emit(f"{self.ctx.me.name} takes control of {name(loc)}.")
        yield from run_inline(self.ctx, loc, "CONTROL")
        return loc

    def exhaust(self, inst: Inst) -> Gen:
        self._use(A.EXHAUST)
        inst.exhausted = True
        return
        yield  # pragma: no cover

    def refresh(self, inst: Inst) -> Gen:
        self._use(A.REFRESH)
        inst.exhausted = False
        self.emit(f"{name(inst)} is refreshed.")
        return
        yield  # pragma: no cover

    def reveal(self, cards: list[Inst]) -> Gen:
        self._use(A.REVEAL)
        shown = ", ".join(name(c) for c in cards) or "nothing"
        self.state.emit(f"{self.ctx.me.name} reveals: {shown}.", irreversible=True)
        return
        yield  # pragma: no cover

    def attack(self) -> None:
        """Mark the start of an attack's negative effect on the opponent (KW-ATK)."""
        self._use(A.ATTACK)
        if self.ctx.opponent:
            self.state.emit(f"{self.ctx.me.name} attacks {self.ctx.opponent.name}.", irreversible=True)


# =========================================================================== shared rules used by actions


def gain(state: GameState, player: Player, kind: str, n: int) -> None:
    if n <= 0:
        return
    if kind == "glory":
        from engine import game

        game.gain_glory(state, player, n)
    else:
        setattr(player, kind, getattr(player, kind) + n)
    state.emit(f"{player.name} gains {n} {kind.capitalize()}.", seat=player.seat)


def _refill(state: GameState, suit: str) -> None:
    from engine.setup import refill_market

    refill_market(state, suit)


def duty_limit(state: GameState, player: Player) -> int:
    return 1 + sum(registry.DUTY_LIMIT.get(i.card, 0) for i in player.duty)


def raise_event(state: GameState, kind: str, seat: int, uid: str | None, **data) -> None:
    state.pending_events.append({"kind": kind, "seat": seat, "uid": uid, **data})


def put_into_play(state: GameState, player: Player, inst: Inst) -> None:
    raise_event(state, "put_into_play", player.seat, inst.uid)


def _payable_developments(ctx: Ctx, free: bool = False) -> list[Inst]:
    out = []
    for inst in ctx.me.development:
        costs = registry.DEV_COSTS.get(inst.card)
        if costs is None:
            continue  # development cost not implemented yet
        if free or all(c.can_pay(ctx) for c in costs):
            out.append(inst)
    return out


# =========================================================================== legality and running


def impl_for(inst: Inst, index: int):
    return registry.OPS.get((inst.card, index))


def legal(state: GameState, player: Player, inst: Inst, index: int, *, free: bool = False) -> bool:
    impl = impl_for(inst, index)
    op = card(inst).operations[index]
    if impl is None:
        return True  # placeholder operation
    ctx = Ctx(state, OpRef(mode="play", seat=player.seat, uid=inst.uid, index=index))
    if op.action_cost and not free and player.actions <= 0:
        return False
    if impl.requires and not impl.requires(ctx):
        return False
    return all(cost.can_pay(ctx) for cost in impl.costs)


def playable_indexes(state: GameState, player: Player, inst: Inst, *, free: bool = False) -> list[int]:
    return [i for i, op in enumerate(card(inst).operations) if op.kind == "PLAY" and legal(state, player, inst, i, free=free)]


def play_inline(ctx: Ctx, inst: Inst, *, free: bool, parent: Actions | None = None, index: int | None = None) -> Gen:
    """Play a card from wherever it is now: move to the Staging Area, pay, resolve (REQ-AS-11)."""
    state = ctx.state
    indexes = playable_indexes(state, ctx.me, inst, free=free) if index is None else [index]
    if not indexes:
        return None
    if index is None and len(indexes) > 1:
        options = [(str(i), card(inst).operations[i].text or "PLAY") for i in indexes]
        index = int((yield from Actions(ctx, ()).choose(f"Which PLAY operation of {name(inst)}?", options)))
    elif index is None:
        index = indexes[0]
    op = card(inst).operations[index]
    take_out(state, inst)
    ctx.me.staging.append(inst)
    state.emit(f"{ctx.me.name} {'free ' if free else ''}plays {name(inst)}.", seat=ctx.me.seat)
    if op.action_cost and not free:
        ctx.me.actions -= 1
    impl = impl_for(inst, index)
    if impl is None:
        state.emit(f"(Card effect not implemented yet: {op.text})", seat=ctx.me.seat)
    else:
        sub = Ctx(state, OpRef(mode="play", seat=ctx.me.seat, uid=inst.uid, index=index))
        actions = Actions(sub, impl.uses)
        for cost in impl.costs:
            yield from cost.pay(actions)
        yield from impl.fn(sub, actions)
    where = locate(state, inst.uid)
    if where is not None and where.zone not in ("hand", "draw", "discard", "reserve", "log"):
        # Not when the effect moved the card away again, e.g. Hostile Contact returning itself.
        put_into_play(state, ctx.me, inst)
    return inst


def run_inline(ctx: Ctx, inst: Inst, kind: str) -> Gen:
    """Resolve a card's operation of the given kind right now, e.g. CONTROL after taking control."""
    for index, op in enumerate(card(inst).operations):
        if op.kind != kind:
            continue
        impl = impl_for(inst, index)
        if impl is None:
            ctx.state.emit(f"({kind} of {name(inst)} is not implemented yet.)", seat=ctx.me.seat)
            continue
        sub = Ctx(ctx.state, OpRef(mode="auto", seat=ctx.me.seat, uid=inst.uid, index=index))
        yield from impl.fn(sub, Actions(sub, impl.uses))


SYSTEM: dict[str, Callable[[Ctx, Actions], Gen]] = {}


def system(name_: str):
    def register(fn):
        SYSTEM[name_] = fn
        return fn

    return register


@system("drawup")
def _drawup(ctx: Ctx, actions: Actions) -> Gen:
    from engine.game import hand_size

    missing = hand_size(ctx.state, ctx.me) - len(ctx.me.hand)
    if missing > 0:
        yield from actions._draw(missing)


def _execute(ctx: Ctx) -> Gen:
    ref = ctx.ref
    state = ctx.state
    if ref.mode == "system":
        yield from SYSTEM[ref.system](ctx, Actions(ctx, ()))
        return
    inst = ctx.this_card
    if inst is None:
        return  # the card left play before its turn came (REQ-AS-30)
    if ref.mode == "play":
        yield from play_inline(ctx, inst, free=False, index=ref.index)
        return
    op = card(inst).operations[ref.index]
    impl = impl_for(inst, ref.index)
    if ref.mode == "activate" or (ref.mode == "trigger" and op.kind == "REACTION"):
        inst.exhausted = True
        state.emit(f"{ctx.me.name} uses {name(inst)}.", seat=ctx.me.seat)
    if ref.mode == "activate" and op.action_cost:
        ctx.me.actions -= 1
    if impl is None:
        state.emit(f"(Card effect not implemented yet: {op.text})", seat=ctx.me.seat)
        return
    actions = Actions(ctx, impl.uses)
    for cost in impl.costs:
        yield from cost.pay(actions)
    yield from impl.fn(ctx, actions)


def start(state: GameState, ref: OpRef) -> None:
    snapshot = state.model_dump(exclude={"running", "decision"})
    state.running = Running(ref=ref, answers=[], snapshot=snapshot)
    _resume(state)


def answer(state: GameState, option: str) -> None:
    run = state.running
    _restore(state, run.snapshot)
    state.running = Running(ref=run.ref, answers=[*run.answers, option], snapshot=run.snapshot)
    _resume(state)


def _restore(state: GameState, snapshot: dict) -> None:
    fresh = GameState.model_validate({**snapshot, "running": None, "decision": None})
    for field in GameState.model_fields:
        setattr(state, field, getattr(fresh, field))


def _resume(state: GameState) -> None:
    run = state.running
    gen = _execute(Ctx(state, run.ref))
    answers = iter(run.answers)
    try:
        ask = next(gen)
        while True:
            reply = next(answers, None)
            if reply is None:
                state.decision = Decision(seat=ask.seat, kind="op", prompt=ask.prompt,
                                          options=[Option(id=i, label=l) for i, l in ask.options], cards=ask.cards)
                return
            ask = gen.send(reply)
    except StopIteration:
        state.running = None
        _state_checks(state)


def _state_checks(state: GameState) -> None:
    """State-based PASSIVE effects, e.g. Thruster Pack is dismissed when nothing is beamed to it."""
    for p in state.players:
        for inst in list(table_cards(p)):
            check = registry.STATE_CHECKS.get(inst.card)
            if check and check(state, p, inst):
                Actions(Ctx(state, OpRef(mode="auto", seat=p.seat, uid=inst.uid)), (A.DISMISS,))._dismiss(inst)
