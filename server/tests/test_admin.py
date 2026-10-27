"""The admin (requirements/19-technical-architecture.md §5.3, REQ-ADMIN-01 to -05)."""

import pytest

from app.config import get_settings


@pytest.fixture
def admin_on(monkeypatch):
    monkeypatch.setattr(get_settings(), "admin_password", "admin-secret")


def waiting_game(client):
    r = client.post("/api/games", json={"display_name": "A", "deck_id": "kirk", "mode": "two_player"})
    assert r.status_code == 201
    return r.json()


def test_without_admin_password_there_is_no_admin(authed):
    assert authed.get("/api/admin/status").json() == {"enabled": False, "admin": False, "account": False}
    assert authed.post("/api/admin/login", json={"password": ""}).status_code == 404
    assert authed.get("/api/admin/games").status_code == 403


def test_admin_needs_a_session_first(client, admin_on):
    assert client.post("/api/admin/login", json={"password": "admin-secret"}).status_code == 401


def test_wrong_admin_password(authed, admin_on):
    r = authed.post("/api/admin/login", json={"password": "nope"})
    assert r.status_code == 401 and r.json()["detail"] == "Incorrect password"
    assert authed.get("/api/admin/status").json() == {"enabled": True, "admin": False, "account": False}


def test_only_the_creator_or_the_admin_can_delete_a_waiting_game(authed, admin_on):
    grant = waiting_game(authed)
    game_id = grant["game"]["id"]
    # Anyone else with the site password: no seat token, so no delete (REQ-ADMIN-05).
    assert authed.delete(f"/api/games/{game_id}").status_code == 403
    assert authed.delete(f"/api/admin/games/{game_id}").status_code == 403  # not signed in as admin
    assert authed.post("/api/admin/login", json={"password": "admin-secret"}).status_code == 204
    assert authed.get("/api/admin/status").json()["admin"]
    listed = {g["id"]: g for g in authed.get("/api/admin/games").json()}
    assert listed[game_id]["status"] == "waiting" and listed[game_id]["players"] == ["A"]
    assert authed.delete(f"/api/admin/games/{game_id}").status_code == 204
    assert authed.get(f"/api/games/{game_id}").status_code == 404
    assert authed.delete(f"/api/admin/games/{game_id}").status_code == 404


def test_the_creator_can_still_delete_their_waiting_game(authed):
    grant = waiting_game(authed)
    r = authed.delete(f"/api/games/{grant['game']['id']}", headers={"X-Seat-Token": grant["seat_token"]})
    assert r.status_code == 204


def test_admin_deletes_a_campaign(authed, admin_on):
    camp = authed.post("/api/campaigns", json={"display_name": "C", "deck_id": "kirk"}).json()["campaign"]
    authed.post("/api/admin/login", json={"password": "admin-secret"})
    assert camp["id"] in {c["id"] for c in authed.get("/api/admin/campaigns").json()}
    assert authed.delete(f"/api/admin/campaigns/{camp['id']}").status_code == 204
    assert camp["id"] not in {c["id"] for c in authed.get("/api/admin/campaigns").json()}


def test_changing_the_admin_password_ends_admin_sessions(authed, admin_on, monkeypatch):
    authed.post("/api/admin/login", json={"password": "admin-secret"})
    assert authed.get("/api/admin/status").json()["admin"]
    monkeypatch.setattr(get_settings(), "admin_password", "another-secret")
    assert not authed.get("/api/admin/status").json()["admin"]
    assert authed.get("/api/admin/games").status_code == 403


def test_admin_sign_out(authed, admin_on):
    authed.post("/api/admin/login", json={"password": "admin-secret"})
    assert authed.post("/api/admin/logout").status_code == 204
    assert not authed.get("/api/admin/status").json()["admin"]


def test_the_admin_takes_over_a_seat(authed, admin_on):
    """REQ-ADMIN-06: a new seat token for the admin; the player's old one stops working."""
    r = authed.post("/api/games", json={"display_name": "Ann", "deck_id": "kirk", "mode": "solo",
                                        "bot": {"deck_id": "soval", "difficulty": "ensign"}})
    game_id, ann = r.json()["game"]["id"], {"X-Seat-Token": r.json()["seat_token"]}
    assert authed.post(f"/api/admin/games/{game_id}/seats/0/take").status_code == 403  # not the admin yet
    assert authed.post("/api/admin/login", json={"password": "admin-secret"}).status_code == 204
    assert authed.post(f"/api/admin/games/{game_id}/seats/1/take").status_code == 404  # no such seat
    assert authed.post("/api/admin/games/nope/seats/0/take").status_code == 404
    took = authed.post(f"/api/admin/games/{game_id}/seats/0/take")
    assert took.status_code == 200 and took.json()["display_name"] == "Ann"
    admin = {"X-Seat-Token": took.json()["seat_token"]}
    assert authed.get(f"/api/games/{game_id}", headers=ann).json()["your_seat"] is None
    state = authed.get(f"/api/games/{game_id}/state", headers=admin).json()
    assert state["you"] == 0
    option = state["decision"]["options"][0]["id"]
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": option}, headers=ann).status_code == 403
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": option}, headers=admin).status_code == 200


def test_the_player_whose_seat_is_taken_is_told_and_disconnected(authed, admin_on):
    r = authed.post("/api/games", json={"display_name": "Ann", "deck_id": "kirk", "mode": "solo",
                                        "bot": {"deck_id": "soval", "difficulty": "ensign"}})
    game_id, token = r.json()["game"]["id"], r.json()["seat_token"]
    assert authed.post("/api/admin/login", json={"password": "admin-secret"}).status_code == 204
    with authed.websocket_connect(f"/api/games/{game_id}/ws?seat={token}") as ws:
        assert ws.receive_json()["type"] == "hello"
        assert ws.receive_json()["type"] == "presence"
        assert authed.post(f"/api/admin/games/{game_id}/seats/0/take").status_code == 200
        assert ws.receive_json() == {"type": "seat_taken", "seat": 0}
