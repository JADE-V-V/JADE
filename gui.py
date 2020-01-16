# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:24:06 2019

@author: Davide Laghi
"""
import os
import sys
import computational as cmp
import utilitiesgui as uty
import postprocess as pp
import status


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


exit_text = '\nSession concluded normally \n'


principal_menu = """
 ***********************************************
              Welcome to JADE
      A nuclear libraries V&V Test Suite
 ***********************************************
 MAIN FUNCTIONS

 * Open Quality check menu                (qual)
 * Open Computational Benchmark menu      (comp)
 * Open Experimental Benchmark menu        (exp)
 * Open Post-Processing menu              (post)
 -----------------------------------------------
 UTILITIES

 * Print available libraries          (printlib)
 * Translate an MCNP input               (trans)
 -----------------------------------------------

 * Exit                                   (exit)
"""


def mainloop(session):
    """
    This handle the actions related to the main menu

    session: (Session) object representing the current Jade session
    """
    clear_screen()
    print(principal_menu)
    while True:
        option = input(' Enter action: ')

        if option == 'comp':
            comploop(session)

        elif option == 'exp':
            clear_screen()
            print(principal_menu)
            print(' Currently not developed. Please select another option')

        elif option == 'qual':
            clear_screen()
            print(principal_menu)
            print(' Currently not developed. Please select another option')

        elif option == 'post':
            pploop(session)

        elif option == 'printlib':
            uty.print_libraries(session.lib_manager)

        elif option == 'trans':
            newlib = input(' Library to use: ')
            inputfile = input(' Input to translate: ')

            if newlib in session.lib_manager.libraries:
                uty.translate_input(session, newlib, inputfile)
                print(' Translation successfully completed!\n')
                session.log.adjourn('file'+inputfile +
                                    ' successfully translated to ' + newlib)

            else:
                print('''
                      Error:
                      The selected library is not available.
                      Check your available libraries using 'printlib'
                      ''')

        elif option == 'exit':
            session.log.adjourn('\nSession concluded normally \n')
            sys.exit()

        else:
            clear_screen()
            print(principal_menu)
            print(' Please enter a valid option!')


computational_menu = """
 ***********************************************
              Welcome to JADE
      A nuclear libraries V&V Test Suite

          COMPUTATIONAL BENCHMARK MENU
 ***********************************************

 * Print available libraries          (printlib)
 * Assess library                       (assess)
 * Back to main menu                      (back)
 * Exit                                   (exit)
"""


def comploop(session):
    """
    This handle the actions related to the computational benchmarck menu

    session: (Session) object representing the current Jade session

    """
    clear_screen()
    print(computational_menu)
    while True:
        option = input(' Enter action: ')

        if option == 'printlib':
            uty.print_libraries(session.lib_manager)

        elif option == 'assess':
            # Select and check library
            lib = session.lib_manager.select_lib()
            ans = session.state.check_override_run(lib, session)
            # If checks are ok perform assessment
            if ans:
                # Check active tests
                to_perform = session.check_active_tests('Run')
                # Logging
                bartext = 'Computational benchmark execution started'
                session.log.bar_adjourn(bartext)
                session.log.adjourn('Selected Library: '+lib,
                                    spacing=False, time=True)
                print(' ########################### COMPUTATIONAL BENCHMARKS EXECUTION ###########################\n')

                if 'Sphere' in to_perform:
                    cmp.sphereTestRun(session, lib)

                print(' ####################### COMPUTATIONAL BENCHMARKS RUN ENDED ###############################\n')
                t = 'Computational benchmark execution ended'
                session.log.bar_adjourn(t)
            else:
                clear_screen()
                print(computational_menu)
                print(' Assessment canceled.')

        elif option == 'back':
            mainloop(session)

        elif option == 'exit':
            session.log.adjourn(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(computational_menu)
            print(' Please enter a valid option!')


pp_menu = """
 ***********************************************
              Welcome to JADE
      A nuclear libraries V&V Test Suite

          POST PROCESSING MENU
 ***********************************************

 * Print tested libraries             (printlib)
 * Post-Process library                     (pp)
 * Compare libraries                   (compare)
 * Back to main menu                      (back)
 * Exit                                   (exit)
"""


def pploop(session):
    """
    This handle the actions related to the post-processing menu

    session: (Session) object representing the current Jade session

    """
    clear_screen()
    print(pp_menu)
    while True:
        option = input(' Enter action: ')

        if option == 'printlib':
            clear_screen()
            print(pp_menu)
            print(' Currently not developed. Please select another option')

        elif option == 'pp':
            # Select and check library
            ans, to_single_pp = session.state.check_override_pp(session)
            # If checks are ok perform assessment
            if ans:
                lib = to_single_pp[0]
                # Check active tests
                to_perform = session.check_active_tests('Post-Processing')
                # Logging
                bartext = 'Post-Processing started'
                session.log.bar_adjourn(bartext)
                session.log.adjourn('Selected Library: '+lib, spacing=False)
                print('\n ########################### POST-PROCESSING STARTED ###########################\n')

                if 'Sphere' in to_perform:
                    try:
                        pp.postprocessSphere(session, lib)
                    except PermissionError as e:
                        clear_screen()
                        print(pp_menu)
                        print(' '+str(e))
                        print(' Please close all excel files and retry')
                        continue

                print('\n ######################### POST-PROCESSING ENDED ###############################\n')
                t = 'Post-Processing completed'
                session.log.bar_adjourn(t, spacing=False)

        elif option == 'compare':
            # Select and check library
            lib, ans = uty.check_override_pp(session)
            # If checks are ok perform assessment
            if ans:
                # Check active tests
                to_perform = uty.check_active_tests(session, 'Post-Processing')
                # Logging
                bartext = 'Post-Processing started'
                session.log.bar_adjourn(bartext)
                session.log.adjourn('Selected Library: '+lib, spacing=False)
                print('\n ########################### POST-PROCESSING STARTED ###########################\n')

                if 'Sphere' in to_perform:
                    try:
                        pp.postprocessSphere(session, lib)
                    except PermissionError as e:
                        clear_screen()
                        print(pp_menu)
                        print(' '+str(e))
                        print(' Please close all excel files and retry')
                        continue

                print('\n ######################### POST-PROCESSING ENDED ###############################\n')
                t = 'Post-Processing completed'
                session.log.bar_adjourn(t, spacing=False)

            else:
                clear_screen()
                print(computational_menu)
                print(' Post-Processing dismissed.')

        elif option == 'back':
            mainloop(session)

        elif option == 'exit':
            session.log.adjourn(exit_text)
            sys.exit()

        else:
            clear_screen()
            print(pp_menu)
            print(' Please enter a valid option!')
