"""Starting tutorials (requirements/24-tutorials.md §1.6)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import tutorial
from app.auth import require_session, viewer_id
from app.db import get_db
from app.models import Game, Seat, User
from app.routes.games import add_seat, summarize
from app.schemas import SeatChoice

router = APIRouter(prefix="/api/tutorials", tags=["tutorials"], dependencies=[Depends(require_session)])


@router.get("")
def all_tutorials(db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> list[dict]:
    """Every tutorial: id, title, summary, whether this account has finished it, and its game in progress if any
    (REQ-TUT-42, -50, -51)."""
    games = db.scalars(select(Game).join(Seat).where(Seat.user_id == viewer, Game.tutorial.is_not(None))
                       .order_by(Game.created_at.desc())).unique().all()
    out = []
    for s in tutorial.scripts().values():
        mine = [g for g in games if (g.tutorial or {}).get("id") == s["id"]]
        playing = next((g.id for g in mine if g.status == "active"), None)
        out.append({"id": s["id"], "title": s["title"], "summary": s["summary"],
                    "finished": any(g.status == "finished" for g in mine), "game_id": playing})
    return out


@router.post("/{tutorial_id}", status_code=status.HTTP_201_CREATED)
def start_tutorial(tutorial_id: str, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    """A new game of the tutorial, for the signed-in account (REQ-TUT-02)."""
    try:
        script = tutorial.script(tutorial_id)
    except tutorial.TutorialError as err:
        raise HTTPException(404, str(err)) from err
    setup = script["setup"]
    game = Game(mode=setup["mode"], box=setup.get("box", "core"), expansions=setup.get("expansions", []),
                promos=False, promo_sets=[],
                tutorial={"id": tutorial_id, "seed": setup.get("seed"), "stack": setup.get("stack")})
    db.add(game)
    seat = add_seat(db, game, SeatChoice(deck_id=setup["deck"], board_side=setup.get("board", "basic")),
                    db.get(User, viewer))
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index}
