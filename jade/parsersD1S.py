# -*- coding: utf-8 -*-
# Created on Fri Sep  3 09:23:52 2021

# @author: Davide Laghi

# Copyright 2021, the JADE Development Team. All rights reserved.

# This file is part of JADE.

# JADE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# JADE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with JADE.  If not, see <http://www.gnu.org/licenses/>.

import re
import os

PAT_BLANK = re.compile(r'[\s\tCc]*\n')
PAT_COMMENT = re.compile('[Cc]+')
PAT_SPACE = re.compile(r'[\s\t]+')
REACFORMAT = '{:>13s}{:>7s}{:>9s}{:>40s}'

# colors
CRED = '\033[91m'
CORANGE = '\033[93m'
CEND = '\033[0m'


class IrradiationFile:

    def __init__(self, nsc, irr_schedules, header=None,
                 formatting=[8, 14, 13, 9], name='irrad'):
        """
        Object representing an irradiation D1S file

        Parameters
        ----------
        nsc : int
            number of irradiation schedule.
        irr_schedules : list of Irradiation object
            contains all irradiation objects.
        header : str, optional
            Header of the file. The default is None.
        formatting : list of int, optional
            fwf values for the output columns. The default is [8, 14, 13, 9].
        name : str, optional
            name of the file. The default is 'irrad'.

        Returns
        -------
        None.

        """
        self.nsc = nsc
        self.irr_schedules = irr_schedules
        self.header = header
        self.formatting = formatting

        # Compute irradiation header
        w1 = str(formatting[0])
        w2 = str(formatting[1])
        w3 = str(formatting[2])
        w4 = str(formatting[3])

        head = '{:>'+w1+'s}{:>'+w2+'s}{:>'
        for i in range(nsc):
            head += w3+'s}{:>'

        head += w4+'s}'

        self.irrformat = head
        self.name = name

    def get_daughters(self):
        """
        Get a list of all daughters among all irradiation files

        Returns
        -------
        list
            list of daughters.

        """
        # Get the list of daughters
        daughters = []
        for irradiation in self.irr_schedules:
            daughters.append(irradiation.daughter)

        return daughters

    def get_irrad(self, daughter):
        """
        Return the irradiation correspondent to the daughter

        Parameters
        ----------
        daughter : TYPE
            DESCRIPTION.

        Returns
        -------
        Irradiation
            Returns the irradiation corresponding to the daughter.
            If no irradiation is found returns None.

        """
        for irradiation in self.irr_schedules:
            if daughter == irradiation.daughter:
                return irradiation

        return None

    @classmethod
    def from_text(cls, filepath):
        """
        Parse irradiation file

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        filepath : str/path
            path to the irradiation file.

        Returns
        -------
        None.

        """
        pat_nsc = re.compile('(?i)(nsc)')
        pat_num = re.compile(r'\d+')
        # name = os.path.basename(filepath)
        with open(filepath, 'r') as infile:
            inheader = True
            header = ''
            irr_schedules = []
            for line in infile:
                # check if we need to exit header mode
                # it my also happen that there is no header
                if pat_nsc.match(line) is not None:
                    nsc = int(pat_num.search(line).group())
                    inheader = False
                # If in header keep reading header
                elif inheader:
                    header += line
                # data
                else:
                    # Avoid comments and blank lines
                    if (PAT_BLANK.match(line) is None and
                            PAT_COMMENT.match(line) is None):

                        irr_schedules.append(Irradiation.from_text(line, nsc))

        return cls(nsc, irr_schedules, header=header)

    def write(self, path):
        """
        Write the D1S irradiation file

        Parameters
        ----------
        path : str or path
            output path where to save the file (only directory).

        Returns
        -------
        None.

        """
        filepath = os.path.join(path, self.name)
        with open(filepath, 'w') as outfile:
            if self.header is not None:
                outfile.write(self.header)
            # write nsc
            outfile.write('nsc '+str(self.nsc)+'\n')

            # --- Write irradiation schedules ---
            # write header
            args = ['Daught.', 'lambda(1/s)']
            for i in range(self.nsc):
                args.append('time_fact_'+str(i+1))
            args.append('comments')
            outfile.write('C '+self.irrformat.format(*args)+'\n')

            # write schedules
            for schedule in self.irr_schedules:
                args = schedule._get_format_args()
                outfile.write(self.irrformat.format(*args)+'\n')


class Irradiation:
    def __init__(self, daughter, lambd, times, comment=None):
        """
        Irradiation object

        Parameters
        ----------
        daughter : str
            daughter nuclide (e.g. 24051).
        lambd : str
            disintegration constant [1/s].
        times : list of strings
            time correction factors.
        comment : str, optional
            comment to the irradiation. The default is None.

        Returns
        -------
        None.

        """
        self.daughter = daughter
        self.lambd = lambd
        self.times = times
        self.comment = comment

    def __eq__(self, other):
        """
        Get a more appropriate equivalence function. Two irradiation are equal
        if they have the same daughter, lambda and correction factors

        """
        if isinstance(other, Irradiation):
            daugther_eq = self.daughter == other.daughter
            lamb_eq = float(self.lambd) == float(other.lambd)
            if len(self.times) == len(other.times):
                times_eq = True
                for time1, time2 in zip(self.times, other.times):
                    if float(time1) != float(time2):
                        times_eq = False
            else:
                times_eq = False

            condition = (daugther_eq and lamb_eq and times_eq)

            return condition
        else:
            return False

    @classmethod
    def from_text(cls, text, nsc):
        """
        Parse a single irradiation

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        text : str
            text to be parsed.
        nsc : int
            number of irradiation schedule.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        pieces = PAT_SPACE.split(text)
        # Check for empty start
        if pieces[0] == '':
            pieces.pop(0)

        daughter = pieces[0]
        lambd = pieces[1]
        times = []
        # Get all decay times
        j = 2
        for i in range(nsc):
            times.append(pieces[j])
            j += 1
        # Get comment
        comment = ''
        try:
            for piece in pieces[j:]:
                comment += ' '+piece
        except IndexError:
            comment = None

        if comment == '':
            comment = None
        else:
            comment = comment.strip()

        return cls(daughter, lambd, times, comment=comment)

    def _get_format_args(self):
        args = [self.daughter, self.lambd]
        for time in self.times:
            args.append(time)
        args.append(self.comment)
        return args


class ReactionFile:
    def __init__(self, reactions, name='react'):
        """
        Reaction file object

        Parameters
        ----------
        reactions : list
            contains all reaction objects contained in the file.
        name : name, optional
            file name. The default is 'react'.

        Returns
        -------
        None.

        """
        self.reactions = reactions
        self.name = name

    @classmethod
    def from_text(cls, filepath):
        """
        Generate a reaction file directly from text file

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        filepath : str or path
            file to read.

        Returns
        -------
        ReactionFile
            Reaction File Object.

        """
        # read all reactions
        reactions = []
        with open(filepath, 'r') as infile:
            for line in infile:
                # Ignore if it is a blank line or a full line comment
                if (PAT_BLANK.match(line) is None and
                        PAT_COMMENT.match(line) is None):
                    # parse reactions
                    reaction = Reaction.from_text(line)
                    reactions.append(reaction)

        return cls(reactions)  # , name=os.path.basename(filepath))

    def get_parents(self):
        """
        Get a list of all parents

        Returns
        -------
        None.

        """
        parents = []
        for reaction in self.reactions:
            parent = reaction.parent.split('.')[0]
            if parent not in parents:
                parents.append(parent)
        return parents

    def change_lib(self, newlib, libmanager=None):
        """
        change the parent library tag of the reactions. If no libmanager is
        provided, the check on the availability of the parent in the xsdir
        file will be not performed.

        Parameters
        ----------
        newlib : str
            (e.g. 31c).
        libmanager : LibManager, optional
            Object managing library operations. The default is None.

        Returns
        -------
        None.

        """
        # Correctly parse the lib input. It may be a dic than only the
        # first dic value needs to be cosidered
        pat_libs = re.compile(r'"\d\d[a-zA-Z]"')
        if newlib[0] == '{':
            libs = pat_libs.findall(newlib)
            lib = libs[1][1:-1]
        else:
            lib = newlib

        # actual translation
        for reaction in self.reactions:
            # Insert here a check that the parent isotope is available
            if libmanager is None:
                reaction.change_lib(lib)
            else:
                # get the available libraries for the parent
                zaid = reaction.parent.split('.')[0]
                libs = libmanager.check4zaid(zaid)
                if newlib in libs:
                    reaction.change_lib(lib)
                else:
                    print(CORANGE+"""
 Warning: {} is not available in xsdir, it will be not translated
 """.format(zaid)+CEND)

    def write(self, path):
        """
        write formatted reaction file

        Parameters
        ----------
        path : str/path
            path to the output file (only dir).

        Returns
        -------
        None.

        """
        filepath = os.path.join(path, self.name)
        with open(filepath, 'w') as outfile:
            for reaction in self.reactions:
                outfile.write(REACFORMAT.format(*reaction.write())+'\n')


class Reaction:
    def __init__(self, parent, MT, daughter, comment=None):
        """
        Represents a single reaction of the reaction file

        Parameters
        ----------
        parent : str
            parent nuclide ZZAAA.XXc representing stable isotope to be
            activated. ZZ and AAA represent the atomic and mass number and
            extension XX, is the extension number of the modified D1S library.
        MT : str
            integer, reaction type (ENDF definition).
        daughter : str
            integer, tag of the daughter nuclide. The value could be
            defined as ZZAAA of daughter nuclide, but any other identification
            type (with integer value) can be used.
        comment : str, optional
            comment to the reaction. The default is None.

        Returns
        -------
        None.

        """
        self.parent = parent
        self.MT = str(int(MT))
        self.daughter = daughter
        self.comment = comment

    def change_lib(self, newlib):
        """
        Change the library tag

        Parameters
        ----------
        newlib : str
            (e.g. 52c).

        Returns
        -------
        None.

        """
        pieces = self.parent.split('.')
        # Override lib
        self.parent = pieces[0]+'.'+newlib

    def write(self):
        """
        Generate the reaction text

        Returns
        -------
        text : str
            reaction text for D1S input.

        """
        # compute text
        textpieces = [self.parent, self.MT, self.daughter]
        if self.comment is None:
            comment = ''
        else:
            comment = self.comment
        textpieces.append(comment)

        return textpieces

    @classmethod
    def from_text(cls, text):
        """
        Create a reaction object from text

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        text : str
            formatted text describing the reaction.

        Returns
        -------
        Reaction
            Reaction object.

        """
        # Split the reaction in its components
        pieces = PAT_SPACE.split(text.strip())
        parent = pieces[0].strip()
        MT = pieces[1]
        daughter = pieces[2]
        # the rest is comments
        comment = ''
        if len(pieces) > 3:
            for piece in pieces[3:]:
                comment = comment+' '+piece

        comment = comment.strip()

        return cls(parent, MT, daughter, comment=comment)
