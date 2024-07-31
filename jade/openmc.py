import os
import openmc

class OpenMCInputFiles:
    def __init__(self, geometry, settings, tallies, materials, name=None) -> None:
        self.geometry = openmc.Geometry.from_xml(geometry, materials)
        self.settings = openmc.Settings.from_xml(settings)
        self.tallies = openmc.Tallies.from_xml(tallies)
        self.materials = openmc.Materials.from_xml(materials)
        self.name = name

    def add_stopCard(self, nps: int) -> None:
        """Add number of particles to simulate

        Parameters
        ----------
        nps : int
            number of particles to simulate
        """
        self.settings.batches = 100
        self.settings.particles = int(nps) / 100

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



    