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
sys.path.insert(1, '../')
from parsersD1S import (Reaction, ReactionFile, Irradiation, IrradiationFile)


INP = os.path.join('TestFiles', 'parserD1S', 'reac_fe')


class TestIrradiationFile:

    def test_fromtext(self):
        """
        Test parsing irradiation file 1
        """
        filepath = os.path.join('TestFiles', 'parserD1S', 'irr_test')
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
        filepath = os.path.join('TestFiles', 'parserD1S', 'irr_test2')
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
        infile = os.path.join('TestFiles', 'parserD1S', 'irr_test')
        outfile = 'tmp_irr_test'
        irrfile = IrradiationFile.from_text(infile)
        irrfile.write(outfile)
        irrfile = IrradiationFile.from_text(outfile)
        self._assert_file1(irrfile)
        os.remove(outfile)

    def test_write2(self):
        """
        Test writing irradiation file 2
        """
        infile = os.path.join('TestFiles', 'parserD1S', 'irr_test2')
        outfile = 'tm_irr_test'
        irrfile = IrradiationFile.from_text(infile)
        irrfile.write(outfile)
        irrfile = IrradiationFile.from_text(outfile)
        self._assert_file2(irrfile)
        os.remove(outfile)


class TestIrradiation:

    def test_reading(self):
        """
        Test the reading of irradiation line
        """
        text = '   24051     2.896e-07    5.982e+00    5.697e+00     Cr51'
        irr = Irradiation.from_text(text, 2)
        self.assert_irr(irr)

    @staticmethod
    def assert_irr(irr):
        """
        Assert irradiation
        """
        assert irr.daughter == '24051'
        assert irr.lambd == '2.896e-07'
        assert irr.times[0] == '5.982e+00'
        assert irr.times[1] == '5.697e+00'
        assert irr.comment == 'Cr51'


class TestReaction:

    def test_fromtext1(self):
        """
        Test different formatting possibilities
        """
        text = '26054.99c  102  26055     Fe55'
        reaction = Reaction.from_text(text)
        assert reaction.parent == '26054.99c'
        assert reaction.MT == '102'
        assert reaction.daughter == '26055'
        assert reaction.comment == 'Fe55'

    def test_fromtext2(self):
        """
        Test different formatting possibilities
        """
        text = '26054.99c 102   26055 Fe55  and some'
        reaction = Reaction.from_text(text)
        assert reaction.parent == '26054.99c'
        assert reaction.MT == '102'
        assert reaction.daughter == '26055'
        assert reaction.comment == 'Fe55 and some'

    def test_changelib(self):
        """
        Test change library tag
        """
        rec = Reaction('26054.99c', '102', '26055')
        rec.change_lib('31c')
        assert rec.parent == '26054.31c'

    def test_write(self):
        """
        check writing
        """
        text = '26054.99c  102  26055     Fe55 and  some'
        reaction = Reaction.from_text(text)
        ftext = reaction.write()
        comptext = '26054.99c 102 26055 Fe55 and some'
        assert comptext == ftext


class TestReactionFile:
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
        outpath = 'tmp'
        reac_file = ReactionFile.from_text(INP)
        reac_file.write(outpath)
        newfile = ReactionFile.from_text(outpath)
        # Remove the temporary file
        os.remove(outpath)
        # do some operations
        newfile.change_lib('31c')
        assert len(newfile.reactions) == 10
        # Check also first line
        rx = newfile.reactions[0]
        assert rx.parent == '26054.31c'
        assert rx.MT == '102'
        assert rx.daughter == '26055'
        assert rx.comment == 'Fe55'
