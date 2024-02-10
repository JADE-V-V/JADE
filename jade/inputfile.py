# -*- coding: utf-8 -*-

# Created on Mon Nov  4 17:21:24 2019

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

import json
import os
import re
import sys
import textwrap
import warnings
from contextlib import contextmanager

import jade.matreader as mat
from jade.parsersD1S import Reaction, ReactionFile

from numjuggler import parser as par


class InputFile:

    def __init__(self, cards, matlist, name=None):
        """
        Object representing an MCNP input file

        Parameters
        ----------
        cards : dic
            contains the cells, surfaces, settings and title cards.
        matlist : matreader.MatCardList
            material list in the input.
        name : str, optional
            name associated with the file. The default is None.

        Returns
        -------
        None.

        """

        # All cards from parser separated by the materials
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

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        inputfile : path like object
            path to the MCNP input file.

        Returns
        -------
        None.

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

        Parameters
        ----------
        out : str
            path to the output file.

        Returns
        -------
        None.

        """
        to_print = self._to_text()

        with open(out, 'w') as outfile:
            outfile.write(to_print)

    def _to_text(self):
        """
        Get the input in MCNP formatted text

        Returns
        -------
        str
            MCNP formatted text for the input
        """
        lines = []

        if self.cards['title'] is not None:
            lines.extend(self.cards['title'].lines)

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

        return toprint

    def translate(self, newlib, libmanager, code='mcnp'):
        """
        Translate the input to another library

        Parameters
        ----------
        newlib : str
            suffix of the new lib to translate to.
        libmanager : libmanager.LibManager
            Library manager for the conversion.

        Returns
        -------
        None.

        """
        try:
            if newlib[0] == '{':
                # covert the dic
                newlib = json.loads(newlib)
        except KeyError:
            # It is already a dict, pass
            pass

        self.matlist.translate(newlib, libmanager, code)

    def update_zaidinfo(self, lib_manager):
        """
        This methods allows to update the in-line comments for every zaids
        containing additional information

        Parameters
        ----------
        lib_manager : libmanager.LibManager
            Library manager for the conversion.

        Returns
        -------
        None.

        """

        self.matlist.update_info(lib_manager)

    def add_stopCard(self, nps):
        """
        Add STOP card

        Parameters
        ----------
        nps : int
            number of particles to simulate.

        Returns
        -------
        None.

        """

        line = 'STOP '
        if nps is not None:
            try:
                line = line+'NPS '+str(int(nps))+' '
            except ValueError:
                pass  # an escaped NaN
        if line == 'STOP ':
            raise ValueError("""
Specify an nps for the simulation""")

        line = line+'\n'

        card = par.Card([line], 5, -1)
        self.cards['settings'].append(card)

    def change_density(self, density, cellidx=1):
        """
        Change the density of the sphere according to the selected zaid

        Parameters
        ----------
        density : str/float
            density to apply.
        cellidx : int, optional
            cell index where to modify the density. The default is 1.

        Returns
        -------
        None.

        """

        # Change density in sphere cell
        try:
            card = self.cards['cells'][cellidx]
        except IndexError:
            raise ValueError('cell n. {} is not available')
        card.get_values()
        card.set_d(str(density))
        card.lines = card.card()

    # def add_edits(self, edits_file):
    #     """
    #     Add weight windows and source bias resulted from ADVANTG analysis

    #     Parameters
    #     ----------
    #     edits_file : path like object
    #         file containing the edits.

    #     Returns
    #     -------
    #     None.

    #     """
    #     # Parse edits file
    #     patBias = re.compile('sb', re.IGNORECASE)
    #     patWWP = re.compile('wwp', re.IGNORECASE)
    #     patSP = re.compile('sp', re.IGNORECASE)

    #     bias = []
    #     wwp = []
    #     with open(edits_file, 'r') as infile:
    #         for line in infile:
    #             if patBias.match(line) is not None:
    #                 bias.append(par.Card([line], 5, -1))
    #             elif patWWP.match(line) is not None:
    #                 wwp.append(par.Card([line], 5, -1))

    #     newsettings = []
    #     for card in self.cards['settings']:
    #         # TODO !!!!! this works only if there is only one source card !!!!
    #         if patSP.match(card.lines[0]) is not None:
    #             newsettings.append(card)
    #             newsettings.extend(bias)
    #         else:
    #             newsettings.append(card)

    #     newsettings.extend(wwp)

    #     self.cards['settings'] = newsettings

    def get_card_byID(self, blockID, cardID):
        """
        Get a card of the input based on its ID

        Parameters
        ----------
        blockID : str
            either 'cell', 'surf', 'settings' or 'title'.
        cardID : str or int
            card ID (e.g. FC22).

        Raises
        ------
        ValueError
            if blockID is not allowed.

        Returns
        -------
        card : numjuggler.parser.Card
            Selected card. If the card is not found, None is returned

        """
        # pattern of card IDs
        patCardID = re.compile(r'{}\s+'.format(str(cardID)), re.IGNORECASE)
        # Try to get the correct block of cards
        try:
            block = self.cards[blockID]
        except KeyError:
            raise ValueError(blockID+' is not a valid block')

        # Try to find the card
        for card in block:
            for line in card.lines:
                check = patCardID.match(line)
                if check is not None:
                    return card

        # If card is not found just return None
        return None

    def addlines2card(self, lines, blockID, cardID, offset_all=True):
        """
        Append some lines to one of the cards in the input

        Parameters
        ----------
        lines : list or str
            list of lines to be appended to the card. If a string is given,
            this is wrapped
        blockID : str
            either 'cell', 'surf', 'settings' or 'title'.
        cardID : str or int
            card ID (e.g. FC22).
        offset_all : bool, optional
            if True all the lines are off-setted with whitespace. If False
            the first line will have no offset (new card)

        Returns
        -------
        bool
        if lines have been successfully added return True, otherwise False.

        """
        card = self.get_card_byID(blockID, cardID)
        if card is not None:
            # If it is not already a list of str wrap it
            if type(lines) != list:
                lines = self.mcnp_wrap(lines, offset_all=offset_all)

            card.lines.extend(lines)
            return True
        return False

    @staticmethod
    def mcnp_wrap(text, maxchars=80, whitespace='      ', offset_all=True):
        """
        Wrap the text of a card in MCNP style

        Parameters
        ----------
        text : str
            text of the card to be formatted.
        maxchars : int, optional
            max limit of chars in one line. The default is 80.
        whitespace : str, optional
            whitespace to be put in front of newlines. The default is '      '.
        offset_all : bool, optional
            if True all the lines are off-setted with whitespace. If False
            the first line will have no offset (new card)

        Returns
        -------
        list
            list of correctly wrapped line of a card expressing the initial
            text.

        """
        text = text.strip('\n')
        if len(text) <= maxchars:
            if offset_all:
                text = whitespace+text+'\n'
            else:
                text = text+'\n'
            return [text]
        else:
            # init the list with the first line
            wrapped = textwrap.wrap(text, maxchars-len(whitespace))
            # first line does not need whitespace
            if offset_all:
                fl = whitespace+wrapped[0]+'\n'
            else:
                fl = wrapped[0]+'\n'
            lines = [fl]
            # add the white space for each line and a newline char
            for line in wrapped[1:]:
                lines.append(whitespace+line+'\n')

        return lines


class D1S_Input(InputFile):

    def translate(self, newlib, libmanager, original_irradfile=None,
                  original_reacfile=None):
        """
        Translate the input to another library. This methods ovverride the
        parent one since often two different libraries must be considered in
        a D1S input: a tranport and an activation library

        Parameters
        ----------
        newlib : str
            suffix of the new lib to translate to.
        libmanager : LibManager
            Library manager for the conversion.
        original_irradfile : d1s_parser.IrradiationFile, optional
            original irradiation file. The default is None.
        original_reacfile : d1s_parser.ReactionFile, optional
            original reaction file. The default is None.

        Returns
        -------
        newirradiations : list
            list of Irradiation objects coming from the translation.
        newreactions : list
            list of Reactions objects coming from the translation.

        """
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

    def add_track_contribution(self, tallyID, zaids, who='parent'):
        """
        Given a list of zaid add the FU bin in the requested tallies in order
        to collect the contribution of them to the tally.

        Parameters
        ----------
        tallyID : str
            ID of the tally onto which to operate (e.g. F4:p).
        zaids : str
            zaid number of the parent/daughter (e.g. 1001).
        who : str, optional
            either 'parent' or 'daughter' specifies the types of zaids to
            be tracked. The default is 'parent'.

        Raises
        ------
        ValueError
            check for admissible who parameter.

        Returns
        -------
        bool
            return True if lines were added correctly

        """
        patnum = re.compile(r'\d+')
        try:
            num = patnum.search(tallyID).group()
        except AttributeError:
            # The pattern was not found
            raise ValueError(tallyID+' is not a valid tally ID')

        text = 'FU'+num+' 0'
        if who == 'parent':
            for zaid in zaids:
                text = text+' -'+zaid
        elif who == 'daughter':
            for zaid in zaids:
                text = text+' '+zaid
        else:
            raise ValueError(who+' is not an admissible "who" parameters')

        res = self.addlines2card(text, 'settings', tallyID, offset_all=False)
        return res


class D1S5_InputFile(D1S_Input):

    def add_stopCard(self, nps):
        """
        STOP card is not supported in MCNP 5. This simply is translated to a
        nps card. 

        Parameters
        ----------
        nps : int
            number of particles to simulate

        Returns
        -------
        None.

        """
        if nps is None:
            raise ValueError(' NPS value is mandatory for MCNP 5 inputs')

        line = 'NPS '+str(int(nps))+'\n'
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
 Please define the pair activation-transport lib for SDDR benchmarks
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

class SerpentInputFile:
    def __init__(self, lines, matlist, name=None):
        """
        Object representing a Serpent input file

        Parameters
        ----------
        cards : dic
            contains the cells, surfaces, settings and title cards.
        matlist : matreader.MatCardList
            material list in the input.
        name : str, optional
            name associated with the file. The default is None.

        Returns
        -------
        None.

        """

        # All cards from parser separated by the materials
        self.lines = lines
        
        # Materials list (see matreader.py)
        self.matlist = matlist

        # Set a name
        self.name = name

    @classmethod
    def from_text(cls, inputfile):
        """
        Reads input file into list. Removes trailing empty lines. 

        Parameters
        ----------
        cls : 'SerpentInputFile'
            The class itself. 
        inputfile : path like object
            path to the Serpent input file.

        Returns
        -------
        SerpentInputFile instance with data from the input file. 

        """
        with open(inputfile, 'r') as f:
            lines = f.readlines()

        # Remove trailing empty lines
        idx = len(lines) - 1
        while True:
            if lines[idx].strip() == '':
                del lines[idx]
                idx -= 1
            else:
                break

        matlist = None

        return cls(lines, matlist,
                   name=os.path.basename(inputfile).split('.')[0])

    def add_stopCard(self, nps: int) -> None:
        """Add number of particles card

        Parameters
        ----------
        nps : int
            number of particles to simulate
        """
        self.lines.append('\nset nps '+str(int(nps))+'\n')

    def _to_text(self) -> str:
        """
        Get the input in Serpent formatted text

        Returns
        -------
        str
            Serpent formatted text for the input
        """

        # Add materials
        self.lines.append(self.matlist.to_text())
        self.lines.append('\n')  # Missing

        toprint = ''
        for line in self.lines:
            toprint = toprint+line

        return toprint

    
    def write(self, out) -> None:
        """
        Write the input to a file

        Parameters
        ----------
        out : str
            path to the output file.

        Returns
        -------
        None.

        """
        to_print = self._to_text()

        with open(out, 'w') as outfile:
            outfile.write(to_print)

class OpenMCInputFiles:
    def __init__(self, geometry, settings, tallies, materials, matlist, name=None):
        """Object representing an OpenMC input file.

        Parameters
        ----------
        geometry : List[str], optional 
            OpenMC geometry
        settings : List[str], optional 
            OpenMC settings
        tallies : List[str], optional 
            OpenMC tallies
        materials : List[str], optional 
            OpenMC materials
        matlist : List[str], optional 
            material list in the input
        name : str, optional
            name associated with the file, by default None
        """
        
        # Geometry, settings and tallies for OpenMC
        self.geometry = geometry
        self.settings = settings
        self.tallies = tallies
        # Temporary material holder until matlist supports openmc mats
        self.materials = materials
        
        # Materials list (see matreader.py)
        self.matlist = matlist

        # Set a name
        self.name = name

    # This should be updated to use xml elements rather than strings
    def _get_lines(self, path: str):
        """Read in lines from file.

        Parameters
        ----------
        path : str
            Path to file

        Returns
        -------
        Optional[List[str]]
            List of lines from the file or none if file not found. 
        """
        if os.path.exists(path):
            with open(path, 'r') as f:
                lines = f.readlines()
        else:
            lines = None
        return lines        
    
    @classmethod
    def from_path(cls, path: str) -> 'OpenMCInputFiles':
        """Reads contents of geometry, settings, tallies, materials from XML files.

        Parameters
        ----------
        path : str
            path to the files

        Returns
        -------
        OpenMCInputFiles
            Intance of class initialised with data from XML files.
        """

        geometry_file = os.path.join(path, 'geometry.xml')
        geometry = cls._get_lines(cls, geometry_file)

        settings_file = os.path.join(path, 'settings.xml')
        settings = cls._get_lines(cls, settings_file)

        tallies_file = os.path.join(path, 'tallies.xml')
        tallies = cls._get_lines(cls, tallies_file)

        materials_file = os.path.join(path, 'materials.xml')
        materials = cls._get_lines(cls, materials_file)

        matlist = None

        name = os.path.basename(os.path.dirname(path))

        return cls(geometry, settings, tallies, materials, matlist, name=name)

    def add_stopCard(self, nps: int) -> None:
        """Add number of particles to simulate 

        Parameters
        ----------
        nps : int
            number of particles to simulate
        """
        for i, line in enumerate(self.settings):
            if '<settings>' in line:
                batches_line = '  <batches>100</batches>\n'
                self.settings.insert(i+1, batches_line)
                particles = int(nps/100)
                particles_line = '  <particles>'+str(particles)+'</particles>\n'
                self.settings.insert(i+1, particles_line)
                break

    def _to_xml(self, libmanager) -> tuple:
        """Convert Class data to XML format

        Parameters
        ----------
        libmanager : libmanager
            Library manager

        Returns
        -------
        tuple
            A tuple containing XML representations of geometry, settings, tallies, and materials.
        """

        # Add materials
        self.materials = self.matlist.to_xml(libmanager)

        geometry = ''
        for line in self.geometry:
            geometry = geometry+line
        
        settings = ''
        for line in self.settings:
            settings = settings+line

        tallies = ''
        for line in self.tallies:
            tallies = tallies+line

        materials = self.materials

        return geometry, settings, tallies, materials

    def write(self, path, libmanager) -> None:
        """
        Write the input to a file

        Parameters
        ----------
        out : str
            path to the output file.

        Returns
        -------
        None.

        """
        geometry, settings, tallies, materials = self._to_xml(libmanager)

        geometry_file = os.path.join(path, 'geometry.xml')
        with open(geometry_file, 'w') as outfile:
            outfile.write(geometry)

        settings_file = os.path.join(path, 'settings.xml')
        with open(settings_file, 'w') as outfile:
            outfile.write(settings)

        tallies_file = os.path.join(path, 'tallies.xml')
        with open(tallies_file, 'w') as outfile:
            outfile.write(tallies)

        materials_file = os.path.join(path, 'materials.xml')
        with open(materials_file, 'w') as outfile:
            outfile.write(materials)
