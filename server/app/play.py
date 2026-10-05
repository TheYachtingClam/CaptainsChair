"""Runs games: builds engine state by replaying stored commands, applies new ones, handles undo."""

from __future__ import annotations

import copy
import secrets
import threading

from sqlalchemy.orm import Session, object_session
from sqlalchemy.orm.attributes import flag_modified

from app.models import Game
from engine import dev
from engine.game import IllegalCommand, _flag_irreversible, advance, choose
from engine.setup import BotSetup, SeatSetup, SetupError, new_game
from engine.state import GameState
from engine.views import game_view

_cache: dict[str, tuple[tuple[int, int], GameState]] = {}
_lock = threading.Lock()  # one command per game at a time (REQ-SRV-42)


def forget(game_id: str) -> None:
    """Drop a deleted game's cached state."""
    _cache.pop(game_id, None)


def start(game: Game) -> None:
    game.seed = secrets.randbits(63)
    game.commands = []
    game.status = "active"
    # Validate setup now rather than on the first view. The game id may not exist yet, so no caching.
    new_game(game.seed, game.mode, seat_setups(game), game.expansions, game.promos, bot_setup(game))


def seat_setups(game: Game) -> list[SeatSetup]:
    """Each seat's setup; a campaign game also brings the human's Reinforcement pile (REQ-CAMP-20)."""
    reinforcement = tuple((game.campaign or {}).get("reinforcement", []))
    return [SeatSetup(s.display_name, s.deck_id, s.board_side, reinforcement if s.index == 0 else ())
            for s in game.seats]


def bot_setup(game: Game) -> BotSetup | None:
    """The stored Bot choice of a solo game (REQ-SRV-18)."""
    if not game.bot:
        return None
    return BotSetup(game.bot["deck_id"], game.bot.get("difficulty", "ensign"), bool(game.bot.get("ticking_clock")))


def _live(command: dict) -> bool:
    """A move that still counts: not undone, not dropped, and not a note."""
    return not command.get("undone") and not command.get("dropped") and "note" not in command


def build(game: Game) -> GameState:
    key = (len(game.commands), sum(1 for c in game.commands if _live(c)))
    cached = _cache.get(game.id)
    if cached and cached[0] == key:
        return copy.deepcopy(cached[1])
    state = new_game(game.seed, game.mode, seat_setups(game), game.expansions, game.promos, bot_setup(game))
    advance(state, flag_irreversible=False)
    # Replay without the can't-be-undone flagging (it tries every option on a copy), then flag the last question.
    for i, command in enumerate(game.commands):
        if "note" in command:
            state.emit(command["note"])
            continue
        if not _live(command):
            continue
        try:
            if "dev" in command:
                dev.apply(state, command["seat"], command["dev"], flag_irreversible=False)
            else:
                choose(state, command["seat"], command["option"], flag_irreversible=False)
        except (IllegalCommand, dev.DevCommandError):
            _drop_from(game, i, state)
            break
    if state.decision is not None:
        _flag_irreversible(state)
    key = (len(game.commands), sum(1 for c in game.commands if _live(c)))
    _cache[game.id] = (key, copy.deepcopy(state))
    return state


def _drop_from(game: Game, index: int, state: GameState) -> None:
    """The rules engine changed since these moves were saved, and move `index` no longer applies.

    That move and every later one are marked dropped (kept for debugging, never replayed), a note is added to the
    game log, and the game continues from the last move that still applies. Saved at once so it happens only once.
    """
    commands = [dict(c) for c in game.commands]
    dropped = 0
    for c in commands[index:]:
        if _live(c):
            c["dropped"] = True
            dropped += 1
    note = (f"The rules engine changed since this game was saved. {dropped} later move(s) no longer apply and were "
            "dropped; the game continues from here.")
    commands.insert(index, {"note": note, "seat": None, "irreversible": True, "turn": state.turn})
    state.emit(note)
    game.commands = commands
    flag_modified(game, "commands")
    session = object_session(game)
    if session is not None:
        session.commit()


def view(game: Game, seat: int | None) -> dict:
    state = build(game)
    out = game_view(state, seat)
    out["can_undo"] = seat is not None and can_undo(game, seat)
    from app.config import get_settings

    out["dev_tools"] = get_settings().dev_tools
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


def apply_dev(db: Session, game: Game, seat: int, cmd: dict) -> None:
    """A developer command (engine/dev.py). It is stored like a move, so undo and replay include it."""
    with _lock:
        state = build(game)
        try:
            dev.apply(state, seat, cmd)
        except dev.DevCommandError as err:
            raise IllegalCommand(str(err)) from err
        game.commands = [*game.commands, {"seat": seat, "dev": cmd, "irreversible": False, "turn": state.turn}]
        flag_modified(game, "commands")
        db.commit()


def _last_live(game: Game) -> int | None:
    """The last command still in play. A note (such as dropped moves) counts, and cannot be undone."""
    return next((i for i in range(len(game.commands) - 1, -1, -1)
                 if not game.commands[i].get("undone") and not game.commands[i].get("dropped")), None)


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


__all__ = ["IllegalCommand", "SetupError", "apply", "apply_dev", "build", "can_undo", "start", "undo", "view"]
