# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 10:15:09 2021

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
from jade.parsersD1S import (
    Reaction,
    ReactionFile,
    Irradiation,
    IrradiationFile,
    REACFORMAT,
)
from jade.libmanager import LibManager
import pandas as pd

cp = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cp)
sys.path.insert(1, root)


INP = os.path.join(cp, "TestFiles", "parserD1S", "reac_fe")


class TestIrradiationFile:

    def test_fromtext(self):
        """
        Test parsing irradiation file 1
        """
        filepath = os.path.join(cp, "TestFiles", "parserD1S", "irr_test")
        irrfile = IrradiationFile.from_text(filepath)
        self._assert_file1(irrfile)

    @staticmethod
    def _assert_file1(irrfile):
        assert len(irrfile.irr_schedules) == 4
        TestIrradiation.assert_irr(irrfile.irr_schedules[0])

    def test_fromtext2(self):
        """
        Test parsing irradiation file 2
        """
        filepath = os.path.join(cp, "TestFiles", "parserD1S", "irr_test2")
        irrfile = IrradiationFile.from_text(filepath)
        self._assert_file2(irrfile)

    @staticmethod
    def _assert_file2(irrfile):
        assert len(irrfile.irr_schedules) == 4
        TestIrradiation.assert_irr(irrfile.irr_schedules[0])

    def test_write(self):
        """
        Test writing irradiation file 1
        """
        infile = os.path.join(cp, "TestFiles", "parserD1S", "irr_test")
        outfile = "irrad"
        irrfile = IrradiationFile.from_text(infile)
        irrfile.write(os.getcwd())
        irrfile = IrradiationFile.from_text(outfile)
        self._assert_file1(irrfile)
        os.remove(outfile)

    def test_write2(self):
        """
        Test writing irradiation file 2
        """
        infile = os.path.join(cp, "TestFiles", "parserD1S", "irr_test2")
        outfile = "irrad"
        irrfile = IrradiationFile.from_text(infile)
        irrfile.write(os.getcwd())
        irrfile = IrradiationFile.from_text(outfile)
        self._assert_file2(irrfile)
        os.remove(outfile)

    def test_get_daughters(self):
        infile = os.path.join(cp, "TestFiles", "parserD1S", "irr_test")
        irrfile = IrradiationFile.from_text(infile)
        daughters = irrfile.get_daughters()
        assert daughters == ["24051", "25054", "26055", "26059"]

    def test_get_irrad(self):
        infile = os.path.join(cp, "TestFiles", "parserD1S", "irr_test")
        irrfile = IrradiationFile.from_text(infile)
        # Check the None
        irradiation = irrfile.get_irrad("20051")
        assert irradiation is None
        # Check true value
        irradiation = irrfile.get_irrad("26055")
        assert irradiation.daughter == "26055"


class TestIrradiation:

    def test_reading(self):
        """
        Test the reading of irradiation line
        """
        text = "   24051     2.896e-07    5.982e+00    5.697e+00     Cr51"
        irr = Irradiation.from_text(text, 2)
        self.assert_irr(irr)

    @staticmethod
    def assert_irr(irr):
        """
        Assert irradiation
        """
        assert irr.daughter == "24051"
        assert irr.lambd == "2.896e-07"
        assert irr.times[0] == "5.982e+00"
        assert irr.times[1] == "5.697e+00"
        assert irr.comment == "Cr51"

    def test_equivalence(self):
        # Equivalent
        text = "   24051     2.896e-07    5.982e+00    5.697e+00     Cr51"
        irr1 = Irradiation.from_text(text, 2)
        text = "   24051     2.896e-07    5.982e+00    5.697     "
        irr2 = Irradiation.from_text(text, 2)
        assert irr1 == irr2

        # Not equal
        text = "   24051     2.896e-07    5.697e+00    5.982e+00     Cr51"
        irr3 = Irradiation.from_text(text, 2)
        text = "   24051     2.896e-07    5.697e+00    Cr51"
        irr4 = Irradiation.from_text(text, 1)
        assert irr1 != irr3
        assert irr1 != {}
        assert irr1 != irr4


class TestReaction:

    def test_fromtext1(self):
        """
        Test different formatting possibilities
        """
        text = "   26054.99c  102  26055     Fe55"
        reaction = Reaction.from_text(text)
        assert reaction.parent == "26054.99c"
        assert reaction.MT == "102"
        assert reaction.daughter == "26055"
        assert reaction.comment == "Fe55"

    def test_fromtext2(self):
        """
        Test different formatting possibilities
        """
        text = "26054.99c 102   26055 Fe55  and some"
        reaction = Reaction.from_text(text)
        assert reaction.parent == "26054.99c"
        assert reaction.MT == "102"
        assert reaction.daughter == "26055"
        assert reaction.comment == "Fe55 and some"

    def test_changelib(self):
        """
        Test change library tag
        """
        rec = Reaction("26054.99c", "102", "26055")
        rec.change_lib("31c")
        assert rec.parent == "26054.31c"

    def test_write(self):
        """
        check writing
        """
        text = "26054.99c  102  26055     Fe55 and  some"
        reaction = Reaction.from_text(text)
        ftext = reaction.write()
        comptext = ["26054.99c", "102", "26055", "Fe55 and some"]
        assert comptext == ftext


class TestReactionFile:

    @pytest.fixture
    def lm(self):
        xsdirpath = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
        activationfile = os.path.join(
            cp, "TestFiles", "libmanager", "Activation libs.xlsx"
        )

        df_rows = [
            ["99c", "sda", "", xsdirpath],
            ["98c", "acsdc", "", xsdirpath],
            ["21c", "adsadsa", "", xsdirpath],
            ["31c", "adsadas", "", xsdirpath],
            ["00c", "sdas", "yes", xsdirpath],
            ["71c", "sdasxcx", "", xsdirpath],
        ]
        df_lib = pd.DataFrame(df_rows)
        df_lib.columns = ["Suffix", "Name", "Default", "MCNP"]
        isotopes_file = os.path.join(root, "jade", "resources", "Isotopes.txt")
        return LibManager(
            df_lib, activationfile=activationfile, isotopes_file=isotopes_file
        )

    def test_fromtext(self):
        """
        right number of reactions
        """
        reac_file = ReactionFile.from_text(INP)
        print(reac_file.reactions)
        assert len(reac_file.reactions) == 10

    def test_write(self):
        """
        writing works
        """
        outpath = "react"
        reac_file = ReactionFile.from_text(INP)
        reac_file.write(os.getcwd())
        newfile = ReactionFile.from_text(outpath)
        # Remove the temporary file
        os.remove(outpath)
        # do some operations
        newfile.change_lib("31c")
        assert len(newfile.reactions) == 10
        # Check also first line
        rx = newfile.reactions[0]
        assert rx.parent == "26054.31c"
        assert rx.MT == "102"
        assert rx.daughter == "26055"
        assert rx.comment == "Fe55"

    def test_translation(self, lm):
        """
        test translation with libmanager where parents are available

        """
        newlib = "98c"

        reac_file = ReactionFile.from_text(INP)
        reac_file.change_lib(newlib, libmanager=lm)

        for reaction in reac_file.reactions:
            assert reaction.parent[-3:] == newlib

    def test_translation2(self, lm):
        """
        test translation with libmanager where parents are not available

        """

        filepath = os.path.join(cp, "TestFiles", "parserD1S", "reac2")

        newlib = "99c"

        reac_file = ReactionFile.from_text(filepath)
        reac_file.change_lib(newlib, libmanager=lm)

        for reaction in reac_file.reactions:
            assert reaction.parent[-3:] != newlib

    def test_get_parents(self):
        filepath = os.path.join(cp, "TestFiles", "parserD1S", "reac_fe")
        reac_file = ReactionFile.from_text(filepath)
        parents = reac_file.get_parents()
        assert parents == ["26054", "26056", "26057", "26058"]
