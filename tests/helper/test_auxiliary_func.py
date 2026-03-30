from __future__ import annotations

from importlib.resources import as_file, files

import pandas as pd

from jade.config.run_config import LibraryOpenMC
from jade.helper.aux_functions import get_code_lib, print_code_lib, same_index
from jade.helper.constants import CODE
from tests.config import resources as conf_res


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
