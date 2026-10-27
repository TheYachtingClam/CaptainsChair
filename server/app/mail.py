"""Email (requirements/19-technical-architecture.md REQ-USER-23, -24): plain text over SMTP, or written to the log
when no SMTP host is set, as on a developer's machine. Sending over SMTP comes in plans/users.md Step 4."""

from __future__ import annotations

import logging

from app.config import get_settings

log = logging.getLogger("captains_chair.mail")
OUTBOX: list[dict] = []  # every email "sent" while no SMTP host is set; tests read it


def send(to: str, subject: str, body: str) -> None:
    settings = get_settings()
    message = {"to": to, "subject": subject, "body": body}
    if not settings.smtp_host:
        OUTBOX.append(message)
        del OUTBOX[:-50]  # keep only the latest
        log.info("Email to %s (not sent: no SMTP_HOST): %s\n%s", to, subject, body)
        return
    raise NotImplementedError("Sending over SMTP comes in plans/users.md Step 4")


def link(path: str) -> str:
    """An absolute link to a page of the site, for an email."""
    return get_settings().public_url.rstrip("/") + path
