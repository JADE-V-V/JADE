from __future__ import annotations

from enum import Enum


class PlotType(Enum):
    BINNED = "Binned graph"
    RATIO = "Ratio graph"
    EXP = "Experimental points"
    EXP_GROUP = "Experimental points group"
    CE_EXP_GROUP = "Experimental points group CE"
    DISCRETE_EXP = "Discrete Experimental points"
    GROUPED_BARS = "Grouped bars"
    WAVES = "Waves"
