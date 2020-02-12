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


class Session:
    """
    This object represent a JADE session
    """

    def __init__(self):
        # Read configuration file. All vital variables are stored here
        self.conf = cnf.Configuration('Config.xlsx')

        # Create the library manager. This will handle library operations
        dl = self.conf.default_lib
        self.lib_manager = libmanager.LibManager(self.conf.xsdir_path,
                                                 defaultlib=dl)

        # Create the session LOG
        cp = os.getcwd()
        cp = os.path.dirname(cp)
        log = os.path.join(cp, 'Utilities', 'Log.txt')
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
