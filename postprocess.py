# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:33:01 2020

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
import datetime
import sphereoutput as spho
import output as bencho
import expoutput as expo


def compareBenchmark(session, lib_input, testname):
    print('\n Comparing '+testname+':' +
          '    '+str(datetime.datetime.now()))
    lib = lib_input.split('-')
    if testname == 'Sphere':
        out = spho.SphereOutput(lib, testname, session)
    elif testname == 'Oktavian':
        out = expo.OktavianOutput(lib, testname, session)
    else:
        out = bencho.BenchmarkOutput(lib, testname, session)

    out.compare()
    session.log.adjourn(testname+' benchmark comparison completed' +
                        '    ' + str(datetime.datetime.now()))


def postprocessBenchmark(session, lib, testname):
    print('\n Post-Processing '+testname+':' +
          '    '+str(datetime.datetime.now()))
    if testname == 'Sphere':
        out = spho.SphereOutput(lib, testname, session)
    elif testname == 'Oktavian':
        print('\n No single pp is foreseen for experimental benchmarks')
        return
    else:
        out = bencho.BenchmarkOutput(lib, testname, session)

    out.single_postprocess()
    session.log.adjourn(testname+' benchmark post-processing completed' +
                        '    ' + str(datetime.datetime.now()))
