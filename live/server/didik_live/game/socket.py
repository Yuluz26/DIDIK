"""The WebSocket every host screen and every child's device keeps open.

First message decides who you are:
  {"t": "host"}                      the parent who opened the room (signed-in cookie)
  {"t": "hello", "token": "..."}     a child coming back (same device, same place)
  {"t": "join", "name", "avatar", "colour"}   a child joining for the first time
After that, messages go to the room as host controls or game actions.
"""

from __future__ import annotations

import json
from urllib.parse import urlparse

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from ..deps import SESSION_COOKIE, user_from_token
from .player import Conn, Player
from .room import JoinError, Room

MAX_MESSAGE = 8_000


def _same_origin(ws: WebSocket) -> bool:
    origin = ws.headers.get("origin")
    if not origin:
        return True  # not a browser (tests, tools); cookies still decide what a host may do
    return urlparse(origin).netloc == ws.headers.get("host")


async def _host_user_id(ws: WebSocket) -> int | None:
    token = ws.cookies.get(SESSION_COOKIE)
    if not token:
        return None

    def lookup() -> int | None:
        with ws.app.state.db.sessions() as db:
            user = user_from_token(db, token)
            return user.id if user else None

    return await run_in_threadpool(lookup)


async def room_socket(ws: WebSocket, key: str) -> None:
    if not _same_origin(ws):
        await ws.close(code=4403)
        return

    await ws.accept()
    room: Room | None = ws.app.state.rooms.find(key)
    if room is None:
        await ws.send_text(json.dumps({"t": "error", "code": "no-room", "message": "Bilik tidak dijumpai atau sudah tamat."}))
        await ws.close(code=4404)
        return

    conn = Conn(ws)
    conn.start()
    role: str | None = None
    player: Player | None = None
    ip = ws.client.host if ws.client else "unknown"

    try:
        while True:
            text = await ws.receive_text()
            if len(text) > MAX_MESSAGE or not conn.allow():
                continue
            try:
                msg = json.loads(text)
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            kind = msg.get("t")

            if role is None:
                if kind == "ping":
                    conn.send({"t": "pong"})
                elif kind == "host":
                    if await _host_user_id(ws) == room.host_id:
                        role = "host"
                        room.attach_host(conn)
                        conn.send({"t": "welcome", "role": "host"})
                    else:
                        conn.send({"t": "error", "code": "not-host", "message": "Hanya ibu bapa yang membuka bilik ini boleh mengawalnya."})
                elif kind == "hello":
                    player = room.rejoin(conn, str(msg.get("token") or ""))
                    if player is None:
                        conn.send({"t": "rejoin-failed"})
                    else:
                        role = "player"
                        conn.send({"t": "welcome", "role": "player", "id": player.id, "token": player.token})
                elif kind == "join":
                    if not ws.app.state.limiter.hit(f"join:{ip}", 30, 60):
                        conn.send({"t": "error", "code": "slow-down", "message": "Terlalu banyak cubaan. Tunggu sebentar."})
                        continue
                    try:
                        player = room.join(conn, msg)
                    except JoinError as error:
                        conn.send({"t": "error", "code": error.code, "message": error.message})
                        continue
                    role = "player"
                    conn.send({"t": "welcome", "role": "player", "id": player.id, "token": player.token})
                continue

            if role == "host":
                room.handle_host(conn, msg)
            elif player is not None:
                if player.id not in room.players:
                    break  # removed by the host
                room.handle_player(player, msg)
    except WebSocketDisconnect:
        pass
    finally:
        conn.close()
        room.detach(conn)
