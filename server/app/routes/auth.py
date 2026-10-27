"""Signing in and accounts (requirements/19-technical-architecture.md §5.2, §5.3)."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import users
from app.auth import clear_session, issue_user_session, login_limiter, require_session, session_user
from app.config import get_settings
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _limit(request: Request, what: str) -> None:
    settings = get_settings()
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(f"{what}:{ip}", settings.login_attempts_per_minute):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts. Try again in a minute.")


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> None:
    """Sign in with an email and password (REQ-USER-10 to -12)."""
    settings = get_settings()
    _limit(request, "login")
    user = users.authenticate(db, body.email, body.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    db.commit()
    issue_user_session(response, settings, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    clear_session(response)


@router.get("/session", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_session)])
def session() -> None:
    """Lets the client check whether it is signed in."""


def _me(request: Request, db: Session):
    user = session_user(request.cookies, db)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to your account")
    return user


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)) -> dict:
    return users.public(_me(request, db))


class ProfileChange(BaseModel):
    display_name: str = Field(max_length=200)


@router.patch("/me")
def change_profile(body: ProfileChange, request: Request, db: Session = Depends(get_db)) -> dict:
    user = _me(request, db)
    try:
        user.display_name = users.clean_name(body.display_name)
    except users.UserError as err:
        raise HTTPException(422, str(err)) from err
    db.commit()
    return users.public(user)


class PasswordChange(BaseModel):
    current: str
    new: str = Field(max_length=200)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(body: PasswordChange, request: Request, response: Response, db: Session = Depends(get_db)) -> None:
    """REQ-USER-14: ends the user's other sessions, renews this one, and sends a notice."""
    _limit(request, "password")
    user = _me(request, db)
    try:
        users.change_password(db, user, body.current, body.new)
    except users.UserError as err:
        raise HTTPException(422, str(err)) from err
    db.commit()
    issue_user_session(response, get_settings(), user)


@router.get("/invite/{code}")
def invite(code: str, db: Session = Depends(get_db)) -> dict:
    """The email address an invitation is for, for the sign-up page (REQ-USER-02)."""
    try:
        return {"email": users.open_invite(db, code).email}
    except users.UserError as err:
        raise HTTPException(404, str(err)) from err


class SignUp(BaseModel):
    code: str
    display_name: str = Field(max_length=200)
    password: str = Field(max_length=200)


@router.post("/signup")
def sign_up(body: SignUp, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    """Create an account from an invitation, and sign in (REQ-USER-02)."""
    _limit(request, "signup")
    try:
        user = users.sign_up(db, body.code, body.display_name, body.password)
    except users.UserError as err:
        raise HTTPException(422, str(err)) from err
    db.commit()
    issue_user_session(response, get_settings(), user)
    return users.public(user)


class Forgot(BaseModel):
    email: str = Field(max_length=254)


@router.post("/forgot", status_code=status.HTTP_202_ACCEPTED)
def forgot(body: Forgot, request: Request, db: Session = Depends(get_db)) -> dict:
    """Always the same answer, whether or not the address has an account (REQ-USER-20)."""
    _limit(request, "forgot")
    users.forgot(db, body.email)
    db.commit()
    return {"detail": "If that address has an account, we have sent a link to reset the password."}


class Reset(BaseModel):
    code: str
    password: str = Field(max_length=200)


@router.post("/reset")
def reset(body: Reset, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    """Set a new password with a reset code; ends every session of the user and signs in here (REQ-USER-21)."""
    _limit(request, "reset")
    try:
        user = users.reset(db, body.code, body.password)
    except users.UserError as err:
        raise HTTPException(422, str(err)) from err
    db.commit()
    issue_user_session(response, get_settings(), user)
    return users.public(user)
