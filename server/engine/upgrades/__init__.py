"""Five-Year Mission upgrade bonuses, option B (requirements/22-solo-mode.md REQ-CAMP-25 to -30).

Each bonus printed on a Bot's "FIVE YEAR MISSION: UPGRADES" card is code, following CLAUDE.md "Card effects are code":

- `@boost(crew, side, index, moment=, uses=, cost=)` registers a BOOST: a generator `fn(ctx, actions)` that runs in
  every later game of the campaign, as an operation of mode "boost", at its moment: `before_hand` (before drawing the
  starting hand), `after_hand`, or `start` (no moment printed: at the start of the game, after the other Boosts).
  A Boost with a cost asks whether to pay it; one that cannot be paid is skipped.
- `@reinforce(crew, side, index)` registers a REINFORCE bonus: a query `fn(cards) -> list of pools`, each pool a list
  of the human's own crew cards (content Cards). The human picks one card from one pool, or for an "and/or" bonus at
  most one from each pool (`each=True`). The cards move to the Reinforcement pile for every later game.

`side` is "win" or "loss" and `index` the bonus's position in that section of the spec, from 0. Bonus keys look like
"pike:win:0".
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass

import engine.game  # noqa: F401  load the engine first, so the bonus modules can import engine.ops
from engine.content import content

MOMENTS = ("before_hand", "after_hand", "start")


@dataclass(frozen=True)
class BoostImpl:
    key: str
    moment: str
    fn: Callable
    uses: frozenset[str]
    costs: tuple


@dataclass(frozen=True)
class ReinforceImpl:
    key: str
    fn: Callable  # (cards) -> list[list[Card]]
    each: bool  # "X and/or Y": at most one card from each pool


BOOSTS: dict[str, BoostImpl] = {}
REINFORCES: dict[str, ReinforceImpl] = {}


def key(crew: str, side: str, index: int) -> str:
    return f"{crew}:{side}:{index}"


def boost(crew: str, side: str, index: int, *, moment: str = "start", uses=(), cost=()):
    assert moment in MOMENTS
    k = key(crew, side, index)

    def register(fn):
        BOOSTS[k] = BoostImpl(k, moment, fn, frozenset(uses), tuple(cost))
        return fn

    return register


def reinforce(crew: str, side: str, index: int, *, each: bool = False):
    k = key(crew, side, index)

    def register(fn):
        REINFORCES[k] = ReinforceImpl(k, fn, each)
        return fn

    return register


def text(bonus_key: str) -> str:
    """The printed text of a bonus."""
    crew, side, index = bonus_key.split(":")
    upgrades = content().command[crew].upgrades
    return (upgrades.win if side == "win" else upgrades.loss).bonuses[int(index)]


def load() -> None:
    """Import every crew's bonus module."""
    for crew in content().command:
        try:
            importlib.import_module(f"engine.upgrades.{crew}")
        except ModuleNotFoundError as exc:
            if exc.name != f"engine.upgrades.{crew}":
                raise


def run(ctx, bonus_key: str):
    """The "boost" operation: pay the Boost's cost if the human wants to, then resolve it."""
    from engine.ops import Actions

    load()
    impl = BOOSTS[bonus_key]
    actions = Actions(ctx, impl.uses)
    label = text(bonus_key).removeprefix("BOOST: ")
    if impl.costs:
        if not all(c.can_pay(ctx) for c in impl.costs):
            ctx.state.emit(f"Boost skipped, its cost cannot be paid: {label}", seat=ctx.me.seat)
            return
        if not (yield from actions.may(f"Use this Boost? {label}")):
            return
        for cost in impl.costs:
            yield from cost.pay(actions)
    ctx.state.emit(f"{ctx.me.name} uses a Boost: {label}", seat=ctx.me.seat)
    yield from impl.fn(ctx, actions)


# ------------------------------------------------------------------ shared queries for REINFORCE bonuses


def own(cards, *positions: str, pred: Callable = lambda c: True) -> list:
    """The crew cards at these setup positions ("Available", "Reserve") that match."""
    return [c for c in cards if c.position in positions and pred(c)]
