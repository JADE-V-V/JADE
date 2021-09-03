# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 09:23:52 2021

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
import re

PAT_BLANK = re.compile(r'[\s\tCc]*\n')
PAT_SPACE = re.compile(r'[\s\t]+')


class IrradiationFile:
    def __init__(self, nsc, irr_schedules, header=None):
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

        Returns
        -------
        None.

        """
        self.nsc
        self.irr_schedules = irr_schedules
        self.header = header

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
        pat_nsc = re.compile('nsc=')
        pat_num = re.compile(r'\d+')
        with open(filepath, 'r') as infile:
            inheader = True
            header = ''
            irr_schedules = []
            for line in infile:
                # check if we need to exit header mode
                if pat_nsc.match(line) is not None:
                    nsc = int(pat_num.search(line).group())
                    inheader = False
                # If in header keep reading header
                elif inheader:
                    header += line
                # data
                else:
                    # Avoid comments
                    if PAT_BLANK.match(line) is None:
                        irr_schedules.append(Irradiation.from_text(line, nsc))


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


class ReactionFile:
    def __init__(self, reactions):
        self.reactions = reactions

    @classmethod
    def from_text(cls, filepath):
        # read all reactions
        reactions = []
        with open(filepath, 'r') as infile:
            for line in infile:
                # Ignore if it is a blank line
                if PAT_BLANK.match(line) is None:
                    # parse reactions
                    reaction = Reaction.from_text(line)
                    reactions.append(reaction)

        return cls(reactions)

    def change_lib(self, newlib):
        """
        change the parent library tag of the reactions

        Parameters
        ----------
        newlib : str
            (e.g. 31c).

        Returns
        -------
        None.

        """
        for reaction in self.reactions:
            reaction.change_lib(newlib)

    def write(self, outpath):
        """
        write formatted reaction file

        Parameters
        ----------
        outpath : str/path
            path to the output file. Includes file name.

        Returns
        -------
        None.

        """
        with open(outpath, 'w') as outfile:
            for reaction in self.reactions:
                outfile.write(reaction.write()+'\n')


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
        self.MT = MT
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
        text = self.parent+' '+self.MT+' '+self.daughter
        if self.comment is not None and self.comment != '':
            text = text+' '+self.comment
        return text

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
        pieces = PAT_SPACE.split(text)
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
