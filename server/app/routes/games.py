from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import content, play
from app.config import get_settings
from app.auth import hash_seat_token, new_seat_token, require_session
from app.db import get_db
from app.hub import hub
from app.models import Game, Seat
from app.schemas import CommandRequest, DevCommand, CreateGameRequest, GameSummary, GameView, SeatChoice, SeatGrant, SeatOut

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


def seat_for_token(game: Game, token: str | None) -> Seat | None:
    if not token:
        return None
    token_hash = hash_seat_token(token)
    return next((s for s in game.seats if s.token_hash == token_hash), None)


def load_game(db: Session, game_id: str) -> Game:
    game = db.scalar(select(Game).where(Game.id == game_id).options(selectinload(Game.seats)))
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Game not found")
    return game


def validate_deck(deck_id: str, expansions: list[str], box: str = content.DEFAULT_BOX) -> None:
    if deck_id not in content.deck_ids_for(expansions, box):
        raise HTTPException(422, "That Crew deck is not available in this game")


def add_seat(db: Session, game: Game, choice: SeatChoice) -> tuple[Seat, str]:
    token = new_seat_token()
    seat = Seat(
        index=len(game.seats),
        display_name=choice.display_name.strip(),
        deck_id=choice.deck_id,
        board_side=choice.board_side,
        token_hash=hash_seat_token(token),
    )
    game.seats.append(seat)
    if len(game.seats) >= seat_count(game):
        try:
            play.start(game)  # the game starts as soon as every seat is filled
        except play.SetupError as err:
            raise HTTPException(422, str(err)) from err
    db.commit()
    db.refresh(game)
    return seat, token


@router.get("", response_model=list[GameSummary])
def list_games(db: Session = Depends(get_db)) -> list[dict]:
    games = db.scalars(select(Game).options(selectinload(Game.seats)).order_by(Game.created_at.desc())).all()
    return [summarize(g) for g in games]


@router.post("", response_model=SeatGrant, status_code=status.HTTP_201_CREATED)
def create_game(body: CreateGameRequest, db: Session = Depends(get_db)) -> dict:
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
        bot = body.bot.model_dump()
    game = Game(mode=body.mode, box=body.box, expansions=body.expansions, promos=body.promos, bot=bot)
    db.add(game)
    seat, token = add_seat(db, game, body)
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index, "seat_token": token}


@router.post("/{game_id}/join", response_model=SeatGrant)
async def join_game(game_id: str, body: SeatChoice, db: Session = Depends(get_db)) -> dict:
    game = load_game(db, game_id)
    if len(game.seats) >= seat_count(game):
        raise HTTPException(status.HTTP_409_CONFLICT, "This game is full")
    validate_deck(body.deck_id, game.expansions, game.box)
    if any(s.deck_id == body.deck_id for s in game.seats):
        raise HTTPException(status.HTTP_409_CONFLICT, "Your opponent already chose that Crew deck")
    seat, token = add_seat(db, game, body)
    await hub.broadcast(game.id, {"type": "game_updated"})
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index, "seat_token": token}


@router.get("/{game_id}", response_model=GameView)
def get_game(
    game_id: str,
    db: Session = Depends(get_db),
    x_seat_token: str | None = Header(default=None),
) -> dict:
    game = load_game(db, game_id)
    seat = seat_for_token(game, x_seat_token)
    return {**summarize(game), "your_seat": seat.index if seat else None}


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: str, db: Session = Depends(get_db), x_seat_token: str | None = Header(default=None)) -> None:
    """Delete a game for everyone. Only a player seated in it may do so."""
    game = load_game(db, game_id)
    seat_or_403(game, x_seat_token)
    db.delete(game)
    db.commit()
    play.forget(game_id)
    await hub.broadcast(game_id, {"type": "game_deleted"})


def seat_or_403(game: Game, token: str | None) -> int:
    seat = seat_for_token(game, token)
    if seat is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You have no seat in this game")
    return seat.index


@router.get("/{game_id}/state")
def game_state(game_id: str, db: Session = Depends(get_db), x_seat_token: str | None = Header(default=None)) -> dict:
    game = load_game(db, game_id)
    if game.seed is None:
        raise HTTPException(409, "The game has not started yet")
    seat = seat_for_token(game, x_seat_token)
    return play.view(game, seat.index if seat else None)


@router.post("/{game_id}/commands")
async def command(game_id: str, body: CommandRequest, db: Session = Depends(get_db), x_seat_token: str | None = Header(default=None)) -> dict:
    game = load_game(db, game_id)
    seat = seat_or_403(game, x_seat_token)
    if game.status != "active":
        raise HTTPException(409, "The game is not in progress")
    try:
        play.apply(db, game, seat, body.option)
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    return play.view(game, seat)


@router.post("/{game_id}/dev")
async def dev_command(game_id: str, body: DevCommand, db: Session = Depends(get_db),
                      x_seat_token: str | None = Header(default=None)) -> dict:
    """Developer panel: only when DEV_TOOLS is on."""
    if not get_settings().dev_tools:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Developer tools are off")
    game = load_game(db, game_id)
    seat = seat_or_403(game, x_seat_token)
    if game.status != "active":
        raise HTTPException(409, "The game is not in progress")
    try:
        play.apply_dev(db, game, seat, body.model_dump(exclude_none=True))
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    return play.view(game, seat)


@router.post("/{game_id}/undo")
async def undo(game_id: str, db: Session = Depends(get_db), x_seat_token: str | None = Header(default=None)) -> dict:
    game = load_game(db, game_id)
    seat = seat_or_403(game, x_seat_token)
    try:
        play.undo(db, game, seat)
    except play.IllegalCommand as err:
        raise HTTPException(409, str(err)) from err
    await hub.broadcast(game.id, {"type": "state_changed"})
    return play.view(game, seat)
