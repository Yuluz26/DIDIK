"""Menara 118: the whole class builds one tower together, up to the height of Merdeka 118.

Every right answer gives a child one block to drop on top. A block stopped over the middle lands whole
and counts for more; off-centre still lands and still counts, so nobody can spoil the tower for the
others. Block heights are set from the number of children and minutes, so a class that keeps
answering reaches the top before time runs out, and the game ends there.

Heights are real (checked): Komtar 248.7 m, Menara Kuala Lumpur 421 m, Menara Berkembar Petronas
451.9 m, Merdeka 118 678.9 m.
"""

from __future__ import annotations

import math
from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode

GOAL = 679
LANDMARKS = [
    ("komtar", "Komtar", 249),
    ("menarakl", "Menara Kuala Lumpur", 421),
    ("petronas", "Menara Berkembar Petronas", 452),
    ("merdeka", "Merdeka 118", 679),
]
MAX_OFFSET = 0.45  # how far off-centre a block can land, as a share of its width
PERFECT = 0.05  # this close to the middle lands whole: "Tepat!"
TOP_BLOCKS = 12  # the blocks a phone needs to draw the top of the tower


class TowerMode(SelfPacedMode):
    key = "menara"
    title = "Menara 118"
    tagline = "Seisi kelas membina satu menara setinggi Merdeka 118. Setiap jawapan betul, satu blok."
    how = "Jawab betul untuk dapat satu blok, kemudian tekan Letak bila blok berada di tengah menara. Lebih tepat di tengah, lebih tinggi menara naik."
    style = "Kerjasama"
    world = "menara"
    level = "menengah"
    unit = "m"

    def setup(self) -> None:
        children = max(1, len(self.players()))
        # About 1.8 blocks per child per minute: answering takes most of the time, the drop a moment.
        expected = max(14.0, children * self.settings.minutes * 1.8)
        self.block = GOAL / expected
        self.height = 0.0
        self.blocks: list[tuple[str, float, float]] = []  # (who, metres, offset)
        self.contrib: dict[str, float] = {}
        self.passed: list[str] = []

    def goal_reached(self) -> bool:
        return self.height >= GOAL

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return None
        seat.step = "drop"
        return {"kind": "block"}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if kind != "drop" or seat is None or seat.step != "drop" or self.height >= GOAL:
            return
        raw = data.get("x")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
            return
        offset = max(-MAX_OFFSET, min(MAX_OFFSET, float(raw)))
        perfect = abs(offset) <= PERFECT
        if perfect:
            offset = 0.0
            metres = self.block * 1.25
        else:
            metres = self.block * (0.6 + 0.4 * (1 - abs(offset) / MAX_OFFSET))
        self.blocks.append((player.id, metres, offset))
        self.height += metres
        self.contrib[player.id] = self.contrib.get(player.id, 0.0) + metres
        player.score = round(self.contrib[player.id])
        for key, name, height in LANDMARKS:
            if self.height >= height and key not in self.passed:
                self.passed.append(key)
                self.room.feed(f"Menara kita melepasi {name} ({height} m)!", "landmark", player)
                self.room.fx({"kind": "landmark", "landmark": key})
        seat.step = "result"
        if seat.result is not None:
            seat.result["reward"] = {"kind": "dropped", "metres": round(metres, 1), "perfect": perfect}
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        view: dict[str, Any] = {
            "height": round(self.height, 1),
            "goal": GOAL,
            "count": len(self.blocks),
            "landmarks": [{"key": k, "name": n, "m": h, "passed": k in self.passed} for k, n, h in LANDMARKS],
        }
        if player is None:
            # The big screen draws the whole tower: [who, metres, offset] from the ground up.
            view["blocks"] = [[who, round(m, 2), round(x, 3)] for who, m, x in self.blocks]
            return view
        # A phone only needs the top of the tower, with where each block starts.
        base = self.height - sum(m for _, m, _ in self.blocks[-TOP_BLOCKS:])
        top = []
        for who, metres, offset in self.blocks[-TOP_BLOCKS:]:
            top.append([who, round(metres, 2), round(offset, 3), round(base, 2)])
            base += metres
        view["top"] = top
        view["block"] = round(self.block, 2)
        view["mine"] = round(self.contrib.get(player.id, 0.0), 1)
        return view

    def results(self) -> dict[str, Any]:
        builders = sorted(self.players(), key=lambda p: (-self.contrib.get(p.id, 0.0), p.joined_at))
        complete = self.height >= GOAL
        passed = [(n, h) for k, n, h in LANDMARKS if k in self.passed and k != "merdeka"]
        if complete:
            headline, note = "Menara 118 siap!", "Setinggi Merdeka 118, bangunan kedua tertinggi di dunia."
        else:
            headline = f"Menara kita setinggi {round(self.height)} m!"
            if passed:
                name, height = passed[-1]
                note = f"Lebih tinggi daripada {name} ({height} m)."
            else:
                note = f"Sedikit lagi untuk melepasi Komtar ({LANDMARKS[0][2]} m)."
        return {
            "kind": "coop",
            "headline": headline,
            "note": note,
            "complete": complete,
            "players": [{"id": p.id, "score": round(self.contrib.get(p.id, 0.0)), "rank": 1} for p in builders],
        }

    def bot_step(self, bot: Any, seat: Seat) -> None:
        if seat.step == "drop":
            spread = 0.04 + 0.3 * (1 - bot.skill)
            self.act(bot, seat, "drop", {"x": max(-MAX_OFFSET, min(MAX_OFFSET, self.rng.gauss(0, spread)))})
