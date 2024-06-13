import sys
import os
import pytest

from jade.main import Session
from jade.configuration import Configuration
from f4enix.input.libmanager import LibManager
from jade.status import Status
from jade.computational import executeBenchmarksRoutines

cp = os.path.dirname(os.path.abspath(__file__))
path_jade = os.path.join(os.path.dirname(cp), "jade")

resources = os.path.join(cp, "TestFiles", "computational")
# CONFIG_FILE = os.path.join(resources, "mainconfig.xlsx")
root = os.path.dirname(cp)


class MockLog:
    def adjourn(self, msg):
        pass


class MockUpSession(Session):
    def __init__(self, tmpdir: os.PathLike, lm: LibManager, config: Configuration):
        self.conf = config
        self.path_comparison = os.path.join(tmpdir, "Post-Processing", "Comparisons")
        self.path_single = os.path.join(tmpdir, "Post-Processing", "Single_Libraries")
        self.path_pp = os.path.join(tmpdir, "Post-Processing")
        self.path_run = os.path.join(tmpdir, "Simulations")
        self.path_test = os.path.join(tmpdir, "Test")
        # self.path_templates = os.path.join(resources, "templates")
        self.path_cnf = os.path.join(
            path_jade, "default_settings", "Benchmarks_Configuration"
        )
        self.path_quality = None
        self.path_uti = None
        self.lib_manager = lm
        self.path_inputs = os.path.join(resources, "inputs")

        keypaths = [
            self.path_pp,
            self.path_comparison,
            self.path_single,
            self.path_test,
            self.path_run,
        ]

        for path in keypaths:
            if not os.path.exists(path):
                os.mkdir(path)

        self.state = Status(self)
        self.log = MockLog()


@pytest.fixture()
def config() -> Configuration:
    conf = Configuration(os.path.join(cp, "TestFiles", "computational", "config.xlsx"))
    # override the path to xsdirs
    conf.lib["MCNP"] = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
    return conf


@pytest.fixture()
def lm(config: Configuration) -> LibManager:
    activation_file = os.path.join(
        cp, "TestFiles", "libmanager", "Activation libs.xlsx"
    )
    # XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
    isotopes_file = os.path.join(root, "jade", "resources", "Isotopes.txt")

    return LibManager(
        config.lib, activationfile=activation_file, isotopes_file=isotopes_file
    )


@pytest.fixture()
def session_mock(
    tmpdir: os.PathLike, lm: LibManager, config: Configuration
) -> MockUpSession:
    session = MockUpSession(tmpdir, lm, config)
    return session


def test_executeBenchmarksRoutines(session_mock: MockUpSession):
    # Generate sphere inputs
    lib = "31c"
    runoption = "c"  # should not change anything
    exp = False
    executeBenchmarksRoutines(session_mock, lib, runoption, exp)
