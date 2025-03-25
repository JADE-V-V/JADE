import numpy as np
import pandas as pd

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
        assert result["Value"].tolist() == expected_values
        assert result["Error"].tolist() == expected_errors
