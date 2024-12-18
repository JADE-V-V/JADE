from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import yaml
import os
from jade.helper.aux_functions import PathLike
from jade.post.excel_routines import ComparisonType, TableType
from jade.post.plotter import PlotType


class PostProcessConfig:
    def __init__(self, root_cfg_pp: PathLike):
        # get all available config excel processors
        excel_cfgs = {}
        for file in os.listdir(Path(root_cfg_pp, "excel")):
            if file.endswith(".yaml") or file.endswith(".yml"):
                cfg = ConfigExcelProcessor.from_yaml(Path(root_cfg_pp, file))
                excel_cfgs[cfg.benchmark] = cfg
        self.excel_cfgs = excel_cfgs
        # TODO get all available config atlas processors


@dataclass
class ConfigExcelProcessor:
    benchmark: str
    tables: list[TableConfig]

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> ConfigExcelProcessor:
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        benchmark = Path(config_file).name.split(".")[0]

        tables = []
        for table_name, dict in cfg.items():
            tables.append(TableConfig.from_dict(dict, table_name))

        return cls(benchmark=benchmark, tables=tables)


@dataclass
class ConfigAtlasProcessor:
    plots: list[PlotConfig]


@dataclass
class PlotConfig:
    results: list[int | str]
    plot_type: PlotType


@dataclass
class TableConfig:
    name: str
    results: list[int | str]
    table_type: TableType
    comparison_type: ComparisonType
    x: list[str]
    y: list[str]
    value: str | None = None  # used for pivot tables
    add_error: bool = False  # add single error sheets to the tables

    @classmethod
    def from_dict(cls, dictionary: dict, name) -> TableConfig:
        return cls(
            name=name,
            results=dictionary["results"],
            table_type=TableType(dictionary["table_type"]),
            comparison_type=ComparisonType(dictionary["comparison_type"]),
            x=dictionary["x"],
            y=dictionary["y"],
            value=dictionary.get("value"),
            add_error=dictionary.get("add_error", False),
        )


class ConfigRawProcessor:
    def __init__(self, results: list[ResultConfig]) -> None:
        """Config for the post-processing of the tallies into raw results.

        Parameters
        ----------
        results : list[ResultConfig]
            List of results to build from the simulation tallies.
        """
        self.results = results

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> ConfigRawProcessor:
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        results = []
        for res_name, dict in cfg.items():
            results.append(ResultConfig.from_dict(dict, res_name))

        return ConfigRawProcessor(results)


@dataclass
class ResultConfig:
    """A Result is a combination of one or more tallies. This configures how to build
    it from the tallies of the simulation.

    Parameters
    ----------
    name : int
        Unique identifier of the result
    modify : dict[int, list[tuple[TallyModOption, dict]]]
        dictionary of tallies to be modified. For each specify the list of modifications
        to apply. For each modification, the keyarguments to pass to the modification
        function should also be provided.
    concat_option : TallyConcatOption
        How to combine the tallies
    """

    name: int
    modify: dict[int, list[tuple[TallyModOption, dict]]]
    concat_option: TallyConcatOption

    @classmethod
    def from_dict(cls, dictionary: dict, name) -> ResultConfig:
        mods = {}
        concat_option = TallyConcatOption(dictionary.pop("concat_option"))
        for tallyid, modifications in dictionary.items():
            new_modifications = []
            for option, keyargs in modifications:
                mod_option = TallyModOption(option)
                new_modifications.append((mod_option, keyargs))
            mods[tallyid] = new_modifications

        return ResultConfig(
            name=name,
            modify=mods,
            concat_option=concat_option,
        )


class TallyModOption(Enum):
    """Available options to modify the tally dataframes."""

    LETHARGY = "lethargy"
    SCALE = "scale"
    NO_ACTION = "no_action"
    BY_ENERGY = "by_energy"
    CONDENSE_GROUPS = "condense_groups"


class TallyConcatOption(Enum):
    """Available options to concatenate different tally dataframes"""

    SUM = "sum"
    CONCAT = "concat"
    NO_ACTION = "no_action"
    SUBTRACT = "subtract"
    RATIO = "ratio"
