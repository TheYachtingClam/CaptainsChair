"""Games (requirements/19-technical-architecture.md §3.5). Every seat belongs to an account, and a request acts in
the signed-in account's own seat (REQ-USER-42)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import bugs, content, mail, play
from app.auth import require_session, viewer_id
from app.config import get_settings
from app.db import get_db
from app.hub import hub
from app.models import BugReport, Game, Seat, User
from app.schemas import (
    BugReportRequest,
    CommandRequest,
    CreateGameRequest,
    DevCommand,
    GameSummary,
    GameView,
    SeatChoice,
    SeatGrant,
    SeatOut,
)

router = APIRouter(prefix="/api/games", tags=["games"], dependencies=[Depends(require_session)])

SEATS_BY_MODE = {"two_player": 2, "solo": 1, "cadet": 1}


def seat_count(game: Game) -> int:
    return SEATS_BY_MODE[game.mode]


def summarize(game: Game) -> dict:
    return {
        "id": game.id,
        "created_at": game.created_at,
        "mode": game.mode,
        "box": game.box,
        "expansions": game.expansions,
        "promos": game.promos,
        "status": game.status,
        "seats": [SeatOut.model_validate(s, from_attributes=True) for s in game.seats],
        "open_seats": seat_count(game) - len(game.seats),
        "bot": game.bot,
        "campaign_id": (game.campaign or {}).get("id"),
    }


def seat_for(game: Game, user_id: str | None) -> Seat | None:
    """The seat the account acts in. An account holds one seat of a game, except the admin in a copy made from a bug
    report, who holds every seat (REQ-BUG-07): then it is the seat whose decision is pending."""
    mine = [s for s in game.seats if user_id is not None and s.user_id == user_id]
    if len(mine) > 1 and game.seed is not None:
        decision = play.build(game).decision
        return next((s for s in mine if decision is not None and s.index == decision.seat), mine[0])
    return mine[0] if mine else None


def seat_or_403(game: Game, user_id: str) -> int:
    seat = seat_for(game, user_id)
    if seat is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You have no seat in this game")
    return seat.index


def load_game(db: Session, game_id: str) -> Game:
    game = db.scalar(select(Game).where(Game.id == game_id).options(selectinload(Game.seats)))
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Game not found")
    return game


def validate_deck(deck_id: str, expansions: list[str], box: str = content.DEFAULT_BOX) -> None:
    if deck_id not in content.deck_ids_for(expansions, box):
        raise HTTPException(422, "That Crew deck is not available in this game")


def add_seat(db: Session, game: Game, choice: SeatChoice, user: User) -> Seat:
    """A new seat for the account, under its display name (REQ-USER-40). One account cannot hold two seats of the
    same game (REQ-USER-42)."""
    if any(s.user_id == user.id for s in game.seats):
        raise HTTPException(status.HTTP_409_CONFLICT, "You already have a seat in this game")
    seat = Seat(index=len(game.seats), display_name=user.display_name, deck_id=choice.deck_id,
                board_side=choice.board_side, user_id=user.id)
    game.seats.append(seat)
    if len(game.seats) >= seat_count(game):
        try:
            play.start(game)  # the game starts as soon as every seat is filled
        except play.SetupError as err:
            raise HTTPException(422, str(err)) from err
    db.commit()
    db.refresh(game)
    return seat


@router.get("", response_model=list[GameSummary])
def list_games(db: Session = Depends(get_db)) -> list[dict]:
    games = db.scalars(select(Game).options(selectinload(Game.seats)).order_by(Game.created_at.desc())).all()
    return [summarize(g) for g in games]


@router.post("", response_model=SeatGrant, status_code=status.HTTP_201_CREATED)
def create_game(body: CreateGameRequest, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    unknown = set(body.expansions) - set(content.EXPANSIONS)
    if unknown:
        raise HTTPException(422, f"Unknown expansion: {', '.join(sorted(unknown))}")
    validate_deck(body.deck_id, body.expansions, body.box)
    bot = None
    if body.mode == "solo":
        if body.bot is None:
            raise HTTPException(422, "Choose a Bot to play against")
        if body.bot.deck_id not in content.bot_ids_for(body.expansions, body.box):
            raise HTTPException(422, "That Bot is not available in this game")
        if body.bot.conspiracy and "base_game" not in content.box_sets(body.box):
            raise HTTPException(422, "Conspiracy needs Core Box content in the game")  # REQ-CORE-62
        bot = body.bot.model_dump()
    game = Game(mode=body.mode, box=body.box, expansions=body.expansions, promos=body.promos, bot=bot,
                promo_sets=list(content.ALL_PROMOS) if body.promos else [])
    db.add(game)
    seat = add_seat(db, game, body, db.get(User, viewer))
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index}


@router.post("/{game_id}/join", response_model=SeatGrant)
async def join_game(game_id: str, body: SeatChoice, db: Session = Depends(get_db),
                    viewer: str = Depends(viewer_id)) -> dict:
    game = load_game(db, game_id)
    if len(game.seats) >= seat_count(game):
        raise HTTPException(status.HTTP_409_CONFLICT, "This game is full")
    validate_deck(body.deck_id, game.expansions, game.box)
    if any(s.deck_id == body.deck_id for s in game.seats):
        raise HTTPException(status.HTTP_409_CONFLICT, "Your opponent already chose that Crew deck")
    seat = add_seat(db, game, body, db.get(User, viewer))
    await hub.broadcast(game.id, {"type": "game_updated"})
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index}


@router.get("/{game_id}", response_model=GameView)
def get_game(game_id: str, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    game = load_game(db, game_id)
    seat = seat_for(game, viewer)
    return {**summarize(game), "your_seat": seat.index if seat else None}


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: str, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> None:
    """Delete a game for everyone. Only a player seated in it may do so."""
    game = load_game(db, game_id)
    seat_or_403(game, viewer)
    db.delete(game)
    db.commit()
    play.forget(game_id)
    await hub.broadcast(game_id, {"type": "game_deleted"})


@router.get("/{game_id}/state")
def game_state(game_id: str, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    game = load_game(db, game_id)
    if game.seed is None:
        raise HTTPException(409, "The game has not started yet")
    seat = seat_for(game, viewer)
    return play.view(game, seat.index if seat else None)


# (game, seat) pairs emailed since that seat last moved: a player who is away gets one email, not one per move
# (REQ-USER-25). Kept in memory; after a restart the next email is sent again, which is harmless.
_emailed: set[tuple[str, int]] = set()


def waiting_email(db: Session, game: Game, mover: int, turn_before: int, active_before: int) -> tuple[str, str, str] | None:
    """The email telling a player of a two-player game that the game is waiting for them (REQ-USER-25): their turn
    has come, or the other player's move needs a decision from them (a Reaction, an attack, a choice forced on them).
    Only if they want turn emails, do not have the game open, and have not been emailed since their last move."""
    _emailed.discard((game.id, mover))
    if game.mode != "two_player" or game.status != "active":
        return None
    state = play.build(game)
    decision = state.decision
    if decision is None or decision.seat == mover or state.result:
        return None
    seat = next((s for s in game.seats if s.index == decision.seat), None)
    other = next((s for s in game.seats if s.index == mover), None)
    if seat is None or other is None or seat.index in hub.connected_seats(game.id) or (game.id, seat.index) in _emailed:
        return None
    user = db.get(User, seat.user_id)
    if user is None or user.disabled or not user.turn_emails:
        return None
    _emailed.add((game.id, seat.index))
    them, link = other.display_name, mail.link(f"/games/{game.id}")
    if state.turn != turn_before and state.active != active_before:
        subject = f"Your turn: {them} finished their turn"
        news = f"{them} has finished their turn in your game of Captain's Chair. It is your turn now:"
    else:
        subject = f"{them} needs a decision from you"
        news = f"{them}'s move in your game of Captain's Chair needs a decision from you:\n\n  {decision.prompt}\n\nAnswer it here:"
    body = (f"Hello {user.display_name},\n\n{news}\n{link}\n\n"
            f"To stop these emails, turn them off on your Account page: {mail.link('/account')}\n")
    return user.email, subject, body


@router.post("/{game_id}/commands")
async def command(game_id: str, body: CommandRequest, background: BackgroundTasks, db: Session = Depends(get_db),
                  viewer: str = Depends(viewer_id)) -> dict:
    game = load_game(db, game_id)
    seat = seat_or_403(game, viewer)
    if game.status != "active":
        raise HTTPException(409, "The game is not in progress")
    before = play.build(game)
    turn_before, active_before = before.turn, before.active
    try:
        play.apply(db, game, seat, body.option)
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    # Sent after the response, so a slow mail server never holds up the move.
    email = waiting_email(db, game, seat, turn_before, active_before)
    if email:
        background.add_task(mail.send, *email)
    return play.view(game, seat)


@router.post("/{game_id}/dev")
async def dev_command(game_id: str, body: DevCommand, db: Session = Depends(get_db),
                      viewer: str = Depends(viewer_id)) -> dict:
    """Developer panel: only when DEV_TOOLS is on."""
    if not get_settings().dev_tools:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Developer tools are off")
    game = load_game(db, game_id)
    seat = seat_or_403(game, viewer)
    if game.status != "active":
        raise HTTPException(409, "The game is not in progress")
    try:
        play.apply_dev(db, game, seat, body.model_dump(exclude_none=True))
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    return play.view(game, seat)


@router.post("/{game_id}/undo")
async def undo(game_id: str, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    game = load_game(db, game_id)
    seat = seat_or_403(game, viewer)
    try:
        play.undo(db, game, seat)
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    return play.view(game, seat)


@router.post("/{game_id}/bugs", status_code=status.HTTP_201_CREATED)
def report_bug(game_id: str, body: BugReportRequest, db: Session = Depends(get_db),
               viewer: str = Depends(viewer_id)) -> dict:
    """A seated player reports a bug. The report keeps the game's setup, seed and commands, so it can be recreated
    even after the game moves on or is deleted (REQ-BUG-01 to -04)."""
    game = load_game(db, game_id)
    seat = seat_or_403(game, viewer)
    if game.seed is None:
        raise HTTPException(409, "The game has not started yet")
    description = body.description.strip()
    if not description:
        raise HTTPException(422, "Describe what you saw")
    name = next(s.display_name for s in game.seats if s.index == seat)
    report = BugReport(game_id=game.id, seat=seat, reporter=name, description=description, kind=body.kind,
                       user_id=viewer, bundle=bugs.bundle(game, seat))
    db.add(report)
    db.commit()
    return {"id": report.id}
