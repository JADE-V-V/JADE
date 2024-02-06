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

import sys
import os
import shutil

cp = os.path.dirname(os.path.abspath(__file__))
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)
sys.path.insert(1, root)

import jade.utilitiesgui as uty
from jade.libmanager import LibManager
import shutil
import pandas as pd
import pytest

ACTIVATION_FILE = os.path.join(cp, "TestFiles", "libmanager", "Activation libs.xlsx")
XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")


class SessionMockup:

    def __init__(self, uti_path):
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
        self.lib_manager = LibManager(
            df_lib, activationfile=ACTIVATION_FILE, isotopes_file=ISOTOPES_FILE
        )
        # Always use fixtures for temporary directories
        self.path_uti = uti_path
        self.conf = ConfMockup()


class ConfMockup:

    def __init__(self):
        self.lib = pd.DataFrame(
            [["00c", "A"], ["31c", "B"]], columns=["Suffix", "name"]
        ).set_index("Suffix")


class TestUtilities:

    @pytest.fixture
    def session(self, tmpdir):
        return SessionMockup(tmpdir)

    @pytest.fixture
    def inputfile(self):
        return os.path.join(cp, "TestFiles", "utilitiesgui", "test.i")

    def test_translate_input(self, session, inputfile, tmpdir):
        """
        the correctness of the translations is already tested in matreader_test
        """
        lib = "00c"
        ans = uty.translate_input(
            session, lib, inputfile, outpath=tmpdir.mkdir("Translate")
        )
        assert ans

    def test_print_libraries(self, session):
        """
        This is properly tested in libmanager_test
        """
        uty.print_libraries(session.lib_manager)
        assert True

    def test_print_material_info(self, session, inputfile, tmpdir):
        outpath = tmpdir.mkdir("MaterialInfo")
        uty.print_material_info(session, inputfile, outpath=outpath)
        testfilename = os.path.basename(inputfile)
        tag = "materialinfo.xlsx"
        fileA = os.path.join(outpath, testfilename + "_" + tag)
        fileB = os.path.join(cp, "TestFiles", "utilitiesgui", tag)

        # --- Do some consistency check on the results ---
        # Check on total fraction of materials to be 1
        elem_df = pd.read_excel(fileA, sheet_name="Sheet2").ffill()
        tot_frac = elem_df.groupby("Material").sum()["Material Fraction"]
        print(tot_frac)
        assert (tot_frac == 1).all()

        # Check for equivalence with an expected output
        excel_equal(fileA, fileB, 2)
        shutil.rmtree(outpath)

    def test_generate_material(self, inputfile, session, tmpdir):
        # using atom fraction
        sourcefile = inputfile
        materials = ["m1", "M2"]
        percentages = [0.5, 0.5]
        newlib = "31c"
        fraction_type = "atom"
        outpath = tmpdir.mkdir("GenerateMaterial")
        uty.generate_material(
            session,
            sourcefile,
            materials,
            percentages,
            newlib,
            fractiontype=fraction_type,
            outpath=outpath,
        )
        filename = os.path.basename(inputfile)
        fileA = os.path.join(cp, "TestFiles", "utilitiesgui", "newmat_atom")
        fileB = os.path.join(outpath, filename + "_new Material")
        txt_equal(fileA, fileB)

        # using mass fraction
        fraction_type = "mass"
        uty.generate_material(
            session,
            sourcefile,
            materials,
            percentages,
            newlib,
            fractiontype=fraction_type,
            outpath=outpath,
        )
        fileA = os.path.join(cp, "TestFiles", "utilitiesgui", "newmat_mass")
        txt_equal(fileA, fileB)

    def test_switch_fractions(self, session, inputfile, tmpdir):

        # Switches are properly tested in matreader
        uty.switch_fractions(session, inputfile, "mass", outpath=tmpdir)
        uty.switch_fractions(session, inputfile, "atom", outpath=tmpdir)

        assert True

    def test_change_ACElib_suffix(self, monkeypatch, tmpdir):
        acefolder = os.path.join(cp, "TestFiles", "utilitiesgui", "ACEchange", "99c")
        newacefolder = os.path.join(tmpdir.mkdir("ACE"), "99c")
        shutil.copytree(acefolder, newacefolder)
        newfolder = os.path.join(tmpdir, "ACE", "99cnew")

        responses = iter([str(newacefolder), "99c", "98c"])
        monkeypatch.setattr("builtins.input", lambda msg: next(responses))
        uty.change_ACElib_suffix()
        for file in os.listdir(newfolder):
            filepath = os.path.join(newfolder, file)
            with open(filepath, "r") as infile:
                for line in infile:
                    print(line)
                    print(line.find(".98c"))
                    if line.find(".98c") != -1:
                        assert True
                    else:
                        assert False
                    break

    def test_get_reaction_file(self, monkeypatch, session, tmpdir):
        # The correctness of the file is already tested in parserD1S
        filepath = os.path.join(cp, "TestFiles", "utilitiesgui", "d1stest.i")
        responses = iter([str(filepath), "99c"])
        monkeypatch.setattr("builtins.input", lambda msg: next(responses))
        uty.get_reaction_file(session, outpath=tmpdir.mkdir("Reaction"))
        assert True

    def test_input_with_option(self, monkeypatch):
        msg = ""
        options = ["option1", "option2"]
        inputs = iter(["wrongoption", "option1"])
        monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
        valid_input = uty.input_with_options(msg, options)
        assert valid_input == "option1"

    def test_clean_runtpe(self, tmpdir):
        folders = os.path.join(cp, "TestFiles", "utilitiesgui", "rmv_runtpe")
        folders_copy = os.path.join(tmpdir.mkdir("clear"), "rmv_runtpe_tmp")
        # Copy the folders
        shutil.copytree(folders, folders_copy)

        uty.clean_runtpe(folders_copy)
        # Check files have been removed
        example = os.path.join(folders_copy, "00c", "Example")
        oktavian = os.path.join(folders_copy, "00c", "Oktavian", "Oktavian_Cr")
        oktavian2 = os.path.join(folders_copy, "00c", "Oktavian", "Oktavian_Al")
        sphere = os.path.join(folders_copy, "00c", "Sphere", "test")

        assert len(os.listdir(example)) == 1
        assert len(os.listdir(oktavian)) == 3
        assert len(os.listdir(oktavian2)) == 3  # No deletion
        assert len(os.listdir(sphere)) == 3
        assert os.path.exists(os.path.join(example, "testtestr"))

    def test_print_XS_EXFOR(self, session, monkeypatch):
        """
        the correctness of the translations is already tested in matreader_test
        """
        msg = ""
        inputs = iter(["1001", "1", "continue", "31c", "continue", "n"])
        monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
        uty.print_XS_EXFOR(session)
        assert True

        # TODO test also EXFOR if installed


def excel_equal(fileA, fileB, n_sheets):
    for i in range(n_sheets):
        sheetA = pd.read_excel(fileA, sheet_name=i)
        sheetB = pd.read_excel(fileB, sheet_name=i)
        assert sheetA.equals(sheetB)


def txt_equal(fileA, fileB):
    with open(fileA, "r") as infileA, open(fileB, "r") as infileB:
        for lineA, lineB in zip(infileA, infileB):
            assert lineA == lineB
