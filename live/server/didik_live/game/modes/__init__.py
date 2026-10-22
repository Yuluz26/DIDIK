"""Every game a room can play, in the order the host sees them: the primary-school games first,
then the ones made for Tingkatan 1-5 (`level = "menengah"`)."""

from __future__ import annotations

from .forest import ForestMode
from .garden import GardenMode
from .jump import JumpMode
from .kart import KartMode
from .penalty import PenaltyMode
from .picture import PictureMode
from .pirate import PirateMode
from .race import RaceMode
from .teams import TeamsMode
from .tower import TowerMode
from .treasure import TreasureMode
from .village import VillageMode

MODES = {
    cls.key: cls
    for cls in (
        RaceMode,
        JumpMode,
        TreasureMode,
        ForestMode,
        TeamsMode,
        VillageMode,
        PictureMode,
        GardenMode,
        KartMode,
        PenaltyMode,
        PirateMode,
        TowerMode,
    )
}
