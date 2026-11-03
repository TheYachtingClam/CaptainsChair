# Captain's Chair Online

An online version of *Star Trek: Captain's Chair*. Gameplay is not implemented yet. The current build has sign-in, a lobby, game creation and joining, and live connections.

## Run it

```bash
scripts/start.sh            # build the client, run on http://localhost:8000
scripts/start.sh --docker   # same, with docker compose
scripts/start.sh --dev      # auto-reloading API on :8000 and client on http://localhost:5173
scripts/start.sh --test     # server tests
scripts/process_scans.py    # turn raw scans into the images the server serves
scripts/build_content.py    # turn card and board specs into the server's data files
```

Everyone signs in with their own account; accounts are made by invitation from the admin. The first run creates `.env`. Set `ADMIN_EMAIL` in it and run `python -m app.create_admin` in `server/` (or `scripts/create_admin.py`): it prints, and emails when SMTP is set, an invitation to sign up as the admin. From then on the Admin page sends invitations.

Local runs need [uv](https://docs.astral.sh/uv/) and Node.js 20 or later. Docker runs need only Docker.

## Deploying

The site runs on Fly.io (`fly.toml`). Merging to `main` deploys it: `.github/workflows/deploy.yml` runs the server tests and the client build on every pull request, and on `main` runs them again, then `flyctl deploy`, then marks resolved the bug reports named by `Fixes-Bug: <id>` lines in the pushed commits.

One-time setup:

- Fly: `fly secrets set BUG_API_TOKEN=<a long random token>` (make one with `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`).
- GitHub, Settings > Secrets and variables > Actions: `FLY_API_TOKEN` (`fly tokens create deploy -a captains-chair-wild-bush-4325`) and `CC_BUG_TOKEN` (the same token as `BUG_API_TOKEN`). Without `FLY_API_TOKEN` the deploy is skipped with a notice.
- For Claude Code cloud sessions, in the environment's settings: allow `captains-chair-wild-bush-4325.fly.dev` under Network access, and set `CC_URL=https://captains-chair-wild-bush-4325.fly.dev` and `CC_BUG_TOKEN=<the token>`.

To roll back, `fly releases -a captains-chair-wild-bush-4325` lists the releases and `fly deploy --image <an earlier image>` puts one back.

## Bug reports

`scripts/bugs.py list` lists the open reports on the live site, `get <id>` downloads one into `bugs/` (git-ignored) and `scripts/replay_bug.py bugs/<file>` rebuilds its game. It needs `CC_URL` and `CC_BUG_TOKEN`. The whole loop, through a regression test and the deploy, is in `plans/bug-pipeline.md` and the `fix-bug` skill (`.claude/skills/fix-bug/SKILL.md`).

## Layout

| Path | Contents |
|---|---|
| `server/` | Python API server (FastAPI) and the rules engine |
| `client/` | React and TypeScript web client (Vite) |
| `requirements/` | Game and system requirements. Start at `00-README.md` |
| `resources/scans/` | Raw scans and rulebook pages, by product and kind, with a spec beside each card and board. Not included in the Docker image. See its README |
| `server/content/images/` | Processed images, served by the server |
| `CLAUDE.md` | Rules for writing card code |
