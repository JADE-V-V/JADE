from __future__ import annotations

from importlib.resources import files

import tests.dummy_structure as dummy_struct
from jade.config.status import GlobalStatus
from jade.helper.constants import CODE

DUMMY_STRUCT = files(dummy_struct)
DUMMY_SIMULATIONS = DUMMY_STRUCT.joinpath("simulations")
DUMMY_RAW_RESULTS = DUMMY_STRUCT.joinpath("raw_data")


class TestGlobalStatus:
    def test_init(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        assert len(status.simulations) == 2
        assert len(status.raw_data) == 5

    def test_was_simulated(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        assert status.was_simulated(CODE("mcnp"), "FENDL 3.2c", "Oktavian")
        assert not status.was_simulated(CODE("openmc"), "FENDL 3.2c", "Oktavian")
        assert not status.was_simulated(CODE("mcnp"), "FENDL 3.2c", "Sphere")

    def test_get_all_raw(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        codelibs, benchmarks = status.get_all_raw()
        assert len(codelibs) == 3
        assert len(benchmarks) == 2

    def test_get_codelibs_from_raw_benchmark(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        codelibs = status.get_codelibs_from_raw_benchmark("Oktavian")
        assert len(codelibs) == 3

    def test_get_benchmark_from_raw_codelib(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        benchmarks = status.get_benchmark_from_raw_codelib("_mcnp_-_FENDL 3.2c_")
        assert len(benchmarks) == 2
