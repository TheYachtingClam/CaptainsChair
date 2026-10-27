"""Access control (requirements/19-technical-architecture.md §5): every request is made by a signed-in account. The
session is a signed cookie holding the user's id and their session version (REQ-USER-13); a password change, a
reset or disabling the account ends it."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Response, WebSocket, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import Settings, get_settings

COOKIE_NAME = "cc_session"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt="cc-session")


def issue_user_session(response: Response, settings: Settings, user) -> None:
    """Sign a user in on this browser for 30 days (REQ-USER-10, -13)."""
    token = _serializer(settings).dumps({"uid": user.id, "v": user.session_version})
    response.set_cookie(COOKIE_NAME, token, max_age=settings.session_days * 86400, httponly=True,
                        secure=settings.secure_cookies, samesite="lax", path="/")


def clear_session(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def _session_data(cookie: str | None, settings: Settings) -> dict | None:
    if not cookie:
        return None
    try:
        data = _serializer(settings).loads(cookie, max_age=settings.session_days * 86400)
    except (BadSignature, SignatureExpired):
        return None
    return data if isinstance(data, dict) and "uid" in data else None


def session_user(cookies, db):
    """The signed-in account, or None: no cookie, a bad one, a disabled account, or a password changed since
    (REQ-USER-11, -14)."""
    from app.models import User

    data = _session_data(cookies.get(COOKIE_NAME), get_settings())
    if data is None:
        return None
    user = db.get(User, data["uid"])
    if user is None or user.disabled or user.session_version != data.get("v"):
        return None
    return user


def _signed_in(cookies):
    from app.db import open_session

    with open_session() as db:
        user = session_user(cookies, db)
        return (user.id, user.is_admin) if user is not None else None


def require_session(request: Request) -> None:
    """FastAPI dependency for every protected endpoint (REQ-USER-03)."""
    if _signed_in(request.cookies) is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")


def viewer_id(request: Request) -> str:
    """FastAPI dependency: the signed-in account's id (REQ-USER-03)."""
    signed_in = _signed_in(request.cookies)
    if signed_in is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    return signed_in[0]


def require_admin(request: Request) -> None:
    """FastAPI dependency for admin endpoints: a signed-in account with the admin flag (REQ-USER-32)."""
    signed_in = _signed_in(request.cookies)
    if signed_in is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    if not signed_in[1]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")


def websocket_user(websocket: WebSocket) -> str | None:
    """The account a WebSocket connection comes from (REQ-SRV-40)."""
    signed_in = _signed_in(websocket.cookies)
    return signed_in[0] if signed_in is not None else None


class LoginRateLimiter:
    """In-memory, per-IP limit on sign-in and similar attempts (REQ-USER-12, -20)."""

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
