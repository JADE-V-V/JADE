# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 16:52:36 2019

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
import testrun
import os
import datetime
import re


def executeBenchmarksRoutines(session, lib, exp=False):
    """
    Check which benchmarks have to be generated and/or run and execute their
    routines

    Parameters
    ----------
    session : jade.Session
        Current JADE session.
    lib : str (or dic string)
        library to assess (e.g. 31c)
        or couple activation+transport (e.g. 99c-31c).
        Double quotes are needed.
    exp : bool
        if True the experimental Benchmarks are selected. The default is False

    Returns
    -------
    None.

    """
    # Get the settings for the tests
    if exp:
        config = session.conf.exp_default.set_index('Description')
    else:
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

            # Handle dic string as lib
            pat_libs = re.compile(r'"\d\d[a-zA-Z]"')
            if lib[0] == '{':
                libs = pat_libs.findall(lib)
                libpath = libs[1][1:-1]
            elif '-' in lib:
                libpath = lib[:3]
            else:
                libpath = lib

            if testname == 'FNG Bulk Blanket and Shielding Experiment':
                lib = {'00c': lib, '34y': '34y'}
            # get path to libdir
            outpath = os.path.join(session.path_run, libpath)
            safemkdir(outpath)
            fname = row['File Name']
            inpfile = os.path.join(session.path_inputs, fname)
            VRTpath = os.path.join(session.path_inputs, 'VRT')
            confpath = os.path.join(session.path_cnf, fname.split('.')[0])

            # Generate test
            args = (inpfile, lib, row, log, VRTpath, confpath)
            # Handle special cases
            if testname == 'Sphere Leakage Test':
                test = testrun.SphereTest(*args)

            elif testname == 'Sphere SDDR':
                test = testrun.SphereTestSDDR(*args)

            elif fname in ['Oktavian', 'Tiara-BC', 'Tiara-BS', 'Tiara-FC', 'FNS', 'FNG-BKT']:
                test = testrun.MultipleTest(*args)

            elif fname == 'FNG':
                test = testrun.MultipleTest(*args, TestOb=testrun.FNGTest)

            else:
                test = testrun.Test(*args)

            # write the input(s)
            if testname in ['Sphere Leakage Test', 'Sphere SDDR']:
                try:
                    limit = int(row['Custom Input'])
                except ValueError:
                    # go back do the default which is None
                    limit = None
                test.generate_test(outpath, libmanager, limit=limit)
            else:
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
