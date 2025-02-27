from __future__ import annotations

import numpy as np
import pandas as pd

from jade.config.atlas_config import PlotConfig
from jade.post.plotter import BinnedPlot, WavesPlot, CEPlot


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
