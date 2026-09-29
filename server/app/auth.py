"""Shared-password access control (requirements/19-technical-architecture.md §5)."""

import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Response, WebSocket, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import Settings, get_settings

COOKIE_NAME = "cc_session"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt="cc-session")


def _password_fingerprint(settings: Settings) -> str:
    # Part of every session, so changing the password ends all sessions
    # (REQ-AUTH-05, REQ-AUTH-13).
    return hmac.new(
        settings.session_secret.encode(), settings.site_password.encode(), hashlib.sha256
    ).hexdigest()[:32]


def check_password(candidate: str, settings: Settings) -> bool:
    return hmac.compare_digest(candidate.encode(), settings.site_password.encode())


def issue_session(response: Response, settings: Settings) -> None:
    token = _serializer(settings).dumps({"pw": _password_fingerprint(settings)})
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def session_is_valid(cookie: str | None, settings: Settings) -> bool:
    if not cookie:
        return False
    try:
        data = _serializer(settings).loads(cookie, max_age=settings.session_days * 86400)
    except (BadSignature, SignatureExpired):
        return False
    return isinstance(data, dict) and hmac.compare_digest(
        str(data.get("pw", "")), _password_fingerprint(settings)
    )


def require_session(request: Request) -> None:
    """FastAPI dependency for every protected endpoint (REQ-AUTH-01)."""
    if not session_is_valid(request.cookies.get(COOKIE_NAME), get_settings()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")


def websocket_has_session(websocket: WebSocket) -> bool:
    return session_is_valid(websocket.cookies.get(COOKIE_NAME), get_settings())


class LoginRateLimiter:
    """In-memory, per-IP limit on login attempts (REQ-AUTH-15)."""

    def __init__(self) -> None:
        self._attempts: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, ip: str, limit: int, window: float = 60.0) -> bool:
        now = time.monotonic()
        attempts = self._attempts[ip]
        while attempts and now - attempts[0] > window:
            attempts.popleft()
        if len(attempts) >= limit:
            return False
        attempts.append(now)
        return True

    def reset(self) -> None:
        self._attempts.clear()


login_limiter = LoginRateLimiter()


def new_seat_token() -> str:
    return secrets.token_urlsafe(32)


def hash_seat_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
