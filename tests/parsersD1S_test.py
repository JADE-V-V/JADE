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
from parsersD1S import (Reaction, ReactionFile, Irradiation)


INP = os.path.join('TestFiles', 'reac_fe')


class TestIrradiation:

    def test_reading(self):
        text = '   24051     2.896e-07    5.982e+00    5.697e+00     Cr51'
        irr = Irradiation.from_text(text, 2)
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
