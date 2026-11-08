from __future__ import annotations

import os
import shutil
from importlib.resources import as_file, files
from pathlib import Path

import pandas as pd
import pytest
from f4enix import Input

from jade.config.run_config import LibraryOpenMC
from jade.helper.aux_functions import (
    add_rmode0,
    get_code_lib,
    get_code_lib_version,
    print_code_lib,
    same_index,
    sanitize_code_version,
    unpack_codelib,
    version_sort_key,
)
from jade.helper.constants import CODE
from tests.config import resources as conf_res
from tests.helper import res as helper_res


def test_code_lib():
    code = CODE.MCNP
    with as_file(files(conf_res).joinpath("cross_sections.xml")) as file:
        lib = LibraryOpenMC(name="FENDL 3.2c", path=file)
    code_lib = print_code_lib(code, lib)

    assert get_code_lib(code_lib) == (code.value, lib.name)


def test_code_lib_version():
    # version is optional and round-trips
    codelib = print_code_lib(CODE.OPENMC, "FENDL 3.2c", version="0.15.0")
    assert codelib == "_openmc_-_0.15.0_-_FENDL 3.2c_"
    assert get_code_lib_version(codelib) == ("openmc", "FENDL 3.2c", "0.15.0")
    # get_code_lib ignores the version
    assert get_code_lib(codelib) == ("openmc", "FENDL 3.2c")
    # legacy strings have no version
    assert get_code_lib_version("_mcnp_-_FENDL 3.2c_") == ("mcnp", "FENDL 3.2c", None)
    assert get_code_lib_version("_exp_-_exp_") == ("exp", "exp", None)
    # pretty format
    assert print_code_lib(CODE.MCNP, "FENDL 3.2c", pretty=True) == "mcnp - FENDL 3.2c"
    assert (
        print_code_lib(CODE.MCNP, "FENDL 3.2c", pretty=True, version="6.2")
        == "mcnp 6.2 - FENDL 3.2c"
    )


@pytest.mark.parametrize(
    "string",
    ["mcnp_-_lib", "_mcnp_", "_mcnp_-__", "_a_-_b_-_c_-_d_", "", "_"],
)
def test_code_lib_version_invalid(string):
    with pytest.raises(ValueError):
        get_code_lib_version(string)


def test_sanitize_code_version():
    assert sanitize_code_version(None) is None
    assert sanitize_code_version("  ") is None
    assert sanitize_code_version("0.15.0") == "0.15.0"
    assert sanitize_code_version("6.3/beta") == "6.3-beta"
    assert sanitize_code_version("a_-_b") == "a-b"
    # result can always be embedded and parsed back
    version = sanitize_code_version('x:y_-_z"')
    codelib = print_code_lib(CODE.MCNP, "lib", version=version)
    assert get_code_lib_version(codelib)[2] == version


def test_version_sort_key():
    versions = ["0.15.0", None, "0.9.1", "0.14.3", "6.2", "6.10"]
    assert sorted(versions, key=version_sort_key) == [
        None,
        "0.9.1",
        "0.14.3",
        "0.15.0",
        "6.2",
        "6.10",
    ]


def test_unpack_codelib():
    assert unpack_codelib(("mcnp", "lib")) == (CODE.MCNP, "lib", None)
    assert unpack_codelib(("openmc", "lib", "0.15.0")) == (CODE.OPENMC, "lib", "0.15.0")


def test_same_index():
    index1 = pd.MultiIndex.from_tuples([(1, 2.0), (2, 3.0), (3, 4.0)])
    index2 = pd.MultiIndex.from_tuples([(1, 2.0), (2, 3.0), (3, 4.0)])
    index3 = pd.MultiIndex.from_tuples([(1, 2.0), (2, 3.1), (3, 4.0)])
    index4 = pd.MultiIndex.from_tuples([(1, 2.0), (2, 3.0), ("a", 4.0)])
    index5 = pd.MultiIndex.from_tuples([(1, 2.0), (2, 3.0)])
    index6 = pd.Index([1, 2, 3])
    index7 = pd.Index([1, "b", 3])
    index8 = pd.Index([1, 2, 3])

    assert same_index(index1, index2) is True
    assert same_index(index1, index3) is False
    assert same_index(index1, index4) is False
    assert same_index(index1, index5) is False
    assert same_index(index6, index7) is False
    assert same_index(index6, index8) is True


def test_add_rmode0(tmp_path: Path):
    src = files(helper_res).joinpath("rmode")
    dst = tmp_path.joinpath("root/mcnp")
    shutil.copytree(src=src, dst=dst)
    add_rmode0(dst)
    # Verify that the card is properly added
    for file in os.listdir(dst):
        if file.endswith(".i"):
            inp = Input.from_input(dst.joinpath(file))
            assert "RMODE" in inp.other_data, (
                f"RMODE card not found in the input file {file}"
            )
