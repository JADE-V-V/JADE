# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:44:45 2020

@author: Davide Laghi
"""
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (LogLocator, AutoMinorLocator, MultipleLocator,
                               AutoLocator)
from matplotlib.markers import CARETUPBASE
from matplotlib.markers import CARETDOWNBASE
from matplotlib.lines import Line2D
from scipy.interpolate import interp1d


class Plotter():
    def __init__(self, data, title, outpath, outname, quantity, unit, xlabel,
                 testname, ext='.png', fontsize=20):
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
        fontsize : int
            reference fontsize to be used throughout the plot. The Default is
            20

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
        self.fontsize = fontsize
        self.testname = testname

        # --- Useful plots parameters ---
        # plot decorators
        self.markers = ['o', 's', 'X', 'p', 'D', '^', 'd', '*']
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
                a_l = {'major': [('INBOARD', 0.21), ('PLASMA', 0.45),
                                 ('OUTBOARD', 0.70)],
                       'minor': [('TF Coil', 0.1), ('VV', 0.26),
                                 ('FW/B/S', 0.37), ('FW/B/S', 0.55),
                                 ('VV', 0.70), ('TF Coil', 0.87)]}
                v_lines = {'major': [49, 53], 'minor': [23, 32, 70, 84]}

                outp = self._ratio_plot(additional_labels=a_l, v_lines=v_lines)
            else:
                outp = self._ratio_plot()
        
        # --- Experimental Points Plot ---
        elif plot_type == 'Experimental points':
            outp = self._exp_points_plot()
        else:
            raise ValueError(plot_type+' is not an admissible plot type')

        return outp

    def _exp_points_plot(self):
        """
        Plot a simple plot that compares experimental data points with
        computational calculation.
        
        Also a C/E plot is added

        Parameters
        ----------


        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        data = self.data
        fontsize = self.fontsize

        ref = data[0]
        # Adjounrn ylabel
        ylabel = self.quantity+' ['+self.unit+']'
        
        # Grid info
        gridspec_kw = {'height_ratios': [4, 1], 'hspace': 0.13}
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
        ax1.set_yscale('log')
        ax1.set_title(self.title, fontsize=fontsize+4)
        ax1.set_ylabel(ylabel).set_fontsize(fontsize)
        ax1.legend(loc='best', prop={'size': fontsize-5})
        
        # limit the ax 2 to +- 50%
        ax2.set_ylim(bottom=0.5, top=1.5)
        ax2.set_ylabel('C/E').set_fontsize(fontsize)
        ax2.set_xlabel(self.xlabel).set_fontsize(fontsize)
        ax2.axhline(y=1, linestyle='--', color='black')
        
        # Common for all axes
        for ax in axes:
            ax.set_xscale('log')

        # # Tiks positioning and dimensions
        # ax.xaxis.set_major_locator(AutoLocator())
        # ax.yaxis.set_major_locator(AutoLocator())
        # ax.xaxis.set_minor_locator(AutoMinorLocator())
        # ax.yaxis.set_minor_locator(AutoMinorLocator())

            ax.tick_params(which='major', width=1.00, length=5,
                           labelsize=fontsize-2)
            ax.tick_params(which='minor', width=0.75, length=2.50)
    
            # Grid
            ax.grid('True', which='major', linewidth=0.50)
            ax.grid('True', which='minor', linewidth=0.20)

        return self._save()

    def _ratio_plot(self, additional_labels=None, v_lines=None):
        """
        Plot a ratio plot where all data dictionaries are plotted against the
        first one which is used as reference

        Parameters
        ----------
        additional_labels : dic
            contains additional tags to print in the plot.
            {'major': [(label, xpos), ...], 'minor': [(label, xpos), ...]}.
            The default is None
        v_lines : dic
            contains additional vertical lines to plot.
            {'major': [xpos, ...], 'minor': [xpos, ...]}.
            The default is None

        Returns
        -------
        outpath : str/path
            path to the saved image

        """
        data = self.data
        fontsize = self.fontsize

        ref = data[0]
        # Adjounrn ylabel
        ylabel = 'Ratio of '+self.quantity+' (vs. '+ref['ylabel']+')'

        # Initialize plot
        fig, ax = plt.subplots(figsize=(16, 9))

        # Plot all data
        try:
            for i, dic in enumerate(data[1:]):
                ax.plot(dic['x'], dic['y']/ref['y'], color=self.colors[i],
                        drawstyle='steps-mid', label=dic['ylabel'])

        except KeyError:
            # it is a single pp
            return self._save()

        # Plot details
        ax.set_title(self.title, fontsize=fontsize+4)
        ax.legend(loc='best', prop={'size': fontsize-5})
        ax.set_xlabel(self.xlabel).set_fontsize(fontsize)
        ax.set_ylabel(ylabel).set_fontsize(fontsize)

        # Tiks positioning and dimensions
        ax.xaxis.set_major_locator(AutoLocator())
        ax.yaxis.set_major_locator(AutoLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        ax.tick_params(which='major', width=1.00, length=5,
                       labelsize=fontsize-2)
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
                ax.text(xpos, 0.95, label, fontsize=fontsize-5,
                        bbox=bbox_dic, transform=ax.transAxes)

            # minor labels
            labels = additional_labels['minor']
            for label, xpos in labels:
                ax.text(xpos, 0.87, label, fontsize=fontsize-6,
                        transform=ax.transAxes)

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
        fontsize = 30  # fontsize for text in plot
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
        ax1.set_title(title, fontsize=fontsize+4)
        # Labels
        ax1.set_ylabel(ylabel).set_fontsize(fontsize)  # Y axis label

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
        ax2.set_ylabel('1σ [%]', labelpad=35).set_fontsize(fontsize)
        ax2.set_yscale('log')
        ax2.set_ylim(bottom=0, top=100)
        ax2.yaxis.set_major_locator(LogLocator(base=10, numticks=15))
        ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=subs,
                                               numticks=12))

        # --- Comparison Plot ---
        if len(data) > 1:
            ax3 = axes[2]
            ax3.axhline(y=1, linestyle='--', color='black')
            ax3.set_ylabel('$T_i/R$', labelpad=30).set_fontsize(fontsize)
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
                    starmap1 = ratio > 2
                    starmap2 = ratio < 0.5
                    normalmap = np.logical_and(np.logical_not(starmap1),
                                               np.logical_not(starmap2))
                    normalY = ratio[normalmap]
                    normalX = newX[normalmap]
                    starX1 = newX[starmap1]
                    starY1 = np.full(len(starX1), 2)
                    starX2 = newX[starmap2]
                    starY2 = np.full(len(starX2), 0.5)

                    ax3.plot(normalX, normalY, 'o', markersize=2,
                             color=colors[idx+1])
                    ax3.scatter(starX1, starY1, marker=CARETUPBASE, s=50,
                                c=colors[idx+1])
                    ax3.scatter(starX2, starY2, marker=CARETDOWNBASE, s=50,
                                c=colors[idx+1])

                # Build ax3 legend
                leg = [Line2D([0], [0], marker=CARETUPBASE, color='black',
                              label='> 2', markerfacecolor='black',
                              markersize=8, lw=0),
                       Line2D([0], [0], marker=CARETDOWNBASE,
                              color='black', label='< 0.5',
                              markerfacecolor='black', markersize=8, lw=0)]
                ax3.legend(handles=leg, loc='best',
                           prop={'size': fontsize-15})

        # Final operations
        ax1.legend(loc='best', prop={'size': fontsize-5})
        axes[-1].set_xlabel(self.xlabel).set_fontsize(fontsize)

        # --- Common Features ---
        for ax in axes:
            # Grid control
            ax.grid()
            ax.grid('True', which='minor', linewidth=0.25)
            # Ticks
            ax.tick_params(which='major', width=1.00, length=5,
                           labelsize=fontsize-2)
            ax.tick_params(which='minor', width=0.75, length=2.50)

        return self._save()

    def _save(self):
        plt.tight_layout()

        plt.savefig(self.outpath)
        plt.close()

        return self.outpath
