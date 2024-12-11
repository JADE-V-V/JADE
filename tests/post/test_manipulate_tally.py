from __future__ import annotations

import pandas as pd

from src.jade.post.manipulate_tally import (
    by_energy,
    by_lethargy,
    concat_tallies,
    no_action,
    no_concat,
    scale,
    sum_tallies,
)


def test_by_lethargy():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = by_lethargy(df.copy())
    assert (df["Energy"] == result["Energy"]).all()
    assert (df["Value"] != result["Value"]).all()


def test_by_energy():
    data = {"Energy": [15, 20, 35], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = by_energy(df.copy())
    assert (df["Value"] != result["Value"]).all()


def test_scale():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = scale(df.copy(), 2)
    expected_values = [20, 40, 60]
    assert result["Value"].tolist() == expected_values


def test_no_action():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = no_action(df.copy())
    assert result.equals(df)


def test_sum_tallies():
    data1 = {"Energy": [1, 2, 3], "Value": [10, 20, 30], "Error": [0.1, 0.2, 0.3]}
    data2 = {"Energy": [1, 2, 3], "Value": [5, 15, 25], "Error": [0.1, 0.2, 0.3]}
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    result = sum_tallies([df1, df2])
    expected_values = [15, 35, 55]
    expected_errors = [
        (10 * 0.1 + 5 * 0.1) / 15,
        (20 * 0.2 + 15 * 0.2) / 35,
        (30 * 0.3 + 25 * 0.3) / 55,
    ]
    assert result["Value"].tolist() == expected_values
    assert result["Error"].tolist() == expected_errors


def test_concat_tallies():
    data1 = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    data2 = {"Energy": [4, 5, 6], "Value": [40, 50, 60]}
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    result = concat_tallies([df1, df2])
    assert len(result) == len(df1) + len(df2)


def test_no_concat():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = no_concat([df])
    assert result.equals(df)
