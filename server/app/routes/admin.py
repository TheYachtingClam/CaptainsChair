"""The admin: delete any game or campaign (requirements/19-technical-architecture.md §5.3, REQ-ADMIN-01 to -05)."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import play
from app.auth import (
    admin_enabled,
    check_admin_password,
    clear_admin,
    is_admin,
    issue_admin,
    login_limiter,
    require_admin,
    require_session,
)
from app.config import get_settings
from app.db import get_db
from app.hub import hub
from app.models import Campaign, Game

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_session)])


class AdminLogin(BaseModel):
    password: str


@router.get("/status")
def admin_status(request: Request) -> dict:
    """Whether the admin is configured, and whether this browser is signed in as the admin."""
    return {"enabled": admin_enabled(get_settings()), "admin": is_admin(request)}


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def admin_login(body: AdminLogin, request: Request, response: Response) -> None:
    settings = get_settings()
    if not admin_enabled(settings):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "There is no admin on this server")
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(f"admin:{ip}", settings.login_attempts_per_minute):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts. Try again in a minute.")
    if not check_admin_password(body.password, settings):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")
    issue_admin(response, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def admin_logout(response: Response) -> None:
    clear_admin(response)


@router.get("/games", dependencies=[Depends(require_admin)])
def all_games(db: Session = Depends(get_db)) -> list[dict]:
    """Every game, newest first, in any state (REQ-ADMIN-03)."""
    games = db.scalars(select(Game).options(selectinload(Game.seats)).order_by(Game.created_at.desc())).all()
    return [{
        "id": g.id,
        "mode": g.mode,
        "status": g.status,
        "created_at": g.created_at.isoformat() if g.created_at else None,
        "players": [s.display_name for s in sorted(g.seats, key=lambda s: s.index)],
        "bot": (g.bot or {}).get("deck_id"),
        "campaign_id": (g.campaign or {}).get("id"),
        "moves": sum(1 for c in g.commands or [] if not c.get("undone")),
    } for g in games]


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_any_game(game_id: str, db: Session = Depends(get_db)) -> None:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Game not found")
    db.delete(game)
    db.commit()
    play.forget(game_id)
    await hub.broadcast(game_id, {"type": "game_deleted"})


@router.get("/campaigns", dependencies=[Depends(require_admin)])
def all_campaigns(db: Session = Depends(get_db)) -> list[dict]:
    """Every Five-Year Mission campaign, newest first (REQ-ADMIN-04)."""
    camps = db.scalars(select(Campaign).order_by(Campaign.created_at.desc())).all()
    return [{
        "id": c.id,
        "display_name": c.display_name,
        "deck_id": c.deck_id,
        "rank": c.rank,
        "assignments": len(c.assignments or []),
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    } for c in camps]


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)) -> None:
    camp = db.get(Campaign, campaign_id)
    if camp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
    db.delete(camp)
    db.commit()
