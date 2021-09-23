# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 12:53:52 2021

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
import sys
import os

sys.path.insert(1, '../')
from libmanager import LibManager
import output


# Files
OUTP_SDDR = os.path.join('TestFiles', 'sphereoutput',
                         'SphereSDDR_11023_Na-23_102_o')
OUTM_SDDR = os.path.join('TestFiles', 'sphereoutput',
                         'SphereSDDR_11023_Na-23_102_m')


class TestSphereSDDRMCNPoutput:

    def test_organizemctal(self):
        out = output.MCNPoutput(OUTM_SDDR, OUTP_SDDR)
        t4 = out.tallydata[4]
        t2 = out.tallydata[2]
        assert list(t4.columns) == ['Cells', 'Segments', 'Value', 'Error']
        assert len(t4) == 1
        assert len(t2) == 176
        assert list(t2.columns) == ['Energy', 'Value', 'Error']
