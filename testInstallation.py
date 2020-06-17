# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:46:49 2020

@author: Davide Laghi
"""
import os
import utilitiesgui as uti
import pandas as pd


def test_installation(session):
    results = []
    # --- General Parameters ---
    default_lib = '70c'
    install_folder = session.path_test_install
    inputs = os.path.join(install_folder, 'Inputs')

    # --- Test Utilities ---
    inputfile = os.path.join(inputs, 'TestInput.i')
    outpath = os.path.join(install_folder, 'Utilities')
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    # Translation
    ans = uti.translate_input(session, default_lib, inputfile,
                              outpath=outpath)
    results.append([' Translation', ans])

    # Print material info
    ans = uti.print_material_info(session, inputfile, outpath=None)
    results.append([' Print Material Infos', ans])

    # Generate materials
    materials = ['M1', 'M2']
    percentages = ['0.1', '0.9']
    ans = uti.generate_material(session, inputfile, materials, percentages,
                                default_lib, fractiontype='atom',
                                outpath=outpath)
    results.append([' Generate Materials', ans])

    print(' ###################################')
    results = pd.DataFrame(results, columns=[' Name', 'Result'])
    results.set_index(' Name', inplace=True)

    print(results)
    text = 'INSTALLATION TEST RESULTS:\n'
    text = text+results.to_string()
    session.log.bar_adjourn(text)
    
