from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from f4enix.core.irradiation import Nuclide
from f4enix.input.libmanager import LibManager
from f4enix.input.materials import Material, Zaid

if TYPE_CHECKING:
    from jade.helper.aux_functions import PathLike

logger = logging.getLogger(__name__)

# Serpent comments are either "% ..." until the end of the line or C-like blocks
PAT_COMMENT = re.compile(r"/\*.*?\*/|%[^\n]*", re.DOTALL)
PAT_TOKEN = re.compile(r"\S+")
# Nuclide identifiers, with or without library suffix. Either ZA (e.g. 1001.31c)
# or symbolic (e.g. H-1.31c, H1)
PAT_NUCLIDE = re.compile(r"^(\d+|[A-Za-z]{1,2}-?\d+m?)(\.\d+[a-z])?$")
PAT_ZA = re.compile(r"^\d+(\.\d+[a-z])?$")
# Cards that may follow a detector or a material definition
CARDS = {
    "branch", "casematrix", "cell", "coef", "datamesh", "dep", "det", "div",
    "dtrans", "ene", "ftrans", "fun", "hisv", "ifc", "include", "lat", "mat",
    "mesh", "mix", "nest", "particle", "pbed", "pin", "plot", "rep", "sample",
    "sens", "set", "solid", "src", "strans", "surf", "therm", "tme", "trans",
    "umsh", "utrans", "wwgen", "wwin",
}  # fmt: skip
# Optional entries of the mat card together with the number of arguments they take
MAT_OPTIONS = {
    "tmp": 1,
    "tms": 1,
    "tft": 2,
    "rgb": 3,
    "vol": 1,
    "mass": 1,
    "burn": 1,
    "fix": 2,
    "moder": 2,
}
# Detector entries whose values are binned (and recorded in the detector output)
DET_BINS = {"dc": "cell", "du": "universe", "dm": "material", "dl": "lattice"}


def _is_number(token: str) -> bool:
    try:
        float(token)
    except ValueError:
        return False
    return True


@dataclass
class SerpentMaterial:
    """Position and content of a ``mat`` card in a Serpent input.

    Attributes
    ----------
    name : str
        name of the material.
    start : int
        position in the text where the card starts.
    pairs_start : int
        position in the text where the nuclide-fraction pairs start.
    end : int
        position in the text where the card ends.
    pairs : list[tuple[str, str]]
        nuclide-fraction pairs of the material.
    """

    name: str
    start: int
    pairs_start: int
    end: int
    pairs: list[tuple[str, str]] = field(default_factory=list)


class SerpentInput:
    def __init__(self, text: str) -> None:
        """Minimal text based representation of a Serpent input. Only the parts of
        the input that JADE needs to modify are parsed. Comments are preserved,
        except for the ones placed among the nuclides of a translated material.

        Parameters
        ----------
        text : str
            content of the Serpent input file.
        """
        self.text = text

    @classmethod
    def from_file(cls, path: PathLike) -> SerpentInput:
        with open(path) as f:
            text = f.read()
        return cls(text)

    def write(self, path: PathLike) -> None:
        with open(path, "w") as f:
            f.write(self.text)

    @property
    def _masked_text(self) -> str:
        # comments are replaced with blanks so that positions are not affected
        return PAT_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), self.text)

    def _tokens(self) -> list[re.Match]:
        return list(PAT_TOKEN.finditer(self._masked_text))

    def remove_set_option(self, option: str) -> None:
        """Remove all the ``set <option>`` cards from the input. The card is assumed
        to be defined on a single line.

        Parameters
        ----------
        option : str
            name of the option (e.g. nps).
        """
        pattern = re.compile(rf"^[ \t]*set[ \t]+{option}\b[^\n]*\n?", re.MULTILINE)
        masked = self._masked_text
        # go backwards to keep the positions valid
        for match in reversed(list(pattern.finditer(masked))):
            self.text = self.text[: match.start()] + self.text[match.end() :]

    def add_card(self, card: str) -> None:
        """Append a card at the end of the input."""
        if not self.text.endswith("\n"):
            self.text += "\n"
        self.text += card + "\n"

    def set_option(self, option: str, *values) -> None:
        """Set (overriding if already present) a ``set <option> <values>`` card."""
        self.remove_set_option(option)
        self.add_card(" ".join(["set", option] + [str(v) for v in values]))

    def get_materials(self) -> list[SerpentMaterial]:
        """Locate all the ``mat`` cards of the input."""
        tokens = self._tokens()
        materials = []
        i = 0
        while i < len(tokens):
            if tokens[i].group() != "mat" or i + 2 >= len(tokens):
                i += 1
                continue
            material = SerpentMaterial(
                name=tokens[i + 1].group(),
                start=tokens[i].start(),
                pairs_start=tokens[i + 2].end(),
                end=tokens[i + 2].end(),
            )
            i += 3
            while i < len(tokens):
                word = tokens[i].group()
                if word in MAT_OPTIONS:
                    i = min(i + MAT_OPTIONS[word] + 1, len(tokens))
                    material.pairs_start = tokens[i - 1].end()
                    material.end = material.pairs_start
                elif (
                    PAT_NUCLIDE.match(word)
                    and i + 1 < len(tokens)
                    and _is_number(tokens[i + 1].group())
                ):
                    material.pairs.append((word, tokens[i + 1].group()))
                    material.end = tokens[i + 1].end()
                    i += 2
                else:
                    break
            materials.append(material)
        return materials

    def remove_materials(self) -> None:
        """Remove all the ``mat`` cards from the input."""
        for material in reversed(self.get_materials()):
            self.text = self.text[: material.start] + self.text[material.end :]

    def translate(self, suffix: str, libmanager: LibManager) -> None:
        """Translate the nuclides of all the materials to the requested library.
        Natural zaids are expanded if not available in the library. Materials that
        include nuclides not identified by their ZA number are left untouched.

        Parameters
        ----------
        suffix : str
            suffix of the library to translate to (e.g. 32c).
        libmanager : LibManager
            library manager aware of the nuclides available in the library.
        """
        for smat in reversed(self.get_materials()):
            if len(smat.pairs) == 0:
                continue
            if not all(PAT_ZA.match(nuclide) for nuclide, _ in smat.pairs):
                logger.warning(
                    "Material %s uses symbolic nuclide names and was not translated",
                    smat.name,
                )
                continue
            zaids = [
                Zaid(float(fraction), Nuclide.from_int_string(nuclide))
                for nuclide, fraction in smat.pairs
            ]
            material = Material(f"M{smat.name}", zaids)
            material.translate(suffix, libmanager)
            new_pairs = pairs_to_text(material.zaids)
            self.text = (
                self.text[: smat.pairs_start] + "\n" + new_pairs + self.text[smat.end :]
            )

    def get_detectors(self) -> dict[str, dict[str, list[str]]]:
        """Get the binned entries of the detector definitions in order of appearance,
        e.g. {"4": {"cell": ["2", "3"]}} for ``det 4 n dc 2 dc 3``."""
        tokens = [t.group() for t in self._tokens()]
        detectors = {}
        current = None
        i = 0
        while i < len(tokens) - 1:
            token = tokens[i]
            if token == "det":
                current = {}
                detectors[tokens[i + 1]] = current
                i += 2
                continue
            if current is not None:
                if token in DET_BINS:
                    current.setdefault(DET_BINS[token], []).append(tokens[i + 1])
                    i += 2
                    continue
                if token == "dr":
                    # the MT number identifies the reaction bin
                    current.setdefault("reaction", []).append(tokens[i + 1])
                    i += 2
                    continue
                if token in CARDS:
                    current = None
            i += 1
        return detectors


def pairs_to_text(zaids: list[Zaid]) -> str:
    """Format a list of zaids as Serpent nuclide-fraction pairs."""
    lines = []
    for zaid in zaids:
        lines.append(
            f"    {zaid.nuclide.write_to_int_string():<12} {zaid.fraction:.6e}"
        )
    return "\n".join(lines)


def material_to_text(
    name: str, density: float, zaids: list[Zaid], header: str = ""
) -> str:
    """Format a Serpent ``mat`` card.

    Parameters
    ----------
    name : str
        name of the material.
    density : float
        density of the material. Negative values are mass densities [g/cc],
        positive ones atomic densities [1/b-cm].
    zaids : list[Zaid]
        nuclides composing the material.
    header : str, optional
        comment to be placed before the card, by default "".
    """
    text = ""
    for line in header.splitlines():
        text += f"% {line}\n"
    text += f"mat {name} {density}\n" + pairs_to_text(zaids)
    return text


class SerpentXsdata:
    def __init__(self, tablenames: list[tuple[str, str]]) -> None:
        """Expose the content of a Serpent xsdata with the interface of the f4enix
        MCNP Xsdir needed for zaid translations.

        Parameters
        ----------
        tablenames : list[tuple[str, str]]
            (zaid, suffix) couples available in the xsdata.
        """
        self.tablenames = tablenames
        self.available_libraries = {}
        for zaid, suffix in tablenames:
            self.available_libraries.setdefault(zaid, []).append(suffix)

    def zaid_has_table(self, zaidname: str, lib: str) -> bool:
        return lib in self.available_libraries.get(zaidname, [])


def get_serpent_libmanager(
    tablenames: list[tuple[str, str]], suffix: str
) -> LibManager:
    """Create a LibManager whose nuclide availability reflects a Serpent xsdata.
    This allows to reuse the f4enix translation logic (e.g. natural zaids
    expansion) also for Serpent inputs.

    Parameters
    ----------
    tablenames : list[tuple[str, str]]
        (zaid, suffix) couples available in the xsdata.
    suffix : str
        suffix of the library that will be used for translations.

    Returns
    -------
    LibManager
        library manager to be used for translations to the Serpent library.
    """
    libmanager = LibManager(defaultlib=suffix)
    xsdata = SerpentXsdata(tablenames)
    # f4enix translations always look for MCNP-like data
    libs = sorted({lib for _, lib in tablenames} | {suffix})
    libmanager.data["mcnp"] = {lib: xsdata for lib in libs}
    libmanager.libraries["mcnp"] = libs
    return libmanager


def find_input_file(folder: PathLike) -> Path:
    """Find the Serpent input file (.i) in a folder."""
    for file in sorted(Path(folder).iterdir()):
        if file.suffix == ".i":
            return file
    raise FileNotFoundError(f"No Serpent input (.i) found in {folder}")
