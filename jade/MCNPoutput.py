"""
Parsing of MCNP output file (.o)

Only a few features are implemented for the moment being.
"""

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

import os
import re
import logging
import pandas as pd
import pyvista as pv
import numpy as np

from f4enix.constants import SCIENTIFIC_PAT, PAT_DIGIT
from f4enix.input.MCNPinput import Input

# -- Identifiers --
SURFACE_ID = "currently being tracked has reached surface"
CELL_ID = "other side of the surface from cell"
POINT_ID = "x,y,z coordinates:"
TOTAL_LP = "particles got lost"
# -- Patterns --
PAT_NPS_LINE = re.compile(r" source")
# patComments = re.compile(r'(?i)C\s+')
# patUniverse = re.compile(r'(?i)u=\d+')
# patNPS = re.compile(r'(?i)nps')
# patNPS_value = re.compile(r'\s+[eE.0-9]+\s*')
# patXYZ = re.compile(r'\s+[eE.0-9]+\s[eE.0-9]+\s[eE.0-9]+\s*')
# patSDEF = re.compile(r'(?i)sdef')
# patSDEFsur = re.compile(r'(?i)sur=\d+')

STAT_CHECKS_COLUMNS = [
    "TFC bin behaviour",
    "mean behaviour",
    "rel error value",
    "rel error decrease",
    "rel error decrease rate",
    "VoV value",
    "VoV decrease",
    "VoV decrease rate",
    "FoM value",
    "FoM behaviour",
    "PDF slope",
]


class Output:
    def __init__(self, filepath: os.PathLike) -> None:
        """Object representing and MCNP output file

        Parameters
        ----------
        filepath : os.PathLike
            path to the output file to be parsed

        Attributes
        ----------
        filepath: os.PathLike
            path to the original output file
        name: str
            name of the original file
        lines: list[str]
            list of all the lines of the file

        Examples
        --------
        >>> from f4enix.output.MCNPoutput import Output
        ... # parse the output
        ... outp = Output('test.o')
        ... # print excel and .vtk file containing info on lost particles
        ... outp.print_lp_debug('outfile_name')
        ... # Get the results of the statistical checks for a specific tally
        ... outp.get_tally_stat_checks(46)
                                mean behaviour    rel error      rel error  ...
                                                    value         decrease  ...
        TFC bin behaviour
        desired                   random           <0.10               yes  ...
        observed                decrease            0.03               yes  ...
        passed?                       no             yes               yes  ...

        This tables are produced only if the bins have non-zero values and
        refer to the total bin. These results, combined with a summary check
        on all tally bins are used to compile the total summary table

        >>> # Get the total summary table
        ... outp.get_stat_checks_table()
                    mean            rel error                        TFC
                    behaviour        value          ...             bins
        Cell
        2              yes           yes            ...            Passed
        4              NaN           NaN            ...         All zeros
        6              NaN           NaN            ...         All zeros
        12             yes           yes            ...            Passed
        14             NaN           NaN            ...         All zeros
        24             NaN           NaN            ...         All zeros
        34             NaN           NaN            ...         All zeros
        22             yes           yes            ...            Passed
        32             yes           yes            ...            Passed
        44              no           yes            ...            Missed
        46              no           yes            ...            Missed
        104             no           yes            ...            Missed

        Get an MCNP table from the output file in a pandas DataFrame format:

        >>> outp.get_table(60)
                         cell	mat	  ... photon wt generation
        2	1.0	  1	     0	  ... 	-1.000E+00
        3	2.0	  2	     1	  ...	-1.000E+00
        4	3.0	  3	     0	  ...	-1.000E+00
        5	4.0	  4	     0	  ...	-1.000E+00
        """
        self.filepath = filepath
        self.name = os.path.basename(filepath).split(".")[0]
        logging.info("reading {} ...".format(self.name))
        self.lines = self._read_lines()
        logging.info("reading completed")

    def _read_lines(self) -> list[str]:
        lines = []
        with open(self.filepath, "r", errors="surrogateescape") as infile:
            for line in infile:
                lines.append(line)
        return lines

    def get_tot_lp(self) -> int:
        """Get the total lost particle number

        Returns
        -------
        int
            total lost particle number
        """
        lp = None
        for line in self.lines[::-1]:
            if TOTAL_LP in line:
                try:
                    lp = PAT_DIGIT.search(line).group()
                    return int(lp)
                except AttributeError:
                    # then the match was not found
                    logging.warning(
                        "The LP number was impossible to determine from this line '{}'".format(
                            line
                        )
                    )
                return None

        logging.warning("No identifier for lost particle was found in output")
        return None

    def get_NPS(self, particle: str = "neutron") -> int:
        """Get the number of particles simulated.

        Parameters
        ----------
        particle: str
            source particle to be looked for. The trigger for founding
        the correct table will be '{particle} creation'. The default is
        'neutron'.


        Returns
        -------
        int
            number of particles simulated
        """
        PAT_NPS_TRIGGER = re.compile(particle + " creation")
        for i, line in enumerate(self.lines):
            if PAT_NPS_TRIGGER.search(line) is not None:
                nps = int(PAT_DIGIT.search(self.lines[i + 3]).group())
                logging.info("NPS found: {}".format(nps))
                return nps

        raise ValueError("No NPS could be read from file")

    def print_lp_debug(
        self,
        outpath: os.PathLike,
        print_video: bool = False,
        get_cosine: bool = True,
        input_mcnp: Input = None,
    ) -> None:
        """prints both an excel ['LPdebug_{}.vtp'] and a vtk cloud point file
        ['LPdebug_{}.vtp'] containing information about the lost particles
        registered in an MCNP run. A .csv file is also printed with origin
        and flight direction of each lost particle.

        Parameters
        ----------
        outpath : os.PathLike
            path to the folder where outputs will be dumped.
        print_video : bool, optional
            if True print the LP to video. deafult is False
        get_cosine : bool, optional
            if True recover also the cosines of the flight direction of each
            lost particle. By default is True
        input_mcnp : Input, optional
            Input file that generated the MCNP output. Providing this will
            ensure that also the universe in which the particles are
            lost will be tracked. By default is None.
        """

        # -- Variables --
        surfaces = []
        cells = []
        universes = []
        x = []
        y = []
        z = []
        u = []
        v = []
        w = []

        logging.info("Recovering lost particles surfaces and cells in " + self.name)

        for i, line in enumerate(self.lines):

            if line.find(SURFACE_ID) != -1:  # LP in surface
                surfaces.append(PAT_DIGIT.search(line).group())

                cell_ID = PAT_DIGIT.search(self.lines[i + 1]).group()
                cells.append(cell_ID)
                # add the universe if requested
                if input_mcnp is not None:
                    universe = input_mcnp.cells[cell_ID].get_u()
                    universes.append(universe)

                point = SCIENTIFIC_PAT.findall(self.lines[i + 6])  # [0:3]
                cosines = SCIENTIFIC_PAT.findall(self.lines[i + 7])  # [0:3]
                x.append(float(point[0]))
                y.append(float(point[1]))
                z.append(float(point[2]))
                if get_cosine:
                    u.append(float(cosines[0]))
                    v.append(float(cosines[1]))
                    w.append(float(cosines[2]))

            # if line.find(CELL_ID) != -1 and input_mcnp is not None:
            #     # LP is in cell
            #     cells.append(PAT_DIGIT.search(line).group())

            # if line.find(POINT_ID) != -1:  # LP in cell
            #     point = SCIENTIFIC_PAT.findall(line)  # [0:3]
            #     x.append(float(point[0]))
            #     y.append(float(point[1]))
            #     z.append(float(point[2]))

            #     if '***' in self.lines[i-10]:
            #         gp = SCIENTIFIC_PAT.findall(self.lines[i-9])[0:3]
            #     else:
            #         gp = SCIENTIFIC_PAT.findall(self.lines[i-10])[0:3]
            #     try:
            #         gp[2]
            #         for i in range(len(gp)):
            #             gp[i] = gp[i][0:-3]+'E'+gp[i][-3:]
            #         gp = '   '.join(gp)
            #         globalpointList.append(gp)
            #     except:
            #         globalpointList.append('NO')

        # Don't do nothing if no particles are lost
        if len(surfaces) == 0:
            logging.info("No particles were lost, no dumps to be done")
            return

        # Building the df
        df = pd.DataFrame()
        df["Surface"] = surfaces
        df["Cell"] = cells
        df["x"] = x
        df["y"] = y
        df["z"] = z
        if get_cosine:
            df["u"] = u
            df["v"] = v
            df["w"] = w
        if len(universes) > 0:
            df["Universe"] = universes

        # Get a complete set of locations
        loc = df.drop_duplicates().set_index(["Surface", "Cell"]).sort_index()

        # Count multiple occasions
        df["count"] = 1
        global_df = df[["Cell", "Surface", "count"]]
        global_df = global_df.groupby(["Cell", "Surface"]).sum()
        global_df = global_df.sort_values(by="count", ascending=False)
        logging.debug("global df was built")

        # --- Printing to excel ---
        logging.info("printing to excel")

        # dump in the excel output
        filename = "LPdebug_{}.{}"
        outfile = os.path.join(outpath, filename.format(self.name, "xlsx"))
        with pd.ExcelWriter(outfile) as writer:
            # global df
            global_df.to_excel(writer, sheet_name="global")
            # loc.to_excel(writer, sheet_name='Locations')
            if input_mcnp is not None:
                logging.info("building universe df")
                u_df = df[["Universe", "Cell", "Surface", "count"]]
                u_df = u_df.groupby(["Universe", "Cell", "Surface"]).sum()
                u_df = u_df.sort_values(by="count", ascending=False)
                u_df.to_excel(writer, sheet_name="by universe")

        # Dump also a csv with only the data
        if get_cosine:
            cols = ["x", "y", "z", "u", "v", "w"]
        else:
            cols = ["x", "y", "z"]
        lp = df[cols]
        outfile = os.path.join(outpath, filename.format(self.name, "csv"))
        lp.to_csv(outfile, index=None)

        # visualize the cloud point
        logging.info("building the cloud point")
        point_cloud = pv.PolyData(loc[["x", "y", "z"]].values)

        if print_video:
            point_cloud.plot()

        outfile = os.path.join(outpath, filename.format(self.name, "vtp"))
        point_cloud.save(outfile)

        logging.info("dump completed")

    def get_statistical_checks_tfc_bins(self) -> dict[int, str]:
        """
        Retrieve the result of the 10 statistical checks for all tallies.
        They are registered as either 'Missed', 'Passed' or 'All zeros' in a
        dictionary indicized using the tallies numbers.

        Returns
        -------
        stat_checks : dict[int, str]
            keys are the tally numbers, values the result of the statistical
            checks.

        """
        # Some global key words and patterns
        start_stat_check = "result of statistical checks"
        miss = "missed"
        passed = "passed"
        allzero = "no nonzero"
        pat_tnumber = re.compile(r"\s*\t*\s*\d+")
        end = "the 10 statistical checks are only"

        # Recover statistical checks
        statcheck_flag = False
        stat_checks = {}
        for line in self.lines:
            if line.find(start_stat_check) != -1:
                statcheck_flag = True

            elif statcheck_flag:
                # Control if is a tally line
                tallycheck = pat_tnumber.match(line)
                if tallycheck is not None:
                    tnumber = int(tallycheck.group())
                    if line.find(miss) != -1:
                        result = "Missed"
                    elif line.find(passed) != -1:
                        result = "Passed"
                    elif line.find(allzero) != -1:
                        result = "All zeros"
                    else:
                        print("Warning: tally n." + str(tnumber) + " not retrieved")

                    stat_checks[tnumber] = result

                elif line.find(end) != -1:
                    # Exit from loop when all checks are read
                    break

        return stat_checks

    def get_tally_stat_checks(self, cell: int) -> pd.DataFrame:
        """Get the table of statistical checks for a specific tally

        Parameters
        ----------
        cell : int
            index of the cell to be parsed

        Returns
        -------
        pd.DataFrame
            table reporting the results of the statistical checks

        Raises
        ------
        ValueError
            if the cell is not found in the file.
        """
        trigger = re.compile(
            "           results of 10 statistical .+\s{}\n".format(cell)
        )
        found = False

        for i, line in enumerate(self.lines):
            if trigger.match(line):
                # found trigger
                found = True
                break
        if found:
            skiprows = i + 5
            nrows = 3
            # df = pd.read_csv(self.filepath, skiprows=skiprows, nrows=nrows,
            #                  header=None, sep=r'\s+')
            rows = []
            for i in range(nrows):
                line = self.lines[skiprows + i]
                rows.append(line.split())
            df = pd.DataFrame(rows)

            df.columns = STAT_CHECKS_COLUMNS
            df.set_index("TFC bin behaviour", inplace=True)

            # values for the pdf slopes are assigned wrongly to FoM
            for row in ["observed", "passed?"]:
                if pd.isna(df.loc[row, "PDF slope"]):
                    # pass the values to the correct columns
                    val = df.loc[row, "FoM value"]
                    df.loc[row, "FoM value"] = np.nan
                    df.loc[row, "PDF slope"] = val

                    if row == "passed?":
                        # assigned passed to the empty ones
                        df.loc[row, "FoM value"] = "yes"
                        df.loc[row, "FoM behaviour"] = "yes"

        else:
            raise ValueError("Cell {} was not found".format(cell))

        return df

    def get_stat_checks_table(self) -> pd.DataFrame:
        """get a table summarizing the 10 statisical checks results for each
        tally.

        one row per tally, one column per statistical check. An extra column
        is added that report the results of the statistical checks in all other
        TFC bins.

        Returns
        -------
        pd.DataFrame
            summary of the statistical checks results.
        """
        # get all available cells from the summary
        summary = self.get_statistical_checks_tfc_bins()
        rows = []
        for cell in list(summary.keys()):
            new_row = [int(cell)]
            try:
                table = self.get_tally_stat_checks(int(cell))
                new_row.extend(list(table.loc["passed?"].values))
            except ValueError as e:
                # If all bins have zero values it is expected not to find it
                if summary[cell] == "All zeros":
                    new_row.extend([np.nan] * 10)
                else:
                    # If they are not all zeros raise the exception
                    raise e
            rows.append(new_row)

        df = pd.DataFrame(rows)
        columns = ["Cell"]
        columns.extend(STAT_CHECKS_COLUMNS[1:])
        df.columns = columns
        df.set_index("Cell", inplace=True)
        df["Other TFC bins"] = pd.Series(summary)

        return df.sort_index()

    def get_table(self, table_num: int) -> pd.DataFrame:
        """Extract a printed table from the MCNP output file.

        All tables should be accessible from their MCNP index.

        Parameters
        ----------
        table_num : int
            MCNP table index

        Returns
        -------
        pd.DataFrame
            parsed table

        Raises
        ------
        ValueError
            If the table associated to the requested index is not found
        """
        pat_table = re.compile("table " + str(table_num))

        skip = None
        look_total = False
        nrows = None

        # look for the trigger
        for i, line in enumerate(self.lines):
            if look_total:
                if line.find("total") != -1:
                    # help inferring the columns width using the data,
                    # it is more reliable
                    infer_line = self.lines[i - 2]
                    widths = self._get_fwf_format_from_string(infer_line)
                    nrows = i - skip - 2
                    break

            if pat_table.search(line) is not None:
                skip = i + 1
                look_total = True

        if skip is None or nrows is None:
            raise ValueError("Table {} not found or does not exists".format(table_num))

        df = pd.read_fwf(
            self.filepath, skiprows=skip, nrows=nrows, widths=widths, header=None
        )
        # the first n rows will actually be the title of the columns.
        # Check the first column to understand where the data starts
        columns = []
        for i in range(10):
            if not pd.isna(df.iloc[i, 0]):
                break

            for j in range(df.shape[1]):
                current_val = df.iloc[i, j]
                try:
                    if pd.isna(current_val):
                        current_val = ""
                except TypeError:
                    current_val = ""

                if i == 0:
                    # append the first part of string
                    columns.append(current_val)
                else:
                    # concat to previous string
                    columns[j] = columns[j] + " " + current_val

        # delete the headers rows
        df = df.iloc[i:, :]
        # add proper column header
        df.columns = columns
        # delete empty columns if any
        df.dropna(axis=1, how="all", inplace=True)

        return df

    @staticmethod
    def _get_fwf_format_from_string(line: str) -> None:
        # This works only with data that has no space
        new_datum = False
        widths = []
        counter = 0

        for i, char in enumerate(line):

            if char == " " and new_datum is False:
                new_datum = True
                widths.append(counter)
                counter = 1
            else:
                counter = counter + 1
                if char != " ":
                    new_datum = False

        # At the end of the  cycle add last spec
        widths.append(counter)

        # exclude dummy at the beginning and \n bin created at end of line
        return widths[1:]

    def get_code_version(self):
        pat_d1s = re.compile(r"d1suned\s+version\s+\d+")
        pat_version = re.compile(r"(?<=version)\s+\d+")

        # there could be different scenarios. The easy one is that the version is
        # stated in the header of the output file
        # In case of D1SUNED
        for line in self.lines[:34]:
            if pat_d1s.search(line) is not None:
                version = pat_version.search(line).group().strip()
                return f"d1suned{version}"

        # In case of MCNP, it is in the first line
        pat_mcnp = re.compile(r"(?<=MCNP_)[\d.]+")
        if pat_mcnp.search(self.lines[0]) is not None:
            version = pat_mcnp.search(self.lines[0]).group().strip("0")
            return version

        # In case is not in the header (it happens on sbatch runs) try to look
        # in the same folder for a .out or .dump file
        pat_d1s = re.compile(r"(?<=d1suned  ver=)\d+")
        folder = os.path.dirname(self.filepath)
        for file in os.listdir(folder):
            if file.endswith(".out") or file.endswith(".dump"):
                with open(os.path.join(folder, file), "r", encoding="utf-8") as infile:
                    for line in infile:
                        if pat_d1s.search(line) is not None:
                            version = pat_d1s.search(line).group()
                            return f"d1suned{version}"
                        if pat_mcnp.search(line) is not None:
                            version = pat_mcnp.search(line).group().strip("0")
                            return version
                        break  # only the first line is needed

        return ValueError("No version was found in the output file or aux files")
