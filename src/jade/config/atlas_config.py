from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from jade.helper.aux_functions import PathLike
from jade.helper.errors import ConfigError


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
        for plot_name, dict in cfg.items():
            # skip plots that start with _, they are aliases
            if plot_name.startswith("_"):
                continue
            plots.append(PlotConfig.from_dict(dict, plot_name))

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
    additional_labels : dict[str, list[tuple[str, float]]], optional
        Additional labels to be added to the plot. The dictionary keys are the type of
        label (major or minor) and the values are lists of tuples with the label and
        the position in the plot.
    v_lines : dict[str, list[float]], optional
        Vertical lines to be added to the plot. The dictionary keys are the type of
        line (major or minor) and the values are lists with the position of the lines.
    recs : list[tuple[str, str, float, float]], optional
        Rectangles to be added to the plot. Each tuple contains the label, the color,
        the xmin position and the xmax position of the rectangle.
    subsets : list[dict], optional
        List of dictionaries with the column and values to be used as a subset of a
        specific result. Each dictionary should have the keys "result", "column" and "values".
    select_runs : re.Pattern, optional
        Regular expression to select only the runs that match the pattern.
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
    additional_labels: dict[str, list[tuple[str, float]]] | None = None
    v_lines: dict[str, list[float]] | None = None
    recs: list[tuple[str, str, float, float]] | None = None
    subsets: list[dict] | None = None
    select_runs: re.Pattern | None = None

    @classmethod
    def from_dict(cls, dictionary: dict, name: str) -> PlotConfig:
        select_runs = dictionary.get("select_runs", None)
        if select_runs is not None:
            select_runs = re.compile(select_runs)
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
            additional_labels=dictionary.get("additional_labels", None),
            v_lines=dictionary.get("v_lines", None),
            recs=dictionary.get("recs", None),
            subsets=dictionary.get("subsets", None),
            select_runs=select_runs,
        )

    def __post_init__(self):
        # Ensure that y labels are always a list
        if not isinstance(self.y_labels, list):
            self.y_labels = [self.y_labels]

        # Ensure correct format of additional labels if present
        if self.additional_labels is not None:
            try:
                for key in self.additional_labels.keys():
                    assert key in ["major", "minor"]
                    assert isinstance(self.additional_labels[key], list)
                    for label, position in self.additional_labels[key]:
                        assert isinstance(label, str)
                        assert isinstance(position, float) or isinstance(position, int)
            except AssertionError:
                raise ConfigError("Invalid format for 'additional_labels'")

        # Ensure correct format of v_lines if present
        if self.v_lines is not None:
            try:
                for key in self.v_lines.keys():
                    assert key in ["major", "minor"]
                    assert isinstance(self.v_lines[key], list)
                    for line in self.v_lines[key]:
                        assert isinstance(line, float) or isinstance(line, int)
            except AssertionError:
                raise ConfigError("Invalid format for 'v_lines'")

        # Ensure correct format of recs if present
        if self.recs is not None:
            try:
                for rec in self.recs:
                    assert len(rec) == 4
                    assert isinstance(rec[0], str)
                    assert isinstance(rec[1], str)
                    assert isinstance(rec[2], float) or isinstance(rec[2], int)
                    assert isinstance(rec[3], float) or isinstance(rec[3], int)
            except AssertionError:
                raise ConfigError("Invalid format for 'recs'")


class PlotType(Enum):
    """Available plot types"""

    BINNED = "binned"
    RATIO = "ratio"
    CE = "ce"
    DOSE_CONTRIBUTION = "dose contribution"
    WAVES = "waves"
    BARPLOT = "barplot"
