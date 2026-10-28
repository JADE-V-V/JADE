from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import f4enix.input.MCNPinput as ipt
import pytest
from f4enix.input.d1suned import IrradiationFile, ReactionFile
from f4enix.input.libmanager import LibManager
from f4enix.input.materials import Material, Zaid

import jade.resources.default_cfg.benchmarks as bench
import tests.dummy_structure.benchmark_templates as res
from jade.config.run_config import (
    LibraryD1S,
    LibraryMCNP,
    LibraryOpenMC,
    LibrarySerpent,
)
from jade.helper.__optionals__ import OMC_AVAIL
from jade.helper.constants import CODE

if OMC_AVAIL:
    import openmc

    from jade.helper.openmc import OpenMCInputFiles
from jade.run.input import (
    InputD1SSphere,
    InputMCNP,
    InputMCNPSphere,
    InputOpenMC,
    InputOpenMcSphere,
    InputSerpent,
    InputSerpentSphere,
)
from tests.run import resources


@pytest.fixture()
def libMCNP():
    # The None in the path tricks into using the default xsdir in F4Enix
    return LibraryMCNP(name="test", path=None, suffix="31c")


@pytest.fixture()
def libOpenMC():
    # The None in the path tricks into using the default xsdir in F4Enix
    with as_file(files(resources).joinpath("cross_sections.xml")) as file:
        lib = LibraryOpenMC(name="test", path=file)
    return lib


@pytest.fixture()
def libSerpent():
    with as_file(files(resources).joinpath("test.xsdata")) as file:
        lib = LibrarySerpent(
            name="test", path=file, suffix="32c", photon_data_dir="/photon/data"
        )
    return lib


@pytest.fixture()
def libD1S():
    # The None in the path tricks into using the default xsdir in F4Enix
    return LibraryD1S(
        name="test",
        path=None,
        suffix="99c",
        transport_library_path=None,
        transport_suffix="31c",
    )


TEMPLATE_ROOT = files(res)
CONFIG_BENCH = files(bench)


class TestIputMCNP:
    def test_input_generation(self, libMCNP, tmpdir):
        template_folder = TEMPLATE_ROOT.joinpath("Oktavian/Oktavian_Al/mcnp")
        inp = InputMCNP(template_folder, libMCNP)
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        # Check if the file was written correctly
        read_inp = ipt.Input.from_input(Path(tmpdir).joinpath("Oktavian_Al.i"))
        nps_line = read_inp.other_data["NPS"].text
        assert nps_line[:6] == "NPS 10"
        assert read_inp.mat_section["M1"].zaids[0].library == "31c"
        assert os.path.exists(Path(tmpdir).joinpath("wwinp"))


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
class TestIputOpenMC:
    def test_zaid_openmc(self):
        nuclide = Zaid.from_string("1000.31c -1")
        material = openmc.Material()
        lm = LibManager()
        OpenMCInputFiles.zaid_to_openmc(nuclide, material, lm)
        assert material.nuclides[0].name == "H0"

        nuclide = Zaid.from_string("1001.31c -1")
        OpenMCInputFiles.zaid_to_openmc(nuclide, material, lm)
        assert material.nuclides[1].name == "H1"

    def test_input_generation(self, libOpenMC, tmpdir):
        template_folder = TEMPLATE_ROOT.joinpath("ITER_1D/ITER_1D/openmc")
        inp = InputOpenMC(template_folder, libOpenMC)
        inp.set_nps(10)
        inp.write(tmpdir)
        settings_file = os.path.join(tmpdir, "settings.xml")
        settings = openmc.Settings.from_xml(settings_file)
        assert settings.source is not None

        weight_windows_outfile = os.path.join(tmpdir, "weight_windows.h5")
        assert os.path.exists(weight_windows_outfile)
        assert hasattr(settings, "weight_windows")
        assert settings.weight_windows is not None
        assert settings.weight_windows_on is True


class TestInputMCNPSphere:
    def test_input_generation(self, libMCNP, tmpdir):
        template_folder = TEMPLATE_ROOT.joinpath("Sphere/Sphere/mcnp")
        inp = InputMCNPSphere(template_folder, libMCNP, "1001", "1.0")
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        # Check if the file was written correctly
        read_inp = ipt.Input.from_input(Path(tmpdir).joinpath("Sphere_1001_H-1.i"))
        nps_line = read_inp.other_data["NPS"].text
        assert nps_line[:6] == "NPS 10"
        assert read_inp.mat_section["M1"].zaids[0].library == "31c"

    def test_material_header(self, libMCNP, tmpdir):
        # header without trailing newline (as stored by f4enix) must not be
        # glued to the extra comment lines, producing an invalid "CC" line
        template_folder = TEMPLATE_ROOT.joinpath("Sphere/Sphere/mcnp")
        zaid = Zaid.from_string("1001.31c 1.0")
        material = Material("M101", [zaid], header="C my material\nC")
        inp = InputMCNPSphere(template_folder, libMCNP, material, "1.0")
        inp.write(tmpdir)

        read_inp = ipt.Input.from_input(Path(tmpdir).joinpath("Sphere_M101.i"))
        header = read_inp.mat_section["M1"].header
        assert header.splitlines() == [
            "C my material",
            "C",
            "C",
            "C True name:M101",
        ]


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
class TestInputOpenMCSphere:
    def test_input_generation(self, tmpdir, libOpenMC):
        template_folder = TEMPLATE_ROOT.joinpath("Sphere/Sphere/openmc")
        inp = InputOpenMcSphere(template_folder, libOpenMC, "1001", "-1.0")
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        # Check if the file was written correctly
        # read_inp = ipt.Input.from_input(Path(tmpdir).joinpath("Sphere_1001_H-1.i"))
        # assert read_inp.other_data["NPS"].lines == ["NPS 10 \n"]
        # assert read_inp.materials["M1"].submaterials[0].zaidList[0].library == "31c"


class TestInputD1SSphere:
    def test_input_generation(self, tmpdir, libD1S):
        template_folder = TEMPLATE_ROOT.joinpath("SphereSDDR/SphereSDDR/d1s")
        irrad_file = CONFIG_BENCH.joinpath("SphereSDDR/irrad_99c.txt")
        inp = InputD1SSphere(
            template_folder, libD1S, "11023", "1.0", 16, "11022", irrad_file
        )
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        # Check if the file was written correctly
        assert os.path.exists(Path(tmpdir).joinpath("SphereSDDR_11023_Na-23_16.i"))
        assert os.path.getsize(Path(tmpdir).joinpath("irrad")) > 0
        assert os.path.getsize(Path(tmpdir).joinpath("react")) > 0

    def test_input_generation_material(self, tmpdir, libD1S):
        # the irradiation file must keep exactly the daughters produced by the
        # reactions (it used to be silently emptied)
        template_folder = TEMPLATE_ROOT.joinpath("SphereSDDR/SphereSDDR/d1s")
        irrad_file = CONFIG_BENCH.joinpath("SphereSDDR/irrad_99c.txt")
        materials = ipt.Input.from_input(
            TEMPLATE_ROOT.joinpath("TypicalMaterials")
        ).mat_section
        inp = InputD1SSphere(
            template_folder, libD1S, materials["M101"], "1.0", irrad_file=irrad_file
        )
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        irrad = IrradiationFile.from_text(Path(tmpdir).joinpath("irrad"))
        react = ReactionFile.from_text(Path(tmpdir).joinpath("react"))
        irrad_daughters = {d.write_to_int_string() for d in irrad.get_daughters()}
        react_daughters = {r.daughter.write_to_int_string() for r in react.reactions}
        assert len(irrad_daughters) > 0
        assert irrad_daughters == react_daughters


class TestInputSerpent:
    def test_input_generation(self, libSerpent, tmpdir):
        with as_file(files(resources).joinpath("serpent_template")) as template:
            inp = InputSerpent(template, libSerpent)
        assert inp.code == CODE.SERPENT
        assert inp.name == "bench"
        inp.set_nps(1000)
        inp.translate()
        inp.write(tmpdir)

        assert sorted(os.listdir(tmpdir)) == ["bench.i", "geom.txt"]
        with open(Path(tmpdir, "bench.i")) as f:
            text = f.read()
        assert "set nps 1000 100" in text
        assert "set nps 50" not in text
        # the library is given through the environment variable
        assert "acelib" not in text
        assert 'set pdatadir "/photon/data"' in text
        assert "26056.32c" in text
        assert ".31c" not in text

    def test_set_nps_few_particles(self, libSerpent):
        with as_file(files(resources).joinpath("serpent_template")) as template:
            inp = InputSerpent(template, libSerpent)
        inp.set_nps(10)
        assert "set nps 10 10" in inp.inp.text


class TestInputSerpentSphere:
    def test_input_generation(self, tmpdir, libSerpent):
        template = TEMPLATE_ROOT.joinpath("Sphere", "Sphere", "serpent")
        inp = InputSerpentSphere(template, libSerpent, "1001", "-0.0708")
        assert inp.name == "Sphere_1001_H-1"
        inp.translate()
        inp.write(tmpdir)
        with open(Path(tmpdir, "Sphere_1001_H-1.i")) as f:
            text = f.read()
        materials = inp.inp.get_materials()
        assert len(materials) == 1
        assert materials[0].name == "1"
        assert materials[0].pairs == [("1001.32c", "1.000000e+00")]
        assert "mat 1 -0.0708" in text
        assert "% hydrogen H-1" in text

    def test_material(self, tmpdir, libSerpent):
        mat_path = TEMPLATE_ROOT.joinpath("TypicalMaterials")
        material = ipt.Input.from_input(mat_path).mat_section["M101"]
        template = TEMPLATE_ROOT.joinpath("Sphere", "Sphere", "serpent")
        inp = InputSerpentSphere(template, libSerpent, material, "-7.93")
        assert inp.name == "Sphere_M101"
        inp.write(tmpdir)
        with open(Path(tmpdir, "Sphere_M101.i")) as f:
            text = f.read()
        assert "% True name:M101" in text
        # MCNP comments are converted
        assert "\nC " not in text
        pairs = inp.inp.get_materials()[0].pairs
        assert len(pairs) == len(material.zaids)
        assert all(nuclide.endswith(".32c") for nuclide, _ in pairs)
