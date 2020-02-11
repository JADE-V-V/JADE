# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:33:01 2020

@author: Davide Laghi
"""
import datetime
import output as o
import warnings


def postprocessSphere(session, lib):
    print(' Post-Processing Sphere Leakage test:' +
          '    '+str(datetime.datetime.now()))
    out = o.SphereOutput(lib, 'Sphere')
    out.single_postprocess()
    session.log.adjourn('Sphere Leakage benchmark post-processing coompleted' +
                        '    ' + str(datetime.datetime.now()))


def compareSphere(session, lib_input):
    print(' Comparing Sphere Leakage test:' +
          '    '+str(datetime.datetime.now()))
    lib = lib_input.split('-')
    out = o.SphereOutput(lib, 'Sphere')
    out.compare(session.state)
    session.log.adjourn('Sphere Leakage benchmark comparison coompleted' +
                        '    ' + str(datetime.datetime.now()))
