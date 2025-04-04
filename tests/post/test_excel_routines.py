import numpy as np
import pandas as pd
import pytest

from jade.config.excel_config import ComparisonType
from jade.post.excel_routines import Table


class TestTable:
    def test_compare(self):
        data1 = {"Energy": [1, 2, 3], "Value": [10, 20, 30], "Error": [0.1, 0.2, 0.3]}
        data2 = {"Energy": [1, 2, 3], "Value": [5, 15, 30], "Error": [0.15, 0.25, 0.35]}
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        result = Table._compare(df1, df2, ComparisonType.PERCENTAGE)
        expected_values = [50, 25, 0]
        expected_errors = [
            np.sqrt((5 * 10 * 0.1) ** 2 + (5 * 0.15) ** 2) / 5,
            np.sqrt((15 * 20 * 0.2) ** 2 + (15 * 0.25) ** 2) / 5,
            0.65,
        ]
        assert pytest.approx(result["Value"].tolist()) == expected_values
        assert pytest.approx(result["Error"].tolist()) == expected_errors

    def test_rename_columns(self):
        data = {
            "A": ["a", "a", "b"],
            "B": [1, 5, 1],
            "C": ["d", "d", "e"],
            "D": [10, 10, 2],
            "Value": [13, 14, 15],
            "Error": [0.1, 0.2, 0.3],
        }
        df = pd.DataFrame(data)
        # # try easy normal renaming first
        # newdf = df.copy()
        # # something that does nothing
        # Table._rename_columns(newdf, {"pippi": "AA"})

        # # index is None
        # assert newdf.columns.names == ["AA", "BB", "C", "D", "Value"]

        newdf = df.pivot(
            index=["A", "B"], columns=["C", "D"], values=["Value", "Error"]
        )
        Table._rename_columns(newdf, {"C": "CC", None: "AA"})
        assert "CC" in newdf.columns.names
        assert "AA" in newdf.columns.names
