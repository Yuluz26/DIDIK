"""All live rooms of this process, found by six-digit code or by word link."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import random
import time
from typing import Any

from . import names
from .room import Room
from .settings import RoomSettings

log = logging.getLogger("didik.rooms")

MAX_ROOMS_PER_HOST = 5
IDLE_EMPTY_SECONDS = 20 * 60
MAX_AGE_SECONDS = 8 * 3600


class RoomManager:
    def __init__(self, allow_bots: bool = True) -> None:
        self.by_code: dict[str, Room] = {}
        self.by_slug: dict[str, Room] = {}
        self.allow_bots = allow_bots
        self._rng = random.SystemRandom()
        self._janitor: asyncio.Task | None = None

    def create(
        self,
        *,
        host_id: int,
        quiz_id: int,
        quiz_title: str,
        questions: list[Any],
        mode_key: str,
        settings: RoomSettings,
    ) -> Room:
        mine = sorted(self.rooms_of(host_id), key=lambda r: r.created)
        for old in mine[: max(0, len(mine) - MAX_ROOMS_PER_HOST + 1)]:
            self.close(old, "Hos telah membuka bilik baharu.")

        code = names.room_code(self._rng)
        while code in self.by_code:
            code = names.room_code(self._rng)
        slug = names.room_slug(self._rng)
        while slug in self.by_slug:
            slug = names.room_slug(self._rng)

        room = Room(
            self,
            code=code,
            slug=slug,
            host_id=host_id,
            quiz_id=quiz_id,
            quiz_title=quiz_title,
            questions=questions,
            mode_key=mode_key,
            settings=settings,
            allow_bots=self.allow_bots,
        )
        self.by_code[code] = room
        self.by_slug[slug] = room
        room.start()
        return room

    def find(self, key: str) -> Room | None:
        key = (key or "").strip().lower()
        return self.by_code.get(key) or self.by_slug.get(key)

    def rooms_of(self, host_id: int) -> list[Room]:
        return [room for room in self.by_code.values() if room.host_id == host_id]

    def close(self, room: Room, message: str = "Bilik ini sudah ditutup.") -> None:
        self.by_code.pop(room.code, None)
        self.by_slug.pop(room.slug, None)
        room.close(message)

    def start_janitor(self) -> None:
        if self._janitor is None:
            self._janitor = asyncio.create_task(self._sweep_forever())

    async def _sweep_forever(self) -> None:
        while True:
            await asyncio.sleep(30)
            with contextlib.suppress(Exception):
                self.sweep()

    def sweep(self) -> None:
        now = time.time()
        for room in list(self.by_code.values()):
            empty_too_long = not room.has_people() and room.idle_for() > IDLE_EMPTY_SECONDS
            if empty_too_long or now - room.created > MAX_AGE_SECONDS:
                log.info("closing room %s", room.code)
                self.close(room, "Bilik ini tamat tempoh.")

    async def shutdown(self) -> None:
        if self._janitor is not None:
            self._janitor.cancel()
        for room in list(self.by_code.values()):
            self.close(room, "Pelayan sedang dimulakan semula. Masuk semula sebentar lagi.")
