"""Pasar Malam: right answers bring stock for your stall at the night market. Sell it to the crowd for
ringgit, and spend ringgit on a lamp, an awning, a bright sign or music: each one makes everything
sell for a ringgit more and draws a bigger crowd. The score is everything ever earned.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat
from .collect import CollectMode

UPGRADES = {
    "lampu": {"name": "Lampu meriah", "cost": 10},
    "kanopi": {"name": "Kanopi berwarna", "cost": 20},
    "papan": {"name": "Papan tanda bercahaya", "cost": 35},
    "muzik": {"name": "Muzik ceria", "cost": 50},
}
GOODS = ["satay", "air", "kuih", "jagung", "aiskrim"]


class MarketMode(CollectMode):
    key = "pasar"
    title = "Pasar Malam"
    tagline = "Jawab betul untuk dapat barang jualan. Jual di gerai, hias gerai, jadi gerai paling meriah!"
    how = "Setiap jawapan betul memberi barang untuk dijual. Ketik Jual untuk dapat ringgit, kemudian hias gerai: setiap hiasan menaikkan harga dan menarik lebih ramai pelanggan."
    style = "Ikut kadar sendiri"
    world = "pasar"
    unit = "RM"

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(stock=2, cash=0, earned=0, upgrades=[], good=self.rng.choice(GOODS), sold=0)

    def price(self, seat: Seat) -> int:
        return 1 + len(seat.extra["upgrades"])

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"stock": 0}
        stock = 4 if seat.streak >= 3 else 3
        seat.extra["stock"] += stock
        return {"stock": stock}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None:
            return
        m = seat.extra
        if kind == "sell" and m["stock"] > 0:
            money = m["stock"] * self.price(seat)
            m["sold"] += m["stock"]
            m["stock"] = 0
            m["cash"] += money
            m["earned"] += money
            player.score = m["earned"]
            self.room.fx({"kind": "sold", "money": money}, to=player, hosts=False)
        elif kind == "upgrade":
            item = str(data.get("item"))
            spec = UPGRADES.get(item)
            if spec is None or item in m["upgrades"] or m["cash"] < spec["cost"]:
                return
            m["cash"] -= spec["cost"]
            m["upgrades"].append(item)
            if len(m["upgrades"]) == len(UPGRADES):
                self.room.feed(f"Gerai {player.nickname} paling meriah di pasar malam!", "market", player)
        else:
            return
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        if player is None:
            return {"upgrades": UPGRADES, "top": self.shared("top", lambda: self.best(3, ("upgrades", "good", "sold")))}
        seat = self.seats.get(player.id)
        if seat is None:
            return {"upgrades": UPGRADES, "stock": 0, "cash": 0, "earned": 0, "mine": [], "good": "satay", "price": 1, "sold": 0}
        m = seat.extra
        return {"upgrades": UPGRADES, "stock": m["stock"], "cash": m["cash"], "earned": m["earned"], "mine": m["upgrades"], "good": m["good"], "price": self.price(seat), "sold": m["sold"]}

    def bot_spend(self, bot: Any, seat: Seat) -> bool:
        m = seat.extra
        affordable = [k for k, u in UPGRADES.items() if k not in m["upgrades"] and u["cost"] <= m["cash"]]
        if affordable:
            self.act(bot, seat, "upgrade", {"item": affordable[0]})
        elif m["stock"] >= 3:
            self.act(bot, seat, "sell", {})
        else:
            return False
        return True
