"""The admin (requirements/19-technical-architecture.md §5.4, REQ-ADMIN-01 to -06)."""

from tests.conftest import another_browser, sign_in_as

SOLO = {"deck_id": "kirk", "mode": "solo", "bot": {"deck_id": "soval", "difficulty": "ensign"}}


def waiting_game(client):
    r = client.post("/api/games", json={"deck_id": "kirk", "mode": "two_player"})
    assert r.status_code == 201
    return r.json()


def admin_browser(client):
    return sign_in_as(another_browser(client), "admin@example.com", "Admin", admin=True)


def test_an_ordinary_account_is_not_the_admin(authed):
    assert authed.get("/api/admin/status").json() == {"admin": False}
    assert authed.get("/api/admin/games").status_code == 403


def test_admin_needs_a_session(client):
    assert client.get("/api/admin/games").status_code == 401


def test_only_the_creator_or_the_admin_can_delete_a_waiting_game(authed):
    game_id = waiting_game(authed)["game"]["id"]
    other = sign_in_as(another_browser(authed), "sam@example.com", "Sam")
    assert other.delete(f"/api/games/{game_id}").status_code == 403  # no seat (REQ-ADMIN-05)
    assert other.delete(f"/api/admin/games/{game_id}").status_code == 403
    admin = admin_browser(authed)
    assert admin.get("/api/admin/status").json()["admin"]
    listed = {g["id"]: g for g in admin.get("/api/admin/games").json()}
    assert listed[game_id]["status"] == "waiting" and listed[game_id]["players"] == ["Nick"]
    assert admin.delete(f"/api/admin/games/{game_id}").status_code == 204
    assert authed.get(f"/api/games/{game_id}").status_code == 404
    assert admin.delete(f"/api/admin/games/{game_id}").status_code == 404


def test_the_creator_can_delete_their_waiting_game(authed):
    grant = waiting_game(authed)
    assert authed.delete(f"/api/games/{grant['game']['id']}").status_code == 204


def test_admin_deletes_a_campaign(authed):
    camp = authed.post("/api/campaigns", json={"deck_id": "kirk"}).json()["campaign"]
    admin = admin_browser(authed)
    assert camp["id"] in {c["id"] for c in admin.get("/api/admin/campaigns").json()}
    assert admin.delete(f"/api/admin/campaigns/{camp['id']}").status_code == 204
    assert camp["id"] not in {c["id"] for c in admin.get("/api/admin/campaigns").json()}


def test_the_admin_takes_over_a_seat(authed):
    """REQ-ADMIN-06: the seat moves to the admin's account; the player is locked out."""
    game_id = authed.post("/api/games", json=SOLO).json()["game"]["id"]
    assert authed.post(f"/api/admin/games/{game_id}/seats/0/take").status_code == 403  # not the admin
    admin = admin_browser(authed)
    assert admin.post(f"/api/admin/games/{game_id}/seats/1/take").status_code == 404  # no such seat
    assert admin.post("/api/admin/games/nope/seats/0/take").status_code == 404
    took = admin.post(f"/api/admin/games/{game_id}/seats/0/take")
    assert took.status_code == 200 and took.json()["display_name"] == "Nick"
    assert authed.get(f"/api/games/{game_id}").json()["your_seat"] is None
    state = admin.get(f"/api/games/{game_id}/state").json()
    assert state["you"] == 0
    option = state["decision"]["options"][0]["id"]
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": option}).status_code == 403
    assert admin.post(f"/api/games/{game_id}/commands", json={"option": option}).status_code == 200


def test_the_player_whose_seat_is_taken_is_told_and_disconnected(authed):
    game_id = authed.post("/api/games", json=SOLO).json()["game"]["id"]
    admin = admin_browser(authed)
    with authed.websocket_connect(f"/api/games/{game_id}/ws") as ws:
        assert ws.receive_json()["type"] == "hello"
        assert ws.receive_json()["type"] == "presence"
        assert admin.post(f"/api/admin/games/{game_id}/seats/0/take").status_code == 200
        assert ws.receive_json() == {"type": "seat_taken", "seat": 0}
