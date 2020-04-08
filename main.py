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


class Session:
    """
    This object represent a JADE session
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
        # Read configuration file. All vital variables are stored here
        self.conf = cnf.Configuration('Config.xlsx')

        # Create the library manager. This will handle library operations
        dl = self.conf.default_lib
        self.lib_manager = libmanager.LibManager(self.conf.xsdir_path,
                                                 defaultlib=dl)

        # --- Generate and store the JADE path structure ---
        cp = os.getcwd()
        cp = os.path.dirname(cp)
        # Benchmark inputs should be externally copied, that is too heavy
        self.path_inputs = os.path.join(cp, 'Benchmarks inputs')
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

        keypaths = [self.path_inputs, self.path_quality, self.path_test,
                    self.path_run, self.path_pp, self.path_uti,
                    self.path_single, self.path_comparison, self.path_logs]
        for path in keypaths:
            if not os.path.exists(path):
                os.mkdir(path)
            
        # Create the session LOG
        log = os.path.join(self.path_logs, 'Log '+time.ctime().replace(':','-')
                           +'.txt')
        self.log = cnf.Log(log)

        # Initialize status
        self.state = status.Status(self)

    def check_active_tests(self, action):
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
        config = self.conf.comp_default
        to_perform = []
        for idx, row in config.iterrows():
            filename = str(row['File Name'])
            testname = filename.split('.')[0]

            pp = row[action]
            if pp is True or pp == 'True' or pp == 'true':
                to_perform.append(testname)

        return to_perform


if __name__ == "__main__":

    # Module having problem with log(0) for tick position in graphs
    warnings.filterwarnings('ignore',
                            r'invalid value encountered in double_scalars')
    warnings.filterwarnings('ignore',
                            r'overflow encountered in power')
    warnings.filterwarnings('ignore', module=r'plotter')

    session = Session()
    gui.mainloop(session)
