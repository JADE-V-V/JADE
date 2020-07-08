# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:44:45 2020

@author: Davide Laghi
"""
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, AutoMinorLocator, MultipleLocator
from matplotlib.markers import CARETUPBASE
from matplotlib.markers import CARETDOWNBASE
from matplotlib.lines import Line2D


class Plotter():
    def __init__(self, data, title, outpath, outname, ext='.jpg'):
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

        ext : str
            extension of image

        Returns
        -------
        None.

        """
        self.data = data
        self.title = title
        self.outpath = os.path.join(outpath, outname+ext)

    def binned_plot(self, mainYlabel, xlabel='Energy [MeV]',
                    normalize=False):
        """
        PLot composed by three subplots.
        Main plot -> binned values (e.g. a flux in energies)
        Error plot -> statistical error
        Ratio plot (Optional) -> ratio among reference and target values

        Parameters
        ----------
        mainYlabel : str
            Y label for the main plot
        xlabel : str, optional
            X label for the entire plot. The default is 'Energy [MeV]'.
        normalize: bool
            If True the plot is normalized. (Default is False)

        Returns
        -------
        None.

        """

        # General parameters
        data = self.data
        title = self.title
        colors = ['blue', 'orange', 'green', 'purple', 'cyan', 'olive']
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
        ax1.set_ylabel(mainYlabel).set_fontsize(fontsize)  # Y axis label

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
        axes[-1].set_xlabel(xlabel).set_fontsize(fontsize)

        # --- Common Features ---
        for ax in axes:
            # Grid control
            ax.grid()
            ax.grid('True', which='minor', linewidth=0.25)
            # Ticks
            ax.tick_params(which='major', width=1.00, length=5,
                           labelsize=fontsize-2)
            ax.tick_params(which='minor', width=0.75, length=2.50)

        plt.tight_layout()

        plt.savefig(self.outpath)
        plt.close()
