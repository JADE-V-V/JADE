from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from f4enix.output.MCNPoutput import Output
from f4enix.output.mctal import Mctal, Tally
from f4enix.output.meshtal import Meshtal
from f4enix.core.irradiation import TCF_Computer
from f4enix.core.irradiation import IrradiationScenario, Nuclide

from jade.helper.__optionals__ import OMC_AVAIL

if TYPE_CHECKING:
    from jade.helper.aux_functions import PathLike

if OMC_AVAIL:
    import jade.helper.openmc as omc

logger = logging.getLogger(__name__)


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
                try:
                    tallynum, tallydata1D, comment = msh.convert2tally()
                    # Add them to the tallly data
                    tallydata[tallynum] = tallydata1D
                    total_bin[tallynum] = None
                    # Create fake tallies to be added to the mctal
                    dummyTally = Tally(tallynum)
                    dummyTally.tallyComment = [comment]
                    self.mctal.tallies.append(dummyTally)
                except RuntimeError:
                    continue  # not a 1D mesh
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
            logger.warning(
                "Code version not found in the output file or aux file for %s",
                self.sim_folder,
            )
            logger.debug(
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

    @staticmethod
    def is_successfully_simulated(files: list[str]) -> bool:
        """Check if the simulation was successful by verifying output files exist."""
        mctal_found = False
        output_found = False
        for file in files:
            if file.endswith(".m"):
                mctal_found = True
            elif file.endswith(".o"):
                output_found = True
        return mctal_found and output_found


class OpenMCSimOutput(AbstractSimOutput):
    def __init__(
        self,
        sim_folder: PathLike,
    ) -> None:
        """
        Class representing all outputs coming from OpenMC run excluding Sphere

        Parameters
        ----------
        output_path : str | os.PathLike
            Path to simulation output files

        Returns
        -------
        None.

        """
        _, statefile, volfile, irr_scenario = self.retrieve_file(sim_folder)

        self.output = omc.OpenMCStatePoint(statefile, volfile)
        self._tally_numbers = self.output.tally_numbers
        self._tally_comments = self.output.tally_comments
        self._tallydata, self._totalbin = self._process_tally()
        self.stat_checks = None
        if irr_scenario:
            self.irr_scenario = IrradiationScenario.from_ascii(irr_scenario)
        else:
            self.irr_scenario = None

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
            elif file_name == "volumes.json":
                file3 = file_name
            elif file_name.endswith(".irr"):
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

    @staticmethod
    def is_successfully_simulated(files: list[str]) -> bool:
        """Check if the simulation was successful by verifying output files exist."""
        statepoint_found = False
        for file in files:
            if file.startswith("statepoint") and file.endswith(".h5"):
                statepoint_found = True
        return statepoint_found
    
    def _prep_tally(self, filter_lookup: dict[str, str], tally: pd.DataFrame) -> pd.DataFrame:
        '''
        Function to prepare the tally dataframe for JADE formatting, by renaming the columns and sorting by the filters.
        
        Parameters
        ----------
        filter_lookup : dict
            Dictionary to map OpenMC filter names to JADE column names
        tally : pd.DataFrame
            The OpenMC tally dataframe to be prepared for JADE formatting

        Returns
        -------
        sorted_tally : pd.DataFrame
            The sorted and renamed tally dataframe ready for JADE formatting

        '''
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
            (k, filter_lookup[k]) for k in filters if k in filter_lookup)
        new_columns["mean"] = filter_lookup["mean"]
        new_columns["std. dev."] = filter_lookup["std. dev."]
        sorted_tally = tally.sort_values(filters)
        sorted_tally = sorted_tally.reset_index(drop=True)
        sorted_tally = sorted_tally.rename(columns=new_columns)
        # remove constant columns
        sorted_tally = _remove_constant_columns(sorted_tally)
        return sorted_tally

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
            sorted_tally = self._prep_tally(filter_lookup, tally)
            
            if "Value" in sorted_tally.columns and "Error" in sorted_tally.columns:
                sorted_tally["Error"] = sorted_tally["Error"] / sorted_tally["Value"]
            
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
        if self.irr_scenario:
            tallydata = self._apply_tcf(tallydata)
        return tallydata, totalbin

    def _read_code_version(self) -> str | None:
        return self.output.version

    def _apply_tcf(self, data: dict[int, pd.DataFrame]) -> dict[int, pd.DataFrame]:
        """Use F4Enix to compute time correction factors and apply them to D1S
        calculations."""
        found = False
        tally_data = {}
        for key, df in data.items():
            if "parentnuclide" in df.columns:
                found = True
                df = df.set_index("parentnuclide")

                # Get the nuclides
                nuclides = []
                for nuclide in df["parentnuclide"]:
                    # Convert OpenMC metastables to F4Enix convention
                    nuclide = nuclide.replace("_m1", "m").replace("_m2", "m")
                    nuclides.append(Nuclide.from_formula(nuclide))

                assert self.irr_scenario is not None
                tcf_results = TCF_Computer().compute_correction_factors(
                    self.irr_scenario, nuclides, norm=1
                )
                tcf = pd.DataFrame(tcf_results)
                tcf.columns = [nuclide.write_to_formula() for nuclide in nuclides]
                tcf.index = self.irr_scenario.cooling_labels
                tcf = tcf.T

                tcf = tcf.mul(df["Value"], axis=0)
                tcf['Error'] = df['Error']  # Keep the original error column

                # and now melt it
                df = tcf.reset_index().melt(
                    id_vars=['index', 'Error'],
                    var_name='Time',
                    value_name='Value')
                df = df.rename(columns={'index': 'User'})

            tally_data[key] = df

        if not found:
            logger.warning(
                "No SDDR tallies found even if irradiation scenario is provided."
            )
        return data



class OpenMCSphereSimOutput(OpenMCSimOutput):
    def __init__(
        self,
        sim_folder: PathLike,
    ) -> None:
        """
        Class representing all outputs coming from OpenMC Sphere run

        Parameters
        ----------
        output_path : str | os.PathLike
            Path to simulation output files

        Returns
        -------
        None.

        """
        _, statefile, volfile, _ = self.retrieve_file(sim_folder)
        
        # Retrieving atomic density for normalisation of the DPA, He and T production tallies
        self.input = omc.OpenMCInputFiles(sim_folder)
        materials = self.input.geometry.get_all_materials()
        # There is only one material in the Sphere input so this is hard coded
        atomic_densities = materials[1].get_nuclide_atom_densities()
        self.atomic_density = sum(atomic_densities.values())

        super().__init__(sim_folder)

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
            sorted_tally = self._prep_tally(filter_lookup, tally)

            # If tally is Sphere, and is tally 14,24,34 then need to normalise by atomic density
            # Need to generate atomic density for a given Sphere input
            RR_tally_IDs = [14, 24, 34]
            if id in RR_tally_IDs:
                sorted_tally["Value"] = sorted_tally["Value"] / self.atomic_density
                sorted_tally["Error"] = sorted_tally["Error"] / self.atomic_density
            else:
                pass
            
            if "Value" in sorted_tally.columns and "Error" in sorted_tally.columns:
                sorted_tally["Error"] = sorted_tally["Error"] / sorted_tally["Value"]
            
            tallydata[id] = sorted_tally
            totalbin[id] = None
        return tallydata, totalbin

def _remove_constant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """eliminate unnecessary columns from OpenMC tally data"""
    # Drop constant axes (if len is > 1)
    if len(df) > 1:
        for column in df.columns:
            if column not in ["Value", "Error"]:
                firstval = df[column].values[0]
                # Should work as long as they are the exact same value
                allequal = (df[column] == firstval).all()
                if allequal:
                    del df[column]
    else:
        # Drop all but the first column
        for column in df.columns:
            if column not in ["Value", "Error"]:
                # Should work as long as they are the exact same value
                del df[column]
    return df
