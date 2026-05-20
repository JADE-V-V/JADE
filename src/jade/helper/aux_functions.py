from __future__ import annotations

import importlib.metadata
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Union

import numpy as np
import pandas as pd
import yaml

if TYPE_CHECKING:
    from jade.config.run_config import Library
from jade.helper.constants import CODE
from jade.post.sim_output import MCNPSimOutput, OpenMCSimOutput

PathLike = Union[str, os.PathLike, Path]

CODE_PATTERN = re.compile(r"_.+_-")
LIB_PATTERN = re.compile(r"-_.+_")


def get_code_lib(string) -> tuple[str, str]:
    """Extracts the code and library names from a code-lib string.

    Parameters
    ----------
    string : str
        The code-lib string, e.g. _mcnp_-_FENDL 3.2c_

    Returns
    -------
    tuple[str, str]
        The code and library names.
    """
    code_match = CODE_PATTERN.search(string)
    if code_match is None:
        raise ValueError(f"Invalid code-lib string: {string}")
    code = code_match.group()[1:-2]  # remove the "<" and ">-"
    lib_match = LIB_PATTERN.search(string)
    if lib_match is None:
        raise ValueError(f"Invalid code-lib string: {string}")
    lib = lib_match.group()[2:-1]  # remove the "-<" and ">"
    return code, lib


def print_code_lib(code: CODE, lib: Library | str, pretty: bool = False) -> str:
    """Prints the code and library names in a code-lib format.

    Parameters
    ----------
    code : CODE
        The code
    lib : Library | str
        The library
    pretty : bool, optional
        If True, the '_' are removed, by default False. When pretty is True, the
        code-lib string cannot be used in get_code_lib().

    Returns
    -------
    str
        The code-lib string, e.g. _mcnp_-_FENDL 3.2c_
    """
    if isinstance(lib, str):
        lib_name = lib
    else:
        lib_name = lib.name

    if pretty:
        return f"{code.value} - {lib_name}"
    else:
        return f"_{code.value}_-_{lib_name}_"


class SimulationChecker(ABC):
    """Abstract base class for simulation success checkers.

    All code-specific checkers must inherit from this class and implement
    the check_success method with the same signature.
    """

    @abstractmethod
    def check_success(self, files: list[str]) -> bool:
        """Check if a simulation run was successful.

        Parameters
        ----------
        files : list[str]
            List of output files to check for success.

        Returns
        -------
        bool
            True if the simulation completed successfully, False otherwise.
        """
        pass


class MCNPChecker(SimulationChecker):
    """Checker for MCNP simulations."""

    def check_success(self, files: list[str]) -> bool:
        """Check if MCNP run was successful by verifying output files exist."""
        return MCNPSimOutput.is_successfully_simulated(files)


class OpenMCChecker(SimulationChecker):
    """Checker for OpenMC simulations."""

    def check_success(self, files: list[str]) -> bool:
        """Check if OpenMC run was successful by verifying output files exist."""
        return OpenMCSimOutput.is_successfully_simulated(files)


class SerpentChecker(SimulationChecker):
    """Checker for Serpent simulations."""

    def check_success(self, files: list[str]) -> bool:
        """Check if Serpent run was successful."""
        # TODO implement the logic to check if the Serpent run was successful
        raise NotImplementedError("Serpent checker not yet implemented")


class D1SChecker(SimulationChecker):
    """Checker for D1S simulations."""

    def check_success(self, files: list[str]) -> bool:
        """Check if D1S run was successful (uses same logic as MCNP)."""
        return MCNPChecker().check_success(files)


def get_jade_version() -> str:
    try:
        return importlib.metadata.version("jade")
    except importlib.metadata.PackageNotFoundError:
        return importlib.metadata.version("jadevv")


def add_rmode0(path: PathLike) -> None:
    """Given a folder, iteratively search for MCNP input files and add the RMODE 0
    card if it is not present."""
    pattern = re.compile(r"rmode 0", re.IGNORECASE)
    for pathroot, folder, filelist in os.walk(path):
        # if the folder name is mcnp
        if os.path.basename(pathroot) == "mcnp":
            for file in filelist:
                if file.endswith(".i"):
                    with open(os.path.join(pathroot, file)) as f:
                        lines = f.readlines()
                    # Remove trailing empty lines at the end of file
                    while lines and lines[-1].strip() == "":
                        lines.pop()
                    with open(os.path.join(pathroot, file), "w") as f:
                        found = False
                        for line in lines:
                            if pattern.match(line):
                                found = True
                            f.write(line)
                        if not found:
                            if not lines[-1].endswith("\n"):
                                f.write("\n")
                            f.write("RMODE 0\n")


# Dictionary mapping CODE enums to checker instances
# All checkers implement the SimulationChecker interface
CODE_CHECKERS: dict[CODE, SimulationChecker] = {
    CODE.MCNP: MCNPChecker(),
    CODE.OPENMC: OpenMCChecker(),
    CODE.SERPENT: SerpentChecker(),
    CODE.D1S: D1SChecker(),
}


class VerboseSafeDumper(yaml.SafeDumper):
    """Avoid the use of aliases in the YAML file"""

    def ignore_aliases(self, data):
        return True


def same_index(
    index1: pd.Index | pd.MultiIndex, index2: pd.Index | pd.MultiIndex
) -> bool:
    """Check if two pandas indices are the same, allowing for small numerical differences."""
    if index1.nlevels != index2.nlevels:
        return False
    for level in range(index1.nlevels):
        subindex1 = index1.get_level_values(level)
        subindex2 = index2.get_level_values(level)
        if not subindex1.equals(subindex2):
            # Check if both indices are numeric and match within a tolerance
            try:
                idx1 = np.array(subindex1, dtype=float)
                idx2 = np.array(subindex2, dtype=float)
                if np.allclose(idx1, idx2, rtol=1e-3):
                    continue
                else:
                    return False
            except Exception:
                return False
    return True
