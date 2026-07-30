from __future__ import annotations

import random
import string

import numpy as np
import pandas as pd
import pytest

from jade.config.atlas_config import PlotConfig
from jade.helper.errors import PlotIndexMismatchError
from jade.post.plotter import BarPlot, BinnedPlot, CEPlot, ScatterPlot, WavesPlot


class TestBinnedPlot:
    def test_plot(self, tmpdir):
        cfg = PlotConfig(
            name="test",
            results=[1, 2, 3],  # dummy values
            plot_type=None,  # dummy value
            title="test",
            x_label="test",
            y_labels=["label 1", "label 2", "label 3"],
            x="energy",
            y="value",
        )

        data1 = pd.DataFrame(
            {
                "energy": range(10),
                "value": np.random.rand(10),
                "Error": np.random.rand(10) * 0.1,
            }
        )

        data2 = pd.DataFrame(
            {
                "energy": range(10),
                "value": np.random.rand(10),
                "Error": np.random.rand(10) * 0.1,
            }
        )

        data3 = pd.DataFrame(
            {
                "energy": range(10),
                "value": np.random.rand(10),
                "Error": np.random.rand(10) * 0.1,
            }
        )

        data = [("data1", data1), ("data2", data2), ("data3", data3)]

        plot = BinnedPlot(cfg, data)
        output = plot.plot()
        output[0][0].savefig(tmpdir.join("test.png"))


class TestWavesPlot:
    def test_plot(self, tmpdir):
        cfg = PlotConfig(
            name="test",
            results=["a", "b", "c"],
            plot_type=None,  # dummy value
            title="test",
            x_label="Case",
            y_labels=["dummy"],
            x="Case",
            y="Value",
            plot_args={"limits": [0.5, 1.5], "shorten_x_name": 2},
        )
        n_libs = 3
        n_cases = 50
        data = []
        for i in range(n_libs):
            cases = [f"Very_long_case_name_{i}" for i in range(n_cases)]
            dfs = []
            for result in cfg.results:
                df = pd.DataFrame(
                    {
                        "Case": cases,
                        "Value": np.random.rand(n_cases),
                        "Error": np.random.rand(n_cases) * 0.1,
                    }
                )
                df["Result"] = result
                dfs.append(df)
            data.append((f"lib{i}", pd.concat(dfs)))

        plot = WavesPlot(cfg, data)
        output = plot.plot()
        for i, (fig, _) in enumerate(output):
            fig.savefig(tmpdir.join(f"test{i}.png"))


class TestCEPlot:
    def test_plot(self, tmpdir):
        cfg = PlotConfig(
            name="test",
            results=["a", "b", "c"],
            plot_type=None,  # dummy value
            title="test",
            x_label="Case",
            y_labels=["dummy"],
            x="Case",
            y="Value",
            plot_args={"style": "step", "ce_limits": [0.5, 1.5], "shorten_x_name": 2},
        )
        n_libs = 3
        n_cases = 50
        data = []
        for i in range(n_libs):
            cases = [f"Very_long_case_name_{i}" for i in range(n_cases)]
            dfs = []
            for result in cfg.results:
                df = pd.DataFrame(
                    {
                        "Case": cases,
                        "Value": np.random.rand(n_cases),
                        "Error": np.random.rand(n_cases) * 0.1,
                        "Subcase": np.random.randint(0, 3),
                    }
                )
                df["Result"] = result
                dfs.append(df)
            data.append((f"lib{i}", pd.concat(dfs)))

        plot = CEPlot(cfg, data)
        output = plot.plot()
        output[0][0].savefig(tmpdir.join("test.png"))

    def test_missing_subcase(self, tmpdir):
        cfg = PlotConfig(
            name="test",
            results=["a", "b", "c"],
            plot_type=None,  # dummy value
            title="test",
            x_label="Case",
            y_labels=["dummy"],
            x="Case",
            y="Value",
            plot_args={
                "style": "step",
                "ce_limits": [0.5, 1.5],
                "subcases": ["Result", ["a", "b", "c"]],
            },
        )
        n_libs = 2
        n_cases = 50
        data = []
        for i in range(n_libs):
            cases = range(n_cases)
            dfs = []
            for result in cfg.results:
                # remove one set
                if result == "b" and i == 1:
                    continue
                df = pd.DataFrame(
                    {
                        "Case": cases,
                        "Value": np.random.rand(n_cases),
                        "Error": np.random.rand(n_cases) * 0.1,
                        # "Subcase": np.random.randint(0, 3),
                    }
                )
                df["Result"] = result
                dfs.append(df)
            data.append((f"lib{i}", pd.concat(dfs)))

        plot = CEPlot(cfg, data)
        output = plot.plot()
        # check only two rows in plot
        assert len(output[0][1]) == 2
        output[0][0].savefig(tmpdir.join("test.png"))

    def test_trigger_index_match_error(self, tmpdir):
        """trigger a PlotIndexMatchError in CEPlot"""
        cfg = PlotConfig(
            name="test",
            results=["a"],
            plot_type=None,  # dummy value
            title="test",
            x_label="Case",
            y_labels=["dummy"],
            x="Case",
            y="Value",
            plot_args={"style": "step"},
        )

        # Create reference data with cases 0-4
        n_cases_ref = 5
        df_ref = pd.DataFrame(
            {
                "Case": range(n_cases_ref),
                "Value": np.random.rand(n_cases_ref),
                "Error": np.random.rand(n_cases_ref) * 0.1,
            }
        )

        # Create target data with DIFFERENT cases (5-9) to trigger mismatch
        n_cases_target = 5
        df_target = pd.DataFrame(
            {
                "Case": range(5, 5 + n_cases_target),
                "Value": np.random.rand(n_cases_target),
                "Error": np.random.rand(n_cases_target) * 0.1,
            }
        )

        data = [("lib_ref", df_ref), ("lib_target", df_target)]

        plot = CEPlot(cfg, data)
        # Expect PlotIndexMismatchError to be raised when plotting
        with pytest.raises(PlotIndexMismatchError):
            plot.plot()


class TestBarPlot:
    def test_plot(self, tmpdir):
        cfg = PlotConfig(
            name="test",
            results=["a"],
            plot_type=None,  # dummy value
            title="test",
            x_label="Position",
            y_labels=["dummy"],
            x="Position",
            y="Value",
            # plot_args={"shorten_x_name": 2},
        )
        n_libs = 3
        data = []
        n_data = 30
        letters = string.ascii_letters
        length = 4
        positions = []
        for i in range(n_data):
            pos = "".join(random.choice(letters) for i in range(length))
            positions.append(pos)
        for i in range(n_libs):
            df = pd.DataFrame(
                {
                    "Position": positions,
                    "Value": np.random.rand(n_data),
                    "Error": np.random.rand(n_data) * 0.1,
                }
            )

            data.append((f"lib{i}", df))

        plot = BarPlot(cfg, data)
        output = plot.plot()
        output[0][0].savefig(tmpdir.join("test.png"), bbox_inches="tight")


class TestScatterPlot:
    def _make_cfg(self, **plot_args):
        return PlotConfig(
            name="test",
            results=["dummy"],
            plot_type=None,
            title="Scatter test",
            x_label="Case",
            y_labels=["Value"],
            x="Case",
            y="Value",
            plot_args=plot_args if plot_args else None,
        )

    def _make_data(self, n_libs=3, n_cases=10):
        cases = [f"case_{i}" for i in range(n_cases)]
        data = []
        for i in range(n_libs):
            df = pd.DataFrame(
                {
                    "Case": cases,
                    "Value": np.random.rand(n_cases) + 0.5,
                    "Error": np.random.rand(n_cases) * 0.1,
                }
            )
            data.append((f"lib{i}", df))
        return data

    def test_plot_categorical(self, tmpdir):
        cfg = self._make_cfg()
        data = self._make_data()
        plot = ScatterPlot(cfg, data)
        output = plot.plot()
        assert len(output) == 1
        fig, axes = output[0]
        assert len(axes) == 2
        fig.savefig(tmpdir.join("test_scatter.png"), bbox_inches="tight")

    def test_plot_numerical_with_ce_limits(self, tmpdir):
        cfg = self._make_cfg(ce_limits=[0.5, 1.5])
        n_cases = 10
        data = []
        for i in range(3):
            df = pd.DataFrame(
                {
                    "Case": np.linspace(1, 10, n_cases),
                    "Value": np.random.rand(n_cases) + 0.5,
                    "Error": np.random.rand(n_cases) * 0.1,
                }
            )
            data.append((f"lib{i}", df))
        plot = ScatterPlot(cfg, data)
        output = plot.plot()
        assert len(output) == 1
        fig, axes = output[0]
        assert len(axes) == 2
        fig.savefig(tmpdir.join("test_scatter_ce.png"), bbox_inches="tight")
