from __future__ import annotations

import math
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

    def plot(self) -> list[tuple[Figure, Axes | list[Axes]]]:
        """Plot the data according to the configuration. More than one plot can be
        produced in case overpopulation needs to be avoided.

        Returns
        -------
        list[tuple[Figure, Axes | list[Axes]]]
            list of matplotlib fig, ax couples produced
        """
        output = self._get_figure()
        if isinstance(output, tuple):
            output = [output]

        # it is rare than more than one figure is returned but it can happen to avoid
        # overpopulation
        newoutput = []
        for fig, axes in output:
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

            newoutput.append((fig, axes))
        return newoutput

    @abstractmethod
    def _get_figure(
        self,
    ) -> tuple[Figure, Axes | list[Axes]] | list[tuple[Figure, Axes | list[Axes]]]:
        pass

    def _build_rectangles(self, ax: Axes) -> None:
        """Build background rectangles on the plot according to the configuration"""
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
            bbox_to_anchor=(0.5, -0.15),
            fancybox=True,
            ncol=3,
            shadow=True,
        )
        # Normal legend needs to be reprinted
        ax.legend(loc="best")
        # And now the custom one
        ax.add_artist(additional_legend)

    def _add_vlines(self, ax: Axes) -> None:
        """Add vertical lines to the plot according to the configuration"""
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
        """Add text labels to the plot according to the configuration"""
        # major labels
        if self.cfg.additional_labels is None:
            return

        if "major" in self.cfg.additional_labels.keys():
            labels = self.cfg.additional_labels["major"]
            bbox_dic = {
                "boxstyle": "round,pad=0.5",
                "facecolor": "white",
                "alpha": 1,
            }
            _place_labels(labels, ax, 0.93, bbox=bbox_dic)

        if "minor" in self.cfg.additional_labels.keys():
            # minor labels
            labels = self.cfg.additional_labels["minor"]
            _place_labels(labels, ax, 0.87)


def _place_labels(
    labels: list[tuple[str, float | int]],
    ax: Axes,
    ypos_perc: float | int,
    bbox: dict | None = None,
) -> None:
    """Helper function to place labels on the correct position in the plot"""
    for label, xpos in labels:
        xmin, xmax = ax.get_xlim()
        if xpos < xmin or xpos > xmax:  # skip the label if not inside the x axis
            continue
        xpos_perc = (xpos - xmin) / (xmax - xmin)
        ax.text(xpos_perc, ypos_perc, label, transform=ax.transAxes, bbox=bbox)


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
        axes[0].set_ylabel(f"Ratio of {self.cfg.y_labels[0]} - (vs {self.data[0][0]})")

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
            scale_subcases = self.cfg.plot_args.get("scale_subcases", False)
        else:
            plot_error = False
            plot_CE = False
            subcases = False
            xscale = "log"
            scale_subcases = False

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

            scale_factor = 1
            for i, df1 in enumerate(dfs):
                x = np.array([0] + list(df1[self.cfg.x]))
                y = np.array([0] + list(df1[self.cfg.y]))
                if scale_subcases:
                    y = y * scale_factor

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
                    lbl = subcases[1][i]
                    if scale_factor != 1 and scale_subcases:
                        lbl += f" x{scale_factor:.0e}"
                    ax1.text(
                        x[int(len(x) / 2)],
                        y[int(len(y) / 2)],
                        lbl,
                        fontsize=8,
                        verticalalignment="center",
                        horizontalalignment="right",
                    )
                # Adjourn the scale factor
                scale_factor = scale_factor * 1e-1

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
                with np.errstate(divide="ignore", invalid="ignore"):
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
            shorten_x_name = self.cfg.plot_args.get("shorten_x_name", False)
            rotate_ticks = self.cfg.plot_args.get("rotate_ticks", False)
            xscale = self.cfg.plot_args.get("xscale", "linear")
        else:
            subcases = False
            style = "step"
            ce_limits = None
            shorten_x_name = False
            rotate_ticks = False
            xscale = "linear"

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

            # If this is the first lib, create the plot
            if idx == 0:
                gridspec_kw = {"hspace": 0.25}
                fig, ax = plt.subplots(
                    nrows=len(dfs), sharex=True, gridspec_kw=gridspec_kw
                )
                if len(dfs) == 1:
                    axes = [ax]
                else:
                    axes = ax

            # plot all subcases
            for i, (case, df1) in enumerate(dfs):
                if i == 0:
                    label = codelib
                else:
                    label = None

                if idx == 0:  # operations to be performed only once per plot
                    axes[i].set_ylabel("C/E")
                    axes[i].set_title(case, fontdict={"fontsize": "medium"})
                    axes[i].axhline(y=1, linestyle="--", color="black")
                    axes[i].grid("True", which="major", linewidth=0.50, alpha=0.5)
                    axes[i].grid("True", which="minor", linewidth=0.20, alpha=0.5)
                    axes[i].set_xscale(xscale)
                    # limit the ax 2 to [0, 2]
                    if ce_limits:
                        axes[i].set_ylim(bottom=ce_limits[0], top=ce_limits[1])
                        # redo the ticks if there are more than one subcases
                        axes[i].yaxis.set_major_locator(MultipleLocator(0.25))
                        axes[i].yaxis.set_minor_locator(AutoMinorLocator(2))

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

        # put the legend in the top right corner if it was not already placed
        if not axes[0].get_legend():
            axes[0].legend(bbox_to_anchor=(1, 1))

        # rotate ticks if requested
        if rotate_ticks:
            _rotate_ticks(axes[-1])
        if shorten_x_name:
            _shorten_x_name(axes[-1], shorten_x_name)

        return fig, axes


class DoseContributionPlot(Plot):
    def _get_figure(self) -> tuple[Figure, Axes]:
        nrows = len(self.data)
        gridspec_kw = {"hspace": 0.25}
        fig, axes = plt.subplots(
            nrows=nrows, ncols=1, gridspec_kw=gridspec_kw, sharex=True
        )
        if isinstance(axes, Axes):
            axes = [axes]

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
        _rotate_ticks(axes[-1])

        return fig, axes


class WavesPlot(Plot):
    def _get_figure(
        self,
    ) -> list[tuple[Figure, Axes | list[Axes]]]:
        # Get optional data
        if self.cfg.plot_args is not None:
            limits = self.cfg.plot_args.get("limits", [0, 1.5])
            shorten_x_name = self.cfg.plot_args.get("shorten_x_name", False)
        else:
            limits = [0, 1.5]
            shorten_x_name = False

        nrows = len(self.cfg.results)
        gridspec_kw = {"hspace": 0.30}

        # Since ratios are not defined if the ref lib is not available there will
        # be a unique common index. Exclude nan values
        common_index = self.data[0][1][self.cfg.x].dropna().unique()

        # split the coommon index into pieces of max 20 elements each
        common_index_chunks = []
        for i in range(0, len(common_index), 20):
            common_index_chunks.append(common_index[i : i + 20])

        output = []
        for index_chunk in common_index_chunks:
            fig, axes = plt.subplots(nrows=nrows, sharex=True, gridspec_kw=gridspec_kw)
            for idx_ax, result in enumerate(self.cfg.results):
                ax = axes[idx_ax]
                # This Should ensure that the x labels order is kept fixed
                ax.scatter(index_chunk, np.ones(len(index_chunk)), alpha=0)

                # ref value
                y_ref = (
                    self.data[0][1]
                    .set_index(["Result", self.cfg.x])
                    .loc[result][self.cfg.y]
                )
                ref_codelib = self.data[0][0]

                # actual plot of values
                for idx_tlib, (codelib, df) in enumerate(self.data[1:]):
                    if idx_ax == 0:
                        label = codelib
                    else:
                        label = None

                    tary = (
                        df.set_index(["Result", self.cfg.x]).loc[result][self.cfg.y]
                        / y_ref
                    )
                    if len(tary) == 1:  # constant value across the x axis
                        tary = pd.Series(tary.values * np.ones(len(index_chunk)))
                        tary.index = index_chunk
                    else:
                        # keep only the values that are in the index_chunk
                        tary = tary[tary.index.isin(index_chunk)]
                    # Plot everything
                    _apply_CE_limits(
                        limits[0],
                        limits[1],
                        tary.values,
                        tary.index,
                        ax,
                        idx_tlib,
                        label,
                    )

            for idx_ax, result in enumerate(self.cfg.results):
                ax = axes[idx_ax]
                # Write title
                ax.set_title(result)
                # Draw the ratio line
                ax.axhline(1, color="black", linestyle="--", linewidth=0.5)
                # Get minor ticks on the y axis
                ax.yaxis.set_minor_locator(AutoMinorLocator())
                # Ticks style
                ax.tick_params(which="major", width=1.00, length=5)
                ax.tick_params(which="minor", width=0.75, length=2.50)
                # Grid stylying
                ax.grid("True", which="major", linewidth=0.75, axis="y")
                ax.grid("True", which="minor", linewidth=0.30, axis="y")

            # put the label only in the middle y ax
            axes[len(axes) // 2].set_ylabel(f"Ratio vs {ref_codelib}")

            # Add the legend
            axes[0].legend(bbox_to_anchor=(1, 1), fancybox=True, shadow=True)

            # change the label text
            if shorten_x_name:
                _shorten_x_name(axes[-1], shorten_x_name)
            # Handle x and y global axes
            _rotate_ticks(axes[-1])

            output.append((fig, axes))

        return output


class BarPlot(Plot):
    def _get_figure(self) -> tuple[Figure, list[Axes]]:
        # Get optional data
        if self.cfg.plot_args is not None:
            log = self.cfg.plot_args.get("log", False)
            maxgroups = self.cfg.plot_args.get("max_groups", 20)
        else:
            log = False
            maxgroups = 20

        # Override log parameter if variation is low on y axis
        if log:
            spread = _checkYspread(self.data, self.cfg.y)
            if spread <= 2:  # less than 2 orders of magnitude
                log = False

        # # Assuming nobody will never print 20 libraries, will introduce a
        # # check though
        # single_width = 1 / len(self.data) - 0.05  # the width of the bars

        # Check if the data is higher than max
        labels = self.data[0][1][self.cfg.x].values
        nrows = len(labels) // maxgroups + 1
        if nrows == 1:
            nlabels = len(labels)
        else:
            nlabels = maxgroups

        # Concat all datasets
        to_concat = []
        for codelib, df in self.data:
            df["code-lib"] = codelib
            to_concat.append(df)
        global_df = pd.concat(to_concat)

        fig, axes = plt.subplots(nrows=nrows)
        if isinstance(axes, Axes):
            axes = [axes]
        # Compute the position of the labels in the different rows
        # and the datasets
        added_labels = 0
        for i in range(nrows):
            ax = axes[i]
            idx_chunk = labels[added_labels : added_labels + nlabels]
            df = global_df[global_df[self.cfg.x].isin(idx_chunk)]

            # Adjourn nlabels
            added_labels += nlabels
            if len(labels) - added_labels > maxgroups:
                nlabels = maxgroups
            else:
                nlabels = len(labels) - added_labels

            # plot
            sns.barplot(
                data=df,
                x=self.cfg.x,
                y=self.cfg.y,
                hue="code-lib",
                palette="dark",
                alpha=0.6,
                ax=ax,
            )
            if log:
                ax.set_yscale("log")
            ax.grid(True, which="major", linewidth=0.75, axis="y", alpha=0.5)
            ax.grid(True, which="minor", linewidth=0.30, axis="y", alpha=0.5)

        # By default seaborn is going to put the y label. delete all y label in axes
        for ax in axes:
            ax.set_ylabel("")
            ax.set_xlabel("")
            _rotate_ticks(ax)
            # delete the legend
            ax.get_legend().remove()

        # augment the padding between the axis depending on the max len of x ticks
        # labels
        for ax in axes[:-1]:
            max_label_len = max(
                [len(label.get_text()) for label in ax.get_xticklabels()]
            )
            fig.subplots_adjust(hspace=0.2 + 0.04 * max_label_len)
        # Since it may be multiple rows, the y label should only be in the middle one
        axes[len(axes) // 2].set_ylabel(self.cfg.y_labels[0])

        axes[-1].set_xlabel(self.cfg.x)
        axes[0].legend(loc="best")

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
        elif plot_config.plot_type == PlotType.WAVES:
            return WavesPlot(plot_config, data)
        elif plot_config.plot_type == PlotType.BARPLOT:
            return BarPlot(plot_config, data)
        else:
            raise NotImplementedError(
                f"Plot type {plot_config.plot_type} not implemented"
            )


# Aux functions
def _get_limits(
    lowerlimit: float | int,
    upperlimit: float | int,
    ydata: list | np.ndarray,
    xdata: list | np.ndarray,
):
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
    with np.errstate(divide="ignore", invalid="ignore"):
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


def _rotate_ticks(ax: Axes) -> None:
    # Handle x and y global axes
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
        label.set_rotation_mode("anchor")


def _shorten_x_name(ax: Axes, shorten_x_name: int) -> None:
    new_labels = []
    for label in ax.get_xticklabels():
        split = label.get_text().split("_")
        new_labels.append(" ".join(split[-shorten_x_name:]))
    ax.set_xticklabels(new_labels)


def _checkYspread(data: list[tuple[str, pd.DataFrame]], value_col: str):
    """
    Compute the min and max values across all datasets and return the spread

    """

    maxval = 0
    minval = 1e36

    for _, df in data:
        ymin = df[value_col].min()
        ymax = df[value_col].max()

        # If min is a negative value, spread computation loses meaning.
        if ymin < 0:
            return 1e36

        # adjourn max and min val across dataset
        minval = min(minval, ymin)
        maxval = max(maxval, ymax)

    # min val or max val could be 0 -> ValueError
    try:
        up = math.log10(ymax)
    except ValueError:
        up = 0

    try:
        down = math.log10(ymin)
    except ValueError:
        down = 0

    spread = up - down

    return spread
