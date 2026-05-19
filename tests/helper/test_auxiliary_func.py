from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path
from f4enix import Input
import pandas as pd
import os

from jade.config.run_config import LibraryOpenMC
from jade.helper.aux_functions import (
    get_code_lib,
    print_code_lib,
    same_index,
    add_rmode0,
)
import shutil
from jade.helper.constants import CODE
from tests.config import resources as conf_res
from tests.helper import res as helper_res


def test_code_lib():
    code = CODE.MCNP
    with as_file(files(conf_res).joinpath("cross_sections.xml")) as file:
        lib = LibraryOpenMC(name="FENDL 3.2c", path=file)
    code_lib = print_code_lib(code, lib)

    assert get_code_lib(code_lib) == (code.value, lib.name)


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
            assert "RMODE" in inp.other_data.keys(), (
                f"RMODE card not found in the input file {file}"
            )
