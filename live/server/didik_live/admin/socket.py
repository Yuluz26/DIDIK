"""The dashboard's live connection: every event as it happens, and the rooms and children online every few
seconds. It needs the owner's session cookie and the site's own origin; a session that ends (signed out
elsewhere, expired) closes it within half a minute."""

from __future__ import annotations

import asyncio
import contextlib
import json
from datetime import UTC, datetime
from urllib.parse import urlparse

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from ..activity import iso
from . import stats
from .auth import COOKIE, find_session

SNAPSHOT_EVERY = 4.0
RECHECK_EVERY = 30.0
MAX_MESSAGE = 1_000


def _session_alive(ws: WebSocket, token: str | None) -> bool:
    with ws.app.state.db.sessions() as db:
        return find_session(db, token) is not None


async def admin_socket(ws: WebSocket) -> None:
    app = ws.app
    origin = ws.headers.get("origin")
    if not origin or urlparse(origin).netloc != ws.headers.get("host"):
        await ws.close(code=4403)
        return
    token = ws.cookies.get(COOKIE)
    if not await run_in_threadpool(_session_alive, ws, token):
        await ws.close(code=4401)
        return

    await ws.accept()
    bus = app.state.bus
    listener = bus.subscribe()
    names: dict[int, str] = app.state.host_names

    async def snapshot() -> dict:
        wanted = {room.host_id for room in app.state.rooms.by_code.values()}
        if wanted - names.keys():
            def fill() -> None:
                with app.state.db.sessions() as db:
                    stats.host_names(db, wanted, names)

            await run_in_threadpool(fill)
        return {"t": "live"} | stats.live(app.state.rooms, names)

    async def send(message: dict) -> None:
        await ws.send_text(json.dumps(message, separators=(",", ":")))

    async def pump() -> None:
        await send({"t": "hello", "now": iso(datetime.now(UTC))})
        await send(await snapshot())
        checked = asyncio.get_running_loop().time()
        while True:
            try:
                message = await asyncio.wait_for(listener.get(), timeout=SNAPSHOT_EVERY)
                await send(message)
                continue
            except TimeoutError:
                pass
            now = asyncio.get_running_loop().time()
            if now - checked >= RECHECK_EVERY:
                checked = now
                if not await run_in_threadpool(_session_alive, ws, token):
                    await send({"t": "bye"})
                    await ws.close(code=4401)
                    return
            await send(await snapshot())

    async def listen() -> None:
        # The dashboard says nothing that matters; reading is how a closed tab is noticed.
        while True:
            text = await ws.receive_text()
            if len(text) <= MAX_MESSAGE and text == '{"t":"ping"}':
                await send({"t": "pong"})

    tasks = [asyncio.create_task(pump()), asyncio.create_task(listen())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        pass
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError, WebSocketDisconnect, RuntimeError):
                await task
        bus.unsubscribe(listener)
