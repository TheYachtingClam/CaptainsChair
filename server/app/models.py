import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, text, ForeignKey, Integer, String, UniqueConstraint
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
    # Promo cards are shuffled into their matching common decks at setup when true.
    promos: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    # The engine state is rebuilt by replaying commands from the seed (REQ-SRV-14).
    seed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    commands: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
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
