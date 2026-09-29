from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import content
from app.auth import hash_seat_token, new_seat_token, require_session
from app.db import get_db
from app.hub import hub
from app.models import Game, Seat
from app.schemas import CreateGameRequest, GameSummary, GameView, SeatChoice, SeatGrant, SeatOut

router = APIRouter(prefix="/api/games", tags=["games"], dependencies=[Depends(require_session)])

SEATS_BY_MODE = {"two_player": 2, "solo": 1, "cadet": 1}


def seat_count(game: Game) -> int:
    return SEATS_BY_MODE[game.mode]


def summarize(game: Game) -> dict:
    return {
        "id": game.id,
        "created_at": game.created_at,
        "mode": game.mode,
        "expansions": game.expansions,
        "status": game.status,
        "seats": [SeatOut.model_validate(s, from_attributes=True) for s in game.seats],
        "open_seats": seat_count(game) - len(game.seats),
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


def validate_deck(deck_id: str, expansions: list[str]) -> None:
    if deck_id not in content.deck_ids_for(expansions):
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
        game.status = "ready"
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
    validate_deck(body.deck_id, body.expansions)
    game = Game(mode=body.mode, expansions=body.expansions)
    db.add(game)
    seat, token = add_seat(db, game, body)
    return {"game": {**summarize(game), "your_seat": seat.index}, "seat_index": seat.index, "seat_token": token}


@router.post("/{game_id}/join", response_model=SeatGrant)
async def join_game(game_id: str, body: SeatChoice, db: Session = Depends(get_db)) -> dict:
    game = load_game(db, game_id)
    if len(game.seats) >= seat_count(game):
        raise HTTPException(status.HTTP_409_CONFLICT, "This game is full")
    validate_deck(body.deck_id, game.expansions)
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
