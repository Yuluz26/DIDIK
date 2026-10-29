"""What the games where answers earn something to spend in your own world share (Pancing Ikan, Kubu
Pasir, Kereta Api Kampung, Pasar Malam): practice bots that spend what they earned before the next
question, and the host's board of the best few worlds.
"""

from __future__ import annotations

from typing import Any

from .base import Seat, SelfPacedMode


class CollectMode(SelfPacedMode):
    def bot_spend(self, bot: Any, seat: Seat) -> bool:
        """Game hook: one thing a bot does with what it has, after an answer. False when there is
        nothing worth doing, and the bot moves on to the next question."""
        return False

    def bot_tick(self, bot: Any, now: float) -> None:
        seat = self.seats.get(bot.id)
        if (
            seat is not None
            and self.stage == "play"
            and not self.paused
            and seat.step == "result"
            and now >= seat.bot_at
            and self.bot_spend(bot, seat)
        ):
            seat.bot_at = now + self.rng.uniform(0.5, 1.0)
            return
        super().bot_tick(bot, now)

    def best(self, count: int, fields: tuple[str, ...]) -> list[dict[str, Any]]:
        """The `count` best scores with the parts of their world the host shows."""
        players = sorted(self.players(), key=lambda p: (-p.score, p.joined_at))[:count]
        return [
            {"id": p.id, "score": p.score, **{f: self.seats[p.id].extra.get(f) for f in fields}}
            for p in players
            if p.id in self.seats
        ]
