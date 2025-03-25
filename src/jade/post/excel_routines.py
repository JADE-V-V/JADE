from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from jade.config.excel_config import ComparisonType, TableConfig, TableType
from jade.helper.errors import PostProcessConfigError
from jade.post.manipulate_tally import compare_data

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
        ref_tag: str,
        target_tag: str,
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
        ref_tag : str
            tag of the reference data
        target_tag : str
            tag of the target data
        """
        self.writer = writer
        self.data = self._compare(ref_df, target_df, table_cfg.comparison_type)
        self.ref_df = ref_df
        self.target_df = target_df
        self.title = title
        self.cfg = table_cfg
        self.ref_tag = ref_tag
        self.target_tag = target_tag
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

        df["Value"], df["Error"] = compare_data(val1, val2, err1, err2, comparison_type)

        return df.reset_index()

    def _add_sheet(
        self,
        sheet_name: str,
        df: pd.DataFrame,
        apply_conditional: bool = True,
        title: str | None = None,
    ):
        if len(sheet_name) > MAX_SHEET_NAME_LEN:
            sheet_name = sheet_name[:31]

        ws = self.writer.book.add_worksheet(sheet_name)
        if title is None:
            title = sheet_name
        self.formatter.add_title(ws, title)
        # as a last operation, change the df columns if requested
        if self.cfg.change_col_names:
            self._rename_columns(df, self.cfg.change_col_names)
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
        # autofit the columns
        # ws.autofit()
        self.formatter.autofit_columns(ws, df)
        # freeze the panes
        ws.freeze_panes(DF_START_ROW + df.columns.nlevels, df.columns.nlevels - 1)

    def add_sheets(self):
        """Add the comparison sheets to the workbook."""
        dfs = self._get_sheet()
        sheet_name = f"{self.cfg.comparison_type.value} {self.cfg.name}"
        title = f"{sheet_name} - {self.ref_tag} vs {self.target_tag}"
        self._add_sheet(sheet_name, dfs[0], apply_conditional=True, title=title)

        if self.cfg.add_error:
            for df, val, tag in zip(
                [dfs[1], dfs[2]], ["ref", "target"], [self.ref_tag, self.target_tag]
            ):
                sheet_name = f"{val} rel. err. {self.cfg.name}"
                title = f"{tag} Relative Error for {self.cfg.name}"
                self._add_sheet(sheet_name, df, title=title)
                # apply standard formatting for error sheets
                self.formatter.apply_conditional_formatting(
                    self.writer.book.get_worksheet_by_name(sheet_name),
                    DF_START_ROW + df.columns.nlevels,
                    df.index.nlevels - 1,
                    ERRORS_THRESHOLD,
                )

    @abstractmethod
    def _get_sheet(self) -> list[pd.DataFrame]:
        """this is the core of the table, its data. It should return a list of
        dataframes that will be added to the workbook (one per sheet)."""
        pass

    @staticmethod
    def _rename_columns(df: pd.DataFrame, names: dict[str, str]) -> None:
        """Rename the columns of the dataframe according to the change_col_names dict."""
        # Apply changes to the index
        if isinstance(df.index, pd.MultiIndex):
            # remove the keys that are not present in the index or it will complain
            index_names = {k: v for k, v in names.items() if k in df.index.names}
            df.index = df.index.rename(index_names)
        else:
            df.index.names = [names[df.index.names[0]]]

        # Apply changes to the columns
        if isinstance(df.columns, pd.MultiIndex):
            # remove the keys that are not present in the index or it will complain
            col_names = {k: v for k, v in names.items() if k in df.columns.names}
            df.columns = df.columns.rename(col_names)
        else:
            df.rename(columns=names, inplace=True)


class PivotTable(Table):
    """multi level pivot table"""

    def _get_sheet(self) -> list[pd.DataFrame]:
        if self.cfg.value is None:
            raise PostProcessConfigError("'value' needs to be defined for pivot table")
        value_df = self.data.pivot(
            index=self.cfg.x, columns=self.cfg.y, values=self.cfg.value
        )
        # this is needed to avoid NaN in the multiindex which would cause incorrect dump
        value_df.columns = pd.MultiIndex.from_frame(
            value_df.columns.to_frame().fillna("")
        )

        if self.cfg.add_error:
            ref_err = self.ref_df.pivot(
                index=self.cfg.x, columns=self.cfg.y, values="Error"
            )
            # this is needed to avoid NaN in the multiindex which would cause incorrect
            # dump
            ref_err.columns = pd.MultiIndex.from_frame(
                ref_err.columns.to_frame().fillna("")
            )

            target_err = self.target_df.pivot(
                index=self.cfg.x, columns=self.cfg.y, values="Error"
            )
            # this is needed to avoid NaN in the multiindex which would cause incorrect
            # dump
            target_err.columns = pd.MultiIndex.from_frame(
                target_err.columns.to_frame().fillna("")
            )

            return [value_df, ref_err, target_err]
        return [value_df]


class SimpleTable(Table):
    """Simply dump the data using cfg.x as index and cfg.y as columns to be retained"""

    def _get_sheet(self) -> list[pd.DataFrame]:
        value_df = self.data.set_index(self.cfg.x)
        value_df = value_df[self.cfg.y]
        dfs = [value_df]
        if self.cfg.add_error:
            ref_err = self.ref_df.set_index(self.cfg.x)[["Error"]]
            target_err = self.target_df.set_index(self.cfg.x)[["Error"]]
            dfs.extend([ref_err, target_err])
        return dfs


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
        elif table_type == TableType.SIMPLE:
            return SimpleTable(*args)
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
        sheet.merge_range(0, 0, 0, 10, title, cell_format=self.title)

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

    def autofit_columns(
        self, worksheet: Worksheet, df: pd.DataFrame, scientific=True
    ) -> None:
        """Autofit the columns of the worksheet to the content of the DataFrame.

        Parameters
        ----------
        worksheet : Worksheet
            worksheet to be formatted
        df : pd.DataFrame
            content of the worksheet
        scientific : bool
            if True it means that the scientific notation will be applied to the
            content. Default is True. If set to False, the max length of the (raw) data
            is checked.
        """
        # get the amount of index layers
        if isinstance(df.index, pd.MultiIndex):
            index_layers = df.index.nlevels
        else:
            index_layers = 1

        for idx, col in enumerate(df.columns):
            # find max in the header
            if isinstance(col, tuple):
                # to_check = [str(c) for c in col]
                # better to consider the 2nd layer as the first will have more space
                try:
                    # there may be more than one layer
                    head_values = [len(str(c)) for c in col[1:]]
                    if len(head_values) > 0:
                        max_header = max(head_values)
                    else:
                        max_header = 0
                except IndexError:
                    max_header = 0
                # if the second header is empty, take the first
                if max_header == 0:
                    max_header = len(str(col[0]))
            else:
                max_header = len(str(col))

            # Find the maximum length of the column content
            # if the scientific notation is used I already now that everything
            # has been formatted to 8 charachters
            if scientific:
                max_content = 8
            else:
                max_content = df[col].astype(str).map(len).max()

            # find the max between the header and the content and add some padding
            max_len = max(max_content, max_header) + 1

            # Set the column width
            worksheet.set_column(idx + index_layers, idx + index_layers, max_len)

        # set the index column(s)
        if index_layers == 1:
            max_index = df.index.astype(str).map(len).max()
            worksheet.set_column(0, 0, max_index + 1)
        else:
            for layer in range(index_layers):
                max_index = df.index.get_level_values(layer).astype(str).map(len).max()
                worksheet.set_column(layer, layer, max_index + 1)
