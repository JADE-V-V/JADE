from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from jade.helper.aux_functions import PathLike


@dataclass
class ConfigAtlasProcessor:
    benchmark: str
    plots: list[PlotConfig]

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> ConfigAtlasProcessor:
        """Create a ConfigExcelProcessor object from a yaml file.

        Parameters
        ----------
        config_file : PathLike
            path to the configuration file

        Returns
        -------
        ConfigAtlasProcessor
            The configuration object
        """
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        benchmark = Path(config_file).name.split(".")[0]

        plots = []
        for table_name, dict in cfg.items():
            plots.append(PlotConfig.from_dict(dict, table_name))

        return cls(benchmark=benchmark, plots=plots)


@dataclass
class PlotConfig:
    name: str
    results: list[int | str]
    plot_type: PlotType
    title: str
    x_label: str
    y_labels: list[str]
    x: str
    y: str
    # optionals
    expand_runs: bool = True

    @classmethod
    def from_dict(cls, dictionary: dict, name: str) -> PlotConfig:
        return cls(
            name=name,
            results=dictionary["results"],
            plot_type=PlotType(dictionary["plot_type"]),
            title=dictionary["title"],
            x_label=dictionary["x_label"],
            y_labels=dictionary["y_labels"],
            x=dictionary["x"],
            y=dictionary["y"],
            expand_runs=dictionary.get("expand_runs", True),
        )

    def __post_init__(self):
        # Ensure that y labels are always a list
        if not isinstance(self.y_labels, list):
            self.y_labels = [self.y_labels]


class PlotType(Enum):
    BINNED = "binned"
    RATIO = "ratio"
    EXP = "exp points"
    EXP_GROUP = "exp points group"
    CE_EXP_GROUP = "exp points group CE"
    DISCRETE_EXP = "discrete exp points"
    GROUPED_BARS = "grouped bars"
    WAVES = "waves"
