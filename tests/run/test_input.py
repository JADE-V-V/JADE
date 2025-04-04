from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import f4enix.input.MCNPinput as ipt
from f4enix.input.libmanager import LibManager
from f4enix.input.materials import Zaid
import pytest

import jade.resources.default_cfg.benchmarks as bench
import tests.dummy_structure.benchmark_templates as res
from jade.config.run_config import LibraryD1S, LibraryMCNP, LibraryOpenMC
from jade.helper.__openmc__ import OMC_AVAIL
if OMC_AVAIL:
    import openmc
    from jade.helper.openmc import OpenMCInputFiles
from jade.run.input import (
    InputD1SSphere,
    InputMCNP,
    InputMCNPSphere,
    InputOpenMC,
    InputOpenMcSphere,
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
        nps_lines = read_inp.other_data["NPS"].lines
        assert len(nps_lines) == 1
        assert nps_lines[0][:6] == "NPS 10"
        assert read_inp.materials["M1"].submaterials[0].zaidList[0].library == "31c"
        assert os.path.exists(Path(tmpdir).joinpath("wwinp"))


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
class TestIputOpenMC:
    def test_zaid_openmc(self):
        nuclide = Zaid.from_string('1000.31c -1')
        material = openmc.Material()
        lm = LibManager()
        OpenMCInputFiles.zaid_to_openmc(nuclide, material, lm)
        assert material.nuclides[0].name == 'H0'

        nuclide = Zaid.from_string('1001.31c -1')
        OpenMCInputFiles.zaid_to_openmc(nuclide, material, lm)
        assert material.nuclides[1].name == 'H1'


class TestInputMCNPSphere:
    def test_input_generation(self, libMCNP, tmpdir):
        template_folder = TEMPLATE_ROOT.joinpath("Sphere/Sphere/mcnp")
        inp = InputMCNPSphere(template_folder, libMCNP, "1001", "1.0")
        inp.set_nps(10)
        inp.translate()
        inp.write(tmpdir)

        # Check if the file was written correctly
        read_inp = ipt.Input.from_input(Path(tmpdir).joinpath("Sphere_1001_H-1.i"))
        nps_lines = read_inp.other_data["NPS"].lines
        assert len(nps_lines) == 1
        assert nps_lines[0][:6] == "NPS 10"
        assert read_inp.materials["M1"].submaterials[0].zaidList[0].library == "31c"


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
