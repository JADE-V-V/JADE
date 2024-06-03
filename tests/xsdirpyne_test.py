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

from f4enix.input.xsdirpyne import Xsdir

import sys
import os

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")


class TestXsdir:
    """No need to test the entire class since it is from Pyne distro.
    New functionalities or modifications will be tested instead
    """

    xsdir = Xsdir(XSDIR_FILE)

    def test_find_table(self):
        names = ["1001.31c", "20000.21c", "8016.00c"]
        for zaidname in names:
            ans = self.xsdir.find_table(zaidname, mode="exact")
            assert ans

        zaidname = "1001"
        tables = self.xsdir.find_table(zaidname, mode="default")
        assert len(tables) == 43
        assert tables[0].name == "1001.03c"

        zaidname = "1001"
        libs = self.xsdir.find_table(zaidname, mode="default-fast")
        assert len(libs) == 43
        assert libs[0] == "03c"

    def test_find_zaids(self):
        lib = "21c"
        zaids = self.xsdir.find_zaids(lib)
        print(zaids)
        assert len(zaids) == 80
