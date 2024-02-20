import os
import sys
import pytest
from jade.main import Session
from jade.configuration import Configuration

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

resources = os.path.join(cp, "TestFiles", "expoutput")
import jade.expoutput as expoutput
import jade.output as outp

CONFIG_FILE_EXP = os.path.join(resources, "mainconfig.xlsx")


# I don't want to deal with testing the Session object itself for the moment
class MockUpSession(Session):
    def __init__(self):
        self.conf = Configuration(CONFIG_FILE_EXP)


class TestExpOutput:
    @pytest.fixture(autouse=True)
    def setup(self):
        session = MockUpSession()
        config = session.conf.comp_default.set_index("Description")
        session.path_comparison = os.path.join(
            resources, "Post-Processing", "Comparison"
        )
        session.path_single = os.path.join(
            resources, "Post-Processing", "Single_Libraries"
        )
        session.path_exp_res = os.path.join(resources, "exp_res")
        session.path_pp = os.path.join(resources, "Post-Processing")
        session.path_run = os.path.join(resources, "Simulations")
        session.path_test = resources
        self.exp_output = outp.BenchmarkOutput(["32c", "31c"], config, session)
