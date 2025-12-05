from __future__ import annotations

import logging
import math

import numpy as np
import pandas as pd

from jade.config.excel_config import ComparisonType
from jade.config.raw_config import TallyConcatOption, TallyModOption


# --- functions to modify tallies ---
def by_lethargy(tally: pd.DataFrame) -> pd.DataFrame:
    """Convert values by energy into values by unit lethargy."""
    # Energies for lethargy computation
    energies = tally["Energy"].values
    flux = tally["Value"].values

    ergs = [1e-10]  # Additional "zero" energy for lethargy computation
    ergs.extend(energies.tolist())
    ergs = np.array(ergs)

    flux = flux / np.log(ergs[1:] / ergs[:-1])

    tally["Value"] = flux
    return tally


def by_energy(tally: pd.DataFrame) -> pd.DataFrame:
    """Convert values by energy into values by unit energy."""
    return divide_by_bin(tally, "Energy")


def divide_by_bin(tally: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convert values by time into values by unit time."""
    bins = tally[column_name].values
    flux = tally["Value"].values

    bin_intervals = [1e-10]  # Additional "zero" bin
    bin_intervals.extend(bins.tolist())
    bin_intervals = np.array(bin_intervals)

    flux = flux / np.abs((bin_intervals[1:] - bin_intervals[:-1]))
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
    tally[group_column] = tally["coarse_bin"].apply(
        lambda x: f"{x.left:g} - {x.right:g}"
    )
    del tally["coarse_bin"]
    grouped = tally.groupby(group_column, observed=False).agg(
        {"Value": "sum", "abs err": lambda x: math.sqrt((x**2).sum())}
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        grouped["Error"] = grouped["abs err"] / grouped["Value"]
    del grouped["abs err"]
    # drop zero values
    grouped = grouped[grouped["Value"] != 0]
    return grouped.reset_index()


def scale(
    tally: pd.DataFrame, factor: int | float | list = 1, column: str = "Value"
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
        logging.debug(f"Groupby column {by} not found in the tally")
        return tally

    if by == "all":
        grouped = tally
        # Error propagation considering that tally["Error"] are relative errors
        # Valid both for sum and mean
        error = pd.Series(
            np.sqrt(((tally["Error"] * tally["Value"]) ** 2).sum())
            / tally["Value"].sum(),
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
        df.reset_index(inplace=True)

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
            logging.debug(f"Column {col} not found in the tally.")
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
    tally: pd.DataFrame, fwhm_frac: float | list[float] = 0.10
) -> pd.DataFrame:
    """Apply Gaussian broadening to the tally.

    Parameters
    ----------
    tally : pd.DataFrame
        tally dataframe to modify
    fwhm_frac: float | list[float]
        FWHM fraction(s) to apply. Default is 0.10 (10%) for all energy bins.
    """
    # If fwhm_frac is a single float, convert it to a list with the same length as the tally
    if isinstance(fwhm_frac, (float, int)):
        fwhm_frac = [float(fwhm_frac)] * len(tally["Energy"])
    # If fwhm_frac is a list, check that its length matches the number of rows in the tally
    elif isinstance(fwhm_frac, list):
        if len(fwhm_frac) != len(tally["Energy"]):
            raise ValueError(
                "Length of fwhm_frac list must match number of rows in tally."
            )
    else:
        raise ValueError("fwhm_frac must be a float or a list of floats.")

    Eb = tally["Energy"].values.astype(float)
    Yb = np.zeros_like(tally["Value"])
    Errb = np.zeros_like(tally["Error"])
    sigma = (
        np.array(fwhm_frac) * np.array(tally["Energy"]) / (2 * np.sqrt(2 * np.log(2)))
    )

    # Apply Gaussian broadening
    for Ei, si, Yi, Erri in zip(tally["Energy"], sigma, tally["Value"], tally["Error"]):
        if Yi == 0:
            continue
        width = 4 * si
        mask = (Eb >= Ei - width) & (Eb <= Ei + width)
        x = Eb[mask]
        k = np.exp(-0.5 * ((x - Ei) / si) ** 2)
        k /= k.sum()
        Yb[mask] += Yi * k
        Errb[mask] += (Erri * Yi * k) ** 2

    # Assign the new broadened values to the tally
    tally["Value"] = Yb
    tally["Error"] = np.sqrt(Errb) / Yb
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
            tally["Error"] = np.where(
                (tally["Cells"] == cell),
                tally["Error"] / volumes[cell],
                tally["Error"],
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
            tally["Error"] = np.where(
                (tally["Cells"] == cell),
                tally["Error"] / masses[cell],
                tally["Error"],
            )
    return tally


MOD_FUNCTIONS = {
    TallyModOption.LETHARGY: by_lethargy,
    TallyModOption.SCALE: scale,
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
                    np.sqrt((v1 * e1) ** 2 + (v2 * e2) ** 2) / (v1 - v2)
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
                    np.sqrt((v1 * v2 * e1) ** 2 + (v2 * e2) ** 2) / (v1 - v2)
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
