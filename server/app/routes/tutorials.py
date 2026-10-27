"""Starting tutorials (requirements/24-tutorials.md §1.6)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import tutorial
from app.auth import require_session, viewer_id
from app.db import get_db
from app.models import Game, User
from app.routes.games import add_seat, summarize
from app.schemas import SeatChoice

router = APIRouter(prefix="/api/tutorials", tags=["tutorials"], dependencies=[Depends(require_session)])


@router.get("")
def all_tutorials() -> list[dict]:
    """Every tutorial: id, title and one-line summary."""
    return [{"id": s["id"], "title": s["title"], "summary": s["summary"]} for s in tutorial.scripts().values()]


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
