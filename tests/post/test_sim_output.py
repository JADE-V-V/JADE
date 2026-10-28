from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pandas as pd
import pytest

import tests.dummy_structure as dummy_struct
from jade.helper.__optionals__ import OMC_AVAIL, SERPENT_AVAIL
from jade.post.sim_output import (
    MCNPSimOutput,
    OpenMCSimOutput,
    OpenMCSphereSimOutput,
    SerpentSimOutput,
)
from tests.post.resources import serpent as serpent_res

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

@pytest.fixture
def openmc_sphere_sim_output() -> OpenMCSphereSimOutput:
    folder = Path(SIMULATION_FOLDER, "_openmc_-_FENDL 3.2b_", "Sphere", "Sphere_m101")
    # Create dummy files for OpenMC Sphere
    return OpenMCSphereSimOutput(folder)

@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
class TestOpenMCSimoutput:
    pass

@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
class TestOpenMCSphereSimOutput:
    def test_openmc_sphere_tallydata(self, openmc_sphere_sim_output):
        assert isinstance(openmc_sphere_sim_output.tallydata, dict)
        assert all(
            isinstance(df, pd.DataFrame) for df in openmc_sphere_sim_output.tallydata.values()
        )

    def test_atomic_density(self, openmc_sphere_sim_output):
        assert isinstance(openmc_sphere_sim_output.atomic_density, float)
        assert openmc_sphere_sim_output.atomic_density == pytest.approx(0.042305713026896896)


SERPENT_FOLDER = files(serpent_res).joinpath("Sphere_1001_H-1")


@pytest.mark.skipif(not SERPENT_AVAIL, reason="serpentTools not available")
class TestSerpentSimOutput:
    @pytest.fixture
    def serpent_sim_output(self) -> SerpentSimOutput:
        return SerpentSimOutput(SERPENT_FOLDER)

    def test_tally_numbers(self, serpent_sim_output):
        # non integer detectors are skipped
        assert serpent_sim_output.tally_numbers == [4, 14, 24]
        assert serpent_sim_output.tally_comments == ["det 4", "det 14", "det 24"]
        assert serpent_sim_output.totalbin == {4: None, 14: None, 24: None}

    def test_code_version(self, serpent_sim_output):
        assert serpent_sim_output.code_version == "Serpent 2.2.1"

    def test_tallydata(self, serpent_sim_output):
        df = serpent_sim_output.tallydata[14]
        assert list(df.columns) == ["Energy", "Value", "Error"]
        assert len(df) == 24
        # upper boundaries of the energy bins
        assert df["Energy"].iloc[0] == pytest.approx(0.01)
        assert df["Energy"].iloc[-1] == pytest.approx(20)

        df = serpent_sim_output.tallydata[24]
        assert list(df.columns) == ["Cells", "Energy", "Value", "Error"]
        # cell names from the input
        assert set(df["Cells"]) == {2, 3}
        assert len(df) == 48

        assert len(serpent_sim_output.tallydata[4]) == 175

    def test_missing_files(self, tmpdir):
        with pytest.raises(FileNotFoundError):
            SerpentSimOutput(tmpdir)

    def test_no_detectors(self, tmpdir):
        for file in ["Sphere_1001_H-1.i", "Sphere_1001_H-1.i_res.m"]:
            tmpdir.join(file).write(SERPENT_FOLDER.joinpath(file).read_text())
        output = SerpentSimOutput(tmpdir)
        assert output.tallydata == {}
        assert output.code_version == "Serpent 2.2.1"

    def test_is_successfully_simulated(self):
        assert SerpentSimOutput.is_successfully_simulated(["a.i", "a.i_res.m"])
        assert not SerpentSimOutput.is_successfully_simulated(["a.i", "a.i_det0.m"])
