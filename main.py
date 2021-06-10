# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:57:57 2019

@author: Davide Laghi
"""
import gui
import configuration as cnf
import libmanager
import os
import status
import warnings
import time
import shutil
import sys

# RED color
CRED = '\033[91m'
CEND = '\033[0m'


class Session:
    """
    This object represent a JADE session. All "environment" variables are
    initialized
    """

    def __init__(self):
        """
        Initialize JADE session:
            - folders structure is created if absent
            - Configuration file is read and correspondent object is created
            - Libmanager is created
            - Logfile is created

        Returns
        -------
        None.

        """

        cp = os.getcwd()

        self.path_default_settings = os.path.join(cp, 'Default Settings')

        cp = os.path.dirname(cp)

        # --- INITIALIZATION ---
        # --- Create/memorize JADE folder structure ---
        # Future implementation
        self.path_quality = os.path.join(cp, 'Quality')
        # Test level 1
        self.path_test = os.path.join(cp, 'Tests')
        # Test level 2
        self.path_run = os.path.join(self.path_test, 'MCNP simulations')
        self.path_pp = os.path.join(self.path_test, 'Post-Processing')
        # Test level 3
        self.path_single = os.path.join(self.path_pp, 'Single Libraries')
        self.path_comparison = os.path.join(self.path_pp, 'Comparisons')
        # Utilities
        self.path_uti = os.path.join(cp, 'Utilities')
        self.path_logs = os.path.join(cp, 'Utilities', 'Log Files')
        self.path_test_install = os.path.join(cp, 'Utilities',
                                              'Installation Test')

        keypaths = [self.path_quality, self.path_test,
                    self.path_run, self.path_pp, self.path_uti,
                    self.path_single, self.path_comparison, self.path_logs,
                    self.path_test_install]
        for path in keypaths:
            if not os.path.exists(path):
                os.mkdir(path)

        # Configuration
        self.path_cnf = os.path.join(cp, 'Configuration',
                                     'Benchmarks Configuration')
        # Copy default settings if it is the first initialization
        if not os.path.exists(self.path_cnf):
            print("""
 Welcome to JADE
 During this first run the entire JADE tree has been initialized.
 The application will be now closed. Before restarting the application, please
 configure at least the variables contained in the "MAIN Config." sheet of the
 Configuration/Config.xlsx file.

""")
            files = self.path_default_settings
            shutil.copytree(files, self.path_cnf)
            # the application needs to be closed
            sys.exit()

        # Read global configuration file. All vital variables are stored here
        self.conf = cnf.Configuration(os.path.join(cp, 'Configuration',
                                                   'Config.xlsx'))

        # Copy files into benchmark inputs folder
        path_inputs = os.path.join(cp, 'Benchmarks inputs')
        if not os.path.exists(path_inputs):
            files = os.path.join('Installation Files', 'Benchmarks inputs')
            shutil.copytree(files, path_inputs)
        self.path_inputs = path_inputs

        # Copy input files for testing
        path_inputs = os.path.join(self.path_test_install, 'Inputs')
        if not os.path.exists(path_inputs):
            files = os.path.join('Installation Files', 'Inputs install')
            shutil.copytree(files, path_inputs)

        # Copy experimental results folder
        path_exp_res = os.path.join(cp, 'Experimental Results')
        if not os.path.exists(path_exp_res):
            files = os.path.join('Installation Files', 'Experimental Results')
            shutil.copytree(files, path_exp_res)
        self.path_exp_res = path_exp_res

        # --- Create the session LOG ---
        log = os.path.join(self.path_logs,
                           'Log '+time.ctime().replace(':', '-')+'.txt')
        self.log = cnf.Log(log)

        # --- Create the library manager ---
        dl = self.conf.default_lib
        self.lib_manager = libmanager.LibManager(self.conf.xsdir_path,
                                                 defaultlib=dl)

        # --- Initialize status ---
        self.state = status.Status(self)

    def check_active_tests(self, action, exp=False):
        """
        Check the configuration file for active benchmarks to perform or
        post-process

        Parameters
        ----------
        session : Session
            JADE session
        action : str
            either 'Post-Processing' or 'Run' (as in Configuration file)
        exp : boolean
            if True checks the experimental benchmarks. Default is False

        Returns
        -------
        to_perform : list
            list of active test names

        """
        # Check Which benchmarks are to perform
        if exp:
            config = self.conf.exp_default
        else:
            config = self.conf.comp_default

        to_perform = []
        for idx, row in config.iterrows():
            filename = str(row['File Name'])
            testname = filename.split('.')[0]

            pp = row[action]
            if pp is True or pp == 'True' or pp == 'true':
                to_perform.append(testname)

        return to_perform


def fatal_exception(message=None):
    """
    Use this function to exit with a code error from a handled exception

    Parameters
    ----------
    message : str, optional
        Message to display. The default is None.

    Returns
    -------
    None.

    """
    if message is None:
        message = 'A Fatal exception have occured'

    message = message+', the application will now exit'
    print(CRED+' FATAL EXCEPTION: \n'+message+CEND)
    sys.exit()


if __name__ == "__main__":

    # Module having problem with log(0) for tick position in graphs
    warnings.filterwarnings('ignore',
                            r'invalid value encountered in double_scalars')
    warnings.filterwarnings('ignore',
                            r'overflow encountered in power')
    warnings.filterwarnings('ignore', module=r'plotter')
    warnings.filterwarnings('ignore',
                            message=r'Warning: converting a masked element to nan.')

    session = Session()
    gui.mainloop(session)
