from __future__ import annotations

import os
import shutil
from pathlib import Path

import pandas as pd

exp_res_folder = Path(
    r"R:\AC_ResultsDB\Jade\04_JADE_latest_root\Experimental_Results\Oktavian"
)
dest_folder = Path(r"D:\DATA\laghida\Desktop\oktavian")
bins = [0.01, 0.1, 1, 3.5, 10, 20]
columns = ["Energy", "Value", "Error"]


def condense_groups(
    tally: pd.DataFrame, bins: list[float] | None = None, group_column: str = "Energy"
) -> pd.DataFrame:
    """Condense the tally into groups. Mostly used to obtain coarser energy groups.

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
        _description_
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
        del df[group_column]
        df[group_column] = f"{min_e} - {max_e}"
        rows.append(df)
        min_e = max_e
    return pd.DataFrame(rows)


for case in os.listdir(exp_res_folder):
    case_folder = Path(exp_res_folder, case)
    for file in os.listdir(case_folder):
        if file.endswith(".csv"):
            pieces = file.split("_")
            case = "_".join(pieces[1:-1])
            if pieces[-1] == "21.csv":
                name = " Neutron flux.csv"
                coarse_name = " Coarse neutron flux.csv"
            else:
                pieces[-1] = "41.csv"
                name = " Gamma flux.csv"
                coarse_name = " Coarse gamma flux.csv"

            df = pd.read_csv(Path(case_folder, file))
            df.columns = columns

            new_name = "Oktavian_" + case + name
            new_coarse_name = "Oktavian_" + case + coarse_name

            df.to_csv(Path(dest_folder, new_name), index=False)
            condensed = condense_groups(df, bins)
            condensed.to_csv(Path(dest_folder, new_coarse_name), index=False)
