# JADE — AI Agent Guide

JADE is a Python V&V (Verification & Validation) framework for nuclear data libraries and particle transport codes. It automates benchmark execution, raw output parsing, and report generation (Excel + Word atlas).

- **Documentation**: [ReadTheDocs](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/)
- **PyPI package**: `jadevv` (imports as `jade`)
- **Python**: ≥ 3.10

---

## Setup

```bash
pip install -e .[dev,ui]   # dev tools: pytest, ruff, sphinx; ui: ttkthemes
```

## Running Tests

```bash
pytest                                        # all tests
pytest --cov=jade --cov-report=term-missing   # with coverage
```

Tests mirror `src/jade/` under `tests/`. Fixtures live in `tests/dummy_structure/` (pre-baked folder tree) and `tests/<subpackage>/resources/`.

## Code Formatting

`ruff` is the **mandated** formatter — run it before committing:

```bash
ruff format .
ruff check .
```

---

## Architecture

```
src/jade/
  app/        — JadeApp orchestrator; fetch.py downloads benchmark inputs from IAEA/F4E/SINBAD
  config/     — Dataclasses + YAML parsers for run/PP config; PathsTree; GlobalStatus
  run/        — Input generation, translation, job submission; benchmark.py + input.py
  post/       — 3-stage pipeline: raw output → CSV → Excel/Atlas Word doc
  helper/     — CODE enum, ALLOWED_COLUMN_NAMES, path/folder helpers, optional deps guard
  gui/        — Tkinter GUIs (conditional on TKINTER_AVAIL)
  resources/  — Bundled default YAML config templates (copied on first install)
```

All entry points wire through `JadeApp` in `src/jade/app/app.py`.

---

## Key Patterns

### ABC + Factory dispatch on `CODE` enum

Every transport-code-extensible concept uses this pattern:

```python
# helper/constants.py
class CODE(str, Enum):
    mcnp = "mcnp"; openmc = "openmc"; serpent = "serpent"; d1s = "d1s"; exp = "exp"

# e.g. run/benchmark.py
class SingleRun(ABC): ...
class SingleRunMCNP(SingleRun): ...
class SingleRunFactory:
    @staticmethod
    def create(code: CODE, ...) -> SingleRun: ...
```

The same pattern applies to `Library`/`LibraryFactory`, `Input`/`InputFactory`, and `AbstractSimOutput`.

### Config construction: always via named classmethods

```python
run_cfg = RunConfig.from_root(paths_tree)       # reads 4 YAML files
run_cfg = RunConfig.from_yamls(env_path, ...)   # explicit paths
```

Never construct config dataclasses directly.

### `test=True` mode for dry-runs

`SingleRun.run(test=True)` and `BenchmarkRun` methods return the shell command string instead of executing it. This is used throughout the test suite.

### Folder naming convention for code-lib pairs

Simulation output folders follow `_<code>_-_<lib name>_`, e.g. `_mcnp_-_FENDL 3.2c_`.  
Encode/decode with `print_code_lib()` / `get_code_lib()` from `src/jade/helper/aux_functions.py`.

### Lazy-loading properties

Expensive state (e.g. `GlobalStatus.simulations`) uses `@property` with an internal `_attr = None` guard. Do not initialize in `__init__`.

### `from __future__ import annotations`

Every module starts with this import.

---

## Standardized Tally DataFrame Columns

All parsed tally DataFrames use only column names from `ALLOWED_COLUMN_NAMES` in `src/jade/helper/constants.py`:

`Energy`, `Cells`, `time`, `tally`, `Dir`, `User`, `Segments`, `Multiplier`, `Cosine`, `Cor A`, `Cor B`, `Cor C`

---

## Adding a New Transport Code

See [dev guide](docs/source/dev/add_transport_code.rst) for full details. The four required touch points are:

1. `src/jade/helper/constants.py` — add tag to `CODE` enum
2. `src/jade/config/run_config.py` — subclass `Library`, register in `LibraryFactory`
3. `src/jade/run/benchmark.py` + `src/jade/run/input.py` — subclass `SingleRun` (implement `_build_command()`, `_get_lib_data_command()`) and `Input` (implement `set_nps()`, `translate()`, `_write()`); register in `SingleRunFactory`
4. `src/jade/post/sim_output.py` — subclass `AbstractSimOutput`; wire into `RawProcessor.__init__()`

Add tests mirroring the new code's path under `tests/`.

## Adding a New Benchmark

See [dev guide](docs/source/dev/add_benchmark/) for full details. The three required config YAML files go in `src/jade/resources/default_cfg/benchmarks_pp/`:

- `raw/<name>.yaml` — tally → CSV pipeline (`ConfigRawProcessor`)
- `excel/<name>.yaml` — comparison table config (`ConfigExcelProcessor`)
- `atlas/<name>.yaml` — Word atlas plot config (`ConfigAtlasProcessor`)

Input files are hosted externally (not in this repo): IAEA GitHub for open benchmarks, F4E GitLab or SINBAD for restricted ones.

**YAML alias convention**: alias names must start with `_` (e.g. `&_my_alias`) to avoid clashing with config key parsing.

---

## Branching & Versioning

- Permanent branches: `master` (stable), `developing` (integration)
- Branch types: `Feature/*` and `Benchmark/*` off `developing`; `Release/*` for stabilization; `Hotfix/*` off `master`
- **Semantic versioning**: Major = non-backwards-compatible change (new transport code, class restructure, folder layout). Minor = new features/benchmarks. Patch = bug fixes.
- Every bug fix must include a regression test.
- PRs require an independent code review (contributor cannot review their own PR).

---

## CI Matrix

- **OS**: `ubuntu-latest`, `ubuntu-20.04`, `windows-latest`
- **Python**: 3.11, 3.12, 3.13
- Full matrix only on `master`/`release*`; feature branches run latest Python on Ubuntu only.
- OpenMC is installed on Linux only; Windows CI skips OpenMC tests.
