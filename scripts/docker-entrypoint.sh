#!/bin/sh
# Starts the server as the unprivileged "app" user. A freshly mounted volume (Fly.io, a bind mount) belongs to root,
# so when the container starts as root this first gives the data directory to "app", then drops to it.
set -e
if [ "$(id -u)" = "0" ]; then
    chown -R app:app /app/data
    exec setpriv --reuid=app --regid=app --init-groups "$@"
fi
exec "$@"
