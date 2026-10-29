"""Every game a room can play, in the order the host sees them (eight classic 2D games, then Legenda,
the JRPG Story Mode). Any game suits any class; teachers and parents choose by taste."""

from __future__ import annotations

from .forest import ForestMode
from .garden import GardenMode
from .jump import JumpMode
from .legenda import LegendaMode
from .picture import PictureMode
from .race import RaceMode
from .teams import TeamsMode
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
        LegendaMode,
    )
}
