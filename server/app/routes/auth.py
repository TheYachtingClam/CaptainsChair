from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth import (
    check_password,
    clear_session,
    issue_session,
    login_limiter,
    require_session,
)
from app.config import get_settings
from app.schemas import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(body: LoginRequest, request: Request, response: Response) -> None:
    settings = get_settings()
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(ip, settings.login_attempts_per_minute):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts. Try again in a minute.")
    if not check_password(body.password, settings):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")
    issue_session(response, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    clear_session(response)


@router.get("/session", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_session)])
def session() -> None:
    """Lets the client check whether it is signed in."""
