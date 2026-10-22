"""All live rooms of this process, found by six-digit code or by word link.

With a store (the app always has one), rooms are saved every few seconds while they change and once
more when the server stops, and brought back when it starts again: a restart costs a class a few
seconds of reconnecting, not its game.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import random
import time
from typing import Any

from . import names
from .player import dumps
from .room import Room
from .settings import RoomSettings
from .store import RoomStore

log = logging.getLogger("didik.rooms")

MAX_ROOMS_PER_HOST = 5
IDLE_EMPTY_SECONDS = 20 * 60
MAX_AGE_SECONDS = 8 * 3600
SAVE_EVERY = 2.0


class RoomManager:
    def __init__(self, allow_bots: bool = True, store: RoomStore | None = None) -> None:
        self.by_code: dict[str, Room] = {}
        self.by_slug: dict[str, Room] = {}
        self.allow_bots = allow_bots
        self.store = store
        self._rng = random.SystemRandom()
        self._janitor: asyncio.Task | None = None
        self._saver: asyncio.Task | None = None
        self._stopping = asyncio.Event()
        # Rooms closed since the last save, whose rows are deleted with the next write.
        self._gone: set[str] = set()

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
        self._add(room)
        room.start()
        return room

    def _add(self, room: Room) -> None:
        self.by_code[room.code] = room
        self.by_slug[room.slug] = room

    def find(self, key: str) -> Room | None:
        key = (key or "").strip().lower()
        return self.by_code.get(key) or self.by_slug.get(key)

    def rooms_of(self, host_id: int) -> list[Room]:
        return [room for room in self.by_code.values() if room.host_id == host_id]

    def close(self, room: Room, message: str = "Bilik ini sudah ditutup.") -> None:
        self.by_code.pop(room.code, None)
        self.by_slug.pop(room.slug, None)
        if self.store is not None:
            self._gone.add(room.code)
        room.close(message)

    # ------------------------------------------------------------ background work

    def start(self) -> None:
        if self._janitor is None:
            self._janitor = asyncio.create_task(self._sweep_forever())
        if self.store is not None and self._saver is None:
            self._saver = asyncio.create_task(self._save_forever())

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

    async def _save_forever(self) -> None:
        # Stopped by `shutdown` through the event, never cancelled: a write is never cut off halfway.
        while not self._stopping.is_set():
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._stopping.wait(), SAVE_EVERY)
            try:
                await self.save()
            except Exception:  # noqa: BLE001 - a failed save is retried on the next round
                log.exception("saving rooms failed")

    async def save(self, everything: bool = False) -> None:
        """Writes the rooms that changed since their last save, and forgets the rooms that closed."""
        if self.store is None:
            return
        rows: list[tuple[str, int, str]] = []
        revisions: list[tuple[Room, int]] = []
        for room in self.by_code.values():
            if everything or room.revision != room.saved_revision:
                rows.append((room.code, room.host_id, dumps(room.save())))
                revisions.append((room, room.revision))
        gone, self._gone = self._gone, set()
        if not rows and not gone:
            return
        try:
            await asyncio.to_thread(self.store.write, rows, gone)
        except Exception:
            self._gone |= gone
            raise
        for room, revision in revisions:
            room.saved_revision = revision

    async def restore(self) -> int:
        """Brings back the rooms saved before the server stopped. Returns how many came back."""
        if self.store is None:
            return 0
        now = time.time()
        for data in await asyncio.to_thread(self.store.load):
            code = str(data.get("code", "?"))
            if now - float(data.get("created", 0)) > MAX_AGE_SECONDS:
                self._gone.add(code)  # it would have closed by now anyway
                continue
            try:
                room = Room.restore(self, data)
            except Exception:  # noqa: BLE001 - one unreadable room must not keep the others away
                log.warning("room %s could not be restored", code, exc_info=True)
                self._gone.add(code)
                continue
            self._add(room)
            game = data.get("game") or {}
            room.carry_on(saved_at=float(data["saved"]), host_paused=bool(game.get("paused")))
        if self.by_code:
            log.info("restored %d room(s)", len(self.by_code))
        return len(self.by_code)

    async def shutdown(self) -> None:
        if self._janitor is not None:
            self._janitor.cancel()
        self._stopping.set()
        if self._saver is not None:
            await self._saver
        rooms = list(self.by_code.values())
        if self.store is None:
            for room in rooms:
                room.close("Pelayan dimulakan semula dan bilik ini telah tamat.")
            return
        for room in rooms:
            room.suspend()
        try:
            await self.save(everything=True)
        except Exception:  # noqa: BLE001
            log.exception("rooms could not be saved at shutdown")
