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
        _, code, _ = users.create_invite(db, email, None)
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


# ------------------------------------------------------------------ the admin as an account (plans/users.md Step 3)

def make_admin(client, email="nick@example.com"):
    """Run the first-admin command and sign up from its invitation, as the owner would."""
    from app import create_admin

    mail.OUTBOX.clear()
    assert create_admin.main([email]) == 0
    code = last_link("/signup?code=")
    r = client.post("/api/auth/signup", json={"code": code, "display_name": "Nick", "password": "correct horse"})
    assert r.status_code == 200 and r.json()["is_admin"]
    return r.json()


def test_the_first_admin_comes_from_an_admin_invitation(client, capsys, monkeypatch):
    from app import create_admin
    from app.config import get_settings

    assert client.post("/api/auth/login", json={"password": "test-password"}).status_code == 204
    assert client.get("/api/admin/status").json() == {"enabled": False, "admin": False, "account": False}
    monkeypatch.setattr(get_settings(), "admin_email", "nick@example.com")
    mail.OUTBOX.clear()
    assert create_admin.main([]) == 0  # ADMIN_EMAIL
    assert "/signup?code=" in capsys.readouterr().out
    assert mail.OUTBOX[-1]["to"] == "nick@example.com" and "as its admin" in mail.OUTBOX[-1]["body"]
    code = last_link("/signup?code=")
    assert client.post("/api/auth/signup", json={"code": code, "display_name": "Nick",
                                                 "password": "correct horse"}).json()["is_admin"]
    assert client.get("/api/admin/status").json() == {"enabled": True, "admin": True, "account": True}
    assert client.get("/api/admin/games").status_code == 200
    # Running it again for an existing account makes that account admin instead of inviting it.
    assert create_admin.main(["nick@example.com"]) == 0


def test_the_admin_invites_and_manages_accounts(client):
    admin = make_admin(client)
    mail.OUTBOX.clear()
    r = client.post("/api/admin/invites", json={"email": "ann@example.com"})
    assert r.status_code == 201 and r.json()["link"].endswith(last_link("/signup?code="))
    assert mail.OUTBOX[-1]["subject"] == "Nick invited you to Captain's Chair Online"
    assert [i["email"] for i in client.get("/api/admin/invites").json()] == ["ann@example.com"]
    assert client.post("/api/admin/invites", json={"email": "nick@example.com"}).status_code == 422  # has an account
    spare = client.post("/api/admin/invites", json={"email": "spare@example.com"}).json()
    assert client.delete(f"/api/admin/invites/{spare['id']}").status_code == 204
    assert client.get(f"/api/auth/invite/{spare['link'].split('code=')[1]}").status_code == 404

    ann = TestClient(client.app)
    code = r.json()["link"].split("code=")[1]
    ann_user = ann.post("/api/auth/signup", json={"code": code, "display_name": "Ann", "password": "correct horse"}).json()
    assert not ann_user["is_admin"] and ann.get("/api/admin/users").status_code == 403
    listed = {u["email"]: u for u in client.get("/api/admin/users").json()}
    assert set(listed) == {"nick@example.com", "ann@example.com"} and listed["nick@example.com"]["is_admin"]

    reset = client.post(f"/api/admin/users/{ann_user['id']}/reset")
    assert reset.status_code == 200 and "/reset?code=" in reset.json()["link"] and mail.OUTBOX[-1]["to"] == "ann@example.com"
    assert client.patch(f"/api/admin/users/{ann_user['id']}", json={"disabled": True}).json()["disabled"]
    assert ann.get("/api/auth/me").status_code == 401  # signed out at once
    assert client.patch(f"/api/admin/users/{ann_user['id']}", json={"disabled": False, "is_admin": True}).json()["is_admin"]
    # An admin cannot lock themselves out (REQ-USER-31).
    assert client.patch(f"/api/admin/users/{admin['id']}", json={"is_admin": False}).status_code == 409
    assert client.patch(f"/api/admin/users/{admin['id']}", json={"disabled": True}).status_code == 409



# ------------------------------------------------------------------ sending email (plans/users.md Step 4)

class FakeSMTP:
    sent: list = []
    fail = False

    def __init__(self, host, port, timeout=None, context=None):
        self.calls = [("connect", host, port)]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self, context=None):
        self.calls.append(("starttls",))

    def login(self, user, password):
        if FakeSMTP.fail:
            import smtplib

            raise smtplib.SMTPAuthenticationError(535, b"Username and Password not accepted")
        self.calls.append(("login", user, password))

    def send_message(self, message):
        FakeSMTP.sent.append((self.calls, message))


@pytest.fixture
def gmail(monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    for key, value in {"smtp_host": "smtp.gmail.com", "smtp_port": 587, "smtp_user": "nick@example.com",
                       "smtp_password": "app-password", "mail_from": "",
                       "public_url": "https://example.fly.dev"}.items():
        monkeypatch.setattr(settings, key, value)
    import smtplib

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    FakeSMTP.sent = []
    FakeSMTP.fail = False
    return FakeSMTP


def test_emails_go_out_through_gmail(client, gmail):
    mail.OUTBOX.clear()
    with open_session() as db:
        _, code, outcome = users.create_invite(db, "ann@example.com", None)
        db.commit()
    assert outcome == "sent" and not mail.OUTBOX
    calls, message = gmail.sent[-1]
    assert calls == [("connect", "smtp.gmail.com", 587), ("starttls",), ("login", "nick@example.com", "app-password")]
    assert message["To"] == "ann@example.com" and message["From"] == "Captain's Chair Online <nick@example.com>"
    assert f"https://example.fly.dev/signup?code={code}" in message.get_content()


def test_a_failed_email_never_breaks_the_request(client, gmail, caplog):
    admin = make_admin_without_mail(client)
    gmail.fail = True
    r = client.post("/api/admin/invites", json={"email": "bob@example.com"})
    assert r.status_code == 201 and r.json()["mail"] == "failed" and "/signup?code=" in r.json()["link"]
    assert client.post("/api/auth/forgot", json={"email": "nick@example.com"}).status_code == 202
    assert "Could not send the email" in caplog.text and "code=" not in caplog.text  # the link is never logged
    _ = admin


def make_admin_without_mail(client):
    with open_session() as db:
        user = users.create_user(db, "nick@example.com", "Nick", "correct horse", is_admin=True)
        db.commit()
    assert client.post("/api/auth/login", json={"email": "nick@example.com", "password": "correct horse"}).status_code == 204
    return user


def test_without_a_password_email_is_only_logged(client, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "smtp_host", "smtp.gmail.com")
    monkeypatch.setattr(get_settings(), "smtp_password", "")
    assert mail.send("ann@example.com", "Hello", "Body") == "logged"
