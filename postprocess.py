# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:33:01 2020

@author: Davide Laghi
"""
import datetime
import sphereoutput as spho
import output as bencho


def compareSphere(session, lib_input):
    print('\n Comparing Sphere Leakage test:' +
          '    '+str(datetime.datetime.now()))
    lib = lib_input.split('-')
    out = spho.SphereOutput(lib, 'Sphere', session)
    out.compare(session.state, session.lib_manager)
    session.log.adjourn('Sphere Leakage benchmark comparison coompleted' +
                        '    ' + str(datetime.datetime.now()))


def postprocessBenchmark(session, lib, testname):
    print('\n Post-Processing '+testname+':' +
          '    '+str(datetime.datetime.now()))
    if testname == 'Sphere':
        out = spho.SphereOutput(lib, testname, session)
    else:
        out = bencho.BenchmarkOutput(lib, testname, session)

    out.single_postprocess(session.lib_manager)
    session.log.adjourn(testname+' benchmark post-processing coompleted' +
                        '    ' + str(datetime.datetime.now()))
