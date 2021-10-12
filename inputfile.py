# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 17:21:24 2019

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
import json
import matreader as mat
from numjuggler import parser as par
import os
import sys
from contextlib import contextmanager
import warnings
from parsersD1S import (ReactionFile, Reaction)


class InputFile:

    def __init__(self, cards, matlist, name=None):

        # All cards from parser epurated by the materials
        self.cards = cards

        # Materials list (see matreader.py)
        self.matlist = matlist

        # Set a name
        self.name = name

    @classmethod
    def from_text(cls, inputfile):
        """
        This method use the numjuggler parser to help identify the mcards in
        the input which will usually undergo special treatments in the input
        creation

        inputfile: (str) path to the MCNP input file
        """
        matPat = re.compile(r'[mM]\d+')
        mxPat = re.compile(r'mx\d+', re.IGNORECASE)
        commentPat = re.compile('[cC]')
        # Using parser the data cards are extracted from the input.
        # Comment sections are interpreted as cards by the parser
        with suppress_stdout():
            # Suppress output from tab replacing
            cards = par.get_cards_from_input(inputfile)
            cardsDic = par.get_blocks(cards)
        datacards = cardsDic[5]

        cards = {'cells': cardsDic[3],  # Parser cards
                 'surf': cardsDic[4],  # Parser cards
                 'settings': []}  # Parser cards

        # Check for a title
        try:
            cards['title'] = cardsDic[2][0]
        except KeyError:
            cards['title'] = None

#        materials = [] # Custom material objects!

        previous_lines = ['']
        for datacard in datacards:
            lines = datacard.lines
            # Check if it is a material card or mx card to ignore
            if matPat.match(lines[0]) is not None \
                    or mxPat.match(lines[0]) is not None:
                # Ignore
                # Check if previous card is the header
                if commentPat.match(previous_lines[0]):
                    # cancel the comment from settings
                    del cards['settings'][-1]

            # Not a material
            else:
                cards['settings'].append(datacard)

            previous_lines = lines

        matlist = mat.MatCardsList.from_input(inputfile)

        return cls(cards, matlist,
                   name=os.path.basename(inputfile).split('.')[0])

    def write(self, out):
        """
        Write the input to a file

        out: (str) path to the output file
        """
        if self.cards['title'] is not None:
            lines = self.cards['title'].lines
        else:
            lines = []

        # Add cells
        for card in self.cards['cells']:
            lines.extend(card.lines)

        lines.append('\n')  # Section breaker

        # Add surfaces
        for card in self.cards['surf']:
            lines.extend(card.lines)

        lines.append('\n')  # Section breaker

        # Add materials
        lines.append(self.matlist.to_text())
        lines.append('\n')  # Missing

        # Add remaining data cards
        for card in self.cards['settings']:
            lines.extend(card.lines)

        toprint = ''
        for line in lines:
            toprint = toprint+line

        with open(out, 'w') as outfile:
            outfile.write(toprint)

    def translate(self, newlib, libmanager):
        """
        Translate the input to another library

        newlib: (str) suffix of the new lib to translate to
        lib_manager: (LibManager) Library manager for the conversion
        """
        try:
            if newlib[0] == '{':
                # covert the dic
                newlib = json.loads(newlib)
        except KeyError:
            # It is already a dict, pass
            pass

        self.matlist.translate(newlib, libmanager)

    def update_zaidinfo(self, lib_manager):
        """
        This methods allows to update the in-line comments for every zaids
        containing additional information

        lib_manager: (LibManager) Library manager for the conversion
        """

        self.matlist.update_info(lib_manager)

    def add_stopCard(self, nps, ctme, precision):
        """
        Add Stop card

        nps = (int) number of particles to simulate
        ctme = (int) copmuter time
        precision = (tally (str), error (float)) [tuple]
        """

        line = 'STOP '
        if nps is not None:
            try:
                line = line+'NPS '+str(int(nps))+' '
            except ValueError:
                pass  # an escaped NaN
        if ctme is not None:
            try:
                line = line+'CTME '+str(int(ctme))+' '
            except ValueError:
                pass  # an escaped NaN

        if precision is not None:
            tally = precision[0]
            error = precision[1]
            line = line+str(tally)+' '+str(error)

        line = line+'\n'

        card = par.Card([line], 5, -1)
        self.cards['settings'].append(card)

    def change_density(self, density, cellidx=1):
        """
        Change the density of the sphere according to the selected zaid

        density: (str/float) density to apply
        cellidx: (int) cell index where to modify the density
        """

        # Change density in sphere cell
        card = self.cards['cells'][cellidx]
        card.get_values()
        card.set_d(str(density))
        card.lines = card.card()

    def add_edits(self, edits_file):
        """
        Add weight windows and source bias resulted from ADVANTG analysis

        zaid : (str) zaid name (e.g. 1001)
        """
        # Parse edits file
        patBias = re.compile('sb', re.IGNORECASE)
        patWWP = re.compile('wwp', re.IGNORECASE)
        patSP = re.compile('sp', re.IGNORECASE)

        bias = []
        wwp = []
        with open(edits_file, 'r') as infile:
            for line in infile:
                if patBias.match(line) is not None:
                    bias.append(par.Card([line], 5, -1))
                elif patWWP.match(line) is not None:
                    wwp.append(par.Card([line], 5, -1))

        newsettings = []
        for card in self.cards['settings']:
            # TODO !!!!! this works only if there is only one source card !!!!
            if patSP.match(card.lines[0]) is not None:
                newsettings.append(card)
                newsettings.extend(bias)
            else:
                newsettings.append(card)

        newsettings.extend(wwp)

        self.cards['settings'] = newsettings


class D1S_Input(InputFile):

    def translate(self, newlib, libmanager, original_irradfile=None,
                  original_reacfile=None):
        # Generally, an activation lib and transport lib are expected
        try:
            activationlib, transportlib = check_transport_activation(newlib)
        except AttributeError:
            # Then the passed library was already a dict
            # Default translation can be operated
            super().translate(newlib, libmanager)
            return None

        active_zaids = []
        transp_zaids = []

        # Give a first translation with the transport lib. This will
        # correctly expand all natural zaid before the actual translation
        # that also uses the activation lib
        self.matlist.translate(transportlib, libmanager)

        # Get the general reaction file
        reacfile = self.get_reaction_file(libmanager, activationlib)

        # --- Check which daughters are available in the irr file ---
        # --- Modify irr file, react file and lib accordingly ---
        newreactions = []
        newirradiations = []
        available_daughters = original_irradfile.get_daughters()
        for reaction in reacfile.reactions:
            # strip the lib from the parent
            parent = reaction.parent.split('.')[0]
            if reaction.daughter in available_daughters:
                # add the parent to the activation lib
                active_zaids.append(parent)
                # add the reaction to the one to use
                reaction.change_lib(activationlib)
                newreactions.append(reaction)
                # add the correspondent irradiation
                irr = original_irradfile.get_irrad(reaction.daughter)
                if irr not in newirradiations:
                    newirradiations.append(irr)
            else:
                # Add the zaid to the transport lib
                transp_zaids.append(parent)

        # Now check for the remaing materials in the input to be assigned
        # to transport
        for material in self.matlist:
            for submaterial in material.submaterials:
                for zaid in submaterial.zaidList:
                    zaidnum = zaid.element+zaid.isotope
                    if (zaidnum not in active_zaids and
                            zaidnum not in transp_zaids):
                        transp_zaids.append(zaidnum)

        newlib = {activationlib: active_zaids, transportlib: transp_zaids}
        # Add the PIKMT card
        self.add_PIKMT_card(active_zaids)
        # Translate the input with the new lib
        self.matlist.translate(newlib, libmanager)

        # Parameters to modify the test attributes
        return newirradiations, newreactions

    def add_PIKMT_card(self, parent_list):
        """
        Add a PIKMT card to the input file

        Parameters
        ----------
        parent_list : list
            list of parent zaids.

        Returns
        -------
        None.

        """
        lines = ['PIKMT\n']
        for parent in parent_list:
            lines.append('         {}    {}\n'.format(parent, 0))

        card = par.Card(lines, 5, -1)
        self.cards['settings'].append(card)

    def get_reaction_file(self, libmanager, lib):
        """
        Collect all the possible reactions that are allowed amnong all the
        materials in the input

        Parameters
        ----------
        libmanager : LibManager
            Object handling all cross-sections related operations.
        lib : str
            library suffix to be used.

        Returns
        -------
        ReactionFile
            Object representing the react file for D1S.

        """
        # parentlist = []
        # daughterlist = []
        # REcover all possible reactions
        reactions = []
        for material in self.matlist:
            for submat in material.submaterials:
                for zaid in submat.zaidList:
                    parent = zaid.element+zaid.isotope
                    zaidreactions = libmanager.get_reactions(lib, parent)
                    # if len(zaidreactions) > 0:
                    #     # it is a parent only if reactions are available
                    #     parentlist.append(parent)
                    for MT, daughter in zaidreactions:
                        reactions.append((parent, MT, daughter))
                        # daughterlist.append(daughter)

        reactions = list(set(reactions))
        reactions.sort()
        # --- Build the reactions and reaction file ---
        reaction_list = []
        for parent, MT, daughter in reactions:
            parent = parent+'.'+lib
            # Build a comment
            _, parent_formula = libmanager.get_zaidname(parent)
            _, daughter_formula = libmanager.get_zaidname(daughter)
            comment = '{} -> {}'.format(parent_formula, daughter_formula)

            rx = Reaction(parent, MT, daughter, comment=comment)
            reaction_list.append(rx)

        return ReactionFile(reaction_list)


class D1S5_InputFile(D1S_Input):

    def add_stopCard(self, nps, ctme, precision):
        """
        STOP card is not supported in MCNP 5. This simply is translated to a
        nps card. Warnings are prompt to the user if ctme or precision are
        specified.

        Parameters
        ----------
        nps : int
            number of particles to simulate
        ctme = int
            computer time
        precision = (str, float)
            tuple indicating the tally number and the precision requested

        Returns
        -------
        None.

        """
        if ctme is not None or precision is not None:
            if self.name != 'SphereSDDR':
                warnings.warn('''
STOP card is substituted with normal NPS card for MCNP5.
specified ctme or precision parameters will be ignored
''')
        elif nps is None:
            raise ValueError(' NPS value is mandatory for MCNP 5 inputs')

        line = 'NPS '+str(nps)+'\n'
        card = par.Card([line], 5, -1)
        self.cards['settings'].append(card)


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def check_transport_activation(lib):
    # Operate on the newlib, should arrive in the 99c-31c format
    errmsg = """
 Please define the pair activation-transport lib for the FNG benchmark
 (e.g. 99c-31c). See additional details on the documentation.
            """
    try:
        activationlib = lib.split('-')[0]
        transportlib = lib.split('-')[1]
    except IndexError:
        raise ValueError(errmsg)
    # Check that libraries have been correctly defined
    if activationlib+'-'+transportlib != lib:
        raise ValueError(errmsg)

    return activationlib, transportlib