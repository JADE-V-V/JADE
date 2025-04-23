from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from f4enix.output.MCNPoutput import Output
from f4enix.output.mctal import Mctal, Tally
from f4enix.output.meshtal import Fmesh1D, Meshtal

from jade.helper.__openmc__ import OMC_AVAIL

if TYPE_CHECKING:
    from jade.helper.aux_functions import PathLike

if OMC_AVAIL:
    import jade.helper.openmc as omc


class AbstractSimOutput(ABC):
    def __init__(self, sim_folder: PathLike) -> None:
        """
        This object (and its children) need to parse the simulation outputs for the
        different codes.

        Parameters
        ----------
        sim_folder : PathLike
            Path to the simulation folder containing the output files.
        """
        self.sim_folder = sim_folder
        self.code_version = self._read_code_version()

    @property
    @abstractmethod
    def tallydata(self) -> dict[int, pd.DataFrame]:
        """This contains for each tally in the simulation the data in a pandas DataFrame.

        Returns
        -------
        dict[str, pd.DataFrame]
            Dictionary of tally dataframes, indexed by tally number.
        """
        pass

    @property
    @abstractmethod
    def totalbin(self) -> dict[int, pd.DataFrame]:
        """This contains for each tally in the simulation the total bin data in a pandas
        DataFrame.

        Returns
        -------
        dict[str, pd.DataFrame]
            Dictionary of total tally dataframes, indexed by tally number.
        """

    @property
    @abstractmethod
    def tally_numbers(self) -> list[int]:
        """This contains the tally numbers in the simulation.

        Returns
        -------
        list[int]
            List of tally numbers.
        """
        pass

    @property
    @abstractmethod
    def tally_comments(self) -> list[str]:
        """This contains the tally comments in the simulation.

        Returns
        -------
        list[str]
            List of tally comments.
        """
        pass

    @abstractmethod
    def _read_code_version(self) -> str:
        """Read the code version used for the simulation.

        Returns
        -------
        str
            The code version.
        """
        pass


class MCNPSimOutput(AbstractSimOutput):
    def __init__(
        self,
        sim_folder: PathLike,
    ) -> None:
        """
        Class parsing all outputs coming from MCNP run

        Parameters
        ----------
        sim_folder : PathLike

        Returns
        -------
        None.

        """
        self.sim_folder = sim_folder
        mctal_file, output_file, meshtal_file = self.retrieve_files(sim_folder)

        # Read and parse the mctal file
        mctal = Mctal(mctal_file)
        # --- restore cabability to collapse segment and cells ---
        # The double binning Surfaces/cells with segments can create
        # issues for JADE since if another binning is added
        # (such as energy) it is not supported. Nevertheless,
        # the additional segmentation can be quite useful and this can be
        # collapsed de facto in a single geometrical binning
        tallydata = mctal.tallydata
        total_bin = mctal.totalbin
        for dictionary in [tallydata, total_bin]:
            for _, df in dictionary.items():
                if df is not None:
                    if (
                        "Cells" in df.columns
                        and "Segments" in df.columns
                        and len(df) > 1
                    ):
                        # Then we can collapse this in a single geometrical binning
                        values = []
                        for cell, segment in zip(df.Cells, df.Segments):
                            val = str(int(cell)) + "-" + str(int(segment))
                            values.append(val)
                        df["Cells-Segments"] = values
                        # delete the collapsed columns
                        del df["Cells"]
                        del df["Segments"]

                    # another thing that can happen mostly for d1s is that there
                    # are user bins with fake total bin, i.e., there is only one bin
                    # and a total bin having the same value. This is a problem
                    # since f4enix parser will not drop the "fake" additional column
                    try:
                        usr_bins = set(df["User"].to_list())
                        if len(usr_bins) <= 2 and "total" in usr_bins:
                            # then the column does not add any additional info, to drop
                            del df["User"]
                            # and drop the duplicates ignoring the warning
                            with pd.option_context("mode.chained_assignment", None):
                                df.drop_duplicates(inplace=True)
                    except KeyError:
                        pass  # no user column

        self.mctal = mctal
        self._tally_numbers = []
        self._tally_comments = []
        # Read the output file
        self.out = Output(output_file)
        stat_checks = self.out.get_statistical_checks_tfc_bins()
        self.stat_checks = self.out.assign_tally_description(
            stat_checks, self.mctal.tallies
        )
        # Read the meshtal file
        if meshtal_file is not None:
            self.meshtal = Meshtal(meshtal_file)
            self.meshtal.readMesh()
            # Extract the available 1D to be merged with normal tallies
            for msh in self.meshtal.mesh.values():
                if isinstance(msh, Fmesh1D):
                    tallynum, tallydata1D, comment = msh.convert2tally()
                    # Add them to the tallly data
                    tallydata[tallynum] = tallydata1D
                    total_bin[tallynum] = None
                    # Create fake tallies to be added to the mctal
                    dummyTally = Tally(tallynum)
                    dummyTally.tallyComment = [comment]
                    self.mctal.tallies.append(dummyTally)
                else:
                    continue
        for tally in self.mctal.tallies:
            self._tally_numbers.append(tally.tallyNumber)
            if len(tally.tallyComment) > 0:
                self._tally_comments.append(tally.tallyComment[0])
            else:
                self._tally_comments.append("")

        for df in tallydata.values():
            # drop a row if it contains total in whatever column
            if "total" in df.values:
                df.drop(
                    df[
                        df.apply(
                            lambda row: row.astype(str).str.contains("total").any(),
                            axis=1,
                        )
                    ].index,
                    inplace=True,
                )

        self._tallydata = tallydata
        self._totalbin = total_bin

    @property
    def tallydata(self) -> dict[int, pd.DataFrame]:
        return self._tallydata

    @property
    def totalbin(self) -> dict[int, pd.DataFrame]:
        return self._totalbin

    @property
    def tally_numbers(self) -> list[int]:
        return self._tally_numbers

    @property
    def tally_comments(self) -> list[str]:
        return self._tally_comments

    def _read_code_version(self) -> str | None:
        try:
            version = self.out.get_code_version()
            return version
        except ValueError:
            logging.warning(
                "Code version not found in the output file or aux file for %s",
                self.sim_folder,
            )
            logging.debug(
                "Contents of the directory: %s",
                os.listdir(os.path.dirname(self.sim_folder)),
            )
            return None

    @staticmethod
    def retrieve_files(results_path: PathLike) -> tuple[Path, Path, Path | None]:
        file1 = None
        file2 = None
        file3 = None

        for file_name in os.listdir(results_path):
            if file_name.endswith(".m"):
                file1 = file_name
            elif file_name.endswith(".o"):
                file2 = file_name
            elif file_name.endswith(".msht"):
                file3 = file_name

        if file1 is None or file2 is None:
            raise FileNotFoundError(
                f"The following path does not contain the required files for MCNP output: {results_path}"
            )

        mctal = Path(results_path, file1)
        outp = Path(results_path, file2)
        meshtal = Path(results_path, file3) if file3 else None

        return mctal, outp, meshtal


class OpenMCSimOutput(AbstractSimOutput):
    def __init__(
        self,
        sim_folder: PathLike,
    ) -> None:
        """
        Class representing all outputs coming from OpenMC run

        Parameters
        ----------
        output_path : str | os.PathLike
            Path to simulation output files

        Returns
        -------
        None.

        """
        outfile, statefile, tffile, volfile = self.retrieve_file(sim_folder)

        self.output = omc.OpenMCStatePoint(statefile, tffile, volfile)
        self._tally_numbers = self.output.tally_numbers
        self._tally_comments = self.output.tally_comments
        self._tallydata, self._totalbin = self._process_tally()
        self.stat_checks = None

    @property
    def tally_numbers(self) -> list[int]:
        return self._tally_numbers

    @property
    def tally_comments(self) -> list[str]:
        return self._tally_comments

    @property
    def tallydata(self) -> dict[int, pd.DataFrame]:
        return self._tallydata

    @property
    def totalbin(self) -> dict[int, pd.DataFrame]:
        return self._totalbin

    @staticmethod
    def retrieve_file(
        results_path: PathLike,
    ) -> tuple[PathLike, PathLike, PathLike | None, PathLike | None]:
        file1 = None
        file2 = None
        file3 = None
        file4 = None

        for file_name in os.listdir(results_path):
            if file_name.endswith(".out"):
                file1 = file_name
            elif file_name.startswith("statepoint"):
                file2 = file_name
            elif file_name.endswith(".yaml"):
                file3 = file_name
            elif file_name == "volumes.json":
                file4 = file_name

        if file1 is None or file2 is None:
            raise FileNotFoundError(
                f"The following path does not contain the required files for OpenMC output: {results_path}"
            )

        file1 = os.path.join(results_path, file1)
        file2 = os.path.join(results_path, file2)
        file3 = os.path.join(results_path, file3) if file3 else None
        file4 = os.path.join(results_path, file4) if file4 else None

        return file1, file2, file3, file4

    def _create_dataframes(
        self, tallies: dict
    ) -> tuple[dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
        """
        Function to create dataframes in JADE format from OpenMC dataframes.

        Parameters
        ----------
        tallies : dict
            Dictionary of OpenMC tally dataframes, indexed by tally number

        Returns
        -------
        tallydata : dict[int, pd.DataFrame]
            Dictionary of JADE formatted tally dataframes, indexed by tally number
        totalbin : dict[int, None]]
            Dictionary of JADE formatted total tally values, each are None for OpenMC
        """
        tallydata = {}
        totalbin = {}
        filter_lookup = {
            "cell": "Cells",
            "surface": "Segments",
            "energy high [eV]": "Energy",
            "time": "Time",
            "mean": "Value",
            "std. dev.": "Error",
        }
        columns = [
            "Cells",
            "User",
            "Segments",
            "Cosine",
            "Energy",
            "Time",
            "Cor C",
            "Cor B",
            "Cor A",
            "Value",
            "Error",
        ]
        for id, tally in tallies.items():
            filters = []
            new_columns = {}
            if "cell" in tally.columns:
                filters.append("cell")
            if "surface" in tally.columns:
                filters.append("surface")
            if "energy high [eV]" in tally.columns:
                filters.append("energy high [eV]")
            if "time" in tally.columns:
                filters.append("time")
            new_columns = dict(
                (k, filter_lookup[k]) for k in filters if k in filter_lookup
            )
            new_columns["mean"] = filter_lookup["mean"]
            new_columns["std. dev."] = filter_lookup["std. dev."]
            sorted_tally = tally.sort_values(filters)
            sorted_tally = sorted_tally.reset_index(drop=True)
            sorted_tally = sorted_tally.rename(columns=new_columns)
            # selected_columns = []
            # for column in columns:
            #     if (
            #         column in sorted_tally.columns
            #         and sorted_tally[column].nunique() != 1
            #     ):
            #         selected_columns.append(column)
            
            # sorted_tally = sorted_tally[selected_columns]
            # sorted_tally.to_csv('tally_'+str(id)+'_sorted.csv')
            tallydata[id] = sorted_tally
            totalbin[id] = None
        return tallydata, totalbin

    def _process_tally(self) -> tuple[dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
        """
        Function to retrieve OpenMC tally dataframes, and re-format for JADE.

        Returns
        -------
        tallydata : dict[int, pd.DataFrame]
            Dictionary of JADE formatted tally dataframes, indexed by tally number
        totalbin : dict[int, None]]
            Dictionary of JADE formatted total tally values, each are None for OpenMC
        """
        tallies = self.output.tallies_to_dataframes()
        tallydata, totalbin = self._create_dataframes(tallies)
        return tallydata, totalbin

    def _read_code_version(self) -> str | None:
        return self.output.version
