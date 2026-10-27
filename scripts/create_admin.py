#!/usr/bin/env python3
"""Make the first admin on a local checkout: runs `python -m app.create_admin` with the server's environment.
For the Docker server use `docker exec captainschair-app-1 python -m app.create_admin`, and on Fly
`fly ssh console -C "python -m app.create_admin"`. See server/app/create_admin.py."""

import os
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "server"
python = SERVER / ".venv" / "bin" / "python"
os.chdir(SERVER)
os.execv(str(python), [str(python), "-m", "app.create_admin", *sys.argv[1:]])
