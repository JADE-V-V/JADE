import pandas as pd

from jade.post.excel_routines import Table


class TestTable:
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
