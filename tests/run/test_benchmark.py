from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import pytest

import jade.resources as res
import tests.dummy_structure as dummy_struct
from jade.config.run_config import (
    BenchmarkRunConfig,
    EnvironmentVariables,
    LibraryD1S,
    LibraryMCNP,
    LibraryOpenMC,
    RunMode,
)
from jade.helper.__openmc__ import OMC_AVAIL
from jade.helper.constants import CODE
from jade.run.benchmark import (
    BenchmarkRun,
    SingleRunMCNP,
    SingleRunOpenMC,
    SphereBenchmarkRun,
    SphereSDDRBenchmarkRun,
)
from tests.run import resources

DEFAULT_CFG = files(res).joinpath("default_cfg")
BENCHMARKS_ROOT = files(dummy_struct).joinpath("benchmark_templates")
RUN_RES = files(resources)


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
    
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
    def test_run_openmc(self, tmpdir):
        with as_file(RUN_RES.joinpath('cross_sections.xml')) as infile:
            lib = LibraryOpenMC(name="ENDF VII-1", path=infile)
        perform = [
            (CODE.OPENMC, lib),
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
            {CODE.OPENMC: "openmc"},
            run_mode=RunMode.SERIAL,
        )

        benchmark = SphereBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        assert len(os.listdir(tmpdir)) == 1


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


class MockInput:
    def __init__(self):
        self.name = "name"

    def translate(self):
        return

    def set_nps(self, nps):
        return


@pytest.fixture()
def env_vars():
    return EnvironmentVariables(
        mpi_tasks=5,
        openmp_threads=10,
        executables={CODE.MCNP: "mcnp6.2", CODE.OPENMC: "openmc"},
        run_mode=RunMode.SERIAL,
        code_configurations={
            CODE.MCNP: Path(DEFAULT_CFG, "exe_config/mcnp_config.sh"),
            CODE.OPENMC: Path(DEFAULT_CFG, "exe_config/openmc_config.sh"),
        },
        batch_template=DEFAULT_CFG.joinpath("batch_templates/Slurmtemplate.sh"),
        batch_system="sbatch",
        mpi_prefix="mpirun",
    )


class TestSingleRunMCNP:
    def test_run(self, env_vars):
        mock_input = MockInput()

        with as_file(RUN_RES.joinpath("xsdir.txt")) as xsdir:
            lib = LibraryMCNP(name="FENDL 3.2c", path=xsdir, suffix="31c")

        single_run = SingleRunMCNP(mock_input, lib, 100)
        command = single_run.run(env_vars, "dummy", test=True)

        assert command == (
            "mpirun -np 5 mcnp6.2 i=name.i n=name. xsdir=xsdir.txt tasks 10 > dump.out"
        )

        # test with no mpi
        env_vars.mpi_tasks = 1
        command = single_run.run(env_vars, "dummy", test=True)
        assert command == "mcnp6.2 i=name.i n=name. xsdir=xsdir.txt tasks 10 > dump.out"

        # test with no openmp
        env_vars.openmp_threads = 1
        command = single_run.run(env_vars, "dummy", test=True)
        assert command == "mcnp6.2 i=name.i n=name. xsdir=xsdir.txt  > dump.out"

    def test_submit_job(self, env_vars, tmpdir):
        mock_input = MockInput()
        env_vars.run_mode = RunMode.JOB_SUMISSION
        with as_file(RUN_RES.joinpath("xsdir.txt")) as xsdir:
            lib = LibraryMCNP(name="FENDL 3.2c", path=xsdir, suffix="31c")

        single_run = SingleRunMCNP(mock_input, lib, 100)

        command = single_run.run(env_vars, tmpdir, test=True)
        assert f"sbatch {tmpdir}" in command


class MockLibrary:
    def __init__(self, name, path):
        self.name = name
        self.path = path


class TestSingleRunOpenMC:
    def test_build_command(self, env_vars):
        mock_input = MockInput()
        lib = MockLibrary(name="ENDF VII-1", path="dummy/cross_sections.xml")
        single_run = SingleRunOpenMC(mock_input, lib, 100)
        command = single_run._build_command(env_vars)
        assert command == ["openmc", "--threads", "10"]
