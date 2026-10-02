import pytest
from starlette.websockets import WebSocketDisconnect


def create(client, **overrides):
    body = {"display_name": "Nick", "deck_id": "georgiou", "mode": "two_player", **overrides}
    return client.post("/api/games", json=body)


def test_decks_listed(authed):
    ids = {d["id"] for d in authed.get("/api/content/decks").json()}
    assert {"georgiou", "soval", "freeman"} <= ids


def test_create_and_join(authed):
    r = create(authed)
    assert r.status_code == 201
    grant = r.json()
    game_id = grant["game"]["id"]
    assert grant["game"]["open_seats"] == 1

    r = authed.post(f"/api/games/{game_id}/join", json={"display_name": "Sam", "deck_id": "soval"})
    assert r.status_code == 200
    assert r.json()["seat_index"] == 1
    assert r.json()["game"]["status"] == "active"

    view = authed.get(f"/api/games/{game_id}", headers={"X-Seat-Token": grant["seat_token"]}).json()
    assert view["your_seat"] == 0
    assert authed.get(f"/api/games/{game_id}").json()["your_seat"] is None


def test_full_game_rejects_join(authed):
    game_id = create(authed).json()["game"]["id"]
    authed.post(f"/api/games/{game_id}/join", json={"display_name": "Sam", "deck_id": "soval"})
    r = authed.post(f"/api/games/{game_id}/join", json={"display_name": "Eve", "deck_id": "kirk"})
    assert r.status_code == 409


def test_expansion_deck_needs_expansion(authed):
    assert create(authed, deck_id="freeman").status_code == 422
    assert create(authed, deck_id="freeman", expansions=["second_contact"]).status_code == 201


def test_seat_tokens_are_not_listed(authed):
    create(authed)
    assert "token" not in authed.get("/api/games").text


def test_websocket_presence(authed):
    grant = create(authed).json()
    game_id = grant["game"]["id"]
    with authed.websocket_connect(f"/api/games/{game_id}/ws?seat={grant['seat_token']}") as ws:
        assert ws.receive_json() == {"type": "hello", "your_seat": 0}
        assert ws.receive_json() == {"type": "presence", "connected": [0]}
        ws.send_json({"type": "ping"})
        assert ws.receive_json() == {"type": "pong"}


def test_websocket_rejects_bad_seat(authed):
    game_id = create(authed).json()["game"]["id"]
    with pytest.raises(WebSocketDisconnect):
        with authed.websocket_connect(f"/api/games/{game_id}/ws?seat=wrong") as ws:
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
    a = create(authed).json()
    b = authed.post(f"/api/games/{a['game']['id']}/join", json={"display_name": "Sam", "deck_id": "soval"}).json()
    return a["game"]["id"], {0: a["seat_token"], 1: b["seat_token"]}


def test_game_starts_and_plays(authed):
    game_id, tokens = started_game(authed)
    views = {seat: authed.get(f"/api/games/{game_id}/state", headers={"X-Seat-Token": t}).json() for seat, t in tokens.items()}
    active = views[0]["active"]
    assert views[active]["decision"]["options"]
    assert "options" not in views[1 - active]["decision"]
    assert views[0]["players"][1]["hand"] is None and views[1]["players"][1]["hand"] is not None

    h = {"X-Seat-Token": tokens[1 - active]}
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}, headers=h).status_code == 409

    h = {"X-Seat-Token": tokens[active]}
    r = authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}, headers=h)
    assert r.status_code == 200 and r.json()["decision"]["kind"] == "glory"
    assert r.json()["can_undo"] is True

    r = authed.post(f"/api/games/{game_id}/undo", headers=h)
    assert r.json()["decision"]["kind"] == "action"
    assert r.json()["can_undo"] is False


def test_irreversible_command_cannot_be_undone(authed):
    game_id, tokens = started_game(authed)
    h0 = {"X-Seat-Token": tokens[0]}
    active = authed.get(f"/api/games/{game_id}/state", headers=h0).json()["active"]
    h = {"X-Seat-Token": tokens[active]}
    authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}, headers=h)
    glory = authed.get(f"/api/games/{game_id}/state", headers=h).json()["decision"]["options"][0]["id"]
    authed.post(f"/api/games/{game_id}/commands", json={"option": glory}, headers=h)
    r = authed.post(f"/api/games/{game_id}/commands", json={"option": "done"}, headers=h)
    assert r.json()["active"] != active and r.json()["can_undo"] is False
    assert authed.post(f"/api/games/{game_id}/undo", headers=h).status_code == 409


def test_state_needs_a_seat_to_act(authed):
    game_id, _ = started_game(authed)
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 403


def test_solo_not_available(authed):
    assert create(authed, mode="solo").status_code == 422


def test_card_text_endpoint(authed):
    cards = authed.get("/api/content/cards").json()
    soval = cards["2SOV01"]
    assert soval["name"] == "Soval"
    assert [op["kind"] for op in soval["operations"]] == ["ACTIVATION", "ENDGAME"]


def test_cadet_game_through_the_api(authed):
    grant = create(authed, mode="cadet").json()
    game_id = grant["game"]["id"]
    assert grant["game"]["status"] == "active"
    h = {"X-Seat-Token": grant["seat_token"]}
    view = authed.get(f"/api/games/{game_id}/state", headers=h).json()
    assert view["mode"] == "cadet" and len(view["players"]) == 1
    r = authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}, headers=h)
    assert r.json()["decision"]["kind"] == "wipe"  # REQ-CTM-20
    r = authed.post(f"/api/games/{game_id}/undo", headers=h)
    assert r.json()["decision"]["kind"] == "action"  # REQ-CTM-15: same undo as normal play


def test_delete_game_needs_a_seat(authed):
    grant = create(authed).json()
    game_id = grant["game"]["id"]
    assert authed.delete(f"/api/games/{game_id}").status_code == 403
    assert authed.delete(f"/api/games/{game_id}", headers={"X-Seat-Token": "nope"}).status_code == 403
    r = authed.delete(f"/api/games/{game_id}", headers={"X-Seat-Token": grant["seat_token"]})
    assert r.status_code == 204
    assert game_id not in {g["id"] for g in authed.get("/api/games").json()}
    assert authed.get(f"/api/games/{game_id}").status_code == 404
    assert authed.delete(f"/api/games/{game_id}", headers={"X-Seat-Token": grant["seat_token"]}).status_code == 404


def test_delete_started_game_by_second_player(authed):
    game_id, tokens = started_game(authed)
    authed.get(f"/api/games/{game_id}/state", headers={"X-Seat-Token": tokens[0]})  # fills the state cache
    assert authed.delete(f"/api/games/{game_id}", headers={"X-Seat-Token": tokens[1]}).status_code == 204
    assert authed.get(f"/api/games/{game_id}/state", headers={"X-Seat-Token": tokens[0]}).status_code == 404
