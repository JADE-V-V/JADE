# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:52:32 2019

@author: Davide Laghi
"""
import pandas as pd
import datetime


class Configuration:
    """
    This object deals with all the configuration variables
    """

    def __init__(self, conf_file):
        """
        Read the configuration excel file and set the configuration

        con_file: (str) path to configuration file
        """
        # ############ load conf file sheets ############

        # Main
        main = pd.read_excel(conf_file, sheet_name='MAIN Config.', skiprows=1,
                             header=None)
        main.columns = ['Variable', 'Value']
        main.set_index('Variable', inplace=True)
        self.xsdir_path = main['Value'].loc['xsdir Path']
        self.suppressW = main['Value'].loc['Suppress warnings']
        self.multi_threads = main['Value'].loc['multithread']
        self.cpu = main['Value'].loc['CPU']
        self.uti_dir = main['Value'].loc['Utilities output path']

        # Computational
        self.comp_default = pd.read_excel(conf_file,
                                          sheet_name='Computational benchmarks',
                                          skiprows=2, nrows=8)

        # Libraries
        lib = pd.read_excel(conf_file, sheet_name='Libraries')
        self.lib = lib

        self.default_lib = lib[lib['Default'] == 'yes']['Suffix'].values[0]


jade = '''
       8888888       oo       888oo       o8888o
           88      o8 8o      88  8oo    88     8
           88     o8   8o     88    8o   88     8
           88    o8=====8o    88    8o   88====°
       88  88   o8       8o   88  8oo    8o
       °°8888  o8         8o  888oo       oo88888
'''

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

        self.text = jade+initialtext

    def adjourn(self, text, spacing=True, time=False):
        """
        Adjourn the log file
        """
        if spacing:
            text = '\n\n'+text.strip('\n')
        self.text = self.text+text

        if time:
            self.text = self.text+'    '+str(datetime.datetime.now())

        with open(self.file, 'w') as outfile:
            outfile.write(self.text)

    def bar_adjourn(self, text, spacing=True):
        """
        Adjourn the log file with hashtag style
        """
        if len(text) > 75:  # There is no space, the bar request is ignored
            self.text = self.text+text
        else:
            hashlen = (len(bar)-len(text))/2
            if hashlen % 1 != 0:
                after = int(hashlen-1)
            else:
                after = int(hashlen)
            before = int(hashlen)

            bartext = bar[:before-1]+' '+text+' '+bar[-after+1:]

            if spacing:
                bartext = '\n\n'+bartext

            self.text = self.text+bartext

        with open(self.file, 'w') as outfile:
            outfile.write(self.text)
