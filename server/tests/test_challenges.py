"""Challenging another player to a game (requirements/19-technical-architecture.md REQ-USER-50 to -53)."""

from app import mail
from tests.conftest import another_browser, sign_in_as


def players(client):
    nick = sign_in_as(client)
    sam = sign_in_as(another_browser(client), "sam@example.com", "Sam")
    return nick, sam


def account(browser):
    return browser.get("/api/auth/me").json()


def challenge(nick, sam, **extra):
    body = {"deck_id": "kirk", "mode": "two_player", "opponent_id": account(sam)["id"], **extra}
    r = nick.post("/api/games", json=body)
    assert r.status_code == 201, r.text
    return r.json()["game"]


def test_opponents_are_other_active_accounts_by_name(client):
    """REQ-USER-50: by display name only, never the email address, and not yourself."""
    nick, sam = players(client)
    listed = nick.get("/api/me/opponents").json()
    assert listed == [{"id": account(sam)["id"], "display_name": "Sam"}]


def test_a_challenge_emails_the_opponent_with_a_link(client):
    """REQ-USER-51: sent at once, with the challenger, their Crew, the game and the link."""
    nick, sam = players(client)
    mail.OUTBOX.clear()
    game = challenge(nick, sam, expansions=["second_contact"])
    assert game["challenge"] == {"user_id": account(sam)["id"], "display_name": "Sam"}
    sent = mail.OUTBOX[-1]
    assert sent["to"] == "sam@example.com"
    assert sent["subject"] == "Nick challenges you to a game of Captain's Chair"
    assert "Nick plays Kirk." in sent["body"] and "To Boldly Go, Second Contact" in sent["body"]
    assert f"/games/{game['id']}" in sent["body"]


def test_the_challenge_email_ignores_the_waiting_email_setting(client):
    nick, sam = players(client)
    sam.patch("/api/auth/me", json={"turn_emails": False})
    mail.OUTBOX.clear()
    challenge(nick, sam)
    assert [m["to"] for m in mail.OUTBOX] == ["sam@example.com"]


def test_only_the_challenged_player_sees_and_joins_it(client):
    """REQ-USER-52: hidden from everyone else, and only Sam may take the seat."""
    nick, sam = players(client)
    kim = sign_in_as(another_browser(client), "kim@example.com", "Kim")
    game = challenge(nick, sam)
    assert game["id"] not in {g["id"] for g in kim.get("/api/games").json()}
    assert game["id"] in {g["id"] for g in sam.get("/api/games").json()}
    assert game["id"] in {g["id"] for g in nick.get("/api/games").json()}
    r = kim.post(f"/api/games/{game['id']}/join", json={"deck_id": "georgiou"})
    assert r.status_code == 403 and "challenge for Sam" in r.json()["detail"]
    r = sam.post(f"/api/games/{game['id']}/join", json={"deck_id": "georgiou"})
    assert r.status_code == 200, r.text
    assert r.json()["game"]["status"] == "active"


def test_declining_deletes_the_game_and_tells_the_challenger(client):
    """REQ-USER-53."""
    nick, sam = players(client)
    game = challenge(nick, sam)
    assert nick.post(f"/api/games/{game['id']}/decline").status_code == 403  # only the challenged player
    mail.OUTBOX.clear()
    assert sam.post(f"/api/games/{game['id']}/decline").status_code == 204
    assert nick.get(f"/api/games/{game['id']}").status_code == 404
    sent = mail.OUTBOX[-1]
    assert sent["to"] == "nick@example.com" and sent["subject"] == "Sam declined your challenge"


def test_a_started_challenge_cannot_be_declined(client):
    nick, sam = players(client)
    game = challenge(nick, sam)
    sam.post(f"/api/games/{game['id']}/join", json={"deck_id": "georgiou"})
    assert sam.post(f"/api/games/{game['id']}/decline").status_code == 409


def test_who_can_be_challenged(client):
    """REQ-USER-50: two-player games only, not yourself, not a disabled or unknown account."""
    nick, sam = players(client)
    me = account(nick)["id"]
    for body, why in [({"mode": "cadet", "opponent_id": account(sam)["id"]}, "two-player"),
                      ({"opponent_id": me}, "yourself"),
                      ({"opponent_id": "nobody"}, "cannot be challenged")]:
        r = nick.post("/api/games", json={"deck_id": "kirk", "mode": "two_player", **body})
        assert r.status_code == 422 and why in r.json()["detail"], r.text


def test_an_open_game_is_still_open_to_anyone(client):
    nick, sam = players(client)
    r = nick.post("/api/games", json={"deck_id": "kirk", "mode": "two_player"})
    game = r.json()["game"]
    assert game["challenge"] is None
    assert game["id"] in {g["id"] for g in sam.get("/api/games").json()}
