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


def executeBenchmarksRoutines(session, lib, exp=False):
    """
    Check which benchmarks have to be generated and/or run and execute their
    routines

    Parameters
    ----------
    session : jade.Session
        Current JADE session.
    lib : str
        library to assess (e.g. 31c).
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
            outpath = os.path.join(session.path_run, lib)  # get path to libdir
            safemkdir(outpath)
            fname = row['File Name']
            inpfile = os.path.join(session.path_inputs, fname)
            VRTpath = os.path.join(session.path_inputs, 'VRT')
            confpath = os.path.join(session.path_cnf, fname.split('.')[0])

            # Generate test
            # Special case for sphere leak
            if testname == 'Sphere Leakage Test':
                test = testrun.SphereTest(inpfile, lib, row, log, VRTpath,
                                          confpath)
            elif testname == 'Oktavian Experiment':
                test = testrun.MultipleTest(inpfile, lib, row, log, VRTpath,
                                            confpath)
            else:
                test = testrun.Test(inpfile, lib, row, log, VRTpath,
                                    confpath)

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
