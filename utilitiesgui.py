# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 11:44:13 2019

@author: Davide Laghi
"""
import os
import inputfile as ipt
import pandas as pd
import xlsxwriter
import matreader as mat


###############################################################################
# ------------------------ UTILITIES ------------------------------------------
###############################################################################
def translate_input(session, lib, inputfile):
    """
    Translate an input file to a selected library. A log of the translation is
    also produced.
    """
    print(" Translating...")

    libmanager = session.lib_manager
    outpath = os.getcwd()
    outpath = os.path.dirname(outpath)
    outpath = session.path_uti
    filename = os.path.basename(inputfile)

    try:
        inp = ipt.InputFile.from_text(inputfile)
    except PermissionError:
        return False

    info1, _ = inp.matlist.get_info(libmanager)
    inp.translate(lib, libmanager)
    inp.update_zaidinfo(libmanager)
    info2, _ = inp.matlist.get_info(libmanager)

    newdir = os.path.join(outpath, 'Translation')
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    outfile = os.path.join(newdir, filename+'_translated_'+lib)
    inp.write(outfile)

    # Log production
    try:
        info1['Fraction old'] = info1['Fraction']
        info1['Fraction new'] = info2['Fraction']
        perc = (info1['Fraction']-info2['Fraction'])/info1['Fraction']
        info1['Fraction difference [%]'] = perc
        del info1['Fraction']

        outlog = os.path.join(newdir, filename+'_translated_'+lib+'_LOG.xlsx')

        info1.to_excel(outlog)
    # In case at leat one entire element was not translated
    except ValueError:
        text = '  Warning: it was impossible to produce the translation Log'
        print(text)
        session.log.adjourn(text)

    return True


def print_libraries(libmanager):
    print(libmanager.libraries)


def print_material_info(session, filepath, lib_manager):
    """
    Print materialcard information to excel file.

    Parameters
    ----------
    session : jade.Session
        JADE current session.

    filepath : str or path
        path to the output file.

    lib_manager : libmanager.LibManager
        Library manager for conversions and name recovery.

    Returns
    -------
    bool
        If False there was a permission error on the input or output file.

    """

    try:
        inputfile = ipt.InputFile.from_text(filepath)
    except PermissionError:
        return False

    inforaw, info_elem = inputfile.matlist.get_info(lib_manager, zaids=True)
    outpath = os.path.join(session.path_uti, 'Materials Infos')
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    outname = os.path.basename(filepath)+'_materialinfo.xlsx'
    outfile = os.path.join(outpath, outname)

    try:
        with pd.ExcelWriter(outfile, engine='xlsxwriter') as writer:
            inforaw.to_excel(writer, sheet_name='Sheet1')
            info_elem.to_excel(writer, sheet_name='Sheet2')
    except xlsxwriter.exceptions.FileCreateError:
        return False

    return True


def generate_material(session, sourcefile, materials, percentages):
    # Read the source file
    try:
        inputfile = ipt.InputFile.from_text(sourcefile)
    except PermissionError:
        return False

    # Collect all submaterials
    submaterials = []
    for materialname, percentage in zip(materials, percentages):
        material = inputfile.matlist[materialname]
        totfraction = material.get_tot_fraction()
        # Scale fractions
        for submat in material.submaterials:
            norm_factor = float(percentage)/totfraction  # normalized and scaled
            submat.scale_fractions(norm_factor)
            submat.update_info(session.lib_manager)
            submaterials.append(submat)

    # Generate new material and matlist
    newmat = mat.Material(None, None, 'M1', submaterials=submaterials)
    matcard = mat.MatCardsList([newmat])

    # Dump it
    outfile = os.path.join(session.path_uti, 'Generated Materials')
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    outfile = os.path.join(outfile, os.path.basename(sourcefile))
    try:
        with open(outfile, 'w') as writer:
            writer.write(matcard.to_text())
    except PermissionError:
        return False

    return True
