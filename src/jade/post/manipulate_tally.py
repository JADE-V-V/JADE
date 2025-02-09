from __future__ import annotations

import numpy as np
import pandas as pd

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
    # Energies for lethargy computation
    energies = tally["Energy"].values
    flux = tally["Value"].values

    ergs = [1e-10]  # Additional "zero" energy for lethargy computation
    ergs.extend(energies.tolist())
    ergs = np.array(ergs)

    flux = flux / (ergs[1:] - ergs[:-1])
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
        df = df.sum()
        df["Error"] = df["abs err"] / df["Value"]
        del df["abs err"]
        del df[group_column]  # avoid warning
        df[group_column] = f"{min_e} - {max_e}"
        rows.append(df)
        min_e = max_e
    return pd.DataFrame(rows).dropna()


def scale(tally: pd.DataFrame, factor: int | float = 1) -> pd.DataFrame:
    """Scale the tally values."""
    tally["Value"] = tally["Value"] * factor
    return tally


def no_action(tally: pd.DataFrame) -> pd.DataFrame:
    """Do nothing to the tally."""
    return tally


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


def keep_last_row(tally: pd.DataFrame) -> pd.DataFrame:
    """Keep only the last row of the tally."""
    return tally.iloc[-1:]


def groupby(tally: pd.DataFrame, by: str, action: str) -> pd.DataFrame:
    """Group the tally by the group_column."""
    # Exclude the error column from the manipulation. The errror needs to be recomputed
    # as the squared root of the sum of the squared errors.
    error_df = tally.set_index(by)["Error"]
    rows = {}
    for idx_val in error_df.index.unique():
        subset = error_df.loc[idx_val]
        error = np.sqrt(np.sum(subset**2))
        rows[idx_val] = error
    error_series = pd.Series(rows, name="Error")

    if action == "sum":
        df = tally.groupby(by).sum()
    elif action == "mean":
        df = tally.groupby(by).mean()
    elif action == "max":
        df = tally.groupby(by).max()
    elif action == "min":
        df = tally.groupby(by).min()

    df["Error"] = error_series

    return df.reset_index()


def delete_cols(tally: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Delete the columns from the tally."""
    return tally.drop(columns=cols)


MOD_FUNCTIONS = {
    TallyModOption.LETHARGY: by_lethargy,
    TallyModOption.SCALE: scale,
    TallyModOption.NO_ACTION: no_action,
    TallyModOption.BY_ENERGY: by_energy,
    TallyModOption.CONDENSE_GROUPS: condense_groups,
    TallyModOption.REPLACE: replace_column,
    TallyModOption.ADD_COLUMN: add_column,
    TallyModOption.KEEP_LAST_ROW: keep_last_row,
    TallyModOption.GROUPBY: groupby,
    TallyModOption.DELETE_COLS: delete_cols,
}


# --- functions to combine tallies ---
def sum_tallies(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Sum all tallies. Value is sum, rel error is recomputed"""
    value = tallies[0]["Value"]
    tot_err = tallies[0]["Error"] * value
    for tally in tallies[1:]:
        value = value + tally["Value"]
        tot_err = tot_err + tally["Error"] * tally["Value"]

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = tot_err / value

    return df


def subtract_tallies(tallies: list[pd.DataFrame]) -> pd.DataFrame:
    """Subtract all tallies."""
    value = tallies[0]["Value"]
    tot_err = tallies[0]["Error"] ** 2
    for tally in tallies[1:]:
        value = value - tally["Value"]
        tot_err = tot_err + tally["Error"] ** 2

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = np.sqrt(tot_err)  # This may be wrong

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
    value = tallies[0]["Value"]
    tot_err = tallies[0]["Error"] ** 2
    for tally in tallies[1:]:
        value = value / tally["Value"]
        tot_err = tot_err + (tally["Error"] / tally["Value"]) ** 2

    df = tallies[0].copy()
    df["Value"] = value
    df["Error"] = np.sqrt(tot_err)  # This may be wrong

    return df


CONCAT_FUNCTIONS = {
    TallyConcatOption.SUM: sum_tallies,
    TallyConcatOption.CONCAT: concat_tallies,
    TallyConcatOption.NO_ACTION: no_concat,
    TallyConcatOption.SUBTRACT: subtract_tallies,
    TallyConcatOption.RATIO: ratio,
}
