# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:57:26 2020

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

MULTI_TEST = [
    'Sphere',
    'Oktavian',
    'SphereSDDR',
    'FNG',
    'Tiara-BC',
    'Tiara-BS',
    'Tiara-FC',
    'FNS-TOF',
    'FNG-BKT',
    'FNG-W',
    'ASPIS-Fe88',
    'TUD-Fe',
    'TUD-W']
EXP_TAG = 'Exp'


class Status():
    def __init__(self, session):
        """
        Stores the state of the JADE runs and post-processing.

        Parameters
        ----------
        session : main.Session
            JADE session.

        Returns
        -------
        None.

        """
        # Paths
        self.test_path = session.path_test
        self.run_path = session.path_run
        self.single_path = session.path_single
        self.comparison_path = session.path_comparison

        self.config = session.conf

        # Initialize run tree
        self.run_tree = self.update_run_status()
        # Initialize pp trees
        self.comparison_tree, self.single_tree = self.update_pp_status()

    # Updated by S. Bradnam to include new level, code, between test and zaid.
    def update_run_status(self):
        """
        Read/Update the run tree status. All files produced by runs are
        registered

        Returns
        -------
        libraries : dic
            dictionary of dictionaries representing the run tree

        """

        # Create nested dictionaries to store info on libraries, tests, codes
        # and files.
        libraries = {}
        for lib in os.listdir(self.run_path):
            libraries[lib] = {}
            cp = os.path.join(self.run_path, lib)
            for test in os.listdir(cp):
                if test in MULTI_TEST:
                    libraries[lib][test] = {}
                    cp1 = os.path.join(cp, test)
                    for code in os.listdir(cp1):
                        libraries[lib][test][code] = {}
                        cp2 = os.path.join(cp1, code)
                        for zaid in os.listdir(cp2):
                            libraries[lib][test][code][zaid] = []
                            cp3 = os.path.join(cp2, zaid)
                            for file in os.listdir(cp3):
                                libraries[lib][test][code][zaid].append(file)
                else:
                    libraries[lib][test] = {}
                    cp1 = os.path.join(cp, test)
                    for code in os.listdir(cp1):
                        libraries[lib][test][code] = []
                        cp2 = os.path.join(cp1, code)
                        for file in os.listdir(cp2):
                            libraries[lib][test][code].append(file)

        # Update tree
        self.run_tree = libraries

        return libraries

    # Updated by S. Bradnam, UKAEA to include new level, code.
    def update_pp_status(self) -> tuple:
        """
        Read/Update the post processing tree status. All files produced by
        post processing registered

        Returns
        -------
        comparison_tree : dic
            Dictionary registering all test post processed for each
            comparison of libraries.
        single_tree : dic
            Dictionary registering all test post processed performed for
            single libraries.

        """
        # Read comparison tree
        comparison_tree = {}
        cp = self.comparison_path
        for lib in os.listdir(cp):
            comparison_tree[lib] = {}
            cp1 = os.path.join(cp, lib)
            for test in os.listdir(cp1):
                comparison_tree[lib][test] = []
                cp2 = os.path.join(cp1, test)
                for code in os.listdir(cp2):
                    comparison_tree[lib][test].append(code)

        # Read Single library tree
        single_tree = {}
        cp = self.single_path
        for lib in os.listdir(cp):
            single_tree[lib] = {}
            cp1 = os.path.join(cp, lib)
            for test in os.listdir(cp1):
                single_tree[lib][test] = []
                cp2 = os.path.join(cp1, test)
                for code in os.listdir(cp2):
                    single_tree[lib][test].append(code)

        # Update Trees
        self.comparison_tree = comparison_tree
        self.single_tree = single_tree

        return comparison_tree, single_tree

    def get_path(self, tree: str, itinerary: list) -> str:
        """
        Get the resulting path of an itinery on one tree

        Parameters
        ----------
        tree : str
            Either 'comparison', 'single', or 'run'.
        itinerary : list
            list of strings representing the step to take inside the tree.

        Raises
        ------
        KeyError
            if var tree is not among possible strings.

        Returns
        -------
        cp : str/path
            path to final step.
        """

        # Identify Tree and starting path
        if tree == "run":
            # tree = self.run_tree
            cp = self.run_path
        elif tree == "single":
            # tree = self.single_tree
            cp = self.single_path
        elif tree == "comparison":
            # tree = self.comparison_tree
            cp = self.comparison_path
        else:
            raise KeyError(str(tree) + " is not a valid option.")

        for step in itinerary:
            cp = os.path.join(cp, step)

        return cp

    def get_unfinished_zaids(self, lib) -> tuple:
        """
        Identify zaids to run for rerun or continuation purposes

        Parameters
        ----------
        lib : str
            library to check.

        Returns
        -------
        unfinished : list
            zaids/typical materials not run.

        """

        # Populate dictionaries
        self.update_run_status()
        test = "Sphere"
        try:
            folders = self.run_tree[lib][test]
        except KeyError:
            return None  # Not Generated

        unfinished = {}
        for code in folders:
            unfinished[code] = []
            for zaid in folders[code]:
                files = folders[code][zaid]
                if not self.check_test_run(files, code):
                    unfinished[code].append(zaid)

        motherdir = os.path.join(self.run_path, lib, test)

        return unfinished, motherdir

    def check_test_run(self, files: list, code: str) -> bool:
        """Check if a test was run successfully for the specified code.

        Parameters
        ----------
        files : list
            filenames inside the test folder
        code : str
            Transport code

        Returns
        -------
        bool
            True if test was ran successfully, False otherwise
        """

        if code == "mcnp" or code == "d1s":
            flag_run_test = self._check_test_mcnp(files)
        if code == "serpent":
            flag_run_test = self._check_test_serpent(files)
        if code == "openmc":
            flag_run_test = self._check_test_openmc(files)

        return flag_run_test

    def _check_test_mcnp(self, files: list) -> bool:
        """
        Check if a test has been run

        Parameters
        ----------
        files : list
            file names inside test folder.

        Returns
        -------
        flag_test_run : Bool
            True if test has been run.

        """
        flag_run_test = False
        for file in files:
            c1 = file[-1] == "m"  # mctal file
            c2 = file[-4:] == "msht"  # meshtally file
            if c1 or c2:
                flag_run_test = True

        return flag_run_test

    def _check_test_serpent(self, files: list) -> bool:
        """Checks to see if Serpent simualtion has been run.

        Parameters
        ----------
        files : list
            file names inside test folder.

        Returns
        -------
        bool
            True if test has been run.
        """
        flag_run_test = False
        for file in files:
            c1 = file[-6:] == "_res.m"  # Serpent outputs matlab format
            c2 = file[-3:] == "out"  # Collects nuclear and material data
            if c1 or c2:
                flag_run_test = True
        return flag_run_test

    def _check_test_openmc(self, files: list) -> bool:
        """Checks to see if OpenMC simualtion has been run.

        Parameters
        ----------
        files : list
            file names inside test folder.

        Returns
        -------
        bool
            True if test has been run.
        """
        flag_run_test = False
        for file in files:
            c1 = file[-3:] == "out"
            c2 = file[-2:] == "h5"
            if c1 or c2:
                flag_run_test = True
        return flag_run_test

    # TODO checking for multiple codes
    def check_override_run(self, lib, session, exp=False):
        """
        Check status of the requested run. If overridden is required permission
        is requested to the user

        Parameters
        ----------
        lib : str
            Library to run.
        session : Session
            Jade Session.
        exp : False
            if True checks the experimental benchmarks. Default is False

        Returns
        -------
        ans : Boolean
            if True proceed with the run, if False, abort.

        """

        test_runned = self.check_lib_run(lib, session, exp=exp)

        # Ask for override
        if len(test_runned) > 0:
            while True:
                print(" The following benchmark(s) have already been run:")
                for code in test_runned:
                    for test in test_runned[code]:
                        print(" - " + code + ": " + test)

                print(
                    """
     You can manage the selection of benchmarks to run in the Config.xlsx file
    """
                )
                i = input(" Would you like to override the results?(y/n) ")

                if i == "y":
                    ans = True
                    logtext = "\nThe following test results have been overwritten:"
                    for code in test_runned:
                        for test in test_runned[code]:
                            logtext = (
                                logtext
                                + "\n"
                                + "- "
                                + code
                                + ": "
                                + test
                                + " ["
                                + lib
                                + "]"
                            )
                    session.log.adjourn(logtext)
                    break
                elif i == "n":
                    ans = False
                    break
                else:
                    print('\n please select one between "y" or "n"')

        else:
            ans = True

        return ans

    def check_lib_run(
            self,
            lib,
            session,
            config_option="Run",
            exp=False) -> dict:
        """
        Check if a library has been run. To be considered run a meshtally or
        meshtal have to be produced (for MCNP). Only active benchmarks (specified in
        the configuration file) are checked.

        Parameters
        ----------
        lib : str
            Library to check.
        session : Session
            Jade Session.
        config_option: str
            Specifies the configuration option onto which the check for tests
            "to perform" are registered.
        exp: boolean
            if True checks the experimental benchmarks. Default is False

        Returns
        -------
        test_runned : Bool
            True if all benchmark have been run for the library.

        """
        # Correctly parse the lib input. It may be a dic than only the first
        # dic value needs to be considered
        pat_libs = re.compile(r'"\d\d[a-zA-Z]"')
        if lib[0] == "{":
            libs = pat_libs.findall(lib)
            lib = libs[1][1:-1]

        # Update Tree
        self.update_run_status()
        # Check if/what is already run
        if exp:
            config = self.config.exp_default
        else:
            config = self.config.comp_default

        # Populate dictionary for each test to perform
        to_perform = {
            "mcnp": session.check_active_tests("MCNP", exp=exp),
            "serpent": session.check_active_tests("Serpent", exp=exp),
            "openmc": session.check_active_tests("OpenMC", exp=exp),
            "d1s": session.check_active_tests("d1S", exp=exp),
        }

        test_runned = {}

        for idx, row in config.iterrows():
            filename = str(row["Folder Name"])
            testname = filename.split(".")[0]
            for code in to_perform:
                if testname in to_perform[code]:
                    # Check if benchmark folder exists
                    try:
                        if exp:
                            exps = self.run_tree[lib][testname]
                            for experiment, codes in exps.items():
                                for code, files in codes.items():
                                    flag_run_zaid = self.check_test_run(
                                        files, code)
                                    if flag_run_zaid:
                                        flag_test_run = True
                                if flag_test_run:
                                    if code not in test_runned:
                                        test_runned[code] = []
                                    test_runned[code].append(testname)
                        else:
                            test = self.run_tree[lib][testname][code]
                            if testname in MULTI_TEST:
                                flag_test_run = False
                                for zaid, files in test.items():
                                    flag_run_zaid = self.check_test_run(
                                        files, code)
                                    if flag_run_zaid:
                                        flag_test_run = True
                                if flag_test_run:
                                    if code not in test_runned:
                                        test_runned[code] = []
                                    test_runned[code].append(testname)
                            else:
                                # Check if output is present
                                flag_test_run = self.check_test_run(test, code)
                                if flag_test_run:
                                    if code not in test_runned:
                                        test_runned[code] = []
                                    test_runned[code].append(testname)
                    except KeyError:  # Folder does not exist
                        pass

        return test_runned

    def check_pp_single(self, lib, session, tree="single", exp=False):
        """
        Check if the post processing of a single library or a comparison has
        been already done. To consider it done, all benchmarks must have been
        post-processed

        Parameters
        ----------
        lib : string
            library/ies to check.
        session : Session
            JADE session.
        tree : string, optional
            Either 'single' to check in the single pp tree or 'comparison'
            to check into the comparison one. The default is 'single'.
        exp: boolean
            if True checks the experimental benchmarks. Default is False

        Returns
        -------
        Boolean
            True if PP has been done.

        """
        self.update_pp_status()
        trees = {
            "single": self.single_tree,
            "comparison": self.comparison_tree}
        try:
            library_tests = trees[tree][lib]
            to_pp = session.check_active_tests("Post-Processing", exp=exp)
            # to_pp_exp = session.check_active_tests('Post-Processing', exp=True)
            # to_pp.extend(to_pp_exp)

            ans = True
            for test in to_pp:
                if test not in library_tests:
                    ans = False
            return ans
        except KeyError:
            # print('entered in key error')
            return False

    def check_override_pp(self, session, exp=False):
        """
        Asks for the library/ies to post-process and checks which tests have
        already been performed and would be overidden according to the
        configuration file.
        This can be used also to check if in a post processing of multiple
        libraries wich single library post processing is missing.

        Parameters
        ----------
        session : Session
            JADE session
        exp: boolean
            if True checks the experimental benchmarks. Default is False

        Returns
        -------
        ans: Boolean
            True if the PP can begin (Possible override has been accepted).
        to_single_pp: list
            list of libraries that need to be single post-processed
        lib_input: str
            libraries input that were given

        """
        lib_input = input(" Libraries to post-process (e.g. 31c-71c): ")
        # Individuate libraries to pp

        libs = lib_input.split("-")

        if lib_input == "back":
            return None, None, lib_input

        if lib_input == "exit":
            return None, None, lib_input
        if exp:
            tagpp = "Comparison"
        else:
            if len(libs) == 1:
                tagpp = "Single Libraries"
            else:
                tagpp = "Comparison"

        # Check if libraries have been run
        flag_not_run = False
        for lib in libs:
            test_run = self.check_lib_run(
                lib, session, "Post-Processing", exp=exp)
            if len(test_run) == 0:  # TODO not checking for each benchmark
                flag_not_run = True
                lib_not_run = lib

        to_single_pp = []

        if flag_not_run:
            ans = False
            print(" " + lib_not_run + " was not run. Please run it first.")
        else:
            # Check if single pp has been done (if not experimental benchmark)
            if not exp:
                for lib in libs:
                    if not self.check_pp_single(lib, session):
                        to_single_pp.append(lib)

            # Single Library PP
            if tagpp == "Single Libraries":
                # Ask for override
                if len(to_single_pp) == 0:
                    lib = libs[0]
                    to_single_pp = [lib]
                    while True:
                        print(
                            """
 One or more benchmark were already post-processed for this library.
 You can manage the selection of benchmarks in the Config.xlsx file.
"""
                        )
                        i = input(
                            " Would you like to override the results?(y/n) ")
                        if i == "y":
                            ans = True
                            logtext = (
                                "\nThe Post-Process for library "
                                + str(lib)
                                + " has been overwritten"
                            )
                            session.log.adjourn(logtext)
                            break
                        elif i == "n":
                            ans = False
                            break
                        else:
                            print('\n please select one between "y" or "n"')

                else:
                    ans = True

            # Libraries comparison PP
            elif tagpp == "Comparison":
                # Check if comparisons have been done
                if exp:
                    name = EXP_TAG
                    for lib in libs:
                        name = name + "_Vs_" + lib
                else:
                    name = libs[0]
                    for lib in libs[1:]:
                        name = name + "_Vs_" + lib

                override = self.check_pp_single(
                    name, session, tree="comparison", exp=exp
                )
                # Ask for override
                if override:
                    while True:
                        print(
                            """
 A comparison for these libraries was already performed.
"""
                        )
                        i = input(
                            " Would you like to override the results?(y/n) ")
                        if i == "y":
                            ans = True
                            logtext = (
                                "\nThe Post-Process for libraries "
                                + str(lib)
                                + " has been overwritten"
                            )
                            session.log.adjourn(logtext)
                            break
                        elif i == "n":
                            ans = False
                            break
                        else:
                            print('\n please select one between "y" or "n"')
                else:
                    ans = True

        return ans, to_single_pp, lib_input


# def gen_dict_extract(key, var):
#     if hasattr(var, 'items'):
#         for k, v in var.items():
#             if k == key:
#                 yield v
#             if isinstance(v, dict):
#                 for result in gen_dict_extract(key, v):
#                     yield result
#             elif isinstance(v, list):
#                 for d in v:
#                     for result in gen_dict_extract(key, d):
#                         yield result
