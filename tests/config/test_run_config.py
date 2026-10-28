from __future__ import annotations

from importlib.resources import as_file, files

import pytest

import jade.resources as res
from jade.config.paths_tree import CfgTree, PathsTree
from jade.config.run_config import (
    BenchmarkRunConfig,
    EnvironmentVariables,
    LibraryFactory,
    LibraryMCNP,
    LibraryOpenMC,
    LibrarySerpent,
    RunConfig,
    RunMode,
)
from jade.helper.constants import CODE
from jade.helper.errors import ConfigError
from tests.config import resources as conf_res
from tests.run import resources as run_res

ROOT_DEFAULT_CFG = files(res).joinpath("default_cfg")
CONF_RES = files(conf_res)


class TestEnvironmentVariables:
    @pytest.mark.parametrize(
        [
            "mpi_tasks",
            "omp_threads",
            "executable",
            "code_job_templates",
            "run_mode",
            "scheduler_command",
        ],
        [
            [
                None,
                None,
                {CODE.MCNP: "test"},
                {CODE.MCNP: "test"},
                RunMode.JOB_SUBMISSION,
                None,
            ],
        ],
    )
    def test_post(
        self,
        mpi_tasks,
        omp_threads,
        executable,
        code_job_templates,
        run_mode,
        scheduler_command,
    ):
        with pytest.raises(ConfigError):
            EnvironmentVariables(
                mpi_tasks=mpi_tasks,
                openmp_threads=omp_threads,
                executables=executable,
                code_job_template=code_job_templates,
                run_mode=run_mode,
                scheduler_command=scheduler_command,
            )


class TestBenchmarkExecConfig:
    def test_post(self):
        with pytest.raises(ConfigError):
            # the None path tricks it into using the default xsdir in F4Enix
            BenchmarkRunConfig(
                description="Sphere benchmark",
                name="Sphere",
                run=[(CODE.MCNP, LibraryMCNP(name="test", path=None, suffix="31c"))],
                nps=10,
                only_input=True,
            )


class TestRunConfig:
    def test_from_yamls(self, tmpdir):
        paths_tree = PathsTree(tmpdir)
        paths_tree.cfg = CfgTree(ROOT_DEFAULT_CFG)
        env_vars_file = paths_tree.cfg.env_vars_file
        run_cfg_file = paths_tree.cfg.run_cfg
        lib_cfg_file = paths_tree.cfg.libs_cfg
        additional_settings_root = paths_tree.cfg.bench_additional_files
        run_cfg = RunConfig.from_yamls(
            env_vars_file,
            paths_tree.cfg.exe_cfg,
            run_cfg_file,
            lib_cfg_file,
            additional_settings_root,
        )


class TestLibraryOpenMC:
    def test_post(self):
        with as_file(CONF_RES.joinpath("cross_sections.xml")) as file:
            lib = LibraryOpenMC("dummy", file)

        zaids = lib.get_lib_zaids()
        assert "1001" in zaids
        assert len(zaids) == len(set(zaids))  # no duplicates


class TestLibrarySerpent:
    def test_get_lib_zaids(self):
        with as_file(files(run_res).joinpath("test.xsdata")) as file:
            lib = LibrarySerpent("dummy", file, suffix="32c")
            # the xsdata is read only when needed
            assert lib._tablenames is None
            zaids = lib.get_lib_zaids()

        assert "1001" in zaids
        assert "26056" in zaids
        assert len(zaids) == 50  # no duplicates from aliases
        # metastable and photon tables are excluded
        assert "95242" not in zaids
        assert "1000" not in zaids
        assert ("1001", "31c") in lib.tablenames
        assert lib.photon_data_dir is None

    def test_factory(self, tmpdir):
        cfg = tmpdir.join("libs_cfg.yml")
        cfg.write(
            "FENDL 3.2c:\n  serpent:\n    path: dummy.xsdata\n    suffix: 32c\n"
            "    photon_data_dir: /photon/data\n"
        )
        lib = LibraryFactory(cfg).create(CODE.SERPENT, "FENDL 3.2c")
        assert isinstance(lib, LibrarySerpent)
        assert lib.suffix == "32c"
        assert lib.photon_data_dir == "/photon/data"
