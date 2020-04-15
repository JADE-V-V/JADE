# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 16:52:36 2019

@author: Davide Laghi
"""
import testrun
import os
import datetime


def executeBenchmarksRoutines(session, lib):
    """
    Check which benchmarks have to be generated and/or run and execute their
    routines

    Parameters
    ----------
    session : jade.Session
        Current JADE session.
    lib : str
        library to assess (e.g. 31c).

    Returns
    -------
    None.

    """
    # Get the settings for the tests
    config = session.conf.comp_default.set_index('Description')
    # Get the log
    log = session.log

    for testname, row in config.iterrows():
        # Check for active test first
        if bool(row['OnlyInput']) or bool(row['Run']):
            print('        -- '+testname.upper()+' STARTED --\n')
            print(' Generating input files:'+'    ' +
                  str(datetime.datetime.now()))
            log.adjourn(testname.upper()+' run started' + '    ' +
                        str(datetime.datetime.now()))

            # --- Input Generation ---
            # Collect infos
            libmanager = session.lib_manager
            outpath = os.path.join(session.path_run, lib)  # get path to libdir
            safemkdir(outpath)
            fname = row['File Name']
            inpfile = os.path.join(session.path_inputs, fname)
            VRTpath = os.path.join(session.path_inputs, 'VRT')

            # Generate test
            # Special case for sphere leak
            if testname == 'Sphere Leakage Test':
                test = testrun.SphereTest(inpfile, lib, row, log, VRTpath)
            else:
                test = testrun.Test(inpfile, lib, row, log, VRTpath)

            test.generate_test(outpath, libmanager)
            # Adjourn log
            log.adjourn(testname.upper()+' test input generated with success' +
                        '    ' + str(datetime.datetime.now()))

            if bool(row['OnlyInput']):
                print('\n        -- '+testname.upper()+' COMPLETED --\n')
            else:
                # --- Input Run ---
                print(' MCNP run running:         ' +
                      str(datetime.datetime.now()))
                test.run(cpu=session.conf.cpu)
                print('\n        -- '+testname.upper()+' COMPLETED --\n')
                # Adjourn log
                log.adjourn(testname.upper()+' run completed with success'
                            + '    '+str(datetime.datetime.now()))


def safemkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
