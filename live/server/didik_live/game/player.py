"""People in a room and their live connections."""

from __future__ import annotations

import asyncio
import contextlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from ..security import token_hash


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
    # The secret a child's device keeps to come back to the same place. Only its hash is kept for
    # longer than the join (and saved with the room), the same way parents' sessions are stored.
    token: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    key: str = ""
    is_bot: bool = False
    approved: bool = True
    joined_at: float = field(default_factory=time.time)
    score: int = 0
    team: str | None = None
    conns: set[Conn] = field(default_factory=set)
    last_sticker: float = 0.0
    skill: float = 0.75  # bots only: how often they answer correctly
    # Where the child stands in the waiting room's square, which way they face, and when they last
    # chose a spot (taps are limited).
    spot: tuple[float, float] = (8.0, 6.5)
    facing: int = 1
    last_walk: float = 0.0
    # When the child was last connected (epoch seconds): after a restart, a game waits for the
    # children who were there a moment ago.
    seen: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.key:
            self.key = token_hash(self.token)

    @property
    def connected(self) -> bool:
        return self.is_bot or any(not c.closed for c in self.conns)

    def owns(self, token: str) -> bool:
        return not self.is_bot and hmac.compare_digest(self.key, token_hash(token))

    def save(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.nickname,
            "avatar": self.avatar,
            "colour": self.colour,
            "skin": self.skin,
            "key": self.key,
            "bot": self.is_bot,
            "approved": self.approved,
            "joined": self.joined_at,
            "score": self.score,
            "team": self.team,
            "skill": self.skill,
            "spot": list(self.spot),
            "facing": self.facing,
            "seen": time.time() if self.connected else self.seen,
        }

    @classmethod
    def restore(cls, data: dict[str, Any]) -> Player:
        return cls(
            id=data["id"],
            nickname=data["name"],
            avatar=data["avatar"],
            colour=data["colour"],
            skin=data["skin"],
            token="",
            key=data["key"],
            is_bot=data["bot"],
            approved=data["approved"],
            joined_at=data["joined"],
            score=data["score"],
            team=data["team"],
            skill=data["skill"],
            spot=(data["spot"][0], data["spot"][1]),
            facing=data["facing"],
            seen=data["seen"],
        )

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
