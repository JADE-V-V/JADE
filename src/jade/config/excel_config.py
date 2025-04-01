from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from jade.helper.aux_functions import PathLike


class TableType(Enum):
    """Type of table to be created"""

    PIVOT = "pivot"
    SIMPLE = "simple"


class ComparisonType(Enum):
    """Comparison type for the tables"""

    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"
    RATIO = "ratio"


@dataclass
class ConfigExcelProcessor:
    """Configuration for the excel processor.

    Parameters
    ----------
    benchmark : str
        Name of the benchmark
    tables : list[TableConfig]
        List of tables configurations
    """

    benchmark: str
    tables: list[TableConfig]

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> ConfigExcelProcessor:
        """Create a ConfigExcelProcessor object from a yaml file.

        Parameters
        ----------
        config_file : PathLike
            path to the configuration file

        Returns
        -------
        ConfigExcelProcessor
            The configuration object
        """
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        benchmark = Path(config_file).name.split(".")[0]

        tables = []
        for table_name, dict in cfg.items():
            tables.append(TableConfig.from_dict(dict, table_name))

        return cls(benchmark=benchmark, tables=tables)


@dataclass
class TableConfig:
    """Configuration for a table.

    Parameters
    ----------
    name : str
        Name of the table
    results : list[int | str]
        List of results to compare
    table_type : TableType
        Type of table to be created
    comparison_type : ComparisonType
        Comparison type for the tables
    x : list[str]
        List of x-axis labels
    y : list[str]
        List of y-axis labels
    value : str | None, optional
        Value to pivot the table (used only for pivot tables), by default None
    add_error : bool, optional
        Add single error sheets to the tables, by default False
    conditional_formatting : dict[str, float] | None, optional
        Conditional formatting dictionary, by default None
    change_col_names : dict[str, str] | None, optional
        Change the column names, by default None. The key is the old name and the value
        is the new name.
    """

    name: str
    results: list[int | str]
    table_type: TableType
    comparison_type: ComparisonType
    x: list[str]
    y: list[str]
    value: str | None = None  # used for pivot tables
    add_error: bool = False  # add single error sheets to the tables
    conditional_formatting: dict[str, float] | None = None
    change_col_names: dict[str, str] | None = None
    subsets: list[dict] | None = None
    select_runs: re.Pattern | None = None

    def __post_init__(self):
        # the conditional formatting dictionary has a fixed structure
        if self.conditional_formatting:
            assert len(self.conditional_formatting) == 3
            for key in ["red", "yellow", "orange"]:
                assert key in self.conditional_formatting.keys()

    @classmethod
    def from_dict(cls, dictionary: dict, name) -> TableConfig:
        select_runs = dictionary.get("select_runs", None)
        if select_runs is not None:
            select_runs = re.compile(select_runs)

        return cls(
            name=name,
            results=dictionary["results"],
            table_type=TableType(dictionary["table_type"]),
            comparison_type=ComparisonType(dictionary["comparison_type"]),
            x=dictionary["x"],
            y=dictionary["y"],
            value=dictionary.get("value"),
            add_error=dictionary.get("add_error", False),
            conditional_formatting=dictionary.get("conditional_formatting"),
            change_col_names=dictionary.get("change_col_names"),
            subsets=dictionary.get("subsets"),
            select_runs=select_runs,
        )
