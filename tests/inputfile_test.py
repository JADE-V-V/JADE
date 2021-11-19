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

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from inputfile import (InputFile, D1S_Input)
from libmanager import LibManager
from parsersD1S import (IrradiationFile, ReactionFile)
from copy import deepcopy
import numpy as np

INP_PATH = os.path.join(cp, 'TestFiles/inputfile/test.i')
DIS_INP_PATH = os.path.join(cp, 'TestFiles/inputfile/d1stest.i')
DIS_NOPKMT_PATH = os.path.join(cp, 'TestFiles/inputfile/d1stest_noPKMT.i')
DIS_GETREACT_PATH = os.path.join(cp, 'TestFiles/inputfile/d1stest_getreact.i')

ACTIVATION_FILE = os.path.join(cp, 'TestFiles', 'libmanager',
                               'Activation libs.xlsx')
XSDIR_FILE = os.path.join(cp, 'TestFiles', 'libmanager', 'xsdir')

IRRAD_PATH = os.path.join(cp, 'TestFiles/inputfile/d1stest_irrad')
REACT_PATH = os.path.join(cp, 'TestFiles/inputfile/d1stest_react')


class TestInputFile:
    testInput = InputFile.from_text(INP_PATH)
    lm = LibManager(XSDIR_FILE, activationfile=ACTIVATION_FILE)

    def test_read_write(self):
        oldtext = self.testInput._to_text()
        # Dump it and re-read it
        dumpfile = 'tmp2.i'
        self.testInput.write(dumpfile)
        newinput = InputFile.from_text(dumpfile)
        # clear
        os.remove(dumpfile)
        newtext = newinput._to_text()
        print(len(newtext))

        assert oldtext == newtext

    def test_add_stopCard(self):
        tests = [(1e3, 500, ('F54', 0.001), 'STOP NPS 1000 CTME 500 F54 0.001\n'),
                 (None, 500, ('F54', 0.001), 'STOP CTME 500 F54 0.001\n'),
                 (1e3, None, ('F54', 0.001), 'STOP NPS 1000 F54 0.001\n'),
                 (1e3, np.nan, ('F54', 0.001), 'STOP NPS 1000 F54 0.001\n'),
                 (1e3, 500, None, 'STOP NPS 1000 CTME 500 \n'),
                 (None, None, ('F54', 0.001), 'STOP F54 0.001\n'),
                 (1e3, None, None, 'STOP NPS 1000 \n')]

        for test in tests:
            nps = test[0]
            ctme = test[1]
            precision = test[2]

            inp = deepcopy(self.testInput)

            inp.add_stopCard(nps, ctme, precision)

            stopcard = inp.get_card_byID('settings', 'STOP')
            assert stopcard.lines[0] == test[3]

        try:
            inp.add_stopCard(None, None, None)
            assert False
        except ValueError:
            assert True

    def test_change_density(self):
        newinp = deepcopy(self.testInput)
        density = 1
        newinp.change_density(density, cellidx=2)
        cellcard = newinp.get_card_byID('cells', '2')
        modline = '2    13  {}  -128 129 1   -2         \n'.format(str(density))
        assert newinp.cards['cells'][2].lines == modline

        try:
            newinp.change_density(1, cellidx=20000000)
            assert False
        except ValueError:
            assert True

    def test_translate(self):
        # The test for a correct translation of material card is already done
        # in matreader. here we only check that it goes trough without errors
        newinput = deepcopy(self.testInput)
        newinput.translate('00c', self.lm)
        newinput = deepcopy(self.testInput)
        newinput.translate('{"31c": "00c", "70c": "81c"}', self.lm)
        assert True

    def test_get_card_byID(self):
        """
        Test ability to select cards by block and card ID
        """
        examples = [('settings', 'fc234'), ('settings', 'Fmesh254:p'),
                    ('cells', 2), ('surf', 2)]
        last_digits = ['s]\n', '=1\n', '-2\n', '97\n']

        for ID, digits in zip(examples, last_digits):
            card = self.testInput.get_card_byID(ID[0], ID[1])
            print(card.lines[-1])
            assert card.lines[-1][-3:] == digits

        # Test also card not found
        card = self.testInput.get_card_byID('settings', 'Fmesh254:')
        assert card is None

        # Test error
        try:
            card = self.testInput.get_card_byID('dummy', 'Fmesh254:')
            assert False
        except KeyError:
            assert True

    def test_addlines2card(self):
        """
        test that a new card can be added to the input.
        """
        # modify one card of the official input
        blockID = 'settings'
        cardID = 'FMESH254:p'

        # --- do it with a list of lines
        # add lines
        inp = deepcopy(self.testInput)
        lines = ['FU4 sadadsda\n', '     adasdaasdas\n']
        inp.addlines2card(lines, blockID, cardID, offset_all=False)
        # dump and reread the input
        tmpfile = 'tmp.i'
        inp.write(tmpfile)
        newinp = InputFile.from_text(tmpfile)
        # Remove tmp file
        os.remove(tmpfile)
        # get the new injected card
        card = newinp.get_card_byID('settings', 'FU4')
        assert card is not None
        assert len(card.lines) == 2

        # do it with a text
        # add lines
        inp = deepcopy(self.testInput)
        lines = 'FU4 '+'ad '*120
        inp.addlines2card(lines, blockID, cardID, offset_all=False)
        # dump and reread the input
        tmpfile = 'tmp.i'
        inp.write(tmpfile)
        newinp = InputFile.from_text(tmpfile)
        # Remove tmp file
        os.remove(tmpfile)
        # get the new injected card
        card = newinp.get_card_byID('settings', 'FU4')
        assert card is not None
        assert len(card.lines) == 5

        # check simple adding of a line to existing card
        # add line
        inp = deepcopy(self.testInput)
        lines = 'newlineee'
        card = inp.get_card_byID(blockID, cardID)
        nlines = len(card.lines)
        inp.addlines2card(lines, blockID, cardID)
        # dump and reread the input
        tmpfile = 'tmp.i'
        inp.write(tmpfile)
        newinp = InputFile.from_text(tmpfile)
        # Remove tmp file
        os.remove(tmpfile)
        # get the new injected card
        card = newinp.get_card_byID(blockID, cardID)
        assert card is not None
        assert len(card.lines) == nlines+1

        # card not found
        ans = inp.addlines2card(lines, blockID, 'dummy')
        assert not ans


class TestD1S_Input:
    inp = D1S_Input.from_text(DIS_INP_PATH)
    irrad = IrradiationFile.from_text(IRRAD_PATH)
    react = ReactionFile.from_text(REACT_PATH)

    lm = LibManager(XSDIR_FILE, activationfile=ACTIVATION_FILE)

    def test_translate(self):
        # This test needs to be improved
        newinp = deepcopy(self.inp)
        lib = '31c-00c'
        newinp.translate(lib, self.lm, original_irradfile=self.irrad,
                         original_reacfile=self.react)
        assert True

    def test_add_PKMT_card(self):
        newinp = D1S_Input.from_text(DIS_NOPKMT_PATH)
        parentlist = ['1001', '8016']
        newinp.add_PIKMT_card(parentlist)
        card = newinp.get_card_byID('settings', 'PIKMT')
        assert card.lines[1] == '         1001    0\n'
        assert card.lines[2] == '         8016    0\n'

    def test_get_reaction_file(self):
        newinp = D1S_Input.from_text(DIS_GETREACT_PATH)
        lib = '99c'
        reacfile = newinp.get_reaction_file(self.lm, lib)
        parents = ['13027', '22046', '24050']
        for reaction, test in zip(reacfile.reactions, parents):
            assert reaction.parent == test+'.'+lib

    def test_add_track_contribution(self):
        zaids = ['1001', '1002']
        tallyID = 'F124:p'

        # --- Test parents---
        inp = deepcopy(self.inp)
        res = inp.add_track_contribution(tallyID, zaids, who='parent')
        assert res
        # dump and reread the input
        tmpfile = 'tmp.i'
        inp.write(tmpfile)
        newinp = D1S_Input.from_text(tmpfile)
        # Remove tmp file
        os.remove(tmpfile)
        # get the new injected card
        card = newinp.get_card_byID('settings', 'FU124')
        assert card.lines[0] == 'FU124 0 -1001 -1002\n'

        # --- Test daughter---
        inp = deepcopy(self.inp)
        res = inp.add_track_contribution(tallyID, zaids, who='daughter')
        assert res
        # dump and reread the input
        tmpfile = 'tmp.i'
        inp.write(tmpfile)
        newinp = D1S_Input.from_text(tmpfile)
        # Remove tmp file
        os.remove(tmpfile)
        # get the new injected card
        card = newinp.get_card_byID('settings', 'FU124')
        assert card.lines[0] == 'FU124 0 1001 1002\n'
