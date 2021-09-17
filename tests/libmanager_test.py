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

sys.path.insert(1, '../')
from libmanager import LibManager


ACTIVATION_FILE = os.path.join('TestFiles', 'libmanager',
                               'Activation libs.xlsx')
XSDIR_FILE = os.path.join('TestFiles', 'libmanager', 'xsdir')


class TestLibManger:

    lm = LibManager(XSDIR_FILE, activationfile=ACTIVATION_FILE)

    def test_reactionfilereading(self):
        assert len(self.lm.reactions['99c']) == 102
        assert len(self.lm.reactions['98c']) == 42

    def test_get_reactions1(self):
        """
        Test ability to recover reactions for parent zaid (one)
        """
        parent = '9019'
        reaction = self.lm.get_reactions('99c', parent)[0]
        assert reaction[0] == '16'
        assert reaction[1] == '9018'

    def test_get_reactions2(self):
        """
        Test ability to recover reactions for parent zaid (multiple)
        """
        parent = '11023'
        reactions = self.lm.get_reactions('99c', parent)
        print(reactions)
        reaction1 = reactions[0]
        reaction2 = reactions[1]

        assert reaction1[0] == '16'
        assert reaction1[1] == '11022'
        assert reaction2[0] == '(102 402)'
        assert reaction2[1] == '11024'

    def test_formula_conversion(self):
        """
        Test the abilty to switch between isotopes formulas and zaid number
        """
        tests = ['N15', 'Er164', 'Kr83']
        finals = ['N-15', 'Er-164', 'Kr-83']
        for test, final in zip(tests, finals):
            conversion = self.lm.get_zaidnum(test)
            name, formula = self.lm.get_zaidname(conversion)

            assert final == formula
