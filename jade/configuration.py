# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:52:32 2019

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
import datetime
import os
import sys

import pandas as pd
import logging

from jade.exceptions import fatal_exception


class Configuration:
    def __init__(self, conf_file):
        """
        Parser of the main configuration file

        Parameters
        ----------
        conf_file : path like object
            path to configuration file.

        Returns
        -------
        None.

        """
        # ############ load conf file sheets ############
        self.conf_file = conf_file
        self.read_settings()

    def _process_path(self, file_path: str) -> str:
        """Process a file path to make sure that its absolute

        Parameters
        ----------
        file_path : str
            Absolute or None.

        Returns
        -------
        str
            An absolute file path.
        """
        if pd.isnull(file_path) is not True:
            if os.path.isabs(file_path) is not True:
                file_path = os.path.join(os.path.dirname(self.conf_file), file_path)
            if not os.path.exists(file_path):
                # If to terminate or not the session is lef to the user
                # other codes path may be present but not used
                logging.warning("Path {file_path} do not exist")
                # fatal_exception(file_path + ' does not exist')

        return file_path

    def read_settings(self) -> None:
        """
        Parse the configuration file

        Returns
        -------
        None.

        """

        conf_file = self.conf_file
        # Main
        main = pd.read_excel(
            conf_file, sheet_name="MAIN Config.", skiprows=1, header=None
        )
        main.columns = ["Variable", "Value"]
        main.set_index("Variable", inplace=True)
        self.mcnp_exec = self._process_path(main["Value"].loc["MCNP executable"])
        self.mcnp_config = self._process_path(main["Value"].loc["MCNP config"])
        self.serpent_exec = self._process_path(main["Value"].loc["Serpent executable"])
        self.serpent_config = self._process_path(main["Value"].loc["Serpent config"])
        self.openmc_exec = self._process_path(main["Value"].loc["OpenMC executable"])
        self.openmc_config = self._process_path(main["Value"].loc["OpenMC config"])
        self.d1s_exec = self._process_path(main["Value"].loc["d1S executable"])
        self.d1s_config = self._process_path(main["Value"].loc["d1S config"])
        self.openmp_threads = main["Value"].loc["OpenMP threads"]
        self.mpi_tasks = main["Value"].loc["MPI tasks"]
        self.batch_system = main["Value"].loc["Batch system"]
        self.batch_file = self._process_path(main["Value"].loc["Batch file"])

        """ Legacy config variables """
        # self.xsdir_path = main['Value'].loc['xsdir Path']
        # self.suppressW = main['Value'].loc['Suppress warnings']
        # self.multi_threads = main['Value'].loc['multithread']
        # self.cpu = main['Value'].loc['CPU']

        # Computational
        comp_default = pd.read_excel(
            conf_file, sheet_name="Computational benchmarks", skiprows=2
        )
        self.comp_default = comp_default.dropna(subset=["Folder Name"])

        # Experimental
        comp_default = pd.read_excel(
            conf_file, sheet_name="Experimental benchmarks", skiprows=2
        )
        self.exp_default = comp_default.dropna(subset=["Folder Name"])

        # Libraries
        lib = pd.read_excel(conf_file, sheet_name="Libraries", keep_default_na=False)
        self.lib = lib

        # self.default_lib = lib[lib['Default'] == 'yes']['Suffix'].values[0]

    def run_option(self, exp=False) -> str:
        """Allow user to specify whether to run in parallel or command line

        Parameters
        ----------
        self : self
            self

        Returns
        -------
        str
            command line or submitted as a job.
        """
        if exp:
            config = self.exp_default.set_index("Description")
        else:
            config = self.comp_default.set_index("Description")

        runoption = "c"

        if not sys.platform.startswith("win"):
            for testname, row in config.iterrows():
                if bool(row["OnlyInput"]):
                    runoption = "c"
                    break
            else:
                while True:
                    runoption = input(
                        " Would you like to run in the command line, c, or submit as a job, s? "
                    )
                    if runoption == "c":
                        break
                    elif runoption == "s":
                        if pd.isnull(self.batch_system):
                            print(
                                " Cannot submit as a batch job, as no batch system has been define in the config file."
                            )
                        else:
                            break
                    elif runoption == "back":
                        break
                    elif runoption == "exit":
                        break
                    else:
                        print(" Please enter a valid option")

        return runoption

    def get_lib_name(self, suffix: str) -> str:
        """
        Get the name of the library from its suffix. If a name was not
        specified in the configuration file the same suffix is returned

        Parameters
        ----------
        suffix : str
            e.g. 21c .

        Returns
        -------
        str
            Name of the library.

        """
        df = self.lib.set_index("Suffix")
        # strip the suffix from dots, just in case
        suffix = suffix.strip(".")
        try:
            name = df.loc[suffix, "Name"]
        except KeyError:
            name = suffix
        return name


jade = """
       8888888       oo       888oo       o8888o
           88      o8 8o      88  8oo    88     8
           88     o8   8o     88    8o   88     8
           88    o8=====8o    88    8o   88====°
       88  88   o8       8o   88  8oo    8o
       °°8888  o8         8o  888oo       oo88888
"""

initialtext = """
      Welcome to JADE, a nuclear libraries V&V test suite

      This is the log file, all main events will be recorded here
-------------------------------------------------------------------------------
###############################################################################
"""

bar = """
##############################################################################
"""


class Log:
    """
    This object stores important milestones of the session
    """

    def __init__(self, logfile):
        """
        Initialize the log file

        logfile: (str) path to logfile
        """
        # outpath for log file
        self.file = logfile

        self.text = jade + initialtext

    def adjourn(self, text, spacing=True, time=False):
        """
        Adjourn the log file
        """
        if spacing:
            text = "\n\n" + text.strip("\n")
        self.text = self.text + text

        if time:
            self.text = self.text + "    " + str(datetime.datetime.now())

        with open(self.file, "w") as outfile:
            outfile.write(self.text)

    def bar_adjourn(self, text, spacing=True):
        """
        Adjourn the log file with hashtag style
        """
        if len(text) > 75:  # There is no space, the bar request is ignored
            self.text = self.text + text
        else:
            hashlen = (len(bar) - len(text)) / 2
            if hashlen % 1 != 0:
                after = int(hashlen - 1)
            else:
                after = int(hashlen)
            before = int(hashlen)

            bartext = bar[: before - 1] + " " + text + " " + bar[-after + 1 :]

            if spacing:
                bartext = "\n\n" + bartext

            self.text = self.text + bartext

        with open(self.file, "w") as outfile:
            outfile.write(self.text)
