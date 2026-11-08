from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import pytest

import tests.dummy_structure as dummy_struct
from jade.config.status import CodeLibRunStatus, GlobalStatus
from jade.helper.constants import CODE
from jade.helper.errors import VersionInconsistencyError
from tests.config import resources

DUMMY_STRUCT = files(dummy_struct)
DUMMY_SIMULATIONS = DUMMY_STRUCT.joinpath("simulations")
DUMMY_RAW_RESULTS = DUMMY_STRUCT.joinpath("raw_data")
CONFIG_RES = files(resources)
CONFIG_RAW = CONFIG_RES.joinpath("raw_data")
CONFIG_SIM = CONFIG_RES.joinpath("simulations")


class TestGlobalStatus:
    def test_init(self):
        status = GlobalStatus(CONFIG_SIM, CONFIG_RAW)
        assert len(status.simulations) == 3
        assert len(status.raw_data) == 2

    def test_was_simulated(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        assert status.was_simulated(CODE("mcnp"), "FENDL 3.2c", "Oktavian")
        assert not status.was_simulated(CODE("openmc"), "FENDL 3.2c", "Oktavian")
        assert not status.was_simulated(CODE("mcnp"), "FENDL 3.2c", "Sphere")
        assert not status.was_simulated(CODE("mcnp"), "FENDL 3.2c", "Dummy_continue")

    def test_get_all_raw(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, CONFIG_RAW)
        codelibs, benchmarks = status.get_all_raw()
        assert len(codelibs) == 1
        assert len(benchmarks) == 2

    def test_get_codelibs_from_raw_benchmark(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        codelibs = status.get_codelibs_from_raw_benchmark("Oktavian")
        assert len(codelibs) == 3

    def test_get_benchmark_from_raw_codelib(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, CONFIG_RAW)
        benchmarks = status.get_benchmark_from_raw_codelib("_mcnp_-_FENDL 3.2c_")
        assert len(benchmarks) == 0
        benchmarks = status.get_benchmark_from_raw_codelib("_mcnp_-_ENDFB-VIII.0_")
        assert len(benchmarks) == 2

    def test_validate_post_processing(self):
        status = GlobalStatus(DUMMY_SIMULATIONS, DUMMY_RAW_RESULTS)
        with pytest.raises(VersionInconsistencyError):
            status._validate_libs_processing(
                CODE.MCNP, "Oktavian", ["FENDL 3.2c", "ENDFB-VIII.0"]
            )
        status._validate_libs_processing(
            CODE.MCNP, "Sphere", ["FENDL 3.2c", "ENDFB-VIII.0"]
        )


def _make_raw(root: Path, codelib: str, bench: str, metadata: dict) -> None:
    folder = Path(root, codelib, bench)
    folder.mkdir(parents=True)
    with open(Path(folder, "metadata.json"), "w") as f:
        json.dump(metadata, f)


@pytest.fixture
def versioned_raw(tmp_path) -> Path:
    raw = Path(tmp_path, "raw")
    raw.mkdir()
    _make_raw(raw, "_openmc_-_FENDL 3.2c_", "Bench", {"benchmark_version": "1.0"})
    _make_raw(
        raw,
        "_openmc_-_0.9.0_-_FENDL 3.2c_",
        "Bench",
        {"benchmark_version": "1.0", "run_id": "a"},
    )
    _make_raw(
        raw,
        "_openmc_-_0.15.0_-_FENDL 3.2c_",
        "Bench",
        {"benchmark_version": "2.0", "run_id": "b"},
    )
    _make_raw(
        raw,
        "_mcnp_-_6.2_-_FENDL 3.2c_",
        "Other",
        {"benchmark_version": "1.0"},
    )
    Path(raw, "_exp_-_exp_", "Bench").mkdir(parents=True)
    sims = Path(tmp_path, "sims")
    sims.mkdir()
    return raw


class TestGlobalStatusVersions:
    def test_raw_keys_include_version(self, versioned_raw):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        assert (CODE.OPENMC, "FENDL 3.2c", "0.15.0", "Bench") in status.raw_data
        assert (CODE.OPENMC, "FENDL 3.2c", None, "Bench") in status.raw_data
        assert (CODE.EXPERIMENT, "exp", None, "Bench") in status.raw_data
        codelibs = status.get_codelibs_from_raw_benchmark("Bench")
        assert codelibs == {
            "_openmc_-_FENDL 3.2c_",
            "_openmc_-_0.9.0_-_FENDL 3.2c_",
            "_openmc_-_0.15.0_-_FENDL 3.2c_",
            "_exp_-_exp_",
        }

    def test_get_raw_versions(self, versioned_raw):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        assert status.get_raw_versions(CODE.OPENMC, "FENDL 3.2c", "Bench") == [
            None,
            "0.9.0",
            "0.15.0",
        ]
        assert status.get_raw_versions(CODE.MCNP, "FENDL 3.2c", "Bench") == []

    def test_resolve_codelib(self, versioned_raw):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        # no version -> most recent
        assert status.resolve_codelib("_openmc_-_FENDL 3.2c_", "Bench") == (
            CODE.OPENMC,
            "FENDL 3.2c",
            "0.15.0",
        )
        # explicit version
        assert status.resolve_codelib("_openmc_-_0.9.0_-_FENDL 3.2c_", "Bench") == (
            CODE.OPENMC,
            "FENDL 3.2c",
            "0.9.0",
        )
        assert status.resolve_codelib("_openmc_-_1.0.0_-_FENDL 3.2c_", "Bench") is None
        assert status.resolve_codelib("_mcnp_-_FENDL 3.2c_", "Bench") is None
        assert status.resolve_codelib("_exp_-_exp_", "Bench") == (
            CODE.EXPERIMENT,
            "exp",
            None,
        )
        assert status.is_raw_available("_mcnp_-_FENDL 3.2c_", "Other")
        assert not status.is_raw_available("_mcnp_-_6.3_-_FENDL 3.2c_", "Other")

    def test_get_benchmark_from_raw_codelib(self, versioned_raw):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        # unversioned request matches any version
        assert status.get_benchmark_from_raw_codelib("_mcnp_-_FENDL 3.2c_") == {"Other"}
        assert status.get_benchmark_from_raw_codelib(["_mcnp_-_6.2_-_FENDL 3.2c_"]) == {
            "Other"
        }
        assert (
            status.get_benchmark_from_raw_codelib("_mcnp_-_6.3_-_FENDL 3.2c_") == set()
        )

    def test_validate_codelibs_versions(self, versioned_raw):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        # same benchmark version, different code versions -> ok
        status.validate_codelibs(
            [
                ("exp", "exp", None),
                ("openmc", "FENDL 3.2c", "0.9.0"),
                ("openmc", "FENDL 3.2c", None),
            ],
            "Bench",
        )
        # benchmark major version differs between code versions
        with pytest.raises(VersionInconsistencyError):
            status.validate_codelibs(
                [
                    ("openmc", "FENDL 3.2c", "0.9.0"),
                    ("openmc", "FENDL 3.2c", "0.15.0"),
                ],
                "Bench",
            )

    @pytest.mark.parametrize(
        "run_id, expected", [("a", True), ("b", True), ("c", False), (None, True)]
    )
    def test_is_simulation_processed(self, versioned_raw, run_id, expected):
        status = GlobalStatus(versioned_raw.parent / "sims", versioned_raw)
        metadata = {} if run_id is None else {"run_id": run_id}
        status._simulations = {
            (CODE.OPENMC, "FENDL 3.2c", "Bench"): CodeLibRunStatus(
                CODE.OPENMC, "FENDL 3.2c", metadata, "", ["run"], []
            )
        }
        assert status.is_simulation_processed(CODE.OPENMC, "FENDL 3.2c", "Bench") is (
            expected
        )
        # nothing processed for this benchmark
        assert not status.is_simulation_processed(CODE.OPENMC, "FENDL 3.2c", "Other")
