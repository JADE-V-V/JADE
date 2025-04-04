from __future__ import annotations

import logging
import os
import shutil
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path

from f4enix.input.d1suned import IrradiationFile, Reaction, ReactionFile
from f4enix.input.libmanager import LibManager
from f4enix.input.materials import MatCardsList, Material, SubMaterial, Zaid
from f4enix.input.MCNPinput import D1S_Input
from f4enix.input.MCNPinput import Input as MCNPInput

from jade.config.run_config import Library, LibraryD1S, LibraryMCNP
from jade.helper.__openmc__ import OMC_AVAIL
from jade.helper.aux_functions import PathLike
from jade.helper.constants import CODE, DOSIMETRY_LIBS
from jade.helper.errors import ConfigError

if OMC_AVAIL:
    import jade.helper.openmc as omc


class Input(ABC):
    def __init__(self, template_folder: PathLike, lib: Library):
        self.template_folder = template_folder

    @property
    @abstractmethod
    def code(self) -> CODE:
        """Code of the input file."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the input file. E.g. ITER_1D"""
        pass

    @property
    @abstractmethod
    def lib(self) -> Library:
        """Library used for the input file."""
        pass

    @abstractmethod
    def set_nps(self, nps: int):
        """Set the number of particles to simulate.

        Parameters
        ----------
        nps : int
            number of particles to simulate.
        """
        pass

    @abstractmethod
    def translate(self):
        """Translate the input to the requested library. This is code-dependent.

        Parameters
        ----------
        lib : Library
            library to which the input needs to be translated to.
        """
        pass

    @abstractmethod
    def _write(self, output_folder: PathLike):
        """Write the input files to the output folder. This should handle also
        additional files such as the wwinp for MCNP."""
        pass

    def write(self, output_folder: PathLike):
        """Write the input files to the output folder. Specific files are hendled
        by _write, while all common files between codes (like
        volumes.json) are handled here.

        Parameters
        ----------
        output_folder : PathLike
            folder where the input files should be written.
        """
        self._write(output_folder)

        # Make copy of volumes.json if it exists
        volumes_json = os.path.join(self.template_folder, "volumes.json")
        if os.path.exists(volumes_json):
            outfile = Path(output_folder, "volumes.json")
            shutil.copyfile(volumes_json, outfile)


class InputMCNP(Input):
    def __init__(self, template_folder: PathLike, lib: LibraryMCNP):
        """Implementation of the Input class for MCNP inputs. The only file to deal with
        here is the input file itself and possibly the wwinp file.

        Parameters
        ----------
        template_folder : PathLike
            path to the folder containing the template input file.
        lib : LibraryMCNP
            library to be used for the input file.
        """
        # localize the .i file
        for file in os.listdir(template_folder):
            if file.endswith(".i"):
                filepath = os.path.join(template_folder, file)
                break
        self.template_folder = template_folder
        self.inp = MCNPInput.from_input(filepath)
        self._name = file.split(".")[0]
        self._lib = lib
        self.lm = LibManager(xsdir_path=lib.path, dosimetry_lib=DOSIMETRY_LIBS)

    @property
    def code(self) -> CODE:
        return CODE.MCNP

    @property
    def name(self) -> str:
        return self._name

    @property
    def lib(self) -> LibraryMCNP:
        return self._lib

    def set_nps(self, nps: int):
        self.inp.add_stopCard(nps)

    def translate(self):
        if self.lib.suffix is None:
            raise ValueError("suffix must be provided for MCNP libraries")
        self.inp.translate(self.lib.suffix, self.lm)
        self.inp.update_zaidinfo(self.lm)

    def _write(self, output_folder: PathLike):
        # write the new input
        self.inp.write(Path(output_folder, f"{self.name}.i"))
        # if ww are availble, copy them here
        if os.path.exists(Path(self.template_folder, "wwinp")):
            shutil.copy(
                Path(self.template_folder, "wwinp"), Path(output_folder, "wwinp")
            )


class InputMCNPSphere(InputMCNP):
    def __init__(
        self,
        template_folder: PathLike,
        lib: LibraryMCNP,
        zaid: str | Material,
        density: str,
    ):
        """Subclass of the MCNP Input. It is needed to dynamically create the different
        zaids/material inputs for the sphere benchmark.

        Parameters
        ----------
        template_folder : PathLike
            path to the folder containing the template input file.
        lib : LibraryMCNP
            library to be used for the input file.
        zaid : str | Material
            zaid or the material to be used in the sphere.
        density : str
            density of the material/isotope in the sphere.
        """
        super().__init__(template_folder, lib)
        self._assign_zaid_material(zaid, density)

    def _assign_zaid_material(self, zaid: str | Material, density: str):
        # --- The material needs to be assigned to the sphere ---
        # Create MCNP material card
        if self.lib.suffix is None:
            raise ConfigError("suffix must be provided for MCNP libraries")
        material = self._get_material(zaid)
        matlist = MatCardsList([material])

        # adjourn density and material
        self.inp.materials = matlist
        sphere_cell = self.inp.cells["2"]
        sphere_cell.set_d(density)
        sphere_cell.lines = sphere_cell.card()

    def _get_material(self, zaid: str | Material) -> Material:
        if isinstance(zaid, Material):
            material = deepcopy(zaid)  # just to be sure not to mess with something
            truename = material.name
            material.header = f"{material.header}C\nC True name:{truename}"
            material.name = "M1"
            # override the input name
            self._name = f"{self.name}_{truename}"
        else:
            if self.lib.suffix is None:
                # use a dummy, this should be called by the OpenMC method also
                zaidlib = "31c"
            else:
                zaidlib = self.lib.suffix
            zaidob = Zaid(1, zaid[:-3], zaid[-3:], zaidlib)
            name, formula = self.lm.get_zaidname(zaid)
            submat = SubMaterial("M1", [zaidob], header="C " + name + " " + formula)
            material = Material([zaidob], None, "M1", submaterials=[submat])
            # override the input name
            self._name = f"{self.name}_{zaid}_{formula}"

        return material


class InputOpenMC(Input):
    @property
    def code(self) -> CODE:
        return CODE.OPENMC

    @property
    def name(self) -> str:
        return self._name

    @property
    def lib(self) -> Library:
        return self._lib

    def __init__(self, template_folder: PathLike, lib: Library):
        self.template_folder = template_folder
        self._name = os.path.basename(os.path.basename(template_folder))
        self._lib = lib
        self.inp = omc.OpenMCInputFiles(template_folder)

    def set_nps(self, nps: int):
        self.inp.add_stopCard(nps)

    def translate(self):
        # No action needed for OpenMC, controlled by the path to lib I believe
        pass

    def _write(self, output_folder: PathLike):
        # dump all files related to the OpenMC input
        self.inp.write(output_folder)
        # Copy tally_factors.yaml if present
        tallies_yaml = os.path.join(self.template_folder, "tally_factors.yaml")
        if os.path.exists(tallies_yaml):
            outfile = os.path.join(output_folder, "tally_factors.yaml")
            shutil.copyfile(tallies_yaml, outfile)


class InputOpenMcSphere(InputOpenMC):
    def __init__(
        self,
        template_folder: PathLike,
        lib: Library,
        zaid: str | Material,
        density: str,
    ):
        """Subclass of the OpenMC Input to deal with the sphere benchmark. The main
        difference is the dynamic creation of the different inputs for all zaids/materials.

        Parameters
        ----------
        template_folder : PathLike
            path to the folder containing the template input file.
        lib : Library
            library to be used for the input file.
        zaid : str | Material
            zaid or the material to be used in the sphere.
        density : str
            density of the material/isotope in the sphere.
        """
        super().__init__(template_folder, lib)
        self.lm = LibManager()
        self._assign_zaid_material(zaid, density)

    def _assign_zaid_material(self, zaid: str | Material, density: str):
        material = self._get_material(zaid)
        material.density = float(density)
        materials = MatCardsList([material])
        # Assign material
        self.inp.matlist_to_openmc(materials, self.lm)

    def _get_material(self, zaid: str | Material) -> Material:
        if isinstance(zaid, Material):
            material = deepcopy(zaid)  # just to be sure not to mess with something
            truename = material.name
            material.header = f"{material.header}C\nC True name:{truename}"
            material.name = "M1"
            # override the input name
            self._name = f"{self.name}_{truename}"
        else:
            # zaid suffix used here is irrelevant, as it is not used in the OpenMC
            zaidob = Zaid(1, zaid[:-3], zaid[-3:], "00c")
            name, formula = self.lm.get_zaidname(zaid)
            submat = SubMaterial("M1", [zaidob], header="C " + name + " " + formula)
            material = Material([zaidob], None, "M1", submaterials=[submat])
            # override the input name
            self._name = f"{self.name}_{zaid}_{formula}"

        return material


class InputSerpent(Input):
    @property
    def code(self) -> CODE:
        return CODE.OPENMC

    @property
    def name(self) -> str:
        return self._name

    @property
    def lib(self) -> Library:
        return self._lib

    def __init__(self, template_folder: PathLike, lib: Library):
        raise NotImplementedError

    def set_nps(self, nps: int):
        raise NotImplementedError

    def translate(self):
        raise NotImplementedError

    def _write(self, output_folder: PathLike):
        raise NotImplementedError


class InputD1S(Input):
    def __init__(self, template_folder: PathLike, lib: LibraryD1S):
        """Implementation of the Input class for D1S inputs.
        In addition to the input file
        and the wwinp file, we also need to deal with the irradiation and reaction files

        Parameters
        ----------
        template_folder : PathLike
            path to the folder containing the template input file.
        lib : LibraryD1S
            library to be used for the input file.
        """
        # localize the .i file
        self.template_folder = template_folder
        for file in os.listdir(template_folder):
            if file.endswith(".i"):
                break
        self._name = file.split(".")[0]
        irrfile = Path(template_folder, f"{self.name}_irrad")
        reacfile = Path(template_folder, f"{self.name}_react")
        self.inp = D1S_Input.from_input(Path(template_folder, file))
        self.lm = LibManager(xsdir_path=lib.path, dosimetry_lib=DOSIMETRY_LIBS)
        self._lib = lib

        try:
            self.inp.irrad_file = IrradiationFile.from_text(irrfile)
        except FileNotFoundError:
            logging.debug("d1S irradition file not found")
        try:
            self.inp.reac_file = ReactionFile.from_text(reacfile)
        except FileNotFoundError:
            # If the irradiation file exists, by default we can get the complete reaction
            # file
            if self.inp.irrad_file is not None:
                self.inp.reac_file = self.inp.get_reaction_file(
                    self.lm, self.lib.suffix, set_as_attribute=True
                )
                logging.debug("d1S reaction file not found, created from irrad file")
            else:
                logging.debug("d1S reaction file not found")

    @property
    def code(self) -> CODE:
        return CODE.D1S

    @property
    def name(self) -> str:
        return self._name

    @property
    def lib(self) -> LibraryD1S:
        return self._lib

    def set_nps(self, nps: int):
        self.inp.add_stopCard(nps)

    def translate(self):
        self.inp.smart_translate(self.lib.suffix, self.lib.transport_suffix, self.lm)
        self.inp.update_zaidinfo(self.lm)

    def _write(self, output_folder: PathLike):
        # write the new input
        self.inp.write(Path(output_folder, f"{self.name}.i"))
        # And irradiation and reaction files if needed
        if self.inp.irrad_file is not None:
            self.inp.irrad_file.write(output_folder)
        if self.inp.reac_file is not None:
            self.inp.reac_file.write(output_folder)
        # if ww are availble, copy them here
        if os.path.exists(Path(self.template_folder, "wwinp")):
            shutil.copy(
                Path(self.template_folder, "wwinp"), Path(output_folder, "wwinp")
            )


class InputD1SSphere(InputD1S, InputMCNPSphere):
    def __init__(
        self,
        template_folder: PathLike,
        lib: LibraryD1S,
        zaid: str | Material,
        density: str,
        MT: str | int | None = None,
        daughter: str | None = None,
        irrad_file: PathLike | None = None,
    ):
        """Subclass of the D1S Input to deal with irradiation of rteaction files.
        The inheritance from the MCNP Sphere is to re-use some logic related to the
        dynamic creation of the different input for all zaids/materials.

        Parameters
        ----------
        template_folder : PathLike
            path to the folder containing the template input file.
        lib : LibraryD1S
            library to be used for the input file.
        zaid : str | Material
            zaid or the material to be used in the sphere.
        density : str
            density of the material/isotope in the sphere.
        MT : str | None, optional
            MT number of the reaction to be considered, by default None
        daughter : str | int | None, optional
            daughter of the reaction, by default None
        irrad_file : PathLike, optional
            path to the irradiation file, which is different for
            each library by default None
        Raises
        ------
        ConfigError
            _description_
        """
        super().__init__(template_folder, lib)
        # the template irradiation file is different for each library.
        self.inp.irrad_file = IrradiationFile.from_text(irrad_file)

        self._assign_zaid_material(zaid, density)
        # recompute the reaction and irradiation files
        if isinstance(zaid, Material):
            if self.lib.suffix is None:
                raise ConfigError("suffix must be provided for D1S libraries")
            self.inp.reac_file = ReactionFile(
                self.inp.get_potential_paths(self.lm, lib.suffix)
            )
            daughters = []
            for reac in self.inp.reac_file.reactions:
                daughters.append(reac.daughter)
            self.inp.irrad_file.select_daughters_irradiation_file(daughters)
            self._name = f"{self.name}_All"
        else:
            assert MT is not None
            assert daughter is not None
            self.inp.irrad_file.select_daughters_irradiation_file([daughter])
            # generate the reaction file with only the specific MT
            reaction = Reaction(f"{zaid}.{lib.suffix}", MT, daughter)
            reacfile = ReactionFile([reaction])
            self.inp.reac_file = reacfile
            # also the name needs to be updated
            self._name = f"{self.name}_{MT}"
