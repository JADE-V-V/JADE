# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 12:05:36 2020

@author: Davide Laghi

Excel support
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
