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
    def __init__(self, tmpdir):
        self.conf = Configuration(CONFIG_FILE_EXP)
        self.path_comparison = os.path.join(tmpdir, "Post-Processing", "Comparison")
        self.path_single = os.path.join(tmpdir, "Post-Processing", "Single_Libraries")
        self.path_exp_res = os.path.join(resources, "Experimental_Results")
        self.path_pp = os.path.join(tmpdir, "Post-Processing")
        self.path_run = os.path.join(resources, "Simulations")
        self.path_test = resources
        self.state = None
        self.path_templates = os.path.join(resources, "templates")
        self.path_cnf = os.path.join(resources, "Benchmarks_Configuration")
        self.path_quality = None
        self.path_uti = None
        self.path_comparison = os.path.join(tmpdir, "Post-Processing", "Comparisons")


class TestExpOutput:
    @pytest.fixture()
    def session_mock(self, tmpdir):
        session = MockUpSession(tmpdir)
        return session

    def test_benchmarkoutput(self, session_mock: MockUpSession):

        config = session_mock.conf.comp_default.set_index("Description")
        conf = config.iloc[1]
        os.makedirs(session_mock.path_comparison)
        os.makedirs(session_mock.path_single)
        self.benchoutput_32c = outp.BenchmarkOutput("32c", conf, session_mock)
        self.benchoutput_32c.single_postprocess()
        self.benchoutput_31c = outp.BenchmarkOutput("31c", conf, session_mock)
        self.benchoutput_31c.single_postprocess()
        self.benchoutput_comp = outp.BenchmarkOutput(["32c", "31c"], conf, session_mock)
        self.benchoutput_comp.compare()
        assert True

    def test_spectrumoutput(self, session_mock: MockUpSession):

        config = session_mock.conf.comp_default.set_index("Description")
        conf = config.iloc[1]
        os.makedirs(session_mock.path_comparison)
        os.makedirs(session_mock.path_single)
        self.benchoutput_32c = outp.BenchmarkOutput("32c", conf, session_mock)
        self.benchoutput_32c.single_postprocess()
        self.benchoutput_31c = outp.BenchmarkOutput("31c", conf, session_mock)
        self.benchoutput_31c.single_postprocess()
        self.benchoutput_comp = outp.BenchmarkOutput(["32c", "31c"], conf, session_mock)
        self.benchoutput_comp.compare()
        assert True
