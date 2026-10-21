from __future__ import annotations

import asyncio
import json

import anyio
import pytest
from fastapi.testclient import TestClient

from didik_live.game.room import JoinError

from .conftest import sample_id
from .roomkit import connection, open_room, settle, until


def run(coro):
    return asyncio.run(coro)


def test_children_get_a_suggested_name_unless_the_host_allows_typing() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        conn, _ = connection()
        typed = room.join(conn, {"name": "Aminah binti Ali", "avatar": "penyu"})
        assert typed.nickname.startswith("Penyu ")  # replaced by a suggestion
        kept = room.join(connection()[0], {"name": "Kancil Ceria", "avatar": "kancil"})
        assert kept.nickname == "Kancil Ceria"
        twin = room.join(connection()[0], {"name": "Kancil Ceria", "avatar": "kancil"})
        assert twin.nickname == "Kancil Ceria 2"

        room.settings.custom_names = True
        assert room.join(connection()[0], {"name": "  Aminah  ", "avatar": "gajah"}).nickname == "Aminah"
        for rude in ("b0d0h", "babi", "Fuuuck", "x"):
            with pytest.raises(JoinError):
                room.join(connection()[0], {"name": rude})
        room.close()

    run(scenario())


def test_locked_full_and_waiting_rooms() -> None:
    async def scenario() -> None:
        room = open_room("lumba", max_players=2, waiting_room=True)
        first = room.join(connection()[0], {"avatar": "kancil"})
        assert not first.approved
        conn, socket = connection()
        room.attach_host(conn)
        await settle()
        assert [p["approved"] for p in socket.of("roster")[-1]["players"]] == [False]

        room.approve(first.id, True)
        assert first.approved
        room.join(connection()[0], {"avatar": "gajah"})
        with pytest.raises(JoinError, match="penuh"):
            room.join(connection()[0], {"avatar": "penyu"})

        room.settings.max_players = 10
        room.locked = True
        with pytest.raises(JoinError, match="mengunci"):
            room.join(connection()[0], {"avatar": "penyu"})
        room.close()

    run(scenario())


def test_a_reconnecting_phone_gets_its_place_back_but_a_second_tab_is_a_new_child() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        conn, _ = connection()
        player = room.join(conn, {"avatar": "kancil"})
        assert room.rejoin(connection()[0], player.token) is None  # first tab still open

        conn.close()
        await settle(0.05)
        again, socket = connection()
        assert room.rejoin(again, player.token) is player
        await settle()
        assert socket.view()["me"]["id"] == player.id
        room.close()

    run(scenario())


def test_a_whole_boat_race() -> None:
    async def scenario() -> None:
        room = open_room("lumba", question_limit=3)
        host, host_socket = connection()
        room.attach_host(host)
        fast, fast_socket = connection()
        slow, _ = connection()
        ace = room.join(fast, {"avatar": "harimau"})
        dud = room.join(slow, {"avatar": "penyu"})

        assert room.start_game() is None
        mode = room.mode
        for _ in range(3):
            await until(lambda: mode.stage == "question")
            await settle(0.1)
            question = fast_socket.view()["game"]["question"]
            assert "correct" not in json.dumps(question)
            room.handle_player(ace, {"t": "answer", "a": mode.pres.sample_answer(True, mode.rng)})
            room.handle_player(dud, {"t": "answer", "a": mode.pres.sample_answer(False, mode.rng)})
            await until(lambda: mode.stage == "reveal")
            await settle(0.15)
            game = fast_socket.view()["game"]
            assert game["result"]["correct"] is True and game["result"]["points"] >= 60
            assert "reveal" in game
            room.handle_host(host, {"t": "skip"})
            if mode.stage == "standings" or mode.index < 2:
                await until(lambda: mode.stage != "reveal")
                room.handle_host(host, {"t": "skip"})

        await until(lambda: room.phase == "ended")
        await settle()
        results = host_socket.view()["results"]
        assert [row["id"] for row in results["players"]] == [ace.id, dud.id]
        assert ace.score > dud.score > 0  # a wrong answer still paddles forward
        room.close()

    run(scenario())


def test_pausing_freezes_the_clock() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        host, socket = connection()
        room.attach_host(host)
        room.join(connection()[0], {"avatar": "kancil"})
        room.start_game()
        await until(lambda: room.mode.stage == "question")
        room.handle_host(host, {"t": "pause"})
        await settle(0.3)
        clock = socket.view()["game"]["clock"]
        assert clock["paused"] is True and clock["left"] > 0
        left = room.mode.paused_left
        await settle(0.3)
        assert room.mode.paused_left == left
        room.handle_host(host, {"t": "resume"})
        await settle()
        assert socket.view()["game"]["clock"]["paused"] is False
        room.close()

    run(scenario())


def test_bots_play_on_their_own_and_the_host_can_remove_children() -> None:
    async def scenario() -> None:
        room = open_room("lumba", question_limit=3)
        host, _ = connection()
        room.attach_host(host)
        room.handle_host(host, {"t": "bots", "count": 3})
        assert len(room.players) == 3
        kid_conn, kid_socket = connection()
        kid = room.join(kid_conn, {"avatar": "arnab"})
        room.start_game()
        await until(lambda: room.mode.stage == "question")
        bots = [p for p in room.players.values() if p.is_bot]
        await until(lambda: all(b.id in room.mode.answers for b in bots), timeout=15)

        room.handle_host(host, {"t": "kick", "id": kid.id})
        await settle(0.1)
        assert kid.id not in room.players
        assert kid_socket.of("kicked")
        room.handle_host(host, {"t": "bots", "count": 0})
        assert not room.players
        room.close()

    run(scenario())


def test_stickers_are_limited_to_the_set_and_rate() -> None:
    async def scenario() -> None:
        room = open_room("lumba")
        host, socket = connection()
        room.attach_host(host)
        kid = room.join(connection()[0], {"avatar": "kancil"})
        for sticker in ("hati", "hati", "<script>"):
            room.handle_player(kid, {"t": "sticker", "id": sticker})
        await settle(0.1)
        assert [m["sticker"] for m in socket.of("fx") if m.get("kind") == "sticker"] == ["hati"]
        room.close()

    run(scenario())


# ---------------------------------------------------------------- over real sockets


def receive(ws, timeout: float = 4.0) -> dict:
    async def read() -> dict:
        with anyio.fail_after(timeout):
            return await ws._send_rx.receive()

    message = ws.portal.call(read)
    return json.loads(message["text"])


def receive_until(ws, check, timeout: float = 6.0) -> dict:
    while True:
        message = receive(ws, timeout)
        if check(message):
            return message


def test_open_a_room_and_play_over_sockets(parent: TestClient) -> None:
    quiz_id = sample_id(parent, "Sains: Betul atau Salah?")
    opened = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "lumba", "settings": {"question_limit": 3}})
    assert opened.status_code == 201, opened.text
    room = opened.json()
    assert room["link"].endswith(f"/m/{room['slug']}")

    info = parent.get(f"/api/rooms/{room['slug']}").json()
    assert info["code"] == room["code"] and info["accepting"] and info["mode"]["title"] == "Lumba Sampan"
    qr = parent.get(f"/api/rooms/{room['code']}/qr.svg")
    assert qr.status_code == 200 and qr.text.lstrip().startswith("<svg")

    with parent.websocket_connect(f"/ws/{room['code']}") as host:
        host.send_json({"t": "host"})
        assert receive_until(host, lambda m: m["t"] == "welcome")["role"] == "host"
        with parent.websocket_connect(f"/ws/{room['slug']}") as kid:
            kid.send_json({"t": "join", "name": "Gajah Riang", "avatar": "gajah", "colour": "biru"})
            welcome = receive_until(kid, lambda m: m["t"] == "welcome")
            assert welcome["token"]
            view = receive_until(kid, lambda m: m["t"] == "view")["view"]
            assert view["me"]["name"] == "Gajah Riang" and view["phase"] == "lobby"

            kid.send_json({"t": "start"})  # a child cannot start the game
            host.send_json({"t": "start"})
            game = receive_until(kid, lambda m: m["t"] == "view" and m["view"].get("game", {}).get("stage") == "question")
            question = game["view"]["game"]["question"]
            assert question["type"] in ("truefalse", "single")
            answer = True if question["type"] == "truefalse" else question["choices"][0]["id"]
            kid.send_json({"t": "answer", "a": answer})
            receive_until(kid, lambda m: m["t"] == "view" and m["view"]["game"].get("stage") == "reveal")


def test_only_the_parent_who_opened_the_room_can_control_it(parent: TestClient, client: TestClient) -> None:
    quiz_id = sample_id(parent, "Matematik Ceria")
    code = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "lumba"}).json()["code"]
    parent.post("/api/auth/logout")
    with client.websocket_connect(f"/ws/{code}") as ws:
        ws.send_json({"t": "host"})
        assert receive_until(ws, lambda m: m["t"] == "error")["code"] == "not-host"


def test_unknown_rooms_and_foreign_origins(client: TestClient) -> None:
    with client.websocket_connect("/ws/000000") as ws:
        assert receive(ws)["code"] == "no-room"
    assert client.get("/api/rooms/000000").status_code == 404
