from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from jade.helper.aux_functions import PathLike


@dataclass
class ConfigAtlasProcessor:
    """Contains the configuration options for the atlas processor.

    Parameters
    -------
    benchmark : str
        Name of the benchmark.
    plots : list[PlotConfig]
        List of the plots to be generated for the benchmark. Each plot is defined by a
        PlotConfig object.
    """

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
    """Contains the configuration options for a plot.

    Parameters
    ----------
    name : str
        Name of the plot (for word text)
    results : list[int | str]
        List of the results to be plotted. These names should be the same as the ones
        used in the raw data files.
    plot_type : PlotType
        Type of the plot to be created.
    title : str
        Title of the plot. (Superior title in the figure)
    x_label : str
        Label for the x-axis.
    y_labels : list[str]
        Label(s) for the y-axis. If the plot has multiple y-axes, more than one label
        can be provided.
    x : str
        Name of the column to be used as x-axis.
    y : str
        Name of the column to be used as y-axis.
    expand_runs : bool, optional
        During the reading of the raw data, all results from different runs are
        concatenated in the same dataframe. If expand_runs is se to True (default)
        a different plot will be generated for each single run.
    plot_args : dict, optional
        Additional arguments to be passed to the plot function. These arguments are
        specific to each plot type.
    """

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
    plot_args: dict | None = None

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
            plot_args=dictionary.get("plot_args", None),
        )

    def __post_init__(self):
        # Ensure that y labels are always a list
        if not isinstance(self.y_labels, list):
            self.y_labels = [self.y_labels]


class PlotType(Enum):
    """Available plot types"""

    BINNED = "binned"
    # RATIO = "ratio"
    # EXP = "exp points"
    # EXP_GROUP = "exp points group"
    # CE_EXP_GROUP = "exp points group CE"
    # DISCRETE_EXP = "discrete exp points"
    # GROUPED_BARS = "grouped bars"
    # WAVES = "waves"
