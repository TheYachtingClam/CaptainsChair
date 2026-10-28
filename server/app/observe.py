"""The admin watches a game (requirements/19-technical-architecture.md §5.6, REQ-ADMIN-07 to -12): the game at any
position, and the timeline of its moves and turns. Nothing here writes to the game or the database.

A position is the game after a number of moves, from 0 (just after setup) to the last move (REQ-ADMIN-09). One replay
builds the timeline and keeps a copy of the state at the start of each turn (a checkpoint), so any position is rebuilt
from the nearest checkpoint with at most a turn's moves. The last few games watched are kept in memory, and a game
that has only gained moves since is extended rather than replayed again."""

from __future__ import annotations

import copy
import threading
from collections import OrderedDict
from dataclasses import dataclass, field

from app import play
from app.models import Game
from engine.state import GameState

KEEP = 4  # games kept in memory
CHECKPOINT_EVERY = 40  # moves between checkpoints in a long turn


@dataclass
class Checkpoint:
    at: int  # the position
    index: int  # the command to replay from
    state: GameState


@dataclass
class Timeline:
    length: int  # commands seen, live or not
    live: int  # live commands among them
    moves: list[dict] = field(default_factory=list)  # one per move: the move that reaches position n is moves[n - 1]
    turn_at: list[int] = field(default_factory=list)  # state.turn at each position
    checkpoints: list[Checkpoint] = field(default_factory=list)
    latest: GameState | None = None  # the state at the last position
    next_index: int = 0  # the command after the last one replayed
    stopped: dict | None = None  # the move that no longer applies, if any


_cache: OrderedDict[str, Timeline] = OrderedDict()
_lock = threading.Lock()


def _counts(game: Game) -> tuple[int, int]:
    commands = game.commands or []
    return len(commands), sum(1 for c in commands if play._live(c))


def _label(state: GameState, command: dict) -> tuple[str, str]:
    """The question a move answered and the label of the answer, read before it is applied."""
    if "dev" in command:
        return "Developer command", ", ".join(f"{k} {v}" for k, v in command["dev"].items())
    decision = state.decision
    if decision is None:
        return "", command["option"]
    option = next((o for o in decision.options if o.id == command["option"]), None)
    return decision.prompt, option.label if option else command["option"]


def _extend(timeline: Timeline, commands: list[dict]) -> None:
    """Replays the commands after the timeline's last one, recording each move and keeping checkpoints."""
    state = timeline.latest
    at = len(timeline.moves)
    try:
        for i in play.replay(commands, state, timeline.next_index):
            timeline.turn_at[at] = state.turn
            last = timeline.checkpoints[-1]
            if timeline.turn_at[last.at] != state.turn or at - last.at >= CHECKPOINT_EVERY:
                timeline.checkpoints.append(Checkpoint(at, i, copy.deepcopy(state)))
            command = commands[i]
            prompt, label = _label(state, command)
            timeline.moves.append({"at": at + 1, "index": i, "turn": state.turn + 1, "seat": command["seat"],
                                   "prompt": prompt, "move": label, "irreversible": bool(command.get("irreversible")),
                                   "dev": "dev" in command})
            timeline.turn_at.append(state.turn)  # set again once the move is applied
            at += 1
        timeline.turn_at[at] = state.turn
    except play.StaleMove as stale:
        # The move that failed never reaches a position: the timeline ends before it.
        timeline.moves.pop()
        timeline.turn_at.pop()
        timeline.stopped = {"at": at - 1, "index": stale.index, "reason": str(stale)}
        timeline.latest = None
    timeline.next_index = len(commands)


def _timeline(game: Game) -> Timeline:
    """The game's timeline, from the cache when the game has not changed or has only gained moves."""
    length, live = _counts(game)
    commands = game.commands or []
    cached = _cache.get(game.id)
    if cached is not None:
        _cache.move_to_end(game.id)
        if (cached.length, cached.live) == (length, live):
            return cached
        added = sum(1 for c in commands[cached.length:] if play._live(c))
        if cached.latest is not None and length > cached.length and live - cached.live == added:
            _extend(cached, commands)
            cached.length, cached.live = length, live
            return cached
    state = play.initial(game)
    timeline = Timeline(length, live, turn_at=[state.turn], checkpoints=[Checkpoint(0, 0, copy.deepcopy(state))],
                        latest=state)
    _extend(timeline, commands)
    _cache[game.id] = timeline
    while len(_cache) > KEEP:
        _cache.popitem(last=False)
    return timeline


def forget(game_id: str) -> None:
    """Drop a deleted game's timeline."""
    with _lock:
        _cache.pop(game_id, None)


def turns(timeline: Timeline) -> list[dict]:
    """Each turn of the game, with its player and the position it opens at (REQ-ADMIN-10): the first position in that
    turn, or, for a Bot's turn played inside one move, the position after that move."""
    players = timeline.checkpoints[0].state.players
    first = timeline.checkpoints[0].state.first_seat
    out = []
    last = max(timeline.turn_at)
    for turn in range(last + 1):
        seat = (first + turn) % len(players)  # end_turn passes the turn to the next seat
        out.append({"turn": turn + 1, "seat": seat, "name": players[seat].name, "bot": players[seat].bot is not None,
                    "at": next(p for p, t in enumerate(timeline.turn_at) if t >= turn)})
    return out


def timeline(game: Game) -> dict:
    """The positions of a game, its moves and its turns (REQ-ADMIN-09, -10). `last` is the last position; `stopped`
    says why the timeline ends early when a stored move no longer applies."""
    with _lock:
        t = _timeline(game)
        return {"last": len(t.moves), "moves": [dict(m) for m in t.moves], "turns": turns(t),
                "stopped": dict(t.stopped) if t.stopped else None}


def state_at(game: Game, at: int | None = None) -> GameState:
    """A copy of the game at position `at` (the last position when None). Raises ValueError outside the timeline."""
    with _lock:
        t = _timeline(game)
        last = len(t.moves)
        at = last if at is None else at
        if not 0 <= at <= last:
            raise ValueError(f"There is no position {at}: the game has {last} moves")
        if at == last and t.latest is not None:
            return copy.deepcopy(t.latest)
        start = next(c for c in reversed(t.checkpoints) if c.at <= at)
        state = copy.deepcopy(start.state)
        commands = game.commands or []
    # Replayed outside the lock: the copy is this request's own.
    moved = start.at
    try:
        for _ in play.replay(commands, state, start.index):
            if moved == at:
                break
            moved += 1
    except play.StaleMove:  # only past the end of the timeline, which `at` never reaches
        raise AssertionError("a position past a move that no longer applies") from None
    return state
