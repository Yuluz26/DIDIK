"""People in a room and their live connections."""

from __future__ import annotations

import asyncio
import contextlib
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket


def dumps(data: Any) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


class Conn:
    """One open WebSocket. Messages go through a queue drained by its own task, so one slow
    phone never holds up the rest of the room; a phone that falls too far behind is dropped
    and simply reconnects."""

    QUEUE_LIMIT = 300

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws
        self.queue: asyncio.Queue[str | None] = asyncio.Queue(self.QUEUE_LIMIT)
        self.closed = False
        self.last_view = ""
        self.writer: asyncio.Task | None = None
        # Token bucket for incoming messages.
        self._tokens = 40.0
        self._refill_at = time.monotonic()

    def start(self) -> None:
        self.writer = asyncio.create_task(self._write())

    def send(self, message: dict[str, Any] | str) -> None:
        if self.closed:
            return
        text = message if isinstance(message, str) else dumps(message)
        try:
            self.queue.put_nowait(text)
        except asyncio.QueueFull:
            self.close()

    def allow(self) -> bool:
        now = time.monotonic()
        self._tokens = min(40.0, self._tokens + (now - self._refill_at) * 25)
        self._refill_at = now
        if self._tokens < 1:
            return False
        self._tokens -= 1
        return True

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        with contextlib.suppress(asyncio.QueueFull):
            self.queue.put_nowait(None)

    async def _write(self) -> None:
        try:
            while True:
                text = await self.queue.get()
                if text is None:
                    break
                await self.ws.send_text(text)
        except Exception:  # noqa: BLE001 - a closed socket ends the writer quietly
            pass
        finally:
            self.closed = True
            with contextlib.suppress(Exception):
                await self.ws.close()


@dataclass
class Player:
    id: str
    nickname: str
    avatar: str
    colour: str
    skin: str = "s2"
    token: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    is_bot: bool = False
    approved: bool = True
    joined_at: float = field(default_factory=time.time)
    score: int = 0
    team: str | None = None
    conns: set[Conn] = field(default_factory=set)
    last_sticker: float = 0.0
    skill: float = 0.75  # bots only: how often they answer correctly

    @property
    def connected(self) -> bool:
        return self.is_bot or any(not c.closed for c in self.conns)

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.nickname,
            "avatar": self.avatar,
            "colour": self.colour,
            "skin": self.skin,
            "score": self.score,
            "team": self.team,
            "online": self.connected,
            "bot": self.is_bot,
        }

    def send(self, message: dict[str, Any] | str) -> None:
        for conn in list(self.conns):
            conn.send(message)
