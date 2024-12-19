from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from jade.helper.aux_functions import PathLike


class TableType(Enum):
    PIVOT = "pivot"


class ComparisonType(Enum):
    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"
    RATIO = "ratio"


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
