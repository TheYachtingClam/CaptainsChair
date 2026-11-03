"""Regression tests made from players' bug reports (plans/bug-pipeline.md).

`scripts/bugs.py fixture <id>` saves a report's trimmed bundle in `tests/bugs/<prefix>.json`; a test in
`test_bug_reports.py` replays it with `replay_fixture` and checks the behaviour that was wrong."""

from __future__ import annotations

import json
from pathlib import Path

from app import bugs, play
from engine.state import GameState

FIXTURES = Path(__file__).resolve().parent / "bugs"


def load_fixture(name: str) -> dict:
    """The saved report `tests/bugs/<name>.json`."""
    return json.loads((FIXTURES / f"{name}.json").read_text())


def replay_fixture(name: str, *, moves: int | None = None, back: int | None = None) -> GameState:
    """The game of the saved report `name`, replayed with today's rules: at the report, after the first `moves`
    commands, or `back` commands before the report. Unlike a stored game, a move that no longer applies raises
    `play.StaleMove` instead of being dropped, so a rule change that breaks a fixture fails its test (REQ-BUG-08)."""
    data = load_fixture(name)["bundle"]
    commands = data["commands"]
    if back is not None:
        moves = len(commands) - back
    game = bugs.as_game(data, moves=moves)
    try:
        state = play.initial(game)
        for _ in play.replay(game.commands, state):
            pass
        return state
    finally:
        play.forget(game.id)
