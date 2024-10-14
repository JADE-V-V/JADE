import os
import re
import openmc

from jade.output import AbstractOutput

class OpenMCInputFiles:
    def __init__(self, path : str, name=None) -> None:        
        self.path = path
        self.name = name
        self.initialise(path)

    def initialise(self, path : str) -> None:
        """Initialise OpenMC input files from xml

        Parameters
        ----------
        path : str
            path to input file destination
        """
        files = os.listdir(path)
        if ('geometry.xml' in files) and ('materials.xml') in files:
            self.load_geometry(os.path.join(path, 'geometry.xml'), materials=os.path.join('materials.xml'))
        else:
            self.geometry = openmc.Geometry()
            self.materials = openmc.Materials()        
        if 'settings.xml' in files:
            self.load_settings(os.path.join(path, 'settings.xml'))
        else:
            self.settings = openmc.Settings()        
        if 'tallies.xml' in files:
            self.load_tallies(os.path.join(path, 'tallies.xml'))
        else:
            self.tallies = openmc.Tallies()
    
    def load_geometry(self, geometry : str, materials) -> None:
        """Initialise OpenMC geometry from xml

        Parameters
        ----------
        geometry : str
            path to geometry input xml
        materials : str
            path to materials input xml, or openmc.Materials object
        """         
        self.geometry = openmc.Geometry.from_xml(geometry, materials)

    def load_settings(self, settings : str) -> None:
        """Initialise OpenMC settings from xml

        Parameters
        ----------
        settings : str
            path to geometry input xml
        """        
        self.settings = openmc.Settings.from_xml(settings)

    def load_tallies(self, tallies : str) -> None:
        """Initialise OpenMC tallies from xml

        Parameters
        ----------
        talllies : str
            path to geometry input xml
        """        
        self.tallies = openmc.Tallies.from_xml(tallies)

    def load_materials(self, materials : str) -> None:
        """Initialise OpenMC materials from xml

        Parameters
        ----------
        materials : str
            path to geometry input xml
        """        
        self.materials = openmc.Materials.from_xml(materials)

    def add_stopCard(self, nps: int, batches=100) -> None:
        """Add number of particles to simulate

        Parameters
        ----------
        nps : int
            number of particles to simulate
        """
        self.settings.batches = batches
        self.settings.particles = int(nps/batches)

    def zaid_to_openmc(self, zaid, openmc_material, libmanager):
        nuclide = zaid.get_fullname(libmanager).replace("-", "")
        if zaid.fraction < 0.0:
            openmc_material.add_nuclide(nuclide, 100*abs(zaid.fraction), 'wo')
        else:
            openmc_material.add_nuclide(nuclide, 100*abs(zaid.fraction), 'ao')
    
    def submat_to_openmc(self, submaterial, openmc_material, libmanager):
        if submaterial.elements is not None:
            for elem in submaterial.elements:
                for zaid in elem.zaids:
                    self.zaid_to_openmc(zaid, openmc_material, libmanager)
        else:
            for zaid in submaterial.zaidList:
                self.zaid_to_openmc(zaid, openmc_material, libmanager)
    
    def mat_to_openmc(self, material, libmanager):
        matid = int(re.sub("[^0-9]", "", str(material.name)))
        matname = str(material.name)
        matdensity = abs(material.density)
        if material.density < 0:
            density_units = "g/cc"
        else:
            density_units = "atom/b-cm"
        openmc_material = openmc.Material(matid, name=matname)
        openmc_material.set_density(density_units, matdensity)
        if material.submaterials is not None:
            for submaterial in material.submaterials:
                self.submat_to_openmc(submaterial, openmc_material, libmanager)
        self.materials.append(openmc_material)
    
    def matlist_to_openmc(self, matlist, libmanager):
        for material in matlist:
            self.mat_to_openmc(material, libmanager)
        self.load_geometry(os.path.join(self.path, 'geometry.xml'), self.materials)

    def write(self, path : str) -> None:
        """Write OpenMC input files to xml

        Parameters
        ----------
        path : str
            path to input file destination
        """
        self.geometry.export_to_xml(os.path.join(path, 'geometry.xml'))
        self.settings.export_to_xml(os.path.join(path, 'settings.xml'))
        self.tallies.export_to_xml(os.path.join(path, 'tallies.xml'))
        self.materials.export_to_xml(os.path.join(path, 'materials.xml'))


class OpenMCSphereInputFiles(OpenMCInputFiles):
    def __init__(self, path : str, name=None) -> None:        
        OpenMCInputFiles.__init__(self, path, name=name)
    

# Output handling for OpenMC
class OpenMCOutput(AbstractOutput):
    @staticmethod
    def _get_output_files(results_path):
        """
        Recover the statepoint and summary file from a directory

        Parameters
        ----------
        results_path : str or path
            path where the OpenMC results are contained.

        Raises
        ------
        FileNotFoundError
            if either statepoint or summary are not found.

        Returns
        -------
        spfile : path
            path to the statepoint file
        summaryfile : path
            path to the summary file

        """
        # Get statepoint file and summary file.
        spfile = None
        summaryfile = None

        for file in os.listdir(results_path):
            if file.startswith("statepoint"):
                spfile = file
            elif file.startswith("summary"):
                summaryfile = file

        if spfile is None or summaryfile is None:
            raise FileNotFoundError(
                """
 The following path does not contain either the statepoint or summary file:
 {}""".format(
                    results_path
                )
            )

        spfile = os.path.join(results_path, spfile)
        summaryfile = os.path.join(results_path, summaryfile)

        return spfile, summaryfile