from __future__ import annotations

import numpy as np
import pandas as pd

from jade.config.atlas_config import PlotConfig
from jade.post.plotter import BinnedPlot


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
        fig, ax = plot.plot()
        fig.savefig(tmpdir.join("test.png"))
