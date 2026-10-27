import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import another_browser, sign_in_as


def create(client, **overrides):
    body = {"deck_id": "georgiou", "mode": "two_player", **overrides}
    return client.post("/api/games", json=body)


def sam(client):
    """A second player: another browser, signed in to another account."""
    return sign_in_as(another_browser(client), "sam@example.com", "Sam")


def test_decks_listed(authed):
    ids = {d["id"] for d in authed.get("/api/content/decks").json()}
    assert {"georgiou", "soval", "freeman"} <= ids


def test_create_and_join(authed):
    r = create(authed)
    assert r.status_code == 201
    grant = r.json()
    game_id = grant["game"]["id"]
    assert grant["game"]["open_seats"] == 1 and grant["seat_index"] == 0
    assert grant["game"]["seats"][0]["display_name"] == "Nick"  # the account's name (REQ-USER-40)

    other = sam(authed)
    r = other.post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    assert r.status_code == 200
    assert r.json()["seat_index"] == 1
    assert r.json()["game"]["status"] == "active"
    assert [s["display_name"] for s in r.json()["game"]["seats"]] == ["Nick", "Sam"]

    assert authed.get(f"/api/games/{game_id}").json()["your_seat"] == 0
    assert other.get(f"/api/games/{game_id}").json()["your_seat"] == 1
    watcher = sign_in_as(another_browser(authed), "eve@example.com", "Eve")
    assert watcher.get(f"/api/games/{game_id}").json()["your_seat"] is None


def test_one_account_cannot_take_both_seats(authed):
    game_id = create(authed).json()["game"]["id"]
    r = authed.post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    assert r.status_code == 409


def test_full_game_rejects_join(authed):
    game_id = create(authed).json()["game"]["id"]
    sam(authed).post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    eve = sign_in_as(another_browser(authed), "eve@example.com", "Eve")
    assert eve.post(f"/api/games/{game_id}/join", json={"deck_id": "kirk"}).status_code == 409


def test_expansion_deck_needs_expansion(authed):
    assert create(authed, deck_id="freeman").status_code == 422
    assert create(authed, deck_id="freeman", expansions=["second_contact"]).status_code == 201


def test_websocket_presence(authed):
    game_id = create(authed).json()["game"]["id"]
    with authed.websocket_connect(f"/api/games/{game_id}/ws") as ws:
        assert ws.receive_json() == {"type": "hello", "your_seat": 0}
        assert ws.receive_json() == {"type": "presence", "connected": [0]}
        ws.send_json({"type": "ping"})
        assert ws.receive_json() == {"type": "pong"}


def test_websocket_needs_a_signed_in_account(authed):
    game_id = create(authed).json()["game"]["id"]
    with pytest.raises(WebSocketDisconnect):
        with another_browser(authed).websocket_connect(f"/api/games/{game_id}/ws") as ws:
            ws.receive_json()


def test_websocket_needs_a_seat(authed):
    game_id = create(authed).json()["game"]["id"]
    with pytest.raises(WebSocketDisconnect):
        with sam(authed).websocket_connect(f"/api/games/{game_id}/ws") as ws:
            ws.receive_json()


def test_promos_option(authed):
    assert create(authed).json()["game"]["promos"] is False
    grant = create(authed, promos=True).json()
    assert grant["game"]["promos"] is True
    assert authed.get(f"/api/games/{grant['game']['id']}").json()["promos"] is True


def test_old_database_gets_promos_column(tmp_path):
    import sqlite3

    from app.db import init_db

    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE games (id VARCHAR(36) PRIMARY KEY, created_at DATETIME, mode VARCHAR(20), expansions JSON, status VARCHAR(20))")
    con.commit()
    con.close()
    init_db(f"sqlite:///{path}")
    cols = [r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(games)")]
    assert "promos" in cols


def started_game(authed):
    """A two-player game, with each seat's browser."""
    a = create(authed).json()
    other = sam(authed)
    other.post(f"/api/games/{a['game']['id']}/join", json={"deck_id": "soval"})
    return a["game"]["id"], {0: authed, 1: other}


def test_game_starts_and_plays(authed):
    game_id, players = started_game(authed)
    views = {seat: p.get(f"/api/games/{game_id}/state").json() for seat, p in players.items()}
    active = views[0]["active"]
    assert views[active]["decision"]["options"]
    assert "options" not in views[1 - active]["decision"]
    assert views[0]["players"][1]["hand"] is None and views[1]["players"][1]["hand"] is not None

    assert players[1 - active].post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 409

    p = players[active]
    r = p.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    assert r.status_code == 200 and r.json()["decision"]["kind"] == "glory"
    assert r.json()["can_undo"] is True

    r = p.post(f"/api/games/{game_id}/undo")
    assert r.json()["decision"]["kind"] == "action"
    assert r.json()["can_undo"] is False


def test_irreversible_command_cannot_be_undone(authed):
    game_id, players = started_game(authed)
    active = authed.get(f"/api/games/{game_id}/state").json()["active"]
    p = players[active]
    p.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    glory = p.get(f"/api/games/{game_id}/state").json()["decision"]["options"][0]["id"]
    p.post(f"/api/games/{game_id}/commands", json={"option": glory})
    r = p.post(f"/api/games/{game_id}/commands", json={"option": "done"})
    assert r.json()["active"] != active and r.json()["can_undo"] is False
    assert p.post(f"/api/games/{game_id}/undo").status_code == 409


def test_state_needs_a_seat_to_act(authed):
    game_id, _ = started_game(authed)
    watcher = sign_in_as(another_browser(authed), "eve@example.com", "Eve")
    assert watcher.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 403


def test_solo_needs_an_available_bot(authed):
    assert create(authed, mode="solo").status_code == 422  # no Bot chosen
    assert create(authed, mode="solo", bot={"deck_id": "nobody"}).status_code == 422  # no such Bot
    assert create(authed, mode="solo", bot={"deck_id": "riker"}).status_code == 422  # needs Second Contact


def test_solo_game_starts_at_once_against_the_bot(authed):
    r = create(authed, mode="solo", bot={"deck_id": "soval", "difficulty": "admiral", "ticking_clock": True})
    assert r.status_code == 201
    grant = r.json()
    assert grant["game"]["status"] == "active" and grant["game"]["bot"]["difficulty"] == "admiral"
    bots = {d["id"]: d["bot"] for d in authed.get("/api/content/decks").json()}
    assert bots["soval"] and bots["khan"]


def test_card_text_endpoint(authed):
    cards = authed.get("/api/content/cards").json()
    soval = cards["2SOV01"]
    assert soval["name"] == "Soval"
    assert [op["kind"] for op in soval["operations"]] == ["ACTIVATION", "ENDGAME"]


def test_cadet_game_through_the_api(authed):
    grant = create(authed, mode="cadet").json()
    game_id = grant["game"]["id"]
    assert grant["game"]["status"] == "active"
    view = authed.get(f"/api/games/{game_id}/state").json()
    assert view["mode"] == "cadet" and len(view["players"]) == 1
    r = authed.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    assert r.json()["decision"]["kind"] == "wipe"  # REQ-CTM-20
    r = authed.post(f"/api/games/{game_id}/undo")
    assert r.json()["decision"]["kind"] == "action"  # REQ-CTM-15: same undo as normal play


def test_delete_game_needs_a_seat(authed):
    grant = create(authed).json()
    game_id = grant["game"]["id"]
    assert sam(authed).delete(f"/api/games/{game_id}").status_code == 403
    r = authed.delete(f"/api/games/{game_id}")
    assert r.status_code == 204
    assert game_id not in {g["id"] for g in authed.get("/api/games").json()}
    assert authed.get(f"/api/games/{game_id}").status_code == 404
    assert authed.delete(f"/api/games/{game_id}").status_code == 404


def test_delete_started_game_by_second_player(authed):
    game_id, players = started_game(authed)
    players[0].get(f"/api/games/{game_id}/state")  # fills the state cache
    assert players[1].delete(f"/api/games/{game_id}").status_code == 204
    assert players[0].get(f"/api/games/{game_id}/state").status_code == 404


def test_moves_that_no_longer_apply_are_dropped(authed):
    """A rules change can make saved moves invalid. The game drops them, says so, and carries on."""
    from app import play
    from app.db import get_db
    from app.models import Game

    grant = create(authed, mode="cadet").json()
    game_id = grant["game"]["id"]
    db = next(get_db())
    game = db.get(Game, game_id)
    game.commands = [{"seat": 0, "option": "no-such-option", "irreversible": False, "turn": 0},
                     {"seat": 0, "option": "end", "irreversible": False, "turn": 0}]
    db.commit()
    play._cache.clear()

    view = authed.get(f"/api/games/{game_id}/state").json()
    assert view["decision"]["kind"] == "action"
    assert "2 later move(s) no longer apply" in view["log"][-1]
    assert view["can_undo"] is False

    # The game continues normally, and the note survives later rebuilds.
    r = authed.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    assert r.status_code == 200 and r.json()["decision"]["kind"] == "wipe"
    play._cache.clear()
    view = authed.get(f"/api/games/{game_id}/state").json()
    assert view["decision"]["kind"] == "wipe"
    assert any("no longer apply" in line for line in view["log"])


def test_the_box_limits_crew_decks(authed):
    """CORE-AS-3 (REQ-CORE-11): a Core Box game takes Core Box Crews only; both boxes take either."""
    assert create(authed, box="core", deck_id="georgiou").status_code == 422
    assert create(authed, deck_id="picard").status_code == 422  # the default box is To Boldly Go
    r = create(authed, box="core", deck_id="picard")
    assert r.status_code == 201 and r.json()["game"]["box"] == "core"
    game_id = r.json()["game"]["id"]
    other = sam(authed)
    join = lambda deck: other.post(f"/api/games/{game_id}/join", json={"deck_id": deck})  # noqa: E731
    assert join("kirk").status_code == 422
    assert join("sisko").status_code == 200
    assert create(authed, box="both", deck_id="georgiou").status_code == 201
    assert create(authed, box="deluxe", deck_id="georgiou").status_code == 422


def test_boxes_and_core_box_bots(authed):
    boxes = authed.get("/api/content/boxes").json()
    assert list(boxes) == ["core", "to_boldly_go", "both"] and boxes["both"]["sets"] == ["base_game", "to_boldly_go"]
    assert create(authed, mode="solo", box="core", deck_id="picard", bot={"deck_id": "sisko"}).status_code == 201
    assert create(authed, mode="solo", box="core", deck_id="picard", bot={"deck_id": "soval"}).status_code == 422
    assert create(authed, mode="solo", box="both", deck_id="picard", bot={"deck_id": "soval"}).status_code == 201


def test_the_weekday_is_stored_with_each_command_and_replayed(authed, monkeypatch):
    """REQ-SRV-52: the engine reads the weekday from the stored command, so a later replay gives the same game."""
    from app import play

    monkeypatch.setattr(play, "today", lambda: 1)  # a Tuesday
    r = create(authed, mode="cadet")
    game_id = r.json()["game"]["id"]
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 200
    from app.db import get_db
    from app.main import app
    from app.models import Game

    db = next(app.dependency_overrides.get(get_db, get_db)())
    game = db.get(Game, game_id)
    assert [c["weekday"] for c in game.commands] == [1]
    monkeypatch.setattr(play, "today", lambda: 4)  # replayed on a Friday
    play._cache.clear()
    state = play.build(game)
    assert state.weekday == 1


def test_new_games_with_promos_include_both_promo_sets(authed):
    r = create(authed, mode="cadet", promos=True)
    assert r.status_code == 201
    from app.db import get_db
    from app.main import app
    from app.models import Game

    db = next(app.dependency_overrides.get(get_db, get_db)())
    assert db.get(Game, r.json()["game"]["id"]).promo_sets == ["promo1", "promo2"]


def test_conspiracy_needs_core_box_content(authed):
    """REQ-SOLO-133, REQ-CORE-62."""
    bot = {"deck_id": "soval", "difficulty": "ensign", "conspiracy": True}
    assert create(authed, mode="solo", bot=bot).status_code == 422
    r = create(authed, mode="solo", box="both", bot={**bot, "deck_id": "picard", "ticking_clock": True})
    assert r.status_code == 201 and r.json()["game"]["bot"]["conspiracy"]
    view = authed.get(f"/api/games/{r.json()['game']['id']}")
    assert view.status_code == 200


def test_the_other_players_turn_can_be_stepped_through():
    """REQ-CLI-19: in a two-player game each player gets the other's latest turn as steps, like a Bot turn."""
    from engine.game import choose
    from engine.views import game_view
    from tests.scenario import card, given, play

    s = given(hand=["2GEO15"], empty_hand=True)  # Analyze: take an Incident to gain a Ship
    play(s, card(s, "2GEO15", zone="hand"), 0)
    while s.decision.kind != "action":
        choose(s, 0, s.decision.options[0].id, flag_irreversible=False)
    theirs = game_view(s, 1)["opponent_turn"]
    assert theirs is not None and not theirs["finished"]
    assert any(st.get("card", {}).get("id") == "2GEO15" for st in theirs["steps"])  # "plays Analyze", with its card
    assert game_view(s, 0)["opponent_turn"] is None or game_view(s, 0)["opponent_turn"]["start"] != theirs["start"]
    choose(s, 0, "end", flag_irreversible=False)
    while not (s.decision.kind == "action" and s.decision.seat == 1):
        d = s.decision
        choose(s, d.seat, {"discard": "done", "control": "skip", "trigger": "pass"}.get(d.kind, d.options[0].id),
               flag_irreversible=False)
    done = game_view(s, 1)["opponent_turn"]
    assert done["finished"] and done["start"] == theirs["start"]
    # Lines only the other player may see are left out.
    assert all(e.private_to in (None, 1) for e in s.log[done["start"]:] if any(st["text"] == e.text for st in done["steps"]))
    assert game_view(s, None)["opponent_turn"] is None  # a spectator has no "other player"


def finish_turn(client, game_id):
    """End the Action Step, place the Glory and keep the hand: the turn passes to the other player."""
    client.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    glory = client.get(f"/api/games/{game_id}/state").json()["decision"]["options"][0]["id"]
    client.post(f"/api/games/{game_id}/commands", json={"option": glory})
    return client.post(f"/api/games/{game_id}/commands", json={"option": "done"}).json()


def test_the_other_player_is_emailed_when_a_turn_ends(authed):
    """REQ-USER-25: in a two-player game the player whose turn it now is gets an email, unless they turned it off."""
    from app import mail

    game_id, players = started_game(authed)
    active = authed.get(f"/api/games/{game_id}/state").json()["active"]
    me, other = players[active], players[1 - active]
    other_email = other.get("/api/auth/me").json()["email"]
    assert other.get("/api/auth/me").json()["turn_emails"] is True  # on by default
    mail.OUTBOX.clear()
    me.post(f"/api/games/{game_id}/commands", json={"option": "end"})
    assert mail.OUTBOX == []  # a move within the turn sends nothing
    glory = me.get(f"/api/games/{game_id}/state").json()["decision"]["options"][0]["id"]
    me.post(f"/api/games/{game_id}/commands", json={"option": glory})
    assert me.post(f"/api/games/{game_id}/commands", json={"option": "done"}).json()["active"] == 1 - active
    sent = [m for m in mail.OUTBOX if m["to"] == other_email]
    assert len(sent) == 1 and "finished their turn" in sent[0]["subject"]
    assert f"/games/{game_id}" in sent[0]["body"] and "/account" in sent[0]["body"]

    # The other player turns them off: the first player is still emailed when the other's turn ends, but the other
    # player is not when the first player's next turn ends.
    assert other.patch("/api/auth/me", json={"turn_emails": False}).json()["turn_emails"] is False
    me_email = me.get("/api/auth/me").json()["email"]
    mail.OUTBOX.clear()
    finish_turn(other, game_id)
    assert [m["to"] for m in mail.OUTBOX] == [me_email]
    mail.OUTBOX.clear()
    finish_turn(me, game_id)
    assert mail.OUTBOX == []


def test_no_turn_emails_in_a_solo_game(authed):
    from app import mail

    game_id = create(authed, mode="solo", bot={"deck_id": "soval", "difficulty": "ensign"}).json()["game"]["id"]
    mail.OUTBOX.clear()
    finish_turn(authed, game_id)
    assert mail.OUTBOX == []


def test_the_name_and_the_turn_email_setting_change_separately(authed):
    assert authed.patch("/api/auth/me", json={"turn_emails": False}).json()["display_name"] == "Nick"
    me = authed.patch("/api/auth/me", json={"display_name": "Nicholas"}).json()
    assert me["display_name"] == "Nicholas" and me["turn_emails"] is False


def test_no_email_while_the_game_is_open(authed):
    """REQ-USER-25: a player with the game open sees the turn come; only an absent player is emailed."""
    from app import mail

    game_id, players = started_game(authed)
    active = authed.get(f"/api/games/{game_id}/state").json()["active"]
    me, other = players[active], players[1 - active]
    mail.OUTBOX.clear()
    with other.websocket_connect(f"/api/games/{game_id}/ws") as ws:
        ws.receive_json()
        finish_turn(me, game_id)
    assert mail.OUTBOX == []


def test_a_decision_mid_turn_is_emailed_once_until_the_player_moves(authed, monkeypatch):
    """REQ-USER-25: the other player's move needs a decision from you (a Reaction, an attack, a forced choice): one
    email, then none until you have moved."""
    from types import SimpleNamespace

    from app.db import open_session
    from app.models import Game
    from app.routes import games as routes

    game_id, players = started_game(authed)
    state = authed.get(f"/api/games/{game_id}/state").json()
    mover, waiting = state["active"], 1 - state["active"]
    asked = SimpleNamespace(decision=SimpleNamespace(seat=waiting, prompt="Discard a card (Tarah attacks)."),
                            turn=state["turn"], active=mover, result=None)
    monkeypatch.setattr(routes.play, "build", lambda game: asked)
    with open_session() as db:
        game = db.get(Game, game_id)
        email = routes.waiting_email(db, game, mover, state["turn"], mover)
        assert email is not None
        to, subject, body = email
        assert to == players[waiting].get("/api/auth/me").json()["email"]
        assert "needs a decision from you" in subject and "Discard a card (Tarah attacks)." in body
        assert routes.waiting_email(db, game, mover, state["turn"], mover) is None  # already told
        routes.waiting_email(db, game, waiting, state["turn"], mover)  # they moved...
        assert routes.waiting_email(db, game, mover, state["turn"], mover) is not None  # ...so the next one is sent
