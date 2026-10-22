"""Restarting the server does not end a room: every game is saved mid-play and carries on from there."""

from __future__ import annotations

import asyncio
import json
import random
import sqlite3
import zlib
from typing import Any

import pytest
from fastapi.testclient import TestClient

from didik_live.app import create_app
from didik_live.config import Settings
from didik_live.game.manager import RoomManager
from didik_live.game.modes import MODES
from didik_live.game.player import dumps
from didik_live.game import room as room_module
from didik_live.game.room import Room
from didik_live.seed import DEMO_EMAIL, DEMO_PASSWORD

from .conftest import sample_id
from .roomkit import connection, open_room, settle, until
from .test_rooms import receive_until


def run(coro):
    return asyncio.run(coro)


def json_roundtrip(data: dict[str, Any]) -> dict[str, Any]:
    return json.loads(dumps(data))


def comparable(saved: dict[str, Any]) -> dict[str, Any]:
    """A saved room without what is allowed to differ after a restart: the save time, when each
    child was last seen, and whether the clock is paused (a restored game waits for the children)."""
    saved = json.loads(json.dumps(saved))
    saved.pop("saved")
    for player in saved["players"]:
        player.pop("seen")
    if saved["game"]:
        saved["game"].pop("paused")
    return saved


async def play_a_little(room: Room, child: Any, rng: random.Random) -> None:
    """A few seconds of a real game: the child answers (right), bots play, sync games move on."""
    mode = room.mode
    if mode.pace == "sync":
        for _ in range(2):
            await until(lambda: room.mode.stage == "question")
            room.mode.act_answer(child, room.mode.pres.sample_answer(True, rng))
            await until(lambda: child.id in room.mode.answers)
            room.mode.skip()  # to the reveal: scores land
            await until(lambda: room.mode.stage != "question")
            room.mode.skip()  # and on to the next question
        await until(lambda: room.mode.stage == "question")
        room.mode.act_answer(child, room.mode.pres.sample_answer(True, rng))
    else:
        await until(lambda: room.mode.stage == "play")
        seat = room.mode.seats[child.id]
        if seat.step == "question":
            room.mode.act_answer(child, seat.pres.sample_answer(True, rng))
            if seat.step not in ("question", "result"):
                room.mode.bot_step(child, seat)  # dig, open a chest, drop a block...
        await settle(1.5)  # the bots answer and act meanwhile


@pytest.mark.parametrize("key", list(MODES))
def test_a_game_saved_mid_play_comes_back_where_it_was_and_still_finishes(key: str) -> None:
    async def scenario() -> None:
        rng = random.Random(7)
        title = "Sains: Betul atau Salah?" if key == "lompat" else "Haiwan di Malaysia"
        room = open_room(key, title, minutes=3)
        room.set_bots(5)
        conn, _ = connection()
        child = room.join(conn, {"avatar": "kancil"})
        assert room.start_game() is None
        await play_a_little(room, child, rng)

        before = json_roundtrip(room.save())
        room.suspend()
        assert before["phase"] == "playing" and before["game"]["stage"] != "intro"
        assert child.token not in json.dumps(before)  # only the token's hash is kept

        again = Room.restore(RoomManager(), before)
        assert comparable(again.save()) == comparable(before)
        again.carry_on(saved_at=before["saved"], host_paused=False)
        assert again.mode.paused  # waiting for the child who was playing
        assert again.base_view()["resuming"]

        await settle(0.6)
        assert again.mode.paused
        back = again.rejoin(connection()[0], child.token)
        assert back is not None and back.id == child.id and back.score == child.score
        await until(lambda: not again.mode.paused, timeout=2)
        assert "resuming" not in again.base_view()

        # The restored game runs on to its end.
        for _ in range(80):
            if again.phase == "ended":
                break
            again.mode.skip()
            await settle(0.1)
        assert again.phase == "ended"
        assert child.id in [row["id"] for row in again.results["players"]]
        again.close()

    run(scenario())


def test_a_game_the_host_paused_stays_paused_after_a_restart() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        conn, _ = connection()
        child = room.join(conn, {"avatar": "kancil"})
        room.start_game()
        await until(lambda: room.mode.stage == "question")
        room.handle_host(connection()[0], {"t": "pause"})
        left = room.mode.time_left()
        saved = json_roundtrip(room.save())
        room.suspend()

        again = Room.restore(RoomManager(), saved)
        again.carry_on(saved_at=saved["saved"], host_paused=saved["game"]["paused"])
        again.rejoin(connection()[0], child.token)
        await settle(0.5)
        assert again.mode.paused and again.mode.time_left() == pytest.approx(left, abs=0.05)
        host, _ = connection()
        again.handle_host(host, {"t": "resume"})
        assert not again.mode.paused
        again.close()

    run(scenario())


def test_after_a_restart_the_game_does_not_wait_for_ever(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(room_module, "RESTART_GRACE", 0.5)

    async def scenario() -> None:
        room = open_room("kebun")
        conn, _ = connection()
        room.join(conn, {"avatar": "kancil"})
        room.start_game()
        await until(lambda: room.mode.stage == "play")
        saved = json_roundtrip(room.save())
        room.suspend()

        again = Room.restore(RoomManager(), saved)
        again.carry_on(saved_at=saved["saved"], host_paused=False)
        assert again.mode.paused
        await until(lambda: not again.mode.paused, timeout=1.5)  # the child never came back
        again.close()

    run(scenario())


def test_a_game_saved_by_another_version_comes_back_in_the_lobby_with_everyone() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        conn, _ = connection()
        child = room.join(conn, {"avatar": "kancil"})
        room.start_game()
        await until(lambda: room.mode.stage == "question")
        saved = json_roundtrip(room.save())
        room.suspend()
        saved["v"] = 0

        again = Room.restore(RoomManager(), saved)
        again.carry_on(saved_at=saved["saved"], host_paused=False)
        assert again.phase == "lobby" and again.mode is None
        assert again.rejoin(connection()[0], child.token) is not None
        assert "tidak dapat disambung" in again.base_view()["feed"][-1]["text"]
        assert again.start_game() is None
        again.close()

    run(scenario())


# ---------------------------------------------------------------- the whole server, stopped and started


def saved_rooms(settings: Settings) -> dict[str, dict[str, Any]]:
    with sqlite3.connect(settings.data_dir / "test.db") as db:
        rows = db.execute("select code, state from live_rooms").fetchall()
    return {code: json.loads(zlib.decompress(state)) for code, state in rows}


def test_restarting_the_server_keeps_rooms_and_children_rejoin_their_game(settings: Settings) -> None:
    with TestClient(create_app(settings)) as parent:
        parent.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        quiz_id = sample_id(parent, "Sains: Betul atau Salah?")
        room = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "lumba", "settings": {"question_limit": 3}}).json()
        with parent.websocket_connect(f"/ws/{room['code']}") as host:
            host.send_json({"t": "host"})
            receive_until(host, lambda m: m["t"] == "welcome")
            with parent.websocket_connect(f"/ws/{room['slug']}") as kid:
                kid.send_json({"t": "join", "name": "Gajah Riang", "avatar": "gajah", "colour": "biru"})
                welcome = receive_until(kid, lambda m: m["t"] == "welcome")
                host.send_json({"t": "start"})
                game = receive_until(kid, lambda m: m["t"] == "view" and m["view"].get("game", {}).get("stage") == "question")
                question = game["view"]["game"]["question"]
                kid.send_json({"t": "answer", "a": True if question["type"] == "truefalse" else question["choices"][0]["id"]})
                receive_until(kid, lambda m: m["t"] == "view" and m["view"]["game"].get("answered"))
        # Leaving the block stops the server the way a restart does.

    saved = saved_rooms(settings)
    assert list(saved) == [room["code"]]
    assert saved[room["code"]]["phase"] == "playing"
    assert welcome["token"] not in json.dumps(saved)

    with TestClient(create_app(settings)) as parent:
        parent.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        assert parent.get(f"/api/rooms/{room['slug']}").json()["phase"] == "playing"
        assert [r["code"] for r in parent.get("/api/rooms/mine").json()["rooms"]] == [room["code"]]
        with parent.websocket_connect(f"/ws/{room['slug']}") as kid:
            kid.send_json({"t": "hello", "token": welcome["token"]})
            back = receive_until(kid, lambda m: m["t"] == "welcome")
            assert back["id"] == welcome["id"] and back["token"] == welcome["token"]
            view = receive_until(kid, lambda m: m["t"] == "view")["view"]
            assert view["me"]["name"] == "Gajah Riang" and view["phase"] == "playing"
            assert view["game"]["answered"] and view["game"]["question"]["prompt"] == question["prompt"]
            # With the only child back, the game is no longer paused.
            receive_until(kid, lambda m: m["t"] == "view" and not m["view"]["game"]["clock"]["paused"])
            with parent.websocket_connect(f"/ws/{room['code']}") as host:
                host.send_json({"t": "host"})
                assert receive_until(host, lambda m: m["t"] == "welcome")["role"] == "host"
                host.send_json({"t": "end"})
                receive_until(kid, lambda m: m["t"] == "view" and m["view"]["phase"] == "ended")


def test_a_closed_room_is_not_saved_any_more(settings: Settings) -> None:
    with TestClient(create_app(settings)) as parent:
        parent.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        quiz_id = sample_id(parent, "Matematik Ceria")
        first = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "lumba"}).json()
        second = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "kebun"}).json()
        rooms = parent.app.state.rooms
        parent.portal.call(rooms.save)
        assert set(saved_rooms(settings)) == {first["code"], second["code"]}

        rooms.close(rooms.find(first["code"]))
        parent.portal.call(rooms.save)
        assert set(saved_rooms(settings)) == {second["code"]}

    with TestClient(create_app(settings)) as client:
        assert client.get(f"/api/rooms/{first['code']}").status_code == 404
        assert client.get(f"/api/rooms/{second['code']}").json()["phase"] == "lobby"
