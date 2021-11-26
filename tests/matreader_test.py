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
import os

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from matreader import (Element, Zaid, MatCardsList)
from libmanager import LibManager


# Files
INP = os.path.join(cp, 'TestFiles', 'matreader', 'mat_test.i')
INP2 = os.path.join(cp, 'TestFiles', 'matreader', 'mat_test2.i')
ACTIVATION_INP = os.path.join(cp, 'TestFiles', 'matreader', 'activation.i')
XSDIR = os.path.join(cp, 'TestFiles', 'matreader', 'xsdir_mcnp6.2')
ISOTOPES_FILE = os.path.join(modules_path, 'Isotopes.txt')
# Other
LIBMAN = LibManager(XSDIR, defaultlib='81c', isotopes_file=ISOTOPES_FILE)


class TestZaid:

    tests = [{'str': '1001.31c   -2.3', 'res': [-2.3, '1', '001', '31c']},
             {'str': '1001.31c\t-2.3', 'res': [-2.3, '1', '001', '31c']},
             {'str': '15205 1', 'res': [1, '15', '205', None]}]

    def test_fromstring(self):
        """
        Test the creation of zaids from strings

        Returns
        -------
        None.

        """

        for test in self.tests:
            text = test['str']
            zaid = Zaid.from_string(text)
            res = test['res']
            assert zaid.fraction == res[0]
            assert zaid.element == res[1]
            assert zaid.isotope == res[2]
            assert zaid.library == res[3]


class TestElement:
    zaid_strings = ['1001.31c   -1', '1002.31c   -3']

    def _buildElem(self):
        zaids = []
        for zaidstr in self.zaid_strings:
            zaids.append(Zaid.from_string(zaidstr))

        elem = Element(zaids)
        return elem

    def test_update_zaidinfo(self):
        """
        Test ability to get additional info for the zaids
        """

        elem = self._buildElem()

        # Check for the correct element
        elem.Z = '1'

        # Check the correct update of infos in element
        elem.update_zaidinfo(LIBMAN)
        res = [{'fullname': 'H-1', 'ab': 25},
               {'fullname': 'H-2', 'ab': 75}]
        for zaid, checks in zip(elem.zaids, res):
            assert int(zaid.ab) == checks['ab']
            assert zaid.fullname == checks['fullname']

    def test_get_fraction(self):
        """
        Test correct recovery of element fraction
        """

        elem = self._buildElem()
        assert elem.get_fraction() == -4


class Testmaterial:
    def test_switch_fraction(self):
        # Read a material
        matcard = MatCardsList.from_input(INP)
        # Fake translation in order to normalize the fractions
        material = matcard[0]
        material.update_info(LIBMAN)
        original = material.to_text()

        # -- Switch back and forth --
        # this first one should do nothing
        material.switch_fraction('atom', LIBMAN)
        unchanged = material.to_text()
        assert original == unchanged
        # switch to mass
        material.switch_fraction('mass', LIBMAN)
        mass = material.to_text()
        # change again, should do nothing
        material.switch_fraction('mass', LIBMAN)
        unchanged = material.to_text()
        assert unchanged == mass
        # go back to atom
        material.switch_fraction('atom', LIBMAN)
        atom = material.to_text()
        # at last check that the inplace oprion works
        material.switch_fraction('mass', LIBMAN, inplace=False)
        inplace = material.to_text()
        assert inplace == atom
        # go back to mass
        material.switch_fraction('mass', LIBMAN)
        massnorm = material.to_text()
        assert massnorm == mass


class TestMatCardList:

    def test_frominput(self):
        """
        Test basic properties

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input(INP)

        assert len(matcard.materials) == 3
        assert len(matcard.matdic) == 3

    def test_headers(self):
        """
        test correct material headers reading

        Returns
        -------
        None.

        """
        matcard = MatCardsList.from_input(INP)

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
        matcard = MatCardsList.from_input(INP)

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
        matcard = MatCardsList.from_input(INP)

        zaids = {'m1': [2, 1],
                 'm2': [1, 1],
                 'm102': [5]}

        for key, zaids in zaids.items():
            for i, submat in enumerate(matcard[key].submaterials):
                assert len(submat.zaidList) == zaids[i]

    def test_translation(self):
        """
        Test that translation works (all possile modes)
        """
        # Dic mode 1
        newlib = {'21c': '31c', '99c': '81c'}
        matcard = MatCardsList.from_input(ACTIVATION_INP)
        matcard.translate(newlib, LIBMAN)
        translation = matcard.to_text()
        assert translation.count('31c') == 3
        assert translation.count('81c') == 3

        # dic mode 2 - test 1
        matcard = MatCardsList.from_input(ACTIVATION_INP)
        newlib = {'99c': ['1001'], '21c': ['28061', '28062', '28064', '29063',
                                           '5010']}
        matcard.translate(newlib, LIBMAN)
        translation = matcard.to_text()
        assert translation.count('99c') == 0
        assert translation.count('21c') == 5
        assert translation.count('81c') == 1

        # dic mode 2 - test 2
        matcard = MatCardsList.from_input(ACTIVATION_INP)
        newlib = {'99c': ['1001'], '21c': ['28061', '28062', '28064', '29063']}
        try:
            matcard.translate(newlib, LIBMAN)
            assert False
        except ValueError:
            assert True

        # classic mode
        matcard = MatCardsList.from_input(INP2)
        matcard.translate('21c', LIBMAN)
        translation = matcard.to_text()
        assert translation.count('21c') == 10

    def test_get_info(self):
        """
        Barely tests that everything is created
        """
        matcard = MatCardsList.from_input(INP)
        df, df_elem = matcard.get_info(LIBMAN, zaids=True, complete=True)
        assert len(df) == 8
        assert len(df_elem) == 7
