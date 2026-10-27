"""Make the first admin (requirements/19-technical-architecture.md REQ-USER-04).

    python -m app.create_admin                   # invite ADMIN_EMAIL as an admin
    python -m app.create_admin someone@example.com

It creates an admin invitation, emails it (or writes it to the log while email is not set up) and prints the link.
Signing up from that link creates an admin account, so no password is ever typed on the server. If the address
already has an account, that account is made admin instead.

On the server: `docker exec captainschair-app-1 python -m app.create_admin` locally, or
`fly ssh console -C "python -m app.create_admin"` on Fly.
"""

from __future__ import annotations

import sys

from app import users
from app.config import get_settings
from app.db import init_db, initialised, open_session


def main(argv: list[str]) -> int:
    email = argv[0] if argv else get_settings().admin_email
    if not email:
        print("Give an email address, or set ADMIN_EMAIL.", file=sys.stderr)
        return 2
    if not initialised():  # a test or the running app may have opened it already
        init_db()
    with open_session() as db:
        existing = users.find_by_email(db, email)
        if existing is not None:
            existing.is_admin = True
            existing.disabled = False
            db.commit()
            print(f"{existing.email} already has an account; it is now an admin.")
            return 0
        try:
            _, code = users.create_invite(db, email, None, admin=True)
        except users.UserError as err:
            print(err, file=sys.stderr)
            return 1
        db.commit()
    print(f"Admin invitation for {users.normal_email(email)} (works once, for {users.INVITE_DAYS} days):")
    print(users.invite_link(code))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
