from __future__ import annotations

from jade.config.run_config import LibraryOpenMC
from jade.helper.aux_functions import get_code_lib, print_code_lib
from jade.helper.constants import CODE


def test_code_lib():
    code = CODE.MCNP
    lib = LibraryOpenMC(name="FENDL 3.2c", path="test")
    code_lib = print_code_lib(code, lib)

    assert get_code_lib(code_lib) == (code.value, lib.name)
