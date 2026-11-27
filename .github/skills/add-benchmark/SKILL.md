---
name: add-benchmark
description: "Add a new benchmark to JADE. Use when: adding a benchmark, creating benchmark YAML configs, writing raw/excel/atlas config files for a new benchmark, contributing benchmarks to JADE, configuring tally modifiers and concatenation options, setting up post-processing for a new simulation benchmark."
argument-hint: "<benchmark_name>"
---

# Add a New JADE Benchmark

## When to Use
- Adding a new benchmark to the JADE V&V suite
- Creating the three required YAML config files (`raw`, `excel`, `atlas`)
- Figuring out which tally modifiers or concatenation options to use
- Deciding where to host benchmark input files

## Checklist

- [ ] Step 1 — Create `raw/<name>.yaml` in `src/jade/resources/default_cfg/benchmarks_pp/raw/<code>/`
- [ ] Step 2 — Create `excel/<name>.yaml` in `src/jade/resources/default_cfg/benchmarks_pp/excel/`
- [ ] Step 3 — Create `atlas/<name>.yaml` in `src/jade/resources/default_cfg/benchmarks_pp/atlas/`
- [ ] Step 4 — Upload input files to the correct external repository
- [ ] Step 5 — Add documentation (RST description + update overview table in `docs/source/benchmarks/`)

---

## Step 1 — Raw Config (`raw/<name>.yaml`)

**Location**: `src/jade/resources/default_cfg/benchmarks_pp/raw/<code>/`  
**Purpose**: Map transport-code tally IDs → transport-code-independent CSV *results*.

Each top-level key is a *result name*. Results that don't exist in a run are silently skipped.

```yaml
# Use _ prefix on YAML aliases to avoid clashing with JADE parser
_my_alias: &_alias_name
  key: value

Result name:
  concat_option: no_action   # or: sum, concat, subtract, ratio
  <tally_id>: [[<modifier>, {<args>}], [<next_modifier>, {}]]
  <tally_id_2>: [[no_action, {}]]
```

**Rules**:
- Tally IDs are integers matching the transport code's tally numbering.
- More than one modifier can be chained in series on the same tally.
- Output column names must come from `ALLOWED_COLUMN_NAMES` — see [YAML config reference](./references/yaml-config.md#allowed-column-names).
- YAML anchor names must start with `_` (e.g. `&_my_alias`).

See [yaml-config.md](./references/yaml-config.md) for all modifiers and concatenation options.

---

## Step 2 — Excel Config (`excel/<name>.yaml`)

**Location**: `src/jade/resources/default_cfg/benchmarks_pp/excel/`  
**Purpose**: Define comparison tables written to the output Excel file.

```yaml
Table name:             # becomes the Excel sheet name
  results:
    - Result name 1     # must match result names in raw config
    - Result name 2
  comparison_type: percentage   # absolute | percentage | ratio | chi_squared
  table_type: simple            # simple | pivot | chi_squared
  x: Energy             # column for x-axis
  y: Value              # column for y-axis
  # optional:
  add_error: true
  conditional_formatting:
    red: 20
    orange: 10
    yellow: 5
```

See [yaml-config.md](./references/yaml-config.md#excel-config) for all options.

---

## Step 3 — Atlas Config (`atlas/<name>.yaml`)

**Location**: `src/jade/resources/default_cfg/benchmarks_pp/atlas/`  
**Purpose**: Define plots written to the output Word atlas document.

```yaml
Plot title:
  results:
    - Result name 1
  plot_type: binned_plot    # see plot gallery in docs
  title: My Plot Title
  x_label: Energy [MeV]
  y_labels: Flux [n/cm2/s]
  x: Energy
  y: Value
  # optional: expand_runs, xlimits, ylimits, v_lines, recs, subsets, plot_args
```

See [yaml-config.md](./references/yaml-config.md#atlas-config) for all options and the [plot gallery](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/dev/pp_gallery.html).

---

## Step 4 — Input Files

Input files live in external repositories — **not** in this repo.

| Case | Where to upload |
|------|----------------|
| Freely distributable | [IAEA open-benchmarks](https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks) |
| SINBAD-derived | SINBAD GitLab (contact davide.laghi@f4e.europa.eu) |
| Proprietary / F4E | F4E private GitLab (requires `F4E_GITLAB_TOKEN` env var) |

**Input file naming requirements per code** — see [where_inputs.rst](../../../docs/source/dev/add_benchmark/where_inputs.rst):

- **MCNP**: `<name>.i`; optional `wwinp`
- **D1S**: MCNP rules + `<name>_irrad` + `<name>_react`
- **OpenMC**: `settings.xml`, `geometry.xml`, `tallies.xml`, `materials.xml`; optional `libsource.so`, `weight_windows.h5`
- **Special dosimetry libraries** (MCNP/D1S): add their suffix to `DOSIMETRY_LIBS` in `src/jade/helper/constants.py`

---

## Step 5 — Documentation

1. Add a benchmark description RST file under `docs/source/benchmarks/benchdesc/`.
2. Update the overview table in `docs/source/benchmarks/computational.rst` or `experimental.rst`.
3. Reference the new file in `docs/source/benchmarks/benchmark_idx.rst`.

---

## Existing Benchmarks as Reference

Browse `src/jade/resources/default_cfg/benchmarks_pp/` to see working examples:
- Simple benchmark: `raw/mcnp/FNG-SS.yaml`
- Multi-result with sphere: `raw/mcnp/Sphere.yaml`
- Benchmark with code-specific subdirectories: `raw/openmc/`, `raw/d1s/`
