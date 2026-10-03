"""Build games in a known position for card tests (plans/card-implementation.md, Step 1).

    s = given(deck="georgiou", hand=["2PER07"], duty=["2PER01"], tracks={"military": 3}, dilithium=2)
    play(s, card(s, "2PER07"), 0)
    answer(s, "Research")

`given` starts a game, moves to seat 0's Action Step, then sets up the position with developer
commands (engine/dev.py), so it builds exactly what the developer panel would.
"""

from __future__ import annotations

from engine import dev
from engine.content import content
from engine.game import advance, choose
from engine.setup import SeatSetup, new_game
from engine.state import GameState, Inst

ZONE_ARGS = ("hand", "staging", "duty", "fleet", "locations", "discard", "draw", "log")


def given(deck: str = "georgiou", *, opponent: str | None = "soval", mode: str = "two_player", seed: int = 1,
          expansions: list[str] | None = None, promos: bool = False, empty_hand: bool = False,
          opp: dict | None = None, tracks: dict[str, int] | None = None, **zones_and_resources) -> GameState:
    """A game at seat 0's Action Step.

    Keyword arguments named after zones (hand, staging, duty, fleet, locations, discard, draw, log) take
    lists of card ids to add. dilithium, latinum, glory and actions add to the pool. `opp` takes the same
    keywords for seat 1. `empty_hand=True` discards the starting hand first.
    """
    if mode == "cadet":
        opponent = None
    seats = [SeatSetup("Me", deck, "basic")] + ([SeatSetup("Opp", opponent, "basic")] if opponent else [])
    state = new_game(seed, mode, seats, expansions, promos)
    state.active = state.first_seat = 0
    advance(state)
    while not (state.decision.kind == "action" and state.decision.seat == 0):
        d = state.decision
        choose(state, d.seat, {"action": "end", "discard": "done", "control": "skip"}.get(d.kind, d.options[0].id))
    if empty_hand:
        me = state.player(0)
        me.discard.extend(me.hand)
        me.hand.clear()
    _setup(state, 0, tracks=tracks, **zones_and_resources)
    if opp:
        _setup(state, 1, **opp)
    return state


def _setup(state: GameState, seat: int, *, tracks: dict[str, int] | None = None, **kw) -> None:
    for zone in ZONE_ARGS:
        for card_id in kw.pop(zone, []):
            dev.apply(state, seat, {"kind": "card", "card": card_id, "zone": zone})
    for resource in dev.RESOURCES:
        if kw.get(resource):
            dev.apply(state, seat, {"kind": "resource", "resource": resource, "amount": kw.pop(resource)})
    for track, amount in (tracks or {}).items():
        dev.apply(state, seat, {"kind": "track", "track": track, "amount": amount})
    unknown = set(kw) - set(dev.RESOURCES)
    if unknown:
        raise TypeError(f"Unknown setup arguments {sorted(unknown)}")


def card(state: GameState, card_id: str, seat: int = 0) -> Inst:
    """The newest copy of a card owned by the seat, wherever it is."""
    from engine.ops import zones

    found = [i for z in zones(state.player(seat)).values() for i in z if i.card == card_id]
    if not found:
        raise LookupError(f"{card_id} not found for seat {seat}")
    return max(found, key=lambda i: int(i.uid[1:]))


def options(state: GameState) -> list[str]:
    return [o.label for o in state.decision.options]


def answer(state: GameState, text: str) -> None:
    """Answer the current question with the option whose label contains `text`."""
    d = state.decision
    match = [o for o in d.options if text in o.label]
    assert match, f"no option {text!r} in {[o.label for o in d.options]} ({d.prompt})"
    choose(state, d.seat, match[0].id)


def play(state: GameState, inst: Inst, index: int) -> None:
    choose(state, state.decision.seat, f"play:{inst.uid}:{index}")


def activate(state: GameState, inst: Inst, index: int) -> None:
    choose(state, state.decision.seat, f"activate:{inst.uid}:{index}")


def can_play(state: GameState, inst: Inst, index: int) -> bool:
    return f"play:{inst.uid}:{index}" in {o.id for o in state.decision.options}


def name(card_id: str) -> str:
    return content().cards[card_id].name
