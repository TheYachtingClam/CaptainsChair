"""Card behaviour registry.

Card code lives in one module per card under engine/cards/<set>/<slug>.py and follows CLAUDE.md.
The engine skeleton only runs continuous PASSIVE modifiers so far; PLAY, ACTIVATION and other
operations fall back to a placeholder until their code is written.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.state import GameState, Player

# card id -> function(state, owner, base_hand_size) -> new hand size
HAND_SIZE: dict[str, Callable[["GameState", "Player", int], int]] = {}


def hand_size_modifier(card_id: str):
    """Register a PASSIVE that changes its owner's hand size while the card is in a table position."""

    def register(fn):
        HAND_SIZE[card_id] = fn
        return fn

    return register


def load_all() -> None:
    """Import every card module so its registrations run."""
    for setpkg in pkgutil.iter_modules(__path__):
        if not setpkg.ispkg:
            continue
        pkg = importlib.import_module(f"{__name__}.{setpkg.name}")
        for mod in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{mod.name}")


load_all()
