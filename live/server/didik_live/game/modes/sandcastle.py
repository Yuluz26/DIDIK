"""Kubu Pasir: right answers fill buckets of sand. Build your castle a floor at a time, put up a sea
wall, plant flags on top. Every so often a wave rolls in: a wall takes the wave and breaks, otherwise
the wave washes the top floor away. The score is the castle standing (ten a floor, five a flag).
"""

from __future__ import annotations

import asyncio
from typing import Any

from ...questions import Outcome
from .base import Seat, now_ms
from .collect import CollectMode

WAVE_EVERY = 45  # seconds
COSTS = {"floor": 2, "wall": 3, "flag": 4}
MAX_FLOORS = 12
MAX_WALLS = 2
MAX_FLAGS = 3


class SandcastleMode(CollectMode):
    key = "kubu"
    title = "Kubu Pasir"
    tagline = "Jawab betul untuk dapat pasir. Bina istana pasir paling tinggi sebelum ombak datang!"
    how = "Setiap jawapan betul memberi baldi pasir. Tambah tingkat, bina tembok dan pacak bendera. Ombak datang setiap 45 saat: tembok menahan ombak, jika tiada tembok satu tingkat runtuh."
    style = "Ikut kadar sendiri"
    world = "pantai"
    unit = "mata"
    saved = ("wave_in", "waves")

    def setup(self) -> None:
        self.wave_in = WAVE_EVERY
        self.waves = 0

    async def run(self) -> None:
        ticker = asyncio.create_task(self.tide())
        try:
            await super().run()
        finally:
            ticker.cancel()

    async def tide(self) -> None:
        while not self.finished:
            await asyncio.sleep(1)
            if self.stage != "play" or self.paused:
                continue
            self.wave_in -= 1
            if self.wave_in <= 0:
                self.wave()
                self.wave_in = WAVE_EVERY

    def wave(self) -> None:
        self.waves += 1
        for player in self.players():
            seat = self.seats.get(player.id)
            if seat is None:
                continue
            c = seat.extra
            if c["walls"] > 0:
                c["walls"] -= 1
            elif c["floors"] > 0:
                c["floors"] -= 1
                c["lost"] += 1
            self.rescore(player, seat)
        self.room.fx({"kind": "wave", "n": self.waves})
        self.room.feed("Ombak datang! Tembok menahan ombak; istana tanpa tembok hilang satu tingkat.", "wave")
        self.room.mark_dirty()

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(sand=2, floors=0, walls=0, flags=0, lost=0, tallest=0)

    def rescore(self, player: Any, seat: Seat) -> None:
        c = seat.extra
        player.score = c["floors"] * 10 + c["flags"] * 5

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"sand": 0}
        sand = 3 if seat.streak >= 3 else 2
        seat.extra["sand"] += sand
        return {"sand": sand}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None or kind != "build":
            return
        c = seat.extra
        part = str(data.get("part"))
        cost = COSTS.get(part)
        if cost is None or c["sand"] < cost:
            return
        if part == "floor" and c["floors"] < MAX_FLOORS:
            c["floors"] += 1
            c["tallest"] = max(c["tallest"], c["floors"])
            if c["floors"] == MAX_FLOORS:
                self.room.feed(f"{player.nickname} membina istana dua belas tingkat!", "castle", player)
        elif part == "wall" and c["walls"] < MAX_WALLS:
            c["walls"] += 1
        elif part == "flag" and c["flags"] < MAX_FLAGS and c["floors"] > 0:
            c["flags"] += 1
        else:
            return
        c["sand"] -= cost
        self.rescore(player, seat)
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        shared = {"costs": COSTS, "maxFloors": MAX_FLOORS, "maxWalls": MAX_WALLS, "maxFlags": MAX_FLAGS, "waveAt": now_ms() + self.wave_in * 1000, "waves": self.waves, "paused": self.paused}
        if player is None:
            return {**shared, "top": self.shared("top", lambda: self.best(3, ("floors", "walls", "flags")))}
        seat = self.seats.get(player.id)
        c = seat.extra if seat else {"sand": 0, "floors": 0, "walls": 0, "flags": 0, "lost": 0, "tallest": 0}
        return {**shared, **{k: c[k] for k in ("sand", "floors", "walls", "flags", "lost", "tallest")}}

    def bot_spend(self, bot: Any, seat: Seat) -> bool:
        c = seat.extra
        if c["walls"] == 0 and c["floors"] >= 3 and c["sand"] >= COSTS["wall"]:
            self.act(bot, seat, "build", {"part": "wall"})
        elif c["sand"] >= COSTS["floor"] and c["floors"] < MAX_FLOORS:
            self.act(bot, seat, "build", {"part": "floor"})
        else:
            return False
        return True
