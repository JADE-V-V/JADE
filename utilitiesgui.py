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
def translate_input(session, lib, inputfile, outpath=None):
    """
    Translate an input file to a selected library. A log of the translation is
    also produced.
    """
    print(" Translating...")

    libmanager = session.lib_manager

    if outpath is None:
        outpath = session.path_uti
    else:
        if not os.path.exists(outpath):
            os.mkdir(outpath)

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


def print_material_info(session, filepath, outpath=None):
    """
    Print materialcard information to excel file.

    Parameters
    ----------
    session : jade.Session
        JADE current session.

    filepath : str or path
        path to the input file.


    outpath: str/os.Path
        output path. Default is None, in this case the utilities folder is
        used

    Returns
    -------
    bool
        If False there was a permission error on the input or output file.

    """
    lib_manager = session.lib_manager

    try:
        inputfile = ipt.InputFile.from_text(filepath)
    except PermissionError:
        return False

    inforaw, info_elem = inputfile.matlist.get_info(lib_manager, zaids=True)
    if outpath is None:
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


def generate_material(session, sourcefile, materials, percentages, newlib,
                      fractiontype='atom', outpath=None):
    """
    Starting from an MCNP input, materials contained in its material list can
    be used to generate a new material combining them.

    Parameters
    ----------
    session : main.Session
        JADE session.
    sourcefile : path/str
        MCNP input file.
    materials : str
        source input materials to use for the generation (e.g. M1-m10).
    percentages : str
        percentages associated to the source materials in the new materials
        (e.g. 0.1-0.9). Their are intended as atom or mass fraction depending
        on the fractiontype that is specified.
    newlib : str
        library for the new material.
    fractiontype : str, optional
        type of fraction to use in the new material (either 'atom' or 'mass'.
        The default is 'atom'.
    outpath : str/path, optional
        specify a particular path for the output file. The default is None.

    Returns
    -------
    bool
        If False a problem with the opening of the input or output file was
        encountered.

    """
    # Read the source file
    try:
        inputfile = ipt.InputFile.from_text(sourcefile)
    except PermissionError:
        return False

    # Translate to requested lib
    inputfile.translate(newlib, session.lib_manager)

    # Collect all submaterials
    submaterials = []
    main_header = "C Material Obtained from "+os.path.basename(sourcefile)

    for materialname, percentage in zip(materials, percentages):
        main_header = (main_header+'\nC Material: '+materialname +
                       ' Percentage: '+str(float(percentage)*100)+'%')
        material = inputfile.matlist[materialname]
        # Ensure materials have the requested fraction type
        material.switch_fraction(fractiontype, session.lib_manager)

        # Scale fractions
        totfraction = material.get_tot_fraction()
        current_submaterials = []
        for submat in material.submaterials:
            norm_factor = float(percentage)/totfraction  # normalized & scaled
            if fractiontype == 'mass':
                norm_factor = -norm_factor
            submat.scale_fractions(norm_factor)
            submat.update_info(session.lib_manager)
            current_submaterials.append(submat)

        # Change the header of the first submaterial to include the mat. one
        current_submaterials[0].header = (material.header +
                                          current_submaterials[0].header)
        submaterials.extend(current_submaterials)

    # Generate new material and matlist
    newmat = mat.Material(None, None, 'M1', submaterials=submaterials,
                          header=main_header)
    matcard = mat.MatCardsList([newmat])
    # matcard.update_info(session.lib_manager)

    # Dump it
    if outpath is None:
        outfile = os.path.join(session.path_uti, 'Generated Materials')
    else:
        outfile = outpath
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    outfile = os.path.join(outfile,
                           os.path.basename(sourcefile)+'_new Material')
    try:
        with open(outfile, 'w') as writer:
            writer.write(matcard.to_text())
    except PermissionError:
        return False

    return True


def switch_fractions(session, sourcefile, fraction_type, outpath=None):
    """
    Switch all fractions of an MCNP input either to mass or atom fraction.

    Parameters
    ----------
    session : main.Session
        JADE session.
    sourcefile : str/path
        MCNP input to switch.
    fraction_type : str
        either 'atom' or 'mass'.
    outpath : str/path, optional
        specific a different outpath. The default is None.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    # Read the source file
    try:
        inputfile = ipt.InputFile.from_text(sourcefile)
    except PermissionError:
        return False

    for material in inputfile.matlist:
        material.switch_fraction(fraction_type, session.lib_manager)

    # Dump it
    if outpath is None:
        outfile = os.path.join(session.path_uti, 'Fraction switch')
    else:
        outfile = outpath
    if not os.path.exists(outfile):
        os.mkdir(outfile)
    outfile = os.path.join(outfile,
                           os.path.basename(sourcefile)+'_'+fraction_type)

    inputfile.write(outfile)

    return True


def select_inputfile(message):
    """
    Safe inputfile selector

    Parameters
    ----------
    message : str
        Message to display for the input

    Returns
    -------
    inputfile : str/path
        valid inputfile as enetered by the user.

    """
    while True:
        inputfile = input(message)
        if os.path.exists(inputfile):
            return inputfile
        else:
            print("""
                  The file does not exist,
                  please select a new one
                  """)


def input_with_options(message, options):
    """
    Safe input selector with options

    Parameters
    ----------
    message : str
        message to use to prompt the choice
    options : list
        list of admissible options

    Returns
    -------
    valid_input : str
        valid input enetered by the user.

    """
    while True:
        valid_input = input(message)
        if valid_input in options:
            return valid_input
        else:
            print("""
                  Please chose a valid option
                  """)
