"""Peti Lanun: every right answer opens one of three chests on your ship.

All three chests are filled on the server before the child chooses, and all three open afterwards so
they see what they missed. Most chests hold gold and a few double it. When the host allows mischief,
a chest can also let you take a quarter of another ship's gold, swap gold with another ship, or lose
a quarter of yours to a storm. A ship that has just been robbed or swapped flies a shield for a short
while, so nobody is picked on again and again.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode, now_ms

CHESTS = 3
SHIELD_SECONDS = 20.0
GOLD = (10, 20, 30, 40, 50)
BIG = 100
DOUBLE_CAP = 300
LONE = 25  # gold instead, when there is no other ship to rob or swap with

# (kind, weight, naughty)
TABLE = [
    ("emas", 50, False),
    ("besar", 9, False),
    ("ganda", 6, False),
    ("curi", 15, True),
    ("tukar", 5, True),
    ("ribut", 8, True),
]


class PirateMode(SelfPacedMode):
    key = "lanun"
    title = "Peti Lanun"
    tagline = "Jawab betul, pilih satu daripada tiga peti. Emas, ganda dua, atau rampas emas kapal lain."
    how = "Setiap jawapan betul membuka satu peti. Kebanyakannya berisi emas; ada yang menggandakan emas kamu, dan ada yang membolehkan kamu merampas atau bertukar emas dengan kapal lain."
    style = "Ikut kadar sendiri"
    world = "lanun"
    look = "3d"
    unit = "emas"
    saved = ("shields",)

    def setup(self) -> None:
        self.shields: dict[str, int] = {}  # player id -> when the shield drops (epoch ms)

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(chests=None, opened=None, pending=None)

    # ------------------------------------------------------------ chests

    def roll(self) -> dict[str, Any]:
        table = [(kind, weight) for kind, weight, naughty in TABLE if self.settings.naughty or not naughty]
        kind = self.rng.choices([k for k, _ in table], weights=[w for _, w in table])[0]
        if kind == "emas":
            return {"kind": kind, "amount": self.rng.choice(GOLD)}
        if kind == "besar":
            return {"kind": kind, "amount": BIG}
        return {"kind": kind}

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return None
        seat.extra.update(chests=[self.roll() for _ in range(CHESTS)], opened=None, pending=None)
        seat.step = "chest"
        return {"kind": "chest"}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None:
            return
        if kind == "open" and seat.step == "chest":
            self.open_chest(player, seat, data.get("chest"))
        elif kind == "target" and seat.step == "target":
            self.plunder(player, seat, data.get("player"))
        elif kind == "keep" and seat.step == "target":
            self.keep(player, seat)

    def open_chest(self, player: Any, seat: Seat, raw: Any) -> None:
        if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw < CHESTS:
            return
        found = dict(seat.extra["chests"][raw])
        seat.extra["opened"] = raw
        if found["kind"] in ("curi", "tukar"):
            if self.targets(player, found["kind"]):
                seat.extra["pending"] = found["kind"]
                seat.step = "target"
                self.room.mark_dirty()
                return
            found = {"kind": "emas", "amount": LONE, "alone": True}
            seat.extra["chests"][raw] = found
        self.apply(player, seat, found)

    def apply(self, player: Any, seat: Seat, found: dict[str, Any]) -> None:
        kind = found["kind"]
        if kind in ("emas", "besar"):
            gain = found["amount"]
        elif kind == "ganda":
            gain = min(max(player.score, 20), DOUBLE_CAP)
        elif kind == "ribut":
            gain = -(player.score // 4)
        else:
            gain = 0
        player.score = max(0, player.score + gain)
        self.finish(seat, {**found, "gain": gain})

    def finish(self, seat: Seat, found: dict[str, Any]) -> None:
        seat.extra["pending"] = None
        seat.step = "result"
        if seat.result is not None:
            seat.result["reward"] = {**found, "chest": seat.extra["opened"]}
        self.room.mark_dirty()

    # ------------------------------------------------------------ other ships

    def shielded(self, player_id: str) -> bool:
        return self.shields.get(player_id, 0) > now_ms()

    def targets(self, player: Any, kind: str) -> list[Any]:
        """Ships this child may rob (those with gold) or swap with, leaving out shielded ones."""
        return [
            p
            for p in self.players()
            if p.id != player.id and not self.shielded(p.id) and (kind == "tukar" or p.score > 0)
        ]

    def plunder(self, player: Any, seat: Seat, target: Any) -> None:
        kind = seat.extra["pending"]
        victim = self.room.players.get(target) if isinstance(target, str) else None
        if victim is None or victim not in self.targets(player, kind):
            return
        if kind == "curi":
            amount = max(1, victim.score // 4)
            victim.score -= amount
            player.score += amount
            found = {"kind": kind, "gain": amount, "other": victim.id}
            self.room.feed(f"{player.nickname} merampas {amount} emas daripada {victim.nickname}!", "steal", player)
        else:
            gain = victim.score - player.score
            player.score, victim.score = victim.score, player.score
            found = {"kind": kind, "gain": gain, "other": victim.id}
            self.room.feed(f"{player.nickname} bertukar emas dengan {victim.nickname}!", "swap", player)
        self.shields[victim.id] = now_ms() + int(SHIELD_SECONDS * 1000)
        self.room.fx({"kind": "plunder", "by": player.id, "from": victim.id, "swap": kind == "tukar", "amount": abs(found["gain"])}, to=victim)
        self.finish(seat, found)

    def keep(self, player: Any, seat: Seat) -> None:
        """Choosing not to swap; or, when every ship worth robbing is shielded, gold instead."""
        kind = seat.extra["pending"]
        if kind == "curi":
            if self.targets(player, kind):
                return
            player.score += LONE
            self.finish(seat, {"kind": "emas", "amount": LONE, "gain": LONE, "alone": True})
        else:
            self.finish(seat, {"kind": "tukar", "gain": 0, "other": None})

    # ------------------------------------------------------------ views

    def shield_until(self, player_id: str) -> int | None:
        return self.shields[player_id] if self.shielded(player_id) else None

    def world_view(self, player: Any) -> dict[str, Any]:
        if player is None:
            return {"fleet": True}
        seat = self.seats.get(player.id)
        if seat is None:
            return {}
        view: dict[str, Any] = {"shieldUntil": self.shield_until(player.id)}
        if seat.extra["opened"] is not None and seat.step in ("target", "result"):
            view["opened"] = seat.extra["opened"]
            view["chests"] = seat.extra["chests"]
        if seat.step == "target":
            kind = seat.extra["pending"]
            view["pending"] = kind
            view["targets"] = [
                {"id": p.id, "gold": p.score, "shieldUntil": self.shield_until(p.id)}
                for p in sorted(self.players(), key=lambda p: -p.score)
                if p.id != player.id and (kind == "tukar" or p.score > 0)
            ]
        return view

    # ------------------------------------------------------------ practice bots

    def bot_step(self, bot: Any, seat: Seat) -> None:
        if seat.step == "chest":
            self.open_chest(bot, seat, self.rng.randrange(CHESTS))
        elif seat.step == "target":
            options = self.targets(bot, seat.extra["pending"])
            if seat.extra["pending"] == "tukar":
                options = [p for p in options if p.score > bot.score]
            if options:
                self.plunder(bot, seat, max(options, key=lambda p: p.score).id)
            else:
                self.keep(bot, seat)
