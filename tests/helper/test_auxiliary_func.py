from __future__ import annotations

from importlib.resources import as_file, files

from jade.config.run_config import LibraryOpenMC
from jade.helper.aux_functions import get_code_lib, print_code_lib
from jade.helper.constants import CODE
from tests.config import resources as conf_res


def test_code_lib():
    code = CODE.MCNP
    with as_file(files(conf_res).joinpath("cross_sections.xml")) as file:
        lib = LibraryOpenMC(name="FENDL 3.2c", path=file)
    code_lib = print_code_lib(code, lib)

    assert get_code_lib(code_lib) == (code.value, lib.name)
