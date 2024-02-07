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
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)
sys.path.insert(1, root)

from jade.configuration import Log
from jade.testrun import Test, SphereTest, SphereTestSDDR, FNGTest, MultipleTest
from jade.libmanager import LibManager
import pytest

# Get a libmanager
ACTIVATION_FILE = os.path.join(cp, "TestFiles", "libmanager", "Activation libs.xlsx")
XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")

# Useful files
FILES = os.path.join(cp, "TestFiles", "testrun")
LOGFILE = Log("dummy.txt")


@pytest.fixture
def LM():
    df_rows = [
        ["99c", "sda", "", XSDIR_FILE],
        ["98c", "acsdc", "", XSDIR_FILE],
        ["21c", "adsadsa", "", XSDIR_FILE],
        ["31c", "adsadas", "", XSDIR_FILE],
        ["00c", "sdas", "", XSDIR_FILE],
        ["71c", "sdasxcx", "", XSDIR_FILE],
        ["81c", "sdasxcx", "yes", XSDIR_FILE],
    ]
    df_lib = pd.DataFrame(df_rows)
    df_lib.columns = ["Suffix", "Name", "Default", "MCNP"]

    return LibManager(
        df_lib, activationfile=ACTIVATION_FILE, isotopes_file=ISOTOPES_FILE
    )


class TestTest:
    files = os.path.join(FILES, "Test")
    dummyout = os.path.join(FILES, "dummy")

    def test_build_normal(self, LM):
        # Just check that nothing breaks
        lib = "81c"
        inp_name = "ITER_1D"
        inp = os.path.join(self.files, inp_name)
        config_data = {
            "Description": "dummy",
            "Folder Name": inp_name,
            "OnlyInput": True,
            "Post-Processing": False,
            "NPS cut-off": 10,
            # "CTME cut-off": 10,
            # "Relative Error cut-off": "F1-0.1",
            "Custom Input": 2,
            "MCNP": True,
        }
        config = pd.Series(config_data)
        VRTpath = "dummy"
        conf_path = "dummy"

        # Build the test
        test = Test(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)

        assert True

    def test_build_d1s(self, LM):
        # Just check that nothing breaks
        lib = "99c-31c"
        inp_name = "ITER_Cyl_SDDR.i"
        inp = os.path.join(self.files, inp_name)
        config_data = {
            "Description": "dummy",
            "Folder Name": inp_name,
            "OnlyInput": True,
            "Run": False,
            "Post-Processing": False,
            "NPS cut-off": 10,
            "CTME cut-off": None,
            "Relative Error cut-off": None,
            "Custom Input": 2,
            "Code": "D1S5",
        }
        config = pd.Series(config_data)
        VRTpath = os.path.join(self.files, "VRT")
        conf_path = "dummy"

        # Build the test
        test = Test(inp, lib, config, LOGFILE, VRTpath, conf_path)
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestSphereTest:
    files = os.path.join(FILES, "SphereTest")
    dummyout = os.path.join(FILES, "dummy")

    def test_build(self, LM):
        # Just check that nothing breaks
        lib = "31c"
        inp_name = "Sphere"
        inp = os.path.join(self.files, inp_name)
        config_data = {
            "Description": "dummy",
            "File Name": inp_name,
            "OnlyInput": True,
            "Post-Processing": False,
            "NPS cut-off": 10,
            "CTME cut-off": None,
            "Relative Error cut-off": None,
            "Custom Input": 3,
            "MCNP": True,
        }
        config = pd.Series(config_data)
        conf_path = os.path.join(self.files, "Spherecnf")

        # Build the test
        test = SphereTest(inp, lib, config, LOGFILE, conf_path, runoption="c")
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestSphereTestSDDR:
    files = os.path.join(FILES, "SphereTestSDDR")
    dummyout = os.path.join(FILES, "dummy")

    def test_build(self, LM):
        # Just check that nothing breaks
        lib = "99c-31c"
        inp_name = "SphereSDDR"
        inp = os.path.join(self.files, inp_name)
        config_data = {
            "Description": "dummy",
            "File Name": inp_name,
            "OnlyInput": True,
            "Post-Processing": False,
            "NPS cut-off": 10,
            # "CTME cut-off": None,
            # "Relative Error cut-off": None,
            "Custom Input": 3,
            "Code": "d1S",
        }
        config = pd.Series(config_data)
        # VRTpath = "dummy"
        conf_path = os.path.join(self.files, "cnf")

        # Build the test
        test = SphereTestSDDR(inp, lib, config, LOGFILE, conf_path, runoption="c")
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True


class TestMultipleTest:
    files = os.path.join(FILES, "MultipleTest")
    dummyout = os.path.join(FILES, "dummy")

    def test_build(self, LM):
        # Just check that nothing breaks
        lib = "31c"
        # inp_folder = os.path.join(self.files, "Inputs")
        inp_name = "Oktavian"
        inp = os.path.join(self.files, inp_name)
        config_data = {
            "Description": "dummy",
            "Folder Name": inp_name,
            "OnlyInput": True,
            "Post-Processing": False,
            "NPS cut-off": 10,
            # "CTME cut-off": None,
            # "Relative Error cut-off": None,
            "Custom Input": 3,
            "MCNP": True,
        }
        config = pd.Series(config_data)
        # VRTpath = "dummy"
        conf_path = os.path.join(self.files, "cnf")

        # Build the test
        test = MultipleTest(inp, lib, config, LOGFILE, conf_path, runoption="c")
        try:
            os.mkdir(self.dummyout)
            test.generate_test(self.dummyout, LM)
        finally:
            rmtree(self.dummyout)
        assert True
