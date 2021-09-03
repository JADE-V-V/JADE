# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 10:20:08 2021

@author: d.laghi

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
sys.path.insert(1, '../')
from matreader import (Zaid, MatCardsList)


class TestZaid:

    def test_fromstring(self):
        """
        Test the creation of zaids from strings

        Returns
        -------
        None.

        """
        tests = [{'str': '1001.31c   -2.3', 'res': [-2.3, '1', '001', '31c']},
                 {'str': '1001.31c\t-2.3', 'res': [-2.3, '1', '001', '31c']},
                 {'str': '15205 1', 'res': [1, '15', '205', None]}]

        for test in tests:
            text = test['str']
            zaid = Zaid.from_string(text)
            res = test['res']
            assert zaid.fraction == res[0]
            assert zaid.element == res[1]
            assert zaid.isotope == res[2]
            assert zaid.library == res[3]


class TestMatCardList:

    def test_frominput(self):
        """
        Test basic properties

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input('mat_test.i')

        assert len(matcard.materials) == 3
        assert len(matcard.matdic) == 3

    def test_headers(self):
        """
        test correct material headers reading

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input('mat_test.i')

        headers = {'m1': 'C Header M1\n', 'm2': 'C Header M2\n', 'm102': ''}
        for key, header in headers.items():
            assert matcard[key].header == header

    def test_subheaders(self):
        """
        Test correct reading of submaterial headers

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input('mat_test.i')

        headers = {'m1': ['C M1-submat1', 'C M1-Submat 2'],
                   'm2': ['', 'C M2-submat1\nC second line'],
                   'm102': ['']}

        for key, subheaders in headers.items():
            for i, submat in enumerate(matcard[key].submaterials):
                assert submat.header == subheaders[i]

    def test_zaidnumbers(self):
        """
        Test correct number of zaids allocated in submaterials

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input('mat_test.i')

        zaids = {'m1': [2, 1],
                 'm2': [1, 1],
                 'm102': [5]}

        for key, zaids in zaids.items():
            for i, submat in enumerate(matcard[key].submaterials):
                assert len(submat.zaidList) == zaids[i]
