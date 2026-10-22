"""Hutan Misteri: the ZEP-style game. Every child walks their animal around one forest map and sees
friends walking too. Question chests are hidden around the map; a right answer at a chest gives a key,
and five keys open the forest gate. The first out earn the most, and everyone keeps exploring.

Movement is server-authoritative: phones send which way they are pushing, the server moves everyone
fifteen times a second with collisions, and positions go out ten times a second for smooth drawing.
"""

from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode, now_ms

# 32 x 20 tiles.  # tree   ~ water   = bridge   R rock (blocked)
#                 . grass  : path    f flowers  m mushroom   C chest   S start   G gate
FOREST = [
    "################################",
    "#SS.....:.....f.~~......f....C.#",
    "#SS..f..:..C....~~..........RR.#",
    "#.......:.......~~..m....:.....#",
    "#..::::::::::::==:::::::::.....#",
    "#..:....##......~~......:...C..#",
    "#C.:...###......~~......:......#",
    "#..:....#...f...~~..##..:...C..#",
    "#..:..........C.~~..##..:...f..#",
    "#..::::::::::::==:::::::::::...#",
    "#....m......RR..~~.:...f..##...#",
    "#~~~~~=~~~~~~~~~~~~=~~~~~~~~~~~#",
    "#~~~~~=~~~~~~~~~~~~=~~~~~~~~~~~#",
    "#..C..:.....C......:.......f...#",
    "#..##.:............:...m....##.#",
    "#..##.::::::::::::::::::::.C##.#",
    "#.f.......C...RR..........::...#",
    "#...........f.......C......:.GG#",
    "#..m..........C............:.GG#",
    "################################",
]
BLOCKED = set("#~R")
SPEED = 3.4  # tiles per second
RADIUS = 0.3
TICK = 1 / 15
REACH = 1.35
KEYS_NEEDED = 5
LOCK_SECONDS = 6.0
ESCAPE_BONUS = [600, 500, 400, 300, 200]


def tiles_of(kind: str) -> list[tuple[int, int]]:
    return [(x, y) for y, row in enumerate(FOREST) for x, ch in enumerate(row) if ch == kind]


CHESTS = [{"id": i, "x": x + 0.5, "y": y + 0.5} for i, (x, y) in enumerate(tiles_of("C"))]
SPAWNS = [(x + 0.5, y + 0.5) for x, y in tiles_of("S")]
GATE_TILES = tiles_of("G")
GATE = (
    sum(x for x, _ in GATE_TILES) / len(GATE_TILES) + 0.5,
    sum(y for _, y in GATE_TILES) / len(GATE_TILES) + 0.5,
)


def blocked(x: float, y: float) -> bool:
    tx, ty = int(math.floor(x)), int(math.floor(y))
    if ty < 0 or ty >= len(FOREST) or tx < 0 or tx >= len(FOREST[0]):
        return True
    return FOREST[ty][tx] in BLOCKED


def free(x: float, y: float) -> bool:
    return not any(blocked(x + dx, y + dy) for dx in (-RADIUS, RADIUS) for dy in (-RADIUS, RADIUS))


def slide(point: list[float], mx: float, my: float) -> None:
    """Moves in small steps so an avatar walks right up to a tree and slides along it."""
    steps = max(1, math.ceil(max(abs(mx), abs(my)) / 0.05))
    sx, sy = mx / steps, my / steps
    for _ in range(steps):
        if sx and free(point[0] + sx, point[1]):
            point[0] += sx
        if sy and free(point[0], point[1] + sy):
            point[1] += sy


def path(start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    """Breadth-first search over walkable tiles; used by the practice bots."""
    queue = deque([start])
    came: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        x, y = node
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in came and not blocked(nx + 0.5, ny + 0.5):
                came[(nx, ny)] = node
                queue.append((nx, ny))
    if goal not in came:
        return []
    route = []
    node: tuple[int, int] | None = goal
    while node is not None:
        route.append(node)
        node = came[node]
    return route[::-1]


class ForestMode(SelfPacedMode):
    key = "hutan"
    title = "Hutan Misteri"
    tagline = "Jelajah hutan bersama kawan, buka peti soalan dan kumpul lima kunci untuk keluar."
    how = "Gerakkan haiwanmu (anak panah atau kayu bedik). Dekati peti dan buka. Jawab betul untuk dapat kunci. Lima kunci membuka pintu hutan."
    style = "Jelajah"
    pace = "roam"
    world = "hutan"
    min_questions = 5
    saved = ("pos", "facing", "escaped")

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        # Live joystick input; after a restart everyone stands still until they push again.
        self.inputs: dict[str, tuple[float, float]] = {}
        self._last_pos = ""
        self.ticker: asyncio.Task | None = None

    def setup(self) -> None:
        self.pos: dict[str, list[float]] = {}
        self.facing: dict[str, int] = {}
        self.escaped: list[str] = []
        for index, player in enumerate(self.players()):
            self.place(player, index)

    def place(self, player: Any, index: int | None = None) -> None:
        index = len(self.pos) if index is None else index
        x, y = SPAWNS[index % len(SPAWNS)]
        # Spread a crowd a little so avatars do not sit exactly on top of each other.
        self.pos[player.id] = [x + (index // 4) * 0.15, y + (index // 4) * 0.1]
        self.facing[player.id] = 1

    def add_player(self, player: Any) -> None:
        self.place(player)
        super().add_player(player)

    def remove_player(self, player: Any) -> None:
        self.pos.pop(player.id, None)
        self.inputs.pop(player.id, None)

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(keys=0, opened=[], locked={}, chest=None)

    def seat(self, player: Any) -> Seat:
        # Unlike the other games, a child starts walking, not answering: no question until a chest.
        seat = self.seats.get(player.id)
        if seat is None:
            seat = self.seats[player.id] = Seat()
            self.new_seat(player, seat)
            seat.step = "explore"
        return seat

    async def run(self) -> None:
        self.ticker = asyncio.create_task(self.tick_forever())
        try:
            await super().run()
        finally:
            self.ticker.cancel()

    def goal_reached(self) -> bool:
        players = self.players()
        return bool(players) and len(self.escaped) >= len(players)

    # ------------------------------------------------------------ movement

    async def tick_forever(self) -> None:
        last_send = 0.0
        last_full = 0.0
        while not self.finished:
            await asyncio.sleep(TICK)
            if self.stage != "play" or self.paused:
                continue
            self.step(TICK)
            now = time.monotonic()
            if now - last_send >= 0.1:
                last_send = now
                # Once a second everyone gets positions even if nobody moved, so a phone that just
                # (re)connected draws the forest straight away.
                full = now - last_full >= 1.0
                if full:
                    last_full = now
                self.send_positions(force=full)

    def step(self, dt: float) -> None:
        for pid, (dx, dy) in list(self.inputs.items()):
            seat = self.seats.get(pid)
            point = self.pos.get(pid)
            if point is None or seat is None or seat.step != "explore" or (dx == 0 and dy == 0):
                continue
            length = math.hypot(dx, dy)
            slide(point, dx / length * SPEED * dt, dy / length * SPEED * dt)
            if dx:
                self.facing[pid] = 1 if dx > 0 else -1

    def send_positions(self, force: bool = False) -> None:
        data = [[pid, round(x, 2), round(y, 2), self.facing.get(pid, 1)] for pid, (x, y) in self.pos.items()]
        text = str(data)
        if text == self._last_pos and not force:
            return
        self._last_pos = text
        self.room.broadcast({"t": "pos", "p": data})

    # ------------------------------------------------------------ actions

    def handle(self, player: Any, kind: str, data: dict[str, Any]) -> None:
        if self.stage != "play":
            return
        if kind == "move":
            try:
                dx = max(-1.0, min(1.0, float(data.get("dx", 0))))
                dy = max(-1.0, min(1.0, float(data.get("dy", 0))))
            except (TypeError, ValueError):
                return
            self.inputs[player.id] = (dx, dy)
        else:
            super().handle(player, kind, data)

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None or player.id in self.escaped:
            return
        if kind == "open":
            self.open_chest(player, seat, data.get("chest"))
        elif kind == "escape":
            self.escape(player, seat)

    def near(self, player: Any, x: float, y: float, reach: float = REACH) -> bool:
        point = self.pos.get(player.id)
        return point is not None and math.hypot(point[0] - x, point[1] - y) <= reach

    def open_chest(self, player: Any, seat: Seat, chest_id: Any) -> None:
        if seat.step != "explore" or not isinstance(chest_id, int) or not 0 <= chest_id < len(CHESTS):
            return
        chest = CHESTS[chest_id]
        if chest_id in seat.extra["opened"] or not self.near(player, chest["x"], chest["y"]):
            return
        if now_ms() < seat.extra["locked"].get(str(chest_id), 0):
            return
        seat.extra["chest"] = chest_id
        self.inputs[player.id] = (0.0, 0.0)
        super().deal(seat)
        self.room.mark_dirty()

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        chest_id = seat.extra["chest"]
        seat.extra["chest"] = None
        if outcome.correct:
            seat.extra["keys"] += 1
            seat.extra["opened"].append(chest_id)
            player.score += 100
            return {"key": True, "keys": seat.extra["keys"]}
        seat.extra["locked"][str(chest_id)] = now_ms() + int(LOCK_SECONDS * 1000)
        return {"key": False, "lockedFor": LOCK_SECONDS}

    def act_next(self, player: Any) -> None:
        seat = self.seats.get(player.id)
        if seat is not None and seat.step == "result":
            seat.step = "explore"
            seat.pres = None
            seat.result = None
            self.room.mark_dirty()

    def escape(self, player: Any, seat: Seat) -> None:
        if seat.step != "explore" or seat.extra["keys"] < self.keys_needed() or not self.near(player, *GATE, reach=1.9):
            return
        order = len(self.escaped)
        bonus = ESCAPE_BONUS[order] if order < len(ESCAPE_BONUS) else 100
        self.escaped.append(player.id)
        player.score += bonus
        seat.step = "escaped"
        self.inputs[player.id] = (0.0, 0.0)
        self.room.feed(f"{player.nickname} berjaya keluar dari hutan! (#{order + 1})", "escape", player)
        self.room.fx({"kind": "escaped", "player": player.id, "order": order + 1, "bonus": bonus})
        self.room.mark_dirty()

    def keys_needed(self) -> int:
        return min(KEYS_NEEDED, len(CHESTS))

    # ------------------------------------------------------------ views

    def forest(self, player: Any | None) -> dict[str, Any]:
        view: dict[str, Any] = {
            "map": FOREST,
            "gate": {"x": GATE[0], "y": GATE[1]},
            "need": self.keys_needed(),
            "escaped": self.escaped,
            "positions": [[pid, round(x, 2), round(y, 2), self.facing.get(pid, 1)] for pid, (x, y) in self.pos.items()],
        }
        if player is None:
            opened = [0] * len(CHESTS)
            for seat in self.seats.values():
                for chest_id in seat.extra.get("opened", []):
                    opened[chest_id] += 1
            view["chests"] = [{**chest, "opened": opened[chest["id"]]} for chest in CHESTS]
            return view
        seat = self.seats.get(player.id)
        now = now_ms()
        opened_ids = seat.extra["opened"] if seat else []
        locked = seat.extra["locked"] if seat else {}
        view["chests"] = [
            {
                **chest,
                "state": "open" if chest["id"] in opened_ids else "locked" if now < locked.get(str(chest["id"]), 0) else "closed",
            }
            for chest in CHESTS
        ]
        view["keys"] = seat.extra["keys"] if seat else 0
        return view

    def world_view(self, player: Any) -> dict[str, Any]:
        return self.forest(player)

    def player_view(self, player: Any) -> dict[str, Any]:
        view = super().player_view(player)
        # Positions are streamed separately; keep them out of the view so it only changes on events.
        view["world"].pop("positions", None)
        return view

    def host_view(self) -> dict[str, Any]:
        view = super().host_view()
        view["world"].pop("positions", None)
        return view

    # ------------------------------------------------------------ bots

    def bot_tick(self, bot: Any, now: float) -> None:
        seat = self.seats.get(bot.id)
        if seat is None or self.stage != "play" or self.paused:
            return
        if seat.step in ("question", "result"):
            super().bot_tick(bot, now)
            return
        if seat.step != "explore" or bot.id not in self.pos:
            return
        x, y = self.pos[bot.id]
        here = (int(x), int(y))
        if seat.extra["keys"] >= self.keys_needed():
            if self.near(bot, *GATE, reach=1.8):
                self.escape(bot, seat)
                return
            target = GATE_TILES[0]
        else:
            choices = [
                c for c in CHESTS
                if c["id"] not in seat.extra["opened"] and now_ms() >= seat.extra["locked"].get(str(c["id"]), 0)
            ]
            if not choices:
                self.inputs[bot.id] = (0.0, 0.0)
                return
            chest = min(choices, key=lambda c: abs(c["x"] - x) + abs(c["y"] - y))
            if self.near(bot, chest["x"], chest["y"], reach=1.1):
                self.open_chest(bot, seat, chest["id"])
                seat.bot_at = now + self.rng.uniform(1.0, 2.5)
                return
            target = (int(chest["x"]), int(chest["y"]))
        route = path(here, target)
        if len(route) < 2:
            self.inputs[bot.id] = (0.0, 0.0)
            return
        nx, ny = route[1]
        self.inputs[bot.id] = (nx + 0.5 - x, ny + 0.5 - y)
