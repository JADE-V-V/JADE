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
import os


class ReactionFile():
    def __init__(self, reactions, name):
        self.name = name
        self.reactions = reactions

    @classmethod
    def from_text(cls, filepath, name=None):
        # If name is not specified use the one from the original
        if name is None:
            name = os.path.basename(filepath)

        # read all reactions
        reactions = []
        pat_blank = re.compile('[\s\t]*\n')
        with open(filepath, 'r') as infile:
            for line in infile:
                # Ignore if it is a blank line
                if pat_blank.match(line) is None:
                    # parse reactions
                    reaction = Reaction.from_text(line)
                    reactions.append(reaction)

        return cls(reactions, name)


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

        # compute text
        text = self.parent+' '+self.MT+' '+self.daughter
        if self.comment is not None and self.comment != '':
            text = text + self.comment
        self.text = text

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
        pat_space = re.compile('[\s\t]+')
        # Split the reaction in its components
        pieces = pat_space.split(text)
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
