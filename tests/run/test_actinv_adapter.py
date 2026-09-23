"""Scalar adapter contracts; no nuclear libraries or ACTINV install required."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import yaml

from jade.app.app import JadeApp
from jade.config.excel_config import ComparisonType
from jade.config.paths_tree import PathsTree
from jade.config.raw_config import ConfigRawProcessor
from jade.config.run_config import (
    EnvironmentVariables,
    LibraryFactory,
    RunMode,
)
from jade.config.status import GlobalStatus
from jade.gui import run_config_gui
from jade.helper.aux_functions import CODE_CHECKERS
from jade.helper.constants import CODE
from jade.helper.errors import ConfigError
from jade.post.excel_routines import Table
from jade.post.manipulate_tally import cooling_time
from jade.post.raw_processor import RawProcessor
from jade.post.sim_output import ActinvSimOutput
from jade.run.benchmark import BenchmarkRun, SingleRunFactory
from jade.run.input import InputACTINV

ROOT = Path(__file__).parents[2]


@pytest.fixture
def config(tmp_path):
    activation = tmp_path / "activation"
    activation.mkdir()
    libraries = {}
    for tag in ("first", "second"):
        npz = activation / f"{tag}.npz"
        npz.write_bytes(tag.encode())
        (activation / f"{tag}_index.json").write_text(
            json.dumps(
                {
                    "schema": "actinv-library-index-2",
                    "projectile": "neutron",
                    "groups": "fispact-709",
                    "targets": [{"za": 26056, "liso": 0}],
                }
            )
        )
        decay = tmp_path / f"{tag}.decay"
        decay.write_text("synthetic decay data")
        libraries[tag] = {"actinv": {"path": str(npz), "decay_primary": str(decay)}}
    libs_file = tmp_path / "libs.yml"
    libs_file.write_text(yaml.safe_dump(libraries))
    return LibraryFactory(libs_file)


@pytest.fixture
def lib(config):
    return config.create(CODE.ACTINV, "first")


@pytest.fixture
def folder(tmp_path):
    folder = tmp_path / "iron-subcase with spaces"
    folder.mkdir()
    spec = {
        "spec": "actinv-spec-1",
        "projectile": "neutron",
        "library": {"path": "catalog:old"},
        "decay": {"primary": "catalog:old-decay", "fallback": "old/fallback.dat"},
        "material": {"mass_g": 1, "basis": "wt_percent", "composition": {"Fe": 100}},
        "spectrum": {"structure": "fispact-709", "flux_per_group": [1.0] * 709},
        "schedule": [{"dt": "5 min", "flux": 1}, {"dt": "66 s", "flux": 0}],
        "options": {"mode": "auto"},
    }
    (folder / "case one.json").write_text(json.dumps(spec))
    return folder


@pytest.fixture
def env(tmp_path):
    path = tmp_path / "env.yml"
    path.write_text(
        yaml.safe_dump(
            {
                "mpi_tasks": 0,
                "openmp_threads": 1,
                "executables": {"actinv": "actinv"},
                "run_mode": "local",
                "code_job_template": {},
                "exe_prefix": None,
            }
        )
    )
    return EnvironmentVariables.from_yaml(path)


@pytest.fixture
def app(config, folder, env, tmp_path):
    tree = PathsTree(tmp_path / "jade")
    tree.init_tree()
    shutil.copytree(
        ROOT / "src/jade/resources/default_cfg", tree.cfg.path, dirs_exist_ok=True
    )
    cfg = tree.cfg.path
    libs = yaml.safe_load((cfg / "libs_cfg.yml").read_text())
    (cfg / "libs_cfg.yml").write_text(yaml.safe_dump({**libs, **config.cfg}))
    run = yaml.safe_load((cfg / "run_cfg.yml").read_text())
    run["FNS-DecayHeat"]["codes"]["actinv"] = ["first"]
    (cfg / "run_cfg.yml").write_text(yaml.safe_dump(run))
    templates = tree.benchmark_input_templates / "FNS-DecayHeat"
    case = templates / "iron" / "actinv"
    case.mkdir(parents=True)
    shutil.copy(folder / "case one.json", case / "spec.json")
    (templates / "benchmark_metadata.json").write_text(
        json.dumps({"name": "FNS-DecayHeat", "version": {"actinv": "1"}})
    )
    app = JadeApp(tree.root, skip_init=True)
    app.run_cfg.env_vars = env
    return app


def result():
    return {
        "certificate": {"solver": "actinv-core test"},
        "steps": [
            {
                "t_s": time,
                "flux": flux,
                "heat_W_per_g": {"total": heat, "alpha": 0, "beta": heat, "gamma": 0},
                "activity_Bq_per_g": {"Mn56": activity},
            }
            for time, flux, heat, activity in ((300, 1, 2e-6, 20), (366, 0, 1e-6, 10))
        ],
    }


def test_explicit_selection_overrides_catalog_and_removes_fallback(folder, config):
    inputs = []
    for name in ("first", "second"):
        selected = config.create(CODE.ACTINV, name)
        run = SingleRunFactory.create(CODE.ACTINV, folder, selected, 1)
        assert run.input.spec["library"] == {
            "path": str(selected.path),
            "sha256": selected.sha256,
        }
        assert run.input.spec["decay"] == {"primary": str(selected.decay_primary)}
        inputs.append(run.input.spec)
    assert inputs[0]["library"] != inputs[1]["library"]
    assert inputs[0]["decay"] != inputs[1]["decay"]


def test_explicit_selection_is_not_alphabetical(lib, folder):
    (lib.path.parent / "aaa-neutron-709g.npz").write_bytes(b"wrong data")
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    assert run.input.spec["library"]["path"] == str(lib.path)


@pytest.mark.parametrize("field", ["path", "decay_primary", "decay_fallback"])
def test_missing_selected_file_fails(config, tmp_path, field):
    config.cfg["first"]["actinv"][field] = str(tmp_path / "missing")
    with pytest.raises(ConfigError, match=field):
        config.create(CODE.ACTINV, "first")


def test_directory_selection_fails(config):
    config.cfg["first"]["actinv"]["path"] = str(
        Path(config.cfg["first"]["actinv"]["path"]).parent
    )
    with pytest.raises(ConfigError, match="file"):
        config.create(CODE.ACTINV, "first")


@pytest.mark.parametrize(
    "field,value",
    [("groups", "wrong"), ("projectile", "proton"), ("schema", "unknown")],
)
def test_incompatible_index_fails(config, field, value):
    path = Path(config.cfg["first"]["actinv"]["path"]).with_name("first_index.json")
    index = json.loads(path.read_text())
    index[field] = value
    path.write_text(json.dumps(index))
    with pytest.raises(ConfigError, match="index"):
        config.create(CODE.ACTINV, "first")


def test_mesh_and_ambiguous_specs_rejected(folder, lib):
    spec_path = folder / "case one.json"
    spec = json.loads(spec_path.read_text())
    (folder / "another.json").write_text(json.dumps(spec))
    with pytest.raises(ConfigError, match="exactly one"):
        InputACTINV(folder, lib)
    spec["spec"] = "actinv-mesh-spec-1"
    spec_path.write_text(json.dumps(spec))
    with pytest.raises(ConfigError, match="mesh"):
        InputACTINV(folder, lib)


def test_continue_uses_persisted_filename_and_rejects_changed_data(folder, config, env):
    lib = config.create(CODE.ACTINV, "first")
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    run.write(folder)
    resumed = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1, mock_input=True)
    assert resumed._build_command(env)[2] == "case one.json"
    with pytest.raises(ConfigError, match="continuation"):
        SingleRunFactory.create(
            CODE.ACTINV,
            folder,
            config.create(CODE.ACTINV, "second"),
            1,
            mock_input=True,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("mpi_tasks", 4),
        ("exe_prefix", "srun"),
        ("run_mode", "job"),
        ("executables", {}),
        ("executables", {CODE.ACTINV: None}),
    ],
)
def test_unsupported_execution_rejected(folder, lib, env, field, value):
    setattr(env, field, value)
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    with pytest.raises(ConfigError):
        run.run(env, folder, test=True)


def test_rejected_settings_keep_previous_results(app):
    previous = app.tree.simulations / "_actinv_-_first_" / "FNS-DecayHeat" / "iron"
    previous.mkdir(parents=True)
    for name in ("result.json", "actinv.complete"):
        (previous / name).write_text("previous")
    app.run_cfg.env_vars.exe_prefix = "srun"
    with pytest.raises(ConfigError, match="prefix"):
        BenchmarkRun(
            app.run_cfg.benchmarks["FNS-DecayHeat"],
            app.tree.simulations,
            app.tree.benchmark_input_templates,
            app.run_cfg.env_vars,
        ).run()
    assert sorted(os.listdir(previous)) == ["actinv.complete", "result.json"]


@pytest.mark.parametrize(
    "method,only_input",
    [("run_benchmarks", False), ("continue_run", False), ("continue_run", True)],
)
def test_session_checks_settings_before_any_benchmark(
    app, monkeypatch, method, only_input
):
    app.run_cfg.benchmarks["FNS-DecayHeat"].only_input = only_input
    app.run_cfg.env_vars.exe_prefix = "srun"  # as in JADE's shipped defaults

    def started(*args, **kwargs):
        raise AssertionError("work started before the settings were checked")

    monkeypatch.setattr("jade.app.app.BenchmarkRunFactory.create", started)
    monkeypatch.setattr("builtins.input", started)
    with pytest.raises(ConfigError, match="prefix"):
        getattr(app, method)()


@pytest.mark.parametrize("entry_point", ["application", "benchmark"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("exe_prefix", "srun"),
        ("mpi_tasks", 4),
        ("run_mode", RunMode.JOB_SUBMISSION),
        ("run_mode", RunMode.GLOBAL_JOB),
    ],
)
def test_input_only_needs_no_executable_or_execution_settings(
    app, config, monkeypatch, entry_point, field, value
):
    benchmark = app.run_cfg.benchmarks["FNS-DecayHeat"]
    benchmark.only_input = True
    app.run_cfg.benchmarks = {"FNS-DecayHeat": benchmark}
    app.run_cfg.env_vars.executables = {}

    def launched(*args, **kwargs):
        raise AssertionError("Input-only generation must not launch a process")

    monkeypatch.setattr(subprocess, "run", launched)
    setattr(app.run_cfg.env_vars, field, value)
    if entry_point == "application":
        app.run_benchmarks()
    else:
        BenchmarkRun(
            benchmark,
            app.tree.simulations,
            app.tree.benchmark_input_templates,
            app.run_cfg.env_vars,
        ).run()
    generated = app.tree.simulations / "_actinv_-_first_" / "FNS-DecayHeat" / "iron"
    spec = json.loads((generated / "spec.json").read_text())
    assert spec["library"]["path"] == str(config.create(CODE.ACTINV, "first").path)
    assert not (generated / "actinv.complete").exists()
    assert not (generated / "result.json").exists()


def test_old_gui_configuration_loads_and_actinv_roundtrips(tmp_path, monkeypatch):
    gui = run_config_gui.ConfigGUI
    tree = Mock()
    owner = Mock(bench_tree=tree)
    gui.load_yaml_run(owner, ROOT / "src/jade/resources/default_cfg/run_cfg.yml")
    assert tree.insert.called
    path = tmp_path / "one.yml"
    path.write_text(
        yaml.safe_dump(
            {
                "FNS-DecayHeat": {
                    "codes": {"actinv": ["first"]},
                    "description": "heat",
                    "nps": 1,
                    "only_input": False,
                    "custom_input": None,
                }
            }
        )
    )
    tree.reset_mock()
    gui.load_yaml_run(owner, path)
    values = tree.insert.call_args.kwargs["values"]
    assert values[7] == "X"
    tree.get_children.return_value = ["row"]
    tree.item.return_value = values
    owner.bench_column_mapping = {
        f"#{i + 1}": column
        for i, column in enumerate(
            (
                "name",
                "description",
                "generate",
                "mcnp",
                "d1s",
                "openmc",
                "serpent",
                "actinv",
                "nps",
                "custom_input",
            )
        )
    }
    owner._get_lib_settings.return_value = ["first"]
    monkeypatch.setattr(
        run_config_gui,
        "filedialog",
        Mock(asksaveasfilename=Mock(return_value=str(path))),
        raising=False,
    )
    monkeypatch.setattr(run_config_gui, "messagebox", Mock(), raising=False)
    gui.save_settings(owner)
    assert yaml.safe_load(path.read_text())["FNS-DecayHeat"]["codes"]["actinv"] == [
        "first"
    ]


def test_scalar_parse_and_cooling_units(tmp_path):
    (tmp_path / "result.json").write_text(json.dumps(result()))
    parsed = ActinvSimOutput(tmp_path)
    heat = cooling_time(parsed.tallydata[1], 300)
    assert list(heat["time"]) == [66]
    assert list(heat["Value"] * 1e6) == [1]
    assert list(heat["Error"]) == [0]
    assert list(parsed.tallydata[2]["Value"]) == [20, 10]


@pytest.mark.parametrize(
    "mutation", ["empty", "nan", "decreasing", "negative", "unbalanced", "version"]
)
def test_bad_result_rejected(tmp_path, mutation):
    data = result()
    if mutation == "empty":
        data["steps"] = []
    elif mutation == "version":
        data["certificate"]["solver"] = None
    elif mutation == "decreasing":
        data["steps"][1]["t_s"] = 200
    else:
        data["steps"][1]["heat_W_per_g"]["total"] = {
            "nan": float("nan"),
            "negative": -1,
            "unbalanced": 2,
        }[mutation]
    (tmp_path / "result.json").write_text(json.dumps(data))
    with pytest.raises(ValueError):
        ActinvSimOutput(tmp_path)


def test_wrong_endpoint_and_incomplete_schedule_rejected(tmp_path):
    (tmp_path / "result.json").write_text(json.dumps(result()))
    parsed = ActinvSimOutput(tmp_path)
    for schedule in (
        [{"dt": "300 s", "flux": 1}],
        [{"dt": "300 s", "flux": 1}, {"dt": "67 s", "flux": 0}],
    ):
        with pytest.raises(ValueError):
            parsed.validate_schedule({"schedule": schedule})


def test_fresh_run_discovery_and_raw_csv(folder, lib, env, monkeypatch, tmp_path):
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    sim = tmp_path / "simulations/_actinv_-_first_/FNS-DecayHeat/iron"
    sim.mkdir(parents=True)
    run.write(sim)
    (sim / "metadata.json").write_text(
        json.dumps(
            {
                "code": "actinv",
                "library": "first",
                "benchmark_name": "FNS-DecayHeat",
                "benchmark_version": "1",
            }
        )
    )

    def fake_cli(command, **kwargs):
        assert isinstance(command, list) and "shell" not in kwargs
        assert kwargs["timeout"] == 180
        Path(command[-1]).write_text(json.dumps(result()))

    monkeypatch.setattr(subprocess, "run", fake_cli)
    assert run.run(env, sim)
    status = GlobalStatus(tmp_path / "simulations", tmp_path / "raw")
    assert status.simulations[(CODE.ACTINV, "first", "FNS-DecayHeat")].success
    raw = tmp_path / "raw"
    raw.mkdir()
    cfg = ConfigRawProcessor.from_yaml(
        ROOT
        / "src/jade/resources/default_cfg/benchmarks_pp/raw/actinv/FNS-DecayHeat.yaml"
    )
    RawProcessor(cfg, sim, raw).process_raw_data()
    csv = pd.read_csv(raw / "iron Decay heat.csv")
    assert list(csv["time"]) == [66]
    assert list(csv["Value"]) == [1]


@pytest.mark.parametrize("failure", ["exit", "invalid", "incomplete", "cancel"])
def test_failed_run_never_reuses_stale_success(folder, lib, env, monkeypatch, failure):
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    run.write(folder)
    (folder / "actinv.complete").write_text("old")
    (folder / "result.json").write_text(json.dumps(result()))

    def fail(command, **kwargs):
        if failure == "exit":
            raise subprocess.CalledProcessError(2, command)
        if failure == "cancel":
            raise KeyboardInterrupt
        payload = result()
        if failure == "incomplete":
            payload["steps"].pop()
        Path(command[-1]).write_text(
            "invalid" if failure == "invalid" else json.dumps(payload)
        )

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises((subprocess.CalledProcessError, ValueError, KeyboardInterrupt)):
        run.run(env, folder)
    assert not CODE_CHECKERS[CODE.ACTINV].check_success(os.listdir(folder))
    assert not list(folder.glob(".actinv-*"))


def test_decimal_cooling_times_survive_table_intersection(tmp_path):
    sim, raw = tmp_path / "sim", tmp_path / "raw"
    sim.mkdir()
    raw.mkdir()
    payload = result()
    payload["steps"][1]["t_s"] = 382.2
    (sim / "result.json").write_text(json.dumps(payload))
    (sim / "metadata.json").write_text(json.dumps({"code": "actinv"}))
    cfg = ConfigRawProcessor.from_yaml(
        ROOT
        / "src/jade/resources/default_cfg/benchmarks_pp/raw/actinv/FNS-DecayHeat.yaml"
    )
    RawProcessor(cfg, sim, raw).process_raw_data()
    calculated = pd.read_csv(raw / "sim Decay heat.csv")
    measured = pd.DataFrame({"time": [82.2], "Value": [2.0], "Error": [0.05]})
    comparison = Table._compare(measured, calculated, ComparisonType.RATIO)
    assert list(comparison["time"]) == [82.2]
    assert list(comparison["Value"]) == [0.5]
    assert list(comparison["Error"]) == [0.05]


def test_other_irradiation_history_fails_instead_of_shifting(tmp_path):
    sim, raw = tmp_path / "sim", tmp_path / "raw"
    sim.mkdir()
    raw.mkdir()
    payload = result()
    # seven-hour irradiation: no endpoint at the configured 300-second shutdown
    for step, elapsed in zip(payload["steps"], (25200, 28800)):
        step["t_s"] = elapsed
    (sim / "result.json").write_text(json.dumps(payload))
    (sim / "metadata.json").write_text(json.dumps({"code": "actinv"}))
    cfg = ConfigRawProcessor.from_yaml(
        ROOT
        / "src/jade/resources/default_cfg/benchmarks_pp/raw/actinv/FNS-DecayHeat.yaml"
    )
    with pytest.raises(ValueError, match="shutdown"):
        RawProcessor(cfg, sim, raw).process_raw_data()


@pytest.mark.parametrize("mode", ["timeout", "cancel", "exit_during_cancel"])
def test_leaf_child_is_reaped_on_timeout_or_cancellation(
    folder, lib, env, monkeypatch, mode
):
    run = SingleRunFactory.create(CODE.ACTINV, folder, lib, 1)
    run.write(folder)
    child = folder / "child.py"
    child.write_text("import time\ntime.sleep(30)\n")
    # Isolated Python leaf child, never a Rust test executable.
    monkeypatch.setattr(
        run,
        "_build_command",
        lambda cfg: [sys.executable, str(child), "unused", "result.json"],
    )
    children = []
    original_popen = subprocess.Popen

    class ObservedChild(original_popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            children.append(self)

        def communicate(self, *args, **kwargs):
            if mode == "cancel":
                raise KeyboardInterrupt
            if mode == "exit_during_cancel":
                self.kill()
                self.wait(timeout=5)
                raise KeyboardInterrupt
            return super().communicate(*args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", ObservedChild)
    run.TIMEOUT_SECONDS = 0.05
    expected = subprocess.TimeoutExpired if mode == "timeout" else KeyboardInterrupt
    with pytest.raises(expected):
        run.run(env, folder)
    assert len(children) == 1 and children[0].returncode is not None
    assert not (folder / "actinv.complete").exists()
    assert not list(folder.glob(".actinv-*"))
