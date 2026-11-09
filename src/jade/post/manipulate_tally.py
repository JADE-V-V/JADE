from __future__ import annotations

import logging
import math

import numpy as np
import pandas as pd

from jade.config.excel_config import ComparisonType
from jade.config.raw_config import TallyConcatOption, TallyModOption

logger = logging.getLogger(__name__)


# --- functions to modify tallies ---
def by_lethargy(tally: pd.DataFrame) -> pd.DataFrame:
    """Convert values by energy into values by unit lethargy."""

    flux = tally["Value"].values.astype(float)
    # Energies for lethargy computation
    # If the result is coarse binned (prior condense_groups applied), Lower and Upper energy columns are required to compute the lethargy
    if "Lower energy" in tally.columns and "Upper energy" in tally.columns:
        lower_bounds = np.array(tally["Lower energy"].values)
        upper_bounds = np.array(tally["Upper energy"].values)
        flux = flux / np.log(upper_bounds / lower_bounds)  # normalize by lethargy
    else:  # if no prior condense_groups was applied, read directly the energy column
        ergs = tally["Energy"].values
        if ergs.dtype == object:
            logger.debug(
                "Coarse binned results require the inclusion of 'Lower energy' and 'Upper energy' columns in the csv results to normalize by lethargy."
            )
        energies = [1e-10]
        energies.extend(ergs.astype(float))
        flux = flux / np.log(
            np.array(energies[1:]) / np.array(energies[:-1])
        )  # normalize by lethargy

    tally["Value"] = flux
    return tally


def by_energy(tally: pd.DataFrame) -> pd.DataFrame:
    """Convert values by energy into values by unit energy."""
    return divide_by_bin(tally, "Energy")


def divide_by_bin(tally: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convert values by time into values by unit time."""
    bins = tally[column_name].values
    flux = tally["Value"].values.astype(float)
    energy = column_name == "Energy"

    if "Lower energy" in tally.columns and "Upper energy" in tally.columns:
        lower_bounds = np.array(tally["Lower energy"].values)
        upper_bounds = np.array(tally["Upper energy"].values)
        flux = flux / np.abs(upper_bounds - lower_bounds)  # normalize by bin width
    else:
        if energy and bins.dtype == object:
            logger.debug(
                "Coarse binned results require the inclusion of 'Lower energy' and 'Upper energy' columns in the csv results to normalize by energy."
            )
        bins = [1e-10]
        bins.extend(tally[column_name].values.astype(float))
        flux = flux / np.abs(
            np.array(bins[1:]) - np.array(bins[:-1])
        )  # normalize by bin width

    tally["Value"] = flux
    return tally


def condense_groups(
    tally: pd.DataFrame, bins: list[float] | None = None, group_column: str = "Energy"
) -> pd.DataFrame:
    """Condense the tally into groups. Mostly used to obtain coarser energy groups.
    If no values are ancountered in a group the group is not included in the output.

    Parameters
    ----------
    tally : pd.DataFrame
        tally dataframe to modify
    bins : list[float], optional
        bin values of the groups. By default None
    group_column : str, optional
        the column onto which perform the grouping, by default "Energy"

    Returns
    -------
    pd.DataFrame
        modified tally
    """
    tally["abs err"] = tally["Error"] * tally["Value"]
    # this divides the entries in coarse energy bins

    tally["coarse_bin"] = pd.cut(tally[group_column], bins=bins, right=False)
    tally = tally.drop(columns=[group_column])
    tally[group_column] = tally["coarse_bin"].apply(
        lambda x: f"{x.left:g} - {x.right:g}" if pd.notna(x) else np.nan
    )
    """
    labels = [f"{bins[i]:g} - {bins[i+1]:g}" for i in range(len(bins) - 1)]

    tally[group_column] = pd.cut(
        tally[group_column],
        bins=bins,
        right=False,
        labels=labels,
    )
    """
    del tally["coarse_bin"]
    grouped = tally.groupby(group_column, observed=False).agg(
        {"Value": "sum", "abs err": lambda x: math.sqrt((x**2).sum())}
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        grouped["Error"] = grouped["abs err"] / grouped["Value"]
    del grouped["abs err"]
    # drop zero values
    grouped = grouped[grouped["Value"] != 0].reset_index()
    grouped[["Lower energy", "Upper energy"]] = (
        grouped["Energy"].str.split(" - ", expand=True).astype(float)
    )
    return grouped


def scale(
    tally: pd.DataFrame, factor: float | list = 1, column: str = "Value"
) -> pd.DataFrame:
    """Scale the tally values."""
    if isinstance(factor, list):
        factor2apply = np.array(factor)
    else:
        factor2apply = float(factor)
    tally[column] = tally[column] * factor2apply
    return tally


def no_action(tally: pd.DataFrame) -> pd.DataFrame:
    """Do nothing to the tally."""
    return tally


def cooling_time(tally: pd.DataFrame, shutdown_time: float) -> pd.DataFrame:
    """Select endpoints strictly after shutdown and express time since shutdown.

    All times use seconds. Values and relative errors are unchanged; this is
    an origin change, not a time-bin integration or interpolation. An output
    endpoint must exist at the configured shutdown time. This check does not
    establish that irradiation actually ended there.
    """
    tolerance = 1e-6
    if not math.isfinite(shutdown_time) or shutdown_time < 0:
        raise ValueError("shutdown_time must be finite and nonnegative")
    times = tally["time"].to_numpy(dtype=float)
    if not np.isfinite(times).all() or not (np.diff(times) > 0).all():
        raise ValueError("Time endpoints must be finite and strictly increasing")
    if not (np.abs(times - shutdown_time) <= tolerance).any():
        raise ValueError(f"No output endpoint at shutdown_time={shutdown_time} s")
    cooling = tally.loc[tally["time"] > shutdown_time + tolerance].copy()
    if cooling.empty:
        raise ValueError("No output endpoints after shutdown")
    cooling["time"] -= shutdown_time
    return cooling.reset_index(drop=True)


def select_subset(tally: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    """Select a subset of the tally based on the provided column and values."""
    return tally.set_index(column).loc[values].reset_index()


def replace_column(
    tally: pd.DataFrame, column: str | None = None, values: dict | None = None
) -> pd.DataFrame:
    """Replace the values of a column based on the provided dictionary."""
    tally[column] = tally[column].replace(values)
    return tally


def add_column(tally: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    """Add a new column to the tally with the provided values."""
    tally[column] = values
    return tally


def add_column_with_dict(
    tally: pd.DataFrame, ref_column: str, values: dict, new_columns: list[str]
) -> pd.DataFrame:
    """Add a new column to the tally with the provided values."""
    # create a new column with the values from the dictionary
    for i, new_column in enumerate(new_columns):
        vals = []
        for idx, row in tally.iterrows():
            key = row[ref_column]
            vals.append(values[key][i])
        tally[new_column] = vals
    return tally


def keep_last_row(tally: pd.DataFrame) -> pd.DataFrame:
    """Keep only the last row of the tally."""
    return tally.iloc[-1:]


def groupby(tally: pd.DataFrame, by: str, action: str) -> pd.DataFrame:
    """Group the tally by the group_column."""
    # Exclude the error column from the manipulation. The errror needs to be recomputed
    # as the squared root of the sum of the squared errors.
    if by not in tally.columns and by != "all":
        logger.debug(f"Groupby column {by} not found in the tally")
        return tally

    if by == "all":
        grouped = tally
        # Error propagation considering that tally["Error"] are relative errors
        # Valid both for sum and mean
        error = pd.Series(
            np.sqrt(((tally["Error"] * tally["Value"]) ** 2).sum())
            / tally["Value"].sum()
            if tally["Value"].sum() != 0
            else 0,
            name="Error",
        )
    else:
        value_df = tally.set_index(by)["Value"]
        error_df = tally.set_index(by)["Error"]
        rows = []
        for idx_val in error_df.index.unique():
            subset_error = error_df.loc[idx_val]
            subset_value = value_df.loc[idx_val]
            # Error propagation considering that tally["Error"] are relative errors
            # Valid both for sum and mean
            err = (
                np.sqrt(np.sum((subset_error * subset_value) ** 2)) / subset_value.sum()
                if subset_value.sum() != 0
                else 0
            )
            rows.append(err)
        error = pd.Series(rows, name="Error")
        grouped = tally.groupby(by, sort=False)

    if action == "sum":
        df = grouped.sum()
        # Application of the computed error propagation
        df["Error"] = error.values
    elif action == "mean":
        df = grouped.mean()
        # Application of the computed error propagation
        df["Error"] = error.values
    elif action == "max":
        # Preserve Error of the row defining the maximum Value
        idx = tally.groupby(by, sort=False)["Value"].idxmax()
        df = grouped.max()
        df["Error"] = tally.loc[idx, "Error"].values
    elif action == "min":
        # Preserve Error of the row defining the minimum Value
        idx = tally.groupby(by, sort=False)["Value"].idxmin()
        df = grouped.min()
        df["Error"] = tally.loc[idx, "Error"].values

    if isinstance(df, pd.Series):
        # a series has been created but we want a df
        df = df.to_frame().T
    else:
        df = df.reset_index()

    return df


def delete_cols(tally: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Delete the columns from the tally."""
    return tally.drop(columns=cols, errors="ignore")


def format_decimals(tally: pd.DataFrame, decimals: dict[str, int]) -> pd.DataFrame:
    """Fix the number of decimals for the data in each column of the tally."""
    for col, dec in decimals.items():
        try:
            tally[col] = tally[col].astype(float).round(dec)
        except KeyError:
            logger.debug(f"Column {col} not found in the tally.")
    return tally


def tof_to_energy(
    tally: pd.DataFrame, m: float = 939.5654133, L: float = 1
) -> pd.DataFrame:
    """
    Convert from TOF to energy domain. Time needs to be in seconds.

    Parameters
    ----------
    tally : pd.DataFrame
        tally dataframe to modify
    m: float
        mass of the particle in MeV/c^2. Default is neutron mass
    L: float
        distance between source and detection in meters. Default is 1.
    """
    c = 299792458  # m/s
    energy = m * (
        1 / np.sqrt(1 - (L / (c * tally["Time"].astype(float).values)) ** 2) - 1
    )
    tally["Energy"] = energy
    return tally


def cumulative_sum(
    tally: pd.DataFrame, column: str = "Value", norm: bool = True
) -> pd.DataFrame:
    """Compute the cumulative sum of the specified column.

    Parameters
    ----------
    tally : pd.DataFrame
        tally dataframe to modify
    column: str
        name of the column to compute the cumulative sum for. Default is "Value".
    """
    if column not in tally.columns:
        raise ValueError(f"Column {column} not found in the tally.")
    elif column == "Error":
        raise ValueError("Cumulative sum cannot be computed for the Error column.")
    original_tally = tally.copy()
    tally[column] = tally[column].cumsum()
    if column == "Value":
        # Error propagation considering that tally["Error"] are relative errors
        tally["Error"] = (
            np.sqrt(((tally["Error"] * original_tally[column]) ** 2).cumsum())
            / tally[column]
        )
    if norm:
        # Normalize in percentage to the last value (total sum)
        tally[column] = tally[column] / tally[column].iloc[-1] * 100
        if column == "Value":
            tally["Error"] = np.sqrt(tally["Error"] ** 2 + tally["Error"].iloc[-1] ** 2)
    return tally


def gaussian_broadening(
    tally: pd.DataFrame, column: str, bins: dict, integral: bool = False
) -> pd.DataFrame:
    """Apply Gaussian broadening to the tally.

    Parameters
    ----------
    tally : pd.DataFrame
        tally dataframe to modify
    column : str
        name of the column to use for Gaussian broadening ("Energy", or "Time")
    bins : dict
        Dictionary of bins for the specified column
    integral : bool, optional
        If true, divide bin totals by their widths before broadening and
        multiply by the destination widths afterward. The first lower edge is
        1e-10, consistent with the existing Gaussian quadrature.
    """
    if not isinstance(integral, bool):
        raise TypeError("integral must be a boolean")
    if integral:
        widths = np.diff(tally[column].to_numpy(dtype=float), prepend=1e-10)
        if not np.isfinite(widths).all() or np.any(widths <= 0):
            raise ValueError(
                "Integral bin edges must be finite and increasing from 1e-10"
            )
        # Normalize per bin width
        input_values = tally["Value"].to_numpy(dtype=float) / widths

    total_bin = []
    hist_bins = [0.0]
    broadened_values = np.zeros(len(tally), dtype=float)
    broadened_errors = np.zeros(len(tally), dtype=float)
    # Iterate over all bins specified in the bins dictionary
    for bin, value in bins.items():
        broad_energies = tally[column][
            (tally[column] <= float(bin)) & (tally[column] > hist_bins[-1])
        ].tolist()
        flag = False
        # Check for scaling type in the current bin
        if "no_scaling" in value:
            scaling = "no_scaling"
            scale = 1
            flag = True
        elif "linear" in value:
            scaling = "linear"
            s = 1
            flag = True
        elif "square" in value:
            scaling = "square"
            s = 2
            flag = True
        elif "square_root" in value:
            scaling = "square_root"
            s = 0.5
            flag = True
        if not flag:
            raise ValueError(
                f"Unknown scaling factor option: {value}. The scaling factor type must be one of 'no_scaling', 'linear', 'square', or 'square_root'."
            )
        if scaling != "no_scaling":
            try:
                ref = value[scaling]["Ref"]
            except KeyError:
                raise ValueError(
                    f"Reference value (energy or time, depending on the column parameter) for scaling (Ref) not found for bin {bin}, scaling type {scaling}. When using this scaling type (different to 'no_scaling'), Ref (bin value at the peak maximum) must be specified."
                )
        try:
            fwhm_frac = value[scaling]["fwhm_frac"]
            if isinstance(fwhm_frac, float):
                fwhm_frac = [fwhm_frac] * len(broad_energies)
            elif isinstance(fwhm_frac, list) and len(fwhm_frac) != len(broad_energies):
                raise ValueError(
                    "Length of FWHM fraction list must match the number of energy bins of the tally within the indicated energy range."
                )
            elif not isinstance(fwhm_frac, (list, float)):
                raise ValueError("FWHM fraction must be a float or a list of floats.")
        except KeyError:
            # If the scaling type is not found as a key in the energies dictionary (only a string is present), use the default FWHM fraction of 0.10 (10%) for all energy bins.
            fwhm_frac = [0.10] * len(broad_energies)
            logger.warning(
                f"FWHM fraction not found for bin {bin}, scaling type {scaling}. Using default FWHM fraction of 0.10 for all affected energy bins."
            )
        total_bin.append(broad_energies)

        Eb = tally[column].values.astype(float)
        Yb = np.zeros(len(tally), dtype=float)
        Errb = np.zeros(len(tally), dtype=float)
        all_widths = np.diff(np.array(Eb), prepend=1e-10)

        # Select the values and errors for the current bin range
        broad_values = tally["Value"][
            (tally[column] <= float(bin)) & (tally[column] > hist_bins[-1])
        ].tolist()
        if integral:
            broad_values = input_values[
                (tally[column] <= float(bin)) & (tally[column] > hist_bins[-1])
            ].tolist()
        broad_errors = tally["Error"][
            (tally[column] <= float(bin)) & (tally[column] > hist_bins[-1])
        ].tolist()
        broad_sigma = (
            np.array(fwhm_frac) * broad_energies / (2 * np.sqrt(2 * np.log(2)))
        )
        broad_widths = all_widths[
            (tally[column] <= float(bin)) & (tally[column] > hist_bins[-1])
        ]

        # Apply Gaussian broadening to the current bin range
        for Ei, si, Yi, Erri, bw in zip(
            broad_energies, broad_sigma, broad_values, broad_errors, broad_widths
        ):
            if Yi == 0:
                continue
            if si == 0:
                idx = np.flatnonzero(Eb == Ei)[0]
                Yb[idx] += Yi
                Errb[idx] += (Erri * Yi) ** 2
                continue
            if scaling != "no_scaling":
                # Compute the scaling factor for the current bin
                scale = (Ei / ref) ** s
            k = np.exp(-0.5 * ((Eb - Ei) / (scale * si)) ** 2) / (
                si * np.sqrt(2 * np.pi) * scale
            )
            # Apply the Gaussian kernel to the current bin
            Yb += Yi * k * bw
            Errb += (Erri * Yi * k * bw) ** 2

        broadened_values += Yb
        broadened_errors += Errb
        hist_bins.append(float(bin))
    # Assign the new broadened values to the tally
    tally["Value"] = broadened_values * widths if integral else broadened_values
    tally["Error"] = np.divide(
        np.sqrt(broadened_errors),
        broadened_values,
        out=np.zeros_like(broadened_values),
        where=broadened_values != 0,
    )

    # Raise warning if not all bins are covered by the gaussian broadening
    if sum(map(len, total_bin)) != tally[column].size:
        logger.warning(
            "Gaussian broadening is not being applied to the full spectra. The following energy bins are not covered by the defined broadening:"
            f"{set(tally[column]) - set(np.concatenate(total_bin))}"
        )

    return tally


def response_broadening(
    tally: pd.DataFrame,
    column: str,
    response_values: list | np.ndarray,
    response_bins: list | np.ndarray | None = None,
    scaling: dict | None = None,
    integral: bool = False,
) -> pd.DataFrame:
    """Broaden a differential tally using a normalized response function.

    Parameters
    ----------
    tally : pd.DataFrame
        Tally dataframe to modify.
    column : str
        name of the column to use for user-defined response function broadening ("Energy", or "Time")
    response_values : list or np.ndarray
        Response function values (user-defined)
    response_bins : list or np.ndarray, optional
        Bins at which response_values are sampled, in the same units
        as the tally bins. If None, uses tally bins (these must then be valid offsets).
    scaling : dict, optional
        Successive upper limits defining source-bin ranges.
        Each range accepts ``no_scaling``, ``linear``, ``square`` or
        ``square_root``, for example {4.0: {}, 8.0: {"linear": {"Ref": 3.0}}}.
        An empty range configuration means no scaling. Omitting scaling applies
        the unscaled response to the full spectrum. Supplied limits must be
        increasing; source bins above the last limit are not included.
        Ref is a positive reference value (peak maximum) in the units of ``column``.
    integral : bool, optional
        If true, integral values are assumed.
        Default is false, assuming differential values.
    """
    if not isinstance(integral, bool):
        raise TypeError("integral must be a boolean")
    Eb = tally[column].to_numpy(dtype=float)
    input_values = tally["Value"].to_numpy(dtype=float)
    input_errors = tally["Error"].to_numpy(dtype=float)

    edges = np.concatenate(([1e-10], Eb))
    all_widths = np.diff(edges)
    if integral:
        # Normalize per bin width
        input_values = input_values / all_widths

    broad_bins = np.asarray(Eb if response_bins is None else response_bins, dtype=float)
    density = np.asarray(response_values, dtype=float)
    if broad_bins.shape != density.shape:
        raise ValueError(
            "The response_bins and response_values array parameters must have the same length."
        )
    intervals = np.diff(broad_bins)
    area = np.sum((density[:-1] / 2 + density[1:] / 2) * intervals)

    density = density / area

    # First and second antiderivatives of the piecewise-linear response density.
    # The second allows integration over both source and destination bin intervals.
    cumulative = np.concatenate(
        ([0.0], np.cumsum((density[:-1] + density[1:]) * intervals / 2))
    )
    slopes = np.diff(density) / intervals
    second_cumulative = np.concatenate(
        (
            [0.0],
            np.cumsum(
                cumulative[:-1] * intervals
                + density[:-1] * intervals**2 / 2
                + slopes * intervals**3 / 6
            ),
        )
    )

    def response_second_integral(offsets: np.ndarray) -> np.ndarray:
        clipped = np.clip(offsets, broad_bins[0], broad_bins[-1])
        indices = np.clip(
            np.searchsorted(broad_bins, clipped, side="right") - 1,
            0,
            len(intervals) - 1,
        )
        delta = clipped - broad_bins[indices]
        # Beyond the response support, the first integral is constant, so the second is linear.
        return (
            second_cumulative[indices]
            + cumulative[indices] * delta
            + density[indices] * delta**2 / 2
            + slopes[indices] * delta**3 / 6
            + cumulative[-1] * np.maximum(offsets - broad_bins[-1], 0.0)
        )

    midpoints = edges[:-1] / 2 + edges[1:] / 2
    scaling_options = {"no_scaling", "linear", "square", "square_root"}
    bins = scaling or {Eb[-1]: {}}

    total_bin = []
    hist_bins = [0.0]
    broadened_values = np.zeros(len(tally), dtype=float)
    broadened_errors = np.zeros(len(tally), dtype=float)
    for bin, value in bins.items():
        if not math.isfinite(float(bin)) or float(bin) <= hist_bins[-1]:
            raise ValueError(
                "Response scaling range edges must be finite and increasing"
            )
        selected = (Eb <= float(bin)) & (Eb > hist_bins[-1])
        broad_energies = Eb[selected].tolist()
        config = value
        if not set(config).issubset(scaling_options):
            raise ValueError(f"Unknown scaling factor option: {config}")
        # Check scaling type for the current bin range
        if not config or "no_scaling" in config:
            scaling_type = "no_scaling"
            scale = 1.0
        elif "linear" in config:
            scaling_type = "linear"
            s = 1
        elif "square" in config:
            scaling_type = "square"
            s = 2
        elif "square_root" in config:
            scaling_type = "square_root"
            s = 0.5
        if scaling_type != "no_scaling":
            try:
                ref = float(config[scaling_type]["Ref"])
            except (KeyError, TypeError, ValueError):
                raise ValueError("Ref must be specified for response width scaling")
        total_bin.append(broad_energies)

        Yb = np.zeros(len(tally), dtype=float)
        Errb = np.zeros(len(tally), dtype=float)
        broad_values = input_values[selected].tolist()
        broad_errors = input_errors[selected].tolist()
        broad_widths = all_widths[selected]
        broad_midpoints = midpoints[selected]
        # Iterate over the bins within the current bin range to implement the response function broadening
        for Ei, midpoint, Yi, Erri, bw in zip(
            broad_energies, broad_midpoints, broad_values, broad_errors, broad_widths
        ):
            if Yi == 0:
                continue
            if scaling_type != "no_scaling":
                with np.errstate(over="ignore", invalid="ignore"):
                    scale = (midpoint / ref) ** s
            # Ei and Ei - bw bound the source bin; edges bound every destination bin.
            # All four edge differences are needed to average over both intervals.
            # Averaging over both intervals ensures better approximation of the response function over the source bin
            source_lower = Ei - bw
            upper_from_lower = (edges[1:] - source_lower) * scale
            upper_from_upper = (edges[1:] - Ei) * scale
            lower_from_lower = (edges[:-1] - source_lower) * scale
            lower_from_upper = (edges[:-1] - Ei) * scale
            # Divide by scale and by both widths for bin averaging.
            k = np.maximum(
                response_second_integral(upper_from_lower)
                - response_second_integral(upper_from_upper)
                - response_second_integral(lower_from_lower)
                + response_second_integral(lower_from_upper),
                0.0,
            ) / (scale * bw * all_widths)
            k[
                (lower_from_upper >= broad_bins[-1])
                | (upper_from_lower <= broad_bins[0])
            ] = 0.0
            # Apply the response function broadening
            Yb += Yi * k * bw
            Errb += (Erri * Yi * k * bw) ** 2
        broadened_values += Yb
        broadened_errors += Errb
        hist_bins.append(float(bin))

    # If integral tally values were provided, revert the bin normalization applied at the beginning of the function
    tally["Value"] = broadened_values * all_widths if integral else broadened_values
    tally["Error"] = np.divide(
        np.sqrt(broadened_errors),
        broadened_values,
        out=np.zeros_like(broadened_values),
        where=broadened_values != 0,
    )
    if sum(map(len, total_bin)) != tally[column].size:
        logger.warning(
            "Response broadening is not being applied to the full spectra. "
            "The following bins are not covered by the defined broadening: %s",
            set(Eb) - set(np.concatenate(total_bin)),
        )
    return tally


def volume(tally: pd.DataFrame, volumes: dict[int, float]) -> pd.DataFrame:
    """Volume divisor function

    Parameters
    ----------
    tally : pd.DataFrame
        Tally to be modified
    volumes : dict[int, float]
        Cell volumes dictionary

    Returns
    -------
    tally : pd.DataFrame
        Modified tally
    """
    if "Cells" in tally:
        cells = tally.Cells.unique()
        for cell in cells:
            tally["Value"] = np.where(
                (tally["Cells"] == cell),
                tally["Value"] / volumes[cell],
                tally["Value"],
            )
    return tally


def mass(tally: pd.DataFrame, masses: dict[int, float]) -> pd.DataFrame:
    """Volume divisor function

    Parameters
    ----------
    tally : pd.DataFrame
        Tally to be modified
    masses : dict[int, float]
        Cell masses dictionary

    Returns
    -------
    tally : pd.DataFrame
        Modified tally
    """
    if "Cells" in tally:
        cells = tally.Cells.unique()
        for cell in cells:
            tally["Value"] = np.where(
                (tally["Cells"] == cell),
                tally["Value"] / masses[cell],
                tally["Value"],
            )
    return tally


MOD_FUNCTIONS = {
    TallyModOption.COOLING_TIME: cooling_time,
    TallyModOption.LETHARGY: by_lethargy,
    TallyModOption.SCALE: scale,
    TallyModOption.RESPONSE_BROADENING: response_broadening,
    TallyModOption.NO_ACTION: no_action,
    TallyModOption.BY_ENERGY: by_energy,
    TallyModOption.BY_BIN: divide_by_bin,
    TallyModOption.CONDENSE_GROUPS: condense_groups,
    TallyModOption.REPLACE: replace_column,
    TallyModOption.ADD_COLUMN: add_column,
    TallyModOption.ADD_COLUMN_WITH_DICT: add_column_with_dict,
    TallyModOption.KEEP_LAST_ROW: keep_last_row,
    TallyModOption.GROUPBY: groupby,
    TallyModOption.DELETE_COLS: delete_cols,
    TallyModOption.FORMAT_DECIMALS: format_decimals,
    TallyModOption.TOF_TO_ENERGY: tof_to_energy,
    TallyModOption.SELECT_SUBSET: select_subset,
    TallyModOption.CUMULATIVE_SUM: cumulative_sum,
    TallyModOption.GAUSSIAN_BROADENING: gaussian_broadening,
    TallyModOption.VOLUME: volume,
    TallyModOption.MASS: mass,
}


# --- functions to combine tallies ---
def sum_tallies(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Sum all tallies. Value is sum, rel error is recomputed"""
    value = tallies[0]["Value"]
    error = tallies[0]["Error"]
    for tally in tallies[1:]:
        value, error = compare_data(
            value,
            -tally["Value"],
            error,
            tally["Error"],
            ComparisonType.ABSOLUTE,
            ignore_index=True,
        )  # Use of the substraction function with a negative sign in the second value to perform a sum

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = error

    return df


def subtract_tallies(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Subtract all tallies."""
    value = tallies[0]["Value"]
    error = tallies[0]["Error"]
    for tally in tallies[1:]:
        value, error = compare_data(
            value,
            tally["Value"],
            error,
            tally["Error"],
            ComparisonType.ABSOLUTE,
            ignore_index=True,
        )

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = error

    return df


def concat_tallies(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all tallies."""
    return pd.concat(tallies)


def no_concat(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Do nothing to the tallies."""
    assert len(tallies) == 1
    return tallies[0]


def ratio(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Ratio of the tallies."""
    if len(tallies) != 2:
        raise ValueError("Only two tallies can be used for ratio")

    value, error = compare_data(
        tallies[1]["Value"],
        tallies[0]["Value"],
        tallies[1]["Error"],
        tallies[0]["Error"],
        ComparisonType.RATIO,
        ignore_index=True,
    )

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = error

    return df


CONCAT_FUNCTIONS = {
    TallyConcatOption.SUM: sum_tallies,
    TallyConcatOption.CONCAT: concat_tallies,
    TallyConcatOption.NO_ACTION: no_concat,
    TallyConcatOption.SUBTRACT: subtract_tallies,
    TallyConcatOption.RATIO: ratio,
}


def compare_data(
    val1: pd.Series,
    val2: pd.Series,
    err1: pd.Series,
    err2: pd.Series,
    comparison_type: ComparisonType,
    ignore_index=False,
) -> tuple[pd.Series | np.ndarray, pd.Series | np.ndarray]:
    """Returns the values and propagated errors for the chosen comparison between two data sets."""

    error = []
    if ignore_index:
        val1 = val1.values
        val2 = val2.values

    if comparison_type == ComparisonType.ABSOLUTE:
        value = val1 - val2
        for v1, v2, e1, e2 in zip(val1, val2, err1, err2):
            if v1 != v2:
                error.append(
                    np.abs(np.sqrt((v1 * e1) ** 2 + (v2 * e2) ** 2) / (v1 - v2))
                )  # relative error propagation for substraction
            else:
                error.append(
                    e1 + e2
                )  # Conservative choice, only applied if the values are equal
    elif comparison_type == ComparisonType.PERCENTAGE:
        value = (val1 - val2) / val1 * 100
        for v1, v2, e1, e2 in zip(val1, val2, err1, err2):
            if v1 != v2:
                error.append(
                    np.abs(np.sqrt((v2 * e1) ** 2 + (v2 * e2) ** 2) / (v1 - v2))
                )  # relative error propagation for percentage
            else:
                error.append(
                    e1 + e2
                )  # Conservative choice, only applied if the values are equal
    elif comparison_type == ComparisonType.RATIO:
        value = val2 / val1  # reference / target
        error = np.sqrt(err1**2 + err2**2)  # relative error propagation for ratio

    elif comparison_type == ComparisonType.CHI_SQUARED:
        # for chi squared evaluation the assumption is that val 1 is the experimental
        # result. In order for the value to be simulation independent and in the
        # assumption that the simulation error are low, only the experimental uncertainty
        # is considered
        value = (val2 / val1 - 1) ** 2 / err1**2
        error = err1

    else:
        raise NotImplementedError(
            f"Comparison type: {comparison_type} is not implemented"
        )

    if not ignore_index:
        error = pd.Series(error)
        error.index = val1.index
    else:
        error = np.array(error)
    return value, error
