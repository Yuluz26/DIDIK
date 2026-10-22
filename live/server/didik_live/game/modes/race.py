"""Lumba Sampan: everyone answers the same question; right and fast moves your boat furthest.

A wrong answer still paddles a little, so nobody is left far behind, and once or twice a race the
rapids carry every boat forward together.
"""

from __future__ import annotations

from typing import Any

from .base import Answered, SyncMode

STEP = 100  # metres for a perfect answer


class RaceMode(SyncMode):
    key = "lumba"
    title = "Lumba Sampan"
    tagline = "Jawab betul dan pantas, sampan kamu meluncur ke garisan penamat."
    how = "Semua jawab soalan yang sama. Betul dan laju = sampan maju jauh. Salah pun tetap maju sikit."
    style = "Serentak"
    world = "sungai"
    unit = "m"
    saved = ("rapids_at", "rapids_now", "length")

    def setup(self) -> None:
        count = len(self.questions)
        candidates = list(range(1, count - 1))
        self.rng.shuffle(candidates)
        self.rapids_at = sorted(candidates[: 1 if count < 8 else 2])
        self.rapids_now = False
        self.length = count * STEP + len(self.rapids_at) * 25

    def points_for(self, player: Any, record: Answered | None, limit: float) -> int:
        if record is None:
            return 6
        if record.outcome.correct:
            speed = max(0.0, 1 - record.elapsed / max(limit, 1))
            streak = min(max(self.streaks.get(player.id, 0) - 1, 0), 2) * 10
            return round(60 + 40 * speed) + streak
        if record.outcome.fraction > 0:
            return round(60 * record.outcome.fraction)
        return 12

    def on_question(self) -> None:
        self.rapids_now = False

    def on_reveal(self) -> None:
        if self.index in self.rapids_at:
            self.rapids_now = True
            for player in self.players():
                player.score += 25
                self.gained[player.id] = self.gained.get(player.id, 0) + 25
            self.room.feed("Arus deras! Semua sampan meluncur ke depan.", "rapids")
            self.room.fx({"kind": "rapids"})

    def add_player(self, player: Any) -> None:
        # A late joiner starts level with the slowest boat, not at the start line.
        others = [p.score for p in self.players() if p.id != player.id]
        player.score = min(others) if others else 0

    def boats(self) -> dict[str, Any]:
        return {
            "length": self.length,
            "rapids": self.rapids_now and self.stage == "reveal",
            "boats": [{"id": p.id, "m": p.score} for p in self.players()],
        }

    def player_view(self, player: Any) -> dict[str, Any]:
        return {**self.question_block(player), "race": self.boats()}

    def host_view(self) -> dict[str, Any]:
        return {**super().host_view(), "race": self.boats()}
