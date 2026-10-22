"""Litar Kart: a three-lap kart race for Tingkatan 1-5.

Everyone answers the same question. A right answer drives your kart forward, further the faster it
came; from the third right answer in a row the nitro adds a burst on top. A wrong answer still
crawls forward, so nobody is lapped out of the race. The circuit is as long as a race of instant
right answers, so only a long nitro run crosses the line before the last question.
"""

from __future__ import annotations

from typing import Any

from .base import Answered, SyncMode

LAPS = 3
STEP = 100  # metres for a right answer given at once
NITRO = 30  # extra metres for every right answer from the third in a row


class KartMode(SyncMode):
    key = "litar"
    title = "Litar Kart"
    tagline = "Tiga pusingan litar. Jawapan betul dan pantas memecut kart kamu ke depan."
    how = "Semua jawab soalan yang sama. Betul dan laju, kart memecut jauh; tiga betul berturut-turut menyalakan nitro. Salah pun kart tetap bergerak sedikit."
    style = "Serentak"
    world = "litar"
    level = "menengah"
    unit = "m"
    reveal_seconds = 4.5

    def setup(self) -> None:
        self.length = max(1, len(self.questions)) * STEP
        self.boosted: list[str] = []

    def show_standings(self) -> bool:
        # The order is on the circuit itself; no table between questions keeps the race moving.
        return False

    def points_for(self, player: Any, record: Answered | None, limit: float) -> int:
        if record is None:
            return 6
        if record.outcome.correct:
            speed = max(0.0, 1 - record.elapsed / max(limit, 1))
            return round(60 + 40 * speed)
        if record.outcome.fraction > 0:
            return round(60 * record.outcome.fraction)
        return 12

    def on_question(self) -> None:
        self.boosted = []

    def on_reveal(self) -> None:
        for player in self.players():
            if self.streaks.get(player.id, 0) >= 3:
                player.score += NITRO
                self.gained[player.id] = self.gained.get(player.id, 0) + NITRO
                self.boosted.append(player.id)

    def add_player(self, player: Any) -> None:
        # A late joiner starts level with the slowest kart, not on the grid.
        others = [p.score for p in self.players() if p.id != player.id]
        player.score = min(others) if others else 0

    def circuit(self) -> dict[str, Any]:
        return {
            "length": self.length,
            "laps": LAPS,
            "karts": [{"id": p.id, "m": p.score} for p in self.players()],
            "nitro": self.boosted if self.stage == "reveal" else [],
        }

    def player_view(self, player: Any) -> dict[str, Any]:
        return {**self.question_block(player), "circuit": self.circuit()}

    def host_view(self) -> dict[str, Any]:
        return {**super().host_view(), "circuit": self.circuit()}
