# -*- coding: utf-8 -*-
"""
Created on Wed May  6 10:15:54 2020

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


class OutputFile:

    def __init__(self, filepath):
        """
        Object for MCNP .out file parsing

        Parameters
        ----------
        filepath : str or path
            path to the .out (.o) MCNP file.

        Returns
        -------
        None.

        """
        self.path = filepath  # Path to the file
        self.name = os.path.basename(filepath)  # file name

        # Store statistical checks in a dictionary
        self.stat_checks = self._get_statistical_checks()

    def _get_statistical_checks(self):
        """
        Retrieve the result of the 10 statistical checks for all tallies.
        They are registered as either 'Missed', 'Passed' or 'All zeros'

        Returns
        -------
        stat_checks : dic
            keys are the tally numbers, values the result of the statistical
            checks.

        """
        # Some global key words and patterns
        start_stat_check = 'result of statistical checks'
        miss = 'missed'
        passed = 'passed'
        allzero = 'no nonzero'
        pat_tnumber = re.compile('\s*\t*\s*\d+')
        end = 'the 10 statistical checks are only'

        # Recover statistical checks
        statcheck_flag = False
        stat_checks = {}
        with open(self.path, 'r') as infile:
            for line in infile:
                if line.find(start_stat_check) != -1:
                    statcheck_flag = True

                elif statcheck_flag:
                    # Control if is a tally line
                    tallycheck = pat_tnumber.match(line)
                    if tallycheck is not None:
                        tnumber = int(tallycheck.group())
                        if line.find(miss) != -1:
                            result = 'Missed'
                        elif line.find(passed) != -1:
                            result = 'Passed'
                        elif line.find(allzero) != -1:
                            result = 'All zeros'
                        else:
                            print('Warning: tally n.'+str(tnumber) +
                                  ' not retrieved')

                        stat_checks[tnumber] = result

                    elif line.find(end) != -1:
                        # Exit from loop when all checks are read
                        break

        return stat_checks

    def assign_tally_description(self, tallylist, warning=False):
        """
        Include the tally descriptions in the statistical checks dictionary

        Parameters
        ----------
        tallylist : list
            List of tallies.
        warning : bool
            if True a warning is printed to video when the tally description
            is not found

        Returns
        -------
        new_stat_check : dic
            the adjourned result of the statistical checks results.

        """
        new_stat_check = {}
        for tnumber, result in self.stat_checks.items():
            for tally in tallylist:
                if int(tally.tallyNumber) == int(tnumber):
                    try:
                        tdescr = tally.tallyComment[0]
                    except IndexError:
                        if warning:
                            print(' WARNING: No description t. '+str(tnumber))
                        tdescr = ''
            newkey = tdescr+' ['+str(tnumber)+']'
            new_stat_check[newkey] = result

        self.stat_checks = new_stat_check

        return new_stat_check
