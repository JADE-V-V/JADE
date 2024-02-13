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
from __future__ import annotations

import json
import os
import re
import sys
import logging
import warnings
import numpy as np

import jade.acepyne as ace
import jade.xsdirpyne as xs
import pandas as pd
from jade.xsdirpyne import OpenMCXsdir, SerpentXsdir, Xsdir
from jade.exceptions import fatal_exception

# colors
CRED = "\033[91m"
CEND = "\033[0m"


MSG_DEFLIB = " The Default library {} was used for zaid {}"


class IsotopeDataParser:
    def __init__(self, isotopes_file: os.PathLike) -> None:
        # load the natural abundance file
        abundances = pd.read_csv(isotopes_file, skiprows=2)
        abundances["idx"] = abundances["idx"].astype(str)
        abundances.set_index("idx", inplace=True)
        self.isotopes = abundances

    def get_formulazaid(self, formula):
        match = re.match(r"([a-z]+)([0-9]+)", formula, re.I)
        parts = match.groups()
        E, A = parts[0], int(parts[1])
        newiso = self.isotopes[self.isotopes["E"] == E]
        Z = newiso["Z"].values[0]
        zaid = "{0}{1:0>3}".format(Z, A)
        return zaid


class LibManager:

    # def __init__(self, xsdir_file, defaultlib='81c', activationfile=None,
    #             isotopes_file=None):
    def __init__(
        self,
        lib_df: pd.DataFrame,
        defaultlib: str = None,
        activationfile: os.PathLike = None,
        isotopes_file: os.PathLike = None,
    ) -> None:
        """
        Object dealing with all complex operations that involves nuclear data.

        Parameters
        ----------
        lib_df : pd.DataFrame
            table related to libraries variables.
        defaultlib : str, optional
            lib suffix to be used as default in translation operations.
            If None, it reads from lib_df
        activationfile : str or path, optional
            path to the config file containing the reactions data for
            activation libraries. The default is None.
        isotopes_file : str or path, optional
            path to the isotopes files. If None (default) the file is searched
            in the current directory.

        Attributes
        ----------
        isotope_parser : IsotopeDataParser
            object dealing with the isotopes data.
        isotopes : pd.DataFrame
            contains the isotopes data.
        defaultlib : str
            lib suffix to be used as default in translation operations.
        data : dict[str, dict[str, Union[Xsdir, OpenMCXsdir, SerpentXsdir]]]
            contains the libraries data. first level keys are the codes, second
            level keys are the library suffixes. ultimate value is the xsdir
            object.
        codes : list
            list of codes available.
        libraries : dict[str, list[str]]
            contains the libraries available for each code.
        reactions : dict[str, pd.DataFrame]
            contains the reactions data for the different activation libraries.

        Returns
        -------
        None.

        """
        if isotopes_file is None:
            isotopes_file = os.path.join("resources", "Isotopes.txt")

        self.isotope_parser = IsotopeDataParser(isotopes_file)
        self.isotopes = self.isotope_parser.isotopes

        # Convert all columns to lower case
        new_columns = []
        for column in lib_df:
            new_columns.append(column.lower())
        lib_df.columns = new_columns

        if defaultlib is None:
            self.defaultlib = lib_df[lib_df["default"] == "yes"]["suffix"].values[0]
        else:
            self.defaultlib = defaultlib

        self.data = {}
        self.codes = []
        lib_df.set_index("suffix", inplace=True)
        # Initilize the Xsdir object
        # self.XS = xs.Xsdir(xsdir_file)

        # this block of code needs to check the availability of the libraries.
        # Only libraries specified in the config file are checked, if paths
        # for the libraries are left empty, the library is not not checked and
        # it is not registered as available. If the path is not empty but
        # library is not found, a warning is raised, choice for interrupting the
        # session is left to the user.
        for code in lib_df.columns[2:]:
            code = code.lower()
            self.codes.append(code)
            self.data[code] = {}
            for library, row in lib_df.iterrows():
                path = row[code]
                # if the path is empty just ignore it
                if path is None or path == "":
                    logging.info("No path for %s library", library)
                    continue

                # if the path is not empty, check if the file exists
                # and if it does not, raise a warning since it may not be the
                # intended behaviour by the user
                if not os.path.exists(path):
                    logging.warning(
                        "Library %s for code %s not found at %s", library, code, path
                    )
                    # fatal_exception(path + " does not exist")

                if code == "mcnp":
                    xsdir = Xsdir(path)
                    # verify that the library is actually in the xsdir
                    available_libs = set(np.array(xsdir.tablenames)[:, 1])
                    if library in available_libs:
                        self.data[code][library] = xsdir
                    else:
                        logging.warning(
                            "Library %s not present in XSDIR file: %s", library, path
                        )

                elif code == "openmc":
                    self.data[code][library] = OpenMCXsdir(path, self, library)

                elif code == "serpent":
                    self.data[code][library] = SerpentXsdir(path)

                elif code == "d1s":
                    xsdir = Xsdir(path)
                    # verify that the library is actually in the xsdir
                    available_libs = set(np.array(xsdir.tablenames)[:, 1])
                    if library in available_libs:
                        self.data[code][library] = xsdir
                    else:
                        logging.warning(
                            "Library %s not present in XSDIR file: %s", library, path
                        )

                else:
                    raise ValueError(f"{code} code not implemented")

        # Identify different libraries installed. This is done checking H
        # libraries = self.check4zaid('1001')
        # libraries.extend(self.check4zaid('1000'))  # photons

        # """ Legacy library definition changed """
        # """
        # libraries = []
        # for table in self.XS:
        #     lib = table.name.split('.')[1]
        #     if lib not in libraries:
        #         libraries.append(lib)

        # self.libraries = libraries
        # """

        # libraries have now been checked at the source, they may be different
        # for each code
        libraries = {}
        for key, value in self.data.items():
            libraries[key] = []
            for lib, _ in value.items():
                libraries[key].append(lib)
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

    def check4zaid(self, zaid: str, code: str = "mcnp"):
        # Needs fixing
        """
        Check which libraries are available for the selected zaid and return it

        Parameters
        ----------
        zaid : str
            zaid string (e.g. 1001).
        code: str, optional
            code to be looked up. default is 'mcnp'

        Returns
        -------
        libraries : list
            list of libraries available for the zaid.

        """
        libraries = []
        if code != "openmc":
            for lib in self.libraries[code]:
                xsdir = self.data[code][lib]
                if lib in xsdir.find_table(zaid, mode="default-fast"):
                    libraries.append(lib)
        else:
            raise NotImplementedError("{} not implemented yet".format(code))

        return libraries

    # def check_zaid(self, zaid, lib, code):
    #     XS = self._get_xs(code, lib)
    #     if isinstance(XS, str) or XS is None:
    #         return True
    #     elif len(XS.find_table(zaid, mode='default-fast')) > 0:
    #         return True
    #     else:
    #         return False

    def convertZaid(self, zaid: str, lib: str, code: str = "mcnp"):
        # Needs fixing
        """
        This methods will convert a zaid into the requested library

        modes:
            - 1to1: there is one to one correspondence for the zaid
            - natural: the zaids will be expanded using the natural abundance
            - absent: the zaid is not available in the library, a default one
              will be used or the natural one if available.

        Parameters
        ----------
        zaid : str
            zaid name (ex. 1001).
        lib : str
            library suffix (ex. 21c).
        code : str, optional
            code for which the translation is performed. default is MCNP

        Raises
        ------
        ValueError
            if the library is not available in the xsdir file or if there is
            no valid translation for the zaid.

        Returns
        -------
        translation : dic
            {zaidname:(lib,nat_abundance,Atomic mass)}.

        """
        # Check if library is available in Xsdir
        if lib not in self.libraries[code]:
            raise ValueError("Library " + lib + " is not available in xsdir file")

        zaidlibs = self.check4zaid(zaid, code)

        if code in ["mcnp", "d1s", "serpent"]:
            XS = self.data[code][lib]
            # Natural zaid
            if zaid[-3:] == "000":
                # Check if zaid has natural info
                if XS.find_table(zaid + "." + lib, mode="exact"):
                    translation = {zaid: (lib, 1, 1)}  # mass not important

                else:  # Has to be expanded
                    translation = {}
                    reduced = self.isotopes[self.isotopes["Z"] == int(zaid[:-3])]
                    for idx, row in reduced.iterrows():
                        # zaid availability must be checked
                        if XS.find_table(idx + "." + lib, mode="exact"):
                            newlib = lib
                        elif self.data[code][self.defaultlib].find_table(
                            idx + "." + self.defaultlib, mode="exact"
                        ):
                            warnings.warn(MSG_DEFLIB.format(self.defaultlib, zaid))
                            newlib = self.defaultlib
                        else:
                            raise ValueError(
                                "No available translation for zaid :"
                                + zaid
                                + "It is needed for natural zaid expansion."
                            )

                        translation[idx] = (
                            newlib,
                            row["Mean value"],
                            row["Atomic Mass"],
                        )
            # 1to1
            elif lib in zaidlibs:
                translation = {zaid: (lib, 1, 1)}  # mass not important

            # No possible correspondence, natural or default lib has to be used
            else:
                # Check if the natural zaid is available
                natzaid = zaid[:-3] + "000"
                if XS.find_table(natzaid + "." + lib, mode="exact"):
                    translation = {natzaid: (lib, 1, 1)}  # mass not important
                # Check if default lib is available
                elif self.data[code][self.defaultlib].find_table(
                    zaid + "." + self.defaultlib, mode="exact"
                ):
                    warnings.warn(MSG_DEFLIB.format(self.defaultlib, zaid))
                    translation = {zaid: (self.defaultlib, 1, 1)}  # mass not imp
                else:
                    raise ValueError("No available translation for zaid :" + zaid)
        else:
            raise ValueError("Translation not required for code " + code)

        return translation

    def get_libzaids(self, lib: str, code: str = "mcnp"):
        # Needs fixing
        """
        Given a library, returns all zaids available

        Parameters
        ----------
        lib : str
            suffix of the library.
        code : str, optional
            code for which the zaids are recovered. default is MCNP

        Returns
        -------
        zaids : list
            list of zaid names available in the library.

        """
        XS = self.data[code][lib]

        zaids = []

        if isinstance(XS, xs.Xsdir):
            for table in XS.find_zaids(lib):
                zaid = table.name.split(".")[0]
                if zaid not in zaids:
                    zaids.append(zaid)
        else:
            raise NotImplementedError("{} code is not yet implemented".format(code))

        return zaids

    def get_formulazaid(self, formula):
        return self.isotope_parser.get_formulazaid(formula)

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
            splitted = zaid.split(".")
            elem = splitted[0][:-3]
            i = int(elem)
            isotope = splitted[0][-3:]

        else:
            i = int(zaid.element)
            isotope = zaid.isotope

        newiso = self.isotopes.set_index("Z")
        newiso = newiso.loc[~newiso.index.duplicated(keep="first")]

        name = newiso["Element"].loc[i]
        formula = newiso["E"].loc[i] + "-" + str(int(isotope))

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
        newiso = self.isotopes.set_index(["E"])
        newiso = newiso.loc[~newiso.index.duplicated(keep="first")]
        # split the name
        patnum = re.compile(r"\d+")
        patname = re.compile(r"[a-zA-Z]+")
        try:
            num = patnum.search(zaidformula).group()
            name = patname.search(zaidformula).group()
        except AttributeError:
            raise ValueError("No correspondent zaid found for " + zaidformula)

        atomnumber = newiso.loc[name, "Z"]

        zaidnum = "{}{:03d}".format(atomnumber, int(num))

        return zaidnum

    def select_lib(self, code: str = "mcnp") -> str:
        """
        Prompt an library input selection with Xsdir availabilty check

        Returns
        -------
        lib : str
            Library to assess.
        code: str, optional
            code for which the library is selected. default is MCNP

        """
        error = (
            CRED
            + """
 Error: {}
 The selected library is not available.
 """
            + CEND
        )
        # Add a counter to avoid falling in an endless loop
        i = 0
        while True:
            i += 1
            lib = input(" Select library (e.g. 31c or 99c-31c): ")
            if lib in self.libraries[code]:
                break

            elif lib[0] == "{":
                libs = json.loads(lib)
                # all libraries should be available
                tocheck = list(libs.values())
                tocheck.extend(list(libs.keys()))
                flag = True
                for val in tocheck:
                    if val not in self.libraries[code]:
                        print(error.format(val))
                        flag = False
                if flag:
                    break

            elif "-" in lib:
                libs = lib.split("-")
                flag = True
                for val in libs:
                    if val not in self.libraries[code]:
                        print(error.format(val))
                        flag = False
                if flag:
                    break

            elif lib == "back":
                break

            elif lib == "exit":
                break

            else:
                print(error.format(lib))

            if i > 10:
                raise ValueError("Too many wrong inputs")
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
            m = self.isotopes["Atomic Mass"].loc[zaid.element + zaid.isotope]
        except KeyError:  # It means that it is a natural zaid
            # For a natural zaid the natural abundance mass is used
            df = self.isotopes.reset_index()
            df["Partial mass"] = df["Atomic Mass"] * df["Mean value"]
            masked = df.set_index("Z").loc[int(zaid.element)]
            m = masked["Partial mass"].sum()

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
            df = self.reactions[lib].set_index("Parent")
            isotopename, formula = self.get_zaidname(parent)
            formulazaid = formula.replace("-", "")  # eliminate the '-'
            # collect and provide as tuples
            subset = df.loc[formulazaid]
            try:
                for _, row in subset.iterrows():
                    MT = str(int(row["MT"]))
                    daughter = row["Daughter"]
                    daughter = self.get_zaidnum(daughter)
                    reactions.append((MT, daughter))

            except AttributeError:
                # then is not a DF but a Series
                MT = str(int(subset["MT"]))
                daughter = subset["Daughter"]
                daughter = self.get_zaidnum(daughter)
                reactions.append((MT, daughter))

        except KeyError:
            # library is not available or parent is not available
            pass

        return reactions
