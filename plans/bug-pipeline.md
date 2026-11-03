# Plan: from a bug report on Fly to a deployed fix

Today a player's bug report sits in the database on Fly, and only someone signed in as the admin in a browser can download it. A Claude Code cloud session can reach neither the site (its network policy blocks `*.fly.dev`) nor the admin account (sign-in is a browser cookie), and nothing deploys except `fly deploy` run by hand. This plan makes the loop **fetch → reproduce → fix → test → merge → deploy → resolve** something a session can run on its own from one request ("fix the newest bug"), with you approving only the merge. Each step ends with something you can test.

## How it works today

- Reports are `BugReport` rows (`server/app/models.py`): description, kind (`bug` or `feature`), status (`open` or `resolved`) and a bundle with the setup, seed and every command (REQ-BUG-03, -04).
- The admin endpoints already give everything needed: `GET /api/admin/bugs` (the list), `GET /api/admin/bugs/{id}/download` (the file, with the seed safe from JavaScript rounding, REQ-BUG-06) and `POST /api/admin/bugs/{id}/status`. All of them need `require_admin`, which reads only the session cookie (`app/auth.py`).
- `scripts/replay_bug.py report.json` rebuilds the game with the current rules and prints where it stands; `bugs.rebuild(bundle)` gives the `GameState` for a test.
- The app is `captains-chair-wild-bush-4325` on Fly (`fly.toml`), with SQLite on the `game_data` volume. There is no `.github/workflows`, so every deploy is a manual `fly deploy` from your computer.
- Cloud sessions push only to their own `ccr-…` branch and open pull requests only when asked.

## Decisions

These are proposed defaults for you to confirm or change.

1. **A machine token, not a password.** The session gets a long random **bug token** that opens only the bug endpoints (list, download, set status). It cannot sign in, play, see users or recreate games. You store it as a Fly secret (`BUG_API_TOKEN`) and as a secret in the cloud environment. No admin password ever sits in an environment variable, and you can change the token on its own.
2. **You approve every deploy by merging.** Claude fixes the bug on its branch and opens a pull request. Merging to `main` deploys. Claude never runs `fly deploy` itself and never holds a Fly token. GitHub holds the Fly token, and a workflow deploys only after the server tests and the client build pass.
3. **A report is resolved by its deploy, not by its fix.** The commit names the report (`Fixes-Bug: <id>`). After a successful deploy, the workflow marks those reports resolved with the bug token. A fix that is never merged leaves the report open.
4. **Every fixed bug leaves a regression test.** The report's bundle is saved as `server/tests/bugs/<short-id>.json`, and a test replays it and asserts the behaviour that was wrong. Before it is committed, the bundle is cut down to what the replay needs: setup, seed and commands. The players' views, log lines and real display names are left out (names become `Player 1`, `Player 2`), and the email addresses that accounts hold are never in the bundle anyway. The downloaded originals stay in a git-ignored `bugs/` folder in the session.
5. **One skill holds the procedure.** `.claude/skills/fix-bug/SKILL.md` is checked in, so any cloud session in this repository knows the steps, and the request is just "fix the newest bug" or "fix bug 3f2a".

## Design

### The bug token (server)

- `Settings.bug_api_token: str = ""` (`app/config.py`). Empty means the token route is off, as in tests that do not set it.
- `auth.require_admin_or_bug_token(request)`: allow the request if the signed-in account is an admin, or if `Authorization: Bearer <token>` equals `bug_api_token` (compared with `hmac.compare_digest`). Failed token attempts go through the same rate limit as logins.
- Only the bug list, the download and the status endpoints use the new dependency. Delete and recreate stay admin-only.
- The token is never logged. A request made with it is logged as `bug-token` in place of a user.

### Network and secrets (your one-time setup, no code)

- Cloud environment → Edit → Network access: add `captains-chair-wild-bush-4325.fly.dev` under **Allowed domains** (keep "Allow package managers" ticked).
- Cloud environment → environment variables: `CC_URL=https://captains-chair-wild-bush-4325.fly.dev` and `CC_BUG_TOKEN=<token>`.
- Fly: `fly secrets set BUG_API_TOKEN=<token>` (the same token).
- GitHub repository → Settings → Secrets → Actions: `FLY_API_TOKEN` (from `fly tokens create deploy -a captains-chair-wild-bush-4325`, a deploy-only token for this one app) and `CC_BUG_TOKEN`.

### `scripts/bugs.py` (the session's tool)

One script, standard library only (`urllib`), reading `CC_URL` and `CC_BUG_TOKEN`:

```bash
scripts/bugs.py list                 # open reports, newest first: short id, kind, date, mode, Crews, description
scripts/bugs.py list --all           # resolved ones too
scripts/bugs.py get 3f2a             # download to bugs/bug-3f2a….json (a unique prefix is enough), print the summary
scripts/bugs.py get newest           # the newest open bug (not feature)
scripts/bugs.py fixture 3f2a         # write the trimmed bundle to server/tests/bugs/3f2a.json (Decision 4)
scripts/bugs.py resolve 3f2a [...]   # mark resolved (used by the deploy workflow)
```

The file `get` writes is exactly the download, so `scripts/replay_bug.py` reads it unchanged. `bugs/` goes into `.gitignore`.

### Regression tests

`server/tests/test_bug_reports.py` uses a small helper, `replay_fixture(name, moves=None) -> GameState` (wrapping `bugs.rebuild`), and holds one test per fixed report, named after it, with the report's description as its docstring. The test asserts the corrected behaviour at the reported position, not only that the replay runs. A fix that changes the rules so that an old move no longer applies (REQ-BUG-08) cuts the fixture's commands back to the last one that still applies.

### Continuous deploy (`.github/workflows/deploy.yml`)

- **On every pull request:** set up Python and Node, run `scripts/start.sh --test` and `cd client && npm ci && npm run build`. This is the check you look at before merging.
- **On push to `main`:** the same checks, then `superfly/flyctl-actions/setup-flyctl` and `flyctl deploy --remote-only`, then wait for `GET /api/health` to answer, then `scripts/bugs.py resolve` for every `Fixes-Bug:` id in the commits of the push.
- A concurrency group keeps two deploys from running at once. A failed deploy leaves the reports open and the run red.
- Fly keeps the previous release, so `fly releases` plus `fly deploy --image <previous>` is the rollback. It goes in the README's new Deploying section.

### The skill (`.claude/skills/fix-bug/SKILL.md`)

The steps a session follows:

1. `scripts/bugs.py list`, then `get <id>` (or `get newest`). Read the description, the pending decision and the last log lines.
2. `scripts/replay_bug.py bugs/<file>.json`, then `--back N` until the position just before it went wrong. Find the card, rule or client code involved, and the requirement or card spec that governs it. If the requirements, the spec and the reporter disagree, stop and ask (CLAUDE.md).
3. `scripts/bugs.py fixture <id>`, then write the failing test in `test_bug_reports.py` and see it fail.
4. Fix it, following CLAUDE.md (spec first, then code; `scripts/build_content.py` after spec edits).
5. `scripts/start.sh --test` (and `npm run build` for client changes) until green. The replay now shows the corrected outcome.
6. Commit with `Fixes-Bug: <full id>` in the message, push the session branch, open a pull request that says what the player saw, the cause, the fix and the test.
7. Tell you the pull request is ready. Merging deploys and resolves the report.

A report that is a feature request, or a bug that cannot be reproduced from its bundle, is reported back to you instead of being guessed at.

## Steps

1. **Token access.** `bug_api_token`, `require_admin_or_bug_token`, used by the three bug endpoints. Tests: the token lists, downloads and resolves; a wrong or missing token gets 401; the token cannot delete, recreate or reach any other admin or game endpoint; with no token configured the bearer route is off; an admin cookie still works. Requirements: a new REQ-BUG-10 in `requirements/19-technical-architecture.md` §5.8.
2. **`scripts/bugs.py`** and `bugs/` in `.gitignore`. Tests: against the FastAPI test client (the script's HTTP layer takes a base URL), `list`, `get`, prefix matching, `fixture`'s trimming (no views, no log lines, no names) and `resolve`.
3. **Regression test harness.** `server/tests/bugs/`, `replay_fixture` and `test_bug_reports.py`, with a first fixture made from a bug report the tests themselves file, so the harness is tested before a real report arrives.
4. **CI and deploy workflow.** `.github/workflows/deploy.yml` and the README's Deploying section. Test: a pull request runs the checks, and the first merge deploys and shows in `fly releases`.
5. **The skill.** `.claude/skills/fix-bug/SKILL.md`, and a line in CLAUDE.md's Engine section pointing at it.
6. **Your setup and a dry run.** You do the one-time setup above. Then a session runs "fix the newest bug" on the Cadet Training report that started this, end to end, through to the deploy and the report showing resolved on the Admin page.

## Not in this plan

- Claude deploying without your merge, or holding Fly credentials.
- Reading or copying the production database. The bug endpoints are the only way in.
- Automatic triage of every new report (a scheduled session could run `bugs.py list` daily and fix the newest one; this is easy to add once the loop works).
