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
                ws.range((startrow, column)).value = value
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
                ws.range((row, column)).value = value
            except (AttributeError, ValueError) as e:
                print(e)
                print('Warning! value not printed: row,column,value', row,
                      column, value)
