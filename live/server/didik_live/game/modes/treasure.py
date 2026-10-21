"""Pulau Harta Karun: every right answer earns a shovel; dig one patch of your island for coins,
a chest, a gem, a treasure map that doubles your luck, or a parrot that steals from someone ahead.

What is under each patch is decided only when it is dug, on the server, so nothing in the
browser can reveal where the gems are.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode

TILES = 12

# (kind, weight, naughty)
LOOT = [
    ("coins", 40, False),
    ("chest", 16, False),
    ("gem", 7, False),
    ("map", 5, False),
    ("sand", 12, False),
    ("parrot", 9, True),
    ("crab", 5, True),
]


class TreasureMode(SelfPacedMode):
    key = "harta"
    title = "Pulau Harta Karun"
    tagline = "Setiap jawapan betul = satu penyodok. Gali pasir dan cari syiling, permata dan peta harta!"
    how = "Jawab betul untuk dapat penyodok, kemudian pilih satu petak untuk digali. Hati-hati dengan burung kakak tua!"
    style = "Ikut kadar sendiri"
    world = "pulau"

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(island=1, dug={}, last=None)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return None
        seat.step = "dig"
        return {"kind": "shovel"}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if kind != "dig" or seat is None or seat.step != "dig":
            return
        try:
            tile = int(data.get("tile"))
        except (TypeError, ValueError):
            return
        dug = seat.extra["dug"]
        if not 0 <= tile < TILES or str(tile) in dug:
            return
        found = self.roll(player)
        dug[str(tile)] = found
        seat.extra["last"] = {"tile": tile, **found}
        seat.step = "result"
        if seat.result is not None:
            seat.result["reward"] = {"kind": "dug", **found}
        self.room.fx({"kind": "dig", "tile": tile, **found}, to=player, hosts=False)
        self.room.mark_dirty()

    def act_next(self, player: Any) -> None:
        seat = self.seats.get(player.id)
        # A fully dug island is swapped for a new one only after the child has seen the last find.
        if seat is not None and seat.step == "result" and len(seat.extra["dug"]) >= TILES:
            seat.extra["island"] += 1
            seat.extra["dug"] = {}
        super().act_next(player)

    def roll(self, player: Any) -> dict[str, Any]:
        table = [(kind, weight) for kind, weight, naughty in LOOT if self.settings.naughty or not naughty]
        kind = self.rng.choices([k for k, _ in table], weights=[w for _, w in table])[0]

        if kind == "coins":
            amount = self.rng.choice([10, 15, 20, 25])
        elif kind == "chest":
            amount = 50
        elif kind == "gem":
            amount = 100
            self.room.feed(f"{player.nickname} jumpa permata!", "gem", player)
        elif kind == "map":
            amount = min(max(player.score, 20), 150)
            self.room.feed(f"{player.nickname} jumpa peta harta: syiling berganda!", "map", player)
        elif kind == "sand":
            amount = 5
        elif kind == "crab":
            amount = -min(60, max(5, player.score // 10)) if player.score > 0 else 0
        else:  # parrot
            return self.parrot(player)

        player.score = max(0, player.score + amount)
        return {"found": kind, "amount": amount}

    def parrot(self, player: Any) -> dict[str, Any]:
        ahead = [p for p in self.players() if p.id != player.id and p.score > player.score]
        if not ahead:
            player.score += 20
            return {"found": "parrot", "amount": 20, "from": None}
        victim = self.rng.choice(ahead)
        amount = min(120, max(10, victim.score * 15 // 100))
        victim.score -= amount
        player.score += amount
        self.room.feed(f"Burung kakak tua {player.nickname} mencuri {amount} syiling daripada {victim.nickname}!", "steal", player)
        self.room.fx({"kind": "stolen", "by": player.id, "amount": amount}, to=victim, hosts=False)
        return {"found": "parrot", "amount": amount, "from": victim.id}

    def world_view(self, player: Any) -> dict[str, Any]:
        if player is None:
            return {"feed": True}
        seat = self.seats.get(player.id)
        if seat is None:
            return {}
        dug = seat.extra["dug"]
        return {
            "island": seat.extra["island"],
            "tiles": [{"i": i, "dug": dug.get(str(i))} for i in range(TILES)],
            "last": seat.extra["last"],
            "canDig": seat.step == "dig",
        }

    def bot_step(self, bot: Any, seat: Seat) -> None:
        if seat.step == "dig":
            free = [i for i in range(TILES) if str(i) not in seat.extra["dug"]]
            if free:
                self.act(bot, seat, "dig", {"tile": self.rng.choice(free)})
