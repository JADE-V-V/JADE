from __future__ import annotations

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.markers import CARETDOWNBASE, CARETUPBASE
from matplotlib.ticker import AutoMinorLocator, LogLocator, MultipleLocator

from jade.config.atlas_config import PlotConfig, PlotType

# Color-blind saver palette
COLORS = [
    "#377eb8",
    "#ff7f00",
    "#4daf4a",
    "#f781bf",
    "#a65628",
    "#984ea3",
    "#999999",
    "#e41a1c",
    "#dede00",
] * 50

# --- linestyles ---
LINESTYLES = ["--", "-.", ":"] * 50


class Plot(ABC):
    def __init__(
        self, plot_config: PlotConfig, data: list[tuple[str, pd.DataFrame]]
    ) -> None:
        self.cfg = plot_config
        self.data = data

    def plot(self) -> tuple[Figure, Axes | list[Axes]]:
        fig, axes = self._get_figure()
        if isinstance(axes, Axes):
            axes = [axes]

        axes[0].set_title(self.cfg.title)
        axes[-1].set_xlabel(self.cfg.x_label)

        return fig, axes

    @abstractmethod
    def _get_figure(self) -> tuple[Figure, Axes]:
        pass


class BinnedPlot(Plot):
    def _get_figure(self) -> tuple[Figure, Axes]:
        linewidth = 0.7
        # Check if the error needs to be plotted
        if self.cfg.plot_args is not None:
            plot_error = self.cfg.plot_args.get("error", False)
        else:
            plot_error = False

        # Set properties for the plot spacing
        if not plot_error:
            gridspec_kw = {"height_ratios": [3, 1], "hspace": 0.13}
            nrows = 2
        else:
            gridspec_kw = {"height_ratios": [4, 1, 1], "hspace": 0.13}
            nrows = 3

        # Initiate plot
        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=1,
            sharex=True,
            # figsize=(18, 13.5),
            gridspec_kw=gridspec_kw,
        )

        # --- Main plot ---
        ax1 = axes[0]
        # Ticks
        subs = (0.2, 0.4, 0.6, 0.8)
        ax1.set_xscale("log")
        ax1.set_yscale("log")
        ax1.set_ylabel(self.cfg.y_labels[0])
        ax1.xaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax1.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax1.xaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))
        ax1.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))

        # --- Error Plot ---
        if plot_error:
            ax2 = axes[1]
            ax2.axhline(y=10, linestyle="--", color="black")
            ax2.set_ylabel("1σ [%]")
            ax2.set_yscale("log")
            ax2.set_ylim(bottom=1, top=100)
            ax2.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
            ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))

            CE_ax = axes[2]
        else:
            CE_ax = axes[1]

        # --- Comparison Plot ---
        CE_ax.axhline(y=1, linestyle="--", color="black")
        CE_ax.set_ylabel("$T_i/R$")
        CE_ax.yaxis.set_major_locator(MultipleLocator(0.5))
        CE_ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        CE_ax.axhline(y=2, linestyle="--", color="red", linewidth=0.5)
        CE_ax.axhline(y=0.5, linestyle="--", color="red", linewidth=0.5)
        CE_ax.set_ylim(bottom=0.3, top=2.2)

        # Generate X axis for bin properties
        oldX = np.array([0] + list(self.data[0][1][self.cfg.x]))
        base = np.log(oldX[:-1])
        shifted = np.log(oldX[1:])
        newX = np.exp((base + shifted) / 2)
        newX[0] = (oldX[1] + oldX[0]) / 2
        # --- Plot Data ---
        for idx, (codelib, df) in enumerate(self.data):
            x = np.array([0] + list(df[self.cfg.x]))
            y = np.array([0] + list(df[self.cfg.y]))

            err = np.array(df["Error"])
            err_multi = np.array(y[1:]) * np.abs(err)

            # Main plot
            if idx > 0:
                tag = "T" + str(idx) + ": "
                linestyle = LINESTYLES[idx - 1]
            else:
                tag = "R: "
                linestyle = "-"

            ax1.step(
                x,
                y,
                label=tag + codelib,
                color=COLORS[idx],
                linestyle=linestyle,
                linewidth=linewidth,
            )
            ax1.errorbar(
                newX,
                y[1:],
                linewidth=0,
                yerr=err_multi,
                elinewidth=0.5,
                color=COLORS[idx],
            )

            # Error Plot
            if plot_error:
                ax2.plot(
                    newX,
                    np.array(df["Error"]) * 100,
                    "o",
                    label=codelib,
                    markersize=2,
                    color=COLORS[idx],
                )

            # Comparison
            if idx > 0:
                ratio = df[self.cfg.y].values / self.data[0][1][self.cfg.y].values
                # Uniform plots actions
                norm, upper, lower = _get_limits(0.5, 2, ratio, newX)

                CE_ax.plot(norm[0], norm[1], "o", markersize=2, color=COLORS[idx])
                CE_ax.scatter(
                    upper[0], upper[1], marker=CARETUPBASE, s=50, c=COLORS[idx]
                )
                CE_ax.scatter(
                    lower[0],
                    lower[1],
                    marker=CARETDOWNBASE,
                    s=50,
                    c=COLORS[idx],
                )

        # Build ax3 legend
        leg = [
            Line2D(
                [0],
                [0],
                marker=CARETUPBASE,
                color="black",
                label="> 2",
                markerfacecolor="black",
                markersize=8,
                lw=0,
            ),
            Line2D(
                [0],
                [0],
                marker=CARETDOWNBASE,
                color="black",
                label="< 0.5",
                markerfacecolor="black",
                markersize=8,
                lw=0,
            ),
        ]
        CE_ax.legend(handles=leg, loc="best")

        # Final operations
        ax1.legend(loc="best")

        # --- Common Features ---
        for ax in axes:
            # Grid control
            ax.grid()
            ax.grid("True", which="minor", linewidth=0.25)
            # Ticks
            ax.tick_params(which="major", width=1.00, length=5)
            ax.tick_params(which="minor", width=0.75, length=2.50)

        return fig, axes


class RatioPlot(Plot):
    pass


class ExpPlot(Plot):
    pass


class ExpGroupPlot(Plot):
    pass


class CeExpGroupPlot(Plot):
    pass


class DiscreteExpPlot(Plot):
    pass


class GroupedBarsPlot(Plot):
    pass


class WavesPlot(Plot):
    pass


class PlotFactory:
    @staticmethod
    def create_plot(
        plot_config: PlotConfig, data: list[tuple[str, pd.DataFrame]]
    ) -> Plot:
        if plot_config.plot_type == PlotType.BINNED:
            return BinnedPlot(plot_config, data)
        else:
            raise NotImplementedError(
                f"Plot type {plot_config.plot_type} not implemented"
            )


# Aux functions
def _get_limits(lowerlimit, upperlimit, ydata, xdata):
    """
    Given an X, Y dataset and bounding y limits it returns three datasets
    couples containing the sets to be normally plotted and the upper and
    lower set.

    Parameters
    ----------
    lowerlimit : float
        bounding lower y limit.
    upperlimit : float
        bounding upper x limit.
    ydata : list or array
        Y axis data.
    xdata : list or array
        X axis data.

    Returns
    -------
    (normalX, normalY)
        x, y sets to be normally plotted
    (upperX, upperY)
        x, y sets that are above upperlimit
    (lowerX, lowerY)
        x, y sets that are below upper limit.

    """
    assert lowerlimit < upperlimit
    # ensure data is array
    ydata = np.array(ydata)
    xdata = np.array(xdata)
    # Get the three logical maps
    upmap = ydata > upperlimit
    lowmap = ydata < lowerlimit
    normalmap = np.logical_and(np.logical_not(upmap), np.logical_not(lowmap))

    # Apply maps to divide the original sets
    normalY = ydata[normalmap]
    normalX = xdata[normalmap]

    upperX = xdata[upmap]
    upperY = np.full(len(upperX), upperlimit)

    lowerX = xdata[lowmap]
    lowerY = np.full(len(lowerX), lowerlimit)

    return (normalX, normalY), (upperX, upperY), (lowerX, lowerY)
