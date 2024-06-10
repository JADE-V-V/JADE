"""
Parsing of D1S-UNED additional files

Parsers for the irradiation and reaction files necessary for Direct-1-Step
calculation using D1S-UNED.
"""

from __future__ import annotations

"""
Copyright 2019 F4E | European Joint Undertaking for ITER and the Development of
Fusion Energy (‘Fusion for Energy’). Licensed under the EUPL, Version 1.2 or - 
as soon they will be approved by the European Commission - subsequent versions
of the EUPL (the “Licence”). You may not use this work except in compliance
with the Licence. You may obtain a copy of the Licence at:
    https://eupl.eu/1.2/en/
Unless required by applicable law or agreed to in writing, software distributed
under the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the Licence permissions
and limitations under the Licence.
"""

import re
import os
import logging

from f4enix.constants import PAT_BLANK, PAT_COMMENT, PAT_SPACE
from f4enix.input.libmanager import LibManager

# PAT_COMMENT = re.compile('[Cc]+')

REACFORMAT = "{:>13s}{:>7s}{:>9s}{:>40s}"


class IrradiationFile:

    def __init__(
        self,
        nsc: int,
        irr_schedules: list[Irradiation],
        header: str = None,
        formatting: list[int] = [8, 14, 13, 9],
        name: str = "irrad",
    ) -> None:
        """
        Object representing an irradiation D1S-UNED file.

        It is built as a container of single irradiation object

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

        Attributes
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

        Examples
        --------
        Some usage examples

        >>> # parse an existing file
        ... irrad_file = IrradiationFile.from_text('irr_test')
        ... # get the list of irradiation schedules
        ... irrad_file.irr_schedules
        [['24051', '2.896e-07', '5.982e+00', '5.697e+00', 'Cr51'],
         ['25054', '2.570e-08', '5.881e+00', '1.829e+00', 'Mn54'],
         ['26055', '8.031e-09', '4.487e+00', '6.364e-01', 'Fe55']]

        >>> # auxiliary method to retrieve a specific irradiation
        ... print(irrad_file.get_irrad('24051'))
        Daughter: 24051
        lambda [1/s]: 2.896e-07
        times: ['5.982e+00', '5.697e+00']
        comment: Cr51

        >>> # auxiliary method to get all daughters
        ... print(irrad_file.get_daughters())
        ['24051', '25054', '26055']

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

        head = "{:>" + w1 + "s}{:>" + w2 + "s}{:>"
        for i in range(nsc):
            head += w3 + "s}{:>"

        head += w4 + "s}"

        self._irrformat = head
        self.name = name

    def get_daughters(self) -> list[str]:
        """
        Get a list of all daughters among all irradiation files

        Returns
        -------
        list[str]
            list of daughters.

        """
        # Get the list of daughters
        daughters = []
        for irradiation in self.irr_schedules:
            daughters.append(irradiation.daughter)

        return daughters

    def get_irrad(self, daughter: str) -> Irradiation | None:
        """
        Return the irradiation correspondent to the daughter

        Parameters
        ----------
        daughter : str
            (e.g. '24051').

        Returns
        -------
        Irradiation | None
            Returns the irradiation corresponding to the daughter.
            If no irradiation is found returns None.

        """
        for irradiation in self.irr_schedules:
            if daughter == irradiation.daughter:
                return irradiation

        return None

    @classmethod
    def from_text(cls, filepath: os.PathLike) -> IrradiationFile:
        """
        Initialize an IrradiationFile object directly parsing and existing
        irradiation file

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        filepath : os.PathLike
            path to the existing irradiation file.

        Returns
        -------
        None.

        """
        logging.info("Parsing {}".format(filepath))
        pat_nsc = re.compile("(?i)(nsc)")
        pat_num = re.compile(r"\d+")
        # name = os.path.basename(filepath)
        with open(filepath, "r") as infile:
            inheader = True
            header = ""
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
                    if (
                        PAT_BLANK.match(line) is None
                        and PAT_COMMENT.match(line) is None
                    ):

                        irr_schedules.append(Irradiation.from_text(line, nsc))

        logging.info("{} correctly parsed".format(filepath))

        return cls(nsc, irr_schedules, header=header)

    def write(self, path: os.PathLike) -> None:
        """
        Write the D1S irradiation file

        Parameters
        ----------
        path : os.PathLike
            output path where to save the file (only directory). self.name will
            be used as output file name

        Returns
        -------
        None.

        """
        filepath = os.path.join(path, self.name)
        with open(filepath, "w") as outfile:
            if self.header is not None:
                outfile.write(self.header)
            # write nsc
            outfile.write("nsc " + str(self.nsc) + "\n")

            # --- Write irradiation schedules ---
            # write header
            args = ["Daught.", "lambda(1/s)"]
            for i in range(self.nsc):
                args.append("time_fact_" + str(i + 1))
            args.append("comments")
            outfile.write("C " + self._irrformat.format(*args) + "\n")

            # write schedules
            for schedule in self.irr_schedules:
                args = schedule._get_format_args()
                outfile.write(self._irrformat.format(*args) + "\n")

        logging.info("Irradiation file written at {}".format(outfile))


class Irradiation:
    def __init__(
        self, daughter: str, lambd: str, times: list[str], comment: str = None
    ) -> None:
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

        Attributes
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

    def __eq__(self, other) -> bool:
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

            condition = daugther_eq and lamb_eq and times_eq

            return condition
        else:
            return False

    @classmethod
    def from_text(cls, text: str, nsc: int) -> Irradiation:
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
        Irradiation
            Instance of irradiation object.

        """
        pieces = PAT_SPACE.split(text)
        # Check for empty start
        if pieces[0] == "":
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
        comment = ""
        try:
            for piece in pieces[j:]:
                comment += " " + piece
        except IndexError:
            comment = None

        if comment == "":
            comment = None
        else:
            comment = comment.strip()

        return cls(daughter, lambd, times, comment=comment)

    def _get_format_args(self) -> list:
        args = [self.daughter, self.lambd]
        for time in self.times:
            args.append(time)
        args.append(self.comment)
        return args

    def _print(self) -> str:
        text = """
Daughter: {}
lambda [1/s]: {}
times: {}
comment: {}
""".format(
            self.daughter, self.lambd, self.times, self.comment
        )

        return text

    def __repr__(self) -> str:
        return str(self._get_format_args())

    def __str__(self) -> str:
        return self._print()


class ReactionFile:
    def __init__(self, reactions: list[Reaction], name: str = "react") -> None:
        """
        Reaction file object

        Parameters
        ----------
        reactions : list[Reaction]
            contains all reaction objects contained in the file.
        name : name, optional
            file name. The default is 'react'.

        Examples
        --------
        It is possible to change the libraries of a reaction file

        >>> from f4enix.input.d1suned import ReactionFile
        ... reac_file = ReactionFile.from_text('reac_fe')
        ... reac_file.change_lib('98c')

        and obtain a list of the parents

        >>> reac_file.get_parents()
        ['26054', '26056', '26057', '26058']

        Returns
        -------
        None.

        """
        self.reactions = reactions
        self.name = name

    @classmethod
    def from_text(cls, filepath: os.PathLike) -> ReactionFile:
        """
        Generate a reaction file directly from text file

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        filepath : os.PathLike
            file to read.

        Returns
        -------
        ReactionFile
            Reaction File Object.

        """
        # read all reactions
        logging.info("Parsing {}".format(filepath))
        reactions = []
        with open(filepath, "r") as infile:
            for line in infile:
                # Ignore if it is a blank line or a full line comment
                if PAT_BLANK.match(line) is None and PAT_COMMENT.match(line) is None:
                    # parse reactions
                    reaction = Reaction.from_text(line)
                    reactions.append(reaction)
        logging.info("{} correctly parsed".format(filepath))

        return cls(reactions)  # , name=os.path.basename(filepath))

    def get_parents(self) -> set[str]:
        """
        Get a list of all parents

        Returns
        -------
        set[str]
            list of parents from all reactions

        """
        parents = []
        for reaction in self.reactions:
            parent = reaction.parent.split(".")[0]
            if parent not in parents:
                parents.append(parent)
        return sorted(set(parents))

    def change_lib(self, newlib: str, libmanager: LibManager = None):
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
        if newlib[0] == "{":
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
                zaid = reaction.parent.split(".")[0]
                libs = libmanager.check4zaid(zaid)
                if newlib in libs:
                    reaction.change_lib(lib)
                else:
                    warning = "{} is not available in xsdir, not translated"
                    logging.warning(warning.format(zaid))

    def write(self, path: os.PathLike) -> None:
        """
        write formatted reaction file

        Parameters
        ----------
        path : os.PathLike
            path to the output file (only dir).

        Returns
        -------
        None.

        """
        filepath = os.path.join(path, self.name)
        with open(filepath, "w") as outfile:
            for reaction in self.reactions:
                outfile.write(REACFORMAT.format(*reaction._get_text()) + "\n")
        logging.info("Reaction file written at {}".format(outfile))

    def _print(self) -> str:
        text = REACFORMAT.format("Parent", "MT", "Daughter", "Comment") + "\n"
        for reaction in self.reactions:
            text = text + REACFORMAT.format(*reaction._get_text()) + "\n"
        return text

    def __repr__(self) -> str:
        return self._print()

    def __str__(self) -> str:
        return self._print()


class Reaction:
    def __init__(
        self, parent: str, MT: int | str, daughter: str, comment: str = None
    ) -> None:
        """
        Represents a single reaction of the reaction file

        Parameters
        ----------
        parent : str
            parent nuclide ZZAAA.XXc representing stable isotope to be
            activated. ZZ and AAA represent the atomic and mass number and
            extension XX, is the extension number of the modified D1S library.
        MT : int | str
            integer, reaction type (ENDF definition, e.g. 102).
        daughter : str
            integer, tag of the daughter nuclide. The value could be
            defined as ZZAAA of daughter nuclide, but any other identification
            type (with integer value) can be used.
        comment : str, optional
            comment to the reaction. The default is None.

        Attributes
        ----------
        parent : str
            parent nuclide ZZAAA.XXc representing stable isotope to be
            activated. ZZ and AAA represent the atomic and mass number and
            extension XX, is the extension number of the modified D1S library.
        MT : str
            integer, reaction type (ENDF definition, e.g. '102').
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

    def change_lib(self, newlib: str) -> None:
        """
        Change the library tag

        Parameters
        ----------
        newlib : str
            library extension as used in xsdir format (e.g. 00c).

        Returns
        -------
        None.

        """
        pieces = self.parent.split(".")
        # Override lib
        self.parent = pieces[0] + "." + newlib

    def _get_text(self) -> list[str]:
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
            comment = ""
        else:
            comment = self.comment
        textpieces.append(comment)

        return textpieces

    def _nice_print(self) -> str:
        text = """
parent: {}
MT channel: {}
daughter: {}
comment: {}
""".format(
            self.parent, self.MT, self.daughter, self.comment
        )
        return text

    @classmethod
    def from_text(cls, text: str) -> Reaction:
        """
        Create a Reaction object from text

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
        comment = ""
        if len(pieces) > 3:
            for piece in pieces[3:]:
                comment = comment + " " + piece

        comment = comment.strip()

        return cls(parent, MT, daughter, comment=comment)

    def __repr__(self) -> str:
        return self._nice_print()

    def __str__(self) -> str:
        return self._nice_print()
