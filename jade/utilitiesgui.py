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
from jade.matreader import SubMaterial
import jade.inputfile as ipt
import pandas as pd
import xlsxwriter
import jade.matreader as mat

from tqdm import tqdm
from jade.inputfile import D1S_Input


import matplotlib.pyplot as plt
import numpy as np

from functools import reduce
from jade.acepyne import *

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
    materials : list
        list of materials to mix (e.g. ['m1', 'M2']).
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
        materialname = materialname.upper()
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


def get_reaction_file(session, outpath=None):
    """
    Given a D1S input file the utility dumps a reaction file that includes
    all possible reactions that can generate for the requested libraries in
    the materials of the input.

    Parameters
    ----------
    session : Session
        JADE session.
    outpath : str or path, optional
        path where to save the reaction file. If None (default), the JADE
        default utilities folder is used.

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
    if outpath is None:
        outpath = os.path.join(session.path_uti, 'Reactions')
    # Dump it
    if not os.path.exists(outpath):  # first time the utilities is used
        os.mkdir(outpath)
    reactionfile.write(outpath)


def select_inputfile(message, max_n_tentatives=10):
    """
    Safe inputfile selector

    Parameters
    ----------
    message : str
        Message to display for the input

    max_n_tentatives : int, optional
        number of max tentatives. The default is 10

    Returns
    -------
    inputfile : str/path
        valid inputfile as enetered by the user.

    """
    i = 0
    while True:
        i += 1
        if i > 10:
            raise ValueError('Too many wrong entries.')
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


def clean_runtpe(root):
    """Clean the runtpe files from all benchmarks simulations contained in
    subdirectories of root

    Parameters
    ----------
    root : os.PathLike
        path to the root folder containing all simulation where runtpe files
        need to be removed
    """
    # Cycle on all library folders
    for lib in os.listdir(root):
        libpath = os.path.join(root, lib)
        # Cycle on all benchmarks
        for benchmark in os.listdir(libpath):
            benchpath = os.path.join(libpath, benchmark)

            try:
                # multi-test
                for test in os.listdir(benchpath):
                    testpath = os.path.join(benchpath, test)
                    _rmv_runtpe_file(testpath)

            except NotADirectoryError:
                # single-test
                _rmv_runtpe_file(benchpath)


def _rmv_runtpe_file(folder):
    """find and remove the runtpe file from a specific folder.

    Parameters
    ----------
    folder : os.PathLike
        folder that contains the runtpe file

    Returns
    -------
    ans : bool
        True if a runtpe file has been found and removed
    """
    selected = None
    for file in os.listdir(folder):
        # The runtpe file will always be called <shorter file name>+'r'
        # Check for the shorter name
        if selected is None or len(file) < len(selected):
            selected = file
    # get the runtpe name
    runtpe = selected+'r'
    filepath = os.path.join(folder, runtpe)

    # If found remove the file
    if os.path.exists(filepath):
        os.remove(filepath)
        ans = True
    else:
        ans = False

    return ans


def print_XS_EXFOR(session):
    # MT_to_print: list, isotope_zai: str, exp_?data: Bool if you wantexp data
    # libs_to_print: list
    ENDF_X4_dict = {1: "N,TOT",
                    2: "N,EL",
                    3: "N,NON",
                    4: "N,INL",
                    5: "N,X",
                    10: "N,TOT",
                    11: "N,2N+D",
                    16: "N,2N",
                    17: "N,3N",
                    18: "N,F",
                    19: "N,F'",
                    20: "N,N+F",
                    21: "N,2N+F",
                    22: "N,N+A",
                    23: "N,N+3A",
                    24: "N,2N+A",
                    25: "N,3N+A",
                    27: "N,ABS",
                    28: "N,N+P",
                    29: "N,N+2A",
                    32: "N,N+D",
                    33: "N,N+T",
                    34: "N,N+HE3",
                    37: "N,4N",
                    38: "N,3N+F",
                    41: "N,2N+P",
                    42: "N,3N+P",
                    44: "N,N+2P",
                    45: "N,N+P+A",
                    51: "N,N'",
                    89: "N,N'",
                    90: "N,N'",
                    91: "N,N'",
                    101: "N,DIS",
                    102: "N,G",
                    103: "N,P",
                    104: "N,D",
                    105: "N,T",
                    106: "N,HE3",
                    107: "N,A",
                    108: "N,2A",
                    111: "N,2P",
                    112: "N,P+A",
                    113: "N,T+2A",
                    115: "N,P+D",
                    116: "N,P+T",
                    117: "N,D+A",
                    151: "N,RES",
                    201: "N,XN",
                    202: "N,XG",
                    203: "N,XP",
                    204: "N,XD",
                    205: "N,XT",
                    206: "N,XHE3",
                    207: "N,XA",
                    208: "N,XPi_pos",
                    209: "N,XPi_0",
                    210: "N,XPi_neg",
                    444: "damage-energy production",
                    452: "N,nu_tot",
                    454: "N,ind_FY",
                    455: "N,nu_d",
                    456: "N,nu_p",
                    458: "N,rel_fis",
                    459: "FY_cum",
                    460: "N,g_bdf",
                    600: "N,P",
                    601: "N,P'",
                    649: "N,P'",
                    650: "N,D",
                    651: "N,D'",
                    699: "N,D'",
                    700: "N,T",
                    701: "N,T'",
                    749: "N,T'",
                    750: "N,HE3'",
                    751: "N,HE3'",
                    799: "N,HE3'",
                    800: "N,A",
                    801: "N,A'",
                    849: "N,A'",
                    875: "N,2N",
                    876: "N,2N",
                    889: "N,2N",
                    890: "N,2N"}
    MT_to_print = []
    libs_to_print = []

    # should introduce a check for zaids
    flag = True

    while flag is True:
        isotope_zai = input(' Enter nuclide ZAI: ')
        isot_list = list(list(session.lib_manager.data['mcnp'].values())[0].awr.keys())
        if type(isotope_zai) is not str or isotope_zai not in isot_list:
            print(' Enter a valid ZAI ID')
            continue
        if int(isotope_zai[-3:]) > 260:
            print(' Cannot print metastable nuclides')
            continue
        else:
            break

    while flag is True:
        mt_num = input(' Enter reaction MT (Enter "continue" to go on): ')
        if mt_num == "continue":
            break
        try:
            mt_num = int(mt_num)
        except ValueError:
            print(' Enter a number!')
        if mt_num not in list(ENDF_X4_dict.keys()):
            print(' Enter a valid MT ID')
            continue
        else:
            MT_to_print.append(mt_num)

    while flag is True:
        msg = ' Enter library suffix to compare (Enter "stop" to go on): '
        lib_compare = input(msg)
        if lib_compare == 'stop':
            break
        if lib_compare not in session.conf.lib.index.tolist():
            print(' Enter a library present in CONFIG')
            continue
        elif lib_compare != 'stop':
            libs_to_print.append(lib_compare)

    while flag is True:
        exp_data_flag = input(' Do you want to plot experimental data?(y/n) ')
        if exp_data_flag == 'y':
            try:
                from x4i3 import exfor_manager
            except ModuleNotFoundError:
                print('Experimental data package not installed')
                exp_flag = False
                break
            exp_flag = True
            break
        elif exp_data_flag == 'n':
            exp_flag = False
            break
        else:
            print(' please select one between "y" or "n"')

    markers = ['s', "8", "1", "o", "v", "^", "<", ">", 'x', '2', '*', 'd', 'h',
               '4']
    fill_markers = ['s', '8', ".", "o", "v", "^", "<", ">", '*', 'd', 'h']
    colors = ['m', 'r', 'c', 'b', 'k', '#BBF90F', '#FFFF00', 'm', 'r', 'c',
              'b', 'k', '#BBF90F', '#FFFF00']

    marker_styles = {}

    for i in range(len(markers)):
        if markers[i] in fill_markers:
            marker_styles[i] = dict(marker=markers[i], facecolors='none',
                                    edgecolors=colors[i], zorder=3)
        else:
            marker_styles[i] = dict(marker=markers[i], color=colors[i],
                                    zorder=3)

    elem_dict = {}

    for index, row in session.lib_manager.isotopes.iterrows():
        elem = row['E']
        z = row['Z']
        if z not in elem_dict.keys():
            elem_dict[z] = elem

    XS_dict = {}
    for index, row in session.conf.lib.iterrows():
        suffix = index
        name = row['name']
        XS_dict[suffix] = {'suffix': suffix, 'name': name}


    datapath = list(session.lib_manager.data['mcnp'].values())[0].directory
    XSDIR = list(session.lib_manager.data['mcnp'].values())[0]

    linestyles = ['-', '--', '-.', ':', (0, (3, 5, 1, 5, 1, 5))]

    err_flag = 0
    isotope_name = elem_dict[int(int(isotope_zai) / 1000)
                             ] + '-' + str(int(isotope_zai) % 1000)

    bookXS = {}

    for key, value in XS_dict.items():
        suffix = value["suffix"]
        name = value["name"]
        if suffix in libs_to_print:
            bookXS[key] = {"suffix": suffix, "name": name}

    for i in bookXS.keys():
        bookXS[i]['ZAID'] = isotope_zai + '.' + bookXS[i]['suffix']

    for j in bookXS.keys():
        for i in XSDIR.tables:
            if bookXS[j]['ZAID'] == i.name:
                bookXS[j]['datapath'] = i.filename.replace("/", "\\")

    for j in bookXS.keys():
        if 'datapath' in bookXS[j]:
            try:
                bookXS[j]['dataXS'] = Library(datapath + "\\" + bookXS[j
                                              ]['datapath'])
            except FileNotFoundError:
                print('File not Found Error: ACEfile of nuclide ' + 
                      isotope_name + ' not found in library ' + j + '\n')
                err_flag = 1
                break
            try:
                bookXS[j]['dataXS'].read()
            except:
                print('Error in reading ACEfile of nuclide ' + isotope_zai +'\n')
                err_flag = 1
                break
            if j != '00c':
                bookXS[j]['dataT'] = bookXS[j]['dataXS'
                                               ].tables[bookXS[j]['ZAID']]
            else:
                ace_zaid = bookXS[j]['ZAID'].split('.')[0] + '.800nc'
                bookXS[j]['dataT'] = bookXS[j]['dataXS'].tables[ace_zaid]

    if err_flag == 1:
        # If the reading od
        return

    for i in MT_to_print:
        if i != 1:
            for k, j in enumerate(bookXS.keys()):
                if 'datapath' in bookXS[j]:
                    try:
                        MT = 'MT'+str(i)
                        bookXS[j][MT] = bookXS[j]['dataT'].reactions[i]
                    except KeyError:
                        print("Channel MT" + str(i) + ' ' + 'not present in '+ bookXS[j]['name'])
                        continue

    for i in MT_to_print:
        MT = 'MT' + str(i)
        legend_plot = []
        data_list = []
        plt.figure(figsize=(18, 11))
        if i != 444 and exp_flag is True:
            db = exfor_manager.X4DBManagerDefault()
            iso_reac_exfor_data = db.retrieve(target=isotope_name,
                                              reaction=ENDF_X4_dict[i],
                                              quantity='SIG')
            for entry_key, entry in iso_reac_exfor_data.items():
                datasets = entry.getSimplifiedDataSets()
                for subentry_key, subentry in datasets.items():
                    if subentry.simplified is True and isinstance(subentry.reaction[0].quantity, list) and len(subentry.reaction[0].quantity) == 1 and subentry.reaction[0].quantity[0] == 'SIG': # and len(subentry.reaction[0]) == 2 and subentry.reaction[0] == 'SIG':
                        x_subentry = []
                        y_subentry = []
                        en_idx = datasets[subentry_key].labels.index('Energy')
                        data_idx = datasets[subentry_key].labels.index('Data')
                        for rows in subentry.data:
                            x_subentry.append(rows[en_idx])
                            y_subentry.append(rows[data_idx])
                        data_list.append((x_subentry, y_subentry,
                                          len(x_subentry),
                                          subentry.author[0] + ', ' + subentry.year))

            sorted_data_list = sorted(data_list, key=lambda x: x[2],
                                      reverse=True)

        for k, j in enumerate(bookXS.keys()):
            if k > 4:
                # should not occur
                # by default more than 4 libraries cannot be required
                break
            if MT == 'MT1' and bookXS[j]['suffix'] in libs_to_print and 'datapath' in bookXS[j]:
                X = bookXS[j]['dataT'].energy
                y_set = bookXS[j]['dataT'].sigma_t
                if len(X) == len(y_set):
                    legend_plot.append(bookXS[j]['name'])
                    plt.plot(X, y_set, linestyle=linestyles[k],
                             linewidth=4, zorder=2)
                else:
                    print(isotope_zai + 'LENERR\n')
                    continue

            elif MT in bookXS[j] and bookXS[j]['suffix'] in libs_to_print and 'datapath' in bookXS[j]:
                r = bookXS[j]['dataT'].reactions[i]
                X = bookXS[j]['dataT'].energy[r.IE:]
                y_set = r.sigma
                if len(X) == len(y_set):
                    legend_plot.append(bookXS[j]['name'])
                    plt.plot(X, y_set, linestyle=linestyles[k], linewidth=4,
                             zorder=2)
                else:
                    print(isotope_zai + 'LENERR\n')
                    continue

        if len(data_list) > 0:
            for idx, elem in enumerate(sorted_data_list):
                if idx > (len(fill_markers) - 1):
                    break
                else:
                    legend_plot.append(elem[3])
                    plt.scatter(sorted_data_list[idx][0],
                                sorted_data_list[idx][1],
                                s=135, **marker_styles[idx], linewidth=2)

        if not legend_plot:
            plt.close()
            print('No data to print for ' + MT + '\n')
            continue

        else:
            plt.grid(visible=True)
            plt.xscale('log')
            plt.yscale('log')
            plt.legend(legend_plot, loc="lower left", fontsize=10,
                       markerscale=0.5)
            plt.xlabel("Energy (MeV)", fontsize=12)
            plt.ylabel("$\sigma$ (barn)", fontsize=12)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.title(isotope_name + ' ' + MT + ' (' + ENDF_X4_dict[i] + ')',
                      fontsize=12)
            plt.show(block=False)
            print(' Cross Section printed')
