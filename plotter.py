# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:44:45 2020

@author: Davide Laghi

Copyright 2021, the JADE Development Team. All rights reserved.

This file is part of JADE.

JADE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JADE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JADE.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import (LogLocator, AutoMinorLocator, MultipleLocator,
                               AutoLocator)
from matplotlib.markers import CARETUPBASE
from matplotlib.markers import CARETDOWNBASE
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from scipy.interpolate import interp1d
from matplotlib.patches import Rectangle


# ============================================================================
#                   Specify parameters for plots
# ============================================================================
SMALL_SIZE = 22
MEDIUM_SIZE = 26
BIGGER_SIZE = 30

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rc('lines', markersize=12)          # Marker default size

# ============================================================================
#                   Specific data for benchmarks plots
# ============================================================================

# --- TBM HCPB ---
TBM_HCPB_RECT = [['Void', 'White', 840, 850.3],
                 ['Eurofer97', '#377eb8', 850.3, 850.6],
                 ['Water cooled Eurofer97', '#ff7f00', 850.6, 851.3],
                 ['Eurofer97', '#377eb8', 851.3, 853.3],
                 ['Breeding Area pt1', '#4daf4a', 853.3, 855.4],
                 ['Breeding Area pt2', '#f781bf',  855.4, 859.9],
                 ['Breeding Area pt3', '#a65628', 859.9, 893.3],
                 ['Breeding Unit Pipework', '#984ea3', 893.3, 918.8],
                 ['Gap', '#999999', 918.8, 946.3],
                 ['SS316L(N)-IG/Water', '#e41a1c', 946.3, 1084.2]]
TBM_HCPB_RECT = pd.DataFrame(TBM_HCPB_RECT)
TBM_HCPB_RECT.columns = ['name', 'color', 'xmin', 'xmax']
XLIM_HCPB = (830, 1090)

# --- TBM WCLL ---
TBM_WCLL_RECT = [['Void', 'White', 840, 850.3],
                 ['Eurofer97', '#377eb8', 850.3, 850.6],
                 ['Water cooled Eurofer97', '#ff7f00', 850.6, 851.3],
                 ['Eurofer97', '#377eb8', 851.3, 853.3],
                 ['Breeding Area pt1', '#4daf4a', 853.3, 854.3],
                 ['Breeding Area pt2', '#f781bf',  854.3, 862.5],
                 ['Breeding Area pt3', '#a65628', 862.5, 903.4],
                 ['Breeding Unit Pipework', '#984ea3', 903.4, 918.8],
                 ['Gap', '#999999', 918.8, 946.3],
                 ['SS316L(N)-IG/Water', '#e41a1c', 946.3, 1084.2]]
TBM_WCLL_RECT = pd.DataFrame(TBM_WCLL_RECT)
TBM_WCLL_RECT.columns = ['name', 'color', 'xmin', 'xmax']
XLIM_WCLL = (830, 1090)

# --- ITER 1D ---
ADD_LABELS_ITER1D = {'major': [('INBOARD', 0.21), ('PLASMA', 0.45),
                               ('OUTBOARD', 0.70)],
                     'minor': [('TF Coil', 0.1), ('VV', 0.26),
                               ('FW/B/S', 0.37), ('FW/B/S', 0.55),
                               ('VV', 0.70), ('TF Coil', 0.87)]}
VERT_LINES_ITER1D = {'major': [49, 53], 'minor': [23, 32, 70, 84]}

# --- ITER CYLINDER SDDR ---
CYL_SDDR_XTICKS = {"'22-1'": 'Hole Front',
                   "'22-2'": 'Cyl. Front',
                   "'22-3'": 'Gap Front',
                   "'22-4'": 'SS Front',
                   "'23-1'": 'Hole Rear',
                   "'23-2'": 'Cyl. Rear',
                   "'23-3'": 'Gap Rear',
                   "'23-4'": 'SS Rear',
                   "'24-1'": 'P. Front (Hole)',
                   "'24-2'": 'P. Front (Cyl.)',
                   "'24-3'": 'P. Front (Gap)',
                   "'24-4'": 'SS Back Front',
                   "'25-1'": 'P. Rear (Hole)',
                   "'25-2'": 'P. Rear (Cyl.)',
                   "'25-3'": 'P. Rear (Gap)',
                   "'25-4'": 'SS Back Rear'}


# ============================================================================
#                   Plotter Class
# ============================================================================
class Plotter():
    def __init__(self, data, title, outpath, outname, quantity, unit, xlabel,
                 testname, ext='.png'):
        """
        Object Handling plots

        Parameters
        ----------
        data : list
            data = [data1, data2, ...]
            data1 = {'x': x data, 'y': y data, 'err': error data,
                     'ylabel': data label}
        title : str
            plot title
        outpath : str/path
            path to save image
        outname : str
            name of the image file
        quantity : str
            quantity of the y axis
        unit : str
            unit of the y axis
        xlabel : str
            name of the x axis
        testname : str
            name of the benchmark
        ext : str
            extension of the image to save. Default is '.png'

        Returns
        -------
        None.

        """
        self.data = data
        self.title = title
        self.outpath = os.path.join(outpath, outname+ext)
        self.xlabel = xlabel
        self.unit = unit
        self.quantity = quantity
        self.testname = testname

        # --- Useful plots parameters ---
        # plot decorators
        self.markers = ['o', 's', 'D', '^', 'X', 'p', 'd', '*']
        # Color-blind saver palette
        self.colors = ['#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
                       '#984ea3', '#999999', '#e41a1c', '#dede00']

    def plot(self, plot_type):
        # --- Binned Plot ---
        if plot_type == 'Binned graph':
            outp = self._binned_plot()

        # --- Ratio Plot ---
        elif plot_type == 'Ratio graph':
            if self.testname == 'ITER_1D':  # Special actions for ITER 1D
                outp = self._ratio_plot(additional_labels=ADD_LABELS_ITER1D,
                                        v_lines=VERT_LINES_ITER1D)
            elif self.testname == 'HCPB_TBM_1D':
                outp = self._ratio_plot(recs=TBM_HCPB_RECT, xlimits=XLIM_HCPB,
                                        markers=True)
            elif self.testname == 'WCLL_TBM_1D':
                outp = self._ratio_plot(recs=TBM_WCLL_RECT, xlimits=XLIM_WCLL,
                                        markers=True)
            else:
                outp = self._ratio_plot()

        # --- Experimental Points Plot ---
        elif plot_type == 'Experimental points':
            outp = self._exp_points_plot()

        # --- Experimental Points Plot ---
        elif plot_type == 'Discreet Experimental points':
            outp = self._exp_points_discreet_plot()

        # --- Grouped bars chart ---
        elif plot_type == 'Grouped bars':
            if self.testname == 'C_Model':
                log = True
                xlegend = None
            elif self.testname == 'ITER_Cyl_SDDR':
                log = True
                xlegend = CYL_SDDR_XTICKS
            else:
                log = False
                xlegend = None

            outp = self._grouped_bar(log=log, xlegend=xlegend)

        # --- Waves plot ---
        elif plot_type == 'Waves':
            outp = self._waves()

        # --- Deafault ---
        else:
            raise ValueError(plot_type+' is not an admissible plot type')

        return outp

    def _waves(self, upperlimit=1.5, lowerlimit=0.5):
        """
        Built a multirow ratio that correlates different results on the same
        x bin

        Parameters
        ----------
        upperlimit: float
            set the y upper limit for the ratio plot
        lowerlimit: float
            set the y lower limit for the ratio plot

        Returns
        -------
        outpath
            path to the saved image.

        """
        nrows = len(self.quantity)
        fig, axes = plt.subplots(figsize=(18, 13.5), nrows=nrows, sharex=True)
        fig.suptitle(self.title, weight='bold')

        # common to all axes
        for i, ax in enumerate(axes):
            # Plot
            refy = np.array(self.data[0]['y'][i])
            for j, libdata in enumerate(self.data[1:]):
                tary = np.array(libdata['y'][i])
                y = tary/refy
                # Compute the plot limits
                norm, upper, lower = _get_limits(lowerlimit, upperlimit,
                                                 y, libdata['x'])
                # This Should ensure that the x labels order is kept fixed
                axes[i].scatter(libdata['x'], np.ones(len(libdata['x'])),
                                alpha=0)
                # Plot everything
                axes[i].scatter(norm[0], norm[1], color=self.colors[j],
                                marker=self.markers[i],
                                label=libdata['ylabel'])
                axes[i].scatter(upper[0], upper[1], marker=CARETUPBASE,
                                c=self.colors[j])
                axes[i].scatter(lower[0], lower[1], marker=CARETDOWNBASE,
                                c=self.colors[j])

            # Write title
            ax.set_title('{}'.format(self.quantity[i]))
            # Draw the ratio line
            ax.axhline(1, color='black', linestyle='--')
            # Get minor ticks on the y axis
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            # Ticks style
            ax.tick_params(which='major', width=1.00, length=5)
            ax.tick_params(which='minor', width=0.75, length=2.50)
            # Grid stylying
            ax.grid('True', which='major', linewidth=0.75, axis='y')
            ax.grid('True', which='minor', linewidth=0.30, axis='y')
            # limits
            toadd = (upperlimit-lowerlimit)/8
            ax.set_ylim(lowerlimit-toadd, upperlimit+toadd)
            ax.axhline(lowerlimit, color='red', linewidth=0.5)
            ax.axhline(upperlimit, color='red', linewidth=0.5)

        # Add the legend
        axes[0].legend(loc='upper center', bbox_to_anchor=(0.88, 1.5),
                       fancybox=True, shadow=True)
        # Handle x and y global axes
        plt.setp(axes[2].get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        axes[-1].set_xlabel(self.xlabel)

        return self._save()

    def _grouped_bar(self, log=False, maxgroups=35, xlegend=None):
        """
        Plot a grouped bar chart on a "categorical" x axis.

        Parameters
        ----------
        log : Bool, optional
            if True the y-axis is set to be logaritimic. The default is False.
        maxgroups : int, optional
            indicated the maximum number of grouped bars to plot in a single
            axis. In case the data to plot is higher, new axis are created
            vertically. The default is 30.
        xlegend : dic, optional
            allows to change the x ticks labels for better plot clarity.
            The default is None.

        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        # Override x ticks labels if requested
        if xlegend is None:
            labels = self.data[0]['x']
        else:
            labels = []
            for lab in self.data[0]['x']:
                lab = repr(lab)
                try:
                    labels.append(xlegend[lab])
                except KeyError:
                    labels.append(lab)

        single_width = 0.35  # the width of the bars
        tot_width = single_width*len(self.data)

        # Check if the data is higher than max
        if len(labels) > maxgroups:
            nrows = int(len(labels)/maxgroups)+1  # rows of the plot
            nlabels = maxgroups  # number of labels in first row
        else:
            nlabels = len(labels)  # number of labels in first row
            nrows = 1

        # Compute the position of the labels in the different rows
        # and the datasets
        x_array = []
        datasets = []
        label_chunks = []
        added_labels = 0
        for i in range(nrows):
            x = np.arange(nlabels)  # the label locations
            x_array.append(x)
            lab_chunk = labels[added_labels: added_labels+nlabels]
            label_chunks.append(lab_chunk)
            # Select the correspondent dataset
            data = []
            for libdata in self.data:
                chunks = {}
                for key, item in libdata.items():
                    if key == 'ylabel':
                        chunks[key] = item
                    else:
                        chunks[key] = item[added_labels: added_labels+nlabels]

                data.append(chunks)
            datasets.append(data)

            # Adjourn nlabels
            added_labels += nlabels
            if len(labels)-added_labels > maxgroups:
                nlabels = maxgroups
            else:
                nlabels = len(labels)-added_labels

        # Initialize plot
        fig, axes = plt.subplots(figsize=(18, 13.5), nrows=nrows)

        # Always want axes as a list even if it is only one
        try:
            iterator = iter(axes)
        except TypeError:
            # not iterable
            axes = [axes]

        # --- Plotting ---
        # Set the title only in the top ax
        axes[0].set_title(self.title)

        # Plot everything
        for ax, datachunk, x, labels in zip(axes, datasets, x_array,
                                            label_chunks):
            pos = -tot_width/2
            for dataset in datachunk:
                ax.bar(x + pos, dataset['y'], single_width,
                       label=dataset['ylabel'],
                       yerr=dataset['err']*dataset['y'],
                       align='edge')
                pos = pos+single_width  # Adourn relative position

            # log scale optional
            if log:
                ax.set_yscale('log')
                ax.yaxis.set_major_locator(LogLocator())
            else:
                ax.yaxis.set_major_locator(AutoLocator())

            # --- Plot details ---
            # Legend and ticks
            ax.legend(loc='best')
            ax.tick_params(which='major', width=1.00, length=5)
            ax.tick_params(which='minor', width=0.75, length=2.50)

            # title and labels
            ylabel = self.quantity+' ['+self.unit+']'
            ax.set_ylabel(ylabel)
            ax.set_xlabel(self.xlabel)

            # Special for x labels
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=60)

            # Grid
            ax.grid('True', which='major', linewidth=0.75, axis='y')
            ax.grid('True', which='minor', linewidth=0.30, axis='y')

        return self._save()

    def _exp_points_plot(self, y_scale='log'):
        """
        Plot a simple plot that compares experimental data points with
        computational calculation.

        Also a C/E plot is added

        Parameters
        ----------
        y_scale: str
            acceppted values are the ones of matplotlib.axes.Axes.set_yscale
            e.g. "linear", "log", "symlog", "logit", ... The default is 'log'.

        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        data = self.data

        ref = data[0]
        # Adjounrn ylabel
        ylabel = self.quantity+' ['+self.unit+']'

        # Grid info
        gridspec_kw = {'height_ratios': [3, 1], 'hspace': 0.13}
        figsize = (18, 13.5)

        # Initialize plot
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True,
                                 figsize=figsize,
                                 gridspec_kw=gridspec_kw)

        ax1 = axes[0]
        ax2 = axes[1]

        # Plot referece
        ax1.plot(ref['x'], ref['y'], 's', color=self.colors[0],
                 label=ref['ylabel'])
        # Get the linear interpolation for C/E
        interpolate = interp1d(ref['x'], ref['y'], fill_value=0,
                               bounds_error=False)

        # Plot all data
        try:
            for i, dic in enumerate(data[1:]):
                # Plot the flux
                ax1.plot(dic['x'], dic['y'], color=self.colors[i+1],
                         drawstyle='steps-mid', label=dic['ylabel'])
                # plot the C/E
                interp_ref = interpolate(dic['x'])
                ax2.plot(dic['x'], dic['y']/interp_ref, color=self.colors[i+1],
                         drawstyle='steps-mid', label=dic['ylabel'])
        except KeyError:
            # it is a single pp
            return self._save()

        # --- Plot details ---
        # ax 1 details
        ax1.set_yscale(y_scale)
        ax1.set_title(self.title)
        ax1.set_ylabel(ylabel)
        ax1.legend(loc='best')

        # limit the ax 2 to [0, 2]
        ax2.set_ylim(bottom=0, top=2)
        ax2.set_ylabel('C/E')
        ax2.set_xlabel(self.xlabel)
        ax2.axhline(y=1, linestyle='--', color='black')
        # # Draw the exp error
        # ax2.fill_between(ref['x'], 1+ref['err'], 1-ref['err'], alpha=0.2)

        # Common for all axes
        for ax in axes:
            ax.set_xscale('log')

        # # Tiks positioning and dimensions
        # ax.xaxis.set_major_locator(AutoLocator())
        # ax.yaxis.set_major_locator(AutoLocator())
        # ax.xaxis.set_minor_locator(AutoMinorLocator())
        # ax.yaxis.set_minor_locator(AutoMinorLocator())

            ax.tick_params(which='major', width=1.00, length=5)
            ax.tick_params(which='minor', width=0.75, length=2.50)

            # Grid
            ax.grid('True', which='major', linewidth=0.50)
            ax.grid('True', which='minor', linewidth=0.20)

        return self._save()

    def _exp_points_discreet_plot(self, y_scale='log', lowerlimit=0.5,
                                  upperlimit=1.5):
        """
        Plot a simple plot that compares experimental data points with
        computational calculation. Differently from _exp_points_plot here
        the computational results are reported in a descreet format.

        Also a C/E plot is added

        Parameters
        ----------
        y_scale: str
            acceppted values are the ones of matplotlib.axes.Axes.set_yscale
            e.g. "linear", "log", "symlog", "logit", ... The default is 'log'.
        upperlimit: float
            set the y upper limit for the ratio plot
        lowerlimit: float
            set the y lower limit for the ratio plot

        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        data = self.data

        # Adjourn ylabel
        ylabel = self.quantity+' ['+self.unit+']'

        # Grid info
        gridspec_kw = {'height_ratios': [3, 1], 'hspace': 0.13}
        figsize = (18, 13.5)

        # Initialize plot
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True,
                                 figsize=figsize,
                                 gridspec_kw=gridspec_kw)

        ax1 = axes[0]
        ax2 = axes[1]

        ref_x = data[0]['x']
        ref_y = data[0]['y']

        # -- Main plot --
        for i, libdata in enumerate(data):
            x = libdata['x']
            y = libdata['y']
            err = libdata['err']
            label = libdata['ylabel']

            ax1.errorbar(x, y, yerr=err, marker=self.markers[i], linestyle='',
                         capsize=10, color=self.colors[i], label=label)

        # -- C/E --
        for i, libdata in enumerate(data[1:]):
            x = libdata['x']
            y = libdata['y']
            label = libdata['ylabel']
            assert x == ref_x

            # Compute the plot limits
            norm, upper, lower = _get_limits(lowerlimit, upperlimit,
                                             y/ref_y, x)
            # This Should ensure that the x labels order is kept fixed
            ax2.scatter(x, np.ones(len(x)), alpha=0)
            # Plot everything
            ax2.scatter(norm[0], norm[1], color=self.colors[i+1],
                        marker=self.markers[i+1], label=label)
            ax2.scatter(upper[0], upper[1], marker=CARETUPBASE,
                        c=self.colors[i+1])
            ax2.scatter(lower[0], lower[1], marker=CARETDOWNBASE,
                        c=self.colors[i+1])

        # --- Plot details ---
        # ax 1 details
        ax1.set_yscale(y_scale)
        ax1.set_title(self.title)
        ax1.set_ylabel(ylabel)
        ax1.legend(loc='best')

        # ax 2 details
        toadd = (upperlimit-lowerlimit)/8
        ax2.set_ylim(bottom=lowerlimit-toadd, top=upperlimit+toadd)
        ax2.set_ylabel('C/E')
        ax2.set_xlabel(self.xlabel)
        ax2.axhline(y=1, linestyle='--', color='black')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        ax2.axhline(lowerlimit, color='red', linewidth=0.5)
        ax2.axhline(upperlimit, color='red', linewidth=0.5)

        # Common for all axes
        for ax in axes:

            ax.tick_params(which='major', width=1.00, length=5)
            ax.tick_params(which='minor', width=0.75, length=2.50)

            # Grid
            ax.grid('True', which='major', linewidth=0.50)
            ax.grid('True', which='minor', linewidth=0.20)

        return self._save()

    def _ratio_plot(self, additional_labels=None, v_lines=None, recs=None,
                    xlimits=None, markers=False):
        """
        Plot a ratio plot where all data dictionaries are plotted against the
        first one which is used as reference

        Parameters
        ----------
        additional_labels : dic, optional
            contains additional tags to print in the plot.
            {'major': [(label, xpos), ...], 'minor': [(label, xpos), ...]}.
            The default is None.
        v_lines : dic, optional
            contains additional vertical lines to plot.
            {'major': [xpos, ...], 'minor': [xpos, ...]}.
            The default is None.
        recs : pd.DataFrame, optional
            contains the data to draw rectangles on the plot. Columns values
            are ['name', 'color', 'xmin', 'xmax']. The default is None
        xlimits : tuple
            (xmin, xmax). The default is None.
        markers : bool
            if True markers are applied to the line plots.
            The default is False.

        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        data = self.data

        ref = data[0]
        # Adjounrn ylabel
        ylabel = 'Ratio of '+self.quantity+' (vs. '+ref['ylabel']+')'

        # Initialize plot
        fig, ax = plt.subplots(figsize=(16, 9))

        # Plot all data
        y_max = 0
        y_min = 0
        try:
            for i, dic in enumerate(data[1:]):
                y = dic['y']/ref['y']
                # Adjourn y max and min
                if i == 0:
                    y_max = max(y)
                    y_min = min(y)
                else:
                    if max(y) > y_max:
                        y_max = max(y)
                    if min(y) < y_min:
                        y_min = y_min
                # Plot
                if markers:
                    marker = self.markers[i]
                else:
                    marker = None
                ax.plot(dic['x'], y, color=self.colors[i],
                        drawstyle='steps-mid', label=dic['ylabel'],
                        marker=marker)

        except KeyError:
            # it is a single pp
            return self._save()

        # Plot details
        ax.set_title(self.title)
        ax.legend(loc='best')
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(ylabel)

        # Tiks positioning and dimensions
        ax.xaxis.set_major_locator(AutoLocator())
        ax.yaxis.set_major_locator(AutoLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        ax.tick_params(which='major', width=1.00, length=5)
        ax.tick_params(which='minor', width=0.75, length=2.50)

        # Grid
        ax.grid('True', which='major', linewidth=0.50)
        ax.grid('True', which='minor', linewidth=0.20)

        # Add additional labels if requested
        if additional_labels is not None:
            # major labels
            labels = additional_labels['major']
            for label, xpos in labels:
                bbox_dic = {'boxstyle': 'round,pad=0.5', 'facecolor': 'white',
                            'alpha': 1}
                ax.text(xpos, 0.95, label,
                        bbox=bbox_dic, transform=ax.transAxes)

            # minor labels
            labels = additional_labels['minor']
            for label, xpos in labels:
                ax.text(xpos, 0.87, label, transform=ax.transAxes)

        # Add vertical lines if requested
        if v_lines is not None:
            # major lines
            lines = v_lines['major']
            for line in lines:
                ax.axvline(line, color='black')

            # minor lines
            lines = v_lines['minor']
            for line in lines:
                ax.axvline(line, color='black', ymin=0.10, ymax=0.90,
                           linestyle='--', linewidth=1)

        # Add Rectangles if requested
        if recs is not None:
            # Plot the rects
            height = y_max-y_min
            _add_recs(ax, recs, height, y_origin=y_min)

            # Build the additional legend
            # Drop duplicates
            df = TBM_HCPB_RECT[['color', 'name']].drop_duplicates()
            legend_elements = []
            for key, row in df.iterrows():
                patch = Patch(facecolor=row['color'], edgecolor='black',
                              label=row['name'], alpha=0.2)
                legend_elements.append(patch)

            additional_legend = ax.legend(handles=legend_elements,
                                          loc='upper center',
                                          bbox_to_anchor=(0.5, -0.1),
                                          fancybox=True,
                                          ncol=5,
                                          shadow=True)
            # Normal legend needs to be reprinted
            ax.legend(loc='best')
            # And now the custom one
            ax.add_artist(additional_legend)

        # Limit the x-axis if needed
        if xlimits is not None:
            ax.set_xlim(xlimits[0], xlimits[1])

        return self._save()

    def _binned_plot(self, normalize=False):
        """
        PLot composed by three subplots.
        Main plot -> binned values (e.g. a flux in energies)
        Error plot -> statistical error
        Ratio plot (Optional) -> ratio among reference and target values

        Parameters
        ----------

        Returns
        -------
        outpath : str/path
            path to the saved image

        """

        # General parameters
        data = self.data
        title = self.title
        colors = self.colors
        ylabel = self.quantity+' ['+self.unit+']'
        if len(data) > 1:
            nrows = 3
        else:
            nrows = 2

        # Set properties for the plot spacing
        if len(data) > 1:
            gridspec_kw = {'height_ratios': [4, 1, 1], 'hspace': 0.13}
        else:
            gridspec_kw = {'height_ratios': [4, 1], 'hspace': 0.13}
        # Initiate plot
        fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True,
                                 figsize=(18, 13.5),
                                 gridspec_kw=gridspec_kw)

        # --- Main plot ---
        ax1 = axes[0]
        ax1.set_title(title)
        # Labels
        ax1.set_ylabel(ylabel)

        # Ticks
        subs = (0.2, 0.4, 0.6, 0.8)
        ax1.set_xscale('log')

        ax1.set_yscale('log')
        ax1.xaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax1.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax1.xaxis.set_minor_locator(LogLocator(base=10.0, subs=subs,
                                               numticks=12))
        ax1.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs,
                                               numticks=12))

        # --- Error Plot ---
        ax2 = axes[1]
        ax2.axhline(y=10, linestyle='--', color='black')
        ax2.set_ylabel('1σ [%]', labelpad=35)
        ax2.set_yscale('log')
        ax2.set_ylim(bottom=0, top=100)
        ax2.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs,
                                               numticks=12))

        # --- Comparison Plot ---
        if len(data) > 1:
            ax3 = axes[2]
            ax3.axhline(y=1, linestyle='--', color='black')
            ax3.set_ylabel('$T_i/R$', labelpad=30)
            ax3.yaxis.set_major_locator(MultipleLocator(0.5))
            ax3.yaxis.set_minor_locator(AutoMinorLocator(5))
            ax3.axhline(y=2, linestyle='--', color='red', linewidth=0.5)
            ax3.axhline(y=0.5, linestyle='--', color='red', linewidth=0.5)
            ax3.set_ylim(bottom=0.3, top=2.2)

        # Generate X axis for bin properties
        oldX = np.array([0]+list(data[0]['x']))
        base = np.log(oldX[:-1])
        shifted = np.log(oldX[1:])
        newX = np.exp((base+shifted)/2)
        newX[0] = (oldX[1]+oldX[0])/2
        # --- Plot Data ---
        for idx, dic_data in enumerate(data):

            x = np.array([0]+list(dic_data['x']))
            y = np.array([0]+list(dic_data['y']))

            if normalize:
                # Find global area
                hist_areas = np.diff(x)*y[1:]
                tot_area = hist_areas.sum()
                # Normalize values
                y = [0]+list(np.diff(x)*y[1:]/tot_area)

            err = np.array(dic_data['err'])
            err_multi = np.array(y[1:])*np.abs(err)

            # Main plot
            if idx > 0:
                tag = 'T'+str(idx)+': '
            else:
                tag = 'R: '
            ax1.step(x, y, label=tag+dic_data['ylabel'], color=colors[idx])
            ax1.errorbar(newX, y[1:], linewidth=0,
                         yerr=err_multi, elinewidth=0.5, color=colors[idx])

            # Error Plot
            ax2.plot(newX, np.array(dic_data['err'])*100, 'o',
                     label=dic_data['ylabel'], markersize=2,
                     color=colors[idx])

            # Comparison
            if len(data) > 1:
                for idx, dic_data in enumerate(data[1:]):
                    ratio = np.array(dic_data['y'])/np.array(data[0]['y'])
                    # Uniform plots actions
                    norm, upper, lower = _get_limits(0.5, 2, ratio, newX)

                    ax3.plot(norm[0], norm[1], 'o', markersize=2,
                             color=colors[idx+1])
                    ax3.scatter(upper[0], upper[1], marker=CARETUPBASE, s=50,
                                c=colors[idx+1])
                    ax3.scatter(lower[0], lower[1], marker=CARETDOWNBASE, s=50,
                                c=colors[idx+1])

                # Build ax3 legend
                leg = [Line2D([0], [0], marker=CARETUPBASE, color='black',
                              label='> 2', markerfacecolor='black',
                              markersize=8, lw=0),
                       Line2D([0], [0], marker=CARETDOWNBASE,
                              color='black', label='< 0.5',
                              markerfacecolor='black', markersize=8, lw=0)]
                ax3.legend(handles=leg, loc='best')

        # Final operations
        ax1.legend(loc='best')
        axes[-1].set_xlabel(self.xlabel)

        # --- Common Features ---
        for ax in axes:
            # Grid control
            ax.grid()
            ax.grid('True', which='minor', linewidth=0.25)
            # Ticks
            ax.tick_params(which='major', width=1.00, length=5)
            ax.tick_params(which='minor', width=0.75, length=2.50)

        return self._save()

    def _save(self):
        plt.tight_layout()

        plt.savefig(self.outpath, bbox_inches='tight')
        plt.close()

        return self.outpath


# ============================================================================
#                   Useful Plotting Functions
# ============================================================================
# colors = ['white', '#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
#           '#984ea3', '#999999', '#e41a1c', '#dede00', '#b83739', '#7d751d',
#           '#00ffee', '#96448a', '#b6fcd5', '#ff7f50', '#4b3832', '#cccc00',
#           '#660066']
def _add_recs(ax, rec_data, height, y_origin=0):
    """
    Given rectangles data add them to a specific pyplot.Ax

    Parameters
    ----------
    ax : matplotlib.pyplot.Ax
        Ax onto which add the rectangles.
    rec_data : pd.DataFrame
        table data for the rectangles.
    height : float
        height of the rectangles (in ax y-unit).
    y_origin : float, optional
        y origin for the rectangles (in ax y-unit). The default is 0.

    Returns
    -------
    None.

    """

    for _, rec in rec_data.iterrows():
        # Create the rectangle
        width = rec['xmax']-rec['xmin']
        origin = (rec['xmin'], y_origin)
        color = rec['color']

        rectangle = Rectangle(origin, width=width, height=height,
                              color=color, alpha=0.2)
        ax.add_patch(rectangle)


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
    # ensure data is array
    ydata = np.array(ydata)
    xdata = np.array(xdata)
    # Get the three logical maps
    upmap = ydata > upperlimit
    lowmap = ydata < lowerlimit
    normalmap = np.logical_and(np.logical_not(upmap),
                               np.logical_not(lowmap))

    # Apply maps to divide the original sets
    normalY = ydata[normalmap]
    normalX = xdata[normalmap]

    upperX = xdata[upmap]
    upperY = np.full(len(upperX), upperlimit)

    lowerX = xdata[lowmap]
    lowerY = np.full(len(lowerX), lowerlimit)

    return (normalX, normalY), (upperX, upperY), (lowerX, lowerY)
