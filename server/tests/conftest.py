import os

os.environ.setdefault("SITE_PASSWORD", "test-password")
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


@pytest.fixture
def authed(client):
    assert client.post("/api/auth/login", json={"password": "test-password"}).status_code == 204
    return client


from contextlib import asynccontextmanager


@asynccontextmanager
async def _no_lifespan(_):
    yield
