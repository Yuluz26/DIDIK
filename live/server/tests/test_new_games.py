"""The six newer 2D games: Pancing Ikan, Lumba Wau, Kubu Pasir, Kereta Api Kampung, Pasar Malam and
Kejar Bintang. (Every game also plays through with bots in test_modes.py.)"""

from __future__ import annotations

from didik_live.game.modes import fishing, sandcastle

from .test_modes import answer, run, started


def test_fishing_needs_bait_and_golden_bait_comes_from_a_streak() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("pancing")
        f = room.mode.seats[kid.id].extra
        assert f["bait"] == 1
        room.handle_player(kid, {"t": "cast"})
        assert f["bait"] == 0 and f["caught"] == 1 and len(f["net"]) == 1
        caught_before = f["caught"]
        room.handle_player(kid, {"t": "cast"})  # no bait left
        assert f["caught"] == caught_before
        for _ in range(3):
            answer(room, kid, True)
            room.handle_player(kid, {"t": "next"})
        assert f["bait"] == 2 and f["gold"] == 1  # the third in a row is golden
        score = kid.score
        room.handle_player(kid, {"t": "cast", "gold": True})
        assert f["gold"] == 0 and f["net"][-1] != "kasut"  # golden bait never brings up a boot
        assert kid.score == score + fishing.FISH[f["net"][-1]]["value"]
        room.close()

    run(scenario())


def test_sandcastle_floors_cost_sand_and_a_wall_takes_the_wave() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("kubu")
        mode = room.mode
        c = mode.seats[kid.id].extra
        room.handle_player(kid, {"t": "build", "part": "floor"})
        assert c["floors"] == 1 and c["sand"] == 0 and kid.score == 10
        room.handle_player(kid, {"t": "build", "part": "floor"})
        assert c["floors"] == 1  # no sand left
        c["sand"] = sandcastle.COSTS["wall"] + sandcastle.COSTS["floor"]
        room.handle_player(kid, {"t": "build", "part": "wall"})
        room.handle_player(kid, {"t": "build", "part": "floor"})
        assert c["walls"] == 1 and c["floors"] == 2
        mode.wave()
        assert c["walls"] == 0 and c["floors"] == 2  # the wall took it
        mode.wave()
        assert c["floors"] == 1 and kid.score == 10  # no wall: the top floor washed away
        room.close()

    run(scenario())


def test_train_carriages_make_each_run_count_more() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("keretapi")
        t = room.mode.seats[kid.id].extra
        room.handle_player(kid, {"t": "go"})
        assert t["station"] == 1 and kid.score == 10 and t["coal"] == 0
        t["coal"] = 5
        room.handle_player(kid, {"t": "car"})
        room.handle_player(kid, {"t": "go"})
        assert t["cars"] == 2 and kid.score == 30 and t["coal"] == 0
        room.close()

    run(scenario())


def test_market_decorations_raise_the_price() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("pasar")
        m = room.mode.seats[kid.id].extra
        room.handle_player(kid, {"t": "sell"})
        assert m["cash"] == 2 and m["stock"] == 0 and kid.score == 2
        room.handle_player(kid, {"t": "upgrade", "item": "lampu"})
        assert m["upgrades"] == []  # 2 ringgit is not enough
        m["cash"], m["stock"] = 10, 3
        room.handle_player(kid, {"t": "upgrade", "item": "lampu"})
        room.handle_player(kid, {"t": "sell"})
        assert m["upgrades"] == ["lampu"] and m["cash"] == 6 and kid.score == 8  # 3 sold at 2 each
        room.close()

    run(scenario())


def test_stars_go_to_the_team_and_the_bigger_team_total_wins() -> None:
    async def scenario() -> None:
        room, _, _, ((a, _), (b, _)) = await started("bintang")
        mode = room.mode
        assert {a.team, b.team} == {"harimau", "penyu"}
        answer(room, a, True)
        room.handle_player(a, {"t": "next"})
        answer(room, b, False)
        assert mode.stars[a.team] == 1 and mode.stars[b.team] == 0 and a.score == 1
        results = mode.results()
        assert results["kind"] == "teams" and results["winner"] == a.team
        room.close()

    run(scenario())


def test_kite_is_a_race_upwards() -> None:
    async def scenario() -> None:
        room, _, _, ((kid, _), _) = await started("wau")
        view = room.mode.player_view(kid)
        assert "race" in view and room.mode.unit == "m"
        room.close()

    run(scenario())
