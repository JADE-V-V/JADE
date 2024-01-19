# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 12:05:36 2020

@author: Davide Laghi

Copyright 2021, the JADE Development Team. All rights reserved.

This file is part of JADE.

JADE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JADE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JADE.  If not, see <http://www.gnu.org/licenses/>.
"""
# from copy import copy
# import openpyxl
import pandas as pd


# def createNewWorkbook(manyWb, theOne):
#     for wb in manyWb:
#         for sheetName in wb.sheetnames:
#             o = theOne.create_sheet(sheetName)
#             safeTitle = o.title
#             copySheet(wb[sheetName], theOne[safeTitle])


# def copySheet(sourceSheet, newSheet):
#     for row in sourceSheet.rows:
#         for cell in row:
#             newCell = newSheet.cell(row=cell.row, column=cell.col_idx,
#                                     value=cell.value)
#             if cell.has_style:
#                 newCell.font = copy(cell.font)
#                 newCell.border = copy(cell.border)
#                 newCell.fill = copy(cell.fill)
#                 newCell.number_format = copy(cell.number_format)
#                 newCell.protection = copy(cell.protection)
#                 newCell.alignment = copy(cell.alignment)


# def merge_sheets(filesInput, outfile):
#     myfriends = [openpyxl.load_workbook(f, read_only=False,
#                                         keep_vba=True) for f in filesInput]
# #    theOne = openpyxl.Workbook()
# #    del theOne['Sheet']  # We want our new book to be empty. Thanks.
#     createNewWorkbook(myfriends, outfile)
#     for excel in myfriends:
#         excel.close()

# #    outfile.save(outfile)


def insert_df(startrow, startcolumn, df, ws, header=True):
    """
    Insert a DataFrame (df) into a Worksheet (ws) using xlwings.
    (startrow) and (startcolumn) identify the starting data entry
    """
    columns = list(df.columns)
    values = df.values
    if header:
        for i, column in enumerate(range(startcolumn,
                                         startcolumn+len(columns))):
            value = columns[i]
            try:
                ws.cell(column=column, row=startrow,value=value)
                #ws.range((startrow, column)).value = value
            except (AttributeError, ValueError) as e:
                print(e)
                print('Warning! header not printes: column,value',
                      column, value)
        startrow = startrow+1

    for i, row in enumerate(range(startrow, startrow+len(df))):
        for j, column in enumerate(range(startcolumn,
                                         startcolumn+len(df.columns))):
            value = values[i][j]
            try:
                ws.cell(column=column,row=row,value=value)
                #ws.range((row, column)).value = value
            except (AttributeError, ValueError) as e:
                print(e)
                print('Warning! value not printed: row,column,value', row,
                      column, value)
def single_excel_writer(self, outpath, lib, tallies, stats=None):
    """
    Produces single library summary excel file using XLSXwriter

    Parameters
    ----------
    outpath : path or str
        path to the output in Tests/Postprocessing.
    lib : str
        Shorthand representation of data library (i.e 00c, 31c).
    tallies : Dataframe
        Summary of tally tallies
    errors: Dataframe
        Errors on tally tallies
    stats: Dataframe
        Results of statistical checks

    Returns
    -------
    None
    """
    writer = pd.ExcelWriter(outpath, engine="xlsxwriter")

    #for df in (tallies, errors):
        #df.set_index("Zaid", inplace=True)

    startrow = 8
    startcol = 1
    max_len = 0
    max_width = 0
    df_positions = []
    


    for tally, results in tallies.items():
        #print(results)
        tally_len, tally_width = results["Value"].shape
        df_positions.append([startrow,startcol])
        #print(pd.Series(results["title"]))
        #pd.Series(results["title"]).to_excel(writer, startrow=startrow, startcol=startcol+1, sheet_name="Values", index=False, header=False)
        results["Value"].to_excel(writer, startrow=startrow+1, startcol=startcol, sheet_name="Values")
        startrow = startrow + tally_len + 3
        max_len = max_len + tally_len
        if tally_width > max_width:
            max_width = tally_width 

    wb = writer.book   
    tal_sheet = writer.sheets["Values"]    
    #errors.to_excel(writer, startrow=8, startcol=1, sheet_name="Errors")
    #err_sheet = writer.sheets["Errors"]

    #tallies_len, tallies_width = tallies.shape
    #errors_len, errors_width = errors.shape

    if stats is not None:
        print(stats)
        #stats.set_index("Zaid", inplace=True)
        stats.to_excel(
            writer, startrow=8, startcol=1, sheet_name="Statistical Checks"
        )
        stat_sheet = writer.sheets["Statistical Checks"]
        stats_len, stats_width = stats.shape

    # Formatting styles
    plain_format = wb.add_format({"bg_color": "#FFFFFF"})
    oob_format = wb.add_format(
        {
            "align": "center",
            "valign": "center",
            "bg_color": "#D9D9D9",
            "text_wrap": True,
        }
    )
    tally_format = wb.add_format({"bg_color": "#D9D9D9"})
    merge_format = wb.add_format(
        {"align": "center", "valign": "center", "border": 2}
    )
    title_merge_format = wb.add_format(
        {
            "font_size": "36",
            "align": "center",
            "valign": "center",
            "bold": True,
            "border": 2,
        }
    )
    subtitle_merge_format = wb.add_format(
        {
            "font_size": "16",
            "align": "center",
            "valign": "center",
            "bold": True,
            "border": 2,
        }
    )
    legend_text_format = wb.add_format({"align": "center", "bg_color": "white"})
    red_cell_format = wb.add_format({"bg_color": "red"})
    orange_cell_format = wb.add_format({"bg_color": "orange"})
    yellow_cell_format = wb.add_format({"bg_color": "yellow"})
    green_cell_format = wb.add_format({"bg_color": "#A6D86E"})
    value_allzero_format = wb.add_format({"bg_color": "#EDEDED"})
    value_belowzero_format = wb.add_format({"bg_color": "#FFC7CE"})
    value_abovezero_format = wb.add_format({"bg_color": "#C6EFCE"})

    # tallies

    # Title Format
    tal_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
    tal_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
    tal_sheet.merge_range(
        "B3:L8", "SPHERE LEAKAGE TEST RESULTS RECAP: TALLIES", title_merge_format
    )
    for tal in range(len(df_positions)):
        tal_sheet.merge_range(df_positions[tal][0], 
                        df_positions[tal][1] + 1,
                        df_positions[tal][0],
                        df_positions[tal][1] + 4,
                        list(tallies.values())[tal]["title"],
                        subtitle_merge_format)
    #tal_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
    #tal_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)

    # Freeze title
    tal_sheet.freeze_panes(8, 2)

    # out of bounds
    tal_sheet.set_column(0, 0, 4, oob_format)
    tal_sheet.set_column(max_width + 2, 1000, 18, oob_format)
    for i in range(9):
        tal_sheet.set_row(i, None, oob_format)
    for i in range(9 + max_len, 1000):
        tal_sheet.set_row(i, None, oob_format)

    # Column widths for tallies, set up to 15th col to ensure title format correct
    tal_sheet.set_column(1, 14, 20)
    tal_sheet.set_column(1, max_width + 2, 20)

    # Row Heights
    tal_sheet.set_row(7, 31)
    #tal_sheet.set_row(8, 73.25)

    # Legend
    tal_sheet.merge_range("N3:O3", "LEGEND", merge_format)
    tal_sheet.merge_range("N8:O8", "According to MCNP manual", oob_format)
    tal_sheet.write("N4", "", red_cell_format)
    tal_sheet.write("O4", ">|5|%", legend_text_format)
    tal_sheet.write("N5", "", orange_cell_format)
    tal_sheet.write("O5", "|1|%≤|5|%", legend_text_format)
    tal_sheet.write("N6", "", yellow_cell_format)
    tal_sheet.write("O6", "|0.5|%≤|1|%", legend_text_format)
    tal_sheet.write("N7", "", green_cell_format)
    tal_sheet.write("O7", "<|0.5|%", legend_text_format)

    # Conditional Formatting
    tal_sheet.conditional_format(
        10,
        1,
        8 + max_len,
        max_width + 1,
        {"type": "blanks", "format": oob_format},
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "text",
            "criteria": "containing",
            "value": "Value = 0",
            "format": value_allzero_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "text",
            "criteria": "containing",
            "value": "Value < 0",
            "format": value_belowzero_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "text",
            "criteria": "containing",
            "value": "Value > 0",
            "format": value_abovezero_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "greater than",
            "value": 0.05,
            "format": red_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": 0.01,
            "maximum": 0.05,
            "format": orange_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": 0.005,
            "maximum": 0.01,
            "format": yellow_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "less than",
            "value": -0.05,
            "format": red_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": -0.05,
            "maximum": -0.01,
            "format": orange_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": -0.01,
            "maximum": -0.005,
            "format": yellow_cell_format,
        },
    )
    tal_sheet.conditional_format(
        10,
        2,
        8 + max_len,
        max_width + 1,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": -0.005,
            "maximum": 0.005,
            "format": green_cell_format,
        },
    )

    # ERRORS

    # Title
    #err_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
    #err_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
    #err_sheet.merge_range(
    #    "B3:L7", "SPHERE LEAKAGE TEST RESULTS RECAP: ERRORS", title_merge_format
    #)
    #err_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
    #err_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)
#
    ## Freeze title
    #err_sheet.freeze_panes(9, 0)
#
    ## out of bounds
    #err_sheet.set_column(0, 0, 4, oob_format)
    #err_sheet.set_column(errors_width + 2, 1000, 18, oob_format)
    #for i in range(9):
    #    err_sheet.set_row(i, None, oob_format)
    #for i in range(9 + errors_len, 1000):
    #    err_sheet.set_row(i, None, oob_format)
#
    ## Column widths for errors, set up to 15th col by default to ensure title format correct
    #err_sheet.set_column(1, 14, 20)
    #err_sheet.set_column(1, errors_width + 2, 20)
#
    ## Row Heights
    #err_sheet.set_row(7, 31)
    #err_sheet.set_row(8, 73.25)
#
    ## Legend
    #err_sheet.merge_range("N3:O3", "LEGEND", merge_format)
    #err_sheet.merge_range("N8:O8", "According to MCNP manual", oob_format)
    #err_sheet.write("N4", "", red_cell_format)
    #err_sheet.write("O4", "> 50%", legend_text_format)
    #err_sheet.write("N5", "", orange_cell_format)
    #err_sheet.write("O5", "20% ≤ 50%", legend_text_format)
    #err_sheet.write("N6", "", yellow_cell_format)
    #err_sheet.write("O6", "10% ≤ 20%", legend_text_format)
    #err_sheet.write("N7", "", green_cell_format)
    #err_sheet.write("O7", "< 10%", legend_text_format)
#
    ## Conditional Formatting
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {"type": "blanks", "format": plain_format},
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {"type": "cell", "criteria": ">", "value": 0.5, "format": red_cell_format},
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {
    #        "type": "cell",
    #        "criteria": "between",
    #        "minimum": 0.2,
    #        "maximum": 0.5,
    #        "format": orange_cell_format,
    #    },
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {
    #        "type": "cell",
    #        "criteria": "between",
    #        "minimum": 0.1,
    #        "maximum": 0.2,
    #        "format": yellow_cell_format,
    #    },
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {"type": "cell", "criteria": "<", "value": -0.5, "format": red_cell_format},
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {
    #        "type": "cell",
    #        "criteria": "between",
    #        "minimum": -0.5,
    #        "maximum": -0.2,
    #        "format": orange_cell_format,
    #    },
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {
    #        "type": "cell",
    #        "criteria": "between",
    #        "minimum": -0.2,
    #        "maximum": -0.1,
    #        "format": yellow_cell_format,
    #    },
    #)
    #err_sheet.conditional_format(
    #    9,
    #    3,
    #    8 + errors_len,
    #    errors_width + 1,
    #    {
    #        "type": "cell",
    #        "criteria": "between",
    #        "minimum": -0.1,
    #        "maximum": 0.1,
    #        "format": green_cell_format,
    #    },
    #)

    # STAT CHECKS
    if stats is not None:
        # Title
        stat_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        stat_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
        stat_sheet.merge_range(
            "B3:L7",
            "SPHERE LEAKAGE TEST RESULTS RECAP: STATISTICAL CHECKS",
            title_merge_format,
        )
        stat_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        stat_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)

        # Freeze title
        stat_sheet.freeze_panes(9, 0)

        # out of bounds
        stat_sheet.set_column(0, 0, 4, oob_format)
        stat_sheet.set_column(stats_width + 2, 1000, 18, oob_format)
        for i in range(9):
            stat_sheet.set_row(i, None, oob_format)
        for i in range(9 + stats_len, 1000):
            stat_sheet.set_row(i, None, oob_format)

        # Column widths for errors, set up to 15th col by default to ensure title format correct
        stat_sheet.set_column(1, 14, 20)
        stat_sheet.set_column(1, stats_width + 2, 20)

        # Row Heights
        stat_sheet.set_row(7, 31)
        stat_sheet.set_row(8, 73.25)

        # Formatting
        stat_sheet.conditional_format(
            9,
            3,
            8 + stats_len,
            stats_width + 1,
            {"type": "blanks", "format": plain_format},
        )
        stat_sheet.conditional_format(
            9,
            3,
            8 + stats_len,
            stats_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Passed",
                "format": value_abovezero_format,
            },
        )
        stat_sheet.conditional_format(
            9,
            3,
            8 + stats_len,
            stats_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "All zeros",
                "format": value_allzero_format,
            },
        )
        stat_sheet.conditional_format(
            9,
            3,
            8 + stats_len,
            stats_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Missed",
                "format": value_belowzero_format,
            },
        )

    wb.close()