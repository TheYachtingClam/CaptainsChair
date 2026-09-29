#!/usr/bin/env bash
# Starts the Captain's Chair server.
#
#   scripts/start.sh            build the client and run the server locally on http://localhost:8000
#   scripts/start.sh --dev      run the API with auto-reload and the Vite dev server on http://localhost:5173
#   scripts/start.sh --docker   build and run everything with docker compose
#   scripts/start.sh --test     run the server tests
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MODE="${1:-local}"

ensure_env() {
  if [[ ! -f .env ]]; then
    local password secret
    password="$(python3 -c 'import secrets; print(secrets.token_urlsafe(9))')"
    secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
    sed -e "s|^SITE_PASSWORD=.*|SITE_PASSWORD=${password}|" \
        -e "s|^SESSION_SECRET=.*|SESSION_SECRET=${secret}|" .env.example > .env
    echo "Created .env. The site password is: ${password}"
    echo "Change SITE_PASSWORD in .env to set your own."
  fi
}

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. $2" >&2; exit 1; }
}

load_env() {
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
}

install_deps() {
  need uv "Install it from https://docs.astral.sh/uv/"
  need npm "Install Node.js 20 or later."
  (cd server && uv sync --python 3.12 --quiet)
  (cd client && [[ -d node_modules ]] || npm ci --silent)
}

case "$MODE" in
  local)
    ensure_env
    install_deps
    echo "Building the client..."
    (cd client && npm run build --silent)
    rm -rf server/static && cp -R client/dist server/static
    load_env
    echo "Starting the server on http://localhost:8000"
    cd server && exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;
  --dev)
    ensure_env
    install_deps
    load_env
    rm -rf server/static  # the Vite dev server serves the client in this mode
    (cd server && uv run uvicorn app.main:app --reload --port 8000) &
    API_PID=$!
    trap 'kill $API_PID 2>/dev/null || true' EXIT
    echo "API on http://localhost:8000, client on http://localhost:5173"
    cd client && npm run dev
    ;;
  --docker)
    ensure_env
    need docker "Install Docker Desktop."
    exec docker compose up --build
    ;;
  --test)
    need uv "Install it from https://docs.astral.sh/uv/"
    cd server && exec uv run pytest -q
    ;;
  *)
    sed -n '2,8p' "$0"
    exit 1
    ;;
esac
