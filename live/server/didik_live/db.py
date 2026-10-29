"""Database engine and sessions. SQLite on localhost; any SQLAlchemy URL (PostgreSQL) in production."""

from __future__ import annotations

from collections.abc import Iterator

import logging

from sqlalchemy import Engine, create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


log = logging.getLogger("didik.db")


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    is_sqlite = url.startswith("sqlite")
    engine = create_engine(url, connect_args={"check_same_thread": False} if is_sqlite else {})

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _record) -> None:  # pragma: no cover - driver hook
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine


class Database:
    def __init__(self, url: str) -> None:
        self.engine = make_engine(url)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_all(self) -> None:
        # Importing the models registers their tables on Base.metadata.
        from . import models  # noqa: F401

        Base.metadata.create_all(self.engine)
        self.add_missing_columns()

    def add_missing_columns(self) -> None:
        """`create_all` makes whole tables only. A column a newer version put on a table that already
        exists (a server upgraded in place) is added here; only columns that may be empty qualify."""
        inspector = inspect(self.engine)
        with self.engine.begin() as connection:
            for table in Base.metadata.sorted_tables:
                if not inspector.has_table(table.name):
                    continue
                have = {column["name"] for column in inspector.get_columns(table.name)}
                for column in table.columns:
                    if column.name in have:
                        continue
                    if not column.nullable:
                        log.error("Lajur %s.%s tiada dan tidak boleh ditambah sendiri.", table.name, column.name)
                        continue
                    kind = column.type.compile(self.engine.dialect)
                    connection.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {kind}'))
                    log.warning("Lajur %s.%s ditambah.", table.name, column.name)

    def session(self) -> Iterator[Session]:
        with self.sessions() as session:
            yield session
