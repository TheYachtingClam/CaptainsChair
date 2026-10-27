import os

os.environ.setdefault("SESSION_SECRET", "test-secret-with-enough-length")
os.environ.setdefault("SECURE_COOKIES", "false")
os.environ.setdefault("STATIC_DIR", "/nonexistent")

import pytest
from fastapi.testclient import TestClient

from app.auth import login_limiter
from app.db import init_db
from app.main import create_app


@pytest.fixture
def client():
    init_db("sqlite:///:memory:")
    login_limiter.reset()
    app = create_app()
    app.router.lifespan_context = _no_lifespan
    with TestClient(app) as c:
        yield c


def sign_in_as(client, email="nick@example.com", name="Nick", *, admin=False, password="correct horse"):
    """A browser signed in to a new account (requirements/19-technical-architecture.md §5). Pass the test client
    to sign that browser in; use `another_browser(client)` first for a second player."""
    from app import users
    from app.db import open_session

    with open_session() as db:
        users.create_user(db, email, name, password, is_admin=admin)
        db.commit()
    assert client.post("/api/auth/login", json={"email": email, "password": password}).status_code == 204
    return client


def another_browser(client):
    """A second browser on the same server, with its own cookies."""
    return TestClient(client.app)


@pytest.fixture
def authed(client):
    """A browser signed in to an ordinary account, Nick."""
    return sign_in_as(client)


@pytest.fixture
def admin(client):
    """A browser signed in to an admin account."""
    return sign_in_as(client, "admin@example.com", "Admin", admin=True)


from contextlib import asynccontextmanager


@asynccontextmanager
async def _no_lifespan(_):
    yield
