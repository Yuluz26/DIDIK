"""Every game a room can play, in the order the host sees them."""

from __future__ import annotations

from .forest import ForestMode
from .garden import GardenMode
from .jump import JumpMode
from .picture import PictureMode
from .race import RaceMode
from .teams import TeamsMode
from .treasure import TreasureMode
from .village import VillageMode

MODES = {
    cls.key: cls
    for cls in (RaceMode, JumpMode, TreasureMode, ForestMode, TeamsMode, VillageMode, PictureMode, GardenMode)
}
