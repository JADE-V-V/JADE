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
    rows = []
    min_e = bins[0]
    for max_e in bins[1:]:
        # get the rows that have Energy between min_e and max_e
        df = tally[(tally[group_column] >= min_e) & (tally[group_column] < max_e)]
        # do the srt of sum of squares of absolute errors
        square_err = 0
        for _, row in df.iterrows():
            square_err += row["abs err"] ** 2
        srss_err = math.sqrt(square_err)
        df = df.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            # it is ok to get some NaN if value is zero
            df["Error"] = srss_err / df["Value"]
        del df["abs err"]
        del df[group_column]  # avoid warning
        df[group_column] = f"{min_e} - {max_e}"
        rows.append(df)
        min_e = max_e
    return pd.DataFrame(rows).dropna()


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
        error = np.sqrt((tally["Error"] ** 2).sum())
    else:
        error_df = tally.set_index(by)["Error"]
        rows = []
        for idx_val in error_df.index.unique():
            subset = error_df.loc[idx_val]
            err = np.sqrt(np.sum(subset**2))
            rows.append(err)
        error = pd.Series(rows, name="Error")
        grouped = tally.groupby(by, sort=False)

    if action == "sum":
        df = grouped.sum()
    elif action == "mean":
        df = grouped.mean()
    elif action == "max":
        df = grouped.max()
    elif action == "min":
        df = grouped.min()

    if isinstance(df, pd.Series):
        # a series has been created but we want a df
        df = df.to_frame().T
    else:
        df.reset_index(inplace=True)

    df["Error"] = error

    return df


def delete_cols(tally: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Delete the columns from the tally."""
    return tally.drop(columns=cols)


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
        value = (val2 / val1 - 1) ** 2 / (err1**2 + err2**2)
        error = [np.nan] * len(value)

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
