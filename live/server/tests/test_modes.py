"""Each game's rules, driven directly, plus a short all-bots run of every game."""

from __future__ import annotations

import asyncio
import time

import pytest

from didik_live.game.modes import MODES
from didik_live.game.modes import forest as forest_mod
from didik_live.game.modes.picture import TILES

from .roomkit import connection, open_room, sample, settle, until


def run(coro):
    return asyncio.run(coro)


async def started(mode: str, title: str = "Haiwan di Malaysia", kids: int = 2, **settings):
    room = open_room(mode, title, **settings)
    host, host_socket = connection()
    room.attach_host(host)
    players = []
    for index in range(kids):
        conn, socket = connection()
        players.append((room.join(conn, {"avatar": ["kancil", "harimau", "penyu", "gajah"][index % 4]}), socket))
    assert room.start_game() is None
    await until(lambda: room.mode.stage not in ("intro",))
    return room, host, host_socket, players


def answer(room, player, correct: bool) -> None:
    seat = room.mode.seats[player.id]
    room.handle_player(player, {"t": "answer", "a": seat.pres.sample_answer(correct, room.mode.rng)})


# ---------------------------------------------------------------- every game with bots only


@pytest.mark.parametrize("key", list(MODES))
def test_every_game_runs_with_practice_bots_and_ends_with_results(key: str) -> None:
    async def scenario() -> None:
        title = "Sains: Betul atau Salah?" if key == "lompat" else "Haiwan di Malaysia"
        room = open_room(key, title, question_limit=4)
        host, host_socket = connection()
        room.attach_host(host)
        room.handle_host(host, {"t": "bots", "count": 4})
        assert room.start_game() is None
        loop = asyncio.get_running_loop()
        end = loop.time() + 30
        while sum(p.score for p in room.players.values()) == 0 and loop.time() < end:
            await asyncio.sleep(1.0)
            # In the games everyone answers together, scores land at the reveal: move it along once
            # a bot has answered right (a game may give nothing for a wrong answer).
            answers = getattr(room.mode, "answers", None) or {}
            if room.mode.stage == "question" and any(r.outcome.correct for r in answers.values()):
                room.handle_host(host, {"t": "skip"})
        assert room.phase == "playing"
        assert sum(p.score for p in room.players.values()) > 0, f"nobody scored in {key}"
        room.handle_host(host, {"t": "end"})
        await settle()
        results = host_socket.view()["results"]
        assert len(results["players"]) == 4
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Lompat!


def test_jump_wrong_islands_cost_a_heart_and_fish_come_back() -> None:
    async def scenario() -> None:
        room, host, _, ((ace, ace_socket), (dud, _)) = await started("lompat", "Sains: Betul atau Salah?")
        mode = room.mode
        for round_no in range(4):
            await until(lambda: mode.stage == "question")
            truth = mode.pres.reveal()["correct"]
            right = "true" if truth is True else "false" if truth is False else truth[0]
            wrong = next(p["id"] for p in mode.pads() if p["id"] != right)
            room.handle_player(ace, {"t": "pick", "pad": wrong})
            room.handle_player(ace, {"t": "pick", "pad": right})  # changed their mind in time
            room.handle_player(dud, {"t": "pick", "pad": wrong})
            await settle(0.12)
            assert ace_socket.view()["game"]["pond"]["picks"][dud.id] == wrong  # friends' choices are visible
            room.handle_host(host, {"t": "skip"})
            await until(lambda: mode.stage == "reveal")
            room.handle_host(host, {"t": "skip"})
        assert mode.hearts[ace.id] == 3
        assert mode.hearts[dud.id] == 0  # a fish now, still in the game
        assert ace.score > dud.score == 0
        room.close()

    run(scenario())


def test_jump_only_offers_questions_it_can_draw_as_islands() -> None:
    assert MODES["lompat"].unplayable_reason(sample("Bahasa Melayu: Kata dan Ayat")) is None
    accepted = [q for q in sample("Matematik Ceria") if MODES["lompat"].accepts(q)]
    assert {q.type for q in accepted} <= {"truefalse", "single"}
    assert all(len(q.choices) <= 4 for q in accepted if q.type == "single")
    only_text = [q for q in sample("Matematik Ceria") if q.type in ("text", "number", "order")]
    assert "Betul/Salah" in MODES["lompat"].unplayable_reason(only_text)


# ---------------------------------------------------------------- Pulau Harta Karun


def test_treasure_digging_needs_a_right_answer_and_each_patch_once() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, socket), (other, _)) = await started("harta")
        mode = room.mode
        room.handle_player(kid, {"t": "dig", "tile": 0})
        assert mode.seats[kid.id].extra["dug"] == {}

        answer(room, kid, True)
        assert mode.seats[kid.id].step == "dig"
        room.handle_player(kid, {"t": "dig", "tile": 0})
        assert "0" in mode.seats[kid.id].extra["dug"]
        assert mode.seats[kid.id].step == "result"
        room.handle_player(kid, {"t": "next"})
        answer(room, kid, True)
        room.handle_player(kid, {"t": "dig", "tile": 0})  # already dug
        assert mode.seats[kid.id].step == "dig"

        answer(room, other, False)
        assert mode.seats[other.id].step == "result"
        room.close()

    run(scenario())


def test_treasure_parrot_only_steals_from_someone_ahead() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), (rich, _)) = await started("harta")
        rich.score = 400
        found = room.mode.parrot(kid)
        assert found["from"] == rich.id and found["amount"] == 60
        assert (kid.score, rich.score) == (60, 340)
        found = room.mode.parrot(rich)  # nobody ahead: the parrot brings coins instead
        assert found["from"] is None and found["amount"] == 20
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Kampung Kita


def test_village_is_built_together_and_ends_when_complete() -> None:
    async def scenario() -> None:
        room, _, host_socket, ((a, _), (b, _)) = await started("kampung", minutes=2)
        mode = room.mode
        total = sum(mode.costs)
        for i in range(total):
            kid = a if i % 2 else b
            answer(room, kid, True)
            seat = mode.seats[kid.id]
            if seat.extra["tokens"]:
                room.handle_player(kid, {"t": "place", "kind": "wau", "x": 0.5, "y": 0.1})
            room.handle_player(kid, {"t": "next"})
            if room.phase != "playing":
                break
        await until(lambda: room.phase == "ended")
        await settle()
        results = host_socket.view()["results"]
        assert results["kind"] == "coop" and results["complete"]
        assert mode.decor and all(0.80 <= d["y"] <= 0.97 for d in mode.decor)  # kept on the padang
        assert host_socket.view()["results"]["players"][0]["score"] > 0
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Pasukan Warna


def test_teams_capture_only_next_to_their_land_and_pay_two_flags_to_take_from_the_other_team() -> None:
    async def scenario() -> None:
        room, _, _, ((a, a_socket), (b, b_socket)) = await started("pasukan")
        mode = room.mode
        assert {a.team, b.team} == {"harimau", "penyu"}
        tiger, tiger_socket = (a, a_socket) if a.team == "harimau" else (b, b_socket)
        seat = mode.seats[tiger.id]
        seat.extra["flags"] = 10
        seat.step = "capture"

        room.handle_player(tiger, {"t": "capture", "cell": "0,0"})  # far from home
        assert mode.cells["0,0"] is None
        await settle(0.05)
        assert "Pilih petak lain" in tiger_socket.of("error")[-1]["message"]  # told, not ignored
        room.handle_player(tiger, {"t": "capture", "cell": "-2,0"})
        assert mode.cells["-2,0"] == "harimau" and seat.extra["flags"] == 9
        room.handle_player(tiger, {"t": "capture", "cell": "3,0"})  # the other team's base
        assert mode.cells["3,0"] == "penyu"

        mode.cells["-1,0"] = "penyu"
        room.handle_player(tiger, {"t": "capture", "cell": "-1,0"})
        assert mode.cells["-1,0"] == "harimau" and seat.extra["flags"] == 7

        # Each child still has a place by the hexagons they took, not a shared first place.
        ranks = {row["id"]: row["rank"] for row in mode.results()["players"]}
        assert ranks[tiger.id] == 1 and ranks[(b if tiger is a else a).id] == 2
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Teka Gambar


def test_picture_guesses_score_privately_and_the_picture_needs_its_token() -> None:
    async def scenario() -> None:
        room, host, host_socket, ((kid, kid_socket), (other, other_socket)) = await started("teka")
        mode = room.mode
        await until(lambda: mode.stage == "question")
        name = mode.current[2][0]
        assert room.picture(mode.token).startswith(b"<svg")
        assert room.picture("tekaan") is None

        room.handle_player(other, {"t": "guess", "text": "bukan ini"})
        room.handle_player(other, {"t": "guess", "text": name})  # still cooling down
        assert other.id not in mode.guessed
        room.handle_player(kid, {"t": "guess", "text": name.upper()})
        assert mode.guessed[kid.id] == 100 + 60 * TILES
        await settle(0.15)
        assert kid_socket.view()["game"]["picture"]["name"] == mode.current[1]
        assert "name" not in other_socket.view()["game"]["picture"]
        assert "name" not in host_socket.view()["game"]["picture"]

        room.handle_host(host, {"t": "skip"})
        await until(lambda: mode.stage == "reveal")
        assert 1 <= len(mode.shown) <= 4
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Kebun Ajaib


def test_garden_economy() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("kebun")
        mode = room.mode
        g = mode.seats[kid.id].extra
        room.handle_player(kid, {"t": "plant", "plot": 0, "crop": "durian"})
        assert g["plots"][0] is None  # cannot afford yet
        room.handle_player(kid, {"t": "plant", "plot": 0, "crop": "cili"})
        assert g["plots"][0] == {"crop": "cili", "stage": 0} and g["coins"] == 10

        answer(room, kid, True)
        assert g["water"] == 3
        room.handle_player(kid, {"t": "harvest", "plot": 0})
        assert g["plots"][0] is not None  # not ripe
        for _ in range(3):
            room.handle_player(kid, {"t": "water", "plot": 0})
        room.handle_player(kid, {"t": "harvest", "plot": 0})
        assert g["plots"][0] is None and g["coins"] == 45 and kid.score == 35

        room.handle_player(kid, {"t": "buy", "item": "tanah"})
        assert len(g["plots"]) == 6  # 45 coins is not enough
        g["coins"] = 500
        for _ in range(5):
            room.handle_player(kid, {"t": "buy", "item": "tanah"})
        assert len(g["plots"]) == 9
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Hutan Misteri


def test_forest_walls_chests_keys_and_the_gate() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("hutan")
        mode = room.mode
        seat = mode.seats[kid.id]
        assert seat.step == "explore"

        start = list(mode.pos[kid.id])
        room.handle_player(kid, {"t": "move", "dx": -1, "dy": 0})
        await asyncio.sleep(0.5)
        assert mode.pos[kid.id][0] >= 1 + forest_mod.RADIUS - 0.01  # stopped by the border trees
        room.handle_player(kid, {"t": "move", "dx": 0, "dy": 0})
        assert mode.pos[kid.id] != start or start[0] <= 1.31

        chest = forest_mod.CHESTS[0]
        room.handle_player(kid, {"t": "open", "chest": chest["id"]})
        assert seat.step == "explore"  # too far away

        mode.pos[kid.id] = [chest["x"], chest["y"] + 0.8]
        room.handle_player(kid, {"t": "open", "chest": chest["id"]})
        assert seat.step == "question"
        answer(room, kid, False)
        room.handle_player(kid, {"t": "next"})
        room.handle_player(kid, {"t": "open", "chest": chest["id"]})
        assert seat.step == "explore"  # locked for a few seconds after a wrong answer

        seat.extra["locked"].clear()
        room.handle_player(kid, {"t": "open", "chest": chest["id"]})
        answer(room, kid, True)
        assert seat.extra["keys"] == 1 and chest["id"] in seat.extra["opened"]

        room.handle_player(kid, {"t": "next"})
        mode.pos[kid.id] = list(forest_mod.GATE)
        room.handle_player(kid, {"t": "escape"})
        assert kid.id not in mode.escaped  # one key is not five
        seat.extra["keys"] = 5
        room.handle_player(kid, {"t": "escape"})
        assert mode.escaped == [kid.id] and kid.score == 100 + 600
        room.close()

    run(scenario())


def test_forest_bots_find_their_way_to_chests() -> None:
    async def scenario() -> None:
        room = open_room("hutan")
        host, _ = connection()
        room.attach_host(host)
        room.handle_host(host, {"t": "bots", "count": 3})
        room.start_game()
        await until(lambda: room.mode.stage == "play")
        await until(lambda: any(s.extra["opened"] for s in room.mode.seats.values()), timeout=20)
        room.close()

    run(scenario())
