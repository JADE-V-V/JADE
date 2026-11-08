from __future__ import annotations

import importlib.metadata
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import yaml

if TYPE_CHECKING:
    from jade.config.run_config import Library
from jade.helper.constants import CODE
from jade.post.sim_output import MCNPSimOutput, OpenMCSimOutput

PathLike = str | os.PathLike | Path

CODELIB_SEP = "_-_"
# characters that cannot be part of a folder name on at least one supported OS
_INVALID_FOLDER_CHARS = re.compile(r'[<>:"/\\|?*\n\r\t]')


def get_code_lib(string) -> tuple[str, str]:
    """Extracts the code and library names from a code-lib string.

    Any code version contained in the string is ignored, use
    :func:`get_code_lib_version` to retrieve it.

    Parameters
    ----------
    string : str
        The code-lib string, e.g. _mcnp_-_FENDL 3.2c_ or
        _openmc_-_0.15.0_-_FENDL 3.2c_

    Returns
    -------
    tuple[str, str]
        The code and library names.
    """
    code, lib, _ = get_code_lib_version(string)
    return code, lib


def get_code_lib_version(string) -> tuple[str, str, str | None]:
    """Extracts the code, library and (optional) code version from a code-lib
    string.

    Parameters
    ----------
    string : str
        The code-lib string, e.g. _mcnp_-_FENDL 3.2c_ or
        _openmc_-_0.15.0_-_FENDL 3.2c_

    Returns
    -------
    tuple[str, str, str | None]
        The code, library and code version. The version is None if not present.

    Raises
    ------
    ValueError
        If the string is not a valid code-lib string.
    """
    string = str(string)
    if len(string) < 2 or not string.startswith("_") or not string.endswith("_"):
        raise ValueError(f"Invalid code-lib string: {string}")
    parts = string[1:-1].split(CODELIB_SEP)
    if len(parts) not in (2, 3) or any(len(part) == 0 for part in parts):
        raise ValueError(f"Invalid code-lib string: {string}")
    if len(parts) == 3:
        return parts[0], parts[2], parts[1]
    return parts[0], parts[1], None


def sanitize_code_version(version: str | None) -> str | None:
    """Make a code version string safe to be used in a folder name.

    Parameters
    ----------
    version : str | None
        raw code version as read from the simulation output.

    Returns
    -------
    str | None
        sanitized version, None if the version is missing or empty.
    """
    if version is None:
        return None
    version = _INVALID_FOLDER_CHARS.sub("-", str(version)).strip()
    # the code-lib separator cannot appear in the version
    version = version.replace(CODELIB_SEP, "-")
    version = version.strip("_")
    if version == "":
        return None
    return version


def version_sort_key(version: str | None) -> tuple:
    """Natural sorting key for code versions (e.g. 0.9.0 < 0.15.0).
    A missing version is always considered the oldest.

    Parameters
    ----------
    version : str | None
        code version.

    Returns
    -------
    tuple
        sorting key.
    """
    if version is None:
        return (0,)
    chunks = re.split(r"(\d+)", version)
    key = []
    for chunk in chunks:
        if chunk == "":
            continue
        if chunk.isdigit():
            key.append((1, int(chunk), ""))
        else:
            key.append((0, 0, chunk))
    return (1, tuple(key))


def unpack_codelib(
    codelib: tuple[str, str] | tuple[str, str, str | None],
) -> tuple[CODE, str, str | None]:
    """Unpack a (code, lib) or (code, lib, version) tuple.

    Parameters
    ----------
    codelib : tuple[str, str] | tuple[str, str, str | None]
        code-lib tuple, the code version is optional.

    Returns
    -------
    tuple[CODE, str, str | None]
        code, library and code version (None if not provided).
    """
    code = CODE(codelib[0])
    lib = codelib[1]
    version = codelib[2] if len(codelib) > 2 else None
    return code, lib, version


def print_code_lib(
    code: CODE,
    lib: Library | str,
    pretty: bool = False,
    version: str | None = None,
) -> str:
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
    version : str | None, optional
        The code version. If provided it is included in the code-lib string,
        by default None.

    Returns
    -------
    str
        The code-lib string, e.g. _mcnp_-_FENDL 3.2c_ or
        _openmc_-_0.15.0_-_FENDL 3.2c_
    """
    if isinstance(lib, str):
        lib_name = lib
    else:
        lib_name = lib.name

    if pretty:
        if version is None:
            return f"{code.value} - {lib_name}"
        return f"{code.value} {version} - {lib_name}"
    else:
        if version is None:
            return f"_{code.value}{CODELIB_SEP}{lib_name}_"
        return f"_{code.value}{CODELIB_SEP}{version}{CODELIB_SEP}{lib_name}_"


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


class ACTINVChecker(SimulationChecker):
    """Only the adapter publishes the marker, after validating a fresh result."""

    def check_success(self, files: list[str]) -> bool:
        return "result.json" in files and "actinv.complete" in files


# Dictionary mapping CODE enums to checker instances
# All checkers implement the SimulationChecker interface
CODE_CHECKERS: dict[CODE, SimulationChecker] = {
    CODE.MCNP: MCNPChecker(),
    CODE.OPENMC: OpenMCChecker(),
    CODE.SERPENT: SerpentChecker(),
    CODE.D1S: D1SChecker(),
    CODE.ACTINV: ACTINVChecker(),
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
            except (ValueError, TypeError):
                return False
    return True
