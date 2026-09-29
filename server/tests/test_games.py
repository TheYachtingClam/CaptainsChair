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
    assert r.json()["game"]["status"] == "ready"

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
