from __future__ import annotations

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from f4enix.input.libmanager import LibManager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.markers import CARETDOWNBASE, CARETUPBASE
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import AutoLocator, AutoMinorLocator, LogLocator, MultipleLocator

from jade.config.atlas_config import PlotConfig, PlotType

LM = LibManager()
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

        # check if the first ax has a title
        if axes[0].get_title() == "":
            fig.suptitle(self.cfg.title, y=0.93)
        else:
            fig.suptitle(self.cfg.title)

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

        fig.tight_layout()  # Adjust padding

        return fig, axes

    @abstractmethod
    def _get_figure(self) -> tuple[Figure, Axes | list[Axes]]:
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
    def _get_figure(self) -> tuple[Figure, list[Axes]]:
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
            ax.grid(True, which="major", linewidth=0.50, alpha=0.5)
            ax.grid(True, which="minor", linewidth=0.20, alpha=0.5)

        # # Limit the x-axis if needed
        # if xlimits is not None:
        #     ax.set_xlim(xlimits[0], xlimits[1])

        return fig, axes


class BinnedPlot(Plot):
    def _get_figure(self) -> tuple[Figure, list[Axes]]:
        linewidth = 0.7
        # Check for additional keyargs
        if self.cfg.plot_args is not None:
            plot_error = self.cfg.plot_args.get("show_error", False)
            plot_CE = self.cfg.plot_args.get("show_CE", False)
            subcases = self.cfg.plot_args.get("subcases", False)
            xscale = self.cfg.plot_args.get("xscale", "log")
        else:
            plot_error = False
            plot_CE = False
            subcases = False
            xscale = "log"

        # if subcases is used, nrows must be 1
        if subcases and (plot_CE or plot_error):
            raise ValueError("Subcases cannot be used with CE or error plots")

        # Set properties for the plot spacing
        if not plot_error and not plot_CE:
            gridspec_kw = {}
            nrows = 1
        elif plot_error and plot_CE:
            gridspec_kw = {"height_ratios": [4, 1, 1], "hspace": 0.13}
            nrows = 3
        elif plot_error and not plot_CE:
            raise NotImplementedError(
                "Plot without CE but with error is not implemented"
            )
        else:
            gridspec_kw = {"height_ratios": [3, 1], "hspace": 0.13}
            nrows = 2

        # Initiate plot
        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=1,
            sharex=True,
            # figsize=(18, 13.5),
            gridspec_kw=gridspec_kw,
        )

        # --- Main plot ---
        if nrows == 1:
            ax1 = axes
        else:
            ax1 = axes[0]
        # Ticks
        subs = (0.2, 0.4, 0.6, 0.8)
        ax1.set_xscale(xscale)
        ax1.set_yscale("log")
        ax1.set_ylabel(self.cfg.y_labels[0])
        if xscale == "log":
            ax1.xaxis.set_major_locator(LogLocator(base=10, numticks=15))
            ax1.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
            ax1.xaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))
            ax1.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))

        # --- Error Plot ---
        if plot_error:
            ax2 = axes[1]
            ax2.axhline(y=10, linestyle="--", color="black", linewidth=0.5)
            ax2.set_ylabel("1σ [%]")
            ax2.set_yscale("log")
            ax2.set_ylim(bottom=1, top=100)
            ax2.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
            ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs, numticks=12))

            if plot_CE:
                CE_ax = axes[2]
        elif plot_CE:
            CE_ax = axes[1]

        # --- Comparison Plot ---
        if plot_CE:
            CE_ax.axhline(y=1, linestyle="--", color="black", linewidth=0.5)
            CE_ax.set_ylabel("$T_i/R$")
            CE_ax.yaxis.set_major_locator(MultipleLocator(0.5))
            CE_ax.yaxis.set_minor_locator(AutoMinorLocator(5))
            CE_ax.set_ylim(bottom=0.3, top=1.7)

        # Generate X axis for bin properties

        # --- Plot Data ---
        for idx, (codelib, df) in enumerate(self.data):
            if subcases:
                dfs = []
                for subcase in subcases[1]:
                    subset = df[df[subcases[0]] == subcase]
                    if len(subset) == 0:
                        continue
                    dfs.append(subset)
            else:
                dfs = [df]

            for i, df1 in enumerate(dfs):
                x = np.array([0] + list(df1[self.cfg.x]))
                y = np.array([0] + list(df1[self.cfg.y]))

                err = np.array(df1["Error"])
                err_multi = np.array(y[1:]) * np.abs(err)

                # Main plot
                if idx > 0:
                    tag = "T" + str(idx) + ": "
                    linestyle = LINESTYLES[idx - 1]
                else:
                    tag = "R: "
                    linestyle = "-"

                if i == 0:
                    label = tag + codelib
                else:
                    label = None

                ax1.step(
                    x,
                    y,
                    label=label,
                    color=COLORS[idx],
                    linestyle=linestyle,
                    linewidth=linewidth,
                    where="pre",
                )
                newX = _get_error_x_pos(x)
                ax1.errorbar(
                    newX,
                    y[1:],
                    linewidth=0,
                    yerr=err_multi,
                    elinewidth=0.5,
                    color=COLORS[idx],
                )
                # add a label if needed (only one per group)
                if subcases and idx == 0:
                    ax1.text(
                        x[-1],
                        y[-1],
                        subcases[1][i],
                        fontsize=8,
                        verticalalignment="center",
                        horizontalalignment="right",
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
            if idx > 0 and plot_CE:
                ratio = df[self.cfg.y].values / self.data[0][1][self.cfg.y].values
                # Uniform plots actions
                CE_ax.step(
                    df[self.cfg.x].values,
                    ratio,
                    color=COLORS[idx],
                    linestyle=linestyle,
                    linewidth=linewidth,
                    where="pre",
                )

        # Final operations
        ax1.legend(loc="best")

        # --- Common Features ---
        if nrows == 1:
            axes = [ax1]

        for ax in axes:
            # Grid control
            ax.grid(alpha=0.5)
            ax.grid("True", which="minor", linewidth=0.25, alpha=0.5)
            # Ticks
            ax.tick_params(which="major", width=1.00, length=5)
            ax.tick_params(which="minor", width=0.75, length=2.50)

        return fig, axes


class CEPlot(Plot):
    def _get_figure(self) -> tuple[Figure, list[Axes]]:
        # Get optional data
        if self.cfg.plot_args is not None:
            subcases = self.cfg.plot_args.get("subcases", False)
            style = self.cfg.plot_args.get("style", "step")
            ce_limits = self.cfg.plot_args.get("ce_limits", None)
        else:
            subcases = False
            style = "step"
            ce_limits = None

        if style not in ["step", "point"]:
            raise ValueError(f"Style {style} not recognized")

        # compute the ratios
        if subcases:
            to_plot = []
            for codelib, df in self.data[1:]:
                to_plot.append(
                    (
                        codelib,
                        df.set_index([subcases[0], self.cfg.x])[self.cfg.y]
                        / self.data[0][1].set_index([subcases[0], self.cfg.x])[
                            self.cfg.y
                        ],
                    )
                )
        else:
            to_plot = [
                (
                    codelib,
                    df.set_index(self.cfg.x)[self.cfg.y]
                    / self.data[0][1].set_index(self.cfg.x)[self.cfg.y],
                )
                for (codelib, df) in self.data[1:]
            ]

        # Plot the data
        for idx, (codelib, df) in enumerate(to_plot):
            # Split the dfs into the subcases if needed
            if subcases:
                dfs = []
                for value in subcases[1]:
                    try:
                        subset = df.loc[value]
                    except KeyError:
                        continue
                    dfs.append((value, subset))
            else:
                dfs = [(None, df)]

            if idx == 0:
                gridspec_kw = {"hspace": 0.25}
                fig, ax = plt.subplots(
                    nrows=len(dfs), sharex=True, gridspec_kw=gridspec_kw
                )
                if len(dfs) == 1:
                    axes = [ax]
                else:
                    axes = ax

            for i, (case, df1) in enumerate(dfs):
                if i == 0:
                    label = codelib
                else:
                    label = None

                if idx == 0:  # operations to be performed only once per plot
                    axes[i].set_ylabel("C/E")
                    axes[i].set_title(case)
                    axes[i].axhline(y=1, linestyle="--", color="black")
                    axes[i].grid("True", which="major", linewidth=0.50, alpha=0.5)
                    axes[i].grid("True", which="minor", linewidth=0.20, alpha=0.5)
                    # limit the ax 2 to [0, 2]
                    axes[i].set_ylim(bottom=0, top=2)
                    # redo the ticks if there are more than one subcases
                    if len(dfs) > 1:
                        yticks = np.arange(0, 2.5, 0.5)
                        axes[i].set_yticks(yticks)

                if style == "step":
                    axes[i].step(
                        df1.index,
                        df1.values,
                        label=label,
                        color=COLORS[idx],
                        linestyle=LINESTYLES[idx],
                        linewidth=0.7,
                        where="pre",
                    )
                elif style == "point":
                    if ce_limits:
                        _apply_CE_limits(
                            ce_limits[0],
                            ce_limits[1],
                            df1.values,
                            df1.index,
                            axes[i],
                            idx,
                            label,
                        )
                    else:
                        ax.scatter(
                            df1.index,
                            df1.values,
                            label=label,
                            color=COLORS[idx],
                            marker=MARKERS[idx],
                            # the marker should be not filled
                            facecolors="none",
                        )

        # put the legend in the top right corner
        if not ce_limits:
            axes[0].legend()

        return fig, axes


class DoseContributionPlot(Plot):
    def _get_figure(self) -> tuple[Figure, Axes]:
        nrows = len(self.data)
        gridspec_kw = {"hspace": 0.25}
        fig, axes = plt.subplots(
            nrows=nrows, ncols=1, gridspec_kw=gridspec_kw, sharex=True
        )

        indices = []
        for idx, (codelib, df) in enumerate(self.data):
            df.set_index("User", inplace=True)
            indices.extend(df.index.to_list())

        # build a common index of isotopes so that the colors are the same for all
        # subplots
        isotopes = list(set(indices))
        isotopes.sort()

        for idx, isotope in enumerate(isotopes):
            if int(isotope) == 0:
                continue
            for i, (codelib, df) in enumerate(self.data):
                if i == 0:
                    _, label = LM.get_zaidname(str(abs(isotope)))
                else:
                    label = None

                tot_dose = df.groupby("Time", sort=False).sum()["Value"]
                try:
                    y = df.loc[isotope].set_index("Time")["Value"] / tot_dose * 100
                    times = y.index
                except KeyError:
                    continue  # not all libs have the same pathways

                axes[i].plot(
                    times,
                    y,
                    color=COLORS[idx],
                    marker=MARKERS[idx],
                    label=label,
                    linewidth=0.5,
                )

        for i, ax in enumerate(axes):
            # --- Plot details ---
            # ax details
            ax.set_title(codelib)
            ax.set_ylabel("SDDR [%]")
            ax.tick_params(which="major", width=1.00, length=5)
            ax.tick_params(axis="y", which="minor", width=0.75, length=2.50)
            # Grid
            ax.grid("True", axis="y", which="major", linewidth=0.50)
            ax.grid("True", axis="y", which="minor", linewidth=0.20)

        # Adjust legend to have multiple columns
        handles, labels = axes[0].get_legend_handles_labels()
        ncol = len(labels) // 20 + 1
        axes[0].legend(handles, labels, bbox_to_anchor=(1, 1), ncol=ncol)
        # plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        for label in axes[-1].get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
            label.set_rotation_mode("anchor")

        return fig, axes


class PlotFactory:
    @staticmethod
    def create_plot(
        plot_config: PlotConfig, data: list[tuple[str, pd.DataFrame]]
    ) -> Plot:
        if plot_config.plot_type == PlotType.BINNED:
            return BinnedPlot(plot_config, data)
        elif plot_config.plot_type == PlotType.RATIO:
            return RatioPlot(plot_config, data)
        elif plot_config.plot_type == PlotType.CE:
            return CEPlot(plot_config, data)
        elif plot_config.plot_type == PlotType.DOSE_CONTRIBUTION:
            return DoseContributionPlot(plot_config, data)
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


def _get_error_x_pos(x_array: np.ndarray) -> np.ndarray:
    oldX = x_array
    base = np.log(oldX[:-1])
    shifted = np.log(oldX[1:])
    newX = np.exp((base + shifted) / 2)
    newX[0] = (oldX[1] + oldX[0]) / 2
    return newX


def _apply_CE_limits(
    min: float | int,
    max: float | int,
    ydata: np.ndarray,
    xdata: np.ndarray,
    ax: Axes,
    idx: int,
    label: str | None,
):
    norm, upper, lower = _get_limits(min, max, ydata, xdata)
    ax.set_ylim(bottom=min - 0.1, top=max + 0.1)
    ax.axhline(y=max, linestyle="--", color="black", linewidth=0.5)
    ax.axhline(y=min, linestyle="--", color="black", linewidth=0.5)

    # first plot empty data to avoid changes in the x axis labels order
    ax.scatter(
        xdata,
        np.ones(len(xdata)),
        alpha=0,
    )

    # normal points
    ax.scatter(
        norm[0],
        norm[1],
        label=label,
        color=COLORS[idx],
        marker=MARKERS[idx],
        # the marker should be not filled
        facecolors="none",
    )
    # upper and lower limits
    ax.scatter(upper[0], upper[1], marker=CARETUPBASE, c=COLORS[idx], facecolors="none")
    ax.scatter(
        lower[0], lower[1], marker=CARETDOWNBASE, c=COLORS[idx], facecolors="none"
    )
    # additional legend
    leg = [
        Line2D(
            [0],
            [0],
            marker=CARETUPBASE,
            color="black",
            label=f"> {max}",
            markerfacecolor="black",
            markersize=8,
            lw=0,
        ),
        Line2D(
            [0],
            [0],
            marker=CARETDOWNBASE,
            color="black",
            label=f"< {min}",
            markerfacecolor="black",
            markersize=8,
            lw=0,
        ),
    ]
    handles, _ = ax.get_legend_handles_labels()
    combined = handles + leg

    if label is not None:
        ax.legend(handles=combined, loc="best")
