"""

@author: Davide Laghi

Copyright 2022, the JADE Development Team. All rights reserved.

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
from shutil import rmtree

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from configuration import Log
from testrun import Test, SphereTest, SphereTestSDDR, FNGTest, MultipleTest
from tests.configuration_test import LOGFILE
from libmanager import LibManager

# Get a libmanager
ACTIVATION_FILE = os.path.join(cp, 'TestFiles', 'libmanager',
                               'Activation libs.xlsx')
XSDIR_FILE = os.path.join(cp, 'TestFiles', 'libmanager', 'xsdir')
ISOTOPES_FILE = os.path.join(modules_path, 'Isotopes.txt')
LM = LibManager(XSDIR_FILE, activationfile=ACTIVATION_FILE,
                isotopes_file=ISOTOPES_FILE)

# Useful files
FILES = os.path.join(cp, 'TestFiles', 'testrun')
LOGFILE = Log('dummy.txt')


class TestTest:
    files = os.path.join(FILES, 'Test')
    dummyout = os.path.join(FILES, 'dummy')

    def test_build_normal(self):
        # Just check that nothing breaks
        lib = '81c'
        inp_name = 'ITER_1D.i'
        inp = os.path.join(self.files, inp_name)
        config_data = {'Description': 'dummy',
                       'File Name': inp_name,
                       'OnlyInput': True,
                       'Run': False,
                       'Post-Processing': False,
                       'NPS cut-off': 10,
                       'CTME cut-off': 10,
                       'Relative Error cut-off': 'F1-0.1',
                       'Custom Input': 2,
                       'Code': 'mcnp6'}
        config = pd.Series(config_data)
        VRTpath = 'dummy'
        conf_path = 'dummy'

        # Build the test
        test = Test(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)

        assert True

    def test_build_d1s(self):
        # Just check that nothing breaks
        lib = '99c-31c'
        inp_name = 'ITER_Cyl_SDDR.i'
        inp = os.path.join(self.files, inp_name)
        config_data = {'Description': 'dummy',
                       'File Name': inp_name,
                       'OnlyInput': True,
                       'Run': False,
                       'Post-Processing': False,
                       'NPS cut-off': 10,
                       'CTME cut-off': None,
                       'Relative Error cut-off': None,
                       'Custom Input': 2,
                       'Code': 'D1S5'}
        config = pd.Series(config_data)
        VRTpath = os.path.join(self.files, 'VRT')
        conf_path = 'dummy'

        # Build the test
        test = Test(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestSphereTest:
    files = os.path.join(FILES, 'SphereTest')
    dummyout = os.path.join(FILES, 'dummy')

    def test_build(self):
        # Just check that nothing breaks
        lib = '31c'
        inp_name = 'Sphere.i'
        inp = os.path.join(self.files, inp_name)
        config_data = {'Description': 'dummy',
                       'File Name': inp_name,
                       'OnlyInput': True,
                       'Run': False,
                       'Post-Processing': False,
                       'NPS cut-off': 10,
                       'CTME cut-off': None,
                       'Relative Error cut-off': None,
                       'Custom Input': 3,
                       'Code': 'mcnp6'}
        config = pd.Series(config_data)
        VRTpath = 'dummy'
        conf_path = os.path.join(self.files, 'Spherecnf')

        # Build the test
        test = SphereTest(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestSphereTestSDDR:
    files = os.path.join(FILES, 'SphereTestSDDR')
    dummyout = os.path.join(FILES, 'dummy')

    def test_build(self):
        # Just check that nothing breaks
        lib = '99c-31c'
        inp_name = 'SphereSDDR.i'
        inp = os.path.join(self.files, inp_name)
        config_data = {'Description': 'dummy',
                       'File Name': inp_name,
                       'OnlyInput': True,
                       'Run': False,
                       'Post-Processing': False,
                       'NPS cut-off': 10,
                       'CTME cut-off': None,
                       'Relative Error cut-off': None,
                       'Custom Input': 3,
                       'Code': 'D1S5'}
        config = pd.Series(config_data)
        VRTpath = 'dummy'
        conf_path = os.path.join(self.files, 'cnf')

        # Build the test
        test = SphereTestSDDR(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestMultipleTest:
    files = os.path.join(FILES, 'MultipleTest')
    dummyout = os.path.join(FILES, 'dummy')

    def test_build(self):
        # Just check that nothing breaks
        lib = '31c'
        inp_folder = os.path.join(self.files, 'Inputs')
        inp_name = 'Oktavian'
        config_data = {'Description': 'dummy',
                       'File Name': inp_name,
                       'OnlyInput': True,
                       'Run': False,
                       'Post-Processing': False,
                       'NPS cut-off': 10,
                       'CTME cut-off': None,
                       'Relative Error cut-off': None,
                       'Custom Input': 3,
                       'Code': 'mcnp6'}
        config = pd.Series(config_data)
        VRTpath = 'dummy'
        conf_path = os.path.join(self.files, 'cnf')

        # Build the test
        test = MultipleTest(inp_folder, lib, config, LOGFILE, VRTpath,
                            conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True
