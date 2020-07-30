# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:33:01 2020

@author: Davide Laghi
"""
import datetime
import sphereoutput as spho
import output as bencho


def compareBenchmark(session, lib_input, testname):
    print('\n Comparing '+testname+':' +
          '    '+str(datetime.datetime.now()))
    lib = lib_input.split('-')
    if testname == 'Sphere':
        out = spho.SphereOutput(lib, 'Sphere', session)
    else:
        out = bencho.BenchmarkOutput(lib, testname, session)

    out.compare(session.state, session.lib_manager)
    session.log.adjourn(testname+' benchmark comparison completed' +
                        '    ' + str(datetime.datetime.now()))


def postprocessBenchmark(session, lib, testname):
    print('\n Post-Processing '+testname+':' +
          '    '+str(datetime.datetime.now()))
    if testname == 'Sphere':
        out = spho.SphereOutput(lib, testname, session)
    else:
        out = bencho.BenchmarkOutput(lib, testname, session)

    out.single_postprocess(session.lib_manager)
    session.log.adjourn(testname+' benchmark post-processing completed' +
                        '    ' + str(datetime.datetime.now()))
