"""Kampung Kita: the whole room builds one village together. Every right answer carries building
material to the site; every third right answer lets a child place a decoration of their own.

Nobody loses. The village is sized from the number of children and minutes, so a room that keeps
answering finishes it, and the game ends early with a celebration when the last building stands.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode

BUILDINGS = [
    ("rumah", "Rumah Kampung", 0.10),
    ("kedai", "Kedai Runcit", 0.12),
    ("sekolah", "Sekolah", 0.16),
    ("jeti", "Jeti Nelayan", 0.12),
    ("masjid", "Masjid", 0.18),
    ("rumahpanjang", "Rumah Panjang", 0.17),
    ("balai", "Balai Raya", 0.15),
]
DECORATIONS = ["kelapa", "bunga", "pelita", "wau", "kucing", "ayam"]
MAX_DECORATIONS = 80
# The padang in front of the village, as fractions of the map; the web app draws the same field.
PADANG_X = (0.04, 0.96)
PADANG_Y = (0.80, 0.97)


class VillageMode(SelfPacedMode):
    key = "kampung"
    title = "Kampung Kita"
    tagline = "Semua pemain bina satu kampung bersama. Tiada yang kalah."
    how = "Setiap jawapan betul membawa bahan binaan. Setiap tiga jawapan betul, kamu boleh letak hiasan sendiri di kampung."
    style = "Kerjasama"
    world = "kampung"

    def setup(self) -> None:
        children = max(1, len(self.players()))
        # About two right answers per child per minute builds the whole village.
        total = max(24, round(children * self.settings.minutes * 2.0))
        self.costs = [max(3, round(total * share)) for _, _, share in BUILDINGS]
        self.built = 0
        self.progress = 0
        self.decor: list[dict[str, Any]] = []
        self.contrib: dict[str, int] = {}
        self._decor_id = 0

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(tokens=0)

    def goal_reached(self) -> bool:
        return self.built >= len(BUILDINGS)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"materials": 0}
        amount = 2 if seat.streak >= 3 else 1
        self.contrib[player.id] = self.contrib.get(player.id, 0) + amount
        player.score = self.contrib[player.id]
        self.add_materials(amount, player)
        decoration = seat.correct % 3 == 0
        if decoration:
            seat.extra["tokens"] += 1
        return {"materials": amount, "decoration": decoration}

    def add_materials(self, amount: int, player: Any) -> None:
        while amount > 0 and self.built < len(BUILDINGS):
            room_left = self.costs[self.built] - self.progress
            used = min(room_left, amount)
            self.progress += used
            amount -= used
            if self.progress >= self.costs[self.built]:
                key, name, _ = BUILDINGS[self.built]
                self.built += 1
                self.progress = 0
                self.room.feed(f"{name} siap dibina!", "built", player)
                self.room.fx({"kind": "built", "building": key, "name": name})

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if kind != "place" or seat is None or seat.extra["tokens"] < 1:
            return
        decoration = data.get("kind")
        try:
            x = float(data.get("x"))
            y = float(data.get("y"))
        except (TypeError, ValueError):
            return
        if decoration not in DECORATIONS:
            return
        seat.extra["tokens"] -= 1
        self._decor_id += 1
        item = {
            "id": self._decor_id,
            "kind": decoration,
            "x": round(min(PADANG_X[1], max(PADANG_X[0], x)), 3),
            "y": round(min(PADANG_Y[1], max(PADANG_Y[0], y)), 3),
            "by": player.id,
        }
        self.decor.append(item)
        del self.decor[:-MAX_DECORATIONS]
        self.room.fx({"kind": "placed", **item})
        self.room.mark_dirty()

    def site(self) -> dict[str, Any]:
        return {
            "buildings": [
                {
                    "key": key,
                    "name": name,
                    "cost": cost,
                    "done": index < self.built,
                    "progress": self.progress if index == self.built else (cost if index < self.built else 0),
                }
                for index, ((key, name, _), cost) in enumerate(zip(BUILDINGS, self.costs, strict=True))
            ],
            "built": self.built,
            "decor": self.decor,
            # Who has carried the most material, so the village can show them at work.
            "helpers": [
                {"id": pid, "n": n}
                for pid, n in sorted(self.contrib.items(), key=lambda kv: -kv[1])
                if pid in self.room.players
            ][:12],
        }

    def world_view(self, player: Any) -> dict[str, Any]:
        site = self.site()
        if player is not None:
            seat = self.seats.get(player.id)
            site["tokens"] = seat.extra["tokens"] if seat else 0
            site["mine"] = self.contrib.get(player.id, 0)
        return site

    def results(self) -> dict[str, Any]:
        helpers = sorted(self.players(), key=lambda p: (-self.contrib.get(p.id, 0), p.joined_at))
        return {
            "kind": "coop",
            "built": self.built,
            "total": len(BUILDINGS),
            "complete": self.built >= len(BUILDINGS),
            "decorations": len(self.decor),
            "players": [{"id": p.id, "score": self.contrib.get(p.id, 0), "rank": 1} for p in helpers],
        }

    def bot_tick(self, bot: Any, now: float) -> None:
        seat = self.seats.get(bot.id)
        if seat is not None and seat.extra["tokens"] > 0 and now >= seat.bot_at and self.stage == "play":
            self.act(bot, seat, "place", {
                "kind": self.rng.choice(DECORATIONS), "x": self.rng.uniform(*PADANG_X), "y": self.rng.uniform(*PADANG_Y)
            })
        super().bot_tick(bot, now)
