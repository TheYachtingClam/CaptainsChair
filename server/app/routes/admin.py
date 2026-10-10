"""The admin: delete any game or campaign (requirements/19-technical-architecture.md §5.3, REQ-ADMIN-01 to -05)."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import bugs, play
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
from app.models import BugReport, Campaign, Game
from app.schemas import BugStatus

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


# ------------------------------------------------------------------ bug reports (REQ-BUG-05 to -08)

def _bug(db: Session, bug_id: str) -> BugReport:
    report = db.get(BugReport, bug_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bug report not found")
    return report


def _bug_summary(r: BugReport) -> dict:
    game = r.bundle.get("game", {})
    return {
        "id": r.id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "game_id": r.game_id,
        "reporter": r.reporter,
        "seat": r.seat,
        "description": r.description,
        "status": r.status,
        "mode": game.get("mode"),
        "box": game.get("box"),
        "players": [f"{s['display_name']} ({s['deck_id']})" for s in game.get("seats", [])],
        "bot": (game.get("bot") or {}).get("deck_id"),
        "turn": r.bundle.get("turn"),
        "step": r.bundle.get("step"),
        "moves": len(r.bundle.get("commands", [])),
    }


@router.get("/bugs", dependencies=[Depends(require_admin)])
def all_bugs(db: Session = Depends(get_db)) -> list[dict]:
    """Every bug report, newest first."""
    reports = db.scalars(select(BugReport).order_by(BugReport.created_at.desc())).all()
    return [_bug_summary(r) for r in reports]


@router.get("/bugs/{bug_id}", dependencies=[Depends(require_admin)])
def one_bug(bug_id: str, db: Session = Depends(get_db)) -> dict:
    """The whole report with its bundle: the file `scripts/replay_bug.py` reads (REQ-BUG-06)."""
    report = _bug(db, bug_id)
    return {**_bug_summary(report), "bundle": report.bundle}


@router.post("/bugs/{bug_id}/status", dependencies=[Depends(require_admin)])
def set_bug_status(bug_id: str, body: BugStatus, db: Session = Depends(get_db)) -> dict:
    report = _bug(db, bug_id)
    report.status = body.status
    db.commit()
    return _bug_summary(report)


@router.delete("/bugs/{bug_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_bug(bug_id: str, db: Session = Depends(get_db)) -> None:
    db.delete(_bug(db, bug_id))
    db.commit()


class Recreate(BaseModel):
    # How many of the report's commands to keep; all of them when left out. Fewer goes back in time.
    moves: int | None = None


@router.post("/bugs/{bug_id}/recreate", dependencies=[Depends(require_admin)])
def recreate_bug(bug_id: str, body: Recreate | None = None, db: Session = Depends(get_db)) -> dict:
    """Make a playable copy of the reported game, as it was at the report or `moves` commands in (REQ-BUG-07). The
    copy is a new game with new seat tokens, returned for every seat; the original game is not touched."""
    from app.auth import hash_seat_token, new_seat_token

    report = _bug(db, bug_id)
    moves = body.moves if body else None
    if moves is not None and not 0 <= moves <= len(report.bundle["commands"]):
        raise HTTPException(422, "There are not that many moves in the report")
    game = bugs.as_game(report.bundle, moves=moves)
    game.status = "active" if moves is not None else game.status
    if game.campaign:  # a copy must never count for the campaign it came from
        game.campaign = {k: v for k, v in game.campaign.items() if k in ("reinforcement", "setup")}
    tokens = {}
    for seat in game.seats:
        tokens[seat.index] = token = new_seat_token()
        seat.token_hash = hash_seat_token(token)
    db.add(game)
    db.commit()
    try:
        state = play.build(game)  # replays with today's rules; moves that no longer apply are dropped and noted
    except Exception as err:  # the setup itself no longer works: report it, and do not leave a broken game behind
        db.delete(game)
        db.commit()
        raise HTTPException(409, f"The game cannot be recreated with the current rules: {err}") from err
    if state.step == "over":
        game.status = "finished"
    elif game.status == "finished":
        game.status = "active"
    db.commit()
    return {"game_id": game.id, "seat_tokens": tokens, "reporter_seat": report.seat}
