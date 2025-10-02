from __future__ import annotations

from importlib.resources import files

import pytest, os

from jade.helper.__optionals__ import OMC_AVAIL
from tests.post.resources import openmc as resources

if OMC_AVAIL:
    import jade.helper.openmc as omc


STATEPOINT = files(resources).joinpath("statepoint.10.h5")
CELL_VOLUMES = files(resources).joinpath("volumes.json")
XML_PATH = os.path.dirname(STATEPOINT)


class TestOpenMCCellData:
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_from_files(self):
        omc_cell_data = omc.OpenMCCellData.from_files(CELL_VOLUMES, XML_PATH)
        assert omc_cell_data.cell_volumes[84] == 396061.0
        assert omc_cell_data.cell_volumes[106] == 225997.0
        assert omc_cell_data.cell_volumes[73] == 758884.0
        assert omc_cell_data.cell_masses[84] == pytest.approx(2864154.7276)
        assert omc_cell_data.cell_masses[106] == pytest.approx(1634319.9052)
        assert omc_cell_data.cell_masses[73] == pytest.approx(5487945.534399999)


class TestOpenMCStatePoint:
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_tallies_to_dataframes(self):
        out = omc.OpenMCStatePoint(STATEPOINT, CELL_VOLUMES)
        tallies = out.tallies_to_dataframes()
        assert "photon" == tallies[56]["particle"][5]
        assert 11 == tallies[56]["cell"][2]
        assert 5.388881950654537e-06 == pytest.approx(
            tallies[24]["mean"][5] / out.cell_data.cell_volumes[tallies[24]["cell"][5]]
        )
        assert 4.331494120455328e-08 == pytest.approx(
            tallies[24]["std. dev."][5]
            / out.cell_data.cell_volumes[tallies[24]["cell"][5]]
        )
