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
import pandas as pd
import pytest

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from jade.libmanager import LibManager
import jade.sphereoutput as sout

class MockSphereOutput(sout.SphereOutput):
    def __init__(self):
        self.lib = '00c'
        self.testname = 'Sphere'
        self.test_path = os.path.join(cp, 'TestFiles', 'sphereoutput', 'Sphere')
        mat_settings = [
            {"num": "M101", "Name": "material", "other": 1},
            {"num": "dummy", "Name": "dummy", "dummy": 1},
        ]
        self.mat_settings = pd.DataFrame(mat_settings).set_index("num")
        self.raw_data = {'mcnp' : {},
                         'serpent' : {},
                         'openmc' : {}}
        self.outputs = {'mcnp' : {},
                        'serpent' : {},
                        'openmc' : {}}

class TestSphereOutput:
    mockoutput = MockSphereOutput()

    def test_read_mcnp_output(self):
        outputs, results, errors, stat_checks = self.mockoutput._read_mcnp_output()
        tally_values = outputs['M101'].tallydata['Value']
        tally_errors = outputs['M101'].tallydata['Error']

        assert 5.38195E-07 == pytest.approx(tally_values[10])
        assert 0.0859 == pytest.approx(tally_errors[176])
        assert results[0]['Zaid'] == 'M101'
        assert errors[0]['Neutron Flux in material cell in Vitamin-J 175 energy groups'] == 0.15204491017964072
        assert stat_checks[0]['Gamma flux in material cell [FINE@FISPACT MANUAL 24 Group Structure] [14]'] == 'Passed'

    def test_read_openmc_output(self):
        outputs, results, errors = self.mockoutput._read_openmc_output()
        tally_values = outputs['M101'].tallydata['Value']
        tally_errors = outputs['M101'].tallydata['Error']        

        assert 0.146561 == pytest.approx(tally_values[10])
        assert 0.00015034 == pytest.approx(tally_errors[176])
        assert results[0]['Zaid'] == 'M101'
        assert errors[0]['Neutron Spectra'] == 0.09626673662857144

# Files
OUTP_SDDR = os.path.join(
    cp, "TestFiles", "sphereoutput", "SphereSDDR_11023_Na-23_102_o"
)
OUTM_SDDR = os.path.join(
    cp, "TestFiles", "sphereoutput", "SphereSDDR_11023_Na-23_102_m"
)


class MockSphereSDDRoutput(sout.SphereSDDRoutput):
    def __init__(self):
        self.lib = "99c"
        self.testname = "SphereSDDR"
        self.test_path = os.path.join(
            cp, "TestFiles", "sphereoutput", "single_excel_sddr"
        )
        mat_settings = [
            {"num": "M203", "Name": "material", "other": 1},
            {"num": "dummy", "Name": "dummy", "dummy": 1},
        ]
        self.mat_settings = pd.DataFrame(mat_settings).set_index("num")
        self.raw_data = {}
        self.outputs = {}
        self.d1s = True


class TestSphereSDDRoutput:
    mockoutput = MockSphereSDDRoutput()

    def test_compute_single_results(self):

        cols = [
            "Parent",
            "Parent Name",
            "MT",
            "F1.0",
            "F2.0",
            "F3.0",
            "F4.0",
            "F5.0",
            "F6.0",
            "D1.0",
            "D2.0",
            "D3.0",
            "D4.0",
            "D5.0",
            "D6.0",
            "H1.0",
            "H2.0",
            "H3.0",
            "H4.0",
            "H5.0",
            "H6.0",
        ]

        outputs, results, errors, stat_checks = (
            self.mockoutput._compute_single_results()
        )
        for df in [results, errors, stat_checks]:
            assert len(df) == 2

        for df in [results, errors]:
            assert list(df.columns[:-5]) == cols

        # print(results)
        # print(errors)
        # print(stat_checks)
        # print(results.columns)


class TestSphereSDDRMCNPoutput:

    out = sout.SphereSDDRMCNPoutput(OUTM_SDDR, OUTP_SDDR)

    def test_get_single_excel_data(self):
        vals, errors = self.out.get_single_excel_data()
        assert isinstance(vals, pd.Series)
        assert isinstance(errors, pd.Series)
        assert len(vals) == 23
        assert len(errors) == 23
