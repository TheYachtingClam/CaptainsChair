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

import dataclasses
import math
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager
from contextvars import ContextVar
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
    TAKE_FROM_REWARD_PILE = "TAKE_FROM_REWARD_PILE"; SWAP_JUNK_WITH_MARKET = "SWAP_JUNK_WITH_MARKET"
    REMOVE_STARDATE_GLORY = "REMOVE_STARDATE_GLORY"; DRAW_FROM_LOG = "DRAW_FROM_LOG"
    ADD_AWAY_TEAM = "ADD_AWAY_TEAM"; REORDER = "REORDER"; SHUFFLE_INTO = "SHUFFLE_INTO"
    GAIN_SPECIALTY = "GAIN_SPECIALTY"; WARP = "WARP"; SEND_AWAY_TEAM = "SEND_AWAY_TEAM"
    REMOVE_AWAY_TEAM = "REMOVE_AWAY_TEAM"; TAKE_CONTROL = "TAKE_CONTROL"; TRIGGER_CONTROL = "TRIGGER_CONTROL"
    EXHAUST = "EXHAUST"; REFRESH = "REFRESH"; FORCE = "FORCE"; ATTACK = "ATTACK"; MOVE_RESOURCES = "MOVE_RESOURCES"
    ADJUST_HAND_SIZE = "ADJUST_HAND_SIZE"


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


def suits_of(inst: Inst) -> set[str]:
    """The printed suit, plus one a SPECIAL adds ("considered a Ship for all purposes")."""
    suits = {card(inst).suit}
    if inst.card in registry.ALSO_SUIT:
        suits.add(registry.ALSO_SUIT[inst.card])
    return suits


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


def deck_face_up(p: Player) -> bool:
    """Whether the player's Draw deck is face-up (Gluonic Distortion in play)."""
    return any(i.card in registry.DECK_FACE_UP for i in table_cards(p))


def is_khan(p: Player) -> bool:
    return p.captain.card in {"2KHA01A", "2KHA01B"}


# =========================================================================== context


class Ctx:
    """Read-only queries for card code (CLAUDE.md rule 8)."""

    def __init__(self, state: GameState, ref: OpRef):
        self.state = state
        self.ref = ref
        self.me = state.player(ref.seat)
        self.opponent = state.opponent(ref.seat)
        self.event = ref.event or {}

    @property
    def event_card(self) -> Inst | None:
        """The card a trigger event is about, e.g. the card put into play or gained, wherever it is now."""
        uid = self.event.get("uid")
        return find_inst(self.state, uid) if uid else None

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
        """Printed traits plus any "treated as" modifiers (KW-TREAT)."""
        return traits_of(self.state, inst)

    def has(self, inst: Inst, trait: str) -> bool:
        """Whether the card has the trait, or is your Wildcard counting as it (REQ-TR-05)."""
        return trait_matches(inst, (trait,), state=self.state, actor=self.me.seat)

    def species(self, inst: Inst) -> set[str]:
        return self.traits(inst) & SPECIES

    def skills(self, inst: Inst, owner: Player | None = None) -> list[str]:
        printed = list(card(inst).skills)
        owner = owner or self.me
        modifier = registry.SKILLS.get(inst.card)
        if modifier and inst in table_cards(owner):
            icons = modifier(self.state, owner, inst)
        else:
            icons = [s for s in printed if s != "Variable"]
        if registry.SKILL_REWRITES:
            for source in table_cards(owner):
                rewrite = registry.SKILL_REWRITES.get(source.card)
                if rewrite:
                    icons = rewrite(self.state, owner, source, icons)
        return icons

    def incidents_from_log(self, player: Player | None = None) -> bool:
        """Whether "Incident from your hand" may also mean your Log for find, free play and return (Pike)."""
        return any(i.card in registry.INCIDENTS_FROM_LOG for i in table_cards(player or self.me))

    def hand_incidents(self, *extra_zones: str, player: Player | None = None) -> list[Inst]:
        """Incidents in your hand (and `extra_zones`), plus your Log when Pike's PASSIVE applies, to return or play."""
        player = player or self.me
        pools = zones(player)
        found = [i for z in ("hand", *extra_zones) for i in pools[z] if card(i).suit == "Incident"]
        if self.incidents_from_log(player):
            found += [i for i in player.log if card(i).suit == "Incident"]
        return found

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

    def secured_by(self, loc: Inst, player: Player | None = None) -> bool:
        """Whether a player (you by default) has secured a Location (REQ-CT-01)."""
        from engine import game

        return game.secured_by(self.state, loc, (player or self.me).seat)

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


def interchangeable(player: Player) -> bool:
    """Whether the player may spend Latinum as Dilithium and vice versa (D'Vana Tendi)."""
    return any(i.card in registry.RESOURCES_INTERCHANGEABLE for i in table_cards(player))


def can_afford(player: Player, dilithium: int = 0, latinum: int = 0, glory: int = 0) -> bool:
    if interchangeable(player):
        short = max(0, dilithium + latinum - player.dilithium - player.latinum)
        return player.glory >= glory + math.ceil(short / 2)  # 1 Glory = 2 Dilithium, which also pay for Latinum
    short_l = max(0, latinum - player.latinum)
    short_d = max(0, dilithium - player.dilithium)
    return player.glory >= glory + short_l + math.ceil(short_d / 2)


def pay_resources(player: Player, dilithium: int = 0, latinum: int = 0, glory: int = 0,
                  state: GameState | None = None) -> None:
    """Spend resources, substituting Glory where needed: 1 Glory = 1 Latinum or 2 Dilithium (KW-SPEND-02).
    With `state`, raises a spend event with what was actually paid (Barry Waddle reacts to spending Latinum)."""
    use_l = min(latinum, player.latinum)
    use_d = min(dilithium, player.dilithium)
    short_l, short_d = latinum - use_l, dilithium - use_d
    if interchangeable(player):  # D'Vana Tendi: the other resource pays first, then Glory
        cross_l = min(short_d, player.latinum - use_l)  # Latinum spent as Dilithium
        cross_d = min(short_l, player.dilithium - use_d)  # Dilithium spent as Latinum
        use_l, use_d = use_l + cross_l, use_d + cross_d
        used_g = glory + math.ceil((short_d - cross_l + short_l - cross_d) / 2)
    else:
        used_g = glory + short_l + math.ceil(short_d / 2)
    player.latinum -= use_l
    player.dilithium -= use_d
    player.glory -= used_g
    if state is not None and (use_d or use_l or used_g):
        raise_event(state, "spend", player.seat, None, dilithium=use_d, latinum=use_l, glory=used_g)


@dataclass
class Spend(Cost):
    """Spend resources, and/or available Action tokens (KW-ACT-03), as a cost."""

    dilithium: int = 0
    latinum: int = 0
    glory: int = 0
    actions: int = 0

    def can_pay(self, ctx):
        return can_afford(ctx.me, self.dilithium, self.latinum, self.glory) and ctx.me.actions >= self.actions

    def pay(self, actions):
        pay_resources(actions.ctx.me, self.dilithium, self.latinum, self.glory, actions.ctx.state)
        actions.ctx.me.actions -= self.actions
        spent = _res_text(self.dilithium, self.latinum, self.glory, self.actions)
        actions.ctx.state.emit(f"{actions.ctx.me.name} spends {spent}.", seat=actions.ctx.me.seat)
        return
        yield  # pragma: no cover


def _res_text(d=0, l=0, g=0, a=0) -> str:
    parts = [f"{n} {k}" for n, k in ((d, "Dilithium"), (l, "Latinum"), (g, "Glory"), (a, "Action(s)")) if n]
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
    """Log a card as a cost. `zones` may name hand, discard and play (your table and Staging Area, beamed too)."""

    pred: Callable[[Ctx, Inst], bool] | None = None
    label: str = "a card"
    zones: tuple[str, ...] = ("hand",)
    include_self: bool = False  # Frank Hollander may log itself

    def candidates(self, ctx):
        this = ctx.this_card
        pool: list[Inst] = []
        if "hand" in self.zones:
            pool += ctx.me.hand
        if "discard" in self.zones:
            pool += ctx.me.discard
        if "play" in self.zones:
            pool += [i for i in ctx.in_play() if i is not ctx.me.captain]
        return [i for i in pool if (self.include_self or i is not this) and (self.pred is None or self.pred(ctx, i))]

    def can_pay(self, ctx):
        return bool(self.candidates(ctx))

    def pay(self, actions):
        where = {"hand": "your hand", "discard": "your Discard pile", "play": "play"}
        text = " or ".join(where[z] for z in self.zones)
        inst = yield from actions.pick_card(f"Log {self.label} from {text} (cost).", self.candidates(actions.ctx))
        actions._log(inst)
        actions.paid.append(inst)


@dataclass
class DismissFromPlay(Cost):
    """Dismiss one of your in-play cards (not in the Staging Area, KW-DSM-04) that matches, as a cost."""

    pred: Callable[[Ctx, Inst], bool] | None = None
    label: str = "a card"

    def candidates(self, ctx):
        table = [*ctx.me.fleet, *ctx.me.duty, *ctx.me.status]
        beamed = [b for host in [*table, *ctx.me.locations] for b in _all_beamed(host)]  # beamed cards are in play
        return [i for i in [*table, *beamed] if i is not ctx.this_card and (self.pred is None or self.pred(ctx, i))]

    def can_pay(self, ctx):
        return bool(self.candidates(ctx))

    def pay(self, actions):
        inst = yield from actions.pick_card(f"Dismiss {self.label} (cost).", self.candidates(actions.ctx))
        actions._dismiss(inst)
        actions.paid.append(inst)


@dataclass
class SpendUnless(Cost):
    """Spend resources, or nothing when a condition holds: "[Dilithium] x6 OR free if ..." (development costs)."""

    spend: "Spend" = None  # type: ignore[assignment]
    free_if: Callable[[Ctx], bool] = lambda ctx: False

    def can_pay(self, ctx):
        return self.free_if(ctx) or self.spend.can_pay(ctx)

    def pay(self, actions):
        if self.free_if(actions.ctx):
            actions.emit("The development cost is waived.")
            return
        yield from self.spend.pay(actions)


@dataclass
class ExhaustCaptain(Cost):
    """Exhaust your Captain as a cost; an exhausted Captain cannot pay it (KW-EXH-04)."""

    def can_pay(self, ctx):
        return not ctx.me.captain.exhausted

    def pay(self, actions):
        actions.ctx.me.captain.exhausted = True
        actions.emit(f"{actions.ctx.me.name} exhausts their Captain.")
        raise_event(actions.state, "exhaust", actions.ctx.me.seat, actions.ctx.me.captain.uid)
        return
        yield  # pragma: no cover


@dataclass
class SpendVariable(Cost):
    """Spend an amount worked out when paying, e.g. "[Dilithium] x every 2 [Military]": `amounts(ctx)` returns the
    keyword arguments of a Spend."""

    amounts: Callable[[Ctx], dict] = lambda ctx: {}

    def can_pay(self, ctx):
        return Spend(**self.amounts(ctx)).can_pay(ctx)

    def pay(self, actions):
        yield from Spend(**self.amounts(actions.ctx)).pay(actions)


@dataclass
class EffectCost(Cost):
    """A cost that is an effect, such as William Boimler's "find 3 Person and beam them to the same Ship". `test(ctx)`
    says whether it can be paid; `effect(ctx, actions)` pays it with an Actions object holding only `uses`."""

    test: Callable[[Ctx], bool] = lambda ctx: True
    effect: Callable = None  # type: ignore[assignment]
    uses: tuple[str, ...] = ()
    label: str = ""

    def can_pay(self, ctx):
        return self.test(ctx)

    def pay(self, actions):
        yield from self.effect(actions.ctx, Actions(actions.ctx, self.uses))


@dataclass
class Condition(Cost):
    """A precondition that is checked like a cost but pays nothing, e.g. Mount Seleya's development cost "and have 1+
    Vulcan logged"."""

    test: Callable[[Ctx], bool] = lambda ctx: True
    label: str = ""

    def can_pay(self, ctx):
        return self.test(ctx)


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
    """Remove one of your Away Teams from any Location (or, with here=True, from this Location); it returns to your
    Captain."""

    here: bool = False

    def locations(self, ctx):
        if self.here:
            return [ctx.this_card] if ctx.this_card is not None and ctx.away_at(ctx.this_card) > 0 else []
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
        self._attack: bool | None = None  # result of this operation's attack check, once made
        self.in_duplicate = False  # resolving a duplicated operation: it cannot duplicate again (KW-DUP-05)
        self.skip_log_self = False  # "ignoring any effect that would log this card" (Apergosians)

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
        if len(cards) == 1 and not optional:
            return cards[0]  # nothing to decide: a required pick with one candidate
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
            top = yield from self._deck_card(player, "Draw which card from your face-up deck?")
            player.draw.remove(top)
            player.hand.append(top)
            drawn += 1
        if drawn:
            self.state.emit(f"{player.name} draws {drawn} card(s).", seat=player.seat, irreversible=True)
            # `source`: the card whose operation drew, for "after drawing cards due to Rebner's operations" (Rumdar).
            this = self.ctx.this_card
            raise_event(self.state, "draw", player.seat, None, count=drawn, source=this.uid if this else None)
        return drawn

    def _deck_card(self, player: Player, prompt: str) -> Gen:
        """The top card of the player's Draw deck, or any card of their choice while it is face-up (Gluonic
        Distortion)."""
        if len(player.draw) > 1 and deck_face_up(player):
            return (yield from self.pick_card(prompt, list(player.draw), seat=player.seat))
        return player.draw[0]
        yield  # pragma: no cover

    def discard_from_deck(self, inst: Inst | None = None) -> Gen:
        """Discard the top card of your Draw deck (Chief Engineer), cycling if it is empty, or `inst`, a deck card
        you have looked at (Deanna Troi-Riker)."""
        self._use(A.DISCARD)
        me = self.ctx.me
        if inst is None:
            if not me.draw and not (yield from self._cycle(me)):
                return None
            inst = yield from self._deck_card(me, "Discard which card from your face-up deck?")
        me.draw.remove(inst)
        me.discard.append(inst)
        self.state.emit(f"{me.name} discards {name(inst)} from the top of their deck.", irreversible=True)
        return inst

    def peek_deck(self) -> Gen:
        """Look privately at the top card of your Draw deck (Deanna Troi-Riker); any card while it is face-up. The
        card stays where it is."""
        self._use(A.PEEK)
        me = self.ctx.me
        if not me.draw and not (yield from self._cycle(me)):
            return None
        inst = yield from self._deck_card(me, "Look at which card of your face-up deck?")
        self.state.emit(f"{me.name} looks at the top card of their deck.", seat=me.seat, irreversible=True)
        self.state.emit(f"It is {name(inst)}.", seat=me.seat, private_to=me.seat)
        return inst

    def shuffle_into(self, inst: Inst) -> Gen:
        """Shuffle a card into your Draw deck (Second Contact, Dooplers)."""
        self._use(A.SHUFFLE_INTO)
        take_out(self.state, inst)
        self.ctx.me.draw.append(inst)
        self.state.shuffle(self.ctx.me.draw)
        self.state.emit(f"{self.ctx.me.name} shuffles {name(inst)} into their deck.", irreversible=True)
        return
        yield  # pragma: no cover

    def shuffle_deck(self) -> Gen:
        """Shuffle your Draw deck (Gluonic Distortion)."""
        self._use(A.SHUFFLE_INTO)
        self.state.shuffle(self.ctx.me.draw)
        self.state.emit(f"{self.ctx.me.name} shuffles their deck.", irreversible=True)
        return
        yield  # pragma: no cover

    def put_into_status(self, inst: Inst) -> Gen:
        """Put a Status card into play above the Crew board (Gluonic Distortion: "when enlisted, put it into play
        immediately", REQ-EXP-RIK-02)."""
        self._use(A.PUT)
        take_out(self.state, inst)
        self.ctx.me.status.append(inst)
        self.emit(f"{self.ctx.me.name} puts {name(inst)} into play.")
        put_into_play(self.state, self.ctx.me, inst)
        return
        yield  # pragma: no cover

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
                optional: bool = False, player: Player | None = None) -> Gen:
        """Discard from hand. With `player` set to the opponent, they discard and choose which (KW-FORCE)."""
        self._use(A.DISCARD)
        player = player or self.ctx.me
        if player is not self.ctx.me:
            self._use(A.FORCE)
        out = []
        for _ in range(n):
            this = self.ctx.this_card
            cards = [i for i in player.hand if i is not this and (pred is None or pred(i))]
            inst = yield from self.pick_card(f"Discard {label}.", cards, optional=optional, seat=player.seat)
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
        raise_event(self.state, "discard", owner.seat, inst.uid, step=self.state.step)

    def discard_top(self) -> Gen:
        self._use(A.DISCARD)
        if not self.ctx.me.draw and not (yield from self._cycle(self.ctx.me)):
            return None
        inst = self.ctx.me.draw.pop(0)
        self.ctx.me.discard.append(inst)
        self.emit(f"{self.ctx.me.name} discards {name(inst)} from the top of their deck.", irreversible=True)
        raise_event(self.state, "discard", self.ctx.me.seat, inst.uid, step=self.state.step)
        return inst

    def dismiss(self, inst: Inst) -> Gen:
        self._use(A.DISMISS)
        self._dismiss(inst)
        return
        yield  # pragma: no cover

    def _dismiss(self, inst: Inst) -> None:
        if is_protected(self.state, inst):
            self.emit(f"{name(inst)} cannot be dismissed from where it is beamed.")
            return
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        if card(inst).suit == "Location":
            self._clear_location(inst)
        dismissal_rewards(self.state, owner, inst)
        inst.at = None
        inst.exhausted = False
        inst.res.clear()
        owner.discard.extend(flatten_beamed(inst))
        owner.discard.append(inst)
        self.state.emit(f"{name(inst)} is dismissed.", seat=owner.seat)
        raise_event(self.state, "dismiss", owner.seat, inst.uid)

    def _clear_location(self, loc: Inst) -> None:
        for p in self.state.players:
            p.away_pool += loc.away.pop(p.seat, 0)
            for ship in [s for s in p.fleet if s.at == loc.uid]:
                self._dismiss(ship)

    def recall(self, inst: Inst) -> Gen:
        self._use(A.RECALL)
        if is_protected(self.state, inst):
            self.emit(f"{name(inst)} cannot be recalled from where it is beamed.")
            return
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
        if inst.card in registry.CANNOT_LOG:
            self.emit(f"{name(inst)} cannot be logged.")
            return
        if self.skip_log_self and self.ctx.this_card is not None and inst.uid == self.ctx.this_card.uid:
            self.emit(f"{name(inst)} is not logged: the duplicated effect that would log it is ignored.")
            return
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        if card(inst).suit == "Location":
            self._clear_location(inst)
        inst.at = None
        inst.exhausted = False
        inst.res.clear()
        beamed = flatten_beamed(inst)
        owner.log.extend(beamed)
        owner.log.append(inst)
        self.state.emit(f"{owner.name} logs {name(inst)}.", seat=owner.seat)
        for logged in [inst, *beamed]:
            raise_event(self.state, "log", owner.seat, logged.uid, by=self.ctx.me.seat)

    def beam(self, inst: Inst, onto: Inst) -> Gen:
        self._use(A.BEAM)
        where = take_out(self.state, inst)
        onto.beamed.append(inst)
        self.emit(f"{self.ctx.me.name} beams {name(inst)} to {name(onto)}.")
        if where.zone in ("hand", "discard"):
            put_into_play(self.state, self.ctx.me, inst, beamed=True)
        return
        yield  # pragma: no cover

    def promote(self, inst: Inst, *, as_person: bool = False) -> Gen:
        """Promote to Duty Officer. `as_person` promotes a non-Person "as if it is a Person" (The Riker Maneuver)."""
        self._use(A.PROMOTE)
        if card(inst).suit != "Person" and not as_person:
            self.emit(f"{name(inst)} is not a Person, so it cannot be promoted.")  # KW-PROM-06
            return
        if inst.card in registry.CANNOT_PROMOTE:
            self.emit(f"{name(inst)} cannot be promoted.")
            return
        if restricted(self.state, self.ctx.me, inst, "promote"):
            self.emit(f"{name(inst)} cannot be promoted: a card in play forbids it.")
            return
        where = take_out(self.state, inst)
        self.ctx.me.duty.append(inst)
        self.emit(f"{self.ctx.me.name} promotes {name(inst)} to Duty Officer.")
        if where.zone in ("hand", "discard"):
            put_into_play(self.state, self.ctx.me, inst)
        raise_event(self.state, "promote", self.ctx.me.seat, inst.uid)
        yield from self._trim_duty(self.ctx.me)

    def _trim_duty(self, player: Player) -> Gen:
        """KW-PROM-04: while a player has more Duty Officers than their slots allow, they dismiss one."""
        while not duty_fits(self.state, player, player.duty):
            fits = [i for i in player.duty if duty_fits(self.state, player, [d for d in player.duty if d is not i])]
            extra = yield from self.pick_card("You have too many Duty Officers. Dismiss one.", fits or list(player.duty),
                                              seat=player.seat)
            self._dismiss(extra)

    def deploy(self, inst: Inst) -> Gen:
        self._use(A.DEPLOY)
        if "Ship" not in suits_of(inst) and "Ongoing" not in card(inst).traits:
            self.emit(f"{name(inst)} is neither a Ship nor Ongoing, so it cannot be deployed.")  # KW-DEP-03
            return
        take_out(self.state, inst)
        inst.at = None
        self.ctx.me.fleet.append(inst)
        self.emit(f"{self.ctx.me.name} deploys {name(inst)}.")
        raise_event(self.state, "deploy", self.ctx.me.seat, inst.uid)
        return
        yield  # pragma: no cover

    def put_on_deck(self, inst: Inst, *, bottom: bool = False) -> Gen:
        """Put a card on top of its owner's Draw deck, or on the bottom (T'Ana)."""
        self._use(A.PUT)
        where = take_out(self.state, inst)
        owner = where.owner or self.ctx.me
        if bottom:
            owner.draw.append(inst)
        else:
            owner.draw.insert(0, inst)
        self.emit(f"{owner.name} puts {name(inst)} on the {'bottom' if bottom else 'top'} of their deck.")
        return
        yield  # pragma: no cover

    def take_incident(self, player: Player | None = None, *, opponent: bool = False, to: str = "hand",
                      _cost: bool = False) -> Gen:
        """Take the top Incident into hand, or `to` "discard" (Ensign Mariner) or "deck_bottom" (Solum).
        `opponent=True` makes the opponent take it instead."""
        if not _cost:
            self._use(A.TAKE_INCIDENT)
        from engine import game

        if not opponent and (player is None or player is self.ctx.me):
            from_junk = [i for i in self.state.junk if card(i).suit == "Incident"]
            if from_junk and any(i.card in registry.INCIDENTS_FROM_JUNK for i in table_cards(self.ctx.me)):
                choice = yield from self.pick_card("Take an Incident from the Junk instead of the Incident deck?",
                                                   from_junk, optional=True, none_label="Take from the Incident deck")
                if choice is not None:
                    self.state.junk.remove(choice)
                    self.ctx.me.hand.append(choice)
                    self.state.emit(f"{self.ctx.me.name} takes {name(choice)} from the Junk.", seat=self.ctx.me.seat)
                    raise_event(self.state, "take_incident", self.ctx.me.seat, choice.uid)
                    return choice
        if opponent:
            if self.ctx.opponent is None:
                if self.ctx.virtual_opponent:
                    # The virtual opponent skips the Incident and you gain 1 Glory (REQ-CTM-13).
                    self.emit("The virtual opponent skips the Incident.")
                    gain(self.state, self.ctx.me, "glory", 1)
                return None
            player = self.ctx.opponent
        taken = game.take_incident(self.state, player or self.ctx.me)
        if taken is not None and to != "hand":
            owner = player or self.ctx.me
            owner.hand.remove(taken)
            if to == "deck_bottom":
                owner.draw.append(taken)
                self.emit(f"{owner.name} puts the Incident on the bottom of their Draw deck.")
            else:
                owner.discard.append(taken)
                self.emit(f"{owner.name} puts the Incident into their Discard pile.")
        return taken

    def return_incident(self, inst: Inst) -> Gen:
        self._use(A.RETURN_INCIDENT)
        # "When you would return an Incident" replacements, e.g. Ambassador Gral (REQ-AS-27).
        if (yield from self._would(self.ctx.me.seat, {"kind": "would_return_incident", "seat": self.ctx.me.seat,
                                                      "uid": inst.uid})):
            return
        take_out(self.state, inst)
        inst.res.clear()
        self.state.incident.append(inst)
        self.emit(f"{self.ctx.me.name} returns {name(inst)} to the Incident deck.")
        raise_event(self.state, "return_incident", self.ctx.me.seat, inst.uid)

    def take_encounter(self, look: int = 1, *, to: str = "hand", bottom: bool = False) -> Gen:
        """Take the top Encounter (or choose 1 of the top `look`, the rest go to the bottom) into hand, or `to` "top" of
        your Draw deck (Infinite Diversity in Infinite Combinations). `bottom=True` takes the bottom card instead
        (Messages from Old Friends)."""
        self._use(A.TAKE_ENCOUNTER)
        if not self.state.encounter:
            return None
        top = self.state.encounter[-1:] if bottom else self.state.encounter[:look]
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
        if to == "top":
            self.ctx.me.draw.insert(0, chosen)
            self.emit(f"{self.ctx.me.name} puts the Encounter {name(chosen)} on top of their deck.", irreversible=True)
        else:
            self.ctx.me.hand.append(chosen)
            self.emit(f"{self.ctx.me.name} takes the Encounter {name(chosen)}.", irreversible=True)
        return chosen

    def junk(self, suits: Iterable[str] | None = None) -> Gen:
        """Junk a faceup Market card, of one of `suits` if given ("Junk a Person from the Market"). Refills."""
        self._use(A.JUNK)
        cards = [i for i in self.state.market.values() if i is not None and not i.res
                 and (suits is None or card(i).suit in suits)]
        inst = yield from self.pick_card("Junk a card from the Market.", cards)
        if inst and (yield from self._would(self.ctx.me.seat, {"kind": "would_junk", "seat": self.ctx.me.seat,
                                                                "uid": inst.uid})):
            return inst  # replaced, e.g. Nova Fleet gains it instead
        if inst:
            suit = card(inst).suit
            self.state.market[suit] = None
            self.state.junk.append(inst)
            self.emit(f"{self.ctx.me.name} junks {name(inst)}.")
            raise_event(self.state, "junk", self.ctx.me.seat, inst.uid, source="market")
            _refill(self.state, suit)
        return inst

    def swap_junk_with_market(self, inst: Inst) -> Gen:
        """Exchange a card in the Junk with the faceup Market card of the same suit (Plomeek Tea). A Market card with
        tokens cannot be swapped (KW-JUNK-02)."""
        self._use(A.SWAP_JUNK_WITH_MARKET)
        suit = card(inst).suit
        current = self.state.market.get(suit)
        if suit not in MARKET_SUITS or (current is not None and current.res):
            self.emit(f"{name(inst)} cannot be swapped into the Market.")
            return None
        self.state.junk.remove(inst)
        if current is not None:
            self.state.junk.append(current)
        self.state.market[suit] = inst
        self.emit(f"{self.ctx.me.name} swaps {name(inst)} from the Junk into the Market"
                  + (f", junking {name(current)}." if current is not None else "."))
        return current
        yield  # pragma: no cover

    def junk_card(self, inst: Inst) -> Gen:
        """Junk a card from your hand, Discard pile (Starbase 80) or Development pile (Knowledge of a Terrible Fate). The
        Market does not refill (KW-JUNK)."""
        self._use(A.JUNK)
        take_out(self.state, inst)
        inst.res.clear()
        self.state.junk.append(inst)
        self.emit(f"{self.ctx.me.name} junks {name(inst)}.")
        raise_event(self.state, "junk", self.ctx.me.seat, inst.uid, source="player")
        return inst
        yield  # pragma: no cover

    def take_from_reward_pile(self, n: int = 2) -> Gen:
        """Look at n random cards from the Reward pile and take one into hand (REQ-EXP-41 to -46). Returns
        (taken, the others), still in the Reward pile, for the card to destroy or keep. Uses randomness."""
        self._use(A.TAKE_FROM_REWARD_PILE)
        pool = list(self.state.rewards)
        if not pool:
            self.emit("The Reward pile is empty.")
            return None, []
        looked = self.state.rng().sample(pool, min(n, len(pool)))
        self.state.emit(f"{self.ctx.me.name} looks at {len(looked)} random card(s) from the Reward pile.",
                        seat=self.ctx.me.seat, irreversible=True)
        taken = yield from self.pick_card("Take which Reward card?", looked)
        self.state.rewards.remove(taken)
        self.ctx.me.hand.append(taken)
        self.emit(f"{self.ctx.me.name} takes {name(taken)} from the Reward pile.")
        return taken, [i for i in looked if i is not taken]

    def destroy(self, inst: Inst) -> Gen:
        """Return a card to the box: it leaves the game (KW-DES)."""
        self._use(A.DESTROY)
        if inst in self.state.rewards:
            self.state.rewards.remove(inst)
        elif locate(self.state, inst.uid) is not None:
            take_out(self.state, inst)
        self.emit(f"{name(inst)} is destroyed.")
        return
        yield  # pragma: no cover

    # ------------------------------------------------------------ gaining cards (KW-GAIN, KW-SCAN, KW-FIND)
    def gain_card(self, suits: Iterable[str] | None = None, pred: Callable[[Inst], bool] | None = None,
                  label: str = "a card", *, from_junk: bool = False, only_junk: bool = False,
                  to_hand: bool = False, optional: bool = False, deck_only: bool = False) -> Gen:
        """Gain [suit] (faceup Market card or unseen top of its deck) or gain [trait] (faceup cards only).

        `from_junk` adds the Junk as a source; `only_junk` is "gain ... from the Junk"."""
        self._use(A.GAIN_CARD)
        # "When you would gain a card" (REQ-AS-27): Lieutenant Dax replaces a Market gain; Starbase 80 adds the Junk.
        if not only_junk and suits is not None and (yield from self._would(
                self.ctx.me.seat, {"kind": "would_gain_market", "seat": self.ctx.me.seat, "uid": None,
                                   "suits": list(suits)})):
            return None
        if not only_junk and not from_junk and (yield from self._would(
                self.ctx.me.seat, {"kind": "would_gain", "seat": self.ctx.me.seat, "uid": None})):
            from_junk = True
        options: list[tuple[str, str]] = []
        from_junk = from_junk or only_junk
        if only_junk:
            pass
        elif suits is not None:
            for suit in suits:
                inst = self.state.market.get(suit)
                if inst is not None and not deck_only and (pred is None or pred(inst)):
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
        if optional:
            options.append(("none", "Gain nothing"))
        if len(options) == 1:
            inst = self._take_gained(options[0][0])  # nothing to decide
            yield from self._place_gained(inst, to_hand)
            return inst
        junk_cards = [i for i in self.state.junk if f"junk:{i.uid}" in {o for o, _ in options}]
        answer = yield from self.choose(f"Gain {label}.", options, show=junk_cards)
        if answer == "none":
            return None
        inst = self._take_gained(answer)
        yield from self._place_gained(inst, to_hand)
        return inst

    def _take_gained(self, answer: str) -> Inst:
        kind, key = answer.split(":", 1)
        if kind == "market":
            inst = self.state.market[key]
            self.state.market[key] = None
            # Every resource token on a Market card goes to the player who gains it (REQ-GN-06).
            for kind, n in sorted(inst.res.items()):
                if n:
                    gain(self.state, self.ctx.me, kind, n, source=inst)
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
        to = "hand" if to_hand else ("top" if answer == "top" else "discard")
        raise_event(self.state, "gain", self.ctx.me.seat, inst.uid, to=to)

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
        pools = {"hand": me.hand, "draw": me.draw, "discard": me.discard, "reserve": me.reserve, "log": me.log}
        this = self.ctx.this_card
        candidates = [(z, i) for z in searched for i in pools[z] if i is not this and pred(i)]
        if "hand" in searched and self.ctx.incidents_from_log():  # Pike's PASSIVE: Incidents from the Log too
            candidates += [("log", i) for i in me.log if card(i).suit == "Incident" and pred(i)]
        options = [(f"{z}:{i.uid}", f"{name(i)} ({'your ' + {'draw': 'Draw deck', 'reserve': 'Reserve deck', 'discard': 'Discard pile', 'hand': 'hand', 'log': 'Log'}[z]})")
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

    def enlist_reserve(self, *, all_cards: bool = False) -> Gen:
        """Enlist the top Reserve card onto the Draw deck, or the whole Reserve deck in its order (Founding the
        Federation)."""
        self._use(A.ENLIST_RESERVE)
        me = self.ctx.me
        cards = list(me.reserve) if all_cards else me.reserve[:1]
        for inst in reversed(cards):
            me.reserve.remove(inst)
            me.draw.insert(0, inst)
            raise_event(self.state, "enlist", me.seat, inst.uid)
        if cards:
            self.emit(f"{me.name} enlists {len(cards)} Reserve card(s).")
        return
        yield  # pragma: no cover

    def enlist_development(self, *, free: bool = False, pred: Callable[[Inst], bool] | None = None,
                           discount: bool = False) -> Gen:
        """Enlist a Development, paying its cost. `discount=True` pays 1 less Dilithium or 1 less Latinum of it
        (Rebner's Things That Make Us Smart)."""
        self._use(A.ENLIST_DEVELOPMENT)
        return (yield from self._enlist_development(free=free, pred=pred, discount=discount))

    def _enlist_development(self, *, free: bool, pred: Callable[[Inst], bool] | None = None,
                            discount: bool = False) -> Gen:
        cards = [i for i in _payable_developments(self.ctx, free=free, discount=discount) if pred is None or pred(i)]
        if not cards:
            self.emit("No Development can be enlisted.")
            return None
        inst = yield from self.pick_card("Enlist which Development?", cards)
        if not free:
            variants = [(label, costs) for label, costs in _cost_variants(registry.DEV_COSTS[inst.card], discount)
                        if all(c.can_pay(self.ctx) for c in costs)]
            costs = variants[0][1] if len(variants) == 1 else dict(variants)[
                (yield from self.choose("Pay 1 less of which resource?", [(k, k) for k, _ in variants]))]
            for cost in costs:
                yield from cost.pay(self)
        self.ctx.me.development.remove(inst)
        self.ctx.me.draw.insert(0, inst)
        self.ctx.me.enlisted.append(inst.card)
        self.emit(f"{self.ctx.me.name} enlists {name(inst)}{' for free' if free else ''}.")
        raise_event(self.state, "enlist", self.ctx.me.seat, inst.uid)
        return inst

    def free_play(self, inst: Inst) -> Gen:
        """Play a card without spending an action (KW-FREE). Other costs still apply."""
        self._use(A.FREE_PLAY)
        return (yield from play_inline(self.ctx, inst, free=True, parent=self))

    def free_play_candidates(self, pred: Callable[[Inst], bool], zones_: Iterable[str] = ("hand",),
                             cards: Iterable[Inst] | None = None) -> list[Inst]:
        """Cards that can be free played now: from the named zones of yours, or from `cards` (e.g. beamed cards)."""
        pool = list(cards) if cards is not None else [i for z in zones_ for i in zones(self.ctx.me)[z]]
        if cards is None and "hand" in zones_ and self.ctx.incidents_from_log():
            pool += [i for i in self.ctx.me.log if card(i).suit == "Incident"]  # Pike's PASSIVE
        return [i for i in pool if pred(i) and playable_indexes(self.state, self.ctx.me, i, free=True)]

    # ------------------------------------------------------------ resources, actions, tracks
    def gain_resource(self, kind: str, n: int = 1, *, source: Inst | None = None, player: Player | None = None,
                      supply: bool = False) -> Gen:
        """Gain from the supply, or from the tokens on `source` (e.g. "gain 1 Dilithium from here"). `player` makes
        someone else gain, e.g. "your opponent gains 2 Dilithium". `supply=True` is Glory "from the supply", which
        does not come off the Stardate card (Chateau Picard)."""
        self._use(A.GAIN_RESOURCE)
        gain(self.state, player or self.ctx.me, kind, n, source=source, supply=supply)
        return
        yield  # pragma: no cover

    def can_spend(self, dilithium: int = 0, latinum: int = 0, glory: int = 0, actions: int = 0) -> bool:
        return can_afford(self.ctx.me, dilithium, latinum, glory) and self.ctx.me.actions >= actions

    def spend(self, dilithium: int = 0, latinum: int = 0, glory: int = 0, actions: int = 0) -> Gen:
        """Spend as an effect. Returns False, spending nothing, when it cannot all be paid."""
        self._use(A.SPEND)
        if not self.can_spend(dilithium, latinum, glory, actions):
            return False
        pay_resources(self.ctx.me, dilithium, latinum, glory, self.state)
        self.ctx.me.actions -= actions
        self.emit(f"{self.ctx.me.name} spends {_res_text(dilithium, latinum, glory, actions)}.")
        return True
        yield  # pragma: no cover

    def place_resources(self, inst: Inst, kind: str, n: int = 1) -> Gen:
        """Put tokens from the supply on a card; Glory comes from the Stardate card if able (KW-PLACE-01)."""
        self._use(A.PLACE_RESOURCES)
        if n <= 0:
            return
        if kind == "glory":
            from engine import game

            for _ in range(n):
                if not self.state.mode == "cadet":
                    game.take_glory_from_stardate(self.state)
        inst.res[kind] = inst.res.get(kind, 0) + n
        self.emit(f"{self.ctx.me.name} places {n} {kind.capitalize()} on {name(inst)}.")
        return
        yield  # pragma: no cover

    def move_resources(self, kind: str, n: int, onto: Inst, *, source: Inst | None = None) -> Gen:
        """Move tokens onto a card, from your pool or from another card (`source`). Not spending, so Glory cannot
        substitute (KW-MOVE-01, -02). Moves as many as are available, up to n."""
        self._use(A.MOVE_RESOURCES)
        have = source.res.get(kind, 0) if source is not None else getattr(self.ctx.me, kind)
        n = min(n, have)
        if n <= 0:
            return 0
        if source is not None:
            source.res[kind] -= n
            if not source.res[kind]:
                del source.res[kind]
        else:
            setattr(self.ctx.me, kind, have - n)
        onto.res[kind] = onto.res.get(kind, 0) + n
        origin = f" from {name(source)}" if source is not None else ""
        self.emit(f"{self.ctx.me.name} moves {n} {kind.capitalize()}{origin} onto {name(onto)}.")
        return n
        yield  # pragma: no cover

    def duplicate(self, cards: list[Inst], *, label: str = "a card", optional: bool = True,
                  indexes: Iterable[int] | None = None, kind: str = "PLAY", skip_log_self: bool = False) -> Gen:
        """Resolve a `kind` operation (PLAY unless stated; Una duplicates a RESUPPLY) of one of `cards` as this card
        (KW-DUP). No extra action is spent; requirements and costs still apply; "this card" in the copied text means the duplicating card. A Duplicate resolved by a
        Duplicate does nothing (KW-DUP-05). Returns (card, index) or None."""
        self._use(A.DUPLICATE)
        if self.in_duplicate:
            self.emit("A Duplicate effect cannot duplicate another one.")
            return None
        this = self.ctx.this_card
        sub = Ctx(self.state, OpRef(mode="play", seat=self.ctx.me.seat, uid=this.uid if this else None,
                                    index=self.ctx.ref.index))
        found: dict[str, tuple[Inst, int, Any]] = {}
        options: list[tuple[str, str]] = []
        for c in cards:
            for index, op in enumerate(card(c).operations):
                impl = impl_for(c, index)
                if op.kind != kind or impl is None or (indexes is not None and index not in indexes):
                    continue
                if impl.requires and not impl.requires(sub):
                    continue
                if not all(cost.can_pay(sub) for cost in impl.costs):
                    continue
                key = f"{c.uid}:{index}"
                found[key] = (c, index, impl)
                options.append((key, f"{name(c)}: {op.text}"))
        if not options:
            self.emit(f"There is no operation of {label} that can be duplicated.")
            return None
        if optional:
            options.append(("none", "Do not duplicate"))
        answer = yield from self.choose(f"Duplicate a {kind} operation of {label}.", options, show=cards)
        if answer == "none":
            return None
        source, index, impl = found[answer]
        self.emit(f"{self.ctx.me.name} duplicates {name(source)}.")
        acts = Actions(sub, impl.uses)
        acts.in_duplicate = True
        acts.skip_log_self = skip_log_self
        for cost in impl.costs:
            yield from cost.pay(acts)
        yield from impl.fn(sub, acts)
        if card(source).operations[index].attack and acts._attack is None:
            yield from acts._attack_check()
        return source, index

    def peek_market_deck(self, suits: Iterable[str] = MARKET_SUITS) -> Gen:
        """Look privately at the top card of a Market deck; it stays there (Sarina Douglas)."""
        self._use(A.PEEK)
        decks = [s for s in suits if self.state.market_decks.get(s)]
        if not decks:
            self.emit("Every Market deck is empty.")
            return None
        suit = decks[0] if len(decks) == 1 else (
            yield from self.choose("Look at the top card of which Market deck?", [(s, f"{s} deck") for s in decks]))
        top = self.state.market_decks[suit][0]
        self.state.emit(f"{self.ctx.me.name} looks at the top card of the {suit} deck.", seat=self.ctx.me.seat)
        self.state.emit(f"You see {name(top)} on top of the {suit} deck.", private_to=self.ctx.me.seat,
                        irreversible=True)
        yield from self.choose(f"Top card of the {suit} deck (only you see it):", [("ok", "Done")], show=[top])
        return top

    def put_into_staging(self, inst: Inst) -> Gen:
        """Put a card into your Staging Area without resolving its PLAY. It counts as put into play (KW-PIP-01)."""
        self._use(A.PUT)
        take_out(self.state, inst)
        self.ctx.me.staging.append(inst)
        self.emit(f"{self.ctx.me.name} puts {name(inst)} into their Staging Area.")
        put_into_play(self.state, self.ctx.me, inst)
        return
        yield  # pragma: no cover

    def remove_stardate_glory(self, n: int) -> Gen:
        """Remove Glory from the current Stardate card to the supply; emptying it follows the usual rules (REQ-SD-02).
        Cadet Training ignores this outside your Clean-up Step (REQ-CTM-11)."""
        self._use(A.REMOVE_STARDATE_GLORY)
        from engine import game

        if self.state.mode == "cadet" and self.state.step != "cleanup":
            self.emit("Cadet Training: Glory is not removed from the Stardate card outside Clean-up.")
            return
        for _ in range(n):
            if self.state.resolution or not self.state.stardates:
                break
            game.take_glory_from_stardate(self.state)
        self.emit(f"{self.ctx.me.name} removes {n} Glory from the Stardate card.")
        return
        yield  # pragma: no cover

    def draw_from_log(self, pred: Callable[[Inst], bool] | None = None, label: str = "a card") -> Gen:
        """Take a card from your Captain's Log into hand, only when an effect says so (KW-LOG-05)."""
        self._use(A.DRAW_FROM_LOG)
        cards = [i for i in self.ctx.me.log if pred is None or pred(i)]
        inst = yield from self.pick_card(f"Take {label} from your Log.", cards)
        if inst:
            self.ctx.me.log.remove(inst)
            self.ctx.me.hand.append(inst)
            self.emit(f"{self.ctx.me.name} takes {name(inst)} from their Log.")
        return inst

    def add_away_team(self, n: int) -> Gen:
        """Move Away Teams from the set-aside supply onto your Captain (Archer, REQ-CD-ARC-01)."""
        self._use(A.ADD_AWAY_TEAM)
        moved = min(n, self.ctx.me.away_aside)
        self.ctx.me.away_aside -= moved
        self.ctx.me.away_pool += moved
        self.emit(f"{self.ctx.me.name} adds {moved} Away Team(s) to their Captain.")
        return moved
        yield  # pragma: no cover

    def put_on_reserve(self, inst: Inst) -> Gen:
        """Put a card on top of your Reserve deck, recreating it if empty (REQ-CD-ARC-02)."""
        self._use(A.PUT)
        take_out(self.state, inst)
        self.ctx.me.reserve.insert(0, inst)
        self.emit(f"{self.ctx.me.name} puts {name(inst)} on top of their Reserve deck.")
        return
        yield  # pragma: no cover

    def peek_and_reorder(self, n: int = 2) -> Gen:
        """Look at the top n cards of your Reserve deck and put each on the top or bottom, in any order (Faith of the
        Heart). Only you see them."""
        self._use(A.PEEK)
        self._use(A.REORDER)
        deck = self.ctx.me.reserve
        looked = deck[:n]
        if not looked:
            return
        self.state.emit(f"{self.ctx.me.name} looks at the top {len(looked)} card(s) of their Reserve deck.",
                        seat=self.ctx.me.seat, irreversible=True)
        top, bottom = [], []
        remaining = list(looked)
        while remaining:
            card_ = remaining[0] if len(remaining) == 1 else (
                yield from self.pick_card("Place which card next?", remaining))
            where = yield from self.choose(f"Put {name(card_)} on the top or the bottom?",
                                           [("top", "Top (placed in this order, first on top)"), ("bottom", "Bottom")],
                                           show=[card_])
            (top if where == "top" else bottom).append(card_)
            remaining.remove(card_)
        del deck[:len(looked)]
        deck[0:0] = top
        deck.extend(bottom)

    def trigger_control(self, loc: Inst) -> Gen:
        """Resolve a Location's CONTROL operation as if control had just been taken (KW-TRIG). It does not count as
        taking control, and costs no action."""
        self._use(A.TRIGGER_CONTROL)
        self.emit(f"{self.ctx.me.name} triggers the CONTROL operation of {name(loc)}.")
        yield from run_inline(self.ctx, loc, "CONTROL")

    def adjust_hand_size(self, n: int) -> Gen:
        """Temporarily change your hand size until the end of this turn (Betazed Intelligence)."""
        self._use(A.ADJUST_HAND_SIZE)
        self.ctx.me.hand_bonus += n
        self.emit(f"{self.ctx.me.name}'s hand size is {n:+d} this turn.")
        return
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
    def warp(self, ship: Inst, *, destinations: list[Inst] | None = None) -> Gen:
        """Move a Ship token to a Location: one of your controlled or a neutral Location, or `destinations`
        (Gomtuu moves an opponent's Ship to another neutral Location). The warp event belongs to the Ship's owner."""
        self._use(A.WARP)
        if destinations is None:
            extra = [i for i in table_cards(self.ctx.me) if i.card in registry.WARP_DESTINATIONS]  # Earth
            destinations = [loc for loc in [*self.ctx.me.locations, *self.state.neutral, *extra] if loc.uid != ship.at]
        dest = yield from self.pick_card(f"Warp {name(ship)} to which Location?", destinations)
        if dest is None:
            return None
        ship.at = dest.uid
        where = locate(self.state, ship.uid)
        owner = where.owner if where and where.owner else self.ctx.me
        self.emit(f"{self.ctx.me.name} warps {name(ship)} to {name(dest)}.")
        raise_event(self.state, "warp", owner.seat, ship.uid, location=dest.uid)
        return dest

    def away_targets(self, where: Callable[[Inst], bool] | None = None, *, ignore_ships: bool = False) -> list[Inst]:
        """Locations an Away Team may be sent to (KW-SEND-03). `ignore_ships` skips the opponent-Ship rule."""
        opp = self.ctx.opponent
        out = list(self.ctx.me.locations)
        def weight(ships):  # REQ-AT-02a: each Ship token counts its weight (A Fleet of 30 California-Class Ships)
            return sum(registry.SHIP_WEIGHT.get(s.card, 1) for s in ships)

        for loc in self.state.neutral:
            mine = weight(self.ctx.ships_at(loc))
            theirs = weight(self.ctx.ships_at(loc, opp)) if opp else 0
            if ignore_ships or theirs <= mine:
                out.append(loc)
        return [loc for loc in out if where is None or where(loc)]

    def send_away_team(self, n: int = 1, where: Callable[[Inst], bool] | None = None, *,
                       same_location: bool = False, target: Inst | None = None, ignore_ships: bool = False) -> Gen:
        self._use(A.SEND_AWAY_TEAM)
        me = self.ctx.me
        sent_to = target
        for _ in range(n):
            if sent_to is None or not same_location:
                targets = self.away_targets(where, ignore_ships=ignore_ships) if target is None else [target]
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
            raise_event(self.state, "send_away_team", me.seat, sent_to.uid, location=sent_to.uid,
                        controlled=sent_to in me.locations, neutral=sent_to in self.state.neutral)
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
        """Take control of a neutral Location, a Crew Location being played, or the top of the Location deck
        (Landru: no Location is revealed to replace it)."""
        self._use(A.TAKE_CONTROL)
        from engine import game

        if loc in self.state.location_deck:
            self.state.location_deck.remove(loc)
            self.ctx.me.locations.append(loc)
            self.ctx.me.controls_this_turn += 1
            self.state.emit(f"{self.ctx.me.name} takes control of {name(loc)} from the Location deck.", irreversible=True)
            put_into_play(self.state, self.ctx.me, loc)
            raise_event(self.state, "take_control", self.ctx.me.seat, loc.uid)
        elif loc in self.state.neutral:
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
        owner = locate(self.state, inst.uid)
        raise_event(self.state, "exhaust", (owner.owner or self.ctx.me).seat if owner else self.ctx.me.seat, inst.uid)
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

    def attack(self, *, removes_away_teams: bool = False) -> Gen:
        """The attack check (KW-ATK). Call it once, before the parts that target the opponent, and resolve those
        parts only if it returns True. The defender may first use a "when you would be attacked" Reaction to ignore
        the negative effect (Riva; Phasers when the attack removes Away Teams). Later calls return the same answer.

        In Cadet Training it returns True and card code resolves the effect against the virtual opponent."""
        self._use(A.ATTACK)
        return (yield from self._attack_check(removes_away_teams))

    def _attack_check(self, removes_away_teams: bool = False) -> Gen:
        if self._attack is not None:
            return self._attack
        opp = self.ctx.opponent
        if opp is None:
            self._attack = self.ctx.virtual_opponent
            if self._attack:
                self.emit(f"{self.ctx.me.name} attacks the virtual opponent.")
            return self._attack
        self.state.emit(f"{self.ctx.me.name} attacks {opp.name}.", irreversible=True)
        raise_event(self.state, "attacked", opp.seat, None, attacker=self.ctx.me.seat)
        ignored = yield from self._would(opp.seat, {"kind": "would_attack", "seat": opp.seat, "uid": None,
                                                    "attacker": self.ctx.me.seat,
                                                    "removes_away_teams": removes_away_teams})
        self._attack = not ignored
        if ignored:
            self.state.emit(f"{opp.name} ignores the negative effect of the attack.", seat=opp.seat)
        return self._attack

    def _would(self, seat: int, event: dict) -> Gen:
        """Offer `seat` their "when … would" REACTIONs for an event that has not happened yet (REQ-AS-27).

        A matching Reaction's function returns True when it replaced or cancelled the event. Returns True if one
        did. Reactions are not offered when an effect such as Pasalk blocks them (REQ-AS-31)."""
        player = self.state.player(seat)
        blocked = reactions_blocked(self.state, seat)
        while True:
            options: list[tuple[str, str]] = []
            found: dict[str, tuple[Inst, int, Any]] = {}
            sources = [] if blocked else [(i, "REACTION") for i in table_cards(player) if not i.exhausted]
            if support_window(self.state, seat):
                sources += [(i, "SUPPORT") for i in player.hand]
            for inst, kind in sources:
                for index, op in enumerate(card(inst).operations):
                    impl = impl_for(inst, index)
                    if op.kind != kind or impl is None or impl.trigger is None:
                        continue
                    sub = Ctx(self.state, OpRef(mode="trigger", seat=seat, uid=inst.uid, index=index, event=event))
                    if impl.trigger(sub, event) and (not impl.requires or impl.requires(sub)) \
                            and all(c.can_pay(sub) for c in impl.costs):
                        key = f"{inst.uid}:{index}"
                        found[key] = (inst, index, impl)
                        extra = " (SUPPORT, from hand)" if kind == "SUPPORT" else ""
                        options.append((key, f"Use {name(inst)}{extra}: {op.text}"))
            if not options:
                return False
            answer = yield from self.choose("Use a Reaction or SUPPORT card now?", options + [("none", "Do not use")],
                                            seat)
            if answer == "none":
                return False
            inst, index, impl = found[answer]
            sub = Ctx(self.state, OpRef(mode="trigger", seat=seat, uid=inst.uid, index=index, event=event))
            if card(inst).operations[index].kind == "SUPPORT":
                _support_to_staging(sub, inst)
            else:
                inst.exhausted = True
                self.state.emit(f"{player.name} uses {name(inst)}.", seat=seat)
                raise_event(self.state, "exhaust", seat, inst.uid)
            acts = Actions(sub, impl.uses)
            for cost in impl.costs:
                yield from cost.pay(acts)
            replaced = yield from impl.fn(sub, acts)
            if card(inst).operations[index].kind == "SUPPORT":
                raise_event(self.state, "support_resolved", seat, inst.uid)  # Anomaly Consolidation Day
            if replaced:
                return True

    def steal(self, kind: str, n: int = 1) -> Gen:
        """Take resources from the opponent, up to what they have (KW-STEAL). Stealing is not gaining, so no
        gain_resource event. Against the Cadet virtual opponent it takes at most 1, from the supply (REQ-CTM-12)."""
        self._use(A.STEAL)
        opp = self.ctx.opponent
        if opp is None:
            taken = min(n, 1) if self.ctx.virtual_opponent else 0
        else:
            taken = min(n, getattr(opp, kind))
            setattr(opp, kind, getattr(opp, kind) - taken)
        if taken:
            setattr(self.ctx.me, kind, getattr(self.ctx.me, kind) + taken)
        self.emit(f"{self.ctx.me.name} steals {taken} {kind.capitalize()}.")
        return taken
        yield  # pragma: no cover

    def give_incident(self, inst: Inst | None) -> Gen:
        """Give an Incident from your hand to the opponent (KW-GIVE). It counts as them taking one (KW-GIVE-03).
        To the Cadet virtual opponent: return it and gain 1 Glory instead (REQ-CTM-13)."""
        self._use(A.GIVE)
        if inst is None:
            return None
        opp = self.ctx.opponent
        take_out(self.state, inst)
        inst.res.clear()
        if opp is None:
            self.state.incident.append(inst)
            self.emit(f"{self.ctx.me.name} gives {name(inst)} to the virtual opponent: it is returned.")
            gain(self.state, self.ctx.me, "glory", 1)
            return inst
        opp.hand.append(inst)
        self.state.emit(f"{self.ctx.me.name} gives {name(inst)} to {opp.name}.", irreversible=True)
        raise_event(self.state, "take_incident", opp.seat, inst.uid)
        return inst
        yield  # pragma: no cover


# =========================================================================== shared rules used by actions


def gain(state: GameState, player: Player, kind: str, n: int, *, source: Inst | None = None,
         supply: bool = False) -> None:
    """Gain resources, from the supply or from tokens on a card (`source`). Raises a gain_resource event."""
    if n <= 0:
        return
    if source is not None:
        n = min(n, source.res.get(kind, 0))
        if n <= 0:
            return
        source.res[kind] -= n
        if not source.res[kind]:
            del source.res[kind]
        setattr(player, kind, getattr(player, kind) + n)
        state.emit(f"{player.name} gains {n} {kind.capitalize()} from {name(source)}.", seat=player.seat)
    else:
        if kind == "glory" and not supply:
            from engine import game

            game.gain_glory(state, player, n)
        else:
            setattr(player, kind, getattr(player, kind) + n)
        state.emit(f"{player.name} gains {n} {kind.capitalize()}.", seat=player.seat)
    raise_event(state, "gain_resource", player.seat, source.uid if source else None, resource=kind, amount=n)


def dismissal_rewards(state: GameState, owner: Player, inst: Inst) -> None:
    """Before a dismissed card's resources return to the supply, apply its "when dismissed, gain" PASSIVE."""
    reward = registry.DISMISS_REWARDS.get(inst.card)
    if reward is None:
        return
    for kind, n in reward(state, owner, inst).items():
        if n > 0:
            setattr(owner, kind, getattr(owner, kind) + n)
            state.emit(f"{owner.name} gains {n} {kind.capitalize()} from {name(inst)}.", seat=owner.seat)
            raise_event(state, "gain_resource", owner.seat, inst.uid, resource=kind, amount=n)


def _refill(state: GameState, suit: str) -> None:
    from engine.setup import refill_market

    refill_market(state, suit)


def support_window(state: GameState, seat: int) -> bool:
    """SUPPORT can be used only during the owner's own Action Step (REQ-EXP-31)."""
    return state.active == seat and state.step == "action"


def _support_to_staging(ctx: Ctx, inst: Inst) -> None:
    """Play a SUPPORT card from hand into the Staging Area; it counts as put into play (REQ-EXP-32, -35)."""
    take_out(ctx.state, inst)
    ctx.me.staging.append(inst)
    ctx.state.emit(f"{ctx.me.name} uses {name(inst)}'s SUPPORT from their hand.", seat=ctx.me.seat)
    put_into_play(ctx.state, ctx.me, inst)


def owned_everywhere(player: Player) -> list[Inst]:
    """Every card the player owns, in any zone, beamed cards included."""
    cards = [player.captain, *[i for z in zones(player).values() for i in z]]
    for inst in list(cards):
        cards.extend(_all_beamed(inst))
    return cards


def reactions_blocked(state: GameState, seat: int) -> bool:
    """True while the active player, not `seat`, has a card such as Vice Admiral Pasalk in play (REQ-AS-31)."""
    if state.active == seat:
        return False
    active = state.player(state.active)
    return any(i.card in registry.NO_OPPONENT_REACTIONS for i in [*table_cards(active), *active.staging])


def duty_slots(state: GameState, player: Player) -> list[tuple[str | None, str | None]]:
    """Every Duty Officer slot: (trait the officer must have or None, uid of the card providing it or None)."""
    slots: list[tuple[str | None, str | None]] = [(None, None)]  # the normal limit of 1 (KW-PROM-04)
    for inst in table_cards(player):
        slots += [(None, inst.uid)] * registry.DUTY_LIMIT.get(inst.card, 0)
    for inst, from_staging in [*((i, False) for i in table_cards(player)), *((i, True) for i in player.staging)]:
        entry = registry.DUTY_SLOTS.get(inst.card)
        if entry and entry[1] in (from_staging, "both"):
            slots += [(trait, inst.uid) for trait in entry[0](state, player, inst)]
    return slots


def duty_fits(state: GameState, player: Player, officers: list[Inst]) -> bool:
    """Whether the officers can all fill a slot. A card's extra slots are for the others, never itself (KW-PROM-04)."""
    slots = duty_slots(state, player)
    if len(officers) > len(slots):
        return False
    match: dict[int, Inst] = {}

    def place(officer: Inst, seen: set[int]) -> bool:
        for k, (trait, provider) in enumerate(slots):
            wanted = (trait,) if isinstance(trait, str) else trait
            if k in seen or provider == officer.uid or (
                    trait and not trait_matches(officer, wanted, state=state, actor=player.seat)):
                continue
            seen.add(k)
            if k not in match or place(match[k], seen):
                match[k] = officer
                return True
        return False

    return all(place(o, set()) for o in officers)


def duty_limit(state: GameState, player: Player) -> int:
    """The number of Duty Officer slots, ignoring trait limits (for display)."""
    return len(duty_slots(state, player))


def restricted(state: GameState, player: Player, target: Inst, verb: str) -> bool:
    """Whether a restriction on the player (e.g. Admiral Jarok) forbids `verb` ("play"/"promote") of target."""
    return any(registry.RESTRICTIONS[i.card](state, player, i, target, verb)
               for i in table_cards(player) if i.card in registry.RESTRICTIONS)


def traits_of(state: GameState, inst: Inst) -> set[str]:
    """Printed traits plus "treated as" modifiers from the owner's cards (KW-TREAT-02)."""
    traits = set(card(inst).traits)
    if not registry.TRAIT_MODIFIERS:
        return traits
    where = locate(state, inst.uid)
    owner = where.owner if where else None
    if owner is None:
        return traits
    for source, from_staging in [*((i, False) for i in table_cards(owner)), *((i, True) for i in owner.staging)]:
        entry = registry.TRAIT_MODIFIERS.get(source.card)
        if entry and entry[1] in (from_staging, "both"):
            traits |= set(entry[0](state, owner, source, inst))
    return traits


# --------------------------------------------------------------------------- Wildcard (REQ-TR-05 to -07)

# The player whose operation, trigger check or goal check is being evaluated, and the state. A Wildcard card counts as
# any single trait only for its owner's own checks: an opponent's effect cannot force it, and at final scoring nobody is
# acting, so it counts as no other trait (REQ-FS-11). Engine-internal, set by the runtime only.
_ACTING: ContextVar[tuple[GameState, int | None] | None] = ContextVar("acting", default=None)


@contextmanager
def acting(state: GameState, seat: int | None):
    token = _ACTING.set((state, seat))
    try:
        yield
    finally:
        _ACTING.reset(token)


def trait_matches(inst: Inst, traits: Iterable[str], *, state: GameState | None = None,
                  actor: int | None = None) -> bool:
    """Whether the card has any of the traits, including "treated as" traits, or is a Wildcard its owner may count as
    one of them. Ruling (REQ-TR-07 simplified): the owner's Wildcard always counts for the owner, without a prompt."""
    wanted = set(traits)
    current = _ACTING.get()
    if state is None and current is not None:
        state, actor = current
    elif actor is None and current is not None and current[0] is state:
        actor = current[1]
    have = traits_of(state, inst) if state is not None else set(card(inst).traits)
    if have & wanted:
        return True
    if "Wildcard" not in have or actor is None or not (wanted - {"Wildcard"}) or state is None:
        return False
    where = locate(state, inst.uid)
    return where is not None and where.owner is not None and where.owner.seat == actor


def wildcards_owned_by_actor(cards: Iterable[Inst]) -> int:
    """How many of these cards are Wildcards the acting player may count, for "different traits" counts."""
    current = _ACTING.get()
    if current is None or current[1] is None:
        return 0
    state, actor = current
    out = 0
    for inst in cards:
        if "Wildcard" in traits_of(state, inst):
            where = locate(state, inst.uid)
            out += bool(where and where.owner and where.owner.seat == actor)
    return out


def is_protected(state: GameState, inst: Inst) -> bool:
    """Whether the card is beamed to a card that protects its beamed cards (Archer's Earth)."""
    where = locate(state, inst.uid)
    return bool(where and where.zone == "beamed" and where.parent is not None
                and where.parent.card in registry.PROTECTED_BEAMED)


def over_duty_limit(state: GameState) -> Player | None:
    return next((p for p in state.players if not duty_fits(state, p, p.duty)), None)


def raise_event(state: GameState, kind: str, seat: int, uid: str | None, **data) -> None:
    state.pending_events.append({"kind": kind, "seat": seat, "uid": uid, **data})


def put_into_play(state: GameState, player: Player, inst: Inst, *, played: bool = False,
                  index: int | None = None, beamed: bool = False) -> None:
    """KW-PIP-01. `played` marks a card put into play by playing it, with the PLAY `index`, for "after playing X"
    triggers; `beamed` one put into play by beaming it."""
    raise_event(state, "put_into_play", player.seat, inst.uid, played=played, index=index, beamed=beamed)


def _cost_variants(costs, discount: bool) -> list[tuple[str, tuple]]:
    """The ways to pay a development cost: as printed, or with 1 less Dilithium or 1 less Latinum of a Spend."""
    if not discount:
        return [("", tuple(costs))]
    out = []
    for kind in ("dilithium", "latinum"):
        for i, cost in enumerate(costs):
            spend = cost.spend if isinstance(cost, SpendUnless) else cost
            if isinstance(spend, Spend) and getattr(spend, kind) > 0:
                cheaper = dataclasses.replace(spend, **{kind: getattr(spend, kind) - 1})
                if isinstance(cost, SpendUnless):
                    cheaper = dataclasses.replace(cost, spend=cheaper)
                out.append((f"1 less {kind.capitalize()}", (*costs[:i], cheaper, *costs[i + 1:])))
                break
    return out or [("", tuple(costs))]


def _payable_developments(ctx: Ctx, free: bool = False, discount: bool = False) -> list[Inst]:
    out = []
    for inst in ctx.me.development:
        costs = registry.DEV_COSTS.get(inst.card)
        if costs is None:
            continue  # development cost not implemented yet
        if free or any(all(c.can_pay(ctx) for c in cs) for _, cs in _cost_variants(costs, discount)):
            out.append(inst)
    return out


# =========================================================================== legality and running


def impl_for(inst: Inst, index: int):
    granted = registry.GRANTED_PLAYS.get(index)
    if granted is not None:
        return registry.OPS.get((granted[0], index))
    return registry.OPS.get((inst.card, index))


def op_at(inst: Inst, index: int):
    """The operation at `index`: printed, or a PLAY granted by another card (GRANTED_PLAYS)."""
    granted = registry.GRANTED_PLAYS.get(index)
    return granted[2] if granted is not None else card(inst).operations[index]


def granted_indexes(player: Player, inst: Inst) -> list[int]:
    """Indexes of PLAYs other cards grant this card now (Deanna Troi-Riker for Incidents)."""
    if not registry.GRANTED_PLAYS:
        return []
    table = {i.card for i in table_cards(player)}
    return [index for index, (source, applies, _) in registry.GRANTED_PLAYS.items() if source in table and applies(inst)]


def play_operations(player: Player, inst: Inst) -> list[tuple[int, Any]]:
    """(index, operation) for every PLAY the card has: printed ones, then granted ones."""
    printed = [(i, op) for i, op in enumerate(card(inst).operations) if op.kind == "PLAY"]
    return printed + [(i, op_at(inst, i)) for i in granted_indexes(player, inst)]


def legal(state: GameState, player: Player, inst: Inst, index: int, *, free: bool = False) -> bool:
    with acting(state, player.seat):
        return _legal(state, player, inst, index, free=free)


def _legal(state: GameState, player: Player, inst: Inst, index: int, *, free: bool = False) -> bool:
    impl = impl_for(inst, index)
    op = op_at(inst, index)
    if index in registry.GRANTED_PLAYS and index not in granted_indexes(player, inst):
        return False
    if impl is None:
        return True  # placeholder operation
    ctx = Ctx(state, OpRef(mode="play", seat=player.seat, uid=inst.uid, index=index))
    if op.action_cost and not free and player.actions <= 0:
        return False
    if impl.requires and not impl.requires(ctx):
        return False
    if op.kind == "PLAY" and restricted(state, player, inst, "play"):
        return False
    return all(cost.can_pay(ctx) for cost in impl.costs)


def playable_indexes(state: GameState, player: Player, inst: Inst, *, free: bool = False) -> list[int]:
    return [i for i, _ in play_operations(player, inst) if legal(state, player, inst, i, free=free)]


def play_inline(ctx: Ctx, inst: Inst, *, free: bool, parent: Actions | None = None, index: int | None = None) -> Gen:
    """Play a card from wherever it is now: move to the Staging Area, pay, resolve (REQ-AS-11)."""
    state = ctx.state
    indexes = playable_indexes(state, ctx.me, inst, free=free) if index is None else [index]
    if not indexes:
        return None
    if index is None and len(indexes) > 1:
        options = [(str(i), op_at(inst, i).text or "PLAY") for i in indexes]
        index = int((yield from Actions(ctx, ()).choose(f"Which PLAY operation of {name(inst)}?", options)))
    elif index is None:
        index = indexes[0]
    op = op_at(inst, index)
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
        if op.attack and actions._attack is None:
            yield from actions._attack_check()  # an ATTACK operation always counts as an attack (KW-ATK-01)
    where = locate(state, inst.uid)
    if where is not None and where.zone not in ("hand", "draw", "discard", "reserve", "log"):
        # Not when the effect moved the card away again, e.g. Hostile Contact returning itself.
        put_into_play(state, ctx.me, inst, played=True, index=index)
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


@system("duty_trim")
def _duty_trim(ctx: Ctx, actions: Actions) -> Gen:
    """A player has more Duty Officers than their slots allow, e.g. Illyrians left the Staging Area."""
    yield from actions._trim_duty(ctx.me)


@system("drawup")
def _drawup(ctx: Ctx, actions: Actions) -> Gen:
    from engine.game import hand_size

    missing = hand_size(ctx.state, ctx.me) - len(ctx.me.hand)
    if missing > 0:
        yield from actions._draw(missing)


def completable_missions(state: GameState, player: Player) -> list:
    """Missions on the player's board whose GOAL is met now and that are not completed (REQ-MS-05, -07, -09)."""
    with acting(state, player.seat):
        return _completable_missions(state, player)


def _completable_missions(state: GameState, player: Player) -> list:
    board = content().boards[player.board]
    if len(player.missions_completed) >= player.mission_tokens:
        return []
    ctx = Ctx(state, OpRef(mode="mission", seat=player.seat))
    out = []
    for mission in board.missions:
        impl = registry.MISSIONS.get(mission.id)
        if mission.id in player.missions_completed or impl is None or impl.goal is None or impl.reward is None:
            continue
        if impl.goal(ctx) is not None:
            out.append(mission)
    return out


def _complete_mission(ctx: Ctx, mission_id: str) -> Gen:
    """REQ-MS-06: find the contributors, resolve the REWARD, dismiss contributors that are beamed afterwards, and
    place a Mission Completion token."""
    impl = registry.MISSIONS[mission_id]
    mission = next(m for m in content().boards[ctx.me.board].missions if m.id == mission_id)
    contributors = impl.goal(ctx)
    if contributors is None:
        ctx.state.emit(f"The goal of {mission.name} is no longer met.", seat=ctx.me.seat)
        return
    ctx.state.emit(f"{ctx.me.name} completes the mission {mission.name}.", seat=ctx.me.seat, irreversible=True)
    actions = Actions(ctx, impl.uses)
    yield from impl.reward(ctx, actions)
    for inst in contributors:
        where = locate(ctx.state, inst.uid)
        if where is not None and where.zone == "beamed" and not is_protected(ctx.state, inst):
            actions._dismiss(find_inst(ctx.state, inst.uid))
    ctx.me.missions_completed.append(mission_id)
    raise_event(ctx.state, "mission_completed", ctx.me.seat, None, mission=mission_id)


def _execute(ctx: Ctx) -> Gen:
    ref = ctx.ref
    state = ctx.state
    if ref.mode == "system":
        yield from SYSTEM[ref.system](ctx, Actions(ctx, ()))
        return
    if ref.mode == "mission":
        yield from _complete_mission(ctx, ref.system)
        return
    inst = ctx.this_card
    if inst is None:
        return  # the card left play before its turn came (REQ-AS-30)
    if ref.mode == "play":
        yield from play_inline(ctx, inst, free=False, index=ref.index)
        return
    op = op_at(inst, ref.index)
    impl = impl_for(inst, ref.index)
    if ref.mode == "activate" or (ref.mode == "trigger" and op.kind == "REACTION"):
        inst.exhausted = True
        state.emit(f"{ctx.me.name} uses {name(inst)}.", seat=ctx.me.seat)
        raise_event(state, "exhaust", ctx.me.seat, inst.uid)
    if ref.mode == "trigger" and op.kind == "SUPPORT":
        _support_to_staging(ctx, inst)
    if ref.mode == "activate" and op.action_cost:
        ctx.me.actions -= 1
    if impl is None:
        state.emit(f"(Card effect not implemented yet: {op.text})", seat=ctx.me.seat)
        return
    actions = Actions(ctx, impl.uses)
    for cost in impl.costs:
        yield from cost.pay(actions)
    yield from impl.fn(ctx, actions)
    if op.attack and actions._attack is None:
        yield from actions._attack_check()  # an ATTACK operation always counts as an attack (KW-ATK-01)


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
    with acting(state, state.running.ref.seat):
        _resume_inner(state)


def _resume_inner(state: GameState) -> None:
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
        ref = run.ref
        inst = find_inst(state, ref.uid) if ref.uid else None
        if ref.mode == "trigger" and inst is not None and ref.index is not None \
                and op_at(inst, ref.index).kind == "SUPPORT":
            raise_event(state, "support_resolved", ref.seat, inst.uid)  # Anomaly Consolidation Day
        _state_checks(state)


def _state_checks(state: GameState) -> None:
    """State-based PASSIVE effects, e.g. Thruster Pack is dismissed when nothing is beamed to it."""
    for p in state.players:
        for inst in list(table_cards(p)):
            check = registry.STATE_CHECKS.get(inst.card)
            if check and check(state, p, inst):
                Actions(Ctx(state, OpRef(mode="auto", seat=p.seat, uid=inst.uid)), (A.DISMISS,))._dismiss(inst)
