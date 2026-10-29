"""What a host can change before opening a room."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TIMING_SCALE = {"normal": 1.0, "longer": 1.5, "relaxed": 2.0}


class RoomSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Question timers: as written, half as long again, or twice as long (WCAG 2.2.1).
    timing: Literal["normal", "longer", "relaxed"] = "normal"
    # Length of the games where everyone plays at their own pace.
    minutes: int = Field(default=5, ge=2, le=20)
    # Limit on questions in the games everyone answers together (None means the whole quiz).
    question_limit: int | None = Field(default=None, ge=3, le=60)
    shuffle: bool = True
    # Children may type their own name (checked for length, characters and rude words); a host can
    # switch to suggested names only.
    custom_names: bool = True
    waiting_room: bool = False
    late_join: bool = True
    # 1 opens a Solo room (one child; Legenda offers it), otherwise a Party room.
    max_players: int = Field(default=60, ge=1, le=100)
    # Surprises that take points away (a parrot that steals, a crab that pinches).
    naughty: bool = True
