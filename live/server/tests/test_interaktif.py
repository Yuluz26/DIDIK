"""Kuiz Interaktif: one trail of questions in the same order for everyone, stars at each stop, and the
game ends once every child still here has reached the end (after a moment for their celebration)."""

from __future__ import annotations

from didik_live.game.modes import interaktif
from didik_live.questions import Outcome

from .roomkit import until
from .test_modes import answer, run, started


def test_stars_reward_right_answers_and_still_reward_trying() -> None:
    assert interaktif.stars_for(Outcome(True, 1.0)) == 3
    assert interaktif.stars_for(Outcome(False, 0.667)) == 2
    assert interaktif.stars_for(Outcome(False, 0.25)) == 1
    assert interaktif.stars_for(Outcome(False, 0.0)) == 0


def test_every_child_walks_the_same_trail_to_the_end(monkeypatch) -> None:
    monkeypatch.setattr(interaktif, "FINALE_SECONDS", 0.2)

    async def scenario() -> None:
        room, _, host_socket, ((ana, ana_socket), (ben, _)) = await started("interaktif", question_limit=3)
        mode = room.mode
        assert mode.total == 3
        trail = [q.id for q in mode.questions]

        # the same question first for both, and then each moves on alone
        assert mode.seats[ana.id].pres.question.id == mode.seats[ben.id].pres.question.id == trail[0]
        answer(room, ana, True)
        assert mode.seats[ana.id].step == "result" and ana.score == 3
        room.handle_player(ana, {"t": "next"})
        assert mode.seats[ana.id].pres.question.id == trail[1]
        assert mode.seats[ben.id].pres.question.id == trail[0]

        answer(room, ana, False)
        room.handle_player(ana, {"t": "next"})
        answer(room, ana, True)
        room.handle_player(ana, {"t": "next"})
        seat = mode.seats[ana.id]
        assert seat.step == "done" and seat.pres is None and len(seat.extra["stars"]) == 3
        assert seat.extra["stars"][0] == 3 and seat.extra["stars"][2] == 3
        room.handle_player(ana, {"t": "next"})  # nothing past the end of the trail
        assert seat.step == "done"
        assert not mode.goal_reached()  # Ben is still walking

        await until(lambda: (((ana_socket.view() or {}).get("game") or {}).get("world") or {}).get("finished") == 1)
        world = ana_socket.view()["game"]["world"]
        assert world["total"] == 3 and world["finished"] == 1 and world["players"] == 2
        host_world = host_socket.view()["game"]["world"]
        assert {kid["id"] for kid in host_world["kids"]} == {ana.id, ben.id}
        assert next(k for k in host_world["kids"] if k["id"] == ana.id)["done"] is True

        for _ in range(3):
            answer(room, ben, True)
            room.handle_player(ben, {"t": "next"})
        assert ben.score == 9
        await until(lambda: room.phase == "ended")
        assert any(item["text"].endswith("Penuh!") for item in room._feed)  # Ben got every star
        room.close()

    run(scenario())


def test_a_late_child_starts_at_the_beginning_of_the_trail() -> None:
    async def scenario() -> None:
        room, _, _, ((ana, _), _) = await started("interaktif", question_limit=4)
        mode = room.mode
        answer(room, ana, True)
        room.handle_player(ana, {"t": "next"})
        from .roomkit import connection

        conn, _ = connection()
        late = room.join(conn, {"avatar": "gajah"})
        assert mode.seats[late.id].pres.question.id == mode.questions[0].id
        room.close()

    run(scenario())
