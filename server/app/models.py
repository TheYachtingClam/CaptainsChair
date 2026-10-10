import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, text, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    mode: Mapped[str] = mapped_column(String(20))
    expansions: Mapped[list[str]] = mapped_column(JSON, default=list)
    # The box played with: core, to_boldly_go or both (REQ-CORE-10). Older games are To Boldly Go games.
    box: Mapped[str] = mapped_column(String(20), default="to_boldly_go", server_default=text("'to_boldly_go'"))
    # Promo cards are shuffled into their matching common decks at setup when true.
    promos: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    # Which promo sets are in the game (REQ-CORE-13). Null on games saved before promo set 1 existed: promo set 2 only.
    promo_sets: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    # The engine state is rebuilt by replaying commands from the seed (REQ-SRV-14).
    seed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    commands: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    # Solo mode: the Bot's Crew, difficulty and Ticking Clock (REQ-SRV-18). Null for other modes.
    bot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # A Five-Year Mission assignment: {"id": campaign id, "assignment": number, "reinforcement": [card ids],
    # "setup": CampaignSetup fields (Boosts and challenges)}.
    campaign: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="waiting")

    seats: Mapped[list["Seat"]] = relationship(
        back_populates="game", order_by="Seat.index", cascade="all, delete-orphan"
    )


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("game_id", "index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"))
    index: Mapped[int] = mapped_column(Integer)
    display_name: Mapped[str] = mapped_column(String(40))
    deck_id: Mapped[str] = mapped_column(String(40))
    board_side: Mapped[str] = mapped_column(String(10))
    # Only a hash of the seat token is stored (REQ-SRV-30).
    token_hash: Mapped[str] = mapped_column(String(64), index=True)

    game: Mapped[Game] = relationship(back_populates="seats")


class Campaign(Base):
    """A Five-Year Mission (requirements/22-solo-mode.md §14), replacing the paper logbook (REQ-CAMP-50 to -54). It is
    reached through its own secret link: only a hash of the token is stored, like seat tokens."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    token_hash: Mapped[str] = mapped_column(String(64), index=True)
    display_name: Mapped[str] = mapped_column(String(40))
    deck_id: Mapped[str] = mapped_column(String(40))
    mode: Mapped[str] = mapped_column(String(30))
    expansions: Mapped[list[str]] = mapped_column(JSON, default=list)
    box: Mapped[str] = mapped_column(String(20), default="to_boldly_go", server_default=text("'to_boldly_go'"))
    promos: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    promo_sets: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    rank: Mapped[str] = mapped_column(String(20), default="ensign")
    # One row per assignment: number, game_id, date, rank, bot, difficulty, board_side, outcome, scores, upgrade.
    assignments: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    reinforcement: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    challenges: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"))  # §14.4
    boosts: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"))  # REQ-CAMP-30
    status: Mapped[str] = mapped_column(String(20), default="active")


class BugReport(Base):
    """A player's bug report with everything needed to recreate the game (REQ-BUG-01 to -08). It has no foreign key
    to the game, so it outlives a deleted game."""

    __tablename__ = "bug_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    game_id: Mapped[str] = mapped_column(String(36), index=True)
    seat: Mapped[int] = mapped_column(Integer)
    reporter: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open or resolved
    # The setup, the seed and every command so far (REQ-BUG-03), plus what the reporter saw.
    bundle: Mapped[dict] = mapped_column(JSON)
