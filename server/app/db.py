from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def init_db(url: str | None = None) -> None:
    global _engine, _session_factory
    url = url or get_settings().database_url
    connect_args: dict = {}
    extra: dict = {}
    if url.endswith(":memory:"):
        extra["poolclass"] = StaticPool  # one shared connection, used by tests
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        path = url.removeprefix("sqlite:///")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
    _engine = create_engine(url, connect_args=connect_args, **extra)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)

    from app import models  # noqa: F401  registers tables

    _drop_games_from_before_accounts(_engine)
    Base.metadata.create_all(_engine)
    _add_missing_columns(_engine)


def _drop_games_from_before_accounts(engine: Engine) -> None:
    """Games, seats and campaigns from before accounts were held by secret tokens, not accounts. They are deleted
    once, when a database that still has seat tokens is opened (decision 2026-10-26, plans/users.md); their tables
    are then made afresh. Bug reports are kept: each carries its own copy of its game (REQ-BUG-08)."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if not inspector.has_table("seats") or "token_hash" not in {c["name"] for c in inspector.get_columns("seats")}:
        return
    with engine.begin() as conn:
        for table in ("seats", "games", "campaigns"):
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))


def _add_missing_columns(engine: Engine) -> None:
    """Add columns introduced after a database was created. There is no migration tool yet;
    this only handles new nullable or defaulted columns."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                ddl = column.type.compile(engine.dialect)
                default = f" DEFAULT {column.server_default.arg}" if column.server_default is not None else ""
                conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN "{column.name}" {ddl}{default}'))


def initialised() -> bool:
    return _session_factory is not None


def open_session() -> Session:
    """A database session outside a request, e.g. to check a session cookie (closed by the caller)."""
    assert _session_factory is not None, "init_db() was not called"
    return _session_factory()


def get_db() -> Iterator[Session]:
    assert _session_factory is not None, "init_db() was not called"
    with _session_factory() as session:
        yield session
