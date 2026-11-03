"""Regression tests made from players' bug reports (plans/bug-pipeline.md).

One test per fixed report, named after its fixture in `tests/bugs/`, with the player's description as its docstring.
Each asserts the behaviour that was wrong, at the reported position, not only that the game replays. Make a fixture
with `scripts/bugs.py fixture <id>`."""

import json

import pytest

from tests.bug_replay import FIXTURES, load_fixture, replay_fixture


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.json")), ids=lambda p: p.stem)
def test_every_fixture_is_trimmed_and_still_replays(path):
    """A fixture holds no player names, views or log lines, and every one of its moves still applies."""
    report = json.loads(path.read_text())
    bundle = report["bundle"]
    assert {"view", "recent_log", "decision"}.isdisjoint(bundle)
    assert all(s["display_name"] == f"Player {s['index'] + 1}" for s in bundle["game"]["seats"])
    state = replay_fixture(path.stem)
    assert (state.turn, state.step) == (bundle["turn"], bundle["step"])


def test_example():
    """Example report for the regression test harness: a Cadet Training game eight moves in."""
    state = replay_fixture("example")
    assert state.decision is not None and state.decision.seat == 0
    earlier = replay_fixture("example", back=3)
    assert len(earlier.log) < len(state.log)
    assert load_fixture("example")["bundle"]["game"]["mode"] == "cadet"
