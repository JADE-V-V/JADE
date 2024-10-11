import pandas as pd
from jade.excelsupport import single_excel_writer, comp_excel_writer
import pytest
import os


class TestExcelSupport:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup: Create a sample DataFrame
        self.lib = "00c"
        self.testname = "Oktavian"

        self.df_value = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        self.df_error = pd.DataFrame({"A": [0.1, 0.2, 0.3], "B": [0.4, 0.5, 0.6]})

        # Define the dictionary
        data = {
            1: {
                "title": "Title 1",
                "x_label": "A",
                "Value": self.df_value,
                "Error": self.df_error,
            },
            2: {
                "title": "Title 2",
                "x_label": "A",
                "Value": self.df_value,
                "Error": self.df_error,
            },
            3: {
                "title": "Title 3",
                "x_label": "A",
                "Value": self.df_value,
                "Error": self.df_error,
            },
        }

        self.stats = {
            "Tally Number": [1, 2, 3, 4, 5],
            "Tally Description": [
                "Description 1",
                "Description 2",
                "Description 3",
                "Description 4",
                "Description 5",
            ],
            "Result": ["Missed", "Passed", "Missed", "Passed", "Missed"],
        }
        self.tallies = data
        self.stat_df = pd.DataFrame(self.stats)

    def test_single_excel_writer(self, tmpdir):
        # Test case: Write data to excel
        outpath = tmpdir.join("test.xlsx")
        single_excel_writer(
            outpath, self.lib, self.testname, self.tallies, self.stat_df
        )

        # Assert that the file exists
        assert os.path.exists(outpath)

    def test_comp_excel_writer(self, tmpdir):
        # Test case: Write data to excel
        outpath = tmpdir.join("test.xlsx")
        comp_excel_writer(
            self,
            outpath,
            "32c_Vs_31c",
            self.testname,
            self.tallies,
            self.tallies,
            self.tallies,
        )

        # Assert that the file exists
        assert os.path.exists(outpath)
