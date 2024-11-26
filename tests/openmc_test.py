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
TALLY_FACTORS = os.path.join(cp, 'TestFiles', 'openmc', 'tally_factors.yaml')
CELL_VOLUMES = os.path.join(cp, 'TestFiles', 'openmc', 'volumes.json')

class TestOpenMCTallyFactors:
    
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_from_yaml(self):
        omc_tally_factors = omc.OpenMCTallyFactors.from_yaml(TALLY_FACTORS)
        assert omc_tally_factors.tally_factors[24].volume == True
        assert omc_tally_factors.tally_factors[56].mass == True
        assert omc_tally_factors.tally_factors[114].identifier == 114

class TestOpenMCCellVolumes:
    
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_from_json(self):
        omc_cell_volumes = omc.OpenMCCellVolumes.from_json(CELL_VOLUMES)
        assert omc_cell_volumes.cell_volumes[84] == 396061.0
        assert omc_cell_volumes.cell_volumes[106] == 225997.0
        assert omc_cell_volumes.cell_volumes[73] == 758884.0


class TestOpenMCStatePoint:

    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_tallies_to_dataframes(self):
        out = omc.OpenMCStatePoint(STATEPOINT, TALLY_FACTORS, CELL_VOLUMES)
        tallies = out.tallies_to_dataframes()
        assert 'photon' == tallies[56]['particle'][5]
        assert 11 == tallies[56]['cell'][2]
        assert 5.388881950654537e-06 == pytest.approx(tallies[24]['mean'][5])
        assert 4.331494120455328e-08 == pytest.approx(tallies[24]['std. dev.'][5])
        #TODO update these numerical tests with correct values
        #     after volumes.json and stetepoint10.h5 are updated 
        #assert 0.17727477233532538 == pytest.approx(tallies[56]['mean'][5])
        #assert 0.0015627129050264142 == pytest.approx(tallies[56]['std. dev.'][5])
