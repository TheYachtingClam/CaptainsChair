"""The Bot in solo mode (requirements/22-solo-mode.md).

The Bot's turn runs inside the turn loop as the "bot" step. It never asks the Bot anything: every Bot choice follows
the fixed rules, so the engine runs the whole turn and stops only when the human must decide something. Each step is
logged in plain words so the human can follow it (REQ-SOLO-05).

Automated Command rows arrive in plans/solo-mode.md Step 2. Until then a resolved card just stays in the Staging Area,
except a Location, which goes to the Control Area (REQ-SOLO-89).
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.content import MARKET_SUITS, content
from engine.state import GameState, Inst, Player

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
            resolve(state, bot, inst)
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
    resolve(state, bot, location)


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


def resolve(state: GameState, bot: Player, inst: Inst) -> None:
    """Resolve a Bot card with its Automated Command cards. Placeholder until plans/solo-mode.md Step 2: the card has
    no effect, but a Location still goes to the Control Area (REQ-SOLO-89)."""
    card = content().cards[inst.card]
    state.emit(f"{bot.name} resolves {card.name}: no Automated Command row yet.", seat=bot.seat)
    if card.suit == "Location" and inst in bot.staging:
        bot.staging.remove(inst)
        bot.locations.append(inst)
        state.emit(f"{card.name} goes to {bot.name}'s Control Area.", seat=bot.seat)


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


def answer(state: GameState) -> str:
    """The option the Bot picks when a human card puts a choice to it: the first listed one (REQ-SOLO-112). Plans Step
    3 refines this (declining to return Incidents, attacks on its hand)."""
    return state.decision.options[0].id
