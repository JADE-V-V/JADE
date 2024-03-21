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

resources = os.path.join(cp, "TestFiles", "sphereoutput")
CONFIG_FILE = os.path.join(resources, "mainconfig.xlsx")
root = os.path.dirname(cp)
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")

from jade.main import Session
from jade.configuration import Configuration
from jade.libmanager import LibManager
from jade.status import Status

import jade.sphereoutput as sout

class MockUpSession(Session):
    def __init__(self, tmpdir, lm: LibManager):
        self.conf = Configuration(CONFIG_FILE)
        self.path_comparison = os.path.join(tmpdir, "Post-Processing", "Comparisons")
        self.path_single = os.path.join(tmpdir, "Post-Processing", "Single_Libraries")
        self.path_pp = os.path.join(tmpdir, "Post-Processing")
        self.path_run = os.path.join(resources, "Simulations")
        self.path_test = resources
        self.path_templates = os.path.join(resources, "templates")
        self.path_cnf = os.path.join(resources, "Benchmarks_Configuration")
        self.path_quality = None
        self.path_uti = None
        self.lib_manager = lm

        keypaths = [self.path_pp,
                    self.path_comparison,
                    self.path_single]
        
        for path in keypaths:
            if not os.path.exists(path):
                os.mkdir(path)

        self.state = Status(self)

class TestSphereOutput:   
    @pytest.fixture()
    def session_mock(self, tmpdir, lm: LibManager):
        session = MockUpSession(tmpdir, lm)
        return session
    
    @pytest.fixture
    def lm(self):
        df_rows = [
            ["31c", "adsadas", ""],
            ["00c", "sdas", "yes"],
        ]
        df_lib = pd.DataFrame(df_rows)
        df_lib.columns = ["Suffix", "Name", "Default"]

        return LibManager(df_lib, isotopes_file=ISOTOPES_FILE)

    def test_sphereoutput_mcnp(self, session_mock: MockUpSession):     
        sphere_00c = sout.SphereOutput('00c', 'mcnp', 'Sphere', session_mock)
        sphere_00c.single_postprocess()
        sphere_31c = sout.SphereOutput('31c', 'mcnp', 'Sphere', session_mock)
        sphere_31c.single_postprocess()
        sphere_comp = sout.SphereOutput(['31c', '00c'], 'mcnp', 'Sphere', session_mock)
        sphere_comp.compare()
        assert True

    def test_sphereoutput_openmc(self, session_mock: MockUpSession):     
        sphere_00c = sout.SphereOutput('00c', 'openmc', 'Sphere', session_mock)
        sphere_00c.single_postprocess()
        sphere_31c = sout.SphereOutput('31c', 'openmc', 'Sphere', session_mock)
        sphere_31c.single_postprocess()
        sphere_comp = sout.SphereOutput(['31c', '00c'], 'openmc', 'Sphere', session_mock)
        sphere_comp.compare()
        assert True        

    def test_read_mcnp_output(self, session_mock: MockUpSession):       
        sphere_00c = sout.SphereOutput('00c', 'mcnp', 'Sphere', session_mock)
        outputs, results, errors, stat_checks = sphere_00c._read_mcnp_output()
        tally_values = outputs['M10'].tallydata['Value']
        tally_errors = outputs['M10'].tallydata['Error']
        assert 3.80420E-07 == pytest.approx(tally_values[10])
        assert 0.0406 == pytest.approx(tally_errors[175])
        assert 0.6213346456692914 == pytest.approx(errors[1]['Neutron Flux at the external surface in Vitamin-J 175 energy groups'])
        assert 'M10' == results[1]['Zaid']
        assert stat_checks[1]['Gamma flux at the external surface [22]'] == 'Missed'

    def test_read_openmc_output(self, session_mock: MockUpSession):       
        sphere_00c = sout.SphereOutput('00c', 'openmc', 'Sphere', session_mock)
        outputs, results, errors = sphere_00c._read_openmc_output()
        tally_values = outputs['M10'].tallydata['Value']
        tally_errors = outputs['M10'].tallydata['Error']        
        assert 0.827104 == pytest.approx(tally_values[10])
        assert 0.000227628 == pytest.approx(tally_errors[176])
        assert 0.10131285308571429 == pytest.approx(errors[1]['Neutron Spectra'])
        assert 'M10' == results[1]['Zaid']

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
        self.raw_data = {"d1s":{}}
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
