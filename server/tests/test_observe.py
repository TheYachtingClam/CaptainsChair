"""The admin watches a game (REQ-ADMIN-07 to -12): positions, the timeline of moves and turns, and checkpoints. The
observer must give exactly the state a plain replay gives, and never write to the game."""

import copy
import random
import uuid

import pytest

from app import observe, play
from app.models import Game, Seat
from engine.game import choose
from engine.views import game_view

MODES = {
    "two_player": (["georgiou", "kirk"], None),
    "solo": (["kirk"], {"deck_id": "soval", "difficulty": "ensign"}),
    "cadet": (["archer"], None),
}


def new(mode: str, seed: int = 7) -> Game:
    decks, bot = MODES[mode]
    game = Game(id=str(uuid.uuid4()), mode=mode, box="to_boldly_go", expansions=[], promos=False, promo_sets=[],
                seed=seed, bot=bot, commands=[], status="active")
    for i, deck in enumerate(decks):
        game.seats.append(Seat(index=i, display_name=f"P{i}", deck_id=deck, board_side="basic", user_id=""))
    return game


def dump(state) -> str:
    return state.model_dump_json()


def played(mode: str, moves: int = 150, seed: int = 7) -> tuple[Game, list[str]]:
    """A game with `moves` random moves stored, and the state after each position, from a plain replay."""
    game = new(mode, seed)
    rng = random.Random(seed)
    state = play.initial(game)
    states = [dump(state)]
    commands = []
    for _ in range(moves):
        if state.step == "over":
            break
        d = state.decision
        ids = [o.id for o in d.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        option = rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids)
        commands.append({"seat": d.seat, "option": option, "irreversible": False, "turn": state.turn, "weekday": 2})
        state.weekday = 2
        choose(state, d.seat, option, flag_irreversible=False)
        states.append(dump(state))
    game.commands = commands
    return game, states


@pytest.fixture(autouse=True)
def fresh_cache():
    observe._cache.clear()
    yield
    observe._cache.clear()


@pytest.mark.parametrize("mode", MODES)
def test_every_position_is_a_plain_replay(mode):
    game, states = played(mode)
    t = observe.timeline(game)
    assert t["last"] == len(game.commands) and t["stopped"] is None
    assert [m["at"] for m in t["moves"]] == list(range(1, t["last"] + 1))
    for at in (*range(0, t["last"] + 1, 5), t["last"]):
        assert dump(observe.state_at(game, at)) == states[at], at
    # play.build also flags the pending question's can't-be-undone options; the observer has no use for them.
    latest = observe.state_at(game)
    if latest.decision is not None:
        play._flag_irreversible(latest)
    assert dump(latest) == dump(play.build(game))
    with pytest.raises(ValueError):
        observe.state_at(game, t["last"] + 1)


def test_moves_are_labelled_with_the_answer_chosen():
    game, _ = played("cadet", 20)
    t = observe.timeline(game)
    state = play.initial(game)
    first = game.commands[0]["option"]
    assert t["moves"][0]["prompt"] == state.decision.prompt
    assert t["moves"][0]["move"] == next(o.label for o in state.decision.options if o.id == first)
    assert t["moves"][0]["turn"] == 1 and t["moves"][0]["seat"] == 0


def test_a_turn_opens_before_its_first_move():
    game, states = played("two_player", 200)
    t = observe.timeline(game)
    assert len(t["turns"]) >= 3
    assert [x["turn"] for x in t["turns"]] == list(range(1, len(t["turns"]) + 1))
    for turn in t["turns"]:
        at = turn["at"]
        state = observe.state_at(game, at)
        assert state.turn + 1 == turn["turn"] and state.active == turn["seat"]
        if at > 0:
            assert t["moves"][at - 1]["turn"] < turn["turn"]
        if at < t["last"]:
            assert t["moves"][at]["turn"] == turn["turn"]
    # The players alternate, starting with the first player.
    assert {x["seat"] for x in t["turns"]} == {0, 1}
    assert all(a["seat"] != b["seat"] for a, b in zip(t["turns"], t["turns"][1:]))


def test_a_bot_turn_opens_after_the_move_that_ran_it():
    game, _ = played("solo", 200)
    t = observe.timeline(game)
    bot_turns = [x for x in t["turns"] if x["bot"]]
    assert bot_turns and all(x["name"] == observe._cache[game.id].latest.players[1].name for x in bot_turns)
    for turn in bot_turns:
        state = observe.state_at(game, turn["at"])
        assert state.turn + 1 >= turn["turn"]
        view = game_view(state, 0)
        assert view["bot_turn"] is not None and view["bot_turn"]["steps"]
        # The move before it was the human's, in the turn before.
        assert t["moves"][turn["at"] - 1]["seat"] == 0 and t["moves"][turn["at"] - 1]["turn"] < turn["turn"]


def test_undone_dropped_tutorial_and_note_entries_are_not_moves():
    game, states = played("cadet", 12)
    real = game.commands
    noise = [
        {**real[3], "undone": True},
        {"seat": 0, "option": "tutorial:next", "irreversible": False, "turn": 0},
        {**real[5], "dropped": True},
    ]
    note = {"note": "A note.", "seat": None, "irreversible": True, "turn": 0}
    game.commands = [*real[:6], *noise, *real[6:], note]
    t = observe.timeline(game)
    assert t["last"] == len(real)
    assert [m["index"] for m in t["moves"]][5:7] == [5, 9]
    for at in range(len(real)):
        assert dump(observe.state_at(game, at)) == states[at], at
    assert observe.state_at(game).log[-1].text == "A note."


def test_a_move_that_no_longer_applies_ends_the_timeline_and_changes_nothing():
    game, states = played("cadet", 12)
    game.commands = [*game.commands[:5], {"seat": 0, "option": "no-such-option", "irreversible": False, "turn": 0},
                     *game.commands[5:]]
    before = copy.deepcopy(game.commands)
    t = observe.timeline(game)
    assert t["last"] == 5 and len(t["moves"]) == 5
    assert t["stopped"]["at"] == 5 and t["stopped"]["index"] == 5 and t["stopped"]["reason"]
    assert dump(observe.state_at(game)) == states[5]
    assert dump(observe.state_at(game, 2)) == states[2]
    assert game.commands == before  # nothing dropped, nothing noted


def test_new_moves_extend_the_timeline_as_a_fresh_build_would():
    game, states = played("two_player", 120)
    full = game.commands
    game.commands = full[:70]
    observe.timeline(game)
    checkpoints = len(observe._cache[game.id].checkpoints)
    game.commands = full  # the row gets a new list when a move is stored
    extended = observe.timeline(game)
    assert len(observe._cache[game.id].checkpoints) > checkpoints
    assert dump(observe.state_at(game)) == states[-1]
    assert dump(observe.state_at(game, 100)) == states[100]
    observe._cache.clear()
    assert observe.timeline(game) == extended


def test_an_undo_rebuilds_the_timeline():
    game, states = played("cadet", 20)
    assert observe.timeline(game)["last"] == 20
    game.commands = [*game.commands[:-1], {**game.commands[-1], "undone": True}]
    assert observe.timeline(game)["last"] == 19
    assert dump(observe.state_at(game)) == states[19]


def test_long_turns_get_extra_checkpoints():
    game, _ = played("cadet", 150)
    observe.timeline(game)
    t = observe._cache[game.id]
    gaps = [b.at - a.at for a, b in zip(t.checkpoints, t.checkpoints[1:])]
    assert gaps and max(gaps) <= observe.CHECKPOINT_EVERY
    assert t.checkpoints[0].at == 0


def test_only_a_few_games_are_kept():
    for seed in range(observe.KEEP + 2):
        game, _ = played("cadet", 3, seed=seed)
        observe.timeline(game)
    assert len(observe._cache) == observe.KEEP
