"""Helpers for driving a room directly, without a browser or a real socket."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from didik_live.game.manager import RoomManager
from didik_live.game.player import Conn
from didik_live.game.room import Room
from didik_live.game.settings import RoomSettings
from didik_live.questions import parse_questions
from didik_live.seed import SAMPLES


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []
        self.closed = False

    async def send_text(self, text: str) -> None:
        self.sent.append(json.loads(text))

    async def close(self, code: int = 1000) -> None:
        self.closed = True

    def views(self) -> list[dict[str, Any]]:
        return [m["view"] for m in self.sent if m.get("t") == "view"]

    def view(self) -> dict[str, Any]:
        views = self.views()
        assert views, f"no view yet; got {[m.get('t') for m in self.sent]}"
        return views[-1]

    def of(self, kind: str) -> list[dict[str, Any]]:
        return [m for m in self.sent if m.get("t") == kind]


def connection() -> tuple[Conn, FakeSocket]:
    socket = FakeSocket()
    conn = Conn(socket)  # type: ignore[arg-type]
    conn.start()
    return conn, socket


def sample(title: str) -> list[Any]:
    for quiz in SAMPLES:
        if quiz["title"] == title:
            return parse_questions(quiz["questions"])
    raise KeyError(title)


def open_room(mode: str, title: str = "Haiwan di Malaysia", **settings: Any) -> Room:
    manager = RoomManager()
    return manager.create(
        host_id=1,
        quiz_id=1,
        quiz_title=title,
        questions=sample(title),
        mode_key=mode,
        settings=RoomSettings(**({"shuffle": False} | settings)),
    )


async def settle(seconds: float = 0.25) -> None:
    await asyncio.sleep(seconds)


async def until(check: Any, timeout: float = 6.0) -> None:
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    while loop.time() < end:
        if check():
            return
        await asyncio.sleep(0.02)
    raise AssertionError("condition not reached in time")
