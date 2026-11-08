from __future__ import annotations

import json
from pathlib import Path

import pytest

from jade.helper.raw_migration import migrate_raw_results, plan_raw_migration


def _make_raw(root: Path, codelib: str, bench: str, metadata: dict | None) -> Path:
    folder = Path(root, codelib, bench)
    folder.mkdir(parents=True)
    Path(folder, "result.csv").write_text("a,b\n1,2\n")
    if metadata is not None:
        with open(Path(folder, "metadata.json"), "w") as f:
            json.dump(metadata, f)
    return folder


@pytest.fixture
def raw_root(tmp_path) -> Path:
    _make_raw(tmp_path, "_mcnp_-_FENDL 3.2c_", "A", {"code_version": "6.2"})
    _make_raw(tmp_path, "_mcnp_-_FENDL 3.2c_", "B", {"code_version": None})
    _make_raw(tmp_path, "_openmc_-_FENDL 3.2c_", "A", {"code_version": "0.15.0"})
    _make_raw(tmp_path, "_openmc_-_FENDL 3.2c_", "C", None)
    _make_raw(tmp_path, "_openmc_-_FENDL 3.2c_", "D", {"code_version": "0.14.3"})
    # destination already present for D
    _make_raw(tmp_path, "_openmc_-_0.14.3_-_FENDL 3.2c_", "D", {"code_version": "x"})
    _make_raw(tmp_path, "_exp_-_exp_", "A", None)
    Path(tmp_path, "__init__.py").write_text("")
    return tmp_path


def test_plan_raw_migration(raw_root):
    moves = {
        (m.source.parent.name, m.source.name): m for m in plan_raw_migration(raw_root)
    }
    assert set(moves) == {
        ("_mcnp_-_FENDL 3.2c_", "A"),
        ("_mcnp_-_FENDL 3.2c_", "B"),
        ("_openmc_-_FENDL 3.2c_", "A"),
        ("_openmc_-_FENDL 3.2c_", "C"),
        ("_openmc_-_FENDL 3.2c_", "D"),
    }
    assert moves[("_mcnp_-_FENDL 3.2c_", "A")].destination == Path(
        raw_root, "_mcnp_-_6.2_-_FENDL 3.2c_", "A"
    )
    assert moves[("_mcnp_-_FENDL 3.2c_", "B")].destination is None
    assert moves[("_openmc_-_FENDL 3.2c_", "C")].destination is None
    assert moves[("_openmc_-_FENDL 3.2c_", "D")].destination is None


def test_migrate_dry_run(raw_root):
    before = sorted(p.relative_to(raw_root) for p in raw_root.rglob("*"))
    migrate_raw_results(raw_root, dry_run=True)
    after = sorted(p.relative_to(raw_root) for p in raw_root.rglob("*"))
    assert before == after


def test_migrate_raw_results(raw_root):
    migrate_raw_results(raw_root)
    assert Path(raw_root, "_mcnp_-_6.2_-_FENDL 3.2c_", "A", "result.csv").exists()
    assert Path(raw_root, "_openmc_-_0.15.0_-_FENDL 3.2c_", "A", "result.csv").exists()
    # not migratable folders stay where they were
    assert Path(raw_root, "_mcnp_-_FENDL 3.2c_", "B").exists()
    assert not Path(raw_root, "_mcnp_-_FENDL 3.2c_", "A").exists()
    assert Path(raw_root, "_openmc_-_FENDL 3.2c_", "C").exists()
    assert Path(raw_root, "_openmc_-_FENDL 3.2c_", "D").exists()
    assert Path(raw_root, "_exp_-_exp_", "A").exists()
    # running again is a no-op for the already migrated folders
    moves = migrate_raw_results(raw_root)
    assert all(m.destination is None for m in moves)


def test_migrate_removes_empty_codelib(tmp_path):
    _make_raw(tmp_path, "_mcnp_-_lib_", "A", {"code_version": "6.2"})
    migrate_raw_results(tmp_path)
    assert not Path(tmp_path, "_mcnp_-_lib_").exists()
    assert Path(tmp_path, "_mcnp_-_6.2_-_lib_", "A").exists()
