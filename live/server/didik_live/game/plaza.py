"""Positions and furniture collision for the pixel classroom waiting room.

Keep these tile coordinates in step with LobbyPlaza.svelte. A tap on a desk can send a pupil
to its chair; everyone can also walk around the desks while waiting for the host.
"""

from __future__ import annotations

import math
import random

WIDTH, HEIGHT = 16.0, 9.0
LEFT, TOP, RIGHT, BOTTOM = 0.7, 3.4, 15.3, 8.6
TEACHER_DESK = (8.0, 4.15, 1.55, 0.4)
SEATS = ((2.45, 5.25), (6.15, 5.25), (9.85, 5.25), (13.55, 5.25),
         (2.45, 7.25), (6.15, 7.25), (9.85, 7.25), (13.55, 7.25))
# Each obstacle is the footprint of a desk; chairs remain reachable behind the desks.
OBSTACLES: tuple[tuple[float, float, float, float], ...] = (
    TEACHER_DESK,
    *((x, y + 0.70, 0.95, 0.34) for x, y in SEATS),
)
# Two children never stand on top of each other: closer than this (wider than tall, the way they
# stand side by side) and the one arriving steps aside.
APART_X, APART_Y = 0.85, 0.5
ARCH = (1.2, 3.6)
# The quickest a child can pick a new spot; taps in between are ignored.
WALK_EVERY = 0.25
# Practice bots stroll now and then: the chance per bot on each quarter-second tick.
BOT_STROLL_CHANCE = 0.035


def _box(x: float, y: float) -> tuple[float, float]:
    return min(RIGHT, max(LEFT, x)), min(BOTTOM, max(TOP, y))


def clamp(x: float, y: float) -> tuple[float, float]:
    """The nearest place a child can stand: inside the square and outside the fountain and everything
    else in the way."""
    x, y = _box(x, y)
    for _ in range(4):
        moved = False
        for ox, oy, rx, ry in OBSTACLES:
            dx, dy = (x - ox) / rx, (y - oy) / ry
            reach = math.hypot(dx, dy)
            if reach < 1.0:
                if reach < 1e-6:
                    dx, dy, reach = 0.0, 1.0, 1.0
                x, y = _box(ox + dx / reach * rx * 1.04, oy + dy / reach * ry * 1.04)
                moved = True
        if not moved:
            break
    x, y = round(x, 2), round(y, 2)
    if not _free(x, y):
        # between two things that touch (the cat by its bench): the nearest free spot round about
        for step in range(1, 40):
            r = step * 0.1
            ring = [_box(round(x + r * math.cos(a), 2), round(y + r * math.sin(a), 2)) for a in (i * math.tau / 16 for i in range(16))]
            free = [spot for spot in ring if _free(*spot)]
            if free:
                return min(free, key=lambda spot: math.hypot(spot[0] - x, spot[1] - y))
    return x, y


def _free(x: float, y: float) -> bool:
    return all(((x - ox) / rx) ** 2 + ((y - oy) / ry) ** 2 >= 1 for ox, oy, rx, ry in OBSTACLES)


def apart(x: float, y: float, others: list[tuple[float, float]]) -> tuple[float, float]:
    """The nearest spot to (x, y) that is not on top of another child (and still inside the square,
    outside the fountain). In a packed square it does the best it can."""
    for _ in range(8):
        near = next(((ox, oy) for ox, oy in others if ((x - ox) / APART_X) ** 2 + ((y - oy) / APART_Y) ** 2 < 1), None)
        if near is None:
            break
        ox, oy = near
        dx, dy = x - ox, y - oy
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            dx = 1.0 if ox < (LEFT + RIGHT) / 2 else -1.0
        reach = math.hypot(dx / APART_X, dy / APART_Y)
        x, y = clamp(ox + dx / reach * 1.05, oy + dy / reach * 1.05)
    return x, y


# Once the desks are full, arrivals use free floor space.
CROWD = len(SEATS)


def arrival(rng: random.Random, crowd: int = 0) -> tuple[float, float]:
    """A free floor spot for a crowded classroom."""
    top = TOP + 0.5
    return clamp(rng.uniform(LEFT + 1.0, RIGHT - 1.0), rng.uniform(top, BOTTOM - 0.2))


def free_arrival(rng: random.Random, others: list[tuple[float, float]]) -> tuple[float, float]:
    """Seat newcomers at an open desk first, then find floor space when the desks are full."""
    crowd = len(others)
    seats = list(SEATS)
    rng.shuffle(seats)
    for x, y in seats:
        if all(((x - ox) / APART_X) ** 2 + ((y - oy) / APART_Y) ** 2 >= 1 for ox, oy in others):
            return x, y
    for _ in range(16):
        x, y = arrival(rng, crowd)
        if all(((x - ox) / APART_X) ** 2 + ((y - oy) / APART_Y) ** 2 >= 1 for ox, oy in others):
            return x, y
    return apart(*arrival(rng, crowd), others)


def stroll(rng: random.Random, x: float, y: float) -> tuple[float, float]:
    """A bot's next spot: a few tiles from where it stands."""
    angle = rng.uniform(0, math.tau)
    distance = rng.uniform(1.0, 3.2)
    return clamp(x + math.cos(angle) * distance, y + math.sin(angle) * distance * 0.6)
