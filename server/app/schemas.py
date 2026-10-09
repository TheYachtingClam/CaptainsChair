from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

GameMode = Literal["two_player", "solo", "cadet"]
BoardSide = Literal["basic", "advanced"]
Difficulty = Literal["ensign", "lieutenant", "commander", "captain", "admiral"]
Box = Literal["core", "to_boldly_go", "both"]  # REQ-CORE-10


class LoginRequest(BaseModel):
    password: str


class SeatChoice(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    deck_id: str
    board_side: BoardSide = "basic"


class BotChoice(BaseModel):
    """Solo mode: the Bot to play against (REQ-SRV-18)."""

    deck_id: str
    difficulty: Difficulty = "ensign"
    ticking_clock: bool = False
    conspiracy: bool = False


class CreateGameRequest(SeatChoice):
    mode: GameMode = "two_player"
    box: Box = "to_boldly_go"
    expansions: list[str] = []
    promos: bool = False
    bot: BotChoice | None = None


class CommandRequest(BaseModel):
    option: str


class DevCommand(BaseModel):
    """Developer panel command (engine/dev.py)."""

    kind: Literal["card", "resource", "track", "mark"]
    card: str | None = None
    zone: str | None = None
    resource: str | None = None
    track: str | None = None
    amount: int = 0


class SeatOut(BaseModel):
    index: int
    display_name: str
    deck_id: str
    board_side: BoardSide


class GameSummary(BaseModel):
    id: str
    created_at: datetime
    mode: GameMode
    box: Box = "to_boldly_go"
    expansions: list[str]
    promos: bool
    status: str
    seats: list[SeatOut]
    open_seats: int
    bot: BotChoice | None = None
    campaign_id: str | None = None


class GameView(GameSummary):
    your_seat: int | None = None


class SeatGrant(BaseModel):
    game: GameView
    seat_index: int
    seat_token: str
