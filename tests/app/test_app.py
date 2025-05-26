from __future__ import annotations

import os
import shutil
from importlib.resources import files
from pathlib import Path

import pytest

import tests
from jade.app.app import JadeApp
from jade.config.run_config import (
    BenchmarkRunConfig,
    EnvironmentVariables,
    LibraryMCNP,
    RunConfig,
    RunMode,
)
from jade.helper.constants import CODE
from tests.run import resources as run_res

RUN_RES = files(run_res)

DUMMY_ROOT = files(tests).joinpath("dummy_structure")


class TestJadeApp:
    def test_run_benchmarks(self, tmpdir, monkeypatch):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the simulation root folder
        app.tree.simulations = tmpdir
        # I should get here a request for override let's say no the first time
        monkeypatch.setattr("builtins.input", lambda _: "n")
        app.run_benchmarks()
        assert len(os.listdir(tmpdir)) == 0

        # Now let's override instead
        monkeypatch.setattr("builtins.input", lambda _: "y")
        app.run_benchmarks()
        assert len(os.listdir(tmpdir)) > 0

    def test_raw_process(self, tmpdir):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the raw processor folder
        app.tree.raw = tmpdir
        app.status.raw_results_path = tmpdir
        app.status.update()

        app.raw_process(subset=["Oktavian"])
        # manually update the status
        app.status.update()
        filepath = Path(
            tmpdir,
            "_mcnp_-_FENDL 3.2c_/Oktavian/Oktavian_Al 21.csv",
        )
        # now run again and test that nothing was overridden
        initial_mod_time = os.path.getmtime(filepath)
        app.raw_process(subset=["Oktavian"])
        assert os.path.getmtime(filepath) == initial_mod_time

    def test_post_process(self, tmpdir):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the post processor folder
        app.tree.postprocessing = tmpdir
        app.status.update()

        app.post_process()

    def test_restore_default_cfg(self, tmpdir):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the config folder
        app.tree.cfg.path = tmpdir
        app.restore_default_cfg()

        assert len(os.listdir(tmpdir)) > 0

    def test_installation(self, tmpdir):
        app = JadeApp(root=tmpdir)

        assert len(os.listdir(tmpdir)) > 0

        # while we are at it, test also the add rmode 0
        app.add_rmode()
        # check one of the files, the Sphere
        path = Path(tmpdir, "benchmark_templates/Sphere/Sphere/mcnp/Sphere.i")
        success = False
        with open(path) as f:
            for line in f:
                if "rmode 0" in line.lower():
                    success = True
        assert success

    def test_rmv_runtpe(self, tmpdir):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # copy the simulation folder in tmp
        shutil.copytree(app.tree.simulations, tmpdir.join("simulations"))
        # place a fake .r file in one of the folders
        target = "_mcnp_-_FENDL 3.2c_/Sphere/Sphere_dummy1"
        nfiles = len(os.listdir(Path(app.tree.simulations, target)))
        # override the simulation root folder
        app.tree.simulations = tmpdir.join("simulations")
        with open(Path(app.tree.simulations, target, "dummy.r"), "w") as out:
            out.write("dummy content")
        check = len(os.listdir(Path(app.tree.simulations, target)))
        app.rmv_runtpe()
        new_len = len(os.listdir(Path(app.tree.simulations, target)))
        assert new_len == nfiles == check - 1

    def test_continue_run(self):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the run config file
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
            0,
            10,
            {CODE.MCNP: "mcnp6.2"},
            run_mode=RunMode.SERIAL,
            code_configurations={
                CODE.MCNP: Path(DUMMY_ROOT, "cfg/exe_config/mcnp_config.sh")
            },
            batch_template=Path(DUMMY_ROOT, "cfg/batch_templates/Slurmtemplate.sh"),
            batch_system="sbatch",
        )
        run_cfg = RunConfig(env_vars, {"Dummy_continue": cfg})
        app.run_cfg = run_cfg
        with pytest.raises(FileNotFoundError):
            app.continue_run()

        env_vars.run_mode = RunMode.JOB_SUMISSION
        run_cfg = RunConfig(env_vars, {"Dummy_continue": cfg})
        app.run_cfg = run_cfg
        command = app.continue_run(testing=True)
        assert "#!/bin/sh\n\n#SBATCH" in command[0]
