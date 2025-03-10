from __future__ import annotations

from importlib.resources import files

import pytest

from jade.helper.__openmc__ import OMC_AVAIL
from tests.post.resources import openmc as resources

if OMC_AVAIL:
    import jade.helper.openmc as omc


STATEPOINT = files(resources).joinpath("statepoint.10.h5")
TALLY_FACTORS = files(resources).joinpath("tally_factors.yaml")
CELL_VOLUMES = files(resources).joinpath("volumes.json")


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
        assert "photon" == tallies[56]["particle"][5]
        assert 11 == tallies[56]["cell"][2]
        assert 5.388881950654537e-06 == pytest.approx(tallies[24]["mean"][5])
        assert 4.331494120455328e-08 == pytest.approx(tallies[24]["std. dev."][5])
        # TODO update these numerical tests with correct values
        #     after volumes.json and stetepoint10.h5 are updated
        # assert 0.17727477233532538 == pytest.approx(tallies[56]['mean'][5])
        # assert 0.0015627129050264142 == pytest.approx(tallies[56]['std. dev.'][5])
