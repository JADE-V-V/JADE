from __future__ import annotations

from dataclasses import dataclass

from jade.post.plotter import PlotType


@dataclass
class ConfigAtlasProcessor:
    plots: list[PlotConfig]


@dataclass
class PlotConfig:
    results: list[int | str]
    plot_type: PlotType
