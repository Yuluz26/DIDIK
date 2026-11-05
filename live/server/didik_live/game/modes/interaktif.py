"""Kuiz Interaktif: every child walks Didi's cloud trail at their own pace, one question after another,
and collects up to three stars at each stop.

The trail is the quiz in one order (shuffled once for the whole room when the host asks for it), so the
host's screen can show where every child is on the same trail. Every question type plays here, and the
hands-on ones (Kira dan masukkan, Susun huruf, Isih kumpulan) are made for it.

No question has its own clock: a small child counts chickens as slowly as they need. The game ends when
every child still here has reached the end of the trail (a moment later, so each one sees their own
celebration first), or when the game's minutes run out.
"""

from __future__ import annotations

import time
from typing import Any

from ...questions import Outcome, present
from .base import Seat, SelfPacedMode

# How long the room waits once everyone has finished, so the last child sees their stars.
FINALE_SECONDS = 6.0


def stars_for(outcome: Outcome) -> int:
    """Three for right; nearly right still earns something, so trying is never worth nothing."""
    if outcome.correct:
        return 3
    if outcome.fraction >= 0.5:
        return 2
    return 1 if outcome.fraction > 0 else 0


class InteraktifMode(SelfPacedMode):
    key = "interaktif"
    title = "Kuiz Interaktif"
    tagline = "Sentuh, seret dan susun bersama Didi. Setiap soalan satu permainan kecil."
    how = (
        "Setiap kanak-kanak berjalan di denai awan Didi ikut kadar sendiri, satu soalan demi satu. "
        "Kira dan masukkan objek, susun huruf, isih ke bakul atau pilih jawapan. Betul dapat tiga bintang; "
        "hampir betul pun masih dapat bintang."
    )
    style = "Ikut kadar sendiri"
    world = "interaktif"
    family = "interaktif"
    unit = "bintang"
    intro_seconds = 3.0

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        if self.settings.question_limit:
            self.questions = self.questions[: self.settings.question_limit]
        self.all_done_at: float | None = None

    @property
    def total(self) -> int:
        return len(self.questions)

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(stars=[])

    def deal(self, seat: Seat) -> None:
        at = len(seat.extra.get("stars", []))
        seat.result = None
        if at >= self.total:
            seat.pres = None
            seat.step = "done"
            return
        question = self.questions[at]
        seat.last_index = at
        seat.pres = present(question, self.rng, self.scaled(question.time_limit))
        seat.step = "question"

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        stars: list[int] = seat.extra["stars"]
        earned = stars_for(outcome)
        stars.append(earned)
        player.score += earned
        last = len(stars) >= self.total
        if last:
            full = sum(stars) == 3 * self.total
            self.room.feed(
                f"{player.nickname} sampai ke hujung denai dengan {sum(stars)} bintang!" + (" Penuh!" if full else ""),
                "finish",
                player,
            )
        elif seat.streak in (5, 10, 20):
            self.room.feed(f"{player.nickname} betul {seat.streak} kali berturut-turut!", "streak", player)
        return {"stars": earned, "last": last}

    def goal_reached(self) -> bool:
        online = self.online()
        done = bool(online) and all(
            (seat := self.seats.get(p.id)) is not None and seat.step == "done" for p in online
        )
        if not done:
            self.all_done_at = None
            return False
        if self.all_done_at is None:
            self.all_done_at = time.monotonic()
        return time.monotonic() - self.all_done_at >= FINALE_SECONDS

    def world_view(self, player: Any | None) -> dict[str, Any]:
        if player is not None:
            seat = self.seats.get(player.id)
            return {
                "total": self.total,
                "stars": list(seat.extra["stars"]) if seat else [],
                "finished": self.shared("finished", self._finished),
                "players": self.shared("seated", lambda: len(self.seats)),
            }
        return {"total": self.total, "kids": self.shared("kids", self._kids)}

    def _finished(self) -> int:
        return sum(1 for seat in self.seats.values() if seat.step == "done")

    def _kids(self) -> list[dict[str, Any]]:
        return [
            {"id": pid, "stars": list(seat.extra["stars"]), "done": seat.step == "done"}
            for pid, seat in self.seats.items()
            if pid in self.room.players
        ]
