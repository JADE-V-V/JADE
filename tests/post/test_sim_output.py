from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pandas as pd
import pytest

import tests.dummy_structure as dummy_struct
from jade.helper.__openmc__ import OMC_AVAIL
from jade.post.sim_output import MCNPSimOutput, OpenMCSimOutput

SIMULATION_FOLDER = files(dummy_struct).joinpath("simulations")


@pytest.fixture
def mcnp_sim_output() -> MCNPSimOutput:
    folder = Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Oktavian", "Oktavian_Al")
    # Create dummy files for MCNP
    return MCNPSimOutput(folder)


class TestMCNPSimOutput:
    def test_mcnp_tallydata(self, mcnp_sim_output):
        assert isinstance(mcnp_sim_output.tallydata, dict)
        assert all(
            isinstance(df, pd.DataFrame) for df in mcnp_sim_output.tallydata.values()
        )
        # TODO check numerical values

    def test_mcnp_totalbin(self, mcnp_sim_output):
        assert isinstance(mcnp_sim_output.totalbin, dict)
        assert all(
            isinstance(df, pd.DataFrame) or df is None
            for df in mcnp_sim_output.totalbin.values()
        )

    def test_mcnp_tally_numbers(self, mcnp_sim_output):
        assert isinstance(mcnp_sim_output.tally_numbers, list)
        assert all(isinstance(num, int) for num in mcnp_sim_output.tally_numbers)

    def test_mcnp_tally_comments(self, mcnp_sim_output):
        assert isinstance(mcnp_sim_output.tally_comments, list)
        assert all(
            isinstance(comment, str) for comment in mcnp_sim_output.tally_comments
        )


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
class TestOpenMCSimoutput:
    pass
