# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:00:45 2019

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
import xsdirpyne as xs
import pandas as pd
import json
import re
import warnings
from main import (CRED, CEND)


MSG_DEFLIB = ' The Deafult library {} was used for zaid {}'


class LibManager:
    """
    This class initialize the Manager that will address all operations were
    libraries changes or comparisons are involved
    """

    def __init__(self, xsdir_file, defaultlib='81c', activationfile=None):
        """
        Object dealing with all complex operations that involves nuclear data

        Parameters
        ----------
        xsdir_file : str or path
            path to the MCNP xsdir reference file.
        defaultlib : str, optional
            lib suffix to be used as default in translation operations.
            The default is '81c'.
        activationfile : str or path, optional
            path to the ocnfig file containing the reactions data for
            activation libraries. The default is None.

        Returns
        -------
        None.

        """
        # load the natural abundance file
        abundances = pd.read_csv('Isotopes.txt', skiprows=2)
        abundances['idx'] = abundances['idx'].astype(str)
        abundances.set_index('idx', inplace=True)
        self.isotopes = abundances

        self.defaultlib = defaultlib

        # Initilize the Xsdir object
        self.XS = xs.Xsdir(xsdir_file)

        # Identify different libraries installed. This is done checking H
        # libraries = self.check4zaid('1001')
        # libraries.extend(self.check4zaid('1000'))  # photons
        libraries = []
        for table in self.XS:
            lib = table.name.split('.')[1]
            if lib not in libraries:
                libraries.append(lib)

        self.libraries = libraries

        # Load the activation reaction data if available
        if activationfile is not None:
            reactions = {}
            file = pd.ExcelFile(activationfile)
            for sheet in file.sheet_names:
                # Load the df that also needs to be filled
                reactions[sheet] = file.parse(sheet).ffill()
                # translate the formula name to zaid
        else:
            reactions = None

        self.reactions = reactions

    def check4zaid(self, zaid):
        """
        Check which libraries are available for the selected zaid and return it
        """
        libraries = []
        for table in self.XS.find_table(zaid):
            libraries.append(table.name.split('.')[-1])

        return libraries

    def convertZaid(self, zaid, lib):
        """
        This methods will convert a zaid into the requested library

        modes:
            - 1to1: there is one to one correspondence for the zaid
            - natural: the zaids will be expanded using the natural abundance
            - absent: the zaid is not available in the library, a default one
            will be used

        zaid: (str) zaid name (ex. 1001)
        lib: (str) library suffix (ex. 21c)
        defaultlib: (str) library suffix (ex. 21c)

        returns translation: (dic) {zaidname:(lib,nat_abundance,Atomic mass)}
        """
        # Check if library is available in Xsdir
        if lib not in self.libraries:
            raise ValueError('Library '+lib+' is not available in xsdir file')

        zaidlibs = self.check4zaid(zaid)
        # Natural zaid
        if zaid[-3:] == '000':
            # Check if zaid has natural info
            if self.XS.find_table(zaid+'.'+lib, mode='exact'):
                translation = {zaid: (lib, 1, 1)}  # mass not important

            else:  # Has to be expanded
                translation = {}
                reduced = self.isotopes[self.isotopes['Z'] == int(zaid[:-3])]
                for idx, row in reduced.iterrows():
                    # zaid availability must be checked
                    if self.XS.find_table(idx+'.'+lib, mode='exact'):
                        newlib = lib
                    elif self.XS.find_table(idx+'.'+self.defaultlib,
                                            mode='exact'):
                        warnings.warn(MSG_DEFLIB.format(self.defaultlib, zaid))
                        newlib = self.defaultlib
                    else:
                        raise ValueError('No available translation for zaid :' +
                                         zaid+'It is needed for natural zaid expansion.')

                    translation[idx] = (newlib, row['Mean value'],
                                        row['Atomic Mass'])
        # 1to1
        elif lib in zaidlibs:
            translation = {zaid: (lib, 1, 1)}  # mass not important

        # No possible correspondence, natural or default lib has to be used
        else:
            # Check if the natural zaid is available
            natzaid = zaid[:-3]+'000'
            if self.XS.find_table(natzaid+'.'+lib, mode='exact'):
                translation = {natzaid: (lib, 1, 1)}  # mass not important
            # Check if default lib is available
            elif self.XS.find_table(zaid+'.'+self.defaultlib, mode='exact'):
                warnings.warn(MSG_DEFLIB.format(self.defaultlib, zaid))
                translation = {zaid: (self.defaultlib, 1, 1)}  # mass not imp
            else:
                # Check if any zaid cross section is available
                libraries = self.check4zaid(zaid)
                # It has to be for the same type of particles
                found = False
                for library in libraries:
                    if library[-1] == lib[-1]:
                        found = True
                # If found no lib is assigned
                if found:
                    translation = {zaid: (None, 1, 1)}  # no masses
                # If no possible translation is found raise error
                else:
                    raise ValueError('No available translation for zaid :' +
                                     zaid)

        return translation

    def get_libzaids(self, lib):
        """
        Given a library, returns all zaids available

        lib: (str) suffix of the library

        returns zaids: (list) of zaid names
        """
        zaids = []

        for table in self.XS.find_zaids(lib):
            zaid = table.name.split('.')[0]
            if zaid not in zaids:
                zaids.append(zaid)

        return zaids

    def get_zaidname(self, zaid):
        """
        Given a zaid, its element name and formula are returned. E.g.,
        hydrogen, H1

        Parameters
        ----------
        zaid : str
            zaid number (e.g. 1001 for H1).

        Returns
        -------
        name : str
            element name (e.g. hydrogen).
        formula : str
            isotope name (e.g. H1).

        """
        if type(zaid) == str:
            splitted = zaid.split('.')
            elem = splitted[0][:-3]
            i = int(elem)
            isotope = splitted[0][-3:]

        else:
            i = int(zaid.element)
            isotope = zaid.isotope

        newiso = self.isotopes.set_index('Z')
        newiso = newiso.loc[~newiso.index.duplicated(keep='first')]

        name = newiso['Element'].loc[i]
        formula = newiso['E'].loc[i]+'-'+str(int(isotope))

        return name, formula

    def get_zaidnum(self, zaidformula):
        """
        Given a zaid formula return the correct number

        Parameters
        ----------
        zaidformula : str
            name of the zaid, e.g., H1.

        Returns
        -------
        zaidnum : str
            number of the zaid ZZZAA

        """
        # get the table and drop the duplicates
        newiso = self.isotopes.set_index(['E'])
        newiso = newiso.loc[~newiso.index.duplicated(keep='first')]
        # split the name
        patnum = re.compile(r'\d+')
        patname = re.compile(r'[a-zA-Z]+')
        num = patnum.search(zaidformula).group()
        name = patname.search(zaidformula).group()

        atomnumber = newiso.loc[name, 'Z']

        zaidnum = "{}{:03d}".format(atomnumber, int(num))

        return zaidnum

    def select_lib(self):
        """
        Prompt an library input selection with Xsdir availabilty check

        Returns
        -------
        lib : str
            Library to assess.

        """
        error = CRED+'''
 Error: {}
 The selected library is not available.
 '''+CEND
        while True:
            lib = input(' Select library (e.g. 31c or {"99c":"98c", "21c":"31c"}): ')
            if lib in self.libraries:
                break

            elif lib[0] == '{':
                libs = json.loads(lib)
                # all libraries should be available
                for val in libs.values():
                    if val not in self.libraries:
                        print(error.format(val))
                        continue
                # If this point is reached, all libs are available
                break

            elif '-' in lib:
                libs = lib.split('-')
                for val in libs:
                    if val not in self.libraries:
                        print(error.format(val))
                        continue
                # If this point is reached, all libs are available
                break

            else:
                print(error.format(lib))
        return lib

    def get_zaid_mass(self, zaid):
        """
        Get the atomic mass of one zaid

        Parameters
        ----------
        zaid : matreader.Zaid
            Zaid to examinate.

        Returns
        -------
        m: float
            atomic mass.

        """
        try:
            m = self.isotopes['Atomic Mass'].loc[zaid.element+zaid.isotope]
        except KeyError:  # It means that it is a natural zaid
            # For a natural zaid the natural abundance mass is used
            df = self.isotopes.reset_index()
            df['Partial mass'] = df['Atomic Mass']*df['Mean value']
            masked = df.set_index('Z').loc[int(zaid.element)]
            m = masked['Partial mass'].sum()

        return float(m)

    def get_reactions(self, lib, parent):
        """
        get the reactions available for a specific zaid and parent nuclide

        Parameters
        ----------
        lib : str
            library suffix as in sheet name of the activation file.
        parent : str
            zaid number of the parent (e.g. 1001).

        Returns
        -------
        reactions : list
            contains tuple of (MT, daughter).

        """
        reactions = []
        try:
            df = self.reactions[lib].set_index('Parent')
            isotopename, formula = self.get_zaidname(parent)
            formulazaid = formula.replace('-', '')  # eliminate the '-'
            # collect and provide as tuples
            subset = df.loc[formulazaid]
            try:
                for _, row in subset.iterrows():
                    MT = str(int(row['MT']))
                    daughter = row['Daughter']
                    daughter = self.get_zaidnum(daughter)
                    reactions.append((MT, daughter))

            except AttributeError:
                # then is not a DF but a Series
                MT = str(int(subset['MT']))
                daughter = subset['Daughter']
                daughter = self.get_zaidnum(daughter)
                reactions.append((MT, daughter))

        except KeyError:
            # library is not available or parent is not available
            pass

        return reactions
