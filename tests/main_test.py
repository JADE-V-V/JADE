"""

@author: Jade Development Team

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
import logging

from jade.main import Session
from jade.configuration import Configuration

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

resources = os.path.join(cp, "TestFiles", "main")
MAIN_CONFIG_FILE = os.path.join(resources, "mainconfig.xlsx")


# I don't want to deal with testing the Session object itself for the moment
class MockUpSession(Session):
    def __init__(self):
        self.conf = Configuration(MAIN_CONFIG_FILE)


class TestSession:
    @pytest.mark.parametrize(
        ["action", "expected"],
        [
            (
                "Run",
                {"mcnp": ["Oktavian"], "openmc": ["FNG"], "serpent": ["FNG"]},
            ),
            (
                "Post-Processing",
                {"mcnp": ["Oktavian"], "openmc": ["FNG"], "serpent": ["FNG"]},
            ),
        ],
    )
    def test_check_active_tests(self, action, expected):
        session = MockUpSession()
        active_tests = session.check_active_tests(action, exp=True)
        assert active_tests == expected

    def test_initialize_log(self, tmpdir):
        session = MockUpSession()
        logfile = os.path.join(tmpdir, "log.txt")
        session._initialize_log(logfile)
        assert os.path.exists(logfile)
        assert os.stat(logfile).st_size > 0
        logging.warning("This is a test")
        with open(logfile, "r", encoding="utf-8") as f:
            assert "This is a test" in f.read()
