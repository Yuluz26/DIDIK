"""Kebun Ajaib: right answers bring water. Plant seeds, water them until they fruit, harvest for
coins, and spend coins on better seeds, fertiliser or more land.

The score is everything ever harvested, so spending on a durian tree is an investment, not a loss.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode

CROPS = {
    "bunga": {"name": "Bunga Raya", "cost": 0, "water": 2, "value": 15},
    "cili": {"name": "Cili", "cost": 10, "water": 3, "value": 35},
    "jagung": {"name": "Jagung", "cost": 20, "water": 3, "value": 55},
    "tembikai": {"name": "Tembikai", "cost": 35, "water": 4, "value": 100},
    "durian": {"name": "Durian", "cost": 60, "water": 5, "value": 200},
}
SHOP = {
    "baja": {"name": "Baja ajaib", "cost": 30, "note": "Tiga siraman seterusnya dikira dua kali."},
    "tanah": {"name": "Tanah baharu", "cost": 50, "note": "Satu batas tanaman lagi (paling banyak 9)."},
}
START_PLOTS = 6
MAX_PLOTS = 9


class GardenMode(SelfPacedMode):
    key = "kebun"
    title = "Kebun Ajaib"
    tagline = "Jawab untuk dapat air. Tanam, siram dan tuai. Kebun siapa paling subur?"
    how = "Setiap jawapan betul memberi titisan air. Tanam benih, siram sampai berbuah, kemudian tuai untuk dapat syiling."
    style = "Ikut kadar sendiri"
    world = "kebun"

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(coins=20, water=1, plots=[None] * START_PLOTS, earned=0, fert=0, harvests=0)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"water": 0}
        drops = 3 if seat.streak >= 3 else 2
        seat.extra["water"] += drops
        return {"water": drops}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None:
            return
        g = seat.extra
        plots: list[dict[str, Any] | None] = g["plots"]
        index = data.get("plot")
        plot = plots[index] if isinstance(index, int) and 0 <= index < len(plots) else "none"

        if kind == "plant" and plot is None:
            crop = CROPS.get(str(data.get("crop")))
            if crop is None or g["coins"] < crop["cost"]:
                return
            g["coins"] -= crop["cost"]
            plots[index] = {"crop": data["crop"], "stage": 0}
        elif kind == "water" and isinstance(plot, dict):
            need = CROPS[plot["crop"]]["water"]
            if g["water"] < 1 or plot["stage"] >= need:
                return
            g["water"] -= 1
            plot["stage"] = min(need, plot["stage"] + (2 if g["fert"] > 0 else 1))
            if g["fert"] > 0:
                g["fert"] -= 1
        elif kind == "harvest" and isinstance(plot, dict):
            crop = CROPS[plot["crop"]]
            if plot["stage"] < crop["water"]:
                return
            g["coins"] += crop["value"]
            g["earned"] += crop["value"]
            g["harvests"] += 1
            player.score = g["earned"]
            plots[index] = None
            self.room.fx({"kind": "harvest", "plot": index, "crop": plot["crop"], "value": crop["value"]}, to=player, hosts=False)
            if plot["crop"] == "durian":
                self.room.feed(f"{player.nickname} menuai durian!", "durian", player)
        elif kind == "buy":
            item = SHOP.get(str(data.get("item")))
            if item is None or g["coins"] < item["cost"]:
                return
            if data["item"] == "tanah":
                if len(plots) >= MAX_PLOTS:
                    return
                plots.append(None)
            else:
                g["fert"] += 3
            g["coins"] -= item["cost"]
        else:
            return
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        if player is None:
            return {"top": self.top_gardens()}
        seat = self.seats.get(player.id)
        if seat is None:
            return {"crops": CROPS, "shop": SHOP}
        g = seat.extra
        return {
            "coins": g["coins"],
            "water": g["water"],
            "fert": g["fert"],
            "earned": g["earned"],
            "plots": g["plots"],
            "maxPlots": MAX_PLOTS,
            "crops": CROPS,
            "shop": SHOP,
        }

    def top_gardens(self) -> list[dict[str, Any]]:
        best = sorted(self.players(), key=lambda p: -p.score)[:3]
        return [{"id": p.id, "plots": self.seats[p.id].extra["plots"]} for p in best if p.id in self.seats]

    # ------------------------------------------------------------ bots

    def bot_tick(self, bot: Any, now: float) -> None:
        seat = self.seats.get(bot.id)
        if seat is None or self.stage != "play" or now < seat.bot_at or seat.step != "result":
            super().bot_tick(bot, now)
            return
        g = seat.extra
        plots = g["plots"]
        for index, plot in enumerate(plots):
            if plot and plot["stage"] >= CROPS[plot["crop"]]["water"]:
                self.act(bot, seat, "harvest", {"plot": index})
                seat.bot_at = now + 0.6
                return
        for index, plot in enumerate(plots):
            if plot and g["water"] > 0 and plot["stage"] < CROPS[plot["crop"]]["water"]:
                self.act(bot, seat, "water", {"plot": index})
                seat.bot_at = now + 0.5
                return
        if None in plots:
            affordable = [k for k, c in CROPS.items() if c["cost"] <= g["coins"]]
            if affordable:
                self.act(bot, seat, "plant", {"plot": plots.index(None), "crop": max(affordable, key=lambda k: CROPS[k]["cost"])})
                seat.bot_at = now + 0.5
                return
        super().bot_tick(bot, now)
