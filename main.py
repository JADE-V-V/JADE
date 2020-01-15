# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:57:57 2019

@author: Davide Laghi
"""
import gui
import configuration as cnf
import libmanager
import os


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


if __name__ == "__main__":
    session = Session()
    gui.mainloop(session)
