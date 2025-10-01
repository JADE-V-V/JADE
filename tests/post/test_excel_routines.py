import numpy as np
import pandas as pd
import pytest

from jade.config.excel_config import ComparisonType
from jade.post.excel_routines import ChiTable, SpherePivotTable, Table


class TestTable:
    def test_get_safe_name(self):
        sheet_name = Table._get_safe_name(
            "Some really long sheet name which is over 32 charaters"
        )
        assert len(sheet_name) < 32

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


class TestChiTable:
    def test_compare(self):
        data1 = {
            "Energy": [0, 1, 2, 3],
            "Value": [2, 10, 20, 30],
            "Error": [0.1, 0.1, 0.2, 0.3],
            "Case": ["a", "a", "b", "b"],
        }
        data2 = {
            "Energy": [1, 2, 3],
            "Value": [5, 15, 30],
            "Error": [0.15, 0.25, 0.35],
            "Case": ["a", "b", "b"],
        }
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        result = ChiTable._compare(df1, df2, ComparisonType.CHI_SQUARED)
        result = result.set_index(["Case", "Energy"])
        assert (
            pytest.approx(result.loc[("b", "TOT"), "Value"])
            == (0.25 / 0.2 - 1) ** 2 / (0.2**2) / 2
        )


class TestSpherePivotTable:
    def test_sort_sphere_index_single(self):
        """Test sorting with single index (Case only)"""
        # Create a dataframe with unsorted cases
        data = {
            "Value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        }
        index = [
            "Sphere_M400",
            "Sphere_26056_Fe-56",
            "Sphere_1001_H-1",
            "Sphere_M101",
            "Sphere_92235_U-235",
            "Sphere_1002_H-2",
        ]
        df = pd.DataFrame(data, index=index)
        
        # Sort the dataframe
        sorted_df = SpherePivotTable._sort_sphere_index(df)
        
        # Expected order: isotopes by Z number, then materials alphabetically
        # Z=1 (H): 1001, 1002
        # Z=26 (Fe): 26056
        # Z=92 (U): 92235
        # Materials: M101, M400
        expected_order = [
            "Sphere_1001_H-1",
            "Sphere_1002_H-2",
            "Sphere_26056_Fe-56",
            "Sphere_92235_U-235",
            "Sphere_M101",
            "Sphere_M400",
        ]
        
        assert sorted_df.index.tolist() == expected_order

    def test_sort_sphere_index_multi(self):
        """Test sorting with multi-index (Case and Energy)"""
        # Create a dataframe with multi-index
        cases = [
            "Sphere_M400",
            "Sphere_M400",
            "Sphere_26056_Fe-56",
            "Sphere_26056_Fe-56",
            "Sphere_1001_H-1",
            "Sphere_1001_H-1",
        ]
        energies = [1.0, 2.0, 1.0, 2.0, 1.0, 2.0]
        values = [10, 20, 30, 40, 50, 60]
        
        df = pd.DataFrame({"Value": values})
        df.index = pd.MultiIndex.from_arrays([cases, energies], names=["Case", "Energy"])
        
        # Sort the dataframe
        sorted_df = SpherePivotTable._sort_sphere_index(df)
        
        # Expected order: H-1 first (Z=1), then Fe-56 (Z=26), then M400
        expected_cases = [
            "Sphere_1001_H-1",
            "Sphere_1001_H-1",
            "Sphere_26056_Fe-56",
            "Sphere_26056_Fe-56",
            "Sphere_M400",
            "Sphere_M400",
        ]
        expected_energies = [1.0, 2.0, 1.0, 2.0, 1.0, 2.0]
        
        result_cases = sorted_df.index.get_level_values(0).tolist()
        result_energies = sorted_df.index.get_level_values(1).tolist()
        
        assert result_cases == expected_cases
        assert result_energies == expected_energies

    def test_sort_sphere_index_empty(self):
        """Test sorting with empty dataframe"""
        # Create an empty dataframe
        df = pd.DataFrame()
        
        # Sort the dataframe - should return empty df unchanged
        sorted_df = SpherePivotTable._sort_sphere_index(df)
        
        assert sorted_df.empty
        assert len(sorted_df) == 0

    def test_get_sheet_integration(self):
        """Test the full _get_sheet method with sorting applied"""
        import tempfile
        from jade.config.excel_config import ComparisonType, TableConfig
        
        # Create test data
        data = {
            "Case": [
                "Sphere_M400",
                "Sphere_1001_H-1",
                "Sphere_26056_Fe-56",
            ] * 2,
            "Energy": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
            "Value": [10.0, 20.0, 30.0, 15.0, 25.0, 35.0],
            "Error": [0.1, 0.2, 0.3, 0.15, 0.25, 0.35],
        }
        ref_df = pd.DataFrame(data)
        target_df = ref_df.copy()
        
        # Create a mock config
        class MockConfig:
            x = ["Case"]
            y = ["Energy"]
            value = "Value"
            add_error = False
            comparison_type = ComparisonType.PERCENTAGE
            conditional_formatting = None
            change_col_names = None
        
        cfg = MockConfig()
        
        # Create a temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            writer = pd.ExcelWriter(f.name, engine='xlsxwriter')
            
            # Create SpherePivotTable instance
            table = SpherePivotTable(
                "Test",
                writer,
                ref_df,
                target_df,
                cfg,
                "ref",
                "target"
            )
            
            # Get the sheets
            sheets = table._get_sheet()
            
            writer.close()
            
            # Verify the result is sorted
            assert len(sheets) == 1
            result_df = sheets[0]
            
            # Check that cases are sorted: H-1 (Z=1), Fe-56 (Z=26), M400 (material)
            expected_order = ["Sphere_1001_H-1", "Sphere_26056_Fe-56", "Sphere_M400"]
            assert result_df.index.tolist() == expected_order

    def test_sort_sphere_index_edge_cases(self):
        """Test sorting with edge cases and unusual formats"""
        # Create a dataframe with various edge case formats
        data = {
            "Value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        }
        index = [
            "Sphere_1001_H-1",      # Normal 4-digit ZAID
            "Sphere_26056_Fe-56",   # Normal 5-digit ZAID
            "Sphere_M400",          # Normal material
            "Sphere_123",           # Unusual ZAID format (3 digits)
            "Sphere_XYZ",           # Non-numeric, non-M identifier
            "UnknownFormat",        # No underscore separator
            "Sphere",               # Only one part
        ]
        df = pd.DataFrame(data, index=index)
        
        # Sort the dataframe - should handle edge cases gracefully
        sorted_df = SpherePivotTable._sort_sphere_index(df)
        
        # Verify the result is a DataFrame and has same length
        assert len(sorted_df) == len(df)
        assert isinstance(sorted_df, pd.DataFrame)
        
        # Check that known good formats are sorted correctly
        result_index = sorted_df.index.tolist()
        
        # H-1 should come before Fe-56 (both are isotopes with proper format)
        h_pos = result_index.index("Sphere_1001_H-1")
        fe_pos = result_index.index("Sphere_26056_Fe-56")
        assert h_pos < fe_pos, "H-1 should come before Fe-56"
        
        # Edge cases should be treated as materials and come after isotopes
        # M400 should be in materials section
        assert "Sphere_M400" in result_index

