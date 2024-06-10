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

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from f4enix.output.meshtal import Meshtal

MSHTAL_FILE = os.path.join(cp, "TestFiles", "meshtal", "test_msht")


class TestMeshtal:
    meshtal = Meshtal(MSHTAL_FILE)

    def test_extract_1D(self):
        fmesh = self.meshtal.fmeshes["244"]
        assert fmesh.tallynum == "244"
        assert fmesh.description == "Photon Flux [#/cc/n_s]"

        fmeshes1D = self.meshtal.extract_1D()
        assert len(fmeshes1D) == 5
        fmesh1D = fmeshes1D["234"]
        assert fmesh1D["desc"] == "Neutron Flux [#/cc/n_s]"
        assert fmesh1D["num"] == "234"
        assert fmesh1D["data"].shape == (79, 3)
        assert list(fmesh1D["data"].columns) == ["Cor A", "Value", "Error"]
