"""Every game a room can play, in the order the host sees them (fourteen 2D games, then Hikayat Lima
Alam, the story mode). Any game suits any class; teachers and parents choose by taste."""

from __future__ import annotations

from .fishing import FishingMode
from .forest import ForestMode
from .garden import GardenMode
from .jump import JumpMode
from .kite import KiteMode
from .legenda import LegendaMode
from .market import MarketMode
from .picture import PictureMode
from .race import RaceMode
from .sandcastle import SandcastleMode
from .stars import StarsMode
from .teams import TeamsMode
from .train import TrainMode
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
        FishingMode,
        KiteMode,
        SandcastleMode,
        TrainMode,
        MarketMode,
        StarsMode,
        LegendaMode,
    )
}
