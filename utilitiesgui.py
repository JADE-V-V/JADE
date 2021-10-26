# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 11:44:13 2019

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
import os
import inputfile as ipt
import pandas as pd
import xlsxwriter
import matreader as mat

from tqdm import tqdm
from inputfile import D1S_Input


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

    inforaw, info_elem = inputfile.matlist.get_info(lib_manager, zaids=True,
                                                    complete=True)
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
        percentage_str = str(round(float(percentage)*100, 2))+'%'
        main_header = (main_header+'\nC Material: '+materialname +
                       ' Percentage: '+percentage_str)
        material = inputfile.matlist[materialname]
        # Ensure materials have the requested fraction type
        material.switch_fraction(fractiontype, session.lib_manager)

        # Scale fractions
        totfraction = material.get_tot_fraction()
        current_submaterials = []
        for j, submat in enumerate(material.submaterials):
            norm_factor = float(percentage)/totfraction  # normalized & scaled
            if fractiontype == 'mass':
                norm_factor = -norm_factor
            submat.scale_fractions(norm_factor)
            submat.update_info(session.lib_manager)
            # Add info to the header in order to back-trace the generation
            submat.header = ('C '+materialname+', submaterial '+str(j+1)+'\n' +
                             submat.header)
            # Drop additional keys if present
            submat.additional_keys = []
            current_submaterials.append(submat)

        # Change the header of the first submaterial to include the mat. one
        new_sub_header = (material.header +
                          current_submaterials[0].header).strip('\n')
        current_submaterials[0].header = new_sub_header
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


def restore_default_config(session):
    """
    Restore the configuration default files.

    Parameters
    ----------
    session : main.Session
        JADE session.

    Returns
    -------
    None.

    """
    msg = """
 Are you sure you want to restore the default configuration?
 All user modification will be lost [y/n] -> """
    ans = input_with_options(msg, ['y', 'n'])

    if ans == 'y':
        session.restore_default_settings()
    else:
        print('\n The operation was canceled.\n')


def change_ACElib_suffix():
    """
    This function changes the suffix of the ACE files contained in a specific
    directory. The modification occurs in the first line of the file. Often
    libraries are distributed toghether with the necessary edits for the
    xsdir file. If these are provided as single files, the suffix will be
    changed in them as well.

    Returns
    -------
    None.

    """
    # Ask for the directory where files are contained
    message = ' Select directory containing ACE files: '
    folder = select_inputfile(message)

    # Ask for the suffix
    old = input(' Suffix to be changed (e.g. 99c): ')
    new = input(' New suffix to be applied (e.g. 98c): ')

    newfolder = os.path.join(os.path.dirname(folder),
                             os.path.basename(folder)+'new')
    # Create new folder
    if not os.path.exists(newfolder):
        os.mkdir(newfolder)

    for file in tqdm(os.listdir(folder)):
        oldfile = os.path.join(folder, file)
        newfile = os.path.join(newfolder, file)
        with open(oldfile, 'r') as infile, open(newfile, 'w') as outfile:
            counter = 0
            try:
                for line in infile:
                    counter += 1
                    if counter == 1:
                        newline = line.replace(old, new)
                        outfile.write(newline)
                    else:
                        outfile.write(line)
            except UnicodeDecodeError:
                print('Decode error in '+file)


def get_reaction_file(session):
    """
    Given a D1S input file the utility dumps a reaction file that includes
    all possible reactions that can generate for the requested libraries in
    the materials of the input.

    Parameters
    ----------
    session : Session
        JADE session.

    Returns
    -------
    None.

    """
    # Select the input file
    message = ' Please select a D1S input file: '
    filepath = select_inputfile(message)
    # Select the library
    lib = session.lib_manager.select_lib()

    # Generate a D1S input
    inputfile = D1S_Input.from_text(filepath)
    reactionfile = inputfile.get_reaction_file(session.lib_manager, lib)
    reactionfile.name = inputfile.name+'_react'+lib
    outpath = os.path.join(session.path_uti, 'Reactions')
    # Dump it
    if not os.path.exists(outpath):  # first time the utilities is used
        os.mkdir(outpath)
    reactionfile.write(outpath)


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
