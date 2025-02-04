from __future__ import annotations

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.markers import CARETDOWNBASE, CARETUPBASE
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import AutoLocator, AutoMinorLocator, LogLocator, MultipleLocator

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
MARKERS = ["o", "s", "D", "^", "X", "p", "d", "*"] * 50


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

        fig.suptitle(self.cfg.title, y=0.93)
        axes[-1].set_xlabel(self.cfg.x_label)

        # additional common extra features that may be requested
        if self.cfg.recs:
            self._build_rectangles(axes[0])
        if self.cfg.v_lines:
            for ax in axes:
                self._add_vlines(ax)
        if self.cfg.additional_labels:
            for ax in axes:
                self._add_labels(ax)

        return fig, axes

    @abstractmethod
    def _get_figure(self) -> tuple[Figure, Axes]:
        pass

    def _build_rectangles(self, ax: Axes) -> None:
        options = self.cfg.recs
        y_min, y_max = ax.get_ylim()
        # Plot the rects
        height = y_max - y_min

        df_options = pd.DataFrame(options)
        df_options.columns = ["name", "color", "xmin", "xmax"]

        for _, rec in df_options.iterrows():
            # Create the rectangle
            width = rec["xmax"] - rec["xmin"]
            origin = (rec["xmin"], y_min)
            color = rec["color"]

            rectangle = Rectangle(
                origin, width=width, height=height, color=color, alpha=0.2
            )
            ax.add_patch(rectangle)

        # Build the additional legend
        # Drop duplicates
        df = df_options[["color", "name"]].drop_duplicates()
        legend_elements = []
        for _, row in df.iterrows():
            patch = Patch(
                facecolor=row["color"],
                edgecolor="black",
                label=row["name"],
                alpha=0.2,
            )
            legend_elements.append(patch)

        additional_legend = ax.legend(
            handles=legend_elements,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            fancybox=True,
            ncol=5,
            shadow=True,
        )
        # Normal legend needs to be reprinted
        ax.legend(loc="best")
        # And now the custom one
        ax.add_artist(additional_legend)

    def _add_vlines(self, ax: Axes) -> None:
        # major lines
        if self.cfg.v_lines is None:
            return

        if "major" in self.cfg.v_lines.keys():
            lines = self.cfg.v_lines["major"]
            for line in lines:
                # Check first if the value is in the axis limits
                if ax.get_xlim()[0] < line < ax.get_xlim()[1]:
                    ax.axvline(line, color="black")

        # minor lines
        if "minor" in self.cfg.v_lines.keys():
            lines = self.cfg.v_lines["minor"]
            for line in lines:
                # Check first if the value is in the axis limits
                if ax.get_xlim()[0] < line < ax.get_xlim()[1]:
                    ax.axvline(
                        line,
                        color="black",
                        ymin=0.10,
                        ymax=0.90,
                        linestyle="--",
                        linewidth=1,
                    )

    def _add_labels(self, ax: Axes) -> None:
        # major labels
        if self.cfg.additional_labels is None:
            return

        if "major" in self.cfg.additional_labels.keys():
            labels = self.cfg.additional_labels["major"]
            for label, xpos in labels:
                bbox_dic = {
                    "boxstyle": "round,pad=0.5",
                    "facecolor": "white",
                    "alpha": 1,
                }
                xmin, xmax = ax.get_xlim()
                xpos_perc = (xpos - xmin) / (xmax - xmin)
                ax.text(xpos_perc, 0.95, label, bbox=bbox_dic, transform=ax.transAxes)

        if "minor" in self.cfg.additional_labels.keys():
            # minor labels
            labels = self.cfg.additional_labels["minor"]
            for label, xpos in labels:
                xmin, xmax = ax.get_xlim()
                xpos_perc = (xpos - xmin) / (xmax - xmin)
                ax.text(xpos_perc, 0.87, label, transform=ax.transAxes)


class RatioPlot(Plot):
    def _get_figure(self) -> tuple[Figure, Axes]:
        # get some optional data
        if self.cfg.plot_args is not None:
            markers = self.cfg.plot_args.get("markers", False)
            split_x = self.cfg.plot_args.get("split_x", None)
        else:
            markers = False
            split_x = None

        # split the x axis if requested
        if split_x is not None:
            ncols = 2
            sharey = True
        else:
            ncols = 1
            sharey = False
        # Initialize plot
        fig, axes = plt.subplots(ncols=ncols, sharey=sharey)

        if isinstance(axes, Axes):
            axes = [axes]

        # Plot all data
        ref_y = self.data[0][1][self.cfg.y]

        for i, (codelib, df) in enumerate(self.data[1:]):
            y = df[self.cfg.y] / ref_y
            # Plot
            marker = None
            if markers:
                marker = MARKERS[i]

            keyargs = {
                "color": COLORS[i],
                "drawstyle": "steps-pre",
                "label": codelib,
                "marker": marker,
                "linestyle": LINESTYLES[i],
                "linewidth": 0.7,
            }

            if split_x is not None:
                x_left, x_right = split_x
                mask_left = df[self.cfg.x] < x_left
                mask_right = df[self.cfg.x] >= x_right
                axes[0].plot(
                    df[mask_left][self.cfg.x],
                    y[mask_left],
                    **keyargs,
                )
                axes[1].plot(
                    df[mask_right][self.cfg.x],
                    y[mask_right],
                    **keyargs,
                )
                fig.subplots_adjust(wspace=0.05)
                # x axis label needs to be specified also for the left plot
                axes[0].set_xlabel(self.cfg.x_label)
            else:
                axes[0].plot(
                    df[self.cfg.x],
                    y,
                    **keyargs,
                )

        # Plot details
        axes[0].legend(loc="best")
        axes[0].set_ylabel(f"Ratio of {self.cfg.y} - (vs {self.data[0][0]})")

        for ax in axes:
            # Tiks positioning and dimensions
            ax.xaxis.set_major_locator(AutoLocator())
            ax.yaxis.set_major_locator(AutoLocator())
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_minor_locator(AutoMinorLocator())

            ax.tick_params(which="major", width=1.00, length=5)
            ax.tick_params(which="minor", width=0.75, length=2.50)

            # Grid
            ax.grid(True, which="major", linewidth=0.50)
            ax.grid(True, which="minor", linewidth=0.20)

        # # Limit the x-axis if needed
        # if xlimits is not None:
        #     ax.set_xlim(xlimits[0], xlimits[1])

        return fig, axes


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
        elif plot_config.plot_type == PlotType.RATIO:
            return RatioPlot(plot_config, data)
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
