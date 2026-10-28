"""Legenda Story Mode: the JRPG rules, solo and party, driven directly."""

from __future__ import annotations

import asyncio
import json

from didik_live.game.manager import RoomManager
from didik_live.game.modes import MODES
from didik_live.game.modes import legenda as story
from didik_live.game.player import dumps
from didik_live.game.room import Room

from .roomkit import connection, open_room, sample, settle, until


def run(coro):
    return asyncio.run(coro)


async def begin(kids: int = 1, title: str = "Haiwan di Malaysia", **settings):
    room = open_room("legenda", title, **settings)
    host, host_socket = connection()
    room.attach_host(host)
    players = []
    for index in range(kids):
        conn, socket = connection()
        players.append((room.join(conn, {"avatar": ["kancil", "harimau", "penyu"][index % 3]}), socket))
    assert room.start_game() is None
    await until(lambda: room.mode.stage == "play")
    return room, host_socket, players


def seat(room, player):
    return room.mode.seats[player.id]


def send(room, player, kind: str, **data) -> None:
    room.handle_player(player, {"t": kind, **data})


def answer(room, player, correct: bool, element: str | None = None) -> None:
    s = seat(room, player)
    assert s.step == "question", s.step
    message = {"t": "answer", "a": s.pres.sample_answer(correct, room.mode.rng), "ev": s.extra["ev"]}
    if element:
        message["el"] = element
    room.handle_player(player, message)
    assert s.step == "result"


def next_(room, player) -> None:
    send(room, player, "next", ev=seat(room, player).extra["ev"])


def to_battle(room, player) -> None:
    """From a cinematic step to the next question, tapping Teruskan like a child would."""
    while seat(room, player).step in ("intro", "travel", "encounter", "clear"):
        next_(room, player)


def clear_road(room, player) -> None:
    for _ in range(story.ENCOUNTERS):
        to_battle(room, player)
        answer(room, player, True)
        next_(room, player)
    assert seat(room, player).step == "clear"
    next_(room, player)
    assert seat(room, player).step == "unlock"
    next_(room, player)


def test_legenda_needs_ten_questions_and_takes_every_type() -> None:
    questions = sample("Haiwan di Malaysia")
    assert len({q.type for q in questions}) == 8
    assert MODES["legenda"].unplayable_reason(questions) is None
    assert "10 soalan" in MODES["legenda"].unplayable_reason(questions[:9])
    assert MODES["legenda"].describe()["look"] == "2d"


def test_solo_world_one_from_hero_choice_to_world_clear() -> None:
    async def scenario() -> None:
        room, _, ((kid, socket),) = await begin(max_players=1)
        s = seat(room, kid)
        assert s.step == "select"
        send(room, kid, "hero", hero="bendahara")  # not in the playable roster
        assert s.step == "select"
        send(room, kid, "hero", hero="mahsuri", ev=s.extra["ev"])
        assert (s.step, s.extra["hero"]) == ("intro", "mahsuri")
        # Nothing to steer: the only things a child sends are next, hero, element, answer, retry.
        send(room, kid, "move", dx=1, dy=0)
        assert s.step == "intro"

        for number in range(1, story.ENCOUNTERS + 1):
            to_battle(room, kid)
            assert s.step == "question" and s.extra["phase"] == "road"
            answer(room, kid, True)
            assert s.result["reward"]["cleared"] == number
            next_(room, kid)
            assert s.step == "clear"
            assert not s.extra["elements"] or number == story.ENCOUNTERS
            next_(room, kid)
        assert s.step == "unlock" and s.extra["elements"]
        next_(room, kid)
        # Alone, the boss gate opens at once.
        await until(lambda: s.step == "reveal")
        next_(room, kid)
        raid = room.mode.raids[s.extra["raid"]]
        for left in range(story.BOSS_BARS - 1, -1, -1):
            assert s.step == "question"
            answer(room, kid, True, element="petir")
            assert raid["hp"] == left
            assert s.result["reward"]["weak"] is True  # Naga Chini is weak to lightning
            next_(room, kid)
        assert s.step == "worldclear" and s.extra["worlds"] == [0]
        next_(room, kid)
        assert (s.step, s.extra["world"], s.extra["hearts"], s.extra["elements"]) == ("intro", 1, 12, False)
        await settle(0.15)
        view = socket.view()["game"]
        assert view["world"]["scene"]["boss"] == "Bujang Senang"
        room.close()

    run(scenario())


def test_hearts_heal_half_cap_at_six_and_wrong_costs_one_and_a_half() -> None:
    async def scenario() -> None:
        room, _, ((kid, _),) = await begin()
        s = seat(room, kid)
        send(room, kid, "hero", hero="tuah")
        to_battle(room, kid)
        answer(room, kid, True)
        assert s.extra["hearts"] == 12  # already full: stays at six hearts
        next_(room, kid)
        to_battle(room, kid)
        answer(room, kid, False)
        assert s.extra["hearts"] == 9 and s.result["reward"]["change"] == -3
        assert s.extra["cleared"] == 1  # a wrong answer never clears the enemy
        next_(room, kid)
        assert s.step == "question"  # the same enemy asks again
        answer(room, kid, True)
        assert s.extra["hearts"] == 10 and s.extra["cleared"] == 2
        room.close()

    run(scenario())


def test_wrong_boss_answers_never_hurt_the_boss_and_falling_keeps_the_checkpoint() -> None:
    async def scenario() -> None:
        room, _, ((kid, _),) = await begin()
        s = seat(room, kid)
        send(room, kid, "hero", hero="tuah")
        clear_road(room, kid)
        await until(lambda: s.step == "reveal")
        next_(room, kid)
        raid = room.mode.raids[s.extra["raid"]]
        answer(room, kid, True)
        assert raid["hp"] == 4
        next_(room, kid)
        for hearts in (9, 6, 3, 0):
            answer(room, kid, False, element="api")
            assert s.extra["hearts"] == hearts and raid["hp"] == 4
            next_(room, kid)
        assert s.step == "fallen" and s.extra["falls"] == 1
        send(room, kid, "next", ev=s.extra["ev"])  # only Cuba lagi leaves this screen
        assert s.step == "fallen"
        send(room, kid, "retry", ev=s.extra["ev"])
        assert (s.step, s.extra["hearts"], s.extra["elements"], s.extra["cleared"]) == ("reveal", 12, True, 5)
        assert raid["hp"] == 4  # the hit already landed stays landed
        next_(room, kid)
        assert s.step == "question"
        room.close()

    run(scenario())


def test_ten_questions_carry_the_whole_story_without_repeats_in_a_row() -> None:
    async def scenario() -> None:
        room, _, ((kid, _),) = await begin(title="Malaysiaku")
        assert len(room.mode.questions) == 10
        s = seat(room, kid)
        send(room, kid, "hero", hero="tuah")
        shown = []
        while not s.extra["finished"]:
            if s.step == "question":
                shown.append(s.pres.public["id"])
                answer(room, kid, True, element="air")
            elif s.step == "gather":
                await until(lambda: s.step != "gather")
            else:
                next_(room, kid)
        assert s.step == "victory" and s.extra["worlds"] == [0, 1, 2, 3, 4]
        assert len(shown) == len(story.WORLDS) * (story.ENCOUNTERS + story.BOSS_BARS) == 50
        assert all(a != b for a, b in zip(shown, shown[1:]))
        # Not even when the deck is shuffled again: three turns pass before a question returns.
        assert all(shown[i] not in shown[i + 1 : i + 4] for i in range(len(shown) - 3))
        assert len(set(shown[:10])) == 10  # the first ten use every question once
        await until(lambda: room.phase == "ended")
        assert room.results["kind"] == "coop" and room.results["complete"] is True
        room.close()

    run(scenario())


def test_answers_keys_never_reach_the_phone_and_double_taps_do_nothing() -> None:
    async def scenario() -> None:
        room, _, ((kid, socket),) = await begin()
        s = seat(room, kid)
        send(room, kid, "hero", hero="tuah")
        stale = s.extra["ev"]
        next_(room, kid)
        send(room, kid, "next", ev=stale)  # the second tap of a double tap
        assert s.step == "travel"
        to_battle(room, kid)
        await settle(0.15)
        game = socket.view()["game"]
        assert "result" not in game["seat"] and "reveal" not in json.dumps(game)
        assert all(set(choice) == {"id", "text"} for choice in game["seat"]["question"].get("choices", []))
        right = s.pres.sample_answer(True, room.mode.rng)
        room.handle_player(kid, {"t": "answer", "a": right})
        room.handle_player(kid, {"t": "answer", "a": right})
        assert s.extra["cleared"] == 1 and s.answered == 1
        room.close()

    run(scenario())


def test_party_waits_at_the_gate_then_shares_one_boss_in_rounds() -> None:
    async def scenario() -> None:
        room, host_socket, ((ana, _), (ben, ben_socket)) = await begin(kids=2)
        a, b = seat(room, ana), seat(room, ben)
        send(room, ana, "hero", hero="tuah")
        send(room, ben, "hero", hero="mahsuri")
        clear_road(room, ana)
        await settle(0.4)
        assert a.step == "gather"  # Ben is still on the road in the same world
        await settle(0.15)
        assert ben_socket.view()["game"]["world"]["friends"][0]["hero"] == "tuah"
        clear_road(room, ben)
        await until(lambda: a.step == "reveal" and b.step == "reveal")
        assert a.extra["raid"] == b.extra["raid"]
        raid = room.mode.raids[a.extra["raid"]]
        next_(room, ana)
        next_(room, ben)

        answer(room, ana, True)
        assert raid["hp"] == 4
        next_(room, ana)
        assert a.step == "wait"  # one hit per child per round
        answer(room, ben, False)
        assert raid["hp"] == 4 and b.extra["hearts"] == 9
        assert raid["round"] == 2
        assert a.step == "question"  # Ben answered, so the next round opened for Ana
        next_(room, ben)
        assert b.step == "question"

        for _ in range(2):
            answer(room, ana, True)
            answer(room, ben, True)
            next_(room, ana)
            next_(room, ben)
        assert raid["hp"] == 0
        assert a.step == b.step == "worldclear"
        assert a.extra["worlds"] == b.extra["worlds"] == [0]
        await settle(0.15)
        host = host_socket.view()["game"]
        assert {row["id"] for row in host["party"]} == {ana.id, ben.id}
        room.close()

    run(scenario())


def test_the_gate_opens_after_a_minute_and_late_friends_join_the_fight() -> None:
    async def scenario() -> None:
        room, _, ((ana, _), (ben, _)) = await begin(kids=2)
        a, b = seat(room, ana), seat(room, ben)
        send(room, ana, "hero", hero="tuah")
        send(room, ben, "hero", hero="mahsuri")
        clear_road(room, ana)
        room.mode.gate_ends[0] = 0  # the minute is up
        await until(lambda: a.step == "reveal")
        raid = room.mode.raids[a.extra["raid"]]
        assert raid["members"] == [ana.id]
        clear_road(room, ben)
        await until(lambda: b.step == "reveal")
        assert b.extra["raid"] == raid["id"] and raid["members"] == [ana.id, ben.id]
        room.close()

    run(scenario())


def test_a_boss_round_does_not_wait_for_a_friend_who_left() -> None:
    async def scenario() -> None:
        room, _, ((ana, _), (ben, _)) = await begin(kids=2)
        a, b = seat(room, ana), seat(room, ben)
        send(room, ana, "hero", hero="tuah")
        send(room, ben, "hero", hero="mahsuri")
        clear_road(room, ana)
        clear_road(room, ben)
        await until(lambda: a.step == "reveal" and b.step == "reveal")
        next_(room, ana)
        next_(room, ben)
        for conn in list(ben.conns):
            room.detach(conn)
        answer(room, ana, True)
        next_(room, ana)
        assert a.step == "question"  # Ben is offline: the round did not wait for him
        room.close()

    run(scenario())


def test_a_story_in_the_middle_of_a_boss_fight_survives_a_restart() -> None:
    async def scenario() -> None:
        room, _, ((kid, _),) = await begin()
        s = seat(room, kid)
        send(room, kid, "hero", hero="mahsuri")
        clear_road(room, kid)
        await until(lambda: s.step == "reveal")
        next_(room, kid)
        answer(room, kid, True)
        saved = json.loads(dumps(room.save()))
        room.close()

        restored = Room.restore(RoomManager(), saved)
        assert restored.phase == "playing" and restored.mode_key == "legenda"
        again = restored.mode.seats[kid.id]
        assert (again.step, again.extra["hero"], again.extra["cleared"]) == ("result", "mahsuri", 5)
        assert restored.mode.raids[again.extra["raid"]]["hp"] == 4
        restored.close()

    run(scenario())


def test_practice_bots_play_the_story_on_their_own() -> None:
    async def scenario() -> None:
        room = open_room("legenda")
        host, _ = connection()
        room.attach_host(host)
        room.handle_host(host, {"t": "bots", "count": 3})
        assert room.start_game() is None
        mode = room.mode
        await until(lambda: any(s.extra["cleared"] >= 2 for s in mode.seats.values()), timeout=40)
        assert all(s.extra["hero"] in story.HEROES for s in mode.seats.values())
        room.close()

    run(scenario())


def test_solo_rooms_hold_one_child(parent) -> None:
    from .conftest import sample_id

    quiz_id = sample_id(parent, "Haiwan di Malaysia")
    response = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": "legenda", "settings": {"max_players": 1}})
    assert response.status_code == 201, response.text
    code = response.json()["code"]
    room = parent.app.state.rooms.find(code)
    room.join(None, {"avatar": "kancil"})
    assert room.accepting_reason() == "Bilik ini sudah penuh."
