from __future__ import annotations

import importlib.metadata
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Union

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
    code = CODE_PATTERN.search(string).group()[1:-2]  # remove the "<" and ">-"
    lib = LIB_PATTERN.search(string).group()[2:-1]  # remove the "-<" and ">"
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


def check_run_mcnp(folder: PathLike) -> bool:
    """check if mcnp run was successful"""
    try:
        MCNPSimOutput.retrieve_files(folder)
        return True
    except FileNotFoundError:
        return False


def check_run_openmc(folder: PathLike) -> bool:
    """check if openmc run was successful"""
    try:
        OpenMCSimOutput.retrieve_file(folder)
        return True
    except FileNotFoundError:
        return False


def check_run_serpent(folder: PathLike) -> bool:
    # TODO implement the logic to check if the Serpent run was successful
    raise NotImplementedError


def check_run_d1s(folder: PathLike) -> bool:
    """check if d1s run was successful"""
    return check_run_mcnp(folder)


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
                    with open(os.path.join(pathroot, file), "w") as f:
                        found = False
                        for line in lines:
                            if pattern.match(line):
                                found = True
                            f.write(line)
                        if not found:
                            f.write("RMODE 0\n")


CODE_CHECKERS = {
    CODE.MCNP: check_run_mcnp,
    CODE.OPENMC: check_run_openmc,
    CODE.SERPENT: check_run_serpent,
    CODE.D1S: check_run_d1s,
}


class VerboseSafeDumper(yaml.SafeDumper):
    """Avoid the use of aliases in the YAML file"""

    def ignore_aliases(self, data):
        return True
