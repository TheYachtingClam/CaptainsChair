"""User accounts (requirements/19-technical-architecture.md §5): passwords, invitations, password resets and the
emails they send. Routes are in app/routes/auth.py; the admin's in app/routes/admin.py."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import mail
from app.models import Invite, PasswordReset, User

INVITE_DAYS = 7  # REQ-USER-02
RESET_HOURS = 1  # REQ-USER-21
MIN_PASSWORD = 8  # REQ-USER-15
_N, _R, _P = 2**14, 8, 1  # scrypt cost: about 16 MB and a few tens of milliseconds a check


class UserError(ValueError):
    """A request that cannot be done, with a message for the person."""


def now() -> datetime:
    return datetime.now(UTC)


def _aware(when: datetime) -> datetime:
    # SQLite returns naive datetimes; they were stored as UTC.
    return when if when.tzinfo else when.replace(tzinfo=UTC)


# ------------------------------------------------------------------ passwords (REQ-USER-15)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    return f"scrypt${_N}${_R}${_P}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def check_password(password: str, stored: str) -> bool:
    try:
        kind, n, r, p, salt, digest = stored.split("$")
    except ValueError:
        return False
    if kind != "scrypt":
        return False
    candidate = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=int(n), r=int(r), p=int(p),
                               dklen=len(base64.b64decode(digest)))
    return hmac.compare_digest(candidate, base64.b64decode(digest))


# Checked against when the email is unknown, so a wrong email takes as long as a wrong password (REQ-USER-11).
_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def check_new_password(password: str) -> None:
    if len(password) < MIN_PASSWORD:
        raise UserError(f"The password must be at least {MIN_PASSWORD} characters.")


def clean_name(display_name: str) -> str:
    name = " ".join(display_name.split())
    if not 1 <= len(name) <= 40:
        raise UserError("The display name must be 1 to 40 characters.")
    return name


def normal_email(email: str) -> str:
    email = email.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@") or len(email) > 254:
        raise UserError("That is not an email address.")
    return email


def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


# ------------------------------------------------------------------ accounts

def find_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))


def authenticate(db: Session, email: str, password: str) -> User | None:
    """The account for this email and password, if both are right and it is not disabled (REQ-USER-10, -11)."""
    user = find_by_email(db, email)
    if user is None:
        check_password(password, _DUMMY_HASH)
        return None
    if not check_password(password, user.password_hash) or user.disabled:
        return None
    user.last_seen_at = now()
    return user


def create_user(db: Session, email: str, display_name: str, password: str, *, is_admin: bool = False) -> User:
    email = normal_email(email)
    if find_by_email(db, email) is not None:
        raise UserError("There is already an account for that email address.")
    check_new_password(password)
    user = User(email=email, display_name=clean_name(display_name), password_hash=hash_password(password),
                is_admin=is_admin, last_seen_at=now())
    db.add(user)
    db.flush()
    return user


def set_password(user: User, password: str) -> None:
    """A new password ends every session of the user (REQ-USER-14, -21)."""
    check_new_password(password)
    user.password_hash = hash_password(password)
    user.session_version += 1


def change_password(db: Session, user: User, current: str, new: str) -> None:
    if not check_password(current, user.password_hash):
        raise UserError("The current password is not right.")
    set_password(user, new)
    mail.send(user.email, "Your Captain's Chair password was changed",
              f"Hello {user.display_name},\n\nThe password of your Captain's Chair Online account was just changed.\n"
              "If you did not change it, ask the admin to reset it.\n")


# ------------------------------------------------------------------ invitations (REQ-USER-02, -30)

def create_invite(db: Session, email: str, created_by: User | None, *,
                  admin: bool = False) -> tuple[Invite, str, mail.Outcome]:
    """A new invitation, its code (only its hash is stored) and how its email went. An admin invitation makes the new
    account an admin (REQ-USER-04)."""
    email = normal_email(email)
    if find_by_email(db, email) is not None:
        raise UserError("There is already an account for that email address.")
    code = secrets.token_urlsafe(24)
    invite = Invite(email=email, code_hash=_code_hash(code), created_by=created_by.id if created_by else None,
                    expires_at=now() + timedelta(days=INVITE_DAYS), is_admin=admin)
    db.add(invite)
    db.flush()
    who = created_by.display_name if created_by else "The admin"
    role = " as its admin" if admin else ""
    outcome = mail.send(email, f"{who} invited you to Captain's Chair Online",
                        f"Hello,\n\n{who} invited you to play Star Trek: Captain's Chair online{role}.\n\n"
                        f"Create your account here (the link works once, for {INVITE_DAYS} days):\n"
                        f"{invite_link(code)}\n")
    return invite, code, outcome


def invite_link(code: str) -> str:
    return mail.link(f"/signup?code={code}")


def open_invite(db: Session, code: str) -> Invite:
    """The usable invitation for this code (REQ-USER-02)."""
    invite = db.scalar(select(Invite).where(Invite.code_hash == _code_hash(code)))
    if invite is None or invite.used_at is not None or _aware(invite.expires_at) < now():
        raise UserError("This invitation has expired or was already used. Ask the admin for a new one.")
    return invite


def sign_up(db: Session, code: str, display_name: str, password: str) -> User:
    invite = open_invite(db, code)
    user = create_user(db, invite.email, display_name, password, is_admin=invite.is_admin)
    invite.used_at = now()
    invite.user_id = user.id
    return user


# ------------------------------------------------------------------ forgotten passwords (REQ-USER-20 to -22)

def start_reset(db: Session, user: User) -> tuple[str, mail.Outcome]:
    """A one-time reset code for the user, sent by email. Returns the link and how the email went."""
    code = secrets.token_urlsafe(24)
    db.add(PasswordReset(user_id=user.id, code_hash=_code_hash(code), expires_at=now() + timedelta(hours=RESET_HOURS)))
    db.flush()
    url = mail.link(f"/reset?code={code}")
    outcome = mail.send(user.email, "Reset your Captain's Chair password",
                        f"Hello {user.display_name},\n\nUse this link to choose a new password (it works once, for "
                        f"{RESET_HOURS} hour):\n{url}\n\nIf you did not ask for this, you can ignore this email.\n")
    return url, outcome


def forgot(db: Session, email: str) -> None:
    """Send a reset link if the address has an active account; say nothing either way (REQ-USER-20)."""
    user = find_by_email(db, email)
    if user is not None and not user.disabled:
        start_reset(db, user)


def reset(db: Session, code: str, password: str) -> User:
    row = db.scalar(select(PasswordReset).where(PasswordReset.code_hash == _code_hash(code)))
    if row is None or row.used_at is not None or _aware(row.expires_at) < now():
        raise UserError("This link has expired or was already used. Ask for a new one.")
    user = db.get(User, row.user_id)
    if user is None or user.disabled:
        raise UserError("This link has expired or was already used. Ask for a new one.")
    set_password(user, password)
    row.used_at = now()
    user.last_seen_at = now()
    return user


def open_invites(db: Session) -> list[Invite]:
    """Invitations not used yet and not expired, newest first (REQ-USER-30)."""
    rows = db.scalars(select(Invite).where(Invite.used_at.is_(None)).order_by(Invite.created_at.desc())).all()
    return [i for i in rows if _aware(i.expires_at) >= now()]


def any_admin(db: Session) -> bool:
    return db.scalar(select(User.id).where(User.is_admin.is_(True), User.disabled.is_(False)).limit(1)) is not None


def public(user: User) -> dict:
    return {"id": user.id, "email": user.email, "display_name": user.display_name, "is_admin": user.is_admin}
