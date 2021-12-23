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
import shutil
import pytest
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from atlas import Atlas

TEMPLATE_PATH = os.path.join(cp, 'TestFiles', 'atlas', 'template.docx')
KEYARGS_DF = [{'caption': 'yo', 'highlight': True},
              {}]


class TestAtlas:

    atlas = Atlas(TEMPLATE_PATH, 'dummyname')
    df = pd.DataFrame(np.zeros((3, 3)))
    df.columns = ['dummy1', 'dummy2', 'dummy3']
    df['highlight'] = ['OK', 'NOK', 'OK']

    def test_insert_img(self):
        # dummy plot
        plt.plot([1, 2], [1, 2])
        try:
            os.mkdir('tmp')
        except FileExistsError:
            pass
        pathfig = os.path.join('tmp', 'dummyfig.png')
        plt.savefig(pathfig)
        try:
            self.atlas.insert_img(pathfig)
            assert True
        finally:
            shutil.rmtree('tmp')

    @pytest.mark.parametrize("keyargs", KEYARGS_DF)
    def test_insert_df(self, keyargs):
        self.atlas.insert_df(self.df, **keyargs)
        assert True

    def test_save(self):
        try:
            os.mkdir('tmp')
        except FileExistsError:
            pass
        # Unfortunately the pdf creation cannot be tested since it requires
        # Office
        try:
            self.atlas.save('tmp', pdfprint=False)
            assert True
        finally:
            shutil.rmtree('tmp')
