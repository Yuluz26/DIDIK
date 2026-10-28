"""The waiting room's town square. Children appear at the arch when they join and walk wherever they
tap while the host gets ready; everyone sees everyone else on their own screen.

Positions are in tiles of the square drawn by the web app (LobbyPlaza.svelte, 16 x 9 tiles); keep
the walkable box, the fountain and the arch in step with that drawing.
"""

from __future__ import annotations

import math
import random

WIDTH, HEIGHT = 16.0, 9.0
# Nobody walks into the tree line at the top or off the edges.
LEFT, TOP, RIGHT, BOTTOM = 0.8, 3.4, 15.2, 8.6
# The fountain in the middle is an ellipse you walk around: its basin and the room a child takes up
# (half a child's width either side, their feet in front of or behind the rim).
FOUNTAIN_X, FOUNTAIN_Y, FOUNTAIN_RX, FOUNTAIN_RY = 8.0, 5.35, 1.75, 0.9
# Two children never stand on top of each other: closer than this (wider than tall, the way they
# stand side by side) and the one arriving steps aside.
APART_X, APART_Y = 0.85, 0.5
# Where new arrivals come in, just under the arch.
ARCH = (8.0, 3.5)
# The quickest a child can pick a new spot; taps in between are ignored.
WALK_EVERY = 0.25
# Practice bots stroll now and then: the chance per bot on each quarter-second tick.
BOT_STROLL_CHANCE = 0.035


def clamp(x: float, y: float) -> tuple[float, float]:
    """The nearest place a child can stand: inside the square and outside the fountain."""
    x = min(RIGHT, max(LEFT, x))
    y = min(BOTTOM, max(TOP, y))
    dx = (x - FOUNTAIN_X) / FOUNTAIN_RX
    dy = (y - FOUNTAIN_Y) / FOUNTAIN_RY
    reach = math.hypot(dx, dy)
    if reach < 1.0:
        if reach < 1e-6:
            dx, dy, reach = 0.0, 1.0, 1.0
        x = FOUNTAIN_X + dx / reach * FOUNTAIN_RX * 1.02
        y = FOUNTAIN_Y + dy / reach * FOUNTAIN_RY * 1.02
    return round(x, 2), round(y, 2)


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


def stroll(rng: random.Random, x: float, y: float) -> tuple[float, float]:
    """A bot's next spot: a few tiles from where it stands."""
    angle = rng.uniform(0, math.tau)
    distance = rng.uniform(1.0, 3.2)
    return clamp(x + math.cos(angle) * distance, y + math.sin(angle) * distance * 0.6)
