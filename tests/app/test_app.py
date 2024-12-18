from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

import tests
from jade.app.app import JadeApp

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

        app.raw_process()
        # manually update the status
        app.status.update()
        filepath = Path(
            tmpdir,
            "_mcnp_-_FENDL 3.2c_/Oktavian/Oktavian_Al 21.csv",
        )
        # now run again and test that nothing was overridden
        initial_mod_time = os.path.getmtime(filepath)
        app.raw_process()
        assert os.path.getmtime(filepath) == initial_mod_time

    def test_restore_default_cfg(self, tmpdir):
        app = JadeApp(root=DUMMY_ROOT, skip_init=True)
        # override the config folder
        app.tree.cfg.path = tmpdir
        app.restore_default_cfg()

        assert len(os.listdir(tmpdir)) > 0

    def test_installation(self, tmpdir):
        app = JadeApp(root=tmpdir)

        assert len(os.listdir(tmpdir)) > 0
