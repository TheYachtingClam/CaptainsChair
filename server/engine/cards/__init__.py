"""Card behaviour registry (CLAUDE.md "Card effects are code").

Card code lives in one module per card under engine/cards/<set>/<slug>.py. A module registers:

- @operation(ids, index, uses=..., cost=..., requires=..., trigger=...) for each printed operation,
  where `index` is the operation's position in the card spec;
- @development_cost(ids, *costs), @endgame(ids), and continuous PASSIVE modifiers.

Operations that are not registered fall back to a placeholder in the engine.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from engine.state import GameState, Inst, Player


def _ids(card_ids: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return (card_ids,) if isinstance(card_ids, str) else tuple(card_ids)


@dataclass(frozen=True)
class OpImpl:
    card_id: str
    index: int
    fn: Callable
    uses: frozenset[str]
    costs: tuple[Any, ...] = ()
    requires: Callable | None = None  # (ctx) -> bool; "Requires ..." preconditions (KW-REQ)
    trigger: Callable | None = None  # (ctx, event) -> bool; for REACTION and triggered PASSIVE operations


OPS: dict[tuple[str, int], OpImpl] = {}


@dataclass
class MissionImpl:
    """A Crew board mission: GOAL check and REWARD (REQ-MS-01). Keyed by the mission id from boards.yaml."""

    mission_id: str
    goal: Callable | None = None  # (ctx) -> list of contributing cards when met, or None
    reward: Callable | None = None  # generator (ctx, actions)
    uses: frozenset[str] = frozenset()


MISSIONS: dict[str, MissionImpl] = {}
DEV_COSTS: dict[str, tuple[Any, ...]] = {}
ENDGAME: dict[str, Callable[["GameState", "Player"], int]] = {}
# Continuous PASSIVE modifiers. They apply only while the card is in a table position (REQ-AS-21).
HAND_SIZE: dict[str, Callable[["GameState", "Player", int], int]] = {}
DUTY_LIMIT: dict[str, int] = {}  # extra Duty Officers allowed while this card is on duty
SKILLS: dict[str, Callable[["GameState", "Player", "Inst"], list[str]]] = {}  # replaces "Variable" icons
SCANS_INCLUDE_JUNK: set[str] = set()
STATE_CHECKS: dict[str, Callable[["GameState", "Player", "Inst"], bool]] = {}  # True = dismiss the card
# Extra Duty Officer slots: fn(state, owner, inst) -> list of slots, each None (any Person) or a trait the officer
# must have. From table positions, or from the Staging Area when registered with staging=True.
DUTY_SLOTS: dict[str, tuple[Callable, bool]] = {}
# Restrictions on the owner: fn(state, owner, inst, target, verb) -> True when `verb` ("play" or "promote") of `target`
# is not allowed. Table positions only.
RESTRICTIONS: dict[str, Callable] = {}
# "Treated as": fn(state, owner, inst, target) -> extra traits for one of the owner's cards. Table positions, or the
# Staging Area when registered with staging=True.
TRAIT_MODIFIERS: dict[str, tuple[Callable, bool]] = {}
# SPECIAL "This card is considered a [suit] for all purposes" (Gomtuu, Species 10-C): card id -> extra suit.
ALSO_SUIT: dict[str, str] = {}
# PASSIVE "When taking an Incident, you may take it from the Junk" (Starbase 80). Table positions.
INCIDENTS_FROM_JUNK: set[str] = set()
# SPECIAL "This card cannot be promoted" (Ensign Boimler, Ensign Mariner).
CANNOT_PROMOTE: set[str] = set()
# Asterisk VP: fn(state, player, inst) -> the card's VP at final scoring, wherever it is (REQ-FS-02 component 4).
VP_SPECIAL: dict[str, Callable] = {}
# PASSIVE "Ship can warp here" on a non-Location card (Archer's Earth). Table positions.
WARP_DESTINATIONS: set[str] = set()
# PASSIVE "Cards beamed here cannot be recalled or dismissed, not even when contributing to a Mission" (Earth).
PROTECTED_BEAMED: set[str] = set()
# SPECIAL "before scoring": card ids whose SPECIAL operation runs at the start of final scoring, wherever the owner
# has the card (Su'Kal).
BEFORE_SCORING: set[str] = set()
# SPECIAL: while this card is in its owner's play (not beamed), the opponent cannot use REACTIONs on the owner's turn.
NO_OPPONENT_REACTIONS: set[str] = set()
# Resources a player gains when this card is dismissed, instead of the usual return to the supply (R.I.S. Talvath).
DISMISS_REWARDS: dict[str, Callable[["GameState", "Player", "Inst"], dict[str, int]]] = {}


def operation(card_ids, index: int, *, uses=(), cost=(), requires=None, trigger=None):
    def register(fn):
        for cid in _ids(card_ids):
            OPS[(cid, index)] = OpImpl(cid, index, fn, frozenset(uses), tuple(cost), requires, trigger)
        return fn

    return register


def mission_goal(mission_id: str):
    """GOAL: fn(ctx) -> the cards that meet it (beamed ones are dismissed on completion, REQ-MS-06), or None."""

    def register(fn):
        MISSIONS.setdefault(mission_id, MissionImpl(mission_id)).goal = fn
        return fn

    return register


def mission_reward(mission_id: str, *, uses=()):
    """REWARD: a generator fn(ctx, actions), like an operation, with the actions it declares."""

    def register(fn):
        impl = MISSIONS.setdefault(mission_id, MissionImpl(mission_id))
        impl.reward = fn
        impl.uses = frozenset(uses)
        return fn

    return register


def development_cost(card_ids, *costs) -> None:
    for cid in _ids(card_ids):
        DEV_COSTS[cid] = tuple(costs)


def endgame(card_ids):
    def register(fn):
        for cid in _ids(card_ids):
            ENDGAME[cid] = fn
        return fn

    return register


def hand_size_modifier(card_ids):
    def register(fn):
        for cid in _ids(card_ids):
            HAND_SIZE[cid] = fn
        return fn

    return register


def skill_icons(card_ids):
    def register(fn):
        for cid in _ids(card_ids):
            SKILLS[cid] = fn
        return fn

    return register


def state_check(card_ids):
    def register(fn):
        for cid in _ids(card_ids):
            STATE_CHECKS[cid] = fn
        return fn

    return register


def duty_slots(card_ids, *, staging: bool = False):
    """PASSIVE/SPECIAL "you may have an additional Person (with X) on duty"."""

    def register(fn):
        for cid in _ids(card_ids):
            DUTY_SLOTS[cid] = (fn, staging)
        return fn

    return register


def restriction(card_ids):
    """PASSIVE "you cannot play or promote ..."."""

    def register(fn):
        for cid in _ids(card_ids):
            RESTRICTIONS[cid] = fn
        return fn

    return register


def trait_modifier(card_ids, *, staging: bool = False):
    """PASSIVE/SPECIAL "... are additionally treated as [trait]" (KW-TREAT-02)."""

    def register(fn):
        for cid in _ids(card_ids):
            TRAIT_MODIFIERS[cid] = (fn, staging)
        return fn

    return register


def dismiss_rewards(card_ids):
    """PASSIVE "when this card is dismissed, gain ...": fn(state, owner, inst) -> {resource: amount}."""

    def register(fn):
        for cid in _ids(card_ids):
            DISMISS_REWARDS[cid] = fn
        return fn

    return register


def load_all() -> None:
    """Import every card module so its registrations run."""
    for setpkg in pkgutil.iter_modules(__path__):
        if not setpkg.ispkg:
            continue
        pkg = importlib.import_module(f"{__name__}.{setpkg.name}")
        for mod in pkgutil.walk_packages(pkg.__path__, prefix=f"{pkg.__name__}."):
            importlib.import_module(mod.name)


load_all()
