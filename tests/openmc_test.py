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
import pytest

from jade.__openmc__ import OMC_AVAIL
if OMC_AVAIL:
    import jade.openmc as omc

cp = os.path.dirname(os.path.abspath(__file__))
STATEPOINT = os.path.join(cp, 'TestFiles', 'openmc', 'statepoint.10.h5')

class TestOpenMCStatePoint:

    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_tallies_to_dataframes(self):
        out = omc.OpenMCStatePoint(STATEPOINT)
        tallies = out.tallies_to_dataframes()
        assert True