# Captain's Chair Online

An online version of *Star Trek: Captain's Chair*. Gameplay is not implemented yet. The current build has sign-in, a lobby, game creation and joining, and live connections.

## Run it

```bash
scripts/start.sh            # build the client, run on http://localhost:8000
scripts/start.sh --docker   # same, with docker compose
scripts/start.sh --dev      # auto-reloading API on :8000 and client on http://localhost:5173
scripts/start.sh --test     # server tests
```

The first run creates `.env` with a random site password and prints it. Change `SITE_PASSWORD` in `.env` to choose your own. Changing it signs everyone out.

Local runs need [uv](https://docs.astral.sh/uv/) and Node.js 20 or later. Docker runs need only Docker.

## Layout

| Path | Contents |
|---|---|
| `server/` | Python API server (FastAPI) and the rules engine |
| `client/` | React and TypeScript web client (Vite) |
| `requirements/` | Game and system requirements. Start at `00-README.md` |
| `manual/` | Scanned rulebooks |
| `CLAUDE.md` | Rules for writing card code |
