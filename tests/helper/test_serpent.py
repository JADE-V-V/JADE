from __future__ import annotations

from importlib.resources import as_file, files

import pytest
from f4enix.core.irradiation import Nuclide
from f4enix.input.materials import Zaid

from jade.config.run_config import LibrarySerpent
from jade.helper.serpent import (
    SerpentInput,
    find_input_file,
    get_serpent_libmanager,
    material_to_text,
)
from tests.run import resources

RESOURCES = files(resources)


@pytest.fixture()
def serpent_input() -> SerpentInput:
    with as_file(RESOURCES.joinpath("serpent_template", "bench.i")) as file:
        return SerpentInput.from_file(file)


@pytest.fixture()
def libSerpent() -> LibrarySerpent:
    with as_file(RESOURCES.joinpath("test.xsdata")) as file:
        return LibrarySerpent(name="test", path=file, suffix="32c")


class TestSerpentInput:
    def test_get_materials(self, serpent_input: SerpentInput):
        materials = serpent_input.get_materials()
        assert [mat.name for mat in materials] == ["steel", "2"]
        assert materials[0].pairs == [
            ("26000.31c", "-0.70"),
            ("24052.31c", "-0.18"),
            ("28058.31c", "-0.12"),
        ]
        # options are skipped
        assert materials[1].pairs == [("1001.31c", "2"), ("8016.31c", "1")]
        text = serpent_input.text
        assert text[materials[1].start : materials[1].pairs_start].endswith("1001")

    def test_translate(self, serpent_input: SerpentInput, libSerpent: LibrarySerpent):
        lm = get_serpent_libmanager(libSerpent.tablenames, "32c")
        serpent_input.translate("32c", lm)
        materials = serpent_input.get_materials()
        nuclides = [nuclide for nuclide, _ in materials[0].pairs]
        # natural iron is expanded since not available in the xsdata
        assert "26000.31c" not in nuclides
        assert "26056.32c" in nuclides
        assert "24052.32c" in nuclides
        # mass fractions are preserved
        total = sum(float(fraction) for _, fraction in materials[0].pairs)
        assert total == pytest.approx(-1)
        assert materials[1].pairs[0][0] == "1001.32c"
        # options and comments outside the pairs are preserved
        assert "rgb 100 100 100" in serpent_input.text
        assert "moder lwtr 1001" in serpent_input.text
        assert "must survive" in serpent_input.text
        assert "therm lwtr lwj3.11t" in serpent_input.text

    def test_translate_symbolic(self):
        inp = SerpentInput("mat 1 -1.0\n Fe-56.31c 1.0\n")
        lm = get_serpent_libmanager([("26056", "32c")], "32c")
        inp.translate("32c", lm)
        assert "Fe-56.31c" in inp.text

    def test_set_option(self, serpent_input: SerpentInput):
        serpent_input.set_option("nps", 1000, 10)
        assert "set nps 50" not in serpent_input.text
        assert serpent_input.text.endswith("set nps 1000 10\n")
        serpent_input.remove_set_option("acelib")
        assert "acelib" not in serpent_input.text

    def test_remove_set_option_commented(self):
        inp = SerpentInput("% set nps 10\nset nps 20\n")
        inp.remove_set_option("nps")
        assert inp.text == "% set nps 10\n"

    def test_remove_materials(self, serpent_input: SerpentInput):
        serpent_input.remove_materials()
        assert serpent_input.get_materials() == []
        assert "therm lwtr" in serpent_input.text

    def test_get_detectors(self, serpent_input: SerpentInput):
        detectors = serpent_input.get_detectors()
        assert detectors == {"4": {"cell": ["10", "20"]}}

        inp = SerpentInput("det 1 n dr -6 void dr 102 void du 3\ncell 1 0 void -1")
        assert inp.get_detectors() == {
            "1": {"reaction": ["-6", "102"], "universe": ["3"]}
        }


def test_material_to_text():
    zaids = [Zaid(1, Nuclide.from_int_string("1001.32c"))]
    text = material_to_text("1", -1.0, zaids, header="H-1\nline 2")
    assert text.startswith("% H-1\n% line 2\nmat 1 -1.0\n")
    assert "1001.32c" in text
    inp = SerpentInput(text)
    assert inp.get_materials()[0].pairs[0][0] == "1001.32c"


def test_find_input_file(tmpdir):
    with pytest.raises(FileNotFoundError):
        find_input_file(tmpdir)
    with as_file(RESOURCES.joinpath("serpent_template")) as folder:
        assert find_input_file(folder).name == "bench.i"
