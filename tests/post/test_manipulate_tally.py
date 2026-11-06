from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from src.jade.post.manipulate_tally import (
    add_column,
    add_column_with_dict,
    by_energy,
    by_lethargy,
    concat_tallies,
    condense_groups,
    cumulative_sum,
    delete_cols,
    divide_by_bin,
    format_decimals,
    gaussian_broadening,
    groupby,
    mass,
    no_action,
    no_concat,
    ratio,
    replace_column,
    response_broadening,
    scale,
    select_subset,
    subtract_tallies,
    sum_tallies,
    tof_to_energy,
    volume,
)


def test_by_lethargy():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = by_lethargy(df.copy())
    assert (df["Energy"] == result["Energy"]).all()
    assert (
        result["Value"]
        == [10 / np.log(1 / 1e-10), 20 / np.log(2 / 1), 30 / np.log(3 / 2)]
    ).all()

    data = {
        "Energy": ["0.1 - 1", "1.1 - 2", "2.3 - 3"],
        "Value": [10, 20, 30],
        "Lower energy": [0.1, 1.1, 2.3],
        "Upper energy": [1, 2, 3],
    }
    df = pd.DataFrame(data)
    result = by_lethargy(df.copy())
    assert (df["Energy"] == result["Energy"]).all()
    assert (
        result["Value"]
        == [10 / np.log(1 / 0.1), 20 / np.log(2 / 1.1), 30 / np.log(3 / 2.3)]
    ).all()


def test_by_energy():
    data = {"Energy": [15, 20, 35], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = by_energy(df.copy())
    assert (
        result["Value"] == [10 / (15 - 1e-10), 20 / (20 - 15), 30 / (35 - 20)]
    ).all()

    data = {
        "Energy": ["10 - 15", "18 - 25", "25 - 35"],
        "Value": [10, 20, 30],
        "Lower energy": [10, 18, 25],
        "Upper energy": [15, 25, 35],
    }
    df = pd.DataFrame(data)
    result = by_energy(df.copy())
    assert (result["Value"] == [10 / (15 - 10), 20 / (25 - 18), 30 / (35 - 25)]).all()


def test_by_bin():
    data = {"Time": [15, 20, 35], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = divide_by_bin(df.copy(), "Time")
    assert (df["Value"] != result["Value"]).all()


def test_scale():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = scale(df.copy(), 2)
    expected_values = [20, 40, 60]
    assert result["Value"].tolist() == expected_values


def test_response_broadening(caplog):
    response_values, response_bins = [1.0, 1.0], [-1.0, 1.0]
    modes = [("no_scaling", None), ("linear", 1), ("square", 2), ("square_root", 0.5)]
    for column in ["Energy", "Time"]:
        tally = pd.DataFrame(
            {
                column: [2.0, 4.0, 6.0, 8.0, 10.0],
                "Value": [0, 1, 0, 0, 0],
                "Error": [0.2] * 5,
            }
        )
        for mode, exponent in modes:
            for factor in [1.0] if exponent is None else [0.5, 2.0]:
                scaling = (
                    None
                    if exponent is None
                    else {"10.0": {mode: {"Ref": 3.0 / factor ** (1 / exponent)}}}
                )
                half_width = 1 / factor
                expected = np.array(
                    [half_width / 8, 1 - half_width / 4, half_width / 8, 0, 0]
                )
                for integral in [False, True]:
                    source = tally.copy()
                    if integral:
                        source["Value"] *= 2
                    result = response_broadening(
                        source,
                        column,
                        response_values,
                        response_bins,
                        scaling=scaling,
                        integral=integral,
                    )
                    np.testing.assert_allclose(
                        result["Value"], expected * (2 if integral else 1), atol=1e-10
                    )
                    np.testing.assert_allclose(
                        result["Error"], [0.2, 0.2, 0.2, 0, 0], atol=1e-10
                    )
                    assert result["Value"].sum() == pytest.approx(2 if integral else 1)

    edges = np.array([1.0, 2.0, 3.0, 13.0, 23.0])
    widths = np.diff(np.r_[0.0, edges])
    transition = pd.DataFrame({"Time": edges, "Value": widths, "Error": [0.0] * 5})
    result = response_broadening(
        transition, "Time", [1.0, 1.0], [-0.1, 0.1], integral=True
    )
    np.testing.assert_allclose(
        result["Value"].to_numpy()[1:-1] / widths[1:-1], 1, atol=1e-10
    )

    caplog.clear()
    result = response_broadening(
        tally.copy(), column, response_values, response_bins, scaling={"2.0": {}}
    )
    np.testing.assert_allclose(result["Value"], 0)
    assert "not being applied to the full spectra" in caplog.text

    for scaling, message in [
        ({"10.0": {"linear": {}}}, "Ref must be specified"),
        ({"10.0": {"cubic": {}}}, "Unknown scaling factor option"),
    ]:
        with pytest.raises(ValueError, match=message):
            response_broadening(
                tally.copy(), column, response_values, response_bins, scaling=scaling
            )
    with pytest.raises(ValueError, match="same length"):
        response_broadening(tally.copy(), column, [1.0], [-1.0, 1.0])
    with pytest.raises(TypeError, match="integral must be a boolean"):
        response_broadening(pd.DataFrame(), "Time", [], integral="yes")


def test_replace_column():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = replace_column(df.copy(), "Value", {10: 5, 20: 15, 30: 25})
    expected_values = [5, 15, 25]
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
        np.sqrt((10 * 0.1) ** 2 + (5 * 0.1) ** 2) / 15,
        np.sqrt((20 * 0.2) ** 2 + (15 * 0.2) ** 2) / 35,
        np.sqrt((30 * 0.3) ** 2 + (25 * 0.3) ** 2) / 55,
    ]
    assert result["Value"].tolist() == expected_values
    assert result["Error"].tolist() == expected_errors


def test_subtract_tallies():
    data1 = {"Energy": [1, 2, 3], "Value": [10, 20, 30], "Error": [0.1, 0.2, 0.3]}
    data2 = {"Energy": [1, 2, 3], "Value": [5, 15, 25], "Error": [0.1, 0.2, 0.3]}
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    result = subtract_tallies([df1, df2])
    expected_values = [5, 5, 5]
    expected_errors = [
        np.sqrt((10 * 0.1) ** 2 + (5 * 0.1) ** 2) / 5,
        np.sqrt((20 * 0.2) ** 2 + (15 * 0.2) ** 2) / 5,
        np.sqrt((30 * 0.3) ** 2 + (25 * 0.3) ** 2) / 5,
    ]
    assert result["Value"].tolist() == expected_values
    assert result["Error"].tolist() == expected_errors


def test_ratio_tallies():
    data1 = {"Energy": [1, 2, 3], "Value": [10, 20, 30], "Error": [0.1, 0.2, 0.3]}
    data2 = {"Energy": [1, 2, 3], "Value": [5, 15, 25], "Error": [0.1, 0.2, 0.3]}
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    result = ratio([df1, df2])
    expected_values = [2, 4 / 3, 6 / 5]
    expected_errors = [
        np.sqrt((0.1) ** 2 + (0.1) ** 2),
        np.sqrt((0.2) ** 2 + (0.2) ** 2),
        np.sqrt((0.3) ** 2 + (0.3) ** 2),
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


def test_condense_groups():
    data = {
        "Energy": [1, 2, 3, 4],
        "Value": [10, 20, 30, 40],
        "Error": [0.1, 0.1, 0.2, 0.1],
    }
    df = pd.DataFrame(data)
    result = condense_groups(df.copy(), bins=[0, 3.1, 10])
    assert (result["Energy"] == ["0 - 3.1", "3.1 - 10"]).all()
    assert (result["Value"] == [60, 40]).all()
    err = 0
    val = 0
    df["abs err"] = df["Error"] * df["Value"]
    for i in range(3):
        err += df.iloc[i]["abs err"] ** 2
        val += df.iloc[i]["Value"]
    assert pytest.approx(result["Error"][0]) == math.sqrt(err) / val
    assert pytest.approx(result["Error"][1]) == 0.1
    assert (result["Lower energy"] == [0, 3.1]).all()
    assert (result["Upper energy"] == [3.1, 10]).all()

    result = condense_groups(df.copy(), bins=[0, 1, 3])
    assert len(result) == 1


def test_add_column():
    data = {"Energy": [1, 2, 3], "Value": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = add_column(df.copy(), "New", [1, 2, 3])
    assert (result["New"] == [1, 2, 3]).all()
    result = add_column(df.copy(), "another", 1)
    assert (result["another"] == [1, 1, 1]).all()


def test_add_column_with_dict():
    # Input DataFrame
    tally = pd.DataFrame({"Cases": ["A", "B", "C", "D"], "Value": [100, 200, 300, 400]})

    # Reference column and values dictionary
    ref_column = "Cases"
    values = {"A": [10, 1], "B": [15, 1], "C": [20, 1], "D": [25, 1]}
    new_columns = ["new_col1", "new_col2"]

    # Call the function
    result = add_column_with_dict(tally, ref_column, values, new_columns)

    # Expected DataFrame
    expected = pd.DataFrame(
        {
            "Cases": ["A", "B", "C", "D"],
            "Value": [100, 200, 300, 400],
            "new_col1": [10, 15, 20, 25],
            "new_col2": [1, 1, 1, 1],
        }
    )

    # Assert the result matches the expected DataFrame
    pd.testing.assert_frame_equal(result, expected)


def test_groupby(recwarn):
    data = {
        "Energy": [1, 1, 2, 2, 3, 3],
        "Value": [1, 2, 3, 4, 0, 0],
        "Error": [0.1, 0.2, 0.3, 0.1, 0.0, 0.0],
    }
    df = pd.DataFrame(data)

    result = groupby(df.copy(), "Energy", "sum")
    assert (result["Value"] == [3, 7, 0]).all()
    assert (
        result["Error"].iloc[0]
        == np.sqrt((0.1 * 1) ** 2 + (0.2 * 2) ** 2) / result["Value"].iloc[0]
    )
    result = groupby(df.copy(), "Energy", "mean")
    assert (result["Value"] == [1.5, 3.5, 0.0]).all()
    result = groupby(df.copy(), "Energy", "max")
    assert (result["Value"] == [2, 4, 0]).all()
    assert (result["Error"] == [0.2, 0.1, 0.0]).all()
    result = groupby(df.copy(), "Energy", "min")
    assert (result["Value"] == [1, 3, 0]).all()
    assert (result["Error"] == [0.1, 0.3, 0.0]).all()
    result = groupby(df.copy(), "all", "sum")
    assert result["Value"].iloc[0] == 10
    assert (
        result["Error"].iloc[0]
        == math.sqrt((0.1 * 1) ** 2 + (0.2 * 2) ** 2 + (0.3 * 3) ** 2 + (0.1 * 4) ** 2)
        / result["Value"].iloc[0]
    )
    assert len(result) == 1


def test_delete_cols():
    data = {
        "Energy": [1, 2, 3],
        "Value": [10, 20, 30],
        "Error": [0.1, 0.2, 0.3],
        "Another": [1, 2, 3],
    }
    df = pd.DataFrame(data)
    result = delete_cols(df.copy(), ["Error", "Another"])
    assert "Error" not in result.columns
    assert "Another" not in result.columns
    assert "Value" in result.columns
    assert "Energy" in result.columns


def test_format_decimals():
    data = {
        "Energy": [1, 2, 3],
        "Value": [10.456, 20.23, 30.905768],
        "Error": [0.199999, 0.2333, 0.34],
    }
    df = pd.DataFrame(data)
    result = format_decimals(df.copy(), {"Energy": 2, "Value": 1, "Error": 3})

    expected_data = {
        "Energy": [1.00, 2.00, 3.00],
        "Value": [10.5, 20.2, 30.9],
        "Error": [0.200, 0.233, 0.340],
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)


def test_tof_to_energy():
    data = {
        "Time": [1, 2, 3],
        "Value": [10, 20, 30],
        "Error": [0.1, 0.2, 0.3],
    }
    df = pd.DataFrame(data)
    tof_to_energy(df.copy())


def test_select_subset():
    data = {
        "Energy": [1, 2, 3, 4, 5],
        "Value": [10, 20, 30, 40, 50],
        "Error": [0.1, 0.2, 0.3, 0.4, 0.5],
    }
    df = pd.DataFrame(data)
    result = select_subset(df.copy(), "Energy", [1, 3])

    assert len(result) == 2


def test_cumulative_sum():
    data = {
        "Time": [1, 2, 3, 5],
        "Value": [10, 20, 30, 50],
        "Error": [0.1, 0.2, 0.3, 0.4],
    }
    df = pd.DataFrame(data)

    result = cumulative_sum(df.copy(), norm=False)
    expected_values = [10, 30, 60, 110]
    expected_error = [
        0.1,
        np.sqrt((0.1 * 10) ** 2 + (0.2 * 20) ** 2) / 30,
        np.sqrt((0.1 * 10) ** 2 + (0.2 * 20) ** 2 + (0.3 * 30) ** 2) / 60,
        np.sqrt((0.1 * 10) ** 2 + (0.2 * 20) ** 2 + (0.3 * 30) ** 2 + (0.4 * 50) ** 2)
        / 110,
    ]
    assert result["Time"].tolist() == data["Time"]
    assert result["Value"].tolist() == expected_values
    assert result["Error"].tolist() == expected_error

    result = cumulative_sum(df.copy(), column="Time")
    expected_values = [1 / 11 * 100, 3 / 11 * 100, 6 / 11 * 100, 100]
    for i in range(len(expected_error)):
        expected_error[i] = np.sqrt(expected_error[i] ** 2 + expected_error[-1] ** 2)
    assert result["Time"].tolist() == expected_values
    assert result["Value"].tolist() == data["Value"]
    assert result["Error"].tolist() == data["Error"]

    with pytest.raises(ValueError, match="Column NotAColumn not found in the tally"):
        cumulative_sum(df, column="NotAColumn")
    with pytest.raises(
        ValueError, match="Cumulative sum cannot be computed for the Error column"
    ):
        cumulative_sum(df, column="Error")


def test_gaussian_broadening(caplog):
    data = {
        "Energy": [1.0, 2.0, 4.0],
        "Value": [1.0, 2.0, 3.0],
        "Error": [0.1, 0.2, 0.3],
    }
    eref = 2.0
    fwhm_cases = [0.2, [0.1, 0.2, 0.3]]
    scaling_cases = [
        ("no_scaling", None),
        ("linear", 1),
        ("square", 2),
        ("square_root", 0.5),
    ]

    for scaling, exponent in scaling_cases:
        for fwhm_frac in fwhm_cases:
            tally = pd.DataFrame(data)
            scaling_config = {"fwhm_frac": fwhm_frac}
            if exponent is not None:
                scaling_config["Ref"] = eref

            result = gaussian_broadening(
                tally.copy(), "Energy", {"4.0": {scaling: scaling_config}}
            )

            energies = np.array(data["Energy"])
            source_widths = np.diff(energies, prepend=1e-10)
            expected_values = np.zeros(len(energies))
            expected_error_variances = np.zeros(len(energies))
            for source_index, source_energy in enumerate(energies):
                source_fwhm = (
                    fwhm_frac
                    if isinstance(fwhm_frac, float)
                    else fwhm_frac[source_index]
                )
                sigma = source_fwhm * source_energy / (2 * np.sqrt(2 * np.log(2)))
                scale = 1.0 if exponent is None else (source_energy / eref) ** exponent
                kernel = np.exp(
                    -0.5 * ((energies - source_energy) / (scale * sigma)) ** 2
                ) / (sigma * np.sqrt(2 * np.pi) * scale)
                contribution = (
                    data["Value"][source_index] * kernel * source_widths[source_index]
                )
                expected_values += contribution
                expected_error_variances += (
                    data["Error"][source_index] * contribution
                ) ** 2

            assert len(result) == len(tally)
            assert result["Value"].to_numpy() == pytest.approx(expected_values)
            assert result["Error"].to_numpy() == pytest.approx(
                np.sqrt(expected_error_variances) / expected_values
            )

    tally = pd.DataFrame(
        {"Energy": [1.0, 2.0], "Value": [1.0, 2.0], "Error": [0.1, 0.2]}
    )
    with pytest.raises(ValueError, match="Reference value.*Ref"):
        gaussian_broadening(
            tally.copy(), "Energy", {"2.0": {"linear": {"fwhm_frac": 0.2}}}
        )
    with pytest.raises(ValueError, match="Length of FWHM fraction list"):
        gaussian_broadening(
            tally.copy(), "Energy", {"2.0": {"no_scaling": {"fwhm_frac": [0.1]}}}
        )
    with pytest.raises(ValueError, match="Unknown scaling factor option"):
        gaussian_broadening(
            tally.copy(), "Energy", {"2.0": {"cubic": {"fwhm_frac": 0.2}}}
        )

    result = gaussian_broadening(tally.copy(), "Energy", {"2.0": {"no_scaling": {}}})
    assert "FWHM fraction not found" in caplog.text
    assert np.isfinite(result["Value"]).all()
    assert np.isfinite(result["Error"]).all()

    for column in ["Energy", "Time"]:
        for fraction in [0.0, 0.2, 1.0]:
            tally = pd.DataFrame(
                {
                    column: [1.0, 2.0, 4.0, 8.0, 20.0],
                    "Value": [0.5, 2.0, 7.0, 3.0, 1.0],
                    "Error": [0.1, 0.2, 0.3, 0.1, 0.2],
                }
            )
            widths = np.diff(tally[column].to_numpy(), prepend=1e-10)
            differential_input = tally.copy()
            differential_input["Value"] /= widths
            bins = {20: {"no_scaling": {"fwhm_frac": fraction}}}
            differential = gaussian_broadening(differential_input, column, bins)
            result = gaussian_broadening(tally.copy(), column, bins, integral=True)
            np.testing.assert_allclose(result["Value"], differential["Value"] * widths)
            np.testing.assert_allclose(result["Error"], differential["Error"])
            if fraction == 0:
                pd.testing.assert_frame_equal(result, tally, check_dtype=False)

    with pytest.raises(TypeError, match="integral must be a boolean"):
        gaussian_broadening(pd.DataFrame(), "Time", {}, integral="yes")

    for edges in [[0.0, 1.0], [1.0, 1.0], [1.0, np.nan]]:
        tally = pd.DataFrame({"Time": edges, "Value": [1.0] * 2, "Error": [0.1] * 2})
        with pytest.raises(ValueError, match="bin edges"):
            gaussian_broadening(tally, "Time", {}, integral=True)


def test_volume():
    data = {
        "Cells": [1, 2, 3, 4, 5],
        "Value": [7.301230e-06, 5.373435e-06, 6.279305e-06, 7.781032e-06, 1.129645e-05],
        "Error": [0.1, 0.2, 0.3, 0.4, 0.5],
    }
    df = pd.DataFrame(data)
    volumes = {1: 2.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 2.0}
    result = volume(df, volumes)
    assert 3.65062e-06 == pytest.approx(result["Value"][0], rel=1e-5)
    assert 0.1 == pytest.approx(result["Error"][0], rel=1e-5)


def test_mass():
    data = {
        "Cells": [1, 2, 3, 4, 5],
        "Value": [7.301230e-06, 5.373435e-06, 6.279305e-06, 7.781032e-06, 1.129645e-05],
        "Error": [0.1, 0.2, 0.3, 0.4, 0.5],
    }
    df = pd.DataFrame(data)
    masses = {1: 2.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 2.0}
    result = mass(df, masses)
    assert 3.65062e-06 == pytest.approx(result["Value"][0], rel=1e-5)
    assert 0.1 == pytest.approx(result["Error"][0], rel=1e-5)
