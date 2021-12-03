"""
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

from posixpath import supports_unicode_filenames
import sys
import os

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

import utilitiesgui as uty
from libmanager import LibManager
import shutil
import pandas as pd

ACTIVATION_FILE = os.path.join(cp, 'TestFiles', 'libmanager',
                               'Activation libs.xlsx')
XSDIR_FILE = os.path.join(cp, 'TestFiles', 'libmanager', 'xsdir')
ISOTOPES_FILE = os.path.join(modules_path, 'Isotopes.txt')


class SessionMockup:

    def __init__(self):
        self.lib_manager = LibManager(XSDIR_FILE,
                                      activationfile=ACTIVATION_FILE,
                                      isotopes_file=ISOTOPES_FILE)


class TestUtilities:
    session = SessionMockup()
    inputfile = os.path.join(cp, 'TestFiles', 'utilitiesgui', 'test.i')
    outpath = os.path.join(cp, 'tmp')

    def test_translate_input(self):
        """
        the correctness of the translations is already tested in matreader_test
        """
        lib = '00c'
        ans = uty.translate_input(self.session, lib, self.inputfile,
                                  outpath=self.outpath)
        shutil.rmtree(self.outpath)
        assert ans

    def test_print_libraries(self):
        """
        This is properly tested in libmanager_test
        """
        uty.print_libraries(self.session.lib_manager)
        assert True

    def test_print_material_info(self):
        uty.print_material_info(self.session, self.inputfile,
                                outpath=self.outpath)
        testfilename = os.path.basename(self.inputfile)
        tag = 'materialinfo.xlsx'
        fileA = os.path.join(cp, 'tmp', testfilename+'_'+tag)
        fileB = os.path.join(cp, 'TestFiles', 'utilitiesgui', tag)
        excel_equal(fileA, fileB, 2)
        # shutil.rmtree(self.outpath)

    def test_generate_material(self):
        # using atom fraction
        sourcefile = self.inputfile
        materials = ['m1', 'M2']
        percentages = [0.5, 0.5]
        newlib = '31c'
        fraction_type = 'atom'
        outpath = self.outpath
        uty.generate_material(self.session, sourcefile, materials, percentages,
                              newlib, fractiontype=fraction_type,
                              outpath=outpath)
        filename = os.path.basename(self.inputfile)
        fileA = os.path.join(cp, 'TestFiles', 'utilitiesgui', 'newmat_atom')
        fileB = os.path.join(outpath, filename+'_new Material')
        txt_equal(fileA, fileB)

        # using mass fraction
        fraction_type = 'mass'
        uty.generate_material(self.session, sourcefile, materials, percentages,
                              newlib, fractiontype=fraction_type,
                              outpath=outpath)
        fileA = os.path.join(cp, 'TestFiles', 'utilitiesgui', 'newmat_mass')
        txt_equal(fileA, fileB)

        shutil.rmtree(outpath)

    def test_switch_fractions(self):

        # Switches are properly tested in matreader
        uty.switch_fractions(self.session, self.inputfile, 'mass',
                             outpath=self.outpath)
        uty.switch_fractions(self.session, self.inputfile, 'atom',
                             outpath=self.outpath)
        shutil.rmtree(self.outpath)
        assert True

    def test_change_ACElib_suffix(self, monkeypatch):
        acefolder = os.path.join(cp, 'TestFiles', 'utilitiesgui', 'ACEchange',
                                 '99c')
        newfolder = os.path.join(os.path.dirname(acefolder),
                                 '99cnew')

        responses = iter([str(acefolder), '99c', '98c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        uty.change_ACElib_suffix()
        for file in os.listdir(newfolder):
            filepath = os.path.join(newfolder, file)
            with open(filepath, 'r') as infile:
                for line in infile:
                    print(line)
                    print(line.find('.98c'))
                    if line.find('.98c') != -1:
                        assert True
                    else:
                        assert False
                    break
        shutil.rmtree(newfolder)

    def test_get_reaction_file(self, monkeypatch):
        # The correctness of the file is already tested in parserD1S
        filepath = os.path.join(cp, 'TestFiles', 'utilitiesgui', 'd1stest.i')
        responses = iter([str(filepath), '99c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        uty.get_reaction_file(self.session, outpath=self.outpath)
        shutil.rmtree(self.outpath)
        assert True

    def test_input_with_option(self, monkeypatch):
        msg = ''
        options = ['option1', 'option2']
        inputs = iter(['wrongoption', 'option1'])
        monkeypatch.setattr('builtins.input', lambda msg: next(inputs))
        valid_input = uty.input_with_options(msg, options)
        assert valid_input == 'option1'


def excel_equal(fileA, fileB, n_sheets):
    for i in range(n_sheets):
        sheetA = pd.read_excel(fileA, sheet_name=i)
        sheetB = pd.read_excel(fileB, sheet_name=i)
        assert sheetA.equals(sheetB)


def txt_equal(fileA, fileB):
    with open(fileA, 'r') as infileA, open(fileB, 'r') as infileB:
        for lineA, lineB in zip(infileA, infileB):
            assert lineA == lineB
