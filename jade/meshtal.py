# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:22:30 2021

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
import re
import pandas as pd

# PATTERNS
PAT_NUM = re.compile(r'(?<=Mesh Tally Number)\s+\d+')  # blank spaces to be elim
PAT_DESC = re.compile(r'(?<=FMESH\s).+')  # get the tally name
PAT_CYLYNDER = re.compile(r'\sR\s+Z\s')  # Start of a cylyndrical tally
PAT_PARTICLE = re.compile(r'(?=<mesh tally).+')

# Meshtal to mctal conversion
# COLUMNS = ['Cells', 'Dir', 'User', 'Segments', 'Multiplier', 'Cosine',
#            'Energy', 'Time', 'Cor C', 'Cor B', 'Cor A', 'Value', 'Error']
CONV = {'Result': 'Value', 'Rel': 'Error', 'R': 'Cor A', 'Z': 'Cor B',
        'Th': 'Cor C'}


class Meshtal:
    def __init__(self, filepath):
        """
        Object representing the meshtal MCNP file.

        Parameters
        ----------
        filepath : path or str
            path to the meshtal MCNP file.

        Returns
        -------
        None.

        """
        self.filepath = filepath  # file path
        self.name = os.path.basename(filepath)  # file name
        self.fmeshes = self._read_file()  # dictionary of the fmeshes

    def extract_1D(self):
        """
        Iterate on the fmeshes and select the one that can be compressed into
        a 1D tally and convert them.

        Returns
        -------
        fmesh1D : dic
            dictionary containing the converted 1D fmeshes

        """
        fmesh1D = {}
        for key, fmesh in self.fmeshes.items():
            flag1D, ax = fmesh.is1D()
            # If the fmesh can compressed to a 1D
            if flag1D:
                # Extract tally data
                _, data = fmesh.convert2tally()
                # keepcols = [ax, fmesh._values_tag, fmesh._error_tag]
                # print(data)
                # data = fmesh.data[keepcols]
                fmesh1D[key] = {'data': data, 'num': key,
                                'desc': fmesh.description}

        self.fmesh1D = fmesh1D

        return fmesh1D

    def _read_file(self):
        """
        read the MCNP meshtal file and populate the Meshtal object.

        Returns
        -------
        fmeshes : TYPE
            DESCRIPTION.

        """
        with open(self.filepath, 'r') as infile:
            # Flags that regulates current operations
            flag_inheader = True
            flag_intally = False
            flag_inmesh = False

            # default values
            particle = None
            description = None

            fmeshes = {}

            for idx, line in enumerate(infile):
                # --- Operations while reading the file header ---
                if flag_inheader:
                    # Things to look for
                    tally_num = PAT_NUM.search(line)

                    # Finding a tally num triggers the exit from header
                    if tally_num is not None:
                        flag_inheader = False
                        flag_intally = True
                        # New Fmesh initialized
                        current_num = tally_num.group().strip()

                # --- Operations while reading the tally header ---
                elif flag_intally:
                    # Things to look for
                    particle_check = PAT_PARTICLE.search(line)
                    description_check = PAT_DESC.search(line)
                    cyl_start = PAT_CYLYNDER.search(line)

                    if description_check is not None:
                        description = description_check.group().strip()
                    if particle_check is not None:
                        particle = particle_check.group().strip()

                    # Finding a cylindrical fmesh start triggers the entering
                    # in the mesh mode
                    if cyl_start is not None:
                        flag_intally = False
                        flag_inmesh = True
                        skiprows = idx  # Memorize where reading should start
                        nrows = 1

                # --- Operations while reading the tally values ---
                elif flag_inmesh:
                    # Just check when the data finishes (blank line)
                    if len(line.strip()) == 0:
                        flag_inheader = True
                        flag_inmesh = False
                        # Blank line, read and adjourn fmesh
                        fmesh_data = pd.read_csv(self.filepath,
                                                 sep=r'\s+',
                                                 skiprows=skiprows,
                                                 nrows=nrows-1)
                        # Generate the FMESH and update the dic
                        fmesh = Fmesh(fmesh_data, current_num, description,
                                      particle)
                        fmeshes[current_num] = fmesh

                        # Reistantiate default values
                        particle = None
                        description = None

                    else:
                        # one more line to read
                        nrows += 1

            # --- At the end of file some more operation may be needed ---
            # If we were still reading tally add it
            if flag_inmesh:
                fmesh_data = pd.read_csv(self.filepath, sep=r'\s+',
                                         skiprows=skiprows,
                                         nrows=nrows)
                # Generate the FMESH and update the dic
                fmesh = Fmesh(fmesh_data, current_num, description, particle)
                fmeshes[current_num] = fmesh

        return fmeshes


class Fmesh:
    def __init__(self, data, tallynum, description, particle):
        """
        Special Fmesh tally object representation

        Parameters
        ----------
        data : pd.DataFrame
            tally result data.
        tallynum : str
            tally MCNP number.
        description : str
            description of the tally.
        particle : str
            tallied particle.

        Returns
        -------
        None.

        """
        self.data = data.dropna(axis=1)
        self.tallynum = tallynum
        self.description = description
        self.particle = particle

        self._values_tag = 'Result'
        self._error_tag = 'Rel'

    def is1D(self):
        """
        This method checks if an fmesh tally can be compressed into 1D
        tally.

        Returns
        -------
        flag_1D : Bool
            If True, the mesh tally has only one true ax.
        ax : str
            name of the true ax. If the fmesh has more than one axis None is
            returned.

        """
        df = self.data.copy()
        axes = []
        for column in df.columns:
            # Iterate on all columns except the results and errors
            if column not in [self._values_tag, self._error_tag]:
                check = set(df[column].values)
                # If the column only has a single costant value it is not a
                # true ax
                if len(check) > 1:
                    axes.append(check)
                    ax = str(column)

        # Check if there was only one ax
        if len(axes) == 1:
            flag_1D = True
        else:
            flag_1D = False
            ax = None

        return flag_1D, ax

    def convert2tally(self):
        """
        Access the fmesh results and get the data columns compatible with the
        mctal classic tallies ones

        Parameters
        ----------

        Returns
        -------
        str
            tally number.
        data : pd.DataFrame
            data with compatible columns name.

        """
        # First of all check if the tally is 1D, in that case reduce the data
        flag1D, ax = self.is1D()

        data = self.data.copy()
        newcols = []
        for column in data.columns:
            if flag1D:
                # Add to the new data only the necessary if is 1D
                if column in [ax, self._values_tag, self._error_tag]:
                    try:
                        newcols.append(CONV[column])
                    except KeyError:
                        print('Key: "'+column+'" is not yet convertible')
                else:
                    # If it not to keep just drop the column
                    del data[column]

            # If it is not a 1D just convert the columns names
            else:
                try:
                    newcols.append(CONV[column])
                except KeyError:
                    print('Key: "'+column+'" is not yet convertible')

        data.columns = newcols

        return self.tallynum, data
