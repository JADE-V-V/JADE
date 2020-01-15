# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 11:44:13 2019

@author: Davide Laghi
"""
import os
import inputfile as ipt


###############################################################################
# ------------------------ UTILITIES ------------------------------------------
###############################################################################

def translate_input(session, lib, inputfile):
    """
    Translate an input file to a selected library. A log of the translation is
    also produced.
    """

    libmanager = session.lib_manager
    outpath = os.getcwd()
    outpath = os.path.dirname(outpath)
    outpath = os.path.join(outpath, 'Utilities')

    inp = ipt.InputFile.from_text(inputfile)
    info1 = inp.matlist.get_info()
    inp.translate(lib, libmanager)
    inp.update_zaidinfo(libmanager)
    info2 = inp.matlist.get_info()

    newdir = os.path.join(outpath, 'Translation')
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    outfile = os.path.join(newdir, inputfile+'_translated_'+lib)
    inp.write(outfile)

    # Log production
    try:
        info1['Fraction old'] = info1['Fraction']
        info1['Fraction new'] = info2['Fraction']
        perc = (info1['Fraction']-info2['Fraction'])/info1['Fraction']
        info1['Fraction difference [%]'] = perc
        del info1['Fraction']

        outlog = os.path.join(newdir, inputfile+'_translated_'+lib+'_LOG.xlsx')

        info1.to_excel(outlog)
    # In case at leat one entire element was not translated
    except ValueError:
        text = '  Warning: it was impossible to produce the translation Log'
        print(text)
        session.log.adjourn(text)


def print_libraries(libmanager):
    print(libmanager.libraries)


###############################################################################
#  ------------------------ ACCESSORY -----------------------------------------
###############################################################################
# tags


mcnptag = '01_MCNP_Run'
outtag = '02_Output'


def check_override(session):
    # Check if library is available
    while True:
        lib = input(' Library to assess (e.g. 31c): ')
        if lib in session.lib_manager.libraries:
            break
        else:
            print('''
              Error:
              The selected library is not available.
              ''')
    # Check if inputs are already present
    config = session.conf.comp_default
    to_override = []
    for idx, row in config.iterrows():
        filename = str(row['File Name'])
        testname = filename.split('.')[0]

        # Check if inputs of the test already exist
        if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), 'Tests',
                                       mcnptag, lib, testname)):
            # Check if the test needs to be run
            run = row['Run']
            if run is True or run == 'True' or run == 'true':
                to_override.append(testname)

    # Ask for override
    if len(to_override) > 0:
        while True:
            print(' The following benchmark(s) have already been completed:')
            for test in to_override:
                print(' - '+test)

            print("""
 You can manage the selection of benchmarks to run in the Config.xlsx file
""")
            i = input(' Would you like to override the results?(y/n) ')

            if i == 'y':
                ans = True
                logtext = '\nThe following test results have been overwritten:'
                for test in to_override:
                    logtext = logtext+'\n'+'- '+test+' ['+lib+']'
                session.log.adjourn(logtext)
                break
            elif i == 'n':
                ans = False
                break
            else:
                print('\n please select one between "y" or "n"')

    else:
        ans = True

    return lib, ans


def check_override_pp(session):
    """
    Asks for the library/ies to post-process and checks which tests have
    already been performed and would be overidden according to the
    configuration file

    Parameters
    ----------
    session : Session
        JADE session

    Returns
    -------
    lib, ans

    """
    # Check if library is available
    while True:
        lib = input(' Libraries to post-process (e.g. 31c-71c): ')
        testpath = os.path.join(os.path.dirname(os.getcwd()), 'Tests',
                                mcnptag, lib)
        if os.path.exists(testpath):
            break
        else:
            print('''
              Error:
              The selected library was not assessed.
              ''')

    # Individuate libraries to pp
    lib = lib.split('-')
    if len(lib) == 1:
        lib = lib[0]
        tagpp = 'Single Libraries'
    else:
        tagpp = 'Comparison'

    # Check if outputs are already present
    config = session.conf.comp_default
    to_override = []
    for idx, row in config.iterrows():
        filename = str(row['File Name'])
        testname = filename.split('.')[0]

        # Check if outputs of the test already exist
        if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), 'Tests',
                                       outtag, tagpp, lib, testname)):
            # Check if the test needs to be post-processed
            pp = row['Post-Processing']
            if pp is True or pp == 'True' or pp == 'true':
                to_override.append(testname)

    # Ask for override
    if len(to_override) > 0:
        while True:
            print("""
 The following benchmark(s) have already been post-processed:""")
            for test in to_override:
                print(' - '+test)

            print("""
 You can manage the selection of benchmarks to post-pr. in the Config.xlsx file
""")
            i = input(' Would you like to override the results?(y/n) ')

            if i == 'y':
                ans = True
                logtext = '\nThe following Post-Processing results have been overwritten:'
                for test in to_override:
                    logtext = logtext+'\n'+'- '+test+' ['+lib+']'
                session.log.adjourn(logtext)
                break
            elif i == 'n':
                ans = False
                break
            else:
                print('\n please select one between "y" or "n"')

    else:
        ans = True

    return lib, ans


def check_active_tests(session, action):
    """
    Check the configuration file for active benchmarks to perform or
    post-process

    Parameters
    ----------
    session : Session
        JADE session
    action : str
        either 'Post-Processing' or 'Run' (as in Configuration file)

    Returns
    -------
    to_perform : list
        list of active test names

    """
    # Check Which benchmarks are to perform
    config = session.conf.comp_default
    to_perform = []
    for idx, row in config.iterrows():
        filename = str(row['File Name'])
        testname = filename.split('.')[0]

        pp = row[action]
        if pp is True or pp == 'True' or pp == 'true':
            to_perform.append(testname)

    return to_perform
