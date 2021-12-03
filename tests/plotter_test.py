# -*- coding: utf-8 -*-
"""

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
import sys
import os
import numpy as np
import shutil
import pytest

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from plotter import Plotter
import plotter

OUTPATH = os.path.join(cp, 'tmp')
outname = 'dummy'
quantity = 'Flux'
unit = '#/cc'
xlabel = 'xlabel'
title = 'plot title'
x = np.random.rand(50)
data1 = {'x': x, 'y': np.random.rand(50)*100,
         'err': np.random.rand(50), 'ylabel': 'data1'}
data2 = {'x': x, 'y': np.random.rand(50)*100,
         'err': np.random.rand(50), 'ylabel': 'data2'}
data = [data1, data2]
default_testname = 'dummy'

KEYARGS = {'data': data, 'title': title, 'outpath': OUTPATH,
           'outname': outname, 'quantity': quantity, 'unit': unit,
           'xlabel': xlabel, 'testname': default_testname}

AVAILABLE_PLOTS = ['Binned graph', 'Ratio graph', 'Experimental points',
                   'Discreet Experimental points', 'Grouped bars']


class TestPlotter:
    """This will merely checks that the plots can be generated without having
    unexpected error. It does not guarantee that the code works as intended.
    """

    def test_get_limits(self):
        lowerlimits = np.random.rand(10)
        upperlimits = lowerlimits*3
        print(upperlimits)
        xdata = x
        ydata = data1['y']/data2['y']
        for lowerlimit, upperlimit in zip(lowerlimits, upperlimits):
            limits = plotter._get_limits(lowerlimit, upperlimit, ydata, xdata)
            assert len(limits) == 3
            totlen = len(limits[0][0])+len(limits[1][0])+len(limits[2][0])
            assert totlen == len(xdata)
            for limit in limits:
                assert len(limit[0]) == len(limit[1])
                assert limit[0].size == limit[1].size

    @pytest.mark.parametrize("plot_type", AVAILABLE_PLOTS)
    def test_plot(self, plot_type):
        plotterob = Plotter(**KEYARGS)
        # In this first one check also the error
        try:
            plotterob.plot('wrongone')
            assert False
        except ValueError:
            assert True

        # Create the tmp directory
        if not os.path.exists(OUTPATH):
            os.mkdir(OUTPATH)

        try:
            plotterob.plot(plot_type)
            assert True
        finally:
            # remove the temporary directory
            shutil.rmtree(OUTPATH)

    def test_waves(self):
        data1 = {'x': x, 'y': [np.random.rand(50)*100, np.random.rand(50)*100],
                 'err': np.random.rand(50), 'ylabel': 'data1'}
        data2 = {'x': x, 'y': [np.random.rand(50)*100, np.random.rand(50)*100],
                 'err': np.random.rand(50), 'ylabel': 'data2'}
        data = [data1, data2]
        keyargs = KEYARGS.copy()
        keyargs['data'] = data
        keyargs['quantity'] = ['ax a', 'ax b']

        plotterob = Plotter(**keyargs)

        # Create the tmp directory
        if not os.path.exists(OUTPATH):
            os.mkdir(OUTPATH)

        try:
            plotterob.plot('Waves')
            assert True
        finally:
            # remove the temporary directory
            shutil.rmtree(OUTPATH)

