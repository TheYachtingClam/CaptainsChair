from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

GameMode = Literal["two_player", "solo", "cadet"]
BoardSide = Literal["basic", "advanced"]


class LoginRequest(BaseModel):
    password: str


class SeatChoice(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    deck_id: str
    board_side: BoardSide = "basic"


class CreateGameRequest(SeatChoice):
    mode: GameMode = "two_player"
    expansions: list[str] = []
    promos: bool = False


class SeatOut(BaseModel):
    index: int
    display_name: str
    deck_id: str
    board_side: BoardSide


class GameSummary(BaseModel):
    id: str
    created_at: datetime
    mode: GameMode
    expansions: list[str]
    promos: bool
    status: str
    seats: list[SeatOut]
    open_seats: int


class GameView(GameSummary):
    your_seat: int | None = None


class SeatGrant(BaseModel):
    game: GameView
    seat_index: int
    seat_token: str
