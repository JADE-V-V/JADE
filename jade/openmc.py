import logging
import os
import re
import openmc


class OpenMCInputFiles:
    def __init__(self, path: str, name=None) -> None:
        self.path = path
        self.name = name
        self.initialise(path)

    def initialise(self, path: str) -> None:
        """Initialise OpenMC input files from xml

        Parameters
        ----------
        path : str
            path to input file destination
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

    def load_geometry(self, geometry: str, materials) -> None:
        """Initialise OpenMC geometry from xml

        Parameters
        ----------
        geometry : str
            path to geometry input xml
        materials : str
            path to materials input xml, or openmc.Materials object
        """
        self.geometry = openmc.Geometry.from_xml(geometry, materials)

    def load_settings(self, settings: str) -> None:
        """Initialise OpenMC settings from xml

        Parameters
        ----------
        settings : str
            path to geometry input xml
        """
        self.settings = openmc.Settings.from_xml(settings)

    def load_tallies(self, tallies: str) -> None:
        """Initialise OpenMC tallies from xml

        Parameters
        ----------
        talllies : str
            path to geometry input xml
        """
        self.tallies = openmc.Tallies.from_xml(tallies)

    def add_stopCard(self, nps: int, batches=100) -> None:
        """Add number of particles to simulate

        Parameters
        ----------
        nps : int
            number of particles to simulate
        """
        if nps < batches:
            batches = nps

        self.settings.batches = batches
        self.settings.particles = int(nps / batches)

    def zaid_to_openmc(self, zaid, openmc_material, libmanager):
        nuclide = zaid.get_fullname(libmanager).replace("-", "")
        if zaid.fraction < 0.0:
            openmc_material.add_nuclide(nuclide, 100 * abs(zaid.fraction), "wo")
        else:
            openmc_material.add_nuclide(nuclide, 100 * abs(zaid.fraction), "ao")

    def submat_to_openmc(self, submaterial, openmc_material, libmanager):
        for elem in submaterial.elements:
            for zaid in elem.zaids:
                self.zaid_to_openmc(zaid, openmc_material, libmanager)

    def mat_to_openmc(self, material, libmanager):
        matid = int(re.sub("[^0-9]", "", str(material.name)))
        matname = str(material.name)
        matdensity = abs(material.density)
        if material.density < 0:
            density_units = "g/cc"
        openmc_material = openmc.Material(matid, name=matname)
        openmc_material.set_density(density_units, matdensity)
        if material.submaterials is not None:
            for submaterial in material.submaterials:
                self.submat_to_openmc(submaterial, openmc_material, libmanager)
        self.materials.append(openmc_material)

    def matlist_to_openmc(self, matlist, libmanager):
        for material in matlist:
            self.mat_to_openmc(material, libmanager)
        self.load_geometry(os.path.join(self.path, "geometry.xml"), self.materials)

    def write(self, path: str) -> None:
        """Write OpenMC input files to xml

        Parameters
        ----------
        path : str
            path to input file destination
        """
        self.geometry.export_to_xml(os.path.join(path, "geometry.xml"))
        self.settings.export_to_xml(os.path.join(path, "settings.xml"))
        self.tallies.export_to_xml(os.path.join(path, "tallies.xml"))
        self.materials.export_to_xml(os.path.join(path, "materials.xml"))


class OpenMCOutput:

    def __init__(self, spfile_path: str) -> None:
        self.initialise(spfile_path)
        self.version = self.read_openmc_version()

    def initialise(self, spfile_path: str) -> None:
        """Read in statepoint file

        Parameters
        ----------
        spfile_path : str
            path to statepoint file
        """
        try:
            # Retrieve the version from the statepoint file (convert from tuple of integers to string)
            self.statepoint = openmc.StatePoint(spfile_path)
        except (FileNotFoundError, KeyError):
            logging.warning(
                "OpenMC version not found in the statepoint file for %s",
                spfile_path,
            )
            return None

    def read_openmc_version(self) -> str:
        """Get OpenMC version from statepoint file

        Returns
        -------
        str
            OpenMC version
        """
        version = ".".join(map(str, self.statepoint.version))
        return version

class OpenMCSphereOutput(OpenMCOutput):
    def __init__(self, spfile_path: str) -> None:
        super.__init__(self, spfile_path)

    def _get_tally_data(self, rows: list, filter: openmc.Filter):
        tally = self.statepoint.get_tally(filters=[filter])
        tally_n = tally.tally_id
        tally_description = tally.name
        energy_bins = tally.find_filter(openmc.EnergyFilter).values[1:]
        fluxes = tally.mean
        errors = tally.std_dev
        for energy, flux, error in zip(energy_bins, fluxes, errors):
            rows.append([tally_n, tally_description,energy, flux, error])
    
    def tally_to_rows(self):
        rows = []
        neutron_particle_filter = openmc.ParticleFilter(['neutron'])
        rows = self._get_tally_data(rows, neutron_particle_filter)
        photon_particle_filter = openmc.ParticleFilter(['photon'])
        rows = self._get_tally_data(rows, photon_particle_filter)
        return rows





    