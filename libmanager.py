# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:00:45 2019

@author: Davide Laghi
"""
import xsdirpyne as xs
import pandas as pd


class LibManager:
    """
    This class initialize the Manager that will address all operations were
    libraries changes or comparisons are involved
    """

    def __init__(self, xsdir_file, defaultlib='81c'):
        """
        Use Pyne module to properly parse the xsdir file

        xsdir_file: (raw str) path to the xsdir file
        defaultlib: (str) suffix of the library to use as default
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
        libraries = self.check4zaid('1001')
        libraries.extend(self.check4zaid('1000'))  # photons

        self.libraries = libraries

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
                    translation[idx] = (lib, row['Mean value'],
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
        Given a zaid, its chemical name and isotope number is returned

        zaid: (Zaid) object or str
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

    def select_lib(self):
        """
        Prompt an library input selection with Xsdir availabilty check

        Returns
        -------
        lib : str
            Library to assess.

        """
        while True:
            lib = input(' Select library (e.g. 31c): ')
            if lib in self.libraries:
                break
            else:
                print('''
                  Error:
                  The selected library is not available.
                  ''')
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
