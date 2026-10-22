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
# The fountain in the middle is an ellipse you walk around.
FOUNTAIN_X, FOUNTAIN_Y, FOUNTAIN_RX, FOUNTAIN_RY = 8.0, 5.25, 1.45, 0.8
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


def arrival(rng: random.Random) -> tuple[float, float]:
    """A spot on the front of the square for someone who has just come in."""
    return clamp(rng.uniform(LEFT + 1.0, RIGHT - 1.0), rng.uniform(6.3, BOTTOM - 0.2))


def stroll(rng: random.Random, x: float, y: float) -> tuple[float, float]:
    """A bot's next spot: a few tiles from where it stands."""
    angle = rng.uniform(0, math.tau)
    distance = rng.uniform(1.0, 3.2)
    return clamp(x + math.cos(angle) * distance, y + math.sin(angle) * distance * 0.6)
