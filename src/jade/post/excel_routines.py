from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd

from jade.config.pp_config import TableConfig
from jade.helper.errors import PostProcessConfigError


class TableType(Enum):
    PIVOT = "pivot"


class ComparisonType(Enum):
    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"
    RATIO = "ratio"


class Table(ABC):
    def __init__(
        self,
        title: str,
        writer: pd.ExcelWriter,
        ref_df: pd.DataFrame,
        target_df: pd.DataFrame,
        table_cfg: TableConfig,
    ):
        self.writer = writer
        self.data = self._compare(ref_df, target_df, table_cfg.comparison_type)
        self.ref_df = ref_df
        self.target_df = target_df
        self.title = title
        self.cfg = table_cfg

    @staticmethod
    def _compare(df1: pd.DataFrame, df2: pd.DataFrame, comparison_type: ComparisonType):
        if comparison_type == ComparisonType.ABSOLUTE:
            return df1 - df2
        elif comparison_type == ComparisonType.PERCENTAGE:
            return (df1 - df2) / df1 * 100
        elif comparison_type == ComparisonType.RATIO:
            return df1 / df2

    def add_sheets(self):
        sheet_df = self._get_sheet()
        sheet_df.to_excel(
            self.writer, sheet_name=f"{self.cfg.name} {self.cfg.comparison_type}"
        )
        # TODO do other operations on the sheets here

        if self.cfg.add_error:
            for df, val in zip([self.ref_df, self.target_df], ["ref", "target"]):
                df.to_excel(self.writer, sheet_name=f"{self.cfg.name} {val} error")
                # TODO apply formatting for the error sheet

    @abstractmethod
    def _get_sheet(self) -> pd.DataFrame:
        pass

    def apply_formatting(self):
        pass

    def resize_columns(self):
        pass


class PivotTable(Table):
    """multi level pivot table"""

    def _get_sheet(self) -> pd.DataFrame:
        if self.cfg.value is None:
            raise PostProcessConfigError("'value' needs to be defined for pivot table")
        return self.data.pivot(
            index=self.cfg.x, columns=self.cfg.y, values=self.cfg.value
        )


class TableFactory:
    @staticmethod
    def create_table(table_type: TableType, args: list) -> Table:
        if table_type == TableType.PIVOT:
            return PivotTable(*args)
        else:
            raise NotImplementedError(f"Table type {table_type} not supported")
