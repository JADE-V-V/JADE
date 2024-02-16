# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:21:15 2019

@author: Pyne https://github.com/pyne/pyne

Copyright 2011-2020, the PyNE Development Team. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE PYNE DEVELOPMENT TEAM ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of the stakeholders of the PyNE project or the employers of PyNE developers.
"""
import os
import math
from typing import List, Tuple
import sys


class Xsdir(object):
    """This class stores the information contained in a single MCNP xsdir file.

    Attributes
    ----------
    f : file handle
        The xsdir file.
    filename : str
        Path to the xsdir file.
    directory : str
        Path to the directory containing the xsdir file.
    datapath : str
        The data path specified in the first line of the xsdir file, if it
        exists.
    awr : dict
        Maps material ids to their atomic weight ratios.
    tables : list
        Entries are XsdirTable objects, that appear in the same order as the
        xsdir table lines.

    Notes
    -----
    See MCNP5 User's Guide Volume 3 Appendix K for more information.
    """

    def __init__(self, filename):
        """Parameters
        ----------
        filename : str
            Path to xsdir file.
        """
        self.f = open(filename, 'r')
        self.filename = os.path.abspath(filename)
        self.directory = os.path.dirname(filename)
        self.awr = {}
        self.tables = []
        self.read()

        # It is useful to have a list of the available tables names to be
        # computed only once at initializations
        tablenames = []
        for table in self:
            name = table.name
            zaidname = name[:-4]
            libname = name[-3:]
            tablenames.append((zaidname, libname))
        self.tablenames = tablenames

    def read(self):
        """Populate the Xsdir object by reading the file.
        """
        # Go to beginning of file
        self.f.seek(0)

        # Read first section (DATAPATH)
        line = self.f.readline()
        words = line.split()
        if words:
            if words[0].lower().startswith('datapath'):
                index = line.index('=')
                self.datapath = line[index+1:].strip()
                self.f.readline()


        # Read second section
        line = self.f.readline()
        words = line.split()
        assert len(words) == 3
        assert words[0].lower() == 'atomic'
        assert words[1].lower() == 'weight'
        assert words[2].lower() == 'ratios'

        while True:
            line = self.f.readline()
            words = line.split()

            # Check for end of second section
            if len(words) % 2 != 0 or words[0] == 'directory':
                break

            for zaid, awr in zip(words[::2], words[1::2]):
                self.awr[zaid] = awr

        # Read third section
        while words[0] != 'directory':
            words = self.f.readline().split()

        while True:
            words = self.f.readline().split()
            if not words:
                break

            # Handle continuation lines
            while words[-1] == '+':
                extraWords = self.f.readline().split()
                words = words[:-1] + extraWords  # Correction
            assert len(words) >= 7

            # Create XsdirTable object and add to line
            table = XsdirTable()
            self.tables.append(table)

            # All tables have at least 7 attributes
            try:
                table.name = words[0]
                table.awr = float(words[1])
                table.filename = words[2]
                table.access = words[3]
                table.filetype = int(words[4])
                table.address = int(words[5])
                table.tablelength = int(words[6])

                if len(words) > 7:
                    table.recordlength = int(words[7])
                if len(words) > 8:
                    table.entries = int(words[8])
                if len(words) > 9:
                    table.temperature = float(words[9])
                if len(words) > 10:
                    table.ptable = (words[10] == 'ptable')
            except ValueError:
                problem_line = words[0]
                print("Error reading line corresponding to {}, passing for now, please adjust XSDIR file".format(problem_line))
                pass

    def find_table(self, name, mode='default'):
        """Find all tables for a given ZIAD.
        *Modified for JADE, a bug was corrected since table.name do not
        find natural zaids.

        mode: 'default' default behaviour
              'exact' check also the library
              'default-fast' accelerated loop giving only the lib names

        Parameters
        ----------
        name : str
            The ZIAD name.

        Returns
        -------
        tables : list
            All XsdirTable objects for a given ZIAD.
        """
        if mode == 'exact':
            # Faster, checks for the exact name
            ans = self._exact_loop(name, self.tablenames)

        elif mode == 'default':
            # Checks all available libraries for the zaid
            tables = []
            for table in self:
                # tablename = table.name.split('.')[0]
                if name == table.name[:-4]:
                    tables.append(table)

            ans = tables

        elif mode == 'default-fast':
            ans = self._all_fast_loop(name, self.tablenames)

        return ans

    @staticmethod
    def _exact_loop(name: str, tablenames: List[Tuple[str, str]]) -> bool:
        for zaidname, libname in tablenames:
            if name == zaidname+'.'+libname:
                return True

        return False

    @staticmethod
    def _all_fast_loop(name: str, tablenames: List[Tuple[str, str]]) -> List[str]:
        libs = []
        for zaidname, libname in tablenames:
            if name == zaidname:
                libs.append(libname)

        return libs

#################  Added by Davide Laghi ###############################  
    def find_zaids(self, lib):
        """Find all zaids for a given library.

        Parameters
        ----------
        lib : str
            The library suffix.

        Returns
        -------
        tables : list
            All XsdirTable objects for a given library.
        """

        tables = []

        for table in self:
            tablelib = table.name.split('.')[-1]
            if lib == tablelib:
                tables.append(table)

        return tables
############################################################################

    def to_xsdata(self, filename):
        """Writes a Serpent xsdata file for all continuous energy xs tables.

        Parameters
        ----------
        filename : str
            The output filename.

        """
        xsdata = open(filename, 'w')
        for table in self.tables:
            if table.serpent_type == 1:
                xsdata.write(table.to_serpent() + '\n')
        xsdata.close()

    def __iter__(self):
        for table in self.tables:
            yield table

    def nucs(self):
        """Provides a set of the valid nuclide ids for nuclides contained
        in the xsdir.

        Returns
        -------
        valid_nucs : set
            The valid nuclide ids.
        """
        valid_nucs = set(nucname.id(table.name.split('.')[0])
                         for table in self.tables if
                         nucname.isnuclide(table.name.split('.')[0]))
        return valid_nucs


class SerpentXsdir(Xsdir):
    """
    Serpent Xsdir class
    """
    def read(self):
        for i, line in enumerate(self.f):
            if i % 2 == 0:
                # Create XsdirTable object and add to line
                table = XsdirTable()
                self.tables.append(table)
                words = line.split()
                if len(words) > 0:
                    table.name = words[0]
                    table.awr = float(words[5])/1.0086649670000
                    table.filename = words[8]
                    table.temperature = float(words[6])/1.1604518025685E+10


class OpenMCXsdir(Xsdir):
    """
    OpenMC Xsdir class
    """
    def __init__(self, filename, libmanager, library):
        """Parameters
        ----------
        filename : str
            Path to xsdir file.
        """
        self.f = open(filename, 'r')
        self.filename = os.path.abspath(filename)
        self.directory = os.path.dirname(filename)
        self.tables = []

        self.read(libmanager, library)

        # It is useful to have a list of the available tables names to be
        # computed only once at initializations
        tablenames = []
        for table in self:
            name = table.name
            zaidname = name[:-4]
            libname = name[-3:]
            tablenames.append((zaidname, libname))
        self.tablenames = tablenames

    def read(self, libmanager, library):
        for i, line in enumerate(self.f):
            if '<library' in line:
                line = line.replace('"', '')
                parts = line.split()
                data = {}
                for part in parts:
                    if '=' in part:
                        values = part.split('=')
                        data[values[0]] = values[1]
                if data['type'] == 'neutron':
                    table = XsdirTable()
                    table.name = libmanager.get_formulazaid(data['materials']) + '.' + library
                    table.filename = data['path']


class XsdirTable(object):
    """Stores all information that describes a xsdir table entry, which appears
    as a single line in xsdir file. Attribute names are based off of those
    found in the MCNP5 User's Guide Volume 3, appendix K.

    Attributes
    ----------
    name : str
        The ZAID and library identifier, delimited by a '.'.
    awr : float
        The atomic mass ratio of the nuclide.
    filename : str
        The relative path of the file containing the xs table.
    access : str
       Additional string to specify an access route, such as UNIX directory.
       This entry is typically 0.
    filetype : int
        Describes whether the file contains formated (1) or unformated (2)
        file.
    address : int
        If filetype is 1, address is the line number of the xsdir table. If
        filetype is 2, address is the record number.
    tablelength : int
        Length of the second block of a data table.
    recordlength : int
        Unused for filetype = 1. For filetype = 2, recordlength is the number
        of entires per record times the size (in bytes) of each entry.
    entries : int
        Unused for filetype = 1. For filetype = 2, it is the number of entries
        per record
    temperature : float
        Temperature in MeV for neutron data only.
    ptable : bool
        True if xs table describes continuous energy neutron data with
        unresolved resonance range probability tables.
    """

    def __init__(self):
        self.name = None
        self.awr = None
        self.filename = None
        self.access = None
        self.filetype = None
        self.address = None
        self.tablelength = None
        self.recordlength = None
        self.entries = None
        self.temperature = None
        self.ptable = False

    @property
    def alias(self):
        """Returns the name of the table entry <ZIAD>.<library id>.
        """
        return self.name

    @property
    def serpent_type(self):
        """Converts cross section table type to Serpent format:
            :1: continuous energy (c).
            :2: dosimetry table (y).
            :3: termal (t).
        """
        if self.name.endswith('c'):
            return 1
        elif self.name.endswith('y'):
            return 2
        elif self.name.endswith('t'):
            return 3
        else:
            return None

    @property
    def metastable(self):
        """Returns 1 is xsdir table nuclide is metastable. Returns zero
        otherwise.
        """
        # Only valid for neutron cross-sections
        if not self.name.endswith('c'):
            return

        # Handle special case of Am-242 and Am-242m
        if self.zaid == '95242':
            return 1
        elif self.zaid == '95642':
            return 0

        # All other cases
        A = int(self.name.split('.')[0]) % 1000
        if A > 600:
            return 1
        else:
            return 0

    @property
    def zaid(self):
        """Returns the ZIAD of the nuclide.
        """
        return self.name[:self.name.find('.')]

    def to_serpent(self, directory=''):
        """Converts table to serpent format.

        Parameters
        ----------
        directory : str
            The directory where Serpent data is to be stored.
        """
        # Adjust directory
        if directory:
            if not directory.endswith('/'):
                directory = directory.strip() + '/'

        return "{0} {0} {1} {2} {3} {4} {5:.11e} {6} {7}".format(
            self.name,
            self.serpent_type, self.zaid, 1 if self.metastable else 0,
            self.awr, self.temperature/8.6173423e-11, self.filetype - 1,
            directory + self.filename)

    def __repr__(self):
        return "<XsDirTable: {0}>".format(self.name)


# """ General XSData object added by S. Bradnam """
# class XSData(object):
#     def __init__(self, libmanager, lib):
#         self.read(libmanager, lib)
#         self.data = None

#     def read(self, libmanager, lib):
#         self.libraries = lib['Suffix'].tolist()
#         # self.mcnp_data = {}
#         # self.serpent_data = {}
#         # self.openmc_data = {}
#         # self.d1s_data = {}

#         for i, library in enumerate(self.libraries):
#             mcnp_value = lib.at[i, "MCNP"]
#             if mcnp_value == '':
#                 self.mcnp_data[library] = None
#             else:
#                 self.mcnp_data[library] = Xsdir(mcnp_value)
#             serpent_value = lib.at[i, "Serpent"]
#             if serpent_value == '':
#                 self.serpent_data[library] = None
#             else:
#                 self.serpent_data[library] = SerpentXsdir(serpent_value)           
#             openmc_value = lib.at[i, "OpenMC"]
#             if openmc_value == '':
#                 self.openmc_data[library] = None
#             else:
#                 self.openmc_data[library] = OpenMCXsdir(openmc_value,
#                                                         libmanager, library) 
#             d1s_value = lib.at[i, "d1S"]
#             if d1s_value == '':
#                 self.d1s_data[library] = None
#             else:
#                 self.d1s_data[library] = Xsdir(d1s_value)
