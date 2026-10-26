"""Regressions for DIDIK Legenda's server-authoritative five-world story."""
from __future__ import annotations

import asyncio
from didik_live.game.modes import MODES
from didik_live.game.modes.story import BOSS_HEARTS, HEARTS, REALMS, StoryMode
from .roomkit import connection, open_room, until


def run(coro):
    return asyncio.run(coro)


async def story_party(kids: int = 1):
    room = open_room("legenda")
    host, _ = connection()
    room.attach_host(host)
    players = []
    for index in range(kids):
        conn, socket = connection()
        players.append(room.join(conn, {"avatar": ["kancil", "harimau"][index]}))
    assert room.start_game() is None
    await until(lambda: room.mode.stage == "play")
    return room, players


def engage(room, player):
    mode = room.mode
    extra = mode.seat(player).extra
    target = 21.5 if extra["phase"] == "boss" else mode.world_view(player)["foes"][extra["obstacle"]]
    mode.positions[player.id] = [target - 0.8, 10.0]
    room.handle_player(player, {"t": "engage"})
    assert mode.seat(player).step == "question"


def answer_and_next(room, player, correct=True):
    mode = room.mode
    seat = mode.seat(player)
    assert seat.step == "question"
    assert "correct" not in str(seat.pres.public)
    room.handle_player(player, {"t": "answer", "a": seat.pres.sample_answer(correct, mode.rng)})
    assert seat.step == "result"
    room.handle_player(player, {"t": "next"})


def complete_obstacles(room, player):
    for _ in range(5):
        engage(room, player)
        answer_and_next(room, player)
    assert room.mode.seat(player).extra["phase"] == "boss"


def test_story_is_nine_two_dimensional_games(monkeypatch) -> None:
    assert len(MODES) == 9
    assert all(m.look == "2d" for m in MODES.values())
    assert "legenda" in MODES and "litar" not in MODES
    assert MODES["legenda"].min_questions == 10


def test_story_progress_and_boss_weapons(monkeypatch) -> None:
    monkeypatch.setattr(StoryMode, "intro_seconds", 0)

    async def scenario():
        room, (hero,) = await story_party()
        mode = room.mode
        assert mode.seat(hero).extra["hearts"] == HEARTS
        room.handle_player(hero, {"t": "engage"})  # too far
        assert mode.seat(hero).step == "explore"
        complete_obstacles(room, hero)
        seat = mode.seat(hero)
        assert seat.extra["weapons"] is True
        room.handle_player(hero, {"t": "element", "element": REALMS[0]["element"]})
        assert seat.extra["weapon"] == REALMS[0]["element"]
        for _ in range(BOSS_HEARTS):
            engage(room, hero)
            answer_and_next(room, hero)
        assert mode.boss_hp["0"] == 0
        assert seat.extra["realm"] == 1
        assert seat.extra["hearts"] == HEARTS
        assert seat.extra["weapons"] is False
        room.close()

    run(scenario())


def test_story_wrong_answer_and_checkpoint_retry(monkeypatch) -> None:
    monkeypatch.setattr(StoryMode, "intro_seconds", 0)

    async def scenario():
        room, (hero,) = await story_party()
        mode = room.mode
        for n in range(4):
            engage(room, hero)
            answer_and_next(room, hero, correct=False)
            assert mode.seat(hero).extra["hearts"] == max(0, HEARTS-(n+1)*3)
        seat = mode.seat(hero)
        assert seat.step == "dead"
        room.handle_player(hero, {"t": "retry"})
        assert seat.step == "explore"
        assert seat.extra["realm"] == 0 and seat.extra["hearts"] == HEARTS
        room.close()

    run(scenario())


def test_story_coop_players_share_boss_but_not_hearts(monkeypatch) -> None:
    monkeypatch.setattr(StoryMode, "intro_seconds", 0)

    async def scenario():
        room, (a,b) = await story_party(kids=2)
        mode = room.mode
        complete_obstacles(room, a)
        complete_obstacles(room, b)
        engage(room, a)
        answer_and_next(room, a, correct=False)
        assert mode.seat(a).extra["hearts"] == HEARTS-3
        assert mode.seat(b).extra["hearts"] == HEARTS
        for i in range(5):
            player = a if i%2==0 else b
            engage(room, player)
            answer_and_next(room, player)
        assert mode.boss_hp["0"] == 0
        # A player who did not land the final hit can enter the next world.
        if mode.seat(a).extra["realm"] == 0:
            engage(room, a)
        if mode.seat(b).extra["realm"] == 0:
            engage(room, b)
        assert mode.seat(a).extra["realm"] == 1
        assert mode.seat(b).extra["realm"] == 1
        room.close()

    run(scenario())
