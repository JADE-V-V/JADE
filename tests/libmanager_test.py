# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 18:02:40 2021

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
import pytest
import pandas as pd

cp = os.path.dirname(os.path.abspath(__file__))
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)
sys.path.insert(1, root)

from jade.libmanager import LibManager
from jade.matreader import Zaid


ACTIVATION_FILE = os.path.join(cp, "TestFiles", "libmanager", "Activation libs.xlsx")
XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")


class TestLibManger:

    @pytest.fixture
    def lm(self):
        df_rows = [
            ["99c", "sda", "", XSDIR_FILE],
            ["98c", "acsdc", "", XSDIR_FILE],
            ["21c", "adsadsa", "", XSDIR_FILE],
            ["31c", "adsadas", "", XSDIR_FILE],
            ["00c", "sdas", "yes", XSDIR_FILE],
            ["71c", "sdasxcx", "", XSDIR_FILE],
        ]
        df_lib = pd.DataFrame(df_rows)
        df_lib.columns = ["Suffix", "Name", "Default", "MCNP"]

        return LibManager(
            df_lib, activationfile=ACTIVATION_FILE, isotopes_file=ISOTOPES_FILE
        )

    def test_available_libs(self, lm: LibManager):
        """
        Test the ability to recover the available libraries
        """
        libs = lm.libraries["mcnp"]
        assert "99c" in libs
        assert "98c" in libs
        assert "21c" in libs
        assert "31c" in libs
        assert "00c" in libs
        assert "71c" in libs

    def test_reactionfilereading(self, lm):
        assert len(lm.reactions["99c"]) == 100
        assert len(lm.reactions["98c"]) == 34

    def test_get_reactions1(self, lm):
        """
        Test ability to recover reactions for parent zaid (one)
        """
        parent = "9019"
        reaction = lm.get_reactions("99c", parent)[0]
        assert reaction[0] == "16"
        assert reaction[1] == "9018"

    def test_get_reactions2(self, lm):
        """
        Test ability to recover reactions for parent zaid (multiple)
        """
        parent = "11023"
        reactions = lm.get_reactions("99c", parent)
        print(reactions)
        reaction1 = reactions[0]
        reaction2 = reactions[1]

        assert reaction1[0] == "16"
        assert reaction1[1] == "11022"
        assert reaction2[0] == "102"
        assert reaction2[1] == "11024"

    def test_formula_conversion(self, lm):
        """
        Test the abilty to switch between isotopes formulas and zaid number
        """
        tests = ["N15", "Er164", "Kr83"]
        finals = ["N-15", "Er-164", "Kr-83"]
        for test, final in zip(tests, finals):
            conversion = lm.get_zaidnum(test)
            name, formula = lm.get_zaidname(conversion)

            assert final == formula

    def test_check4zaid(self, lm: LibManager):
        """
        Correctly checks availability of zaids
        """
        zaid = "1001"
        libs = lm.check4zaid(zaid)
        assert len(libs) > 1
        assert len(libs[0]) == 3

        zaid = "1010"
        assert len(lm.check4zaid(zaid)) == 0

    def test_convertZaid(self, lm: LibManager):
        # --- Exception if library is not available ---
        try:
            zaid = "1001"
            lib = "44c"
            lm.convertZaid(zaid, lib)
            assert False
        except ValueError:
            assert True

        # --- Natural zaid ---
        # 1 to 1
        zaid = "12000"
        lib = "21c"
        translation = lm.convertZaid(zaid, lib)
        assert translation == {zaid: (lib, 1, 1)}
        # expansion
        lib = "31c"
        translation = lm.convertZaid(zaid, lib)
        assert len(translation) == 3
        # not available in the requested lib but available in default

        # available only in the default library
        zaid = "84000"
        translation = lm.convertZaid(zaid, lib)
        assert translation["84209"][0] == "00c"

        # --- 1 to 1 ---
        zaid = "1001"
        translation = lm.convertZaid(zaid, lib)
        assert translation == {zaid: (lib, 1, 1)}

        # --- absent ---
        # Use the natural zaid
        zaid = "12024"
        lib = "21c"
        translation = lm.convertZaid(zaid, lib)
        assert translation == {"12000": (lib, 1, 1)}

        # zaid available in default or other library
        zaid = "84210"
        translation = lm.convertZaid(zaid, lib)
        assert translation[zaid][0] != lib

        # zaid does not exist or not available in any library
        zaid = "84200"
        try:
            translation = lm.convertZaid(zaid, lib)
            assert False
        except ValueError:
            assert True

    def test_get_libzaids(self, lm):

        lib = "21c"
        zaids = lm.get_libzaids(lib)
        assert len(zaids) == 76
        assert zaids[0] == "1001"

    def test_get_zaidname(self, lm):
        zaid = "1001"
        name, formula = lm.get_zaidname(zaid)
        assert name == "hydrogen"
        assert formula == "H-1"

        zaid = "1000"
        name, formula = lm.get_zaidname(zaid)
        assert name == "hydrogen"
        assert formula == "H-0"

    def test_get_zaidnum(self, lm):
        zaid = "92235"
        try:
            zaidnum = lm.get_zaidnum(zaid)
            assert False
        except ValueError:
            assert True

        zaid = "U235"
        zaidnum = lm.get_zaidnum(zaid)
        assert zaidnum == "92235"

    def test_select_lib(self, monkeypatch, lm):
        # monkeypatch the "input" function

        # Good trials
        for lib in ["31c", '{"21c": "31c", "00c": "71c"}', "21c-31c"]:
            monkeypatch.setattr("builtins.input", lambda _: lib)
            selectedlib = lm.select_lib()
            assert selectedlib == lib

        # Not found
        for lib in ["44c", '{"21c": "44c", "44c": "71c"}', "21c-44c"]:
            monkeypatch.setattr("builtins.input", lambda _: lib)
            try:
                selectedlib = lm.select_lib()
                print(lib)
                assert False
            except ValueError:
                assert True

    def test_get_zaid_mass(self, lm):
        # Normal zaid
        zaid = "99235.31c  -1"
        zaid = Zaid.from_string(zaid)
        mass = lm.get_zaid_mass(zaid)
        assert mass == 252.08298
        # Natural zaid
        zaid = "8000.21c  1"
        zaid = Zaid.from_string(zaid)
        mass = lm.get_zaid_mass(zaid)
        assert mass == 15.99937442590581
