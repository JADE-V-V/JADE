from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

import pytest

import jade.resources as res
import tests.dummy_structure as dummy_struct
from jade.config.run_config import (
    BenchmarkRunConfig,
    EnvironmentVariables,
    LibraryD1S,
    LibraryMCNP,
    RunMode,
)
from jade.helper.__openmc__ import OMC_AVAIL
from jade.helper.constants import CODE
from jade.run.benchmark import BenchmarkRun, SphereBenchmarkRun, SphereSDDRBenchmarkRun

DEFAULT_CFG = files(res).joinpath("default_cfg")
BENCHMARKS_ROOT = files(dummy_struct).joinpath("benchmark_templates")


class TestBenchmarkRun:
    def test_run_mcnp(self, tmpdir):
        perform = [
            (CODE.MCNP, LibraryMCNP(name="FENDL 3.2c", path=None, suffix="31c")),
            (CODE.MCNP, LibraryMCNP(name="ENDF VII-1", path=None, suffix="00c")),
        ]
        cfg = BenchmarkRunConfig(
            description="Oktavian TOF",
            name="Oktavian",
            run=perform,
            nps=10,
            only_input=True,
        )

        env_vars = EnvironmentVariables(
            10,
            10,
            {CODE.MCNP: "mcnp6.2"},
            run_mode=RunMode.JOB_SUMISSION,
            code_configurations={CODE.MCNP: Path(DEFAULT_CFG, "mcnp/mcnp.cfg")},
            batch_template=DEFAULT_CFG.joinpath("batch_templates/Slurmtemplate.sh"),
            batch_system="slurm",
            mpi_prefix="srun",
        )

        benchmark = BenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        assert len(os.listdir(tmpdir)) == 2
        assert (
            len(os.listdir(Path(tmpdir, "_mcnp_-_FENDL 3.2c_/Oktavian/Oktavian_Al")))
            == 3
        )

    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
    def test_run_openmc(self, tmpdir):
        pass


class TestSphereBenchmarkRun:
    def test_run_mcnp(self, tmpdir):
        perform = [
            (CODE.MCNP, LibraryMCNP(name="FENDL 3.2c", path=None, suffix="31c")),
            (CODE.MCNP, LibraryMCNP(name="ENDF VII-1", path=None, suffix="00c")),
        ]
        cfg = BenchmarkRunConfig(
            description="Sphere benchmark",
            name="Sphere",
            run=perform,
            nps=10,
            only_input=True,
            custom_inp=2,
            additional_settings_path=DEFAULT_CFG.joinpath("benchmarks/Sphere"),
        )

        env_vars = EnvironmentVariables(
            None,
            0,
            {CODE.MCNP: "mcnp6.2"},
            run_mode=RunMode.SERIAL,
        )

        benchmark = SphereBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        assert len(os.listdir(tmpdir)) == 2
        assert len(os.listdir(Path(tmpdir, "_mcnp_-_FENDL 3.2c_/Sphere"))) == 4
        assert (
            len(os.listdir(Path(tmpdir, "_mcnp_-_FENDL 3.2c_/Sphere/Sphere_1001_H-1")))
            == 2
        )


class TestSphereSDDRBenchmarkRun:
    def test_run_mcnp(self, tmpdir):
        perform = [
            (
                CODE.D1S,
                LibraryD1S(
                    name="lib1",
                    path=None,
                    suffix="99c",
                    transport_suffix="31c",
                    transport_library_path=None,
                ),
            ),
            (
                CODE.D1S,
                LibraryD1S(
                    name="lib2",
                    path=None,
                    suffix="98c",
                    transport_library_path=None,
                    transport_suffix="31c",
                ),
            ),
        ]
        cfg = BenchmarkRunConfig(
            description="Sphere benchmark",
            name="SphereSDDR",
            run=perform,
            nps=10,
            only_input=True,
            custom_inp=2,
            additional_settings_path=DEFAULT_CFG.joinpath("benchmarks/SphereSDDR"),
        )

        env_vars = EnvironmentVariables(
            0,
            None,
            {CODE.D1S: "d1suned"},
            run_mode=RunMode.SERIAL,
        )

        benchmark = SphereSDDRBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        assert len(os.listdir(tmpdir)) == 2
        assert len(os.listdir(Path(tmpdir, "_d1s_-_lib1_/SphereSDDR"))) == 4
        assert len(os.listdir(Path(tmpdir, "_d1s_-_lib2_/SphereSDDR"))) == 4


class TestSingleRunMCNP:
    @pytest.mark.skip(reason="Not implemented")
    def test_build_command(self):
        pass

    @pytest.mark.skip(reason="Not implemented")
    def test_submit_job(self):
        pass


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
class TestSingleRunOpenMC:
    @pytest.mark.skip(reason="Not implemented")
    def test_build_command(self):
        pass


class TestSingleRunSerpent:
    pass
