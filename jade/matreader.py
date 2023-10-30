# -*- coding: utf-8 -*-

# Created on 24/10/2019

# @author: Davide laghi

# Support classes for MCNP material card reader/writer

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

import copy
import os
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from contextlib import contextmanager
from decimal import Decimal

import pandas as pd

from numjuggler import parser as par

# -------------------------------------
#         == COMMON PATTERNS ==
# -------------------------------------
PAT_COMMENT = re.compile(r"[cC][\s\t]+")
PAT_MAT = re.compile(r"[\s\t]*[mM]\d+")
PAT_MX = re.compile(r"[\s\t]*mx\d+", re.IGNORECASE)


def indent(elem, level=0) -> None:
    """Indent an XML element and its children to make the XML structure more human-readable.

    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        XML element to be indented
    level : int, optional
        Current level of indentation, by default 0
    """

    # Create the indentation string based on the specified level
    i = "\n" + level * "  "
    if len(elem):
        # If the element has child elements
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# -------------------------------------
# == CLASSES FOR MATERIAL READING ==
# -------------------------------------
class Zaid:
    def __init__(self, fraction, element, isotope, library, ab="", fullname=""):
        """
        Object representing a Zaid

        Parameters
        ----------
        fraction : str/float
            fraction of the zaid.
        element : str
            element part of the zaid (AA).
        isotope : str
            isotope part of the zaid (ZZZ).
        library : str
            library suffix (e.g. 99c).
        ab : str, optional
            abundance of the zaid in the material. The default is ''.
        fullname : str, optional
            formula name (e.g. H1). The default is ''.

        Returns
        -------
        None.

        """
        self.fraction = float(fraction)
        self.element = element
        self.isotope = isotope
        self.library = library
        self.ab = ab
        self.fullname = fullname

        if self.library is None:
            self.name = self.element + self.isotope
        else:
            self.name = self.element + self.isotope + "." + self.library

    @classmethod
    def from_string(cls, string):
        """
        Generate a zaid object from an MCNP string

        Parameters
        ----------
        cls : matreader.Zaid
            zaid to be created.
        string : str
            original MCNP string.

        Returns
        -------
        Zaid
            created zaid.

        """
        # Divide fraction from zaid
        patSpacing = re.compile(r"[\s\t]+")
        items = patSpacing.split(string)

        # ZAID
        pieces = items[0].split(".")
        # Try to identify library if present
        try:
            library = pieces[1]
        except IndexError:
            library = None

        # Identify element and isotope
        element = pieces[0][:-3]
        isotope = pieces[0][-3:]

        # identify fraction
        fraction = items[1]

        return cls(fraction, element, isotope, library)

    def to_text(self):
        """
         Get the zaid string ready for a material card

        Returns
        -------
        str
            zaid string.

        """
        fraction = "{:.6E}".format(Decimal(self.fraction))
        if self.library is None:
            zaidname = self.element + self.isotope
        else:
            zaidname = self.element + self.isotope + "." + self.library
        # formats abundance floating point number as a string
        try:
            abundance = "%s" % float("%.5g" % float(self.ab))
        except ValueError:
            abundance = ""

        abundance = "AB(%) " + abundance
        inline_comm = "    $ " + self.fullname
        args = (zaidname, fraction, inline_comm, abundance)

        return "{0:>15} {1:>18} {2:<12} {3:<10}".format(*args)

    def to_xml(self, libmanager, submaterial) -> None:
        """Generate XML content for a nuclide within a material.

        Parameters
        ----------
        libmanager :
            libmanager
        submaterial :
            The XML element for the material where the nuclide content will be added.
        """
        nuclide = self.get_fullname(libmanager).replace("-", "")
        if self.fraction < 0.0:
            ET.SubElement(
                submaterial, "nuclide", name=nuclide, wo=str(abs(self.fraction))
            )
        else:
            ET.SubElement(
                submaterial, "nuclide", name=nuclide, ao=str(abs(self.fraction))
            )

    def get_fullname(self, libmanager):
        """
        Get the formula name of the zaid (e.g. H1)

        Parameters
        ----------
        libmanager : libmanager.LibManager
            libmanager handling the libraries operations.

        Returns
        -------
        formula : str
            zaid formula name.

        """
        name, formula = libmanager.get_zaidname(self)

        return formula


#    def update_info(self,ab,fullname):
#        """
#        Update zaid info
#        """
#        self.additional_info['ab'] = ab
#        self.additional_info['fullname'] = fullname


class Element:
    def __init__(self, zaidList):
        """
        Generate an Element object starting from a list of zaids.
        It will collapse multiple instance of a zaid into a single one

        Parameters
        ----------
        zaidList : list
            list of zaids constituing the element.

        Returns
        -------
        None.

        """
        zaids = {}
        for zaid in zaidList:
            # If already in dic sum the fractions
            if zaid.name in zaids.keys():
                zaids[zaid.name] = zaids[zaid.name] + zaid.fraction
            else:
                zaids[zaid.name] = zaid.fraction

        zaidList = []
        for name, fraction in zaids.items():
            zaidList.append(Zaid.from_string(name + " " + str(fraction)))

        self.Z = zaid.element
        self.zaids = zaidList

    def update_zaidinfo(self, libmanager):
        """
        Update zaids infos through a libmanager. Info are the formula name and
        the abundance in the material.

        Parameters
        ----------
        libmanager : libmanager.LibManager
            libmanager handling the libraries operations.

        Returns
        -------
        None.

        """
        tot_fraction = 0
        for zaid in self.zaids:
            tot_fraction = tot_fraction + zaid.fraction

        for zaid in self.zaids:
            fullname = zaid.get_fullname(libmanager)
            ab = zaid.fraction / tot_fraction * 100
            #            zaid.update_info(ab,fullname)
            zaid.ab = ab
            zaid.fullname = fullname

    def get_fraction(self):
        """
        Get the sum of the fraction of the zaids composing the element

        Returns
        -------
        fraction : float
            element fraction.

        """
        fraction = 0
        for zaid in self.zaids:
            fraction = fraction + zaid.fraction

        return fraction


class SubMaterial:
    # init method for zaid
    def __init__(self, name, zaidList, elemList=None, header=None, additional_keys=[]):
        """
        Generate a SubMaterial Object starting from a list of Zaid and
        eventually Elements list

        Parameters
        ----------
        name : str
            if the first submaterial, the name is the name of the material
            (e.g. m1).
        zaidList : list[Zaid]
            list of zaids composing the submaterial.
        elemList : list[Element], optional
            list of elements composing the submaterial. The default is None.
        header : str, optional
            Header of the submaterial. The default is None.
        additional_keys : list[str], optional
            list of additional keywords in the submaterial. The default is [].

        Returns
        -------
        None.

        """

        # List of zaids object of the submaterial
        self.zaidList = zaidList

        # Name of the material
        if name is not None:
            self.name = name.strip()  # Be sure to strip spaces
        else:
            self.name = None

        # List of elements in material
        if elemList is None:
            self.collapse_zaids()
        else:
            self.elements = elemList

        # Header of the submaterial
        self.header = header

        # Additional keys as plib,hlib etc.
        self.additional_keys = additional_keys

    @classmethod
    def from_text(cls, text):
        """
        Generate a submaterial from MCNP input text

        Parameters
        ----------
        cls : SubMaterial
            submaterial to be generated.
        text : list[str]
            Original text of the MCNP input.

        Returns
        -------
        SubMaterial
            generated submaterial.

        """
        # Useful patterns
        patSpacing = re.compile(r"[\s\t]+")
        patComment = PAT_COMMENT
        patName = PAT_MAT
        searchHeader = True
        header = ""
        zaidList = []
        additional_keys_list = []
        for line in text:
            zaids = None
            additional_keys = None
            # Header MUST be at the top of the text block
            if searchHeader:
                # Get header
                if patComment.match(line) is None:
                    searchHeader = False
                    # Special treatment for first line
                    try:
                        name = patName.match(line).group()
                    except AttributeError:
                        # There is no material name
                        name = None

                    pieces = patSpacing.split(line)
                    if len(pieces) > 1:
                        # CASE1: only material name+additional spacing
                        if pieces[1] == "":
                            pass  # no more actions for this line
                        # CASE2: material name + zaids or only zaids
                        else:
                            if name is None:
                                start = 0
                            else:
                                start = patName.match(line).end()
                            zaids, additional_keys = readLine(line[start:])
                    # CASE3: only material name and no spacing
                    else:
                        pass  # no more actions for this line
                else:
                    header = header + line
                    continue
            else:
                zaids, additional_keys = readLine(line)

            if zaids is not None:
                zaidList.extend(zaids)

            if additional_keys is not None:
                additional_keys_list.extend(additional_keys)

        return cls(
            name,
            zaidList,
            elemList=None,
            header=header[:-1],
            additional_keys=additional_keys_list,
        )

    def collapse_zaids(self):
        """
        Organize zaids into their elements and collapse multiple instances

        Returns
        -------
        None.

        """
        elements = {}
        for zaid in self.zaidList:
            if zaid.element not in elements.keys():
                elements[zaid.element] = [zaid]
            else:
                elements[zaid.element].append(zaid)

        elemList = []
        for element_tag, zaids in elements.items():
            elemList.append(Element(zaids))

        self.elements = elemList

    def to_text(self):
        """
        Write to text in MNCP format the submaterial

        Returns
        -------
        str
            formatted submaterial text.

        """
        if self.header is not None:
            text = self.header + "\n"
        else:
            text = ""
        # if self.name is not None:
        #     text = text+'\n'+self.name
        if self.elements is not None:
            for elem in self.elements:
                for zaid in elem.zaids:
                    text = text + zaid.to_text() + "\n"
        else:
            for zaid in self.zaidList:
                text = text + zaid.to_text() + "\n"

        # Add additional keys
        if len(self.additional_keys) > 0:
            text = text + "\t"
            for key in self.additional_keys:
                text = text + " " + key

        return text.strip("\n")

    def to_xml(self, libmanager, material) -> None:
        """Generate XML content for a material and add it to a material tree.

        Parameters
        ----------
        libmanager :
            libmanager handling the libraries operations.
        material :
            The XML tree where the material content will be added.
        """

        #matid = id
        #matname = str(self.name)
        #matdensity = str(abs(density))
        #if density < 0:
        #    density_units = "g/cc"
        #else:
        #    density_units = "atom/b-cm"
        #submaterial = ET.SubElement(material_tree, "material", id=matid, name=matname)
        #ET.SubElement(submaterial, "density", value=matdensity, units=density_units)
        if self.elements is not None:
            for elem in self.elements:
                for zaid in elem.zaids:
                    zaid.to_xml(libmanager, material)
        else:
            for zaid in self.zaidList:
                zaid.to_xml(libmanager, material)

    def translate(self, newlib, lib_manager, code):
        """
        This method implements the translation logic of JADE. All zaids are
        translated accordingly to the newlib specified.

        Parameters
        ----------
        newlib : dict or str
            There are a few ways that newlib can be provided:

            1) str (e.g. 31c), the new library to translate to will be the
            one indicated;

            2) dic (e.g. {'98c' : '99c', '31c: 32c'}), the new library is
            determined based on the old library of the zaid

            3) dic (e.g. {'98c': [list of zaids], '31c': [list of zaids]}),
            the new library to be used is explicitly stated depending
            on the zaidnum.
        lib_manager : LibManager
            Object handling libraries operation.

        Returns
        -------
        None.

        """
        newzaids = []
        for zaid in self.zaidList:
            # Implement the capability to translate to different libraries
            # depending on the starting one
            if type(newlib) == dict:
                # Check for which kind of dic it is
                if type(list(newlib.values())[0]) == str:
                    # The assignment is based on old lib
                    try:
                        newtag = newlib[zaid.library]
                    except KeyError:
                        # the zaid should have been assigned to a library
                        raise ValueError(
                            """
 Zaid {} was not assigned to any library""".format(
                                zaid.name
                            )
                        )

                else:
                    # The assignment is explicit, all libs need to be searched
                    newtag = None
                    zaidnum = zaid.element + zaid.isotope
                    for lib, zaids in newlib.items():
                        if zaidnum in zaids:
                            newtag = lib
                            break
                    # Check that a library has been actually found
                    if newtag is None:
                        # the zaid should have been assigned to a library
                        raise ValueError(
                            """
 Zaid {} was not assigned to any library""".format(
                                zaid.name
                            )
                        )
            else:
                newtag = newlib

            try:
                translation = lib_manager.convertZaid(
                    zaid.element + zaid.isotope, newtag, code
                )
            except ValueError:
                # No Available translation was found, ignore zaid
                # Only video warning, to propagate to the log would be too much
                print(
                    "  WARNING: no available translation was found for "
                    + zaid.name
                    + ".\n  The zaid has been ignored. "
                )
                continue

            # Check if it is  atomic or mass fraction
            if float(zaid.fraction) < 0:
                ref_mass = 0
                for key, item in translation.items():
                    ref_mass = ref_mass + item[1] * item[2]

                for key, item in translation.items():
                    fraction = str(item[1] * item[2] / ref_mass * zaid.fraction)
                    element = str(key)[:-3]
                    isotope = str(key)[-3:]
                    library = item[0]

                    newzaids.append(Zaid(fraction, element, isotope, library))

            else:
                for key, item in translation.items():
                    fraction = str(item[1] * zaid.fraction)
                    element = str(key)[:-3]
                    isotope = str(key)[-3:]
                    library = item[0]

                    newzaids.append(Zaid(fraction, element, isotope, library))

        self.zaidList = newzaids
        self.collapse_zaids()

    def update_info(self, lib_manager):
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
        self.collapse_zaids()  # To be sure to have adjourned elements

        for elem in self.elements:
            elem.update_zaidinfo(lib_manager)

        # TODO
        # Here the zaidlist of the submaterial should be adjourned or the next
        # collapse zaid will cancel the informations. If update info is used
        # as last operations there are no problems.

    def get_info(self, lib_manager):
        """
        Returns DataFrame containing the different fractions of the elements
        and zaids

        Parameters
        ----------
        lib_manager : libmanager.LibManager
            Library manager for the conversion.

        Returns
        -------
        df_el : pd.DataFrame
            table of information of the submaterial on an elemental level.
        df_zaids : pd.DataFrame
            table of information of the submaterial on a zaid level.

        """
        # dic_element = {'Element': [], 'Fraction': []}
        # dic_zaids = {'Element': [], 'Zaid': [], 'Fraction': []}
        dic_element = {"Element": [], "Fraction": []}
        dic_zaids = {"Element": [], "Isotope": [], "Fraction": []}
        for elem in self.elements:
            fraction = elem.get_fraction()
            # dic_element['Element'].append(elem.Z)
            dic_element["Fraction"].append(fraction)
            for zaid in elem.zaids:
                fullname = zaid.get_fullname(lib_manager)
                elementname = fullname.split("-")[0]
                # dic_zaids['Element'].append(elem.Z)
                # dic_zaids['Zaid'].append(zaid.isotope)
                dic_zaids["Element"].append(elementname)
                dic_zaids["Isotope"].append(
                    fullname + " [" + str(zaid.element) + str(zaid.isotope) + "]"
                )
                dic_zaids["Fraction"].append(zaid.fraction)

            dic_element["Element"].append(elementname)

        df_el = pd.DataFrame(dic_element)
        df_zaids = pd.DataFrame(dic_zaids)

        return df_el, df_zaids

    def scale_fractions(self, norm_factor):
        """
        Scale the zaids fractions using a normalizing factor

        Parameters
        ----------
        norm_factor : float
            scaling factor.

        Returns
        -------
        None.

        """
        for zaid in self.zaidList:
            zaid.fraction = zaid.fraction * norm_factor

        self.collapse_zaids()


# Support function for Submaterial
# Could be moved to static method
def readLine(string: str):
    """Peforms various operations on a string

    Parameters
    ----------
    string : str
        string to operate on

    Returns
    -------
    tuple
        Contains zaids and additional keys as lists
    """
    # Define regular expressions
    patSpacing = re.compile(r"[\s\t]+")
    patComment = re.compile(r"\$")
    patnumber = re.compile(r"\d+")

    pieces = patSpacing.split(string)
    # Remove first piece if it is empty
    if pieces[0] == "":
        del pieces[0]
    # Remove last piece if it is empty
    if pieces[-1] == "":
        del pieces[-1]

    # Remove comment section
    i = 0
    for i, piece in enumerate(pieces):
        if patComment.match(pieces[i]) is not None:
            del pieces[i:]
            break

    i = 0
    zaids = []
    additional_keys = None
    while True:
        try:
            # Check if it is zaid or keyword
            if patnumber.match(pieces[i]) is None or pieces[i] == "":
                additional_keys = pieces[i:]
                break
            else:
                zaidstring = pieces[i] + " " + pieces[i + 1]
                zaid = Zaid.from_string(zaidstring)
                zaids.append(zaid)

            i = i + 2

        except IndexError:
            break

    return zaids, additional_keys


class Material:
    def __init__(
        self,
        zaids,
        elem,
        name,
        submaterials=None,
        mx_cards=[],
        header=None,
        density=None,
    ):
        """
        Object representing a material

        Parameters
        ----------
        zaids : list[zaids]
            zaids composing the material.
        elem : list[elem]
            elements composing the material.
        name : str
            name of the material (e.g. m1).
        submaterials : list[Submaterials], optional
            list of submaterials composing the material. The default is None.
        mx_cards : list, optional
            list of mx_cards in the material if present. The default is [].
        header : str, optional
            material header. The default is None.
        density : float, optional
            material density. Default is None.

        Returns
        -------
        None.

        """

        self.zaids = zaids
        self.elem = elem
        self.submaterials = submaterials
        self.name = name.strip()
        self.mx_cards = mx_cards
        self.header = header
        self.density = density

        # Adjust the submaterial and headers reading
        try:
            # The first submaterial header is actually the material header.
            # If submat is void it has to be deleted (only header), otherwise
            # it means it has no header
            submat = submaterials[0]
            if len(submat.zaidList) == 0:  # Happens in reading from text
                # self.header = submat.header
                del self.submaterials[0]
            # else:
            #     self.submaterials[0].header = None
        except IndexError:
            self.header = None

    @classmethod
    def from_text(cls, text):
        """
        Create a material from transport code formatted text.

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        text : list[str]
            Transport code formatted text.

        Returns
        -------
        matreader.Material
            material object created.

        """
        # split the different submaterials
        patC = PAT_COMMENT
        pat_matHeader = PAT_MAT
        inHeader = True
        subtext = []
        submaterials = []

        for line in text:
            checkComment = patC.match(line)
            checkHeaderMat = pat_matHeader.match(line)

            if checkHeaderMat is not None:
                header = "".join(subtext)
                subtext = []

            if inHeader:
                subtext.append(line)
                if checkComment is None:  # The end of the header is found
                    inHeader = False
            else:
                if checkComment is None:  # Still in the material
                    subtext.append(line)
                else:  # a new header starts
                    submaterials.append(SubMaterial.from_text(subtext))
                    inHeader = True
                    subtext = [line]

        submaterials.append(SubMaterial.from_text(subtext))

        return cls(
            None, None, submaterials[0].name, submaterials=submaterials, header=header
        )

    def to_text(self):
        """
        Write the material to transport code formatted text.

        Returns
        -------
        str
            Transport code formatted text representing the material.

        """
        if self.density is not None:
            if self.header is not None:
                text = (
                    self.header.strip("\n")
                    + "\n"
                    + self.name.lower().strip("\n")
                    + " "
                    + str(self.density)
                )
            else:
                text = self.name.lower() + " " + str(self.density)
        else:
            if self.header is not None:
                text = self.header.strip("\n") + "\n" + self.name.upper().strip("\n")
            else:
                text = self.name.upper()
        if self.submaterials is not None:
            for submaterial in self.submaterials:
                text = text + "\n" + submaterial.to_text()
            # Add mx cards
            for mx in self.mx_cards:
                for line in mx:
                    line = line.strip("\n")
                    text = text + "\n" + line.upper()
        else:
            text = "  Not supported yet, generate submaterials first"
            pass  # TODO
        if self.density is not None:
            text = text.replace("$", "%")
            text = re.sub("^c", "%", text, flags=re.MULTILINE | re.I)

        return text.strip("\n")

    def to_xml(self, libmanager, material_tree):
        """Generate XML content for a material and its submaterials.

        Parameters
        ----------
        libmanager :
            libmanager
        material_tree :
            The XML element for the material where content will be added.
        """
        matid = re.sub("[^0-9]", "", str(self.name))
        matname = str(self.name)
        matdensity = str(abs(self.density))
        if self.density < 0:
            density_units = "g/cc"
        else:
            density_units = "atom/b-cm"
        material = ET.SubElement(material_tree, "material", id=matid, name=matname)
        ET.SubElement(material, "density", value=matdensity, units=density_units)
        if self.submaterials is not None:
            for submaterial in self.submaterials:
                submaterial.to_xml(libmanager, material)

    def translate(self, newlib, lib_manager, code="mcnp", update=True):
        """
        This method allows to translate all submaterials to another library

        Parameters
        ----------
        newlib : dict or str
            There are a few ways that newlib can be provided:

            1) str (e.g. 31c), the new library to translate to will be the
            one indicated;

            2) dic (e.g. {'98c' : '99c', '31c: 32c'}), the new library is
            determined based on the old library of the zaid

            3) dic (e.g. {'98c': [list of zaids], '31c': [list of zaids]}),
            the new library to be used is explicitly stated depending
            on the zaidnum.
        lib_manager : libmanager.LibManager
            object handling all libraries operations.
        update : bool, optional
            if True, material infos are updated. The default is True.

        Returns
        -------
        None.
        """
        for submat in self.submaterials:
            submat.translate(newlib, lib_manager, code)

        self.update_info(lib_manager)

    def get_tot_fraction(self):
        """
        Returns the total material fraction
        """
        fraction = 0
        for submat in self.submaterials:
            for zaid in submat.zaidList:
                fraction = fraction + zaid.fraction

        return fraction

    def add_mx(self, mx_cards):
        """
        Add a list of mx_cards to the material
        """
        self.mx_cards = mx_cards

    def update_info(self, lib_manager):
        """
        This methods allows to update the in-line comments for every zaids
        containing additional information

        lib_manager: (LibManager) Library manager for the conversion
        """
        for submaterial in self.submaterials:
            submaterial.update_info(lib_manager)

    def switch_fraction(self, ftype, lib_manager, inplace=True):
        """
        Switch between atom or mass fraction for the material card.
        If the material is already switched the command is ignored.

        Parameters
        ----------
        ftype : str
            Either 'mass' or 'atom' to chose the type of switch.
        lib_manager : libmanager.LibManager
            Handles zaid data.
        inplace : bool
            if True the densities of the isotopes are changed inplace,
            otherwise a copy of the material is provided. DEFAULT is True

        Raises
        ------
        KeyError
            if ftype is not either 'atom' or 'mass'.

        Returns
        -------
        submaterials : list
            list of the submaterials where fraction have been switched

        """
        # Get total fraction
        totf = self.get_tot_fraction()
        new_submats = []

        if ftype == "atom":  # mass2atom switch
            if totf < 0:  # Check if the switch must be effectuated
                # x_n = (x_m/m)/sum(x_m/m)
                # get sum(x_m/m)
                norm = 0
                for submat in self.submaterials:
                    for zaid in submat.zaidList:
                        atom_mass = lib_manager.get_zaid_mass(zaid)
                        norm = norm + (-1 * zaid.fraction / atom_mass)

                for submat in self.submaterials:
                    new_zaids = []
                    new_submat = copy.deepcopy(submat)
                    for zaid in submat.zaidList:
                        atom_mass = lib_manager.get_zaid_mass(zaid)
                        if inplace:
                            zaid.fraction = (-1 * zaid.fraction / atom_mass) / norm
                        else:
                            newz = copy.deepcopy(zaid)
                            newz.fraction = (-1 * zaid.fraction / atom_mass) / norm
                            new_zaids.append(newz)
                    new_submat.zaidList = new_zaids
                    new_submat.update_info(lib_manager)
                    new_submats.append(new_submat)
            else:
                new_submats = self.submaterials

        elif ftype == "mass":  # atom2mass switch
            if totf > 0:  # Check if the switch must be effectuated
                # x_n = (x_m*m)/sum(x_m*m)
                # get sum(x_m*m)
                norm = 0
                for submat in self.submaterials:
                    for zaid in submat.zaidList:
                        atom_mass = lib_manager.get_zaid_mass(zaid)
                        norm = norm + (zaid.fraction * atom_mass)

                for submat in self.submaterials:
                    new_zaids = []
                    new_submat = copy.deepcopy(submat)
                    for zaid in submat.zaidList:
                        atom_mass = lib_manager.get_zaid_mass(zaid)
                        if inplace:
                            zaid.fraction = (-1 * zaid.fraction * atom_mass) / norm
                        else:
                            newz = copy.deepcopy(zaid)
                            newz.fraction = (-1 * zaid.fraction * atom_mass) / norm
                            new_zaids.append(newz)
                    new_submat.zaidList = new_zaids
                    new_submat.update_info(lib_manager)
                    new_submats.append(new_submat)
            else:
                new_submats = self.submaterials

        else:
            raise KeyError(ftype + " is not a valid key error [atom, mass]")

        self.update_info(lib_manager)

        return new_submats


class MatCardsList(Sequence):
    def __init__(self, materials):
        """
        Object representing the list of materials included in an MCNP input.
        This class is a child of the Sequence base class.

        Parameters
        ----------
        materials : list[Material]
            list of materials.

        Returns
        -------
        None.

        """
        self.materials = materials
        # Build also the dictionary
        self.matdic = self._compute_dic()

    def __len__(self):
        return len(self.materials)

    def __repr__(self):
        return str(self.matdic)

    def __getitem__(self, key):
        if type(key) is int:
            return self.materials[key]
        else:
            return self.matdic[key.upper()]

    def append(self, material):
        self.materials.append(material)
        self.matdic = self._compute_dic()

    def remove(self, item):
        self.materials.remove(item)  # TODO this should get the key instead
        self.matdic = self._compute_dic()

    def _compute_dic(self):
        matdic = {}
        for material in self.materials:
            matdic[material.name.upper()] = material

        return matdic

    @classmethod
    def from_input(cls, inputfile):
        """
        This method use the numjuggler parser to help identify the mcards in
        the input. Then the mcards are parsed using the classes defined in this
        module

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        inputfile : os.PathLike
            MCNP input file containing the material section.

        Returns
        -------
        MatCardsList
            new material card list generated.

        """
        matPat = PAT_MAT
        mxPat = PAT_MX
        commentPat = PAT_COMMENT
        # Using parser the data cards are extracted from the input.
        # Comment section are interpreted as cards by the parser
        with suppress_stdout():
            # Suppress output from tab replacing
            cards = par.get_cards_from_input(inputfile)
            cardsDic = par.get_blocks(cards)
        datacards = cardsDic[5]

        materials = []
        previous_lines = [""]
        mx_cards = []
        mx_found = False

        for datacard in datacards:
            lines = datacard.lines

            # Check if it is a material card
            if matPat.match(lines[0]) is not None:
                # Check if previous card is the header
                if commentPat.match(previous_lines[0]):
                    previous_lines.extend(lines)
                    material = Material.from_text(previous_lines)
                else:
                    material = Material.from_text(lines)

                materials.append(material)

            # Check if the current is an mx cards
            if mxPat.match(lines[0]) is not None:
                mx_cards.append(lines)
                mx_found = True

            # If not Add mx cards if previous one was an mx
            elif mx_found:
                materials[-1].add_mx(mx_cards)
                mx_cards = []
                mx_found = False

            else:
                mx_found = False

            previous_lines = lines

        # If material is last datacard
        if mx_found:
            materials[-1].add_mx(mx_cards)

        return cls(materials)

    def to_text(self):
        """
        return text of the material cards in order

        Returns
        -------
        str
            material card list MCNP formatted text.

        """
        text = ""
        for material in self.materials:
            text = text + "\n" + material.to_text()

        return text.strip("\n")

    def to_xml(self, libmanager) -> str:
        """Generate an XML representation of materials and return it as a string.

        Parameters
        ----------
        libmanager :
            libmanager

        Returns
        -------
        str
            The XML representation of materials as a string.
        """

        # Create XML element to represent the collection of materials.
        material_tree = ET.Element("materials")

        for material in self.materials:
            material.to_xml(libmanager, material_tree)

        # Apply indentation to the generated XML data.
        indent(material_tree)

        return ET.tostring(material_tree, encoding="unicode", method="xml")

    def translate(self, newlib, lib_manager, code="mcnp"):
        """
        This method allows to translate the material cards to another library.
        The zaid are collapsed again to get the new elements

        Parameters
        ----------
        newlib : dict or str
            There are a few ways that newlib can be provided:

            1) str (e.g. 31c), the new library to translate to will be the
            one indicated;

            2) dic (e.g. {'98c' : '99c', '31c: 32c'}), the new library is
            determined based on the old library of the zaid

            3) dic (e.g. {'98c': [list of zaids], '31c': [list of zaids]}),
            the new library to be used is explicitly stated depending
            on the zaidnum.
        lib_manager : libmanager.LibManager
            Library manager for the conversion.

        Returns
        -------
        None.

        """
        for material in self.materials:
            material.translate(newlib, lib_manager, code)

            # Rebuild elements
            for submat in material.submaterials:
                submat.collapse_zaids()

    def update_info(self, lib_manager):
        """
        This methods allows to update the in-line comments for every zaids
        containing additional information

        Parameters
        ----------
        lib_manager : libmanager.Libmanager
            Library manager for the conversion.

        Returns
        -------
        None.

        """
        for mat in self.materials:
            mat.update_info(lib_manager)

    def get_info(self, lib_manager, zaids=False, complete=False):
        """
        Get the material informations in terms of fraction and composition
        of the material card

        Parameters
        ----------
        lib_manager : libmanager.LibManager
            To handle element name recovering.
        zaids : bool, optional
            Consider or not the zaid level. The default is False.
        complete: bool, optional
            If True both the atom and mass fraction are given in the raw
            table. The default is False.

        Returns
        -------
        df : pd.DataFrame
            Raw infos on the fractions.
        df_elem : pd.DataFrame
            processed info for the element: normalized fraction added both for
            material and submaterial.

        """
        infos = []
        complete_infos = []
        for mat in self.materials:
            submats_atom = mat.switch_fraction("atom", lib_manager, inplace=False)
            submats_mass = mat.switch_fraction("mass", lib_manager, inplace=False)
            i = 0
            for submat, submat_a, submat_m in zip(
                mat.submaterials, submats_atom, submats_mass
            ):
                dic_el, dic_zaids = submat.get_info(lib_manager)
                dic_el_a, dic_zaids_a = submat_a.get_info(lib_manager)
                dic_el_m, dic_zaids_m = submat_m.get_info(lib_manager)

                if zaids:
                    dic = dic_zaids
                    dic_a = dic_zaids_a
                    dic_m = dic_zaids_m
                else:
                    dic = dic_el
                    dic_a = dic_el_a
                    dic_m = dic_el_m

                dic["Material"] = mat.name
                dic["Submaterial"] = i + 1
                infos.append(dic)

                c_dic = copy.deepcopy(dic)
                c_dic["Atom Fraction"] = dic_a["Fraction"]
                c_dic["Mass Fraction"] = dic_m["Fraction"]
                complete_infos.append(c_dic)

                i = i + 1

        df = pd.concat(infos)
        df_complete = pd.concat(complete_infos)
        del df_complete["Fraction"]

        if zaids:
            df.set_index(
                ["Material", "Submaterial", "Element", "Isotope"], inplace=True
            )
            df_complete.set_index(
                ["Material", "Submaterial", "Element", "Isotope"], inplace=True
            )

        else:
            df.set_index(["Material", "Submaterial", "Element"], inplace=True)
            df_complete.set_index(["Material", "Submaterial", "Element"], inplace=True)

        # Additional df containing normalized element fraction of submaterial
        # and material

        # Get total fractions
        df_elem = df.groupby(["Material", "Submaterial", "Element"]).sum()
        df_sub = df.groupby(["Material", "Submaterial"]).sum()
        df_mat = df.groupby(["Material"]).sum()

        # Compute percentages
        sub_percentage = []
        mat_percentage = []
        for idx, row in df_elem.iterrows():
            matID = idx[0]
            elemID = idx[1]
            sub_percentage.append(
                row["Fraction"] / df_sub["Fraction"].loc[(matID, elemID)]
            )
            mat_percentage.append(row["Fraction"] / df_mat["Fraction"].loc[matID])

        df_elem["Sub-Material Fraction"] = sub_percentage
        df_elem["Material Fraction"] = mat_percentage

        if complete:
            return df_complete, df_elem
        else:
            return df, df_elem


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
