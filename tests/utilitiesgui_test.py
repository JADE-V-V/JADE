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
import json
import pandas as pd
import pytest
import re

cp = os.path.dirname(os.path.abspath(__file__))
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)
sys.path.insert(1, root)

import jade.utilitiesgui as uty
from f4enix.input.libmanager import LibManager


ACTIVATION_FILE = os.path.join(cp, "TestFiles", "libmanager", "Activation libs.xlsx")
XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")


class SessionMockup:

    def __init__(self, uti_path, input_path=None):
        df_rows = [
            ["99c", "sda", "", XSDIR_FILE, XSDIR_FILE],
            ["98c", "acsdc", "", XSDIR_FILE, XSDIR_FILE],
            ["21c", "adsadsa", "", XSDIR_FILE, None],
            ["31c", "adsadas", "", XSDIR_FILE, None],
            ["00c", "sdas", "yes", XSDIR_FILE, None],
            ["71c", "sdasxcx", "", XSDIR_FILE, None],
        ]
        df_lib = pd.DataFrame(df_rows)
        df_lib.columns = ["Suffix", "Name", "Default", "MCNP", "d1S"]
        self.lib_manager = LibManager(
            df_lib, activationfile=ACTIVATION_FILE, isotopes_file=ISOTOPES_FILE
        )
        # Always use fixtures for temporary directories
        self.path_uti = uti_path
        self.conf = ConfMockup()
        if input_path is not None:
            self.path_inputs = input_path


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

    def test_print_libraries(self, session):
        """
        This is properly tested in libmanager_test
        """
        uty.print_libraries(session.lib_manager)
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
        example = os.path.join(folders_copy, "00c", "Example", "mcnp")
        oktavian = os.path.join(folders_copy, "00c", "Oktavian", "Oktavian_Cr", "mcnp")
        oktavian2 = os.path.join(folders_copy, "00c", "Oktavian", "Oktavian_Al", "mcnp")
        sphere = os.path.join(folders_copy, "00c", "Sphere", "test", "mcnp")

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
        inputs = iter(["1001", "1", "continue", "31c", "continue", "y"])
        monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
        uty.print_XS_EXFOR(session)
        assert True

        # TODO test also EXFOR if installed

    def test_add_rmode(self, tmpdir):
        pattern = re.compile(r"RMODE 0")
        src = os.path.join(cp, "TestFiles", "utilitiesgui", "benchmark_inputs")
        dest = tmpdir.join("inputs")
        session = SessionMockup(tmpdir.join("uty"), dest)
        # first copy some benchmarks there
        shutil.copytree(src, dest)
        # add the rmode keywords
        uty.add_rmode(session)
        for dirpath, dirnames, filenames in os.walk(dest):
            if len(filenames) > 0:
                file = filenames[0]
                if os.path.basename(dirpath) == "mcnp":
                    # ensure RMODE 0 is added only once
                    with open(
                        os.path.join(dirpath, file), "r", encoding="utf-8"
                    ) as infile:
                        counter = 0
                        for line in infile:
                            if pattern.match(line):
                                counter += 1
                        assert counter == 1


def excel_equal(fileA, fileB, n_sheets):
    for i in range(n_sheets):
        sheetA = pd.read_excel(fileA, sheet_name=i)
        sheetB = pd.read_excel(fileB, sheet_name=i)
        assert sheetA.equals(sheetB)


def txt_equal(fileA, fileB):
    with open(fileA, "r") as infileA, open(fileB, "r") as infileB:
        for lineA, lineB in zip(infileA, infileB):
            assert lineA == lineB
