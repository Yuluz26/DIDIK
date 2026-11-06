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
from typing import Any, ClassVar

from ...games import SUBJECTS, deal_games
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


class SubjectInteraktifMode(InteraktifMode):
    """Kuiz Interaktif in one subject's games (games.py): the same trail and stars, but every question that
    one of the subject's games suits is played as that game, whatever quiz it comes from. The rest are
    played the plain hands-on way."""

    subject: ClassVar[str] = ""

    @classmethod
    def unplayable_reason(cls, questions: list[Any]) -> str | None:
        if any(deal_games(cls.subject, questions)):
            return None
        return f"Tiada soalan dalam kuiz ini yang sesuai untuk permainan {SUBJECTS[cls.subject]}. Cuba Kuiz Interaktif."

    @classmethod
    def describe(cls, questions: list[Any] | None = None) -> dict[str, Any]:
        info = super().describe(questions)
        info["subject"] = cls.subject
        if questions is not None:
            info["eligible"] = sum(1 for game in deal_games(cls.subject, questions) if game)
        return info

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        self._dealt: tuple[tuple[int, ...], list[str | None]] | None = None

    def dealt(self) -> list[str | None]:
        """The game for each stop of the trail; worked out again only if the trail changes (a restart)."""
        order = tuple(id(q) for q in self.questions)
        if self._dealt is None or self._dealt[0] != order:
            self._dealt = (order, deal_games(self.subject, self.questions))
        return self._dealt[1]

    def deal(self, seat: Seat) -> None:
        super().deal(seat)
        if seat.pres is not None:
            seat.pres.public["game"] = self.dealt()[seat.last_index]


class SainsInteraktifMode(SubjectInteraktifMode):
    key = "interaktif-sains"
    subject = "sains"
    title = "Makmal Sains"
    style = "Interaktif Sains"
    tagline = "Ramuan berbuih, teropong angkasa, litar dan magnet. Setiap soalan menjadi eksperimen."
    how = (
        "Kuiz Interaktif dalam permainan Sains: tuang ramuan ke dalam bikar, cari jawapan dengan teropong, "
        "nyalakan mentol litar, tarik benda ke magnet dan label organ seperti imbasan X-ray. Ikut kadar sendiri; "
        "betul dapat tiga bintang."
    )


class SejarahInteraktifMode(SubjectInteraktifMode):
    key = "interaktif-sejarah"
    subject = "sejarah"
    title = "Ekspedisi Sejarah"
    style = "Interaktif Sejarah"
    tagline = "Gali artifak, bina empayar dan putar mesin masa. Setiap soalan satu penemuan."
    how = (
        "Kuiz Interaktif dalam permainan Sejarah: gali tapak arkeologi, gantung peristiwa pada garis masa, "
        "bina istana setingkat demi setingkat, cop dokumen arkib dan pacak pin pada peta purba. Ikut kadar "
        "sendiri; betul dapat tiga bintang."
    )


class IslamInteraktifMode(SubjectInteraktifMode):
    key = "interaktif-islam"
    subject = "islam"
    title = "Cahaya Ilmu"
    style = "Interaktif Pendidikan Islam"
    tagline = "Kompas kiblat, peta hijrah, lentera dan neraca amal. Setiap soalan satu amalan."
    how = (
        "Kuiz Interaktif dalam permainan Pendidikan Islam: pusing kompas kiblat, susun perjalanan hijrah, "
        "nyalakan lentera, timbang amalan dan isi tabung zakat. Huruf Arab diwarnakan mengikut hukum tajwid. "
        "Ikut kadar sendiri; betul dapat tiga bintang."
    )
