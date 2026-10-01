"""Runs games: builds engine state by replaying stored commands, applies new ones, handles undo."""

from __future__ import annotations

import copy
import secrets
import threading

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models import Game
from engine.game import IllegalCommand, advance, choose
from engine.setup import SeatSetup, SetupError, new_game
from engine.state import GameState
from engine.views import game_view

_cache: dict[str, tuple[tuple[int, int], GameState]] = {}
_lock = threading.Lock()  # one command per game at a time (REQ-SRV-42)


def start(game: Game) -> None:
    game.seed = secrets.randbits(63)
    game.commands = []
    game.status = "active"
    # Validate setup now rather than on the first view. The game id may not exist yet, so no caching.
    new_game(game.seed, game.mode, [SeatSetup(s.display_name, s.deck_id, s.board_side) for s in game.seats],
             game.expansions, game.promos)


def build(game: Game) -> GameState:
    live = [c for c in game.commands if not c.get("undone")]
    key = (len(game.commands), len(live))
    cached = _cache.get(game.id)
    if cached and cached[0] == key:
        return copy.deepcopy(cached[1])
    seats = [SeatSetup(s.display_name, s.deck_id, s.board_side) for s in game.seats]
    state = new_game(game.seed, game.mode, seats, game.expansions, game.promos)
    advance(state)
    for command in live:
        choose(state, command["seat"], command["option"])
    _cache[game.id] = (key, copy.deepcopy(state))
    return state


def view(game: Game, seat: int | None) -> dict:
    state = build(game)
    out = game_view(state, seat)
    out["can_undo"] = seat is not None and can_undo(game, seat)
    return out


def apply(db: Session, game: Game, seat: int, option: str) -> None:
    with _lock:
        state = build(game)
        before = len(state.log)
        choose(state, seat, option)  # raises IllegalCommand
        irreversible = any(e.irreversible for e in state.log[before:])
        game.commands = [*game.commands, {"seat": seat, "option": option, "irreversible": irreversible, "turn": state.turn}]
        if state.step == "over":
            game.status = "finished"
        flag_modified(game, "commands")
        db.commit()


def _last_live(game: Game) -> int | None:
    return next((i for i in range(len(game.commands) - 1, -1, -1) if not game.commands[i].get("undone")), None)


def can_undo(game: Game, seat: int) -> bool:
    """Free undo of your own last command, if it revealed nothing and the turn has not passed (REQ-UNDO-30)."""
    if game.status != "active":
        return False
    i = _last_live(game)
    if i is None:
        return False
    last = game.commands[i]
    return last["seat"] == seat and not last.get("irreversible")


def undo(db: Session, game: Game, seat: int) -> None:
    with _lock:
        if not can_undo(game, seat):
            raise IllegalCommand("Nothing you can undo")
        i = _last_live(game)
        commands = [dict(c) for c in game.commands]
        commands[i]["undone"] = True  # kept for debugging, never replayed (REQ-UNDO-41)
        game.commands = commands
        flag_modified(game, "commands")
        db.commit()


__all__ = ["IllegalCommand", "SetupError", "apply", "build", "can_undo", "start", "undo", "view"]
