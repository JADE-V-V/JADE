from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from jade.config.excel_config import ComparisonType, TableConfig, TableType
from jade.helper.errors import PostProcessConfigError

MAX_SHEET_NAME_LEN = 31


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
        index_cols = []
        # everything that is not Value or Error should be an index
        for col in df1.columns:
            if col not in ["Value", "Error"]:
                index_cols.append(col)
        df1 = df1.set_index(index_cols)
        df2 = df2.set_index(index_cols)
        # we want only the intersection of the two indices
        common_index = df1.index.intersection(df2.index)
        df = df1.loc[common_index].copy()

        val1 = df1.loc[common_index]["Value"]
        val2 = df2.loc[common_index]["Value"]
        err1 = df1.loc[common_index]["Error"]
        err2 = df2.loc[common_index]["Error"]

        error = np.sqrt(err1**2 + err2**2)

        if comparison_type == ComparisonType.ABSOLUTE:
            value = val1 - val2
        elif comparison_type == ComparisonType.PERCENTAGE:
            value = (val1 - val2) / val1 * 100
        elif comparison_type == ComparisonType.RATIO:
            value = val1 / val2

        df["Value"] = value
        df["Error"] = error
        return df.reset_index()

    def add_sheets(self):
        sheet_df = self._get_sheet()
        sheet_name = f"{self.cfg.comparison_type.value} {self.cfg.name}"
        if len(sheet_name) > MAX_SHEET_NAME_LEN:
            sheet_name = sheet_name[:31]
        sheet_df.to_excel(self.writer, sheet_name=sheet_name)
        # TODO do other operations on the sheets here

        if self.cfg.add_error:
            for df, val in zip([self.ref_df, self.target_df], ["ref", "target"]):
                sheet_name = f"{val} err {self.cfg.name}"
                if len(sheet_name) > MAX_SHEET_NAME_LEN:
                    sheet_name = sheet_name[:31]
                df.to_excel(self.writer, sheet_name=sheet_name)
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
