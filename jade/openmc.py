import os
import openmc

class OpenMCInputFiles:
    def __init__(self, path : str, name=None) -> None:        
        self.initialise(path)
        self.name = name

    def initialise(self, path : str) -> None:
        """Initialise OpenMC input files from xml

        Parameters
        ----------
        path : str
            path to input file destination
        """
        files = os.listdir(path)
        if 'settings.xml' in files:
            self.load_settings(os.path.join(path, 'settings.xml'))        
        if 'tallies.xml' in files:
            self.load_tallies(os.path.join(path, 'tallies.xml'))
        if 'geometry.xml' in files:
            if 'materials.xml' in files:
                self.load_geometry(os.path.join(path, 'geometry.xml'), materials=os.path.join('materials.xml'))
            else:
                self.load_geometry(os.path.join(path, 'geometry.xml'))
        if 'materials.xml' in files:
            self.load_materials(os.path.join(path, 'materials.xml'))


    
    def load_geometry(self, geometry : str, materials=None) -> None:
        """Initialise OpenMC geometry from xml

        Parameters
        ----------
        geometry : str
            path to geometry input xml
        materials : str (optional)
            path to materials input xml
        """         
        if materials is None:
            self.geometry = openmc.Geometry.from_xml(geometry)
        else:
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
        self.settings.particles = int(nps) / batches

    def write(self, path) -> None:
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

    
    