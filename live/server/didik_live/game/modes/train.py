"""Kereta Api Kampung: right answers are coal for your little steam train. Spend coal on another
carriage, or to run to the next station; the longer the train, the more passengers ride and the more
kilometres each run counts. The score is kilometres travelled.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat
from .collect import CollectMode

STATIONS = ["Kampung Durian", "Pekan Rambutan", "Bukit Merah", "Tanjung Kelapa", "Kuala Sungai", "Bandar Bunga Raya"]
CAR_COST = 3
RUN_COST = 2
KM_PER_CAR = 10
MAX_CARS = 8


class TrainMode(CollectMode):
    key = "keretapi"
    title = "Kereta Api Kampung"
    tagline = "Jawab betul untuk dapat arang. Tambah gerabak dan bawa penumpang dari stesen ke stesen!"
    how = "Setiap jawapan betul memberi arang. Arang menambah gerabak atau menjalankan kereta api ke stesen seterusnya. Lebih banyak gerabak, lebih jauh perjalanan dikira."
    style = "Ikut kadar sendiri"
    world = "landasan"
    unit = "km"

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(coal=2, cars=1, station=0, runs=0)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"coal": 0}
        coal = 3 if seat.streak >= 3 else 2
        seat.extra["coal"] += coal
        return {"coal": coal}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None:
            return
        t = seat.extra
        if kind == "car" and t["coal"] >= CAR_COST and t["cars"] < MAX_CARS:
            t["coal"] -= CAR_COST
            t["cars"] += 1
        elif kind == "go" and t["coal"] >= RUN_COST:
            t["coal"] -= RUN_COST
            t["station"] = (t["station"] + 1) % len(STATIONS)
            t["runs"] += 1
            km = KM_PER_CAR * t["cars"]
            player.score += km
            self.room.fx({"kind": "arrive", "station": t["station"], "km": km}, to=player, hosts=False)
            if t["cars"] == MAX_CARS and t["runs"] % 3 == 0:
                self.room.feed(f"Kereta api panjang {player.nickname} tiba di {STATIONS[t['station']]}!", "train", player)
        else:
            return
        self.room.mark_dirty()

    def world_view(self, player: Any) -> dict[str, Any]:
        shared = {"stations": STATIONS, "carCost": CAR_COST, "runCost": RUN_COST, "kmPerCar": KM_PER_CAR, "maxCars": MAX_CARS}
        if player is None:
            return {**shared, "top": self.shared("top", lambda: self.best(3, ("cars", "station")))}
        seat = self.seats.get(player.id)
        t = seat.extra if seat else {"coal": 0, "cars": 1, "station": 0, "runs": 0}
        return {**shared, "coal": t["coal"], "cars": t["cars"], "station": t["station"], "runs": t["runs"]}

    def bot_spend(self, bot: Any, seat: Seat) -> bool:
        t = seat.extra
        if t["cars"] < 4 and t["coal"] >= CAR_COST:
            self.act(bot, seat, "car", {})
        elif t["coal"] >= RUN_COST:
            self.act(bot, seat, "go", {})
        else:
            return False
        return True
