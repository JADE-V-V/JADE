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

import os
import sys
import pytest
from jade.configuration import Configuration, Log

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

resources = os.path.join(cp, "TestFiles", "configuration")
MAIN_CONFIG_FILE = os.path.join(resources, "mainconfig.xlsx")


@pytest.fixture
def config():
    configob = Configuration(MAIN_CONFIG_FILE)
    return configob


@pytest.fixture
def log(tmpdir):
    file = os.path.join(tmpdir, "tmplog.txt")
    logob = Log(file)
    return logob


class TestConfiguration:

    def test_read(self, config):
        # TODO
        # Check that everything is read in a correct way
        assert config.mpi_tasks == 4

    def test_get_lib_name(self, config):
        suffix_list = ["21c", "33c", "pincopalle"]
        expected_list = ["FENDL 2.1c", "33c", "pincopalle"]
        for suffix, expected in zip(suffix_list, expected_list):
            assert config.get_lib_name(suffix) == expected


class TestLog:
    # Here it is tested that the class just works without prompting errors
    # In depth test makes no sense because the class should be substitued
    # with the pre-built python log module.

    def test_bar_adjourn(self, log):
        txt = "assdad"
        log.bar_adjourn(txt)
        log.bar_adjourn(txt, spacing=True)

        txt = "asdadasdadasdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        log.bar_adjourn(txt)

        txt = "asa"
        log.bar_adjourn(txt)

        assert True

    def test_adjourn(self, log):
        txt = "adsdadasdadasd"
        log.adjourn(txt, spacing=True, time=True)
        assert True
