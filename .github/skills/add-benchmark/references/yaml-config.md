# YAML Config Reference for JADE Benchmarks

## Allowed Column Names

All tally DataFrame columns must use names from this list (defined in `src/jade/helper/constants.py`):

| Column Name | Notes |
|-------------|-------|
| `Energy` | |
| `Cells` | |
| `time` | |
| `tally` | |
| `Dir` | |
| `User` | |
| `Segments` | |
| `Multiplier` | |
| `Cosine` | |
| `Cor A` | not fully supported |
| `Cor B` | not fully supported |
| `Cor C` | not fully supported |

---

## Raw Config — Tally Modifiers

Applied per-tally, before concatenation. Chain multiple in series: `[[mod1, {args}], [mod2, {}]]`.

| Modifier | Args | Description |
|----------|------|-------------|
| `no_action` | — | Pass through unchanged |
| `volume` | — | Divide by volume (from `volumes.json` in benchmark inputs) |
| `mass` | — | Divide by mass (from `volumes.json` + OpenMC XML) |
| `scale` | `factor`: float \| int \| list | Multiply by factor |
| `lethargy` | — | Convert flux to per-unit-lethargy |
| `by_energy` | — | Convert flux to per-unit-energy |
| `by_bin` | `column_name`: str | Convert to per-unit-bin |
| `condense_groups` | `bins`: list of floats, `group_column`: str | Condense to coarser binning (SRSS errors) |
| `replace` | `column`: str, `values`: dict | Replace column values via dictionary mapping |
| `add_column` | `column`: str, `values`: list \| scalar | Add a new column |
| `add_column_with_dict` | `ref_column`: str, `values`: dict, `new_columns`: list | Add columns from dict keyed by ref_column |
| `keep_last_row` | — | Keep only the last row |
| `groupby` | `by`: str \| `'all'`, `action`: `sum`\|`mean`\|`max`\|`min` | Aggregate rows |
| `delete_cols` | `cols`: list of str | Remove columns |
| `format_decimals` | `decimals`: dict of {col: int} | Round column values |
| `tof_to_energy` | `m`: float (opt), `L`: float (opt) | Convert time-of-flight bins to Energy column |
| `select_subset` | `column`: str, `values`: list | Keep only rows matching values |
| `cumulative_sum` | `column`: str (opt), `norm`: bool (opt, default True) | Cumulative sum (optionally normalised) |
| `gaussian_broadening` | `fwhm_frac`: float \| list (opt, default 0.1) | Apply Gaussian broadening to Value column |

---

## Raw Config — Concatenation Options

Applied after all per-tally modifiers, when a result is assembled from multiple tallies.

| Option | Description |
|--------|-------------|
| `no_action` | Single tally — no concatenation needed |
| `sum` | Sum all tallies element-wise |
| `concat` | `pd.concat()` — stack rows |
| `subtract` | Subtract (in order provided) |
| `ratio` | Divide first tally by second (exactly 2 tallies) |

---

## Excel Config — Full Options

### Mandatory

| Key | Type | Description |
|-----|------|-------------|
| `results` | list[str] | Result names from raw config |
| `comparison_type` | str | `absolute` \| `percentage` \| `ratio` \| `chi_squared` |
| `table_type` | str | `simple` \| `pivot` \| `chi_squared` |
| `x` | str | Column for x-axis |
| `y` | str | Column for y-axis |

### Optional

| Key | Type | Description |
|-----|------|-------------|
| `value` | str | Pivot column (pivot tables only) |
| `add_error` | bool | Include error columns |
| `conditional_formatting` | dict | `{red: N, orange: N, yellow: N}` thresholds |
| `change_col_names` | dict | Rename columns before output |
| `subsets` | list[dict] | Per-result row filtering: `[{result: name, values: {col: [vals]}}]` |

---

## Atlas Config — Full Options

### Mandatory

| Key | Type | Description |
|-----|------|-------------|
| `results` | list[str] | Result names from raw config |
| `plot_type` | str | See [plot gallery](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/dev/pp_gallery.html) |
| `title` | str | Plot title |
| `x_label` | str | X-axis label |
| `y_labels` | str \| list | Y-axis label(s) |
| `x` | str | Column for x-axis (from `ALLOWED_COLUMN_NAMES`) |
| `y` | str | Column for y-axis (from `ALLOWED_COLUMN_NAMES`) |

### Optional

| Key | Type | Description |
|-----|------|-------------|
| `expand_runs` | bool (default true) | One plot per run/case |
| `additional_labels` | dict | Text boxes: `{major: [(text, x)], minor: [(text, x)]}` |
| `v_lines` | dict | Vertical lines: `{major: [x1, x2], minor: [x3]}` |
| `plot_args` | dict | Plot-type specific arguments |
| `recs` | list | Coloured regions: `[(name, colour, x_min, x_max)]` |
| `subsets` | list[dict] | Per-result row filtering |
| `select_runs` | str | Regex to filter cases/runs |
| `xlimits` | tuple | `[x_min, x_max]` |
| `ylimits` | tuple | `[y_min, y_max]` |
