from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from jade.config.excel_config import ComparisonType, TableConfig, TableType
from jade.helper.errors import PostProcessConfigError

MAX_SHEET_NAME_LEN = 31
DF_START_ROW = 3
ERRORS_THRESHOLD = {"red": 0.5, "orange": 0.2, "yellow": 0.1}


class Table(ABC):
    def __init__(
        self,
        title: str,
        writer: pd.ExcelWriter,
        ref_df: pd.DataFrame,
        target_df: pd.DataFrame,
        table_cfg: TableConfig,
    ):
        """Create a Table object that is responsible for comparing two dataframes and
        adding the comparison to the workbook.

        Parameters
        ----------
        title : str
            title of the table
        writer : pd.ExcelWriter
            writer object for the workbook
        ref_df : pd.DataFrame
            dataframe of the reference data
        target_df : pd.DataFrame
            dataframe of the target data
        table_cfg : TableConfig
            configuration options of the table
        """
        self.writer = writer
        self.data = self._compare(ref_df, target_df, table_cfg.comparison_type)
        self.ref_df = ref_df
        self.target_df = target_df
        self.title = title
        self.cfg = table_cfg
        self.formatter = Formatter(writer.book)

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

    def _add_sheet(
        self, sheet_name: str, df: pd.DataFrame, apply_conditional: bool = True
    ):
        if len(sheet_name) > MAX_SHEET_NAME_LEN:
            sheet_name = sheet_name[:31]

        ws = self.writer.book.add_worksheet(sheet_name)
        self.formatter.add_title(ws, sheet_name)
        df.to_excel(self.writer, sheet_name=sheet_name, startrow=DF_START_ROW)

        # additional operation on the sheet
        if apply_conditional and self.cfg.conditional_formatting:
            self.formatter.apply_conditional_formatting(
                ws,
                DF_START_ROW + df.columns.nlevels,
                df.index.nlevels - 1,
                self.cfg.conditional_formatting,
            )
        # put the scientific formatter for all numbers
        self.formatter.apply_scientific_formatting(
            ws, df.columns.nlevels + DF_START_ROW, df.index.nlevels
        )
        ws.autofit()
        ws.freeze_panes(DF_START_ROW + df.columns.nlevels, df.columns.nlevels - 1)

    def add_sheets(self):
        """Add the comparison sheets to the workbook."""
        dfs = self._get_sheet()
        sheet_name = f"{self.cfg.comparison_type.value} {self.cfg.name}"
        self._add_sheet(sheet_name, dfs[0], apply_conditional=True)

        if self.cfg.add_error:
            for df, val in zip([dfs[1], dfs[2]], ["ref", "target"]):
                sheet_name = f"{val} rel. err."
                self._add_sheet(sheet_name, df)
                # apply standard formatting for error sheets
                self.formatter.apply_conditional_formatting(
                    self.writer.book.get_worksheet_by_name(sheet_name),
                    DF_START_ROW + df.columns.nlevels,
                    df.index.nlevels - 1,
                    ERRORS_THRESHOLD,
                )

    @abstractmethod
    def _get_sheet(self) -> list[pd.DataFrame]:
        pass


class PivotTable(Table):
    """multi level pivot table"""

    def _get_sheet(self) -> list[pd.DataFrame]:
        if self.cfg.value is None:
            raise PostProcessConfigError("'value' needs to be defined for pivot table")
        value_df = self.data.pivot(
            index=self.cfg.x, columns=self.cfg.y, values=self.cfg.value
        )

        if self.cfg.add_error:
            ref_err = self.ref_df.pivot(
                index=self.cfg.x, columns=self.cfg.y, values="Error"
            )
            target_err = self.target_df.pivot(
                index=self.cfg.x, columns=self.cfg.y, values="Error"
            )
            return [value_df, ref_err, target_err]
        return [value_df]


class TableFactory:
    """Factory class for creating Table objects according to the TableType."""

    @staticmethod
    def create_table(table_type: TableType, args: list) -> Table:
        """Create a Table object according to the TableType.

        Parameters
        ----------
        table_type : TableType
            type of the table
        args : list
            arguments for the Table object this will be table type dependent

        Returns
        -------
        Table
            Corresponding Table object

        Raises
        ------
        NotImplementedError
            If the table type is not supported
        """
        if table_type == TableType.PIVOT:
            return PivotTable(*args)
        else:
            raise NotImplementedError(f"Table type {table_type} not supported")


class Formatter:
    def __init__(self, wb: Workbook):
        """Create a Formatter object that is responsibke for all formatting operation
        in the workbook.

        Parameters
        ----------
        wb : Workbook
            workbook on which the formatter operates

        Attributes
        ----------
        red : Format
            Format with red background and border.
        orange : Format
            Format with orange background and border.
        yellow : Format
            Format with yellow background and border.
        green : Format
            Format with green background and border.
        identical : Format
            Format with greenish background and border.
        not_avail : Format
            Format with grey background and border.
        ref0 : Format
            Format with purple background and border.
        merge : Format
            Format for merged cells with center alignment and border.
        plain : Format
            Format with white background.
        scientific : Format
            Format for scientific notation.
        percent : Format
            Format for percentage.
        oob : Format
            Format with center alignment, grey background, and text wrapping.
        title : Format
            Format for title with large font size, center alignment, bold text, and
            border.
        subtitle : Format
            Format for subtitle with medium font size, center alignment, bold text,
            and border.
        legend : Format
            Format for legend with center alignment, white background, and border.
            The workbook instance on which the formatter operates.

        """
        # colors
        self.red = wb.add_format({"bg_color": "red", "border": 3})
        self.orange = wb.add_format({"bg_color": "#FFC000", "border": 3})
        self.yellow = wb.add_format({"bg_color": "#FFFF00", "border": 3})
        self.green = wb.add_format({"bg_color": "#92D050", "border": 3})

        self.identical = wb.add_format({"bg_color": "#7ABD7E", "border": 3})
        self.not_avail = wb.add_format({"bg_color": "#B8B8B8", "border": 3})
        self.ref0 = wb.add_format({"bg_color": "#8465C5", "border": 3})

        # actions
        self.merge = wb.add_format({"align": "center", "valign": "center", "border": 2})
        self.plain = wb.add_format({"bg_color": "#FFFFFF"})
        self.scientific = wb.add_format({"num_format": "0.00E+00"})
        self.percent = wb.add_format({"num_format": "0.00%"})

        # special
        self.oob = wb.add_format(
            {
                "align": "center",
                "valign": "center",
                "bg_color": "#D9D9D9",
                "text_wrap": True,
            }
        )
        self.title = wb.add_format(
            {
                "font_size": "28",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
            }
        )
        self.subtitle = wb.add_format(
            {
                "font_size": "16",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
            }
        )

        self.legend = wb.add_format(
            {"align": "center", "bg_color": "white", "border": 1}
        )

        self.wb = wb

    def add_title(self, sheet: Worksheet, title: str):
        """Add a formtted title to the sheet.

        Parameters
        ----------
        sheet : Worksheet
            sheet to which the title is added
        title : str
            title to be added
        """
        sheet.merge_range(0, 0, 0, 5, title, cell_format=self.title)

    def apply_scientific_formatting(
        self, sheet: Worksheet, head_row_end: int, index_col_end: int
    ):
        """Apply scientific formatting to all numbers in the sheet.
        Formatting is not applied to header of index of the dataframe.

        Parameters
        ----------
        sheet : Worksheet
            sheet to which the formatting is applied
        head_row_end : int
            row index of where the data starts
        index_col_end : int
            column index of where the data starts
        """
        for row in range(head_row_end, sheet.dim_rowmax + 1):
            for col in range(index_col_end, sheet.dim_colmax + 1):
                try:
                    value = sheet.table[row][col].number
                    sheet.write(row, col, value, self.scientific)
                except (KeyError, AttributeError):
                    pass

    def apply_conditional_formatting(
        self,
        sheet: Worksheet,
        head_row_end: int,
        index_col_end: int,
        thresholds: dict[str, float],
    ):
        """Apply conditional formatting to the sheet.

        This applies a classic red-orange-yellow-green color scheme to the data
        according to the thresholds.

        Parameters
        ----------
        sheet : Worksheet
            sheet to which the formatting is applied
        head_row_end : int
            row index of where the data starts
        index_col_end : int
            column index of where the data starts
        thresholds : dict[str, float]
            dictionary with keys "red", "orange", and "yellow" and float values
            representing the thresholds for the color scheme
        """
        first_col = index_col_end + 1
        first_row = head_row_end + 1
        args = [
            first_row,
            first_col,
            sheet.dim_rowmax,
            sheet.dim_colmax,
        ]
        sheet.conditional_format(
            *args,
            options={"type": "blanks", "format": self.oob},
        )
        # RED
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "greater than",
                "value": thresholds["red"],
                "format": self.red,
            },
        )
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "<",
                "value": -thresholds["red"],
                "format": self.red,
            },
        )
        # ORANGE
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "between",
                "maximum": thresholds["red"],
                "minimum": thresholds["orange"],
                "format": self.orange,
            },
        )
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "between",
                "maximum": -thresholds["orange"],
                "minimum": -thresholds["red"],
                "format": self.orange,
            },
        )
        # YELLOW
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "between",
                "maximum": thresholds["orange"],
                "minimum": thresholds["yellow"],
                "format": self.yellow,
            },
        )
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "between",
                "maximum": -thresholds["yellow"],
                "minimum": -thresholds["orange"],
                "format": self.yellow,
            },
        )
        # GREEN
        sheet.conditional_format(
            *args,
            options={
                "type": "cell",
                "criteria": "between",
                "maximum": thresholds["yellow"],
                "minimum": -thresholds["yellow"],
                "format": self.green,
            },
        )
