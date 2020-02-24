# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 16:52:36 2019

@author: Davide Laghi
"""
import testrun
import os
import datetime

mcnptag = '01_MCNP_Run'
inputdir = 'Benchmarks inputs'


def sphereTestRun(session, lib):
    """
    Function executing the sphere leakage test
    """
    log = session.log
    print('        -- SPHERE LEAKAGE TEST STARTED --\n')
    print(' Generating input files:'+'    '+str(datetime.datetime.now()))
    log.adjourn('Sphere test run started' + '    ' +
                str(datetime.datetime.now()))

    # --- Input Generation ---
    libmanager = session.lib_manager
    # Get directory
    cp = os.getcwd()
    cp = os.path.dirname(cp)
    cpt = os.path.join(cp, 'Tests')
#    safemkdir(os.path.join(cp,'Sphere'))
    cpt = os.path.join(cpt, mcnptag)
    safemkdir(cpt)
    outpath = os.path.join(cpt, lib)
    safemkdir(outpath)
    # Get the settings for the test
    config = session.conf.comp_default.set_index('Description')
    config = config.loc['Sphere Leakage Test']

    fname = config['File Name']
    inpfile = os.path.join(cp, inputdir, fname)
    spheretest = testrun.SphereTest(inpfile, lib, config, log)
    spheretest.generate_test(libmanager, outpath)
    # Adjourn log
    log.adjourn('Sphere test input generated with success'+'    ' +
                str(datetime.datetime.now()))

    if bool(config['OnlyInput']):
        print('\n        -- SPHERE LEAKAGE TEST COMPLETED --\n')
        # Adjourn log
        log.adjourn('Sphere test inputs generated with success' +
                    '    ' + str(datetime.datetime.now()))
    else:
        # --- Input Run ---
        print(' MCNP run running:         '+str(datetime.datetime.now()))
        spheretest.run(cpu=session.conf.cpu)
        print('\n        -- SPHERE LEAKAGE TEST COMPLETED --\n')
        # Adjourn log
        log.adjourn('Sphere test run completed with success'+'    ' +
                    str(datetime.datetime.now()))


def safemkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
