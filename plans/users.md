# Plan: user accounts

Today the site has no accounts. This plan adds them: each person signs in as themselves, and their games, campaigns and reports belong to that account on any device. Each step ends with something you can test.

## How it works today

| Piece | Now | Problem |
|---|---|---|
| Getting in | One shared site password (`SITE_PASSWORD`), a 30-day signed cookie (REQ-AUTH-01 to -16) | Everyone is the same anonymous visitor. Changing the password signs everyone out |
| Your seat in a game | A secret seat token, kept in that browser's local storage (REQ-SRV-30) | Lost if you clear the browser or switch device; the lobby's "Your games" only knows this browser |
| Your campaign | A secret link token, also in local storage | Same: lose the link, lose the campaign |
| Your name | Typed again for every game | Nothing ties two games to the same person |
| Admin | A second password (`ADMIN_PASSWORD`) | Not tied to a person; anyone with it is the admin |
| Bug reports | Reporter's name as typed for that game | Can't follow up with the person |

## What accounts give

- Sign in once per device with your own email address and password.
- "Your games" and "Your campaigns" come from the server, so they follow you to any device.
- Your display name comes from your account.
- The admin is an account with an admin flag, not a shared password.
- Reports carry the reporter's account.

Out of scope for this plan: social sign-in, friends lists, ratings and statistics, matchmaking. Each can be added later on top of accounts.

## Decisions

Answered on 2026-10-26:

1. **Who can create an account:** only with an **invite** from the admin. The admin makes an invite for an email address; the person gets the invite by email, or the admin copies the link and sends it themselves.
2. **How people sign in:** **email address and password**, with "Forgot password?" emails. This needs an email-sending service (decision 6).
3. **The shared site password:** **retired** once accounts work; signing in to an account becomes the gate.
4. **Existing games and campaigns:** first "claimed automatically"; changed later on 2026-10-26 to **deleted**, because simplicity mattered more than the games in progress. Seat tokens, campaign links, the shared site password and the admin password were all removed at once, and the server drops the old games, seats and campaigns the first time it opens a database that still has seat tokens (`db._drop_games_from_before_accounts`). Bug reports are kept.
5. **The admin:** an **admin flag on accounts**. The first admin is made with a command on the server (`scripts/create_admin.py`, run once through `fly ssh console`); after that the admin can make others admin. `ADMIN_PASSWORD` is retired.

6. **Email service:** **your Gmail account, through an app password**, for now (decided 2026-10-26). The server sends through Gmail's SMTP server with Python's own `smtplib`, so the emails come from your Gmail address and no domain is needed. The settings are `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER` (your Gmail address), `SMTP_PASSWORD` (the app password, as a Fly secret, never in the code) and `MAIL_FROM` (the same address, with a display name such as "Captain's Chair Online"). Gmail allows a few hundred emails a day, far more than invites and resets need. Without these settings (on your Mac, and in tests) the server writes each email to its log instead of sending it, so everything can be tried locally.

   **Later:** a service such as Resend, from a domain you own and verify, needs only new values for the same settings; no code changes.

## Design

### Data

- New table `users`: id, email (unique, stored lower-case), display name, password hash, `is_admin`, `disabled`, created and last-seen times, and a `session_version` that is raised on a password change or reset, ending every session of that user.
- New table `invites`: the email address invited, a random code (only its hash stored), who made it, when it expires (7 days), and when it was used.
- New table `password_resets`: a random code (only its hash stored), the user, when it expires (1 hour) and whether it was used.
- `seats` and `campaigns` have a required `user_id`; `bug_reports` a nullable one (reports from before accounts have none).
- The Bot has no seat row, so nothing changes for it.

### Passwords and sessions

- Passwords are hashed with `hashlib.scrypt` from Python's standard library, with a random salt per user. No new dependency.
- The session cookie keeps today's form (signed, `HttpOnly`, `Secure`, `SameSite=Lax`, 30 days) but carries the user id and their `session_version` instead of a password fingerprint.
- Sign-in attempts stay rate-limited per address (REQ-AUTH-15), and an unknown email and a wrong password give the same message.
- "Forgot password?" always answers "If that address has an account, we sent a link", so it never reveals who has an account. It is rate-limited too.
- Minimum password length 8; no other rules.

### Email

- `app/mail.py` sends plain-text emails through SMTP (Gmail for now, decision 6), or logs them when no SMTP settings are set.
- Three emails: the invite ("Nick invited you to Captain's Chair Online" with the sign-up link), the password reset link, and "your password was changed" as a safety notice.
- Links use a `PUBLIC_URL` setting, for example `https://captains-chair-wild-bush-4325.fly.dev`, so they point at the site.

### Who may act

- A seat belongs to the account that created or joined it. A command, an undo or a report is allowed when the seat's `user_id` is the signed-in user.
- A campaign belongs to its account and opens only for it.
- Admin endpoints check the account's `is_admin` flag.
- The WebSocket finds the seat from the signed-in user.
- Taking over a seat (REQ-ADMIN-06) moves the seat to the admin's account.

## Steps

### Step 1: Requirements (done)

- Rewrite `requirements/19-technical-architecture.md` §5 (access control) for accounts: new REQ-USER rules for sign-up, sign-in, sessions, invites, password reset, the admin flag and claiming. Retire or rewrite REQ-AUTH-01 to -16 and REQ-ADMIN-01 to -06.
- Update §3.5 (endpoints), §4.2 (pages) and §6 (environment variables).

**You check:** the rewritten section reads right before any code changes.

What was done: `requirements/19-technical-architecture.md` §5 is now "Access control: user accounts", with REQ-USER-01 to -43 (accounts and invitations, sessions, forgotten passwords and email, the admin, ownership of games and campaigns). REQ-AUTH-01 to -16 and REQ-ADMIN-01, -02 are retired; REQ-ADMIN-03 to -06 stay, with the take-over now moving the seat to the admin's account. Also updated: the endpoints (§3.5), seat tokens (REQ-SRV-30, -40, -50), the pages (§4.2), the environment variables and logging rules (§6), the bug report recreate rule (REQ-BUG-07), REQ-CAMP-54 in the solo requirements, and the index.

### Step 2: Accounts and sign-in on the server (done)

- The `users` and `invites` tables, password hashing, and the new session cookie.
- Endpoints: sign up with an invite (the email is fixed by the invite), sign in, sign out, "who am I", change display name, change password, "forgot password" and "reset password" with a code.
- Emails are written to the log at this step (decision 6 comes in Step 4).
- While this step and the next are in progress, the shared password still works, so nothing breaks.

**You test:** server tests for each endpoint, including a wrong password, a used or expired invite, a used or expired reset code, the rate limits, and a password change signing out other devices.

What was done: tables `users`, `invites` and `password_resets` (`app/models.py`); `app/users.py` (scrypt password hashing, invitations, sign-up, password change and reset); `app/mail.py`, which for now writes every email to the log and keeps the latest in `mail.OUTBOX`; the account session cookie in `app/auth.py` (user id and session version, checked against the database on every request), alongside the shared-password session; endpoints in `app/routes/auth.py`: `POST /login` (with an email), `GET`/`PATCH /me`, `POST /password`, `GET /invite/{code}`, `POST /signup`, `POST /forgot`, `POST /reset`. Tests: `tests/test_users.py`, 15 tests. There is no way to make an invitation outside the code yet: that is the admin's, in Step 3.

### Step 3: The admin as an account (done)

- `scripts/create_admin.py` makes the first admin.
- Admin endpoints check the flag. New ones: list users, invite an email address (and see or copy the link), list and cancel open invites, send a password reset, disable or re-enable a user, make or unmake an admin.
- The Admin page gets a Users section.

**You test:** create the first admin locally, invite a second account, reset its password, disable it.

What was done: the first admin comes from an **admin invitation** (`python -m app.create_admin`, address from `ADMIN_EMAIL`, set to nmayne@gmail.com in the local `.env`), so no password is typed on the server. Admin endpoints accept an admin account (and, until Step 8, the admin password). New admin endpoints for accounts and invitations, and the Admin page's Invitations and Accounts sections. Pulled forward from Step 7 so the invitation can be used: the sign-in page takes an email and password (with "Forgot password?" and a switch back to the shared password), and the sign-up and reset-password pages that email links open. The top bar shows the account's name and, for an admin, a link to the Admin page. Tests: `tests/test_users.py`, 17 tests.

### Step 4: Sending email (done)

- `app/mail.py` with SMTP settings (decision 6), and the three emails.
- You: turn on 2-Step Verification on the Google account if it isn't already, then create an app password for the site.
- On Fly: set the SMTP secrets and `PUBLIC_URL`. You set the app password yourself with `fly secrets set`, so it never passes through this chat or the code.

**You test:** invite yourself at a second address and receive the email; use "Forgot password?" and receive the link.

What was done: `app/mail.py` sends over SMTP with Python's `smtplib` (STARTTLS on 587, TLS on 465) when `SMTP_HOST` and `SMTP_PASSWORD` are set, and otherwise writes to the log as before. A failed email is logged (without its text, which holds the link) and never fails the request; invitations and resets report "sent", "logged" or "failed", and the Admin page says what to do. The local `.env` has the Gmail settings for nmayne@gmail.com except the app password, which you add yourself; `.env.example` documents them. Tests: a fake SMTP server checks the Gmail conversation, the sender and the link, and that a failure is handled.

### Step 5: Seats and campaigns belong to accounts (done)

- Creating or joining a game, starting a campaign and sending a report record the user.
- New endpoints: "my games" and "my campaigns".
- Commands, undo, reports and the WebSocket accept the signed-in owner of a seat; seat tokens remain the fallback.
- Join rules: you can't take both seats of a two-player game with one account.

**You test:** play a game from one browser, open the site in another browser signed in as the same user, and carry on.

What was done: `seats`, `campaigns` and `bug_reports` have a `user_id`. Creating or joining a game, starting a campaign or an assignment, and sending a report record the signed-in account, and a seat or campaign takes the account's display name. A request may act in the account's own seat (`seat_for` in `app/routes/games.py`); a seat token still works for a seat no account holds, but not for one an account holds. One account cannot take both seats of a game. Campaigns open for their owner without the link. New endpoints `GET /api/me/games` and `GET /api/me/campaigns` (`app/routes/me.py`). The game socket finds the account's seat. Taking over a seat, or recreating a reported game, gives that seat to the admin's account. Client: the lobby's "Your games" and Five-Year Missions include the account's, the game page connects through the account, and the seat and campaign forms use the account's name. Tests: `tests/test_users.py`, 27 tests.

### Step 6: Claiming existing games and campaigns (dropped)

Dropped with decision 4 as changed: the old games are deleted instead, and with them the shared site password, the admin password, seat tokens and campaign links (done the same day). The server is account-only: every endpoint takes the account from the session (`auth.viewer_id`), `/api/admin/login` and `/logout` are gone, and the client keeps nothing in local storage for seats or campaigns. A recreated bug report gives every seat to the admin, who acts in the seat whose decision is pending. API tests sign in with `sign_in_as` and `another_browser` (`tests/conftest.py`).

### Step 7: The client

- Sign-in page, sign-up page (from an invite link), "Forgot password?" and reset-password pages.
- An account menu: display name, change password, sign out.
- The lobby's "Your games" and the campaign list come from the server.
- The seat form stops asking for a name.
- The Admin page's Users section.

**You test:** the whole flow in the browser: invite, sign up, play, sign out, sign in elsewhere.

### Step 8: Switch over and retire the old pieces

- The code side is done (Step 6). What is left is on Fly:
- Deploy. **The first start deletes every game and campaign on Fly** (decision 4).
- Set the secrets `PUBLIC_URL`, `ADMIN_EMAIL`, `SMTP_HOST`, `SMTP_USER`, `MAIL_FROM`; you set `SMTP_PASSWORD` yourself. Remove `SITE_PASSWORD` and `ADMIN_PASSWORD`.
- Create the first admin on Fly with `fly ssh console -C "python -m app.create_admin"`, then invite the players.

**You test:** on Fly, sign in as the admin, invite a player, and play a game together.

## Risks and notes

- **Signing everyone out once.** The switch in Step 8 ends every current session, and games in progress are deleted (decision 4); players sign in again with their new accounts.
- **Email delivery.** Emails come from your own Gmail address, so they should arrive reliably. If one goes astray, the admin can always copy an invite or reset link from the Admin page and send it another way.
- **Your address is the sender.** Players see your Gmail address on invites and resets, and replies come to you. A spare Gmail account for the site avoids that.
- **Backups.** Accounts make the database more valuable. Fly snapshots the volume daily; check the retention, and consider a periodic copy of the SQLite file somewhere else.
- **Privacy.** Only the admin sees the user list and email addresses. Opponents see only display names.
