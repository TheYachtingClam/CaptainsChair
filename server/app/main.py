import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import init_db
from app.routes import admin, auth, campaigns, content, games, health, ws


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    app = FastAPI(title="Captain's Chair API", version="0.1.0", lifespan=lifespan)
    for module in (health, auth, content, games, campaigns, admin, ws):
        app.include_router(module.router)

    # In production the server also serves the built React client (REQ-OPS-01).
    static_dir: Path = settings.static_dir
    if (static_dir / "index.html").exists():
        if (static_dir / "assets").exists():
            app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            if path.startswith("api/"):
                raise HTTPException(404)
            candidate = (static_dir / path).resolve()
            if path and candidate.is_file() and static_dir.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
