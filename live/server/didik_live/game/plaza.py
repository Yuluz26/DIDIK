"""The waiting room's town square. Children appear at the arch when they join and walk wherever they
tap while the host gets ready; everyone sees everyone else on their own screen.

Positions are in tiles of the square drawn by the web app (LobbyPlaza.svelte, 16 x 9 tiles); keep
the walkable box, the fountain, the other things in the way and the arch in step with that drawing.

Nobody stands in the fountain or on a lamp post, a bench, the arch's posts or the cat and the hen: a spot
inside one of them moves to just outside it. (The web app walks children round them too.)
"""

from __future__ import annotations

import math
import random

WIDTH, HEIGHT = 16.0, 9.0
# Nobody walks into the tree line at the top or off the edges.
LEFT, TOP, RIGHT, BOTTOM = 0.8, 3.4, 15.2, 8.6
# The fountain in the middle is an ellipse you walk around: its basin and the room a child takes up.
# A child is two tiles tall, so in front of the fountain they stand a full tile clear of its rim (else
# their body covers the water and they seem to stand in it); behind it, clear of its top; at the sides,
# half a child's width clear of the basin.
FOUNTAIN_X, FOUNTAIN_Y, FOUNTAIN_RX, FOUNTAIN_RY = 8.0, 5.6, 1.8, 1.35
# Everything else in the way, where it stands on the ground, as (x, y, half width, half depth) in tiles:
# the two lamp posts, the two benches, the arch's two posts, the cat by the right bench and the hen.
OBSTACLES: tuple[tuple[float, float, float, float], ...] = (
    (FOUNTAIN_X, FOUNTAIN_Y, FOUNTAIN_RX, FOUNTAIN_RY),
    (5.6, 4.2, 0.4, 0.3),
    (10.4, 4.2, 0.4, 0.3),
    (2.6, 4.45, 1.05, 0.4),
    (13.4, 4.45, 1.05, 0.4),
    (6.85, 3.4, 0.35, 0.3),
    (9.15, 3.4, 0.35, 0.3),
    (14.4, 4.8, 0.45, 0.3),
    (1.5, 7.3, 0.4, 0.3),
)
# Two children never stand on top of each other: closer than this (wider than tall, the way they
# stand side by side) and the one arriving steps aside.
APART_X, APART_Y = 0.85, 0.5
# Where new arrivals come in, just under the arch.
ARCH = (8.0, 3.5)
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


# Past this many children the newcomers spread over the whole square, so a full class is not one
# long row along the front.
CROWD = 16


def arrival(rng: random.Random, crowd: int = 0) -> tuple[float, float]:
    """A spot for someone who has just come in: the front of the square, or anywhere in it once
    the square is busy."""
    top = 6.3 if crowd < CROWD else TOP + 0.5
    return clamp(rng.uniform(LEFT + 1.0, RIGHT - 1.0), rng.uniform(top, BOTTOM - 0.2))


def free_arrival(rng: random.Random, others: list[tuple[float, float]]) -> tuple[float, float]:
    """A spot for a newcomer that is not on top of anyone: a few tries in the arrival area first,
    and only in a packed square the nearest free spot to one of them."""
    crowd = len(others)
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
