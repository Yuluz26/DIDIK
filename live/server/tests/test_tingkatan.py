"""The games made for Tingkatan 1-5: Litar Kart, Sepakan Penalti, Peti Lanun and Menara 118."""

from __future__ import annotations

import asyncio

import pytest

from didik_live.game.modes import MODES

from .roomkit import connection, settle, until
from .test_modes import answer, started


def run(coro):
    return asyncio.run(coro)


def answer_now(room, player, correct: bool) -> None:
    """Answers the question everyone is on (the games played together)."""
    room.handle_player(player, {"t": "answer", "a": room.mode.pres.sample_answer(correct, room.mode.rng)})


def test_the_four_games_say_they_are_for_secondary_school() -> None:
    levels = {key: cls.describe()["level"] for key, cls in MODES.items()}
    assert [k for k, level in levels.items() if level == "menengah"] == ["litar", "penalti", "lanun", "menara"]
    assert all(level in ("rendah", "menengah") for level in levels.values())
    assert MODES["litar"].describe()["unit"] == "m" and MODES["lanun"].describe()["unit"] == "emas"


# ---------------------------------------------------------------- Litar Kart


def test_kart_nitro_from_the_third_right_answer_and_wrong_answers_still_move() -> None:
    async def scenario() -> None:
        room, host, _, ((ace, ace_socket), (dud, _)) = await started("litar")
        mode = room.mode
        assert mode.length == len(mode.questions) * 100
        for round_no in range(4):
            await until(lambda: mode.stage == "question")
            answer_now(room, ace, True)
            answer_now(room, dud, False)
            await until(lambda: mode.stage == "reveal")  # everyone answered: no waiting for the clock
            assert (ace.id in mode.boosted) == (round_no >= 2)
            assert mode.gained[ace.id] >= 60 + (30 if round_no >= 2 else 0)
            assert mode.gained[dud.id] == 12
            room.handle_host(host, {"t": "skip"})
            await until(lambda: mode.stage != "reveal")
            assert mode.stage == "question"  # straight on: the order is on the circuit
        await settle(0.12)
        circuit = ace_socket.view()["game"]["circuit"]
        assert circuit["laps"] == 3 and {k["id"]: k["m"] for k in circuit["karts"]}[ace.id] == ace.score

        conn, _ = connection()
        late = room.join(conn, {"avatar": "gajah"})
        assert late.score == dud.score  # starts level with the slowest kart
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Sepakan Penalti


def test_penalty_each_team_kicks_and_the_share_of_right_answers_decides() -> None:
    async def scenario() -> None:
        room, host, host_socket, players = await started("penalti", kids=4)
        mode = room.mode
        tigers = [p for p, _ in players if p.team == "harimau"]
        turtles = [p for p, _ in players if p.team == "penyu"]
        assert len(tigers) == len(turtles) == 2

        async def play_round(tiger_right: int, turtle_right: int) -> dict[str, dict]:
            await until(lambda: mode.stage == "question")
            for team, right in ((tigers, tiger_right), (turtles, turtle_right)):
                for index, kid in enumerate(team):
                    answer_now(room, kid, index < right)
            await until(lambda: mode.stage == "reveal")
            kicks = {k["team"]: k for k in mode.rounds[-1]["kicks"]}
            room.handle_host(host, {"t": "skip"})
            return kicks

        kicks = await play_round(2, 1)
        assert kicks["harimau"]["result"] == "gol" and kicks["harimau"]["dive"] != kicks["harimau"]["aim"]
        assert kicks["penyu"]["result"] in ("selamat", "tiang")
        assert [k["team"] for k in mode.rounds[0]["kicks"]] == ["harimau", "penyu"]

        kicks = await play_round(1, 1)  # the same share: both score
        assert kicks["harimau"]["result"] == kicks["penyu"]["result"] == "gol"
        assert [k["team"] for k in mode.rounds[1]["kicks"]] == ["penyu", "harimau"]  # turns to kick first

        kicks = await play_round(0, 0)  # nobody right: both miss
        assert {k["result"] for k in kicks.values()} <= {"selamat", "luar"}
        assert mode.goals == {"harimau": 2, "penyu": 1}

        room.handle_host(host, {"t": "end"})
        await settle()
        results = host_socket.view()["results"]
        assert results["kind"] == "teams" and results["winner"] == "harimau" and results["teamUnit"] == "gol"
        assert results["teams"][0] == {"key": "harimau", "name": "Pasukan Harimau", "score": 2, "players": 2}
        room.close()

    run(scenario())


def test_penalty_draw_on_goals_goes_to_more_right_answers_or_stays_a_draw() -> None:
    async def scenario() -> None:
        room, _, _, _ = await started("penalti", kids=2)
        mode = room.mode
        mode.goals = {"harimau": 3, "penyu": 3}
        mode.rights = {"harimau": 5, "penyu": 7}
        results = mode.results()
        assert results["winner"] == "penyu" and results["note"].startswith("Seri 3-3")
        mode.rights = {"harimau": 5, "penyu": 5}
        assert mode.results()["winner"] is None
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Peti Lanun


def test_pirate_chests_open_after_a_right_answer_and_all_three_are_shown_after() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, socket), _) = await started("lanun")
        mode = room.mode
        seat = mode.seats[kid.id]
        answer(room, kid, False)
        assert seat.step == "result" and seat.extra["chests"] is None
        room.handle_player(kid, {"t": "next"})

        answer(room, kid, True)
        assert seat.step == "chest"
        await settle(0.12)
        assert "chests" not in socket.view()["game"]["world"]  # nothing to peek at before choosing

        seat.extra["chests"] = [{"kind": "emas", "amount": 40}, {"kind": "ganda"}, {"kind": "besar", "amount": 100}]
        room.handle_player(kid, {"t": "open", "chest": True})
        room.handle_player(kid, {"t": "open", "chest": 3})
        assert seat.step == "chest"
        room.handle_player(kid, {"t": "open", "chest": 0})
        assert kid.score == 40 and seat.step == "result"
        await settle(0.12)
        world = socket.view()["game"]["world"]
        assert world["opened"] == 0 and len(world["chests"]) == 3
        assert socket.view()["game"]["seat"]["result"]["reward"]["gain"] == 40
        room.close()

    run(scenario())


def test_pirate_steal_takes_a_quarter_and_a_robbed_ship_is_shielded() -> None:
    async def scenario() -> None:
        room, _, _, players = await started("lanun", kids=3)
        mode = room.mode
        (thief, _), (rich, rich_socket), (other, _) = players
        rich.score, other.score = 200, 80
        seat = mode.seats[thief.id]

        answer(room, thief, True)
        seat.extra["chests"] = [{"kind": "curi"}] * 3
        room.handle_player(thief, {"t": "open", "chest": 1})
        assert seat.step == "target"
        room.handle_player(thief, {"t": "target", "player": rich.id})
        assert (thief.score, rich.score) == (50, 150)
        assert mode.shielded(rich.id)
        await settle(0.12)
        assert rich_socket.of("fx")[-1]["kind"] == "plunder"

        room.handle_player(thief, {"t": "next"})
        answer(room, thief, True)
        seat.extra["chests"] = [{"kind": "tukar"}] * 3
        room.handle_player(thief, {"t": "open", "chest": 2})
        room.handle_player(thief, {"t": "target", "player": rich.id})  # still shielded
        assert seat.step == "target"
        room.handle_player(thief, {"t": "target", "player": other.id})
        assert (thief.score, other.score) == (80, 50)
        room.close()

    run(scenario())


def test_pirate_without_mischief_only_gives_gold_and_a_lone_ship_gets_gold_instead() -> None:
    async def scenario() -> None:
        room, _, _, _ = await started("lanun", naughty=False)
        assert {room.mode.roll()["kind"] for _ in range(400)} <= {"emas", "besar", "ganda"}
        room.close()

        room, _, _, ((kid, _), (other, _)) = await started("lanun")
        seat = room.mode.seats[kid.id]
        answer(room, kid, True)
        seat.extra["chests"] = [{"kind": "curi"}] * 3
        room.handle_player(kid, {"t": "open", "chest": 0})  # nobody has gold to take
        assert seat.step == "result" and kid.score == 25 and other.score == 0
        room.close()

    run(scenario())


# ---------------------------------------------------------------- Menara 118


def test_tower_blocks_need_a_right_answer_and_centred_blocks_count_more() -> None:
    async def scenario() -> None:
        room, _, host_socket, ((kid, socket), _) = await started("menara", minutes=2)
        mode = room.mode
        seat = mode.seats[kid.id]
        room.handle_player(kid, {"t": "drop", "x": 0})
        assert mode.height == 0

        answer(room, kid, True)
        assert seat.step == "drop"
        for bad in ("0", None, True, float("inf")):
            room.handle_player(kid, {"t": "drop", "x": bad})
        assert mode.height == 0
        room.handle_player(kid, {"t": "drop", "x": 0.03})
        assert mode.height == pytest.approx(mode.block * 1.25) and mode.blocks[-1][2] == 0.0
        assert seat.result["reward"]["perfect"] is True

        room.handle_player(kid, {"t": "next"})
        answer(room, kid, True)
        room.handle_player(kid, {"t": "drop", "x": 5})  # far off: still lands, at the edge
        assert mode.blocks[-1][2] == 0.45 and mode.blocks[-1][1] == pytest.approx(mode.block * 0.6)
        assert kid.score == round(mode.block * 1.85)

        await settle(0.12)
        top = socket.view()["game"]["world"]["top"]
        assert len(top) == 2 and top[1][3] == pytest.approx(mode.block * 1.25, abs=0.01)
        assert len(host_socket.view()["game"]["world"]["blocks"]) == 2
        room.close()

    run(scenario())


def test_tower_passes_the_landmarks_and_ends_at_the_height_of_merdeka_118() -> None:
    async def scenario() -> None:
        room, _, host_socket, ((kid, _), _) = await started("menara", minutes=2)
        mode = room.mode
        mode.block = 100.0
        for _ in range(10):
            answer(room, kid, True)
            room.handle_player(kid, {"t": "drop", "x": 0})
            room.handle_player(kid, {"t": "next"})
            if mode.height >= 679:
                break
        await until(lambda: room.phase == "ended")
        await settle()
        assert mode.passed == ["komtar", "menarakl", "petronas", "merdeka"]
        results = host_socket.view()["results"]
        assert results["kind"] == "coop" and results["complete"] and results["headline"] == "Menara 118 siap!"
        room.close()

    run(scenario())
