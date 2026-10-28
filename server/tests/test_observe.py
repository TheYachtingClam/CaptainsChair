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


# ------------------------------------------------------------------ the endpoints (REQ-ADMIN-07, -08, -12)

def two_player_game(admin, moves=8):
    """Ann and Bob play a few moves; the admin holds no seat."""
    from tests.conftest import another_browser, sign_in_as

    ann = sign_in_as(another_browser(admin), "ann@example.com", "Ann")
    bob = sign_in_as(another_browser(admin), "bob@example.com", "Bob")
    game_id = ann.post("/api/games", json={"deck_id": "georgiou", "mode": "two_player"}).json()["game"]["id"]
    bob.post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    players = {0: ann, 1: bob}
    for _ in range(moves):
        seat = ann.get(f"/api/games/{game_id}/state").json()["decision"]["seat"]
        options = players[seat].get(f"/api/games/{game_id}/state").json()["decision"]["options"]
        pick = next((o for o in options if o["id"].startswith("play:")), options[0])
        assert players[seat].post(f"/api/games/{game_id}/commands", json={"option": pick["id"]}).status_code == 200
    return game_id, players


def stored(game_id):
    from app.db import get_db

    db = next(get_db())
    game = db.get(Game, game_id)
    return game, db


def test_watching_needs_the_admin(admin):
    game_id, players = two_player_game(admin, moves=2)
    for client in players.values():
        assert client.get(f"/api/admin/games/{game_id}/timeline").status_code == 403
        assert client.get(f"/api/admin/games/{game_id}/observe").status_code == 403
        assert client.post(f"/api/admin/games/{game_id}/copy", json={"moves": 0}).status_code == 403
    waiting = players[0].post("/api/games", json={"deck_id": "kirk", "mode": "two_player"}).json()["game"]["id"]
    assert admin.get(f"/api/admin/games/{waiting}/timeline").status_code == 409
    assert admin.get("/api/admin/games/no-such-game/observe").status_code == 404


def test_the_admin_sees_everything_or_as_a_seat_sees_it(admin):
    game_id, players = two_player_game(admin)
    everything = admin.get(f"/api/admin/games/{game_id}/observe").json()
    assert all(p["hand"] is not None and p["draw"] is not None and p["reserve"] is not None
               for p in everything["players"])
    assert everything["decision"]["options"] and everything["decision"]["observe"] is True
    assert everything["you"] is None and everything["can_undo"] is False and everything["dev_tools"] is False

    as_ann = admin.get(f"/api/admin/games/{game_id}/observe?as=0").json()
    assert as_ann["players"][0]["hand"] is not None and as_ann["players"][1]["hand"] is None
    assert as_ann["players"][1]["draw"] is None and "observe" not in as_ann["decision"]
    ann_own = players[0].get(f"/api/games/{game_id}/state").json()
    assert as_ann["players"] == ann_own["players"] and as_ann["decision"] == ann_own["decision"]

    watcher = admin.get(f"/api/admin/games/{game_id}/observe?as=watcher").json()
    seatless = admin.get(f"/api/games/{game_id}/state").json()  # the admin holds no seat here
    assert watcher["players"] == seatless["players"] and watcher["log"] == seatless["log"]
    assert all(p["hand"] is None for p in watcher["players"]) and "options" not in watcher["decision"]

    assert admin.get(f"/api/admin/games/{game_id}/observe?as=5").status_code == 422
    assert admin.get(f"/api/admin/games/{game_id}/observe?as=nobody").status_code == 422


def test_positions_and_the_timeline(admin):
    game_id, _ = two_player_game(admin)
    t = admin.get(f"/api/admin/games/{game_id}/timeline").json()
    assert t["last"] == 8 and len(t["moves"]) == 8 and t["turns"][0]["turn"] == 1 and t["stopped"] is None
    start = admin.get(f"/api/admin/games/{game_id}/observe?at=0").json()
    assert start["observe"] == {"at": 0, "last": 8, "live": False, "as": "all"} and start["turn"] == 1
    assert admin.get(f"/api/admin/games/{game_id}/observe").json()["observe"]["live"] is True
    assert admin.get(f"/api/admin/games/{game_id}/observe?at=8").json()["observe"]["live"] is True
    assert admin.get(f"/api/admin/games/{game_id}/observe?at=9").status_code == 422
    assert admin.get(f"/api/admin/games/{game_id}/observe?at=-1").status_code == 422


def test_watching_stores_nothing(admin):
    game_id, _ = two_player_game(admin)
    game, db = stored(game_id)
    before = (copy.deepcopy(game.commands), game.status, [(s.index, s.user_id) for s in game.seats])
    db.close()
    admin.get(f"/api/admin/games/{game_id}/timeline")
    for at in range(9):
        admin.get(f"/api/admin/games/{game_id}/observe?at={at}")
    game, db = stored(game_id)
    assert (game.commands, game.status, [(s.index, s.user_id) for s in game.seats]) == before
    db.close()


def test_copy_from_here_makes_a_playable_copy(admin):
    game_id, _ = two_player_game(admin)
    r = admin.post(f"/api/admin/games/{game_id}/copy", json={"moves": 3})
    assert r.status_code == 200
    copy_id = r.json()["game_id"]
    copied, db = stored(copy_id)
    original, _ = stored(game_id)
    assert copied.status == "active" and len(copied.commands) == 3 and len(original.commands) == 8
    owners = {s.user_id for s in copied.seats}
    assert len(owners) == 1 and owners.isdisjoint(s.user_id for s in original.seats) and "" not in owners
    assert [s.display_name for s in copied.seats] == ["Ann", "Bob"]
    db.close()
    # It is the game at position 3, and the admin plays it from there in the seat that must decide.
    watched = admin.get(f"/api/admin/games/{game_id}/observe?at=3").json()
    view = admin.get(f"/api/games/{copy_id}/state").json()
    assert view["you"] == view["decision"]["seat"] == watched["decision"]["seat"]
    assert view["players"][view["you"]]["hand"] == watched["players"][view["you"]]["hand"]
    option = view["decision"]["options"][0]["id"]
    assert admin.post(f"/api/games/{copy_id}/commands", json={"option": option}).status_code == 200
    assert admin.post(f"/api/admin/games/{game_id}/copy", json={"moves": 9}).status_code == 422


def test_a_copy_of_a_campaign_game_never_counts_for_the_campaign(admin):
    r = admin.post("/api/games", json={"deck_id": "kirk", "mode": "solo",
                                       "bot": {"deck_id": "soval", "difficulty": "ensign"}})
    game_id = r.json()["game"]["id"]
    game, db = stored(game_id)
    game.campaign = {"id": "some-campaign", "assignment": 1, "reinforcement": []}
    db.commit()
    db.close()
    copy_id = admin.post(f"/api/admin/games/{game_id}/copy", json={"moves": 0}).json()["game_id"]
    copied, db = stored(copy_id)
    assert copied.campaign == {"reinforcement": []}
    db.close()


def test_a_copy_of_a_tutorial_keeps_its_stacked_decks(admin):
    """The stack is part of a tutorial's setup (REQ-TUT-12), so a copy deals the same cards (and so does a bug report's
    copy, which shares the setup)."""
    game_id = admin.post("/api/tutorials/picard-basics").json()["game"]["id"]
    copy_id = admin.post(f"/api/admin/games/{game_id}/copy", json={"moves": 0}).json()["game_id"]
    original = admin.get(f"/api/games/{game_id}/state").json()
    copied = admin.get(f"/api/games/{copy_id}/state").json()
    assert copied["players"][0]["hand"] == original["players"][0]["hand"]
    assert copied["market"] == original["market"]


# ------------------------------------------------------------------ live follow, unseen (REQ-ADMIN-11)

def test_the_admin_watches_live_without_being_seen(admin):
    from app.hub import hub

    game_id, players = two_player_game(admin, moves=0)
    seat = admin.get(f"/api/admin/games/{game_id}/observe").json()["decision"]["seat"]
    with players[1 - seat].websocket_connect(f"/api/games/{game_id}/ws") as player:
        assert player.receive_json()["type"] == "hello"
        assert player.receive_json() == {"type": "presence", "connected": [1 - seat]}
        with admin.websocket_connect(f"/api/games/{game_id}/ws") as watcher:
            assert watcher.receive_json() == {"type": "hello", "your_seat": None, "watching": True}
            assert hub.connected_seats(game_id) == [1 - seat]
            option = players[seat].get(f"/api/games/{game_id}/state").json()["decision"]["options"][0]["id"]
            assert players[seat].post(f"/api/games/{game_id}/commands", json={"option": option}).status_code == 200
            assert watcher.receive_json() == {"type": "state_changed"}
            # The player was told of the move, and of no new connection.
            assert player.receive_json() == {"type": "state_changed"}
        assert hub.connected_seats(game_id) == [1 - seat]


def test_a_waiting_email_is_sent_while_only_the_admin_watches(admin):
    from app import mail
    from tests.test_games import finish_turn

    game_id, players = two_player_game(admin, moves=0)
    active = admin.get(f"/api/admin/games/{game_id}/observe").json()["active"]
    other_email = players[1 - active].get("/api/auth/me").json()["email"]
    mail.OUTBOX.clear()
    with admin.websocket_connect(f"/api/games/{game_id}/ws") as watcher:
        watcher.receive_json()
        finish_turn(players[active], game_id)
    assert [m["to"] for m in mail.OUTBOX] == [other_email]


def test_only_a_seated_player_or_the_admin_may_connect(admin):
    from starlette.websockets import WebSocketDisconnect

    from tests.conftest import another_browser, sign_in_as

    game_id, players = two_player_game(admin, moves=0)
    stranger = sign_in_as(another_browser(admin), "eve@example.com", "Eve")
    for client, url in ((stranger, ""), (stranger, "?watch=1"), (players[0], "?watch=1")):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/games/{game_id}/ws{url}") as ws:
                ws.receive_json()


def test_the_admin_can_watch_a_game_they_play_in(admin):
    from app.hub import hub
    from tests.conftest import another_browser, sign_in_as

    game_id = admin.post("/api/games", json={"deck_id": "georgiou", "mode": "two_player"}).json()["game"]["id"]
    bob = sign_in_as(another_browser(admin), "bob@example.com", "Bob")
    bob.post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    with admin.websocket_connect(f"/api/games/{game_id}/ws?watch=1") as watcher:
        assert watcher.receive_json()["watching"] is True
        assert hub.connected_seats(game_id) == []
    with admin.websocket_connect(f"/api/games/{game_id}/ws") as seated:
        assert seated.receive_json() == {"type": "hello", "your_seat": 0}
        assert hub.connected_seats(game_id) == [0]
