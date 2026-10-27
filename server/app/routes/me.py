"""The signed-in account's own games and campaigns (requirements/19-technical-architecture.md REQ-USER-40)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_session, viewer_id
from app.db import get_db
from app.models import Campaign, Game, Seat
from app.routes.games import summarize

router = APIRouter(prefix="/api/me", tags=["me"], dependencies=[Depends(require_session)])


@router.get("/games")
def my_games(db: Session = Depends(get_db), user_id: str = Depends(viewer_id)) -> list[dict]:
    """Every game with a seat held by this account, newest first, with that seat."""
    games = db.scalars(select(Game).join(Seat).where(Seat.user_id == user_id)
                       .options(selectinload(Game.seats)).order_by(Game.created_at.desc())).unique().all()
    return [{**summarize(g), "your_seat": next(s.index for s in g.seats if s.user_id == user_id)} for g in games]


@router.get("/campaigns")
def my_campaigns(db: Session = Depends(get_db), user_id: str = Depends(viewer_id)) -> list[dict]:
    camps = db.scalars(select(Campaign).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc())).all()
    return [{"id": c.id, "display_name": c.display_name, "deck_id": c.deck_id, "rank": c.rank, "status": c.status,
             "assignments": len(c.assignments or []), "created_at": c.created_at.isoformat() if c.created_at else None}
            for c in camps]
