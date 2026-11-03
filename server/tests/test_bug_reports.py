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


def test_0c32aebf():
    """The tutorial is saying that I can use the Deanna's Play (which is not true). I should be using the passive, and
    the passive isn't changing the actions on the incident, I cannot move forward.

    The engine offered Deanna's granted PLAY (index 100), but the card panel listed only the printed operations, so
    the one move the coach was waiting for had no button. The client now adds every offered PLAY whose index is past
    the printed ones, reading its text from the option label; this pins down what it relies on."""
    from types import SimpleNamespace

    from app import tutorial
    from engine.content import content

    state = replay_fixture("0c32aebf")
    game = SimpleNamespace(**load_fixture("0c32aebf")["bundle"]["game"])
    game.commands = load_fixture("0c32aebf")["bundle"]["commands"]
    hostile = next(i for i in state.players[0].hand if i.card == "3RIK20")
    index, free = tutorial.progress(game)
    assert not free and tutorial.script("riker-primer")["steps"][index]["id"] == "hostile"
    want = f"play:{hostile.uid}:100"
    assert tutorial.allowed(game, state) == {want}
    assert 100 >= len(content().cards["3RIK20"].operations)  # not printed: the panel must add it from the options
    option = next(o for o in state.decision.options if o.id == want)
    assert option.label.startswith("Play Hostile Contact (action): Discard a card to return this card.")
    assert option.label.endswith("(Deanna Troi-Riker)")
