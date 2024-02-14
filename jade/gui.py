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
from typing import TYPE_CHECKING
import os
import sys

import jade.computational as cmp
import jade.postprocess as pp
import jade.testrun as testrun
import jade.utilitiesgui as uty
from jade.__version__ import __version__
from tqdm import tqdm
from jade.status import EXP_TAG

if TYPE_CHECKING:
    from jade.main import Session


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
 * Translate an MCNP input               (trans)
 * Print materials info               (printmat)
 * Generate material                  (generate)
 * Switch fractions                     (switch)
 * Change ACE lib suffix                (acelib)
 * Produce D1S Reaction file             (react)
 * Remove all runtpe files           (rmvruntpe)
 * Compare ACE/EXFOR                (comparelib)
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

        elif option == "trans":
            newlib = session.lib_manager.select_lib()
            if newlib == "back":
                mainloop(session)
            if newlib == "exit":
                session.log.adjourn(exit_text)
                sys.exit()
            inputfile = input(" MCNP input file: ")

            if newlib in session.lib_manager.libraries:
                ans = uty.translate_input(session, newlib, inputfile)
                if ans:
                    print(" Translation successfully completed!\n")
                    session.log.adjourn(
                        "file" + inputfile + " successfully translated to " + newlib
                    )
                else:
                    print(
                        """
    Error:
    The file does not exist or can't be opened
                      """
                    )

            else:
                print(
                    """
    Error:
    The selected library is not available.
    Check your available libraries using 'printlib'
                      """
                )

        elif option == "printmat":
            inputfile = input(" MCNP Input file of interest: ")
            ans = uty.print_material_info(session, inputfile)
            if ans:
                print(" Material infos printed")
            else:
                print(
                    """
    Error:
    Either the input or output files do not exist or can't be opened
                      """
                )

        elif option == "generate":
            inputfile = uty.select_inputfile(" MCNP input file: ")
            message = " Fraction type (either 'mass' or 'atom'): "
            options = ["mass", "atom"]
            fraction_type = uty.input_with_options(message, options)
            materials = input(" Source materials (e.g. m1-m10): ")
            percentages = input(" Materials percentages (e.g. 0.1-0.9): ")
            lib = session.lib_manager.select_lib()
            if lib == "back":
                mainloop(session)
            if lib == "exit":
                session.log.adjourn(exit_text)
                sys.exit()
            materials = materials.split("-")
            percentages = percentages.split("-")

            if len(materials) == len(percentages):
                ans = uty.generate_material(
                    session,
                    inputfile,
                    materials,
                    percentages,
                    lib,
                    fractiontype=fraction_type,
                )
                if ans:
                    print(" Material generated")
                else:
                    print(
                        """
    Error:
    Either the input or output files can't be opened
                          """
                    )

            else:
                print(
                    """
    Error:
    The number of materials and percentages must be the same
                          """
                )

        elif option == "switch":
            # Select MCNP input
            inputfile = uty.select_inputfile(" MCNP input file: ")
            # Select fraction type
            options = ["mass", "atom"]
            message = " Fraction to switch to (either 'mass' or 'atom'): "
            fraction_type = uty.input_with_options(message, options)

            # Switch fraction
            ans = uty.switch_fractions(session, inputfile, fraction_type)
            if ans:
                print(" Fractions have been switched")
            else:
                print(
                    """
    Error:
    Either the input or output files can't be opened"""
                )

        elif option == "acelib":
            uty.change_ACElib_suffix()
            print("\n Suffix change was completed\n")

        elif option == "react":
            uty.get_reaction_file(session)
            print("\n Reaction file has been dumped\n")

        elif option == "rmvruntpe":
            uty.clean_runtpe(session.path_run)
            print("\n Runtpe files have been removed\n")

        elif option == "comparelib":
            uty.print_XS_EXFOR(session)

        elif option == "exit":
            session.log.adjourn("\nSession concluded normally \n")
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
            lib = session.lib_manager.select_lib()
            if lib == "back":
                comploop(session)
            if lib == "exit":
                session.log.adjourn(exit_text)
                sys.exit()
            runoption = session.conf.run_option()
            if runoption == "back":
                comploop(session)
            if runoption == "exit":
                session.log.adjourn(exit_text)
                sys.exit()
            ans = session.state.check_override_run(lib, session)
            # If checks are ok perform assessment
            if ans:
                # Logging
                bartext = "Computational benchmark execution started"
                session.log.bar_adjourn(bartext)
                session.log.adjourn(
                    "Selected Library: " + lib, spacing=False, time=True
                )
                print(
                    " ########################### COMPUTATIONAL BENCHMARKS EXECUTION ###########################\n"
                )
                cmp.executeBenchmarksRoutines(session, lib, runoption)  # Core function
                print(
                    " ####################### COMPUTATIONAL BENCHMARKS RUN ENDED ###############################\n"
                )
                t = "Computational benchmark execution ended"
                session.log.bar_adjourn(t)
            else:
                clear_screen()
                print(computational_menu)
                print(" Assessment cancelled.")

        elif option == "continue":
            # Select and check library
            # Warning: this is done only for sphere test at the moment
            lib = session.lib_manager.select_lib()
            if lib == "back":
                comploop(session)
            if lib == "exit":
                session.log.adjourn(exit_text)
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
                print(" Completing sphere assessment:")
                session.log.adjourn(
                    "Assessment of: " + lib + " started", spacing=False, time=True
                )
                flagOk = True
                for directory in tqdm(unfinished):
                    path = os.path.join(motherdir, directory)
                    name = directory + "_"

                    flag = testrun.Test._runMCNP(
                        "mcnp6", name, path, cpu=session.conf.cpu
                    )
                    if flag:
                        flagOk = False
                        session.log.adjourn(name + " reached timeout, eliminate folder")

                if not flagOk:
                    print(
                        """
 Some MCNP run reached timeout, they are listed in the log file.
 Please remove their folders before attempting to postprocess the library"""
                    )

                print(" Assessment completed")

                session.log.adjourn(
                    "Assessment of: " + lib + " completed", spacing=True, time=True
                )

        elif option == "back":
            mainloop(session)

        elif option == "exit":
            session.log.adjourn(exit_text)
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
            lib = session.lib_manager.select_lib()
            if lib == "back":
                comploop(session)
            if lib == "exit":
                session.log.adjourn(exit_text)
                sys.exit()
            runoption = session.conf.run_option()
            if runoption == "back":
                comploop(session)
            if runoption == "exit":
                session.log.adjourn(exit_text)
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
                runoption = session.conf.run_option(exp=True)
                bartext = "Experimental benchmark execution started"
                session.log.bar_adjourn(bartext)
                session.log.adjourn(
                    "Selected Library: " + lib, spacing=False, time=True
                )
                print(
                    " ########################### EXPERIMENTAL BENCHMARKS EXECUTION ###########################\n"
                )
                # Core function
                cmp.executeBenchmarksRoutines(session, lib, runoption, exp=True)
                print(
                    " ####################### EXPERIMENTAL BENCHMARKS RUN ENDED ###############################\n"
                )
                t = "Experimental benchmark execution ended"
                session.log.bar_adjourn(t)
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
            session.log.adjourn(exit_text)
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
            ans, to_single_pp, lib_input = session.state.check_override_pp(session)
            if lib_input == "back":
                pploop(session)
            if lib_input == "exit":
                sys.exit()
            # If checks are ok perform assessment
            if ans:
                lib = to_single_pp[0]
                # Check active tests
                # to_perform = session.check_active_tests('Post-Processing')
                # For the moment no pp is foreseen for experimental benchmarks
                # to_perf_exp = session.check_active_tests('Post-Processing',
                #                                          exp=True)
                # to_perform.extend(to_perf_exp)

                # Logging
                bartext = "Post-Processing started"
                session.log.bar_adjourn(bartext)
                session.log.adjourn("Selected Library: " + lib, spacing=False)
                print(
                    "\n ########################### POST-PROCESSING STARTED ###########################\n"
                )
                # Core function
                pp.postprocessBenchmark(session, lib)
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
                session.log.bar_adjourn(t, spacing=False)

        elif option == "compare":
            # Update the configuration file
            session.conf.read_settings()

            # Select and check library
            ans, to_single_pp, lib_input = session.state.check_override_pp(session)

            if ans:
                # Logging
                bartext = "Comparison Post-Processing started"
                session.log.bar_adjourn(bartext)
                session.log.adjourn("Selected Library: " + lib_input, spacing=True)
                print(
                    "\n ########################### COMPARISON STARTED ###########################\n"
                )

                # Check active tests
                to_perform = session.check_active_tests("Post-Processing")

                # Execute single pp
                for lib in to_single_pp:
                    print("to single pp", to_single_pp)
                    for testname in to_perform:
                        print("to_perform", to_perform)
                        try:
                            print(" Single PP of library " + lib + " required")
                            pp.postprocessBenchmark(session, lib)
                            session.log.adjourn(
                                """
Additional Post-Processing of library:"""
                                + lib
                                + " completed\n",
                                spacing=False,
                            )
                        except PermissionError as e:
                            clear_screen()
                            print(pp_menu)
                            print(" " + str(e))
                            print(" Please close all excel/word files and retry")
                            continue

                # Execute Comparison
                for testname in to_perform:
                    try:
                        pp.compareBenchmark(session, lib_input, testname)
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
                session.log.bar_adjourn(t, spacing=False)

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
                session.log.bar_adjourn(bartext)
                session.log.adjourn("Selected Library: " + lib_input, spacing=True)
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
                #                             session.log.adjourn("""
                # Additional Post-Processing of library:"""+lib+' completed\n', spacing=False)
                #                         except PermissionError as e:
                #                             clear_screen()
                #                             print(pp_menu)
                #                             print(' '+str(e))
                #                             print(' Please close all excel/word files and retry')
                #                             continue

                # Execute Comparison
                lib_input = EXP_TAG + "-" + lib_input  # Insert the exp tag
                for testname in to_perform:
                    try:
                        pp.compareBenchmark(session, lib_input, testname, exp=True)
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
                session.log.bar_adjourn(t, spacing=False)

        elif option == "back":
            mainloop(session)

        elif option == "exit":
            session.log.adjourn(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(pp_menu)
            print(" Please enter a valid option!")
