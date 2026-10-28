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
    LibrarySerpent,
    RunMode,
)
from jade.helper.__optionals__ import OMC_AVAIL
from jade.helper.constants import CODE
from jade.helper.errors import ConfigError
from jade.run.benchmark import (
    BenchmarkRun,
    SingleRunFactory,
    SingleRunMCNP,
    SingleRunOpenMC,
    SingleRunSerpent,
    SphereBenchmarkRun,
    SphereSDDRBenchmarkRun,
)
from tests.run import resources

DEFAULT_CFG = files(res).joinpath("default_cfg")
BENCHMARKS_ROOT = files(dummy_struct).joinpath("benchmark_templates")
RUN_RES = files(resources)


class TestBenchmarkRun:
    @pytest.mark.parametrize("executables", [{CODE.MCNP: "mcnp6.2"}, {}])
    def test_run_mcnp(self, tmpdir, executables):
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
            executables,
            run_mode=RunMode.JOB_SUBMISSION,
            code_job_template={
                CODE.MCNP: Path(DEFAULT_CFG, "exe_config/mcnp_template.sh")
            },
            scheduler_command="slurm",
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

    def test_get_continue_run_command(self):
        lib = LibraryMCNP(
            name="FENDL 3.2c", path=RUN_RES.joinpath("xsdir.txt"), suffix="31c"
        )
        perform = [
            (CODE.MCNP, lib),
        ]
        cfg = BenchmarkRunConfig(
            description="Dummy",
            name="Dummy_continue",
            run=perform,
            nps=10,
            only_input=True,
        )

        env_vars = EnvironmentVariables(
            10,
            10,
            {CODE.MCNP: "mcnp6.2"},
            run_mode=RunMode.LOCAL,
            code_job_template={
                CODE.MCNP: Path(DEFAULT_CFG, "exe_config/mcnp_config.sh")
            },
            scheduler_command="slurm",
        )
        sim_folder = files(dummy_struct).joinpath("simulations")
        benchmark = BenchmarkRun(cfg, sim_folder, BENCHMARKS_ROOT, env_vars)
        command = benchmark._get_continue_run_command(CODE.MCNP, lib, testing=True)
        # assert command == expected_command
        assert "Dummy_continue1" not in command[0][0]  # successful simulation
        assert (
            'mpirun -np 10 mcnp6.2 i=Dummy2.i n=Dummy2. xsdir="xsdir.txt" tasks 10'
            in command[0][0]
        )

    def test_global_run(self, tmpdir):
        perform = [
            (
                CODE.MCNP,
                LibraryMCNP(
                    name="FENDL 3.2c", path=RUN_RES.joinpath("xsdir.txt"), suffix="31c"
                ),
            ),
            (
                CODE.MCNP,
                LibraryMCNP(
                    name="ENDF VII-1", path=RUN_RES.joinpath("xsdir.txt"), suffix="00c"
                ),
            ),
        ]
        cfg = BenchmarkRunConfig(
            description="Oktavian TOF",
            name="Oktavian",
            run=perform,
            nps=10,
            only_input=False,
        )

        env_vars = EnvironmentVariables(
            10,
            10,
            {CODE.MCNP: "mcnp6.2"},
            run_mode=RunMode.GLOBAL_JOB,
            code_job_template={
                CODE.MCNP: Path(DEFAULT_CFG, "exe_config/mcnp_template.sh")
            },
            scheduler_command="slurm",
            exe_prefix="srun",
        )

        benchmark = BenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        commands = benchmark.run()
        assert len(commands) == 4
        assert os.path.exists(commands[0][2])
        assert len(commands[0][1]) == 6
        assert commands[0][0] == CODE.MCNP
        assert "srun" in commands[0][1][0]


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
            run_mode=RunMode.LOCAL,
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
        with as_file(RUN_RES.joinpath("cross_sections.xml")) as infile:
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
            run_mode=RunMode.LOCAL,
        )

        benchmark = SphereBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        assert len(os.listdir(tmpdir)) == 1

    def test_run_serpent(self, tmpdir):
        with as_file(RUN_RES.joinpath("test.xsdata")) as infile:
            lib = LibrarySerpent(name="FENDL 3.2c", path=infile, suffix="32c")
        cfg = BenchmarkRunConfig(
            description="Sphere benchmark",
            name="Sphere",
            run=[(CODE.SERPENT, lib)],
            nps=10,
            only_input=True,
            custom_inp=2,
            additional_settings_path=DEFAULT_CFG.joinpath("benchmarks/Sphere"),
        )
        env_vars = EnvironmentVariables(
            None,
            0,
            {CODE.SERPENT: "sss2"},
            run_mode=RunMode.LOCAL,
        )

        benchmark = SphereBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        benchmark.run()

        root = Path(tmpdir, "_serpent_-_FENDL 3.2c_", "Sphere")
        assert sorted(os.listdir(root)) == [
            "Sphere_1001_H-1",
            "Sphere_1002_H-2",
            "Sphere_M101_SS316L(N)-IG",
            "Sphere_M400_Water",
        ]
        assert sorted(os.listdir(Path(root, "Sphere_1001_H-1"))) == [
            "Sphere_1001_H-1.i",
            "metadata.json",
        ]

    def test_run_serpent_wrong_lib(self, tmpdir):
        lib = LibraryMCNP(name="FENDL 3.2c", path=None, suffix="31c")
        cfg = BenchmarkRunConfig(
            description="Sphere benchmark",
            name="Sphere",
            run=[(CODE.SERPENT, lib)],
            nps=10,
            only_input=True,
            custom_inp=2,
            additional_settings_path=DEFAULT_CFG.joinpath("benchmarks/Sphere"),
        )
        env_vars = EnvironmentVariables(None, 0, {}, run_mode=RunMode.LOCAL)
        benchmark = SphereBenchmarkRun(cfg, tmpdir, BENCHMARKS_ROOT, env_vars)
        with pytest.raises(ConfigError):
            benchmark.run()


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
            run_mode=RunMode.LOCAL,
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
        run_mode=RunMode.LOCAL,
        code_job_template={
            CODE.MCNP: Path(DEFAULT_CFG, "exe_config/mcnp_template.sh"),
            CODE.OPENMC: Path(DEFAULT_CFG, "exe_config/openmc_template.sh"),
        },
        scheduler_command="sbatch",
        exe_cfg_root=DEFAULT_CFG.joinpath("exe_config"),
    )


class TestSingleRunMCNP:
    def test_run(self, env_vars):
        mock_input = MockInput()

        with as_file(RUN_RES.joinpath("xsdir.txt")) as xsdir:
            lib = LibraryMCNP(name="FENDL 3.2c", path=xsdir, suffix="31c")

        single_run = SingleRunMCNP(mock_input, lib, 100)
        command = single_run.run(env_vars, "dummy", test=True)

        assert command == (
            'mpirun -np 5 mcnp6.2 i=name.i n=name. xsdir="xsdir.txt" tasks 10 > dump.out'
        )

        # test with no mpi
        env_vars.mpi_tasks = 1
        command = single_run.run(env_vars, "dummy", test=True)
        assert (
            command == 'mcnp6.2 i=name.i n=name. xsdir="xsdir.txt" tasks 10 > dump.out'
        )

        # test with no openmp
        env_vars.openmp_threads = 1
        command = single_run.run(env_vars, "dummy", test=True)
        assert command == 'mcnp6.2 i=name.i n=name. xsdir="xsdir.txt"  > dump.out'

    def test_submit_job(self, env_vars, tmpdir):
        mock_input = MockInput()
        env_vars.run_mode = RunMode.JOB_SUBMISSION
        with as_file(RUN_RES.joinpath("xsdir.txt")) as xsdir:
            lib = LibraryMCNP(name="FENDL 3.2c", path=xsdir, suffix="31c")

        single_run = SingleRunMCNP(mock_input, lib, 100)

        command = single_run.run(env_vars, tmpdir, test=True)
        assert "#!/bin/sh\n\n#SBATCH" in command
        # avoid linux path breaking in case of lib names with spaces
        assert '--chdir="' in command
        assert '--output="' in command
        assert '--error="' in command


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


class TestSingleRunSerpent:
    @pytest.fixture()
    def lib(self):
        with as_file(RUN_RES.joinpath("test.xsdata")) as xsdata:
            return LibrarySerpent(name="FENDL 3.2c", path=xsdata, suffix="32c")

    def test_run(self, env_vars, lib):
        env_vars.executables[CODE.SERPENT] = "sss2"
        single_run = SingleRunSerpent(MockInput(), lib, 100)
        command = single_run.run(env_vars, "dummy", test=True)
        assert command == "mpirun -np 5 sss2 name.i -omp 10 > dump.out"

        env_vars.mpi_tasks = 1
        env_vars.openmp_threads = 1
        command = single_run.run(env_vars, "dummy", test=True)
        assert command == "sss2 name.i > dump.out"

        name, value = single_run._get_lib_data_command()
        assert name == "SERPENT_ACELIB"
        assert value == str(lib.path)

    def test_submit_job(self, env_vars, lib, tmpdir):
        env_vars.executables[CODE.SERPENT] = "sss2"
        env_vars.run_mode = RunMode.JOB_SUBMISSION
        env_vars.code_job_template[CODE.SERPENT] = Path(
            DEFAULT_CFG, "exe_config/serpent_template.sh"
        )
        single_run = SingleRunSerpent(MockInput(), lib, 100)
        command = single_run.run(env_vars, tmpdir, test=True)
        assert f'export SERPENT_ACELIB="{lib.path}"' in command
        assert "sss2 name.i -omp 10" in command

    def test_factory(self, lib):
        template = BENCHMARKS_ROOT.joinpath("Sphere", "Sphere", "serpent")
        single_run = SingleRunFactory.create(CODE.SERPENT, template, lib, 100)
        assert isinstance(single_run, SingleRunSerpent)
        assert single_run.input.name == "Sphere"
        # mock input for continue runs
        single_run = SingleRunFactory.create(
            CODE.SERPENT, template, lib, 100, mock_input=True
        )
        assert single_run.input.name == "Sphere"
        with pytest.raises(ConfigError):
            SingleRunFactory.create(CODE.SERPENT, template, MockLibrary("a", "b"), 1)
