"""Email (requirements/19-technical-architecture.md REQ-USER-23, -24): plain text over SMTP, for now through a Gmail
account with an app password (smtp.gmail.com, port 587, STARTTLS). Without SMTP settings, as on a developer's
machine and in tests, each email is written to the log instead, and kept in OUTBOX."""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from typing import Literal

from app.config import get_settings

log = logging.getLogger("captains_chair.mail")
OUTBOX: list[dict] = []  # every email written to the log instead of sent; tests read it
SENDER_NAME = "Captain's Chair Online"
TIMEOUT = 20  # seconds

Outcome = Literal["sent", "logged", "failed"]


def configured() -> bool:
    """SMTP needs a host and a password; without either, emails go to the log."""
    settings = get_settings()
    return bool(settings.smtp_host and settings.smtp_password)


def sender() -> str:
    settings = get_settings()
    name, address = parseaddr(settings.mail_from)
    return formataddr((name or SENDER_NAME, address or settings.smtp_user))


def send(to: str, subject: str, body: str) -> Outcome:
    """Send one plain-text email. Returns "sent", "logged" (no SMTP settings) or "failed" (the error is logged; the
    caller carries on, so a mail problem never breaks sign-up or the admin's work)."""
    if not configured():
        OUTBOX.append({"to": to, "subject": subject, "body": body})
        del OUTBOX[:-50]  # keep only the latest
        log.info("Email to %s (not sent: no SMTP settings): %s\n%s", to, subject, body)
        return "logged"
    settings = get_settings()
    message = EmailMessage()
    message["From"] = sender()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        if settings.smtp_port == 465:  # TLS from the start
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=TIMEOUT,
                                  context=ssl.create_default_context()) as smtp:
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
        else:  # 587: plain, then STARTTLS (Gmail)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=TIMEOUT) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as err:
        # Never log the message body: it holds the link (REQ-OPS-05).
        log.error("Could not send the email %r to %s: %s", subject, to, err)
        return "failed"
    log.info("Sent the email %r to %s", subject, to)
    return "sent"


def link(path: str) -> str:
    """An absolute link to a page of the site, for an email."""
    return get_settings().public_url.rstrip("/") + path
