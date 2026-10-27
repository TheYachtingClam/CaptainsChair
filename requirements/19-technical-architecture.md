# 19 – Technical Architecture: Python API Server, React Client, Password Access

This document covers how the online game is built. It does not change any game rules. The game rules are in files 01–18.

## 1. Overview

- **REQ-TECH-01** The system has two parts:
  - an **API server** written in Python, which owns all game state and enforces every rule;
  - a **web client** written in React, which shows the game and sends player choices.
- **REQ-TECH-02** The server is the only authority. The client never decides whether a move is legal, and never receives hidden information (see [11-logging-and-hidden-information.md](11-logging-and-hidden-information.md)).
- **REQ-TECH-03** Access to the whole site needs a personal account, which can only be created by invitation (see §5).

```
Browser (React)  ──HTTPS / REST──►  Python API server  ──►  Database
                 ◄──WebSocket────   (rules engine)
```

## 2. Assumptions

These are defaults. Change them here if you decide otherwise.

- The expected audience is a small private group: friends playing two-player games, plus solo games against the Bot and Cadet Training.
- One server instance is enough; there is no need for horizontal scaling.
- Each player has a personal account, created from an invitation. Their display name comes from the account.
- The site runs behind HTTPS, provided by a reverse proxy or the hosting platform.

## 3. API server (Python)

### 3.1 Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 or later |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Data validation and API schemas | Pydantic v2 |
| Real-time updates | WebSockets, built into FastAPI |
| Database | SQLite through SQLAlchemy 2. The code must allow switching to PostgreSQL by changing configuration only |
| Tests | pytest |
| Dependency management | `pyproject.toml`, with a lock file |

### 3.2 Code structure

- **REQ-SRV-01** The rules engine is a separate Python package with **no** web or database code. It takes a game state and a player command, and returns a new state plus a list of events. This keeps it fully testable.
- **REQ-SRV-02** Suggested layout:

```
server/
  app/            FastAPI app, routes, WebSocket handlers, auth
  engine/         rules engine: state, commands, keywords, turn steps
  content/        card, board and Stardate data files (JSON or YAML)
  persistence/    database models and storage
  tests/          engine tests, API tests, acceptance scenarios
```

- **REQ-SRV-03** Card data lives in data files under `content/`, following the schema in [12-component-anatomy.md](12-component-anatomy.md). Card effects are implemented as engine code, one function per operation, using only the actions each function declares. The rules and the action list are in [CLAUDE.md](../CLAUDE.md).
- **REQ-SRV-04** Each acceptance scenario in [18-acceptance-scenarios.md](18-acceptance-scenarios.md) must have an automated engine test.
- **REQ-SRV-05 Images.** Raw scans of cards, crew boards and command cards live in `resources/scans/` and are never part of the Docker image. `scripts/process_scans.py` turns them into WebP files named by id in `server/content/images/`, in the same folders as the scans. Cards are sized to exact card proportions; boards and command cards keep their own proportions. A manifest records each image's kind, size and content version. The server serves them only to signed-in users, at `/api/content/images/{id}?v={version}`, with a private one-year cache for the current version. Game views include an image URL only for cards the viewing player may see; facedown cards use a card-back image.

### 3.3 Game state and commands

- **REQ-SRV-10** The full game state is one serialisable object: all zones, tokens, tracks, Stardates, the current turn step and any pending decision.
- **REQ-SRV-11** Every player input is a **command**, for example play a card, choose an operation, pick a target, answer a prompt or end the step.
- **REQ-SRV-12** When the engine needs a choice, the state holds a **pending decision**. It records which player must decide, what the legal options are, and whether the decision is optional. This covers Reactions on the opponent's turn, "may" effects, Wildcard choices and forced choices.
- **REQ-SRV-13** The server rejects any command that is not legal in the current state. It returns a clear error message and leaves the state unchanged.
- **REQ-SRV-14** The server stores every accepted command in order. Replaying the commands from the starting state, with the same random seed, must reproduce the game exactly. This supports debugging, reconnection and saved games.
- **REQ-SRV-15** Shuffles use a random generator seeded per game on the server. The seed is never sent to clients.
- **REQ-SRV-16** Undo is part of the first version. Every option in a pending decision says whether it can be undone, so the client can warn the player first. Details are in [20-undo.md](20-undo.md).
- **REQ-SRV-17** The Bot ([22-solo-mode.md](22-solo-mode.md)) runs inside the server, as part of the rules engine's turn loop: its turn needs no stored commands, so a game is still rebuilt from the seed and the human's commands alone. Its choices use only what the Bot rules allow.
- **REQ-SRV-19** A game starts as soon as every seat is filled: the server picks a random seed, runs setup, and the first decision goes to the Starting Player. A solo game against the Bot starts with one seat, with the Bot as the second player run by the engine itself (plans/solo-mode.md, design decision 1); Cadet Training starts with one seat and runs the virtual-opponent rules of [16-solo-and-cadet-training.md](16-solo-and-cadet-training.md).
- **REQ-SRV-18** Game creation accepts the box (REQ-CORE-10), the expansions to include, whether to include promo cards (REQ-CS-20), and for solo games the Bot's Crew, difficulty and optional Ticking Clock challenge.
- **REQ-SRV-52** The server stores with every accepted command the weekday on which it was received, in the server's time zone. The engine reads the weekday only from there, never from the clock, so a replay gives the same result (REQ-CORE-53). Developer commands and undone commands follow the same rule.

### 3.4 Hidden information

- **REQ-SRV-20** Before sending state to a client, the server builds a **view** for that player. The view removes everything that player may not see:
  - the opponent's hand, sent as a card count only;
  - the order and contents of every facedown deck, sent as counts only;
  - cards a player looked at privately, such as during a scan, visible only to that player and only while relevant.
- **REQ-SRV-21** Public zones are sent in full. This includes both Captain's Logs (see [11-logging-and-hidden-information.md](11-logging-and-hidden-information.md) §3).
- **REQ-SRV-22** Tests must check that no view contains hidden information.

### 3.5 REST endpoints

All endpoints except login and health require a valid session (see §5).

| Method and path | Purpose |
|---|---|
| `POST /api/auth/login` | Check an email address and password and start a session (REQ-USER-10) |
| `POST /api/auth/logout` | End the session |
| `GET /api/auth/me` | The signed-in user: id, email, display name, admin flag |
| `POST /api/auth/signup` | Create an account from an invitation code (REQ-USER-02) |
| `PATCH /api/auth/me` | Change the display name |
| `POST /api/auth/password` | Change the password, given the current one (REQ-USER-14) |
| `POST /api/auth/forgot` | Email a password-reset link; always answers the same (REQ-USER-20) |
| `POST /api/auth/reset` | Set a new password with a reset code (REQ-USER-21) |
| `GET /api/me/games`, `GET /api/me/campaigns` | The signed-in user's games and campaigns (REQ-USER-40) |
| `GET /api/admin/users`, `PATCH /api/admin/users/{id}` | Admin: list users; disable, enable, make or unmake admin (REQ-USER-31) |
| `POST /api/admin/invites`, `GET /api/admin/invites`, `DELETE /api/admin/invites/{id}` | Admin: invite an email address, list open invitations, cancel one (REQ-USER-30) |
| `POST /api/admin/users/{id}/reset` | Admin: send a password-reset email and show the link (REQ-USER-22) |
| `GET /api/health` | Liveness check for hosting; no auth |
| `GET /api/content/decks` | List Crew decks with complexity and summary text |
| `GET /api/content/cards` | Card list for reference screens |
| `POST /api/games` | Create a game: mode, chosen deck, board side. The seat takes the account's display name |
| `GET /api/games` | List open and in-progress games |
| `POST /api/games/{id}/join` | Join as the second player |
| `DELETE /api/games/{id}` | Delete the game for everyone. Only a player seated in that game (REQ-USER-42). Connected players get a `game_deleted` message and return to the lobby |
| `GET /api/admin/games` | Admin: every game, in any state, with its players |
| `DELETE /api/admin/games/{id}` | Admin: delete any game; connected players get `game_deleted` |
| `POST /api/admin/games/{id}/seats/{index}/take` | Admin: take over a seat; it moves to the admin's account (REQ-ADMIN-06) |
| `GET /api/admin/campaigns`, `DELETE /api/admin/campaigns/{id}` | Admin: list or delete Five-Year Mission campaigns |
| `GET /api/games/{id}` | Current view of the game for this player |
| `POST /api/games/{id}/commands` | Submit a command |
| `GET /api/games/{id}/log` | Public action log |
| `POST /api/campaigns` | Start a Five-Year Mission campaign |
| `GET /api/campaigns/{id}` | Campaign log, rank, Reinforcement pile and Boosts |
| `POST /api/campaigns/{id}/assignments` | Start the next assignment against a chosen or random Bot |
| `POST /api/campaigns/{id}/upgrade` | Choose the upgrade after an assignment |
| `POST /api/games/{id}/undo` | Undo the last command. See [20-undo.md](20-undo.md) |
| `POST /api/games/{id}/bugs` | A seated player reports a bug; the report keeps the game's setup, seed and commands (§5.5) |
| `GET /api/admin/bugs`, `GET /api/admin/bugs/{id}`, `GET /api/admin/bugs/{id}/download` | Admin: list bug reports; one report with its bundle; the report as a JSON file |
| `POST /api/admin/bugs/{id}/status`, `DELETE /api/admin/bugs/{id}` | Admin: mark a report resolved or open; delete it |
| `POST /api/admin/bugs/{id}/recreate` | Admin: make a playable copy of the reported game, as reported or some moves earlier |

- **REQ-SRV-30** A seat belongs to the account that created or joined the game (REQ-USER-42). There are no seat tokens: a request acts in the seat of the signed-in account.

### 3.6 WebSocket

- **REQ-SRV-40** Each client opens one WebSocket per game at `/api/games/{id}/ws`, authenticated with the session. The server finds the seat from the signed-in user; an account without a seat in the game is refused.
- **REQ-SRV-41** After any accepted command, the server pushes each connected player their own updated view, plus the new events for animation and the action log.
- **REQ-SRV-42** Commands may be sent over the WebSocket or over REST. The server processes one command per game at a time, in arrival order.
- **REQ-SRV-43** When a player reconnects, the server sends the full current view.
- **REQ-SRV-44** The server tells each player when their opponent connects or disconnects.

### 3.7 Persistence

- **REQ-SRV-50** Accounts, game records, command history and seat ownership are stored in the database. A server restart must not lose any game.
- **REQ-SRV-51** Finished games keep their final score breakdown.

## 4. Web client (React)

### 4.1 Stack

| Concern | Choice |
|---|---|
| Framework | React 18 or later |
| Language | TypeScript |
| Build tool | Vite |
| Server data | TanStack Query for REST, plus one WebSocket hook per game |
| Styling | CSS modules or Tailwind; the choice is left to the team |
| Tests | Vitest and React Testing Library, plus Playwright for end-to-end tests |

- **REQ-CLI-01** TypeScript types for API messages are generated from the server's OpenAPI schema, so client and server stay in step.
- **REQ-CLI-02** The client holds no game logic. It displays the view and the pending decision the server sends. To show legal options, it uses the option list from the pending decision.

### 4.2 Pages

| Page | Contents |
|---|---|
| Sign-in page | Email, password, and a "Forgot password?" link. Shown whenever there is no valid session |
| Sign-up page | Reached from an invitation link: the invited email (fixed), display name and password |
| Forgot and reset password pages | Ask for the email address; then, from the emailed link, set a new password |
| Account | Reached from the account name in the top bar, beside Sign out: the email address (shown, not changed), the display name, and changing the password (current one, new one twice). A new display name applies to games created or joined afterwards |
| Lobby | Create game, list of open games to join, list of the player's own in-progress games. Each of the player's own games has a Delete button that asks for confirmation, because deleting cannot be undone |
| New game | Choose mode (two-player, solo against the Bot, Cadet Training), box (Core Box, To Boldly Go or both), expansions, promo cards, Crew deck (with complexity and summary) and board side; the display name comes from the account. Solo adds Bot Crew, difficulty and Ticking Clock |
| Campaign | Five-Year Mission log, rank, upgrades, challenges and the next assignment |
| Game table | The main play screen (§4.3), with a Report a bug button (§5.5) |
| Score screen | Final score breakdown per player, following [13-final-scoring.md](13-final-scoring.md) |
| Reference | Keyword glossary, icon reference and common card list |

### 4.3 Game table

- **REQ-CLI-10** Show the central area: Market decks and faceup cards, Junk pile, Incident deck, Encounter deck, Stardate pile with its Glory, Location deck and the three Neutral Zone slots with token counts per player.
- **REQ-CLI-11** Show both player areas: Location Area with Duty Officer slots, Fleet Area, Staging Area, Draw deck count, Discard pile, Reserve deck count, Development pile, Captain's Log, Crew board with tracks and missions, resource pool and Action tokens.
- **REQ-CLI-12** Clicking any public pile opens a viewer: Discard pile, Junk pile, Development pile and Captain's Log. Cards beamed to a card are always visible: each is drawn as a small card tucked under its host, in either player's area. Hovering one shows its large preview, and clicking one selects it like any other card, or answers a question it is an option for (for example which beamed card to recall).
- **REQ-CLI-13** Clicking a card shows a large version with its full rules text. Keywords in the text link to the reference.
- **REQ-CLI-14** When the player has a pending decision, the table highlights the legal choices and shows a prompt explaining what to choose. Optional decisions have a clear skip button.
- **REQ-CLI-15** When a Reaction becomes available on the opponent's turn, the player gets a clear prompt with a way to use it or decline.
- **REQ-CLI-16** An action log lists every public event in plain words.
- **REQ-CLI-17** A turn indicator shows whose turn it is, the current step, and whether a Resolution has been triggered with how many turns remain.
- **REQ-CLI-18** The table works on a laptop screen, a tablet, and a phone held upright, from 375 pixels wide (§4.4). Turning a phone sideways must not break the table, but it gets no layout of its own.
- **REQ-CLI-19** In a two-player game each player can step through the other player's latest turn, as with a Bot's turn (REQ-SOLO-56): the same panel with Previous, Next, Auto-play, Skip to end and Done, showing each log line of that turn and, where a line is about a card (played, used, deployed, gained, logged, taken control of and so on), that card. Only lines the viewer may see are shown. It follows the other player's turn live as it happens. Unlike a Bot's turn, the player's own turn does not wait for Done.

### 4.4 Phones

A phone is a screen narrower than 700 pixels, or one without a mouse (no hover). The plan is [plans/phone.md](../plans/phone.md).

- **REQ-CLI-30** Nothing needs hover. Anything shown on hover with a mouse, such as the enlarged card, the cards beamed to it, and the name of a Ship or Away Team token, can be reached by touch too.
- **REQ-CLI-31** **Inspecting a card.** Pressing and holding any visible card, including the opponent's, the Market's and a Location's, opens a full-screen viewer: the card, the cards beamed to it, and its tokens. A tap anywhere closes it. A short tap keeps its usual meaning: select the card, or answer a question with it. The first time a player opens a game on a phone, a one-line hint says that pressing and holding shows a card.
- **REQ-CLI-32** **One area at a time.** On a phone, the table shows one area at a time, chosen from a bar at the bottom of the screen: **You** (the Neutral Zone, for planning your turn, then your mat and hand), **Centre** (Market, Junk, decks, Stardate, Neutral Zone), **Opponent** (their mat, or the Bot's) and **System** (Exit game, Report a bug and Suggest a feature, the game's details, the Players list, the connection and its events, then the log; on a phone these are shown only there). A tab shows a mark when something changed there since it was last shown. When a question asks for cards in one area, that area is shown.
- **REQ-CLI-33** **Your hand** is shown under your mat, outside its border, fanned as on a laptop, with cards large enough to tap; the cards overlap more as the hand grows, so it always fits the width of the screen.
- **REQ-CLI-34** **Questions and panels.** On a phone the question box, the card's action panel and the turn playback panel (REQ-SOLO-56, REQ-CLI-19) open as one sheet from the bottom of the screen. It can be collapsed to a single line that still says what is asked, so the table behind it can be seen, and expanded again with a tap.
- **REQ-CLI-35** Buttons and other tap targets are at least 44 by 44 pixels on a phone. The page never scrolls sideways, except a row of cards that is meant to.
- **REQ-CLI-36** The lobby, new game, campaign, account, sign-in and Admin pages work at 375 pixels wide.
- **REQ-CLI-37** On a phone the Neutral Zone is compact: its three Locations side by side, small, each with every player's tokens as icons and a mark where a player has secured it.
- **REQ-CLI-38** On a phone the **Centre** shows, from the top: the Encounter, Incident and Location decks (and the Reward pile when it has cards) in one row, each a small card back with its name in its colour and its count; the Market four across, each suit's deck drawn the same way above its face-up card, as on the table; then the Junk and the Stardate side by side; then the Neutral Zone.

## 5. Access control: user accounts

Every player has their own account, created only by invitation from the admin, and signs in with an email address and a password. Their games, campaigns and reports belong to the account, on any device. This replaced the shared site password (REQ-AUTH-01 to -16, retired), the separate admin password (REQ-ADMIN-01 and -02, retired), and the seat tokens and campaign links that identified players before. Games and campaigns from before accounts were deleted when accounts arrived (decision of 2026-10-26); the server drops them once, the first time it opens a database that still has seat tokens. Bug reports were kept. The plan is [plans/users.md](../plans/users.md).

### 5.1 Accounts and invitations

- **REQ-USER-01** An account has an email address (unique, compared without regard to case), a display name (1 to 40 characters, shown to other players), a password, an admin flag, and a disabled flag.
- **REQ-USER-02** An account can only be created from an **invitation**. The admin invites an email address (REQ-USER-30); the invitation link lets that person choose a display name and password. The email address is the invited one and cannot be changed during sign-up. An invitation can be used once and expires after 7 days.
- **REQ-USER-03** There is no sign-up without an invitation. Every page and API endpoint, except sign-in, sign-up from an invitation, forgot and reset password, and health, needs a signed-in account.
- **REQ-USER-04** The first admin is made on the server with `python -m app.create_admin [email]` (the address defaults to the `ADMIN_EMAIL` setting). It creates an **admin invitation**, emails it and prints the link; signing up from it creates an admin account, so no password is typed on the server. If the address already has an account, that account is made admin instead. After that, an admin can make other accounts admin, or invite someone as an admin.

### 5.2 Signing in and sessions

- **REQ-USER-10** Signing in takes the email address and password. A correct pair creates a session that lasts **30 days** on that browser, until the user signs out.
- **REQ-USER-11** A wrong email address and a wrong password give the same message, "Incorrect email or password", so nobody can find out which addresses have accounts. A disabled account cannot sign in, and its sessions end.
- **REQ-USER-12** Sign-in attempts are rate-limited per IP address, for example 5 a minute.
- **REQ-USER-13** The session is a signed cookie (`HttpOnly`, `Secure`, `SameSite=Lax`), signed with `SESSION_SECRET`. It holds the user's id and their session version. The WebSocket checks the same cookie before accepting.
- **REQ-USER-14** Changing the password needs the current one. It raises the session version, which ends every other session of that user; the current one is renewed. A "your password was changed" email is sent.
- **REQ-USER-15** Passwords are at least 8 characters. They are stored only as a salted `scrypt` hash, and compared in constant time.
- **REQ-USER-16** Signing out ends the session on that browser only.

### 5.3 Forgotten passwords and email

- **REQ-USER-20** "Forgot password?" asks for an email address and always answers "If that address has an account, we have sent a link", whether or not it does. If it does, the user gets an email with a reset link. Requests are rate-limited per IP address.
- **REQ-USER-21** A reset link can be used once and expires after 1 hour. Setting a new password with it raises the session version, ending every session of that user, and signs them in.
- **REQ-USER-22** The admin can also send a user a reset email from the Admin page, and sees the link, to pass on another way if the email does not arrive.
- **REQ-USER-23** Emails are plain text, sent over SMTP with the settings in §6 (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM`), from a Gmail account with an app password for now (`smtp.gmail.com`, port 587 with STARTTLS; port 465 uses TLS from the start). The sender is `MAIL_FROM`, or "Captain's Chair Online" at `SMTP_USER` when it is blank. Without `SMTP_HOST` and `SMTP_PASSWORD`, as on a developer's machine, each email is written to the server log instead. Links in emails start with `PUBLIC_URL`. An email that cannot be sent never fails the request: the error is logged without the email's text, and the Admin page says so and shows the link to pass on.
- **REQ-USER-24** There are three emails: the invitation, the password-reset link, and the notice that a password was changed.

### 5.4 The admin

The admin is any account with the admin flag. They can manage accounts and clean up games and campaigns that their players cannot, for example a game waiting for an opponent who never came.

- **REQ-USER-30** The Admin page invites an email address: it sends the invitation email and shows the link, to pass on another way if the email does not arrive. It lists open invitations and can cancel one. Inviting an address that already has an account is refused.
- **REQ-USER-31** The Admin page lists every account with its email, display name, admin flag, disabled flag, creation date and last sign-in. It can disable or re-enable an account and make an account admin or not. An admin cannot remove their own admin flag or disable themselves, so there is always one admin.
- **REQ-USER-32** Admin pages and endpoints need a signed-in account with the admin flag.

### 5.5 Games, campaigns and reports belong to accounts

- **REQ-USER-40** Creating or joining a game, starting a campaign, and sending a bug report or suggestion record the account. The lobby's "Your games" and the list of campaigns come from the server, so they follow the user to any device.
- **REQ-USER-41** Retired: claiming games from before accounts. Those games were deleted instead.
- **REQ-USER-42** A player may act in a seat (commands, undo, delete the game, report) only when the seat belongs to their account. One account cannot hold both seats of a two-player game, except the admin in a copy of a reported game (REQ-BUG-07).
- **REQ-USER-43** A campaign is opened only by the account that started it.

### 5.6 Admin tools for games and campaigns

These keep their numbers; REQ-ADMIN-01 and -02, about the admin password, are retired (REQ-USER-04, -32).

- **REQ-ADMIN-03** The Admin page lists every game, in any state, with its mode, status, players and creation date, and can delete any game after a confirmation. Players connected to a deleted game get the `game_deleted` message.
- **REQ-ADMIN-04** The Admin page lists every Five-Year Mission campaign and can delete one after a confirmation. Its games are not deleted.
- **REQ-ADMIN-05** Apart from the admin, only a player seated in a game can delete it. A game still waiting for an opponent therefore can be deleted only by the player who created it.
- **REQ-ADMIN-06** The admin can take over any seat of any game from the Admin page, after a confirmation. The seat moves to the admin's account, and the admin is taken to the game in that seat. The player who held it is locked out for good: they can no longer act in it, any page they have open is told and disconnected, and they can still watch. The game itself is unchanged and carries on from where it was.

### 5.7 Limits

Accounts identify people, but the site is still meant for a small private group: there is no email verification beyond the invitation, no two-step sign-in, and no way for players to delete their own account (the admin disables it). The email address is visible only to the admin; other players see display names.

### 5.8 Bug reports

A player who sees something wrong can report it from the game table. The report carries what is needed to recreate the game, so the bug can be reproduced later, also after the game has moved on or been deleted. A report also records the reporter's account (REQ-USER-40).

- **REQ-BUG-01** The game table has a **Report a bug** button for a seated player once the game has started, also after it is over. It is not shown to someone without a seat.
- **REQ-BUG-02** The button opens a dialog that asks what the player saw and what they expected (required, up to 4000 characters). Sending it does not change or interrupt the game; the dialog confirms that the report was saved.
- **REQ-BUG-03** The server saves the description with a **bundle**: the game's mode, box, expansions, promo sets, seed, Bot choice, campaign setup, seats (name, Crew deck, board side) and every stored command so far, including undone and dropped ones and each command's weekday (REQ-SRV-52). Because a game is rebuilt from exactly these (REQ-SRV-14), the bundle recreates the game as it was, and any earlier moment by replaying fewer commands.
- **REQ-BUG-04** The bundle also records what the reporter was looking at, for reading without a replay: the turn, step and active seat, the pending decision with its options, the last 60 log lines, and the reporter's own view of the game.
- **REQ-BUG-05** Only the admin can read reports, because a bundle holds both players' hidden cards. The Admin page lists them, newest first, with the reporter, the game and the description, and can mark one resolved, reopen it or delete it.
- **REQ-BUG-06** The admin can download a report as a JSON file, written by the server (`GET /api/admin/bugs/{id}/download`) so that no number passes through the browser; the seed is also stored as text, because JavaScript rounds a 63-bit seed and the game would no longer replay. `scripts/replay_bug.py` rebuilds the game from that file with the rules of the current checkout and prints where it stands: the last log lines and the pending decision. `--moves N` and `--back N` stop earlier; `--state` writes the whole engine state.
- **REQ-BUG-07** The admin can **recreate** a report: the server makes a new game from the bundle, as reported or a chosen number of moves earlier. Every seat of the copy belongs to the admin's account, so the admin can play both sides of a two-player game: each request acts in the seat whose decision is pending. The copy is an ordinary game and can be played on. The original game is not touched, and a copy of a campaign assignment never counts for the campaign.
- **REQ-BUG-08** A report has no link to the game's row, so deleting the game keeps the report. If the rules have changed so that a stored move no longer applies, the copy follows REQ-SRV-14's rule for that: the move and the later ones are dropped and a note is logged.
- **REQ-BUG-09** Next to Report a bug, a seated player has **Suggest a feature**: the same dialog, asking what they would like the game to do. A suggestion is saved the same way, with the same bundle (REQ-BUG-03, -04), so the position that prompted it can be recreated. The Admin page lists bugs and suggestions together, marked by kind, and can show only one kind.

## 6. Deployment and operations

- **REQ-OPS-01** The React app is built to static files. The Python server serves them in production, so the site runs as a single service on one domain. This avoids cross-origin setup.
- **REQ-OPS-02** In development, the Vite dev server proxies `/api` to the Python server.
- **REQ-OPS-03** A Dockerfile builds the client and runs the server in one image.
- **REQ-OPS-04** Configuration comes only from environment variables:

| Variable | Purpose |
|---|---|
| `SESSION_SECRET` | Key for signing session cookies |
| `ADMIN_EMAIL` | Where `python -m app.create_admin` sends the first admin invitation when no address is given |
| `PUBLIC_URL` | The site's address, used in links in emails, for example `https://captains-chair-wild-bush-4325.fly.dev` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM` | Sending email (REQ-USER-23). Optional: without them, emails go to the server log |
| `DATABASE_URL` | Database location. Defaults to a local SQLite file |
| `LOG_LEVEL` | Server log detail |

- **REQ-OPS-05** Server logs must never contain passwords, session cookies, or invitation and reset codes. When no SMTP settings are set, the emails written to the log do contain their links; that is only for a developer's machine.
- **REQ-OPS-06** The SQLite database file is backed up daily if the host allows it.
- **REQ-OPS-07** The site is hosted on Fly.io from `fly.toml`: one machine, with one volume mounted at `/app/data` for the SQLite file. It must stay a single machine, because the server caches games in memory and locks commands in-process (REQ-SRV-42). The session secret and the SMTP password are Fly secrets, never in the file. The container starts as root only to give the mounted volume to the unprivileged `app` user (`scripts/docker-entrypoint.sh`), then runs the server as `app`.

## 7. Out of scope for the first version

- Profiles, statistics and match history per person (accounts exist, §5).
- Matchmaking with strangers.
- Spectators.
- Turn timers.
