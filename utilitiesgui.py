# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 11:44:13 2019

@author: Davide Laghi
"""
import os
import inputfile as ipt


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

    info1 = inp.matlist.get_info()
    inp.translate(lib, libmanager)
    inp.update_zaidinfo(libmanager)
    info2 = inp.matlist.get_info()

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
    

# def print_material_info()
