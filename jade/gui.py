# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:24:06 2019

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

import os
import logging
import sys
import json
from typing import TYPE_CHECKING
import logging

from tqdm import tqdm

import jade.computational as cmp
import jade.postprocess as pp
import jade.testrun as testrun
import jade.utilitiesgui as uty
from jade.__version__ import __version__
from jade.status import EXP_TAG
from jade.input_fetch import fetch_iaea_inputs

if TYPE_CHECKING:
    from jade.main import Session

# colors
CRED = "\033[91m"
CEND = "\033[0m"

date = "10/05/2022"
version = __version__
POWERED_BY = "NIER, UNIBO, F4E, UKAEA"


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


exit_text = "\nSession concluded normally \n"

header = (
    """
 ***********************************************
              Welcome to JADE """
    + version
    + """
      A nuclear libraries V&V Test Suite
          Release date: """
    + date
    + "\n"
)

principal_menu = (
    header
    + """
                 MAIN MENU

        Powered by {}
 ***********************************************
 MAIN FUNCTIONS

 * Open Quality check menu                (qual)
 * Open Computational Benchmark menu      (comp)
 * Open Experimental Benchmark menu        (exp)
 * Open Post-Processing menu              (post)
 -----------------------------------------------
 UTILITIES

 * Print available libraries          (printlib)
 * Restore default configurations      (restore)
 * Change ACE lib suffix                (acelib)
 * Remove all runtpe files           (rmvruntpe)
 * Compare ACE/EXFOR                (comparelib)
 * Fetch IAEA inputs                 (iaeafetch)
 * Add RMODE 0 key                       (rmode)               
 -----------------------------------------------

 * Exit                                   (exit)
""".format(
        POWERED_BY
    )
)


def mainloop(session: Session):
    """
    This handle the actions related to the main menu

    session: (Session) object representing the current Jade session
    """
    clear_screen()
    print(principal_menu)
    while True:
        option = input(" Enter action: ")

        if option == "comp":
            comploop(session)

        elif option == "exp":
            exploop(session)

        elif option == "qual":
            clear_screen()
            print(principal_menu)
            print(" Currently not developed. Please select another option")

        elif option == "post":
            pploop(session)

        elif option == "printlib":
            uty.print_libraries(session.lib_manager)

        elif option == "restore":
            uty.restore_default_config(session)

        elif option == "acelib":
            uty.change_ACElib_suffix()
            print("\n Suffix change was completed\n")

        elif option == "rmvruntpe":
            uty.clean_runtpe(session.path_run)
            print("\n Runtpe files have been removed\n")

        elif option == "rmode":
            uty.add_rmode(session)
            msg = "RMODE 0 key has been added to the inputs"
            logging.info(msg)
            print(f"\n {msg}\n")

        elif option == "iaeafetch":
            # token = input(" Please enter your GitHub token: ")
            ans = fetch_iaea_inputs(session)
            if ans:
                print("\n IAEA inputs have been successfully downloaded\n")
            else:
                print(
                    "\n Error in downloading the IAEA inputs, double check your token\n"
                )

        elif option == "comparelib":
            uty.print_XS_EXFOR(session)

        elif option == "exit":
            logging.info("\nSession concluded normally \n")
            sys.exit()

        else:
            clear_screen()
            print(principal_menu)
            print(" Please enter a valid option!")


computational_menu = (
    header
    + """
          COMPUTATIONAL BENCHMARK MENU

        Powered by {}
 ***********************************************

 * Print available libraries          (printlib)
 * Assess library                       (assess)
 * Continue assessment                (continue)
 * Back to main menu                      (back)
 * Exit                                   (exit)
""".format(
        POWERED_BY
    )
)


def comploop(session: Session):
    """
    This handle the actions related to the computational benchmarck menu

    session: (Session) object representing the current Jade session

    """
    clear_screen()
    print(computational_menu)
    while True:
        option = input(" Enter action: ")

        if option == "printlib":
            uty.print_libraries(session.lib_manager)

        elif option == "assess":
            # Select and check library
            codes_run = list(session.check_active_tests("Run").keys())
            codes_only_input = list(session.check_active_tests("OnlyInput").keys())
            codes = list(set(codes_run + codes_only_input))
            lib = select_lib(session.lib_manager, codes)
            if lib == "back":
                comploop(session)
            if lib == "exit":
                logging.info(exit_text)
                sys.exit()
            runoption = session.conf.run_option()
            if runoption == "back":
                comploop(session)
            if runoption == "exit":
                logging.info(exit_text)
                sys.exit()
            ans = session.state.check_override_run(lib, session)
            # If checks are ok perform assessment
            if ans:
                # Logging
                bartext = "Computational benchmark execution started"
                logging.info(bartext)
                logging.info("Selected Library: %s", lib)
                print(
                    " ########################### COMPUTATIONAL BENCHMARKS EXECUTION ###########################\n"
                )
                cmp.executeBenchmarksRoutines(session, lib, runoption)  # Core function
                print(
                    " ####################### COMPUTATIONAL BENCHMARKS RUN ENDED ###############################\n"
                )
                t = "Computational benchmark execution ended"
                logging.info(t)
            else:
                clear_screen()
                print(computational_menu)
                print(" Assessment cancelled.")

        elif option == "continue":
            # Select and check library
            # Warning: this is done only for sphere test at the moment
            codes = list(session.check_active_tests("Run").keys())
            lib = select_lib(session.lib_manager, codes)
            if lib == "back":
                comploop(session)
            if lib == "exit":
                logging.info(exit_text)
                sys.exit()
            try:
                unfinished, motherdir = session.state.get_unfinished_zaids(lib)
            except TypeError:
                unfinished = None

            if unfinished is None:
                print(" The selected library was not assessed")
            elif len(unfinished) == 0:
                print(" The assessment is already completed")
            else:
                runoption = session.conf.run_option()
                print(" Completing sphere assessment:")
                logging.info("Assessment of: %s  started", lib)
                flagOk = True
                for code, directories in unfinished.items():
                    for directory in tqdm(directories, desc=code):
                        path = os.path.join(motherdir, directory, code)
                        name = directory + "_"
                        if code == "mcnp":
                            flag = testrun.Test.run_mcnp(
                                lib,
                                session.conf,
                                session.lib_manager,
                                name,
                                path,
                                runoption=runoption,
                            )
                        elif code == "openmc":
                            flag = testrun.Test.run_openmc(
                                lib,
                                session.conf,
                                session.lib_manager,
                                path,
                                runoption=runoption,
                            )
                        elif code == "serpent":
                            flag = testrun.Test.run_serpent(
                                lib,
                                session.conf,
                                session.lib_manager,
                                name,
                                path,
                                runoption=runoption,
                            )
                        else:
                            raise ValueError("Code not recognized")

                        if flag:
                            flagOk = False
                            logging.info("%s reached timeout, eliminate folder", name)

                if not flagOk:
                    print(
                        """
 Some MCNP run reached timeout, they are listed in the log file.
 Please remove their folders before attempting to postprocess the library"""
                    )

                print(" Assessment completed")

                logging.info("Assessment of: %s completed", lib)

        elif option == "back":
            mainloop(session)

        elif option == "exit":
            logging.info(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(computational_menu)
            print(" Please enter a valid option!")


experimental_menu = (
    header
    + """
          EXPERIMENTAL BENCHMARK MENU

        Powered by {}
 ***********************************************

 * Print available libraries          (printlib)
 * Assess library                       (assess)
 * Continue assessment                (continue)
 * Back to main menu                      (back)
 * Exit                                   (exit)
""".format(
        POWERED_BY
    )
)


def exploop(session: Session):
    """
    This handle the actions related to the experimental benchmarck menu

    session: (Session) object representing the current Jade session

    """
    clear_screen()
    print(experimental_menu)
    while True:
        option = input(" Enter action: ")

        if option == "printlib":
            uty.print_libraries(session.lib_manager)

        elif option == "assess":
            # Update the configuration file
            session.conf.read_settings()
            # Select and check library
            codes = list(session.check_active_tests("Run", exp=True).keys())
            lib = select_lib(session.lib_manager, codes)
            if lib == "back":
                comploop(session)
            if lib == "exit":
                logging.info(exit_text)
                sys.exit()
            runoption = session.conf.run_option(exp=True)
            if runoption == "back":
                comploop(session)
            if runoption == "exit":
                logging.info(exit_text)
                sys.exit()
            # it may happen that lib are two but only the first is the assessed
            pieces = lib.split("-")
            if len(pieces) > 1:
                libtocheck = pieces[0]
            else:
                libtocheck = lib
            ans = session.state.check_override_run(libtocheck, session, exp=True)
            # If checks are ok perform assessment
            if ans:
                # Logging
                bartext = "Experimental benchmark execution started"
                logging.info(bartext)
                logging.info("Selected Library: %s", lib)
                print(
                    " ########################### EXPERIMENTAL BENCHMARKS EXECUTION ###########################\n"
                )
                # Core function
                cmp.executeBenchmarksRoutines(session, lib, runoption, exp=True)
                print(
                    " ####################### EXPERIMENTAL BENCHMARKS RUN ENDED ###############################\n"
                )
                t = "Experimental benchmark execution ended"
                logging.info(t)
            else:
                clear_screen()
                print(computational_menu)
                print(" Assessment canceled.")

        elif option == "continue":
            # Update the configuration file
            session.conf.read_settings()
            clear_screen()
            print(principal_menu)
            print(" Currently not developed. Please select another option")

        elif option == "back":
            mainloop(session)

        elif option == "exit":
            logging.info(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(computational_menu)
            print(" Please enter a valid option!")


pp_menu = (
    header
    + """
          POST PROCESSING MENU

        Powered by {}
 ***********************************************

 * Print tested libraries             (printlib)
 * Post-Process library                     (pp)
 * Compare libraries                   (compare)
 * Compare Vs Experiments              (compexp)
 * Back to main menu                      (back)
 * Exit                                   (exit)
""".format(
        POWERED_BY
    )
)


def pploop(session: Session):
    """
    This handle the actions related to the post-processing menu

    session: (Session) object representing the current Jade session

    """
    clear_screen()
    print(pp_menu)
    while True:
        option = input(" Enter action: ")

        if option == "printlib":
            lib_tested = list(session.state.run_tree.keys())
            print(lib_tested)

        elif option == "pp":
            # Update the configuration file
            session.conf.read_settings()
            # Select and check library
            ans, to_single_pp, lib_input = session.state.check_override_pp(
                session, force_one_lib=True
            )
            if lib_input == "back":
                pploop(session)
            if lib_input == "exit":
                sys.exit()
            # If checks are ok perform assessment
            if ans:
                lib = to_single_pp[0]
                # Check active tests
                to_perform = session.check_active_tests("Post-Processing")
                # For the moment no pp is foreseen for experimental benchmarks
                # to_perf_exp = session.check_active_tests('Post-Processing',
                #                                          exp=True)
                # to_perform.extend(to_perf_exp)

                # Logging
                bartext = "Post-Processing started"
                logging.info(bartext)
                logging.info("Selected Library: %s", lib)
                print(
                    "\n ########################### POST-PROCESSING STARTED ###########################\n"
                )
                # Core function
                for code, testnames in to_perform.items():
                    pp.postprocessBenchmark(session, lib_input, code, testnames)
                # for testname in to_perform:
                #    try:
                #        pp.postprocessBenchmark(session, lib, testname)
                #    except PermissionError as e:
                #        clear_screen()
                #        print(pp_menu)
                #        print(' '+str(e))
                #        print(' Please close all excel/word files and retry')
                #        continue
                print(
                    "\n ######################### POST-PROCESSING ENDED ###############################\n"
                )
                t = "Post-Processing completed"
                logging.info(t)

        elif option == "compare":
            # Update the configuration file
            session.conf.read_settings()

            # Select and check library
            ans, to_single_pp, lib_input = session.state.check_override_pp(session)

            if ans:
                # Logging
                bartext = "Comparison Post-Processing started"
                logging.info(bartext)
                logging.info("Selected Library: %s", lib_input)
                print(
                    "\n ########################### COMPARISON STARTED ###########################\n"
                )

                # Check active tests
                to_perform = session.check_active_tests("Post-Processing")

                # Execute single pp
                for lib in to_single_pp:
                    for code, testnames in to_perform.items():
                        try:
                            print(" Single PP of library " + lib + " required")
                            pp.postprocessBenchmark(session, lib, code, testnames)
                            logging.info(
                                """
Additional Post-Processing of library: %s completed\n""",
                                lib,
                            )
                        except PermissionError as e:
                            clear_screen()
                            print(pp_menu)
                            print(" " + str(e))
                            print(" Please close all excel/word files and retry")
                            continue

                # Execute Comparison
                for code, testnames in to_perform.items():
                    try:
                        pp.compareBenchmark(session, lib_input, code, testnames)
                    except PermissionError as e:
                        clear_screen()
                        print(pp_menu)
                        print(" " + str(e))
                        print(" Please close all excel/word files and retry")
                        continue

                print(
                    "\n ######################### COMPARISON ENDED ###############################\n"
                )
                t = "Post-Processing completed"
                logging.info(t)

        elif option == "compexp":
            # Update the configuration file
            session.conf.read_settings()

            # Select and check library
            ans, to_single_pp, lib_input = session.state.check_override_pp(
                session, exp=True
            )

            if ans:
                # Logging
                bartext = "Comparison Post-Processing started"
                logging.info(bartext)
                logging.info("Selected Library:  %s", lib_input)
                print(
                    "\n ########################### COMPARISON STARTED ###########################\n"
                )

                # Check active tests
                to_perform = session.check_active_tests("Post-Processing", exp=True)

                #                 # Execut single pp
                #                 for lib in to_single_pp:
                #                     for testname in to_perform:
                #                         try:
                #                             print(' Single PP of library '+lib+' required')
                #                             pp.postprocessBenchmark(session, lib, testname)
                #                             logging.info("""
                # Additional Post-Processing of library:"""+lib+' completed\n', spacing=False)
                #                         except PermissionError as e:
                #                             clear_screen()
                #                             print(pp_menu)
                #                             print(' '+str(e))
                #                             print(' Please close all excel/word files and retry')
                #                             continue

                # Execute Comparison
                lib_input = EXP_TAG + "-" + lib_input  # Insert the exp tag
                for code, testname in to_perform.items():
                    try:
                        pp.compareBenchmark(
                            session, lib_input, code, testname, exp=True
                        )
                    except PermissionError as e:
                        clear_screen()
                        print(pp_menu)
                        print(" " + str(e))
                        print(" Please close all excel/word files and retry")
                        continue

                print(
                    "\n ######################### COMPARISON ENDED ###############################\n"
                )
                t = "Post-Processing completed"
                logging.info(t)

        elif option == "back":
            mainloop(session)

        elif option == "exit":
            logging.info(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(pp_menu)
            print(" Please enter a valid option!")


def select_lib(lm, codes: list[str] = ["mcnp"]) -> str:
    """
    Prompt a library input selection with Xsdir availabilty check

    Parameters
    ----------
    code: list[str], optional
        code for which the library is selected. default is MCNP

    Returns
    -------
    lib : str
        Library to assess.

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
        # check that library is available in all requested codes

        if lm.is_lib_available(lib, codes):
            break  # if the library is available for all codes, break loop

        elif lib[0] == "{":
            libs = json.loads(lib)
            # all libraries should be available
            tocheck = list(libs.values())
            tocheck.extend(list(libs.keys()))
            flag = True
            for val in tocheck:
                if not lm.is_lib_available(val, codes):
                    print(error.format(val))
                    flag = False
            if flag:
                break

        elif "-" in lib:
            libs = lib.split("-")
            flag = True
            for val in libs:
                if not lm.is_lib_available(val, codes):
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

        if i > 20:
            raise ValueError("Too many wrong inputs")
    return lib
