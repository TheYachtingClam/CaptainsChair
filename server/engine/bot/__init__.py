"""The Bot in solo mode (requirements/22-solo-mode.md).

The Bot's turn runs inside the turn loop as the "bot" step. It never asks the Bot anything: every Bot choice follows
the fixed rules, so the engine runs the whole turn and stops only when the human must decide something. Each step is
logged in plain words so the human can follow it (REQ-SOLO-05).

Each card the Bot resolves runs as an operation of mode "bot" (`resolve_op`), so a row that asks the human something
pauses and replays like any card operation. Rows are code, one function per row, in `engine/bot/<crew>.py`.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import engine.game  # noqa: F401 - loads the card registry in the right order before the Crew row modules
from engine.content import MARKET_SUITS, content
from engine.state import GameState, Inst, OpRef, Player


# =========================================================================== registries


@dataclass(frozen=True)
class RowImpl:
    crew: str
    side: str  # traits | no_duty_officer | with_duty_officer
    number: int
    fn: Callable
    uses: frozenset[str]


ROWS: dict[tuple[str, str, int], RowImpl] = {}
SIDE_NAMES = {"traits": "TRAITS", "no_duty_officer": "SUITS WITH NO DUTY OFFICER",
              "with_duty_officer": "SUITS WITH DUTY OFFICER"}
# Crew special rules that are data: card traits discarded instead of logged when logging the top of the Bot deck
# (Soval: Path of Surak; Freeman: Lower Decker), and value bonuses for the Bot (Riker, Freeman).
LOG_TOP_DISCARDS: dict[str, tuple[str, ...]] = {}
VALUE_BONUS: dict[str, Callable[[Inst], int]] = {}
# Crew special rules run before the matching row, with the Bot actions they need (Pike: gain on a Specialty track).
ON_RESOLVE: dict[str, tuple[Callable, tuple[str, ...]]] = {}


def row(crew: str, side: str, number: int, *, uses=()):
    """Register one Automated Command row: `fn(ctx, actions)` generator, with `actions` a BotActions holding only the
    `uses` actions. `number` is the row's number on the card side, as in the spec."""

    def register(fn):
        ROWS[(crew, side, number)] = RowImpl(crew, side, number, fn, frozenset(uses))
        return fn

    return register

TRACKS = ("research", "influence", "military")  # the Bot's tie order: topmost first (REQ-SOLO-85)


def is_bot(player: Player | None) -> bool:
    return player is not None and player.bot is not None


def bot_of(state: GameState) -> Player | None:
    return next((p for p in state.players if p.bot is not None), None)


def _name(inst: Inst) -> str:
    return content().cards[inst.card].name


# =========================================================================== value (REQ-SOLO-40 to -43)


def value(state: GameState, inst: Inst, player: Player) -> int:
    """How many VP the card would score for `player` if the game ended just after gaining it: printed VP, plus the
    player's current multiplier for each Focus icon, plus 5 for an ENDGAME operation, plus 1 per Glory on it.

    The Bot uses its own multipliers; "value to you" passes the human (REQ-SOLO-42)."""
    from engine.scoring import printed_vp

    data = content()
    card = data.cards[inst.card]
    board = data.boards[player.board]
    multipliers = {t: board.multiplier(t, player.highest[t]) for t in TRACKS}
    total = printed_vp(card.vp)
    if player.bot is not None and player.bot.crew in VALUE_BONUS:
        total += VALUE_BONUS[player.bot.crew](inst)  # Riker, Freeman: some traits are worth 1 more to the Bot
    if card.focus == "Best":
        total += max(multipliers.values(), default=0)
    elif card.focus and card.focus.lower() in multipliers:
        total += multipliers[card.focus.lower()]
    if any(op.kind == "ENDGAME" for op in card.operations):
        total += 5
    return total + inst.res.get("glory", 0)


def _tokens(inst: Inst) -> int:
    return sum(inst.res.values())


def most_valuable(state: GameState, cards: Iterable[Inst], player: Player) -> Inst | None:
    """The most valuable card to `player`. Ties: more resource tokens, then the leftmost, meaning the first in `cards`
    (REQ-SOLO-41)."""
    best = None
    for inst in cards:
        if best is None or (value(state, inst, player), _tokens(inst)) > (value(state, best, player), _tokens(best)):
            best = inst
    return best


def least_valuable(state: GameState, cards: Iterable[Inst], player: Player) -> Inst | None:
    """The least valuable card to `player`. Ties: fewer resource tokens, then the leftmost (REQ-SOLO-41, -59)."""
    best = None
    for inst in cards:
        if best is None or (value(state, inst, player), _tokens(inst)) < (value(state, best, player), _tokens(best)):
            best = inst
    return best


def market_cards(state: GameState) -> list[Inst]:
    """The faceup Market cards, left to right."""
    return [state.market[s] for s in MARKET_SUITS if state.market.get(s) is not None]


# =========================================================================== the Bot's turn (REQ-SOLO-50 to -61)


def step_bot(state: GameState) -> None:
    """One part of the Bot's turn per call; card operations and human decisions run in between."""
    bot = state.player(state.active)
    if state.substep == "control":
        state.substep = "draw"
        _control(state, bot)
    elif state.substep == "draw":
        state.substep = "resolve"
        _draw_actions(state, bot)
    elif state.substep == "resolve":
        if bot.bot.facedown:
            uid = bot.bot.facedown.pop(0)
            inst = next(i for i in bot.staging if i.uid == uid)
            state.emit(f"{bot.name} flips {_name(inst)}.", seat=bot.seat, irreversible=True)
            queue_resolution(state, bot, inst)
        else:
            state.substep = "cleanup"
    elif state.substep == "cleanup":
        _cleanup(state, bot)


def _control(state: GameState, bot: Player) -> None:
    """REQ-SOLO-51, -52: take control of the most valuable secured Location, then resolve it."""
    from engine.game import secured_by, take_control

    secured = [loc for loc in state.neutral if secured_by(state, loc, bot.seat)]
    location = most_valuable(state, secured, bot)
    if location is None:
        state.emit(f"{bot.name} has not secured a Location.", seat=bot.seat)
        return
    take_control(state, bot, location, run_control=False)  # the Bot ignores the card's CONTROL text
    queue_resolution(state, bot, location)


def bot_actions(state: GameState) -> int:
    """The Bot actions on the current Stardate card (REQ-SOLO-11)."""
    if not state.stardates:
        return 0
    return content().cards[state.stardates[0].card].bot_actions or 0


def draw_card(state: GameState, bot: Player) -> Inst | None:
    """The top card of the Bot deck, reshuffling the Bot Discard pile (not the Staging Area) and adding the top
    Supplement card when it is empty (REQ-SOLO-60 to -62)."""
    from engine.game import cycle_deck

    if not bot.draw and not cycle_deck(state, bot):
        return None
    return bot.draw.pop(0)


def _draw_actions(state: GameState, bot: Player) -> None:
    """REQ-SOLO-53: draw one card per Bot action, facedown in a row in the Staging Area."""
    n = bot_actions(state)
    drawn = 0
    for _ in range(n):
        inst = draw_card(state, bot)
        if inst is None:
            break
        bot.staging.append(inst)
        bot.bot.facedown.append(inst.uid)
        drawn += 1
    state.emit(f"{bot.name} has {n} action(s) and draws {drawn} card(s) facedown.", seat=bot.seat, irreversible=True)


def queue_resolution(state: GameState, bot: Player, inst: Inst) -> None:
    """Resolve a Bot card as an operation, so human questions inside it pause and replay."""
    state.op_queue.append(OpRef(mode="bot", seat=bot.seat, uid=inst.uid))


def resolve_op(ctx) -> Iterable:
    """The "bot" operation: resolve ctx.this_card with the Automated Command cards."""
    inst = ctx.this_card
    if inst is not None:
        yield from resolve(ctx, inst)


def _rows_for(bot: Player, inst: Inst, side_key: str):
    crew = content().command[bot.bot.crew]
    side = crew.side(side_key)
    return list(side.rows) if side else []


def resolve(ctx, inst: Inst) -> Iterable:
    """REQ-SOLO-82, -87, -120, -121: SURPRISE first; otherwise the first TRAITS row with one of the card's traits (a
    Wildcard matches every trait row, in order); otherwise the card's suit row on the SUITS side face up. "Continue
    resolution" moves on to the next match. Afterwards a Location still in the Staging Area goes to the Control Area
    (REQ-SOLO-89)."""
    from engine.bot.actions import BotActions
    from engine.ops import Ctx

    state, bot = ctx.state, ctx.me
    card = content().cards[inst.card]
    sub = Ctx(state, OpRef(mode="bot", seat=bot.seat, uid=inst.uid))
    special = ON_RESOLVE.get(bot.bot.crew)
    if special is not None:
        fn, uses = special
        yield from fn(sub, BotActions(sub, uses, inst, lambda other: resolve(ctx, other)))
    if "Surprise" in card.traits:
        yield from _surprise(sub, inst)
    else:
        traits = set(card.traits)
        wildcard = "Wildcard" in traits
        trait_rows = [r for r in _rows_for(bot, inst, "traits") if "Surprise" not in r.matches
                      and (wildcard or traits & set(r.matches))]
        resolved_any = False
        for r in trait_rows + [None]:  # None: the SUITS row, looked up when reached (the side may have flipped)
            if r is None:
                side = bot.bot.suits_side
                r = next((x for x in _rows_for(bot, inst, side) if card.suit in x.matches), None)
                if r is None:
                    break
            else:
                side = "traits"
            impl = ROWS.get((bot.bot.crew, side, r.number))
            state.emit(f"{card.name} matches {' / '.join(r.matches)} (row {r.number} of {SIDE_NAMES[side]}).",
                       seat=bot.seat)
            resolved_any = True
            if impl is None:
                state.emit("(This Automated Command row is not implemented yet.)", seat=bot.seat)
                break
            actions = BotActions(sub, impl.uses, inst, lambda other: resolve(ctx, other))
            yield from impl.fn(sub, actions)
            if not actions.continued:
                break
        if not resolved_any:
            state.emit(f"{card.name} matches no Automated Command row.", seat=bot.seat)
    if card.suit == "Location" and inst in bot.staging:
        bot.staging.remove(inst)
        bot.locations.append(inst)
        state.emit(f"{card.name} goes to {bot.name}'s Control Area.", seat=bot.seat)


def _surprise(ctx, inst: Inst) -> Iterable:
    """REQ-SOLO-87: a card with the Surprise trait resolves its own SURPRISE (Bot only) operation instead."""
    from engine import cards as registry
    from engine.ops import Actions

    card = content().cards[inst.card]
    index = next((k for k, op in enumerate(card.operations) if op.kind == "SURPRISE"), None)
    impl = registry.OPS.get((inst.card, index)) if index is not None else None
    ctx.state.emit(f"{card.name} has the Surprise trait: the Bot resolves its SURPRISE operation.", seat=ctx.me.seat)
    if impl is None:
        ctx.state.emit("(This SURPRISE operation is not implemented yet.)", seat=ctx.me.seat)
        return
    yield from impl.fn(ctx, Actions(ctx, impl.uses))


def _cleanup(state: GameState, bot: Player) -> None:
    """REQ-SOLO-57 to -59: a held Stardate's effect, discard the Staging Area, place 1 Glory on the Market card least
    valuable to the human."""
    from engine.game import end_turn, take_glory_from_stardate, wipe_market, wipe_neutral_zone

    for stardate in bot.received_stardates:
        text = next((op.text or "" for op in content().cards[stardate.card].operations
                     if op.kind == "STARDATE RESOLUTION"), "")
        if text:
            wipe_market(state)
            if "neutral Location" in text:
                wipe_neutral_zone(state)
    bot.received_stardates = []
    bot.discard.extend(bot.staging)
    bot.staging = []
    bot.bot.facedown = []
    human = next(p for p in state.players if p.bot is None)
    target = least_valuable(state, market_cards(state), human)
    if target is not None:
        take_glory_from_stardate(state)
        target.res["glory"] = target.res.get("glory", 0) + 1
        state.emit(f"{bot.name} places 1 Glory on {_name(target)}, the Market card least valuable to "
                   f"{human.name}.", seat=bot.seat)
    end_turn(state)


# =========================================================================== choices put to the Bot


DECLINE = ("none", "no", "pass", "stop")


def answer(state: GameState) -> str:
    """The option the Bot picks when a human card puts a choice to it (REQ-SOLO-111, -112, -166, -187):

    - it declines any chance to return an Incident;
    - asked which of its Ships to give up, it picks the most recently deployed one;
    - otherwise it takes the first option it can legally resolve, which is the first one listed (the engine only
      lists legal options), even if that option does nothing."""
    decision = state.decision
    ids = [o.id for o in decision.options]
    prompt = decision.prompt.lower()
    if "return" in prompt and "incident" in prompt:
        decline = next((i for i in ids if i in DECLINE), None)
        if decline is not None:
            return decline
    bot = state.player(decision.seat)
    fleet = [s.uid for s in bot.fleet]
    ships = [i for i in ids if i in fleet]
    if ships and len(ships) == len([i for i in ids if i not in DECLINE]):
        return max(ships, key=fleet.index)
    return ids[0]


def load_rows() -> None:
    """Import every Crew module in engine/bot so its rows register."""
    for mod in pkgutil.iter_modules(__path__):
        if mod.name != "actions":
            importlib.import_module(f"{__name__}.{mod.name}")


load_rows()
