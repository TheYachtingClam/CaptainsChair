# 19 – Technical Architecture: Python API Server, React Client, Password Access

This document covers how the online game is built. It does not change any game rules. The game rules are in files 01–18.

## 1. Overview

- **REQ-TECH-01** The system has two parts:
  - an **API server** written in Python, which owns all game state and enforces every rule;
  - a **web client** written in React, which shows the game and sends player choices.
- **REQ-TECH-02** The server is the only authority. The client never decides whether a move is legal, and never receives hidden information (see [11-logging-and-hidden-information.md](11-logging-and-hidden-information.md)).
- **REQ-TECH-03** Access to the whole site is protected by one shared password (see §5).

```
Browser (React)  ──HTTPS / REST──►  Python API server  ──►  Database
                 ◄──WebSocket────   (rules engine)
```

## 2. Assumptions

These are defaults. Change them here if you decide otherwise.

- The expected audience is a small private group: friends playing two-player games, plus solo games against the Bot and Cadet Training.
- One server instance is enough; there is no need for horizontal scaling.
- Players do not have individual accounts. They enter a display name when they create or join a game.
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
- **REQ-SRV-17** The Bot ([22-solo-mode.md](22-solo-mode.md)) runs inside the server as another source of commands. It uses the same rules engine and its own view, with no access to hidden information beyond what the Bot rules allow.
- **REQ-SRV-19** A game starts as soon as every seat is filled: the server picks a random seed, runs setup, and the first decision goes to the Starting Player. Solo play against the Bot is rejected at game creation until the Bot exists; Cadet Training starts with one seat and runs the virtual-opponent rules of [16-solo-and-cadet-training.md](16-solo-and-cadet-training.md).
- **REQ-SRV-18** Game creation accepts the expansions to include, whether to include promo cards (REQ-CS-20), and for solo games the Bot's Crew, difficulty and optional Ticking Clock challenge.

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
| `POST /api/auth/login` | Check the shared password and start a session |
| `POST /api/auth/logout` | End the session |
| `GET /api/health` | Liveness check for hosting; no auth |
| `GET /api/content/decks` | List Crew decks with complexity and summary text |
| `GET /api/content/cards` | Card list for reference screens |
| `POST /api/games` | Create a game: mode, chosen deck, board side, display name |
| `GET /api/games` | List open and in-progress games |
| `POST /api/games/{id}/join` | Join as the second player |
| `DELETE /api/games/{id}` | Delete the game for everyone. Needs the seat token of a player in that game. Connected players get a `game_deleted` message and return to the lobby |
| `GET /api/games/{id}` | Current view of the game for this player |
| `POST /api/games/{id}/commands` | Submit a command |
| `GET /api/games/{id}/log` | Public action log |
| `POST /api/campaigns` | Start a Five-Year Mission campaign |
| `GET /api/campaigns/{id}` | Campaign log, rank, Reinforcement pile and Boosts |
| `POST /api/campaigns/{id}/assignments` | Start the next assignment against a chosen or random Bot |
| `POST /api/campaigns/{id}/upgrade` | Choose the upgrade after an assignment |
| `POST /api/games/{id}/undo` | Undo the last command. See [20-undo.md](20-undo.md) |

- **REQ-SRV-30** After creating or joining a game, the player receives a **seat token**. It identifies which seat they hold, so they can rejoin after a refresh. It is separate from the site password session.

### 3.6 WebSocket

- **REQ-SRV-40** Each client opens one WebSocket per game at `/api/games/{id}/ws`, authenticated with the session and the seat token.
- **REQ-SRV-41** After any accepted command, the server pushes each connected player their own updated view, plus the new events for animation and the action log.
- **REQ-SRV-42** Commands may be sent over the WebSocket or over REST. The server processes one command per game at a time, in arrival order.
- **REQ-SRV-43** When a player reconnects, the server sends the full current view.
- **REQ-SRV-44** The server tells each player when their opponent connects or disconnects.

### 3.7 Persistence

- **REQ-SRV-50** Game records, command history and seat tokens are stored in the database. A server restart must not lose any game.
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
| Password page | One password field and a submit button. Shown whenever there is no valid session |
| Lobby | Create game, list of open games to join, list of the player's own in-progress games. Each of the player's own games has a Delete button that asks for confirmation, because deleting cannot be undone |
| New game | Choose mode (two-player, solo against the Bot, Cadet Training), expansions, promo cards, Crew deck (with complexity and summary), board side and display name. Solo adds Bot Crew, difficulty and Ticking Clock |
| Campaign | Five-Year Mission log, rank, upgrades, challenges and the next assignment |
| Game table | The main play screen (§4.3) |
| Score screen | Final score breakdown per player, following [13-final-scoring.md](13-final-scoring.md) |
| Reference | Keyword glossary, icon reference and common card list |

### 4.3 Game table

- **REQ-CLI-10** Show the central area: Market decks and faceup cards, Junk pile, Incident deck, Encounter deck, Stardate pile with its Glory, Location deck and the three Neutral Zone slots with token counts per player.
- **REQ-CLI-11** Show both player areas: Location Area with Duty Officer slots, Fleet Area, Staging Area, Draw deck count, Discard pile, Reserve deck count, Development pile, Captain's Log, Crew board with tracks and missions, resource pool and Action tokens.
- **REQ-CLI-12** Clicking any public pile opens a viewer: Discard pile, Junk pile, Development pile, Captain's Log, and beamed cards under a host card.
- **REQ-CLI-13** Clicking a card shows a large version with its full rules text. Keywords in the text link to the reference.
- **REQ-CLI-14** When the player has a pending decision, the table highlights the legal choices and shows a prompt explaining what to choose. Optional decisions have a clear skip button.
- **REQ-CLI-15** When a Reaction becomes available on the opponent's turn, the player gets a clear prompt with a way to use it or decline.
- **REQ-CLI-16** An action log lists every public event in plain words.
- **REQ-CLI-17** A turn indicator shows whose turn it is, the current step, and whether a Resolution has been triggered with how many turns remain.
- **REQ-CLI-18** The table works on a laptop screen. Tablet support is desirable. Phone support is not required.

## 5. Access control: shared password

The whole site is behind one password that you share with the people you want to let in. There are no user accounts.

### 5.1 Behaviour

- **REQ-AUTH-01** Every page and every API endpoint, except login and health, requires a valid session.
- **REQ-AUTH-02** Without a valid session, the client shows only the password page.
- **REQ-AUTH-03** A correct password creates a session that lasts **30 days**. The player is not asked again on that browser until it expires or they log out.
- **REQ-AUTH-04** A wrong password shows "Incorrect password" and nothing else.
- **REQ-AUTH-05** Changing the password on the server ends all existing sessions.

### 5.2 Server implementation

- **REQ-AUTH-10** The password is set through an environment variable, for example `SITE_PASSWORD`. It is never stored in the code or the repository.
- **REQ-AUTH-11** The server compares passwords with a constant-time comparison.
- **REQ-AUTH-12** On success, the server sets a signed session cookie:
  - `HttpOnly`, so page scripts cannot read it;
  - `Secure`, so it is only sent over HTTPS;
  - `SameSite=Lax`.
- **REQ-AUTH-13** The cookie is signed with a secret from another environment variable, for example `SESSION_SECRET`. The signed value includes a fingerprint of the current password, so changing the password invalidates old cookies.
- **REQ-AUTH-14** The WebSocket connection checks the same session cookie before accepting.
- **REQ-AUTH-15** Login attempts are rate-limited per IP address, for example 5 attempts per minute, to slow down password guessing.
- **REQ-AUTH-16** The server refuses to start if `SITE_PASSWORD` or `SESSION_SECRET` is missing.

### 5.3 Limits of this approach

A shared password keeps strangers out, but it does not identify people. Anyone with the password can open any game's lobby entry. Seats are protected by seat tokens (REQ-SRV-30), so one player cannot act as another. If you later need per-person accounts, replace §5 without changing the rest of the system.

## 6. Deployment and operations

- **REQ-OPS-01** The React app is built to static files. The Python server serves them in production, so the site runs as a single service on one domain. This avoids cross-origin setup.
- **REQ-OPS-02** In development, the Vite dev server proxies `/api` to the Python server.
- **REQ-OPS-03** A Dockerfile builds the client and runs the server in one image.
- **REQ-OPS-04** Configuration comes only from environment variables:

| Variable | Purpose |
|---|---|
| `SITE_PASSWORD` | The shared access password |
| `SESSION_SECRET` | Key for signing session cookies |
| `DATABASE_URL` | Database location. Defaults to a local SQLite file |
| `LOG_LEVEL` | Server log detail |

- **REQ-OPS-05** Server logs must never contain the password, session cookies or seat tokens.
- **REQ-OPS-06** The SQLite database file is backed up daily if the host allows it.

## 7. Out of scope for the first version

- Per-user accounts, profiles and match history per person.
- Matchmaking with strangers.
- Spectators.
- Turn timers.
