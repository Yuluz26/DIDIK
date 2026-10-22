"""Saved rooms, one database row each, so that restarting the server does not end a class's game.

Writing happens in a worker thread: the room's JSON is made on the event loop (where rooms change) and
handed over as text, then compressed and written here.
"""

from __future__ import annotations

import json
import logging
import zlib
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from ..db import Database
from ..models import LiveRoom

log = logging.getLogger("didik.rooms")


class RoomStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def load(self) -> list[dict[str, Any]]:
        """Every saved room. A row that cannot be read is dropped."""
        rooms: list[dict[str, Any]] = []
        broken: list[str] = []
        with self.database.sessions() as db:
            for row in db.scalars(select(LiveRoom)):
                try:
                    rooms.append(json.loads(zlib.decompress(row.state)))
                except (zlib.error, ValueError):
                    log.warning("saved room %s could not be read", row.code)
                    broken.append(row.code)
            if broken:
                db.execute(delete(LiveRoom).where(LiveRoom.code.in_(broken)))
                db.commit()
        return rooms

    def write(self, rooms: list[tuple[str, int, str]], gone: set[str]) -> None:
        """Saves (code, host id, JSON) for each room and deletes the rows of rooms that closed."""
        rows = [LiveRoom(code=code, host_id=host, state=zlib.compress(text.encode(), 6)) for code, host, text in rooms]
        with self.database.sessions() as db:
            if gone:
                db.execute(delete(LiveRoom).where(LiveRoom.code.in_(gone)))
                db.commit()
            for row in rows:
                db.merge(row)
            try:
                db.commit()
                return
            except SQLAlchemyError:
                db.rollback()
        # One bad row (its host's account was just deleted) must not stop the others being saved.
        for row in rows:
            with self.database.sessions() as db:
                try:
                    db.merge(row)
                    db.commit()
                except SQLAlchemyError:
                    log.warning("room %s could not be saved", row.code)
