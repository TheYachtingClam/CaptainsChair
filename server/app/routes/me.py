"""The signed-in account's own games and campaigns (requirements/19-technical-architecture.md REQ-USER-40)."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import play
from app.auth import require_session, viewer_id
from app.db import get_db
from app.models import Campaign, Game, Seat, User
from app.routes.games import summarize

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/me", tags=["me"], dependencies=[Depends(require_session)])


def _fill_standing(db: Session, games) -> None:
    """Games saved before the lobby's standing existed get it once, by replaying them (REQ-CLI-60)."""
    missing = [g for g in games if g.seed is not None and g.standing is None]
    for game in missing:
        try:
            play.record(game, play.build(game))
        except Exception:  # a setup the current rules can no longer build: the lobby shows it without a standing
            log.warning("cannot work out where game %s stands", game.id)
    if missing:
        db.commit()


@router.get("/games")
def my_games(db: Session = Depends(get_db), user_id: str = Depends(viewer_id)) -> list[dict]:
    """Every game with a seat held by this account, newest first, with that seat."""
    games = db.scalars(select(Game).join(Seat).where(Seat.user_id == user_id)
                       .options(selectinload(Game.seats)).order_by(Game.created_at.desc())).unique().all()
    _fill_standing(db, games)
    return [{**summarize(g), "your_seat": next(s.index for s in g.seats if s.user_id == user_id)} for g in games]


@router.get("/campaigns")
def my_campaigns(db: Session = Depends(get_db), user_id: str = Depends(viewer_id)) -> list[dict]:
    camps = db.scalars(select(Campaign).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc())).all()
    return [{"id": c.id, "display_name": c.display_name, "deck_id": c.deck_id, "rank": c.rank, "status": c.status,
             "assignments": len(c.assignments or []), "created_at": c.created_at.isoformat() if c.created_at else None}
            for c in camps]


@router.get("/opponents")
def opponents(db: Session = Depends(get_db), user_id: str = Depends(viewer_id)) -> list[dict]:
    """The players this account can challenge (REQ-USER-50): every other active account, by display name only; email
    addresses stay with the admin (REQ-USER-60)."""
    users = db.scalars(select(User).where(User.disabled.is_(False), User.id != user_id)).all()
    return sorted(({"id": u.id, "display_name": u.display_name} for u in users), key=lambda u: u["display_name"].lower())
