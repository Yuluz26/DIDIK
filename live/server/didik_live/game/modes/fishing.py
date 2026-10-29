"""Pancing Ikan: a right answer is bait (three in a row, golden bait). Cast the line into the lake and
see what bites, from a bilis to the rare golden arowana. Golden bait never brings up an old boot and
makes the big fish likelier. The score is the worth of everything caught.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat
from .collect import CollectMode

# name, points, how often it bites (and how often with golden bait)
FISH = {
    "kasut": {"name": "Kasut buruk", "value": 0, "odds": 6, "gold": 0},
    "bilis": {"name": "Ikan Bilis", "value": 5, "odds": 30, "gold": 10},
    "puyu": {"name": "Ikan Puyu", "value": 10, "odds": 25, "gold": 14},
    "keli": {"name": "Ikan Keli", "value": 15, "odds": 18, "gold": 18},
    "patin": {"name": "Ikan Patin", "value": 25, "odds": 12, "gold": 22},
    "kelah": {"name": "Ikan Kelah", "value": 40, "odds": 6, "gold": 22},
    "arowana": {"name": "Arowana Emas", "value": 80, "odds": 2, "gold": 12},
}
NET = 8  # the latest catches a child sees in their bucket


class FishingMode(CollectMode):
    key = "pancing"
    title = "Pancing Ikan"
    tagline = "Jawab betul untuk dapat umpan, kemudian pancing di tasik. Siapa dapat Arowana Emas?"
    how = "Setiap jawapan betul memberi umpan. Ketik tasik untuk melempar joran. Tiga betul berturut-turut memberi umpan emas: ikan besar lebih kerap menyambar!"
    style = "Ikut kadar sendiri"
    world = "tasik"
    unit = "mata"

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(bait=1, gold=0, net=[], caught=0, best=None)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"bait": 0}
        golden = seat.streak >= 3 and seat.streak % 3 == 0
        seat.extra["gold" if golden else "bait"] += 1
        return {"bait": 1, "gold": golden}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None or kind != "cast":
            return
        f = seat.extra
        golden = bool(data.get("gold")) and f["gold"] > 0
        if not golden and f["bait"] < 1:
            return
        f["gold" if golden else "bait"] -= 1
        weights = [spec["gold" if golden else "odds"] for spec in FISH.values()]
        fish = self.rng.choices(list(FISH), weights=weights)[0]
        spec = FISH[fish]
        f["net"] = (f["net"] + [fish])[-NET:]
        f["caught"] += 1
        if spec["value"] and (f["best"] is None or spec["value"] > FISH[f["best"]]["value"]):
            f["best"] = fish
        player.score += spec["value"]
        self.room.fx({"kind": "catch", "fish": fish, "value": spec["value"], "gold": golden}, to=player, hosts=False)
        if fish == "arowana":
            self.room.feed(f"{player.nickname} memancing Arowana Emas!", "gold", player)
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        if player is None:
            return {"fish": FISH, "top": self.shared("top", lambda: self.best(3, ("best", "caught", "net")))}
        seat = self.seats.get(player.id)
        f = seat.extra if seat else {"bait": 0, "gold": 0, "net": [], "caught": 0, "best": None}
        return {"fish": FISH, "bait": f["bait"], "gold": f["gold"], "net": f["net"], "caught": f["caught"], "best": f["best"]}

    def bot_spend(self, bot: Any, seat: Seat) -> bool:
        f = seat.extra
        if f["gold"] or f["bait"]:
            self.act(bot, seat, "cast", {"gold": f["gold"] > 0})
            return True
        return False
