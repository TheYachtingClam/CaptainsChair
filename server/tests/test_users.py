"""User accounts (requirements/19-technical-architecture.md §5, REQ-USER-01 to -24; plans/users.md Step 2)."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app import mail, users
from app.auth import login_limiter
from app.db import open_session
from app.models import Invite, PasswordReset, User


def invite(email="ann@example.com"):
    with open_session() as db:
        _, code = users.create_invite(db, email, None)
        db.commit()
    return code


def sign_up(client, email="ann@example.com", name="Ann", password="correct horse"):
    code = invite(email)
    r = client.post("/api/auth/signup", json={"code": code, "display_name": name, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


def second_browser(client):
    other = TestClient(client.app)
    return other


def last_link(path):
    body = mail.OUTBOX[-1]["body"]
    return next(w for w in body.split() if path in w).split("code=")[1]


# ------------------------------------------------------------------ invitations and sign-up

def test_an_invitation_creates_an_account_and_signs_in(client):
    mail.OUTBOX.clear()
    code = invite("Ann@Example.com")
    sent = mail.OUTBOX[-1]
    assert sent["to"] == "ann@example.com" and "/signup?code=" in sent["body"]
    assert client.get(f"/api/auth/invite/{code}").json() == {"email": "ann@example.com"}
    r = client.post("/api/auth/signup", json={"code": code, "display_name": "  Ann   L ", "password": "correct horse"})
    assert r.status_code == 200 and r.json()["display_name"] == "Ann L" and not r.json()["is_admin"]
    assert client.get("/api/auth/me").json()["email"] == "ann@example.com"
    assert client.get("/api/games").status_code == 200  # an account is a session (REQ-USER-03)
    again = client.post("/api/auth/signup", json={"code": code, "display_name": "Ann", "password": "correct horse"})
    assert again.status_code == 422 and "used" in again.json()["detail"]  # once only
    assert client.get(f"/api/auth/invite/{code}").status_code == 404


def test_invitations_expire_and_cannot_be_for_an_existing_account(client):
    code = invite("bob@example.com")
    with open_session() as db:
        row = db.query(Invite).one()
        row.expires_at = users.now() - timedelta(minutes=1)
        db.commit()
    r = client.post("/api/auth/signup", json={"code": code, "display_name": "Bob", "password": "correct horse"})
    assert r.status_code == 422 and "expired" in r.json()["detail"]
    sign_up(client, "carol@example.com", "Carol")
    with open_session() as db, pytest.raises(users.UserError):
        users.create_invite(db, "CAROL@example.com", None)
    assert client.post("/api/auth/signup", json={"code": "made-up", "display_name": "X",
                                                 "password": "correct horse"}).status_code == 422


def test_sign_up_checks_the_name_and_password(client):
    code = invite()
    short = client.post("/api/auth/signup", json={"code": code, "display_name": "Ann", "password": "short"})
    assert short.status_code == 422 and "8 characters" in short.json()["detail"]
    blank = client.post("/api/auth/signup", json={"code": code, "display_name": "   ", "password": "correct horse"})
    assert blank.status_code == 422
    assert client.post("/api/auth/signup", json={"code": code, "display_name": "Ann",
                                                  "password": "correct horse"}).status_code == 200


def test_passwords_are_stored_hashed():
    stored = users.hash_password("correct horse")
    assert stored.startswith("scrypt$") and "correct horse" not in stored
    assert users.check_password("correct horse", stored) and not users.check_password("wrong horse", stored)
    assert stored != users.hash_password("correct horse")  # salted


# ------------------------------------------------------------------ signing in

def test_signing_in_and_out(client):
    sign_up(client)
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401 and client.get("/api/games").status_code == 401
    r = client.post("/api/auth/login", json={"email": " ANN@example.com", "password": "correct horse"})
    assert r.status_code == 204 and client.get("/api/auth/me").json()["display_name"] == "Ann"


def test_a_wrong_email_and_a_wrong_password_look_the_same(client):
    sign_up(client)
    client.post("/api/auth/logout")
    wrong_password = client.post("/api/auth/login", json={"email": "ann@example.com", "password": "nope nope"})
    unknown = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "nope nope"})
    assert wrong_password.status_code == unknown.status_code == 401
    assert wrong_password.json() == unknown.json() == {"detail": "Incorrect email or password"}


def test_sign_in_is_rate_limited(client):
    login_limiter.reset()
    codes = [client.post("/api/auth/login", json={"email": "x@example.com", "password": "nope nope"}).status_code
             for _ in range(7)]
    assert codes[:5] == [401] * 5 and codes[-1] == 429


def test_a_disabled_account_cannot_sign_in_and_its_sessions_end(client):
    sign_up(client)
    with open_session() as db:
        db.query(User).one().disabled = True
        db.commit()
    assert client.get("/api/games").status_code == 401
    assert client.post("/api/auth/login", json={"email": "ann@example.com", "password": "correct horse"}).status_code == 401


def test_the_shared_site_password_still_works_until_step_8(client):
    assert client.post("/api/auth/login", json={"password": "test-password"}).status_code == 204
    assert client.get("/api/games").status_code == 200
    assert client.get("/api/auth/me").status_code == 401  # but it is not an account


def test_an_account_session_opens_the_game_socket(client):
    sign_up(client)
    r = client.post("/api/games", json={"display_name": "Ann", "deck_id": "kirk", "mode": "solo",
                                        "bot": {"deck_id": "soval", "difficulty": "ensign"}})
    game_id, token = r.json()["game"]["id"], r.json()["seat_token"]
    with client.websocket_connect(f"/api/games/{game_id}/ws?seat={token}") as ws:
        assert ws.receive_json()["type"] == "hello"


# ------------------------------------------------------------------ the account

def test_changing_the_display_name(client):
    sign_up(client)
    assert client.patch("/api/auth/me", json={"display_name": "Annie"}).json()["display_name"] == "Annie"
    assert client.patch("/api/auth/me", json={"display_name": "x" * 41}).status_code == 422


def test_changing_the_password_signs_out_other_browsers(client):
    sign_up(client)
    other = second_browser(client)
    assert other.post("/api/auth/login", json={"email": "ann@example.com", "password": "correct horse"}).status_code == 204
    assert other.get("/api/auth/me").status_code == 200
    mail.OUTBOX.clear()
    wrong = client.post("/api/auth/password", json={"current": "nope nope", "new": "battery staple"})
    assert wrong.status_code == 422
    assert client.post("/api/auth/password", json={"current": "correct horse", "new": "battery staple"}).status_code == 204
    assert client.get("/api/auth/me").status_code == 200  # this browser stays signed in
    assert other.get("/api/auth/me").status_code == 401  # the other one does not
    assert mail.OUTBOX[-1]["subject"] == "Your Captain's Chair password was changed"
    client.post("/api/auth/logout")
    assert client.post("/api/auth/login", json={"email": "ann@example.com", "password": "battery staple"}).status_code == 204


# ------------------------------------------------------------------ forgotten passwords

def test_forgot_password_never_says_whether_an_account_exists(client):
    sign_up(client)
    mail.OUTBOX.clear()
    known = client.post("/api/auth/forgot", json={"email": "ann@example.com"})
    unknown = client.post("/api/auth/forgot", json={"email": "nobody@example.com"})
    assert known.status_code == unknown.status_code == 202 and known.json() == unknown.json()
    assert [m["to"] for m in mail.OUTBOX] == ["ann@example.com"]  # only the real account gets an email


def test_a_reset_link_works_once_and_signs_out_everywhere(client):
    sign_up(client)
    other = second_browser(client)
    other.post("/api/auth/login", json={"email": "ann@example.com", "password": "correct horse"})
    client.post("/api/auth/logout")
    client.post("/api/auth/forgot", json={"email": "ann@example.com"})
    code = last_link("/reset?code=")
    r = client.post("/api/auth/reset", json={"code": code, "password": "battery staple"})
    assert r.status_code == 200 and client.get("/api/auth/me").status_code == 200  # signed in here
    assert other.get("/api/auth/me").status_code == 401  # and out everywhere else
    assert client.post("/api/auth/reset", json={"code": code, "password": "another one"}).status_code == 422


def test_a_reset_link_expires(client):
    sign_up(client)
    client.post("/api/auth/forgot", json={"email": "ann@example.com"})
    code = last_link("/reset?code=")
    with open_session() as db:
        db.query(PasswordReset).one().expires_at = users.now() - timedelta(minutes=1)
        db.commit()
    r = client.post("/api/auth/reset", json={"code": code, "password": "battery staple"})
    assert r.status_code == 422 and "expired" in r.json()["detail"]
