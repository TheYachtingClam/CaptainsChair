from tests.conftest import sign_in_as


def make_user(email="nick@example.com", password="correct horse"):
    from app import users
    from app.db import open_session

    with open_session() as db:
        users.create_user(db, email, "Nick", password)
        db.commit()


def test_health_needs_no_login(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_protected_endpoints_need_login(client):
    assert client.get("/api/games").status_code == 401
    assert client.get("/api/content/decks").status_code == 401
    assert client.get("/api/auth/session").status_code == 401


def test_wrong_password(client):
    make_user()
    r = client.post("/api/auth/login", json={"email": "nick@example.com", "password": "nope"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect email or password"


def test_login_needs_an_email(client):
    assert client.post("/api/auth/login", json={"password": "correct horse"}).status_code == 422


def test_login_and_logout(client):
    make_user()
    r = client.post("/api/auth/login", json={"email": "nick@example.com", "password": "correct horse"})
    assert r.status_code == 204
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie
    assert client.get("/api/auth/session").status_code == 204
    client.post("/api/auth/logout")
    assert client.get("/api/auth/session").status_code == 401


def test_rate_limit(client):
    make_user()
    for _ in range(5):
        client.post("/api/auth/login", json={"email": "nick@example.com", "password": "nope"})
    r = client.post("/api/auth/login", json={"email": "nick@example.com", "password": "correct horse"})
    assert r.status_code == 429


def test_a_forged_cookie_is_not_a_session(client):
    client.cookies.set("cc_session", "not-a-signed-value")
    assert client.get("/api/auth/session").status_code == 401


def test_admin_endpoints_need_the_admin_flag(client):
    sign_in_as(client)
    assert client.get("/api/admin/games").status_code == 403
    assert client.get("/api/admin/status").json() == {"admin": False}
