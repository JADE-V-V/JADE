from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from jade.helper.__openmc__ import OMC_AVAIL

if OMC_AVAIL:
    import openmc
import pandas as pd
import yaml

if TYPE_CHECKING:
    from f4enix.input.libmanager import LibManager
    from f4enix.input.materials import MatCardsList, Material, SubMaterial, Zaid

    from jade.helper.aux_functions import PathLike

PAT_DIGITS = re.compile(r'\d+')

@dataclass
class OpenMCTallyFactors:
    """Configuration for a computational benchmark.

    Attributes
    ----------
    tally_factors : dict[int, TallyFactors]
        Options for the Excel benchmark.
    """

    tally_factors: dict[int, TallyFactors]

    @classmethod
    def from_yaml(cls, file: str | os.PathLike) -> OpenMCTallyFactors:
        """Build the configuration for a computational benchmark from a yaml file.

        Parameters
        ----------
        file : str | os.PathLike
            path to the yaml file.

        Returns
        -------
        OpenMCTallyFactors
            The tally factors for the OpenMC benchmark.
        """
        with open(file) as f:
            cfg = yaml.safe_load(f)

        tally_factors = {}
        for key, value in cfg.items():
            tally_factors[int(key)] = TallyFactors(**value, identifier=int(key))
        return cls(tally_factors=tally_factors)


@dataclass
class TallyFactors:
    """Data class storing tally factors

    Attributes
    ----------
    identifier : int
        Identifier of the tally.
    normalisation : float
        Normalisation factor for the tally.
    volume : bool
        True if volume divisor is needed, False if not. Default is False.
    mass : BinningType | list[BinningType]
        True if mass divisor is needed, False if not. Default is False.
    """

    identifier: int
    volume: bool = False
    mass: bool = False
    normalisation: float = 1


@dataclass
class OpenMCCellVolumes:
    """Configuration for a computational benchmark.

    Attributes
    ----------
    cell_volumes : dict[int, float]
        Dictionary of cell volumes
    """

    cell_volumes: dict[int, float]

    @classmethod
    def from_json(cls, file: str | os.PathLike) -> OpenMCCellVolumes:
        """Load in cell volumes from a json file.

        Parameters
        ----------
        file : str | os.PathLike
            path to the json file.

        Returns
        -------
        OpenMCCellVolumes
            The cell volumes for the OpenMC benchmark.
        """
        with open(file) as f:
            cfg = json.load(f)

        cell_volumes = {}
        for key, value in cfg["cells"].items():
            cell_volumes[int(key)] = float(value)
        return cls(cell_volumes=cell_volumes)

    def volumes(self, cells: iter | None = None) -> dict[int, float]:
        """
        Returns dictionary of volumes for a cell list

        Returns
        -------
        volumes : dict
            Dictionary of volumes, indexed by cell number
        """
        volumes = dict(
            (k, self.cell_volumes[k]) for k in cells if k in self.cell_volumes
        )
        return volumes


@dataclass
class OpenMCCellDensities:
    """Configuration for a computational benchmark.

    Attributes
    ----------
    cell_volumes : dict[int, float]
        Dictionary of cell volumes
    """

    cell_densities: dict[int, float]

    @classmethod
    def from_xml(cls, xml_path: str | os.PathLike) -> OpenMCCellDensities:
        """Load in cell densities from the geometry xml input file.

        Parameters
        ----------
        xml_path : str | os.PathLike
            path to the xml input files

        Returns
        -------
        OpenMCCellDensities
            The cell densities for the OpenMC benchmark.
        """
        omc_input_files = OpenMCInputFiles(xml_path)
        cells = omc_input_files.geometry.get_all_cells()
        cell_densities = {}
        for cell_number, cell in cells.items():
            materials = cell.get_all_materials()
            if len(materials) == 1:
                for material in materials.values():
                    cell_densities[int(cell_number)] = material.get_mass_density()
        return cls(cell_densities=cell_densities)

    def densities(self, cells: iter | None = None) -> dict[int:float]:
        """
        Returns dictionary of densities for a cell list

        Returns
        -------
        densities : dict
            Dictionary of densities in g/cm3, indexed by cell number
        """
        densities = dict(
            (k, self.cell_densities[k]) for k in cells if k in self.cell_densities
        )
        return densities


class OpenMCInputFiles:
    def __init__(self, path: PathLike, name=None) -> None:
        """Class to handle the OpenMC input file generation

        Parameters
        ----------
        path : str
            path to input files
        name : str, optional
            name associated with the input file, by default None

        Returns
        -------
        None
        """
        self.path = path
        self.name = name
        self.initialise(path)

    def initialise(self, path: str) -> None:
        """Initialise OpenMC input files from xml

        Parameters
        ----------
        path : str
            path to input file destination

        Returns
        -------
        None
        """
        files = os.listdir(path)
        if ("geometry.xml" in files) and ("materials.xml") in files:
            self.load_geometry(
                os.path.join(path, "geometry.xml"),
                materials=os.path.join(path, "materials.xml"),
            )
        else:
            self.geometry = openmc.Geometry()
            self.materials = openmc.Materials()
        if "settings.xml" in files:
            self.load_settings(os.path.join(path, "settings.xml"))
        if "tallies.xml" in files:
            self.load_tallies(os.path.join(path, "tallies.xml"))
        else:
            self.tallies = openmc.Tallies()

    def load_geometry(
        self,
        geometry: str | os.PathLike,
        materials: openmc.Materials | str | os.PathLike,
    ) -> None:
        """Initialise OpenMC geometry from xml

        Parameters
        ----------
        geometry : str
            path to geometry input xml
        materials : str
            path to materials input xml, or openmc.Materials object

        Returns
        -------
        None
        """
        self.geometry = openmc.Geometry.from_xml(geometry, materials)
        if type(materials) is not openmc.Materials:
            self.materials = openmc.Materials.from_xml(materials)

    def load_settings(self, settings: str) -> None:
        """Initialise OpenMC settings from xml

        Parameters
        ----------
        settings : str
            path to settings input xml

        Returns
        -------
        None
        """
        self.settings = openmc.Settings.from_xml(settings)

    def load_tallies(self, tallies: str) -> None:
        """Initialise OpenMC tallies from xml

        Parameters
        ----------
        talllies : str
            path to geometry input xml

        Returns
        -------
        None
        """
        self.tallies = openmc.Tallies.from_xml(tallies)

    def add_stopCard(self, nps: int, batches: int = 100) -> None:
        """Add number of particles to simulate

        Parameters
        ----------
        nps : int
            number of particles to simulate
        batches : int, optional
            number of batches, by default 100

        Returns
        -------
        None
        """
        if nps < batches:
            batches = nps

        self.settings.batches = batches
        self.settings.particles = int(nps / batches)

    @staticmethod
    def zaid_to_openmc(
        zaid: Zaid, openmc_material: openmc.Material, libmanager: LibManager
    ) -> None:
        """Convert Zaid to OpenMC format with atom or weight fraction

        Parameters
        ----------
        zaid : str
            Zaid to be added to the OpenMC material
        openmc_material : openmc.Material
            An instance of the OpenMC Material class representing the material used in the simulation.

        Returns
        -------
        None
        """
        nuclide = zaid.get_fullname(libmanager).replace("-", "")
        # if no istope number is in the nuclide, a zero needs to be added
        if PAT_DIGITS.search(nuclide) is None:
            nuclide = nuclide + '0'
        if zaid.fraction < 0.0:
            openmc_material.add_nuclide(nuclide, 100 * abs(zaid.fraction), "wo")
        else:
            openmc_material.add_nuclide(nuclide, 100 * abs(zaid.fraction), "ao")

    def submat_to_openmc(
        self,
        submaterial: SubMaterial,
        openmc_material: openmc.Material,
        libmanager: LibManager,
    ) -> None:
        """Handle submaterials in OpenMC

        Parameters
        ----------
        submaterial : SubMaterial
            An instance of the SubMaterial class representing a subcomponent of a material.
            It contains elements, each of which has ZAIDs (nuclide identifiers).
        openmc_material : openmc.Material
            An instance of the OpenMC Material class representing the material used in the simulation.
        libmanager : libmanager.LibManager
            An instance of the LibManager class responsible for managing external libraries.

        Returns
        -------
        None
        """
        for elem in submaterial.elements:
            for zaid in elem.zaids:
                self.zaid_to_openmc(zaid, openmc_material, libmanager)

    def mat_to_openmc(self, material: Material, libmanager: LibManager) -> None:
        """Convert a material to an OpenMC material and handle its submaterials.

        Parameters
        ----------
        material : Material
            An instance of the Material class representing the material to be converted.
        libmanager : LibManager
            An instance of the LibManager class responsible for managing external libraries.

        Returns
        -------
        None
        """
        matid = int(re.sub("[^0-9]", "", str(material.name)))
        matname = str(material.name)
        matdensity = abs(material.density)
        if material.density < 0:
            density_units = "g/cc"
        else:
            raise ValueError('Density should be provided negative (mass)')
        openmc_material = openmc.Material(matid, name=matname)
        openmc_material.set_density(density_units, matdensity)
        if material.submaterials is not None:
            for submaterial in material.submaterials:
                self.submat_to_openmc(submaterial, openmc_material, libmanager)
        self.materials.append(openmc_material)

    def matlist_to_openmc(self, matlist: MatCardsList, libmanager: LibManager) -> None:
        """Convert a list of materials to OpenMC materials and load the geometry.

        Parameters
        ----------
        matlist : MatCardsList
            A list of Material instances to be converted. Each material should have the necessary
            attributes required by the mat_to_openmc method.
        libmanager : LibManager
            An instance of the LibManager class responsible for managing external libraries.

        Returns
        -------
        None
        """
        for material in matlist:
            self.mat_to_openmc(material, libmanager)
        self.load_geometry(os.path.join(self.path, "geometry.xml"), self.materials)

    def write(self, path: PathLike) -> None:
        """Write OpenMC input files to xml

        Parameters
        ----------
        path : str
            path to input file destination

        Returns
        -------
        None
        """
        self.geometry.export_to_xml(os.path.join(path, "geometry.xml"))
        self.settings.export_to_xml(os.path.join(path, "settings.xml"))
        self.tallies.export_to_xml(os.path.join(path, "tallies.xml"))
        self.materials.export_to_xml(os.path.join(path, "materials.xml"))


class OpenMCStatePoint:
    def __init__(
        self,
        spfile_path: str | os.PathLike,
        tffile_path: str | os.PathLike | None = None,
        volfile_path: str | os.PathLike | None = None,
    ) -> None:
        """Class for handling OpenMC statepoint file

        Parameters
        ----------
        spfile_path : str
            path to statepoint file
        """
        self.initialise(spfile_path, tffile_path, volfile_path)
        self.version = self.read_openmc_version()

    def initialise(
        self,
        spfile_path: str | os.PathLike,
        tffile_path: str | os.PathLike | None,
        volfile_path: str | os.PathLike | None,
    ) -> None:
        """Read in statepoint file

        Parameters
        ----------
        spfile_path : str
            path to statepoint file
        """
        try:
            # Retrieve the version from the statepoint file (convert from tuple of integers to string)
            self.results_path = os.path.dirname(spfile_path)
            self.statepoint = openmc.StatePoint(spfile_path)
            self.tally_numbers = []
            self.tally_comments = []
            for _, tally in self.statepoint.tallies.items():
                self.tally_numbers.append(tally.id)
                self.tally_comments.append(tally.name)
        except (FileNotFoundError, KeyError):
            logging.warning(
                "OpenMC version not found in the statepoint file for %s",
                spfile_path,
            )
        try:
            self.tally_factors = OpenMCTallyFactors.from_yaml(tffile_path)
        except (FileNotFoundError, TypeError):
            logging.warning(
                "OpenMC tally factor file not found for %s",
                tffile_path,
            )
            self.tally_factors = None
        try:
            self.cell_volumes = OpenMCCellVolumes.from_json(volfile_path)
        except (FileNotFoundError, TypeError):
            logging.warning(
                "OpenMC volume file not found for %s",
                volfile_path,
            )
            self.cell_volumes = None
        try:
            self.cell_densities = OpenMCCellDensities.from_xml(self.results_path)
        except FileNotFoundError:
            logging.warning(
                "OpenMC xml files not found for %s",
                self.results_path,
            )
            self.cell_densities = None

    def read_openmc_version(self) -> str:
        """Get OpenMC version from statepoint file

        Returns
        -------
        str
            OpenMC version
        """
        version = ".".join(map(str, self.statepoint.version))
        return version

    def _update_tally_numbers(self, tally_numbers: list) -> None:
        """Update tally numbers

        Parameters
        ----------
        tally_numbers : list
            List of remaining tally numbers
        """
        for tally_number in self.tally_numbers:
            if tally_number not in tally_numbers:
                idx = self.tally_numbers.index(tally_number)
                del self.tally_comments[idx]
                del self.tally_numbers[idx]

    def _normalise_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """_summary_

        Parameters
        ----------
        df : pd.DataFrame
            Input data frame to be normalised

        Returns
        -------
        df : pd.DataFrame
            Input data frame, all eV quantities scaled to MeV
        """
        for column in df.columns:
            if "[eV]" in column:
                df[column] *= 1e-6
        if ("heating" or "damage-energy") in df["score"].values:
            df["mean"] = np.where(
                (df["score"] == "heating") | (df["score"] == "damage-energy"),
                1e-6 * df["mean"],
                df["mean"],
            )
            df["std. dev."] = np.where(
                (df["score"] == "heating") | (df["score"] == "damage-energy"),
                1e-6 * df["std. dev."],
                df["std. dev."],
            )
        return df

    def _get_tally_data(self, tally: openmc.Tally):
        """Extract tally data from statepoint file

        Parameters
        ----------
        tally : openmc.Tally
            openmc tally

        Returns
        -------
        df : pd.DataFrame
            pandas dataframe containing tally data re-normlaised to MCNP default units
        """
        df = tally.get_pandas_dataframe()
        df = self._normalise_df(df)
        return df

    def _combine_heating_tallies(self, heating_tallies: dict) -> dict:
        """Extract tally data from statepoint file

        Parameters
        ----------
        tallies : dict
            Dictionary containing all OpenMC heating tallies

        Returns
        -------
        heating_tallies_df : dict
            dictionary of pandas dataframes containing combined tally data
        """
        photon_tallies = {}
        heating_tallies_df = {}
        for id, tally in heating_tallies.items():
            particle_filter = tally.find_filter(openmc.ParticleFilter)
            if "neutron" in particle_filter.bins:
                heating_tallies_df[id] = self._get_tally_data(tally)
            if "photon" in particle_filter.bins:
                photon_tallies[id] = tally
                heating_tallies_df[id] = self._get_tally_data(tally)
        for id, photon_tally in photon_tallies.items():
            photon_cell_filter = photon_tally.find_filter(openmc.CellFilter)
            for _, tally in heating_tallies.items():
                particle_filter = tally.find_filter(openmc.ParticleFilter)
                cell_filter = tally.find_filter(openmc.CellFilter)
                if (
                    ("electron" in particle_filter.bins)
                    or ("positron" in particle_filter.bins)
                ) and (photon_cell_filter == cell_filter):
                    tally_df = self._get_tally_data(tally)
                    heating_tallies_df[id]["mean"] += tally_df["mean"]
                    heating_tallies_df[id]["std. dev."] = (
                        heating_tallies_df[id]["std. dev."].pow(2)
                        + tally_df["std. dev."].pow(2)
                    ).pow(0.5)
        return heating_tallies_df

    def _get_volumes(self, tally_df: pd.DataFrame) -> dict[int, float]:
        """
        Function to extract unique cell volumes from tally dataframe

        Parameters
        ----------
        tally_df : pd.DataFrame
            Pandas DataFrame containing tally data

        Returns
        -------
        volumes : dict[int, float]
            Dictionary of cell volumes, indeced by cell
        """
        cells = tally_df.cell.unique()
        volumes = self.cell_volumes.volumes(cells)
        return volumes

    def _get_masses(self, tally_df: pd.DataFrame) -> dict[int, float]:
        """
        Function to extract unique cell masses from tally dataframe

        Parameters
        ----------
        tally_df : pd.DataFrame
            Pandas DataFrame containing tally data

        Returns
        -------
        masses : dict[int, float]
            Dictionary of cell volumes, indeced by cell
        """
        volumes = self._get_volumes(tally_df)
        masses = {}
        for cell, volume in volumes.items():
            density = self.cell_densities.cell_densities[cell]
            masses[cell] = density * volume
        return masses

    def _apply_tally_factors(self, tallies: dict) -> dict:
        """
        Function to apply tally factor and volume corrections to tally data

        Parameters
        ----------
        tallies : dict
            Dictionary of tallies to be corrected

        Returns
        -------
        tallies : dict
            Dictionary of tallies with tally factors applied
        """
        for tally_number, tally_df in tallies.items():
            if tally_number in self.tally_factors.tally_factors:
                normalisation = self.tally_factors.tally_factors[
                    tally_number
                ].normalisation
                tally_df["mean"] *= normalisation
                tally_df["std. dev."] *= normalisation
                if self.tally_factors.tally_factors[tally_number].volume:
                    volumes = self._get_volumes(tally_df)
                    for cell, volume in volumes.items():
                        tally_df["mean"] = np.where(
                            (tally_df["cell"] == cell),
                            tally_df["mean"] / volume,
                            tally_df["mean"],
                        )
                        tally_df["std. dev."] = np.where(
                            (tally_df["cell"] == cell),
                            tally_df["std. dev."] / volume,
                            tally_df["std. dev."],
                        )
                if self.tally_factors.tally_factors[tally_number].mass:
                    masses = self._get_masses(tally_df)
                    for cell, mass in masses.items():
                        tally_df["mean"] = np.where(
                            (tally_df["cell"] == cell),
                            tally_df["mean"] / mass,
                            tally_df["mean"],
                        )
                        tally_df["std. dev."] = np.where(
                            (tally_df["cell"] == cell),
                            tally_df["std. dev."] / mass,
                            tally_df["std. dev."],
                        )
            tallies[tally_number] = tally_df
        return tallies

    def tallies_to_dataframes(self) -> dict:
        """Call to extract tally data from statepoint file

        Returns
        -------
        tallies : dict
            dictionary of dataframes containing all tally data
        """
        tallies = {}
        heating_tallies = {}
        for _, tally in self.statepoint.tallies.items():
            if "heating" in tally.scores:
                heating_tallies[tally.id] = tally
            else:
                tallies[tally.id] = self._get_tally_data(tally)
        heating_tallies_df = self._combine_heating_tallies(heating_tallies)
        if len(heating_tallies_df) > 0:
            for id, tally_df in heating_tallies_df.items():
                tallies[id] = tally_df
        self._update_tally_numbers(tallies.keys())
        if self.tally_factors is not None:
            tallies = self._apply_tally_factors(tallies)
        return tallies


class OpenMCSphereStatePoint(OpenMCStatePoint):
    def __init__(self, spfile_path: str) -> None:
        """Class to handle the data extraction of the Sphere leakage benchmark in OpenMC

        Parameters
        ----------
        spfile_path : str
            path to statepoint file
        """
        super().__init__(spfile_path)

    def _get_tally_data(self, rows: list, filter: openmc.Filter) -> list:
        """Extract tally data from statepoint file

        Parameters
        ----------
        rows : list
            list of rows to append tally data to
        filter : openmc.Filter
            determines OpenMC tally type

        Returns
        -------
        list
            list of rows with tally data appended
        """
        tally = self.statepoint.get_tally(filters=[filter])
        tally_n = tally.id
        tally_description = tally.name.title()
        energy_bins = tally.find_filter(openmc.EnergyFilter).values[1:]
        fluxes = tally.mean.flatten()
        errors = tally.std_dev.flatten()
        for energy, flux, error in zip(energy_bins, fluxes, errors):
            rows.append([tally_n, tally_description, energy, flux, error])
        return rows

    def tally_to_rows(self) -> list:
        """Call to extract tally data from statepoint file

        Returns
        -------
        list
            list of rows with all sphere case tally data
        """
        rows = []
        neutron_particle_filter = openmc.ParticleFilter(["neutron"])
        rows = self._get_tally_data(rows, neutron_particle_filter)
        photon_particle_filter = openmc.ParticleFilter(["photon"])
        rows = self._get_tally_data(rows, photon_particle_filter)
        return rows
