def test_health_needs_no_login(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_protected_endpoints_need_login(client):
    assert client.get("/api/games").status_code == 401
    assert client.get("/api/content/decks").status_code == 401
    assert client.get("/api/auth/session").status_code == 401


def test_wrong_password(client):
    r = client.post("/api/auth/login", json={"password": "nope"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect password"


def test_login_and_logout(client):
    r = client.post("/api/auth/login", json={"password": "test-password"})
    assert r.status_code == 204
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie
    assert client.get("/api/auth/session").status_code == 204
    client.post("/api/auth/logout")
    assert client.get("/api/auth/session").status_code == 401


def test_rate_limit(client):
    for _ in range(5):
        client.post("/api/auth/login", json={"password": "nope"})
    assert client.post("/api/auth/login", json={"password": "test-password"}).status_code == 429


def test_password_change_ends_sessions(authed, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "site_password", "a-new-password")
    assert authed.get("/api/auth/session").status_code == 401
