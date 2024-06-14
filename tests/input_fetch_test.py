import sys
import os
import shutil
import pandas as pd

cp = os.path.dirname(os.path.abspath(__file__))
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)
sys.path.insert(1, root)

from jade.input_fetch import fetch_iaea_inputs
from jade.libmanager import LibManager


ACTIVATION_FILE = os.path.join(cp, "TestFiles", "libmanager", "Activation libs.xlsx")
XSDIR_FILE = os.path.join(cp, "TestFiles", "libmanager", "xsdir")
ISOTOPES_FILE = os.path.join(root, "jade", "resources", "Isotopes.txt")


class SessionMockup:

    def __init__(self, uti_path, input_path, exp_data_path):
        df_rows = [
            ["99c", "sda", "", XSDIR_FILE, XSDIR_FILE],
            ["98c", "acsdc", "", XSDIR_FILE, XSDIR_FILE],
            ["21c", "adsadsa", "", XSDIR_FILE, None],
            ["31c", "adsadas", "", XSDIR_FILE, None],
            ["00c", "sdas", "yes", XSDIR_FILE, None],
            ["71c", "sdasxcx", "", XSDIR_FILE, None],
        ]
        df_lib = pd.DataFrame(df_rows)
        df_lib.columns = ["Suffix", "Name", "Default", "MCNP", "d1S"]
        self.lib_manager = LibManager(
            df_lib, activationfile=ACTIVATION_FILE, isotopes_file=ISOTOPES_FILE
        )
        # Always use fixtures for temporary directories
        self.path_uti = uti_path
        self.path_exp_res = exp_data_path
        self.conf = ConfMockup()
        if input_path is not None:
            self.path_inputs = input_path


class ConfMockup:

    def __init__(self):
        self.lib = pd.DataFrame(
            [["00c", "A"], ["31c", "B"]], columns=["Suffix", "name"]
        ).set_index("Suffix")


def test_fetch_iaea_inputs(tmpdir, monkeypatch):
    """ " Test that benchmarks can be correctly fetched from the IAEA website.
    test also the overwriting"""
    session = SessionMockup(
        tmpdir.mkdir("uty"), tmpdir.mkdir("inputs"), tmpdir.mkdir("exp")
    )

    # test correct fetching in an empty folder
    fetch_iaea_inputs(session)
    assert len(os.listdir(session.path_inputs)) > 0
    assert len(os.listdir(session.path_exp_res)) > 0

    # test overwriting
    # clean everything
    shutil.rmtree(session.path_inputs)
    os.mkdir(session.path_inputs)
    # copy a dummy folder
    dummy = os.path.join(cp, "TestFiles", "utilitiesgui", "Sphere")
    shutil.copytree(dummy, os.path.join(session.path_inputs, "Sphere"))

    # do not override
    msg = ""
    inputs = iter(["n"])
    monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
    fetch_iaea_inputs(session)
    assert len(os.listdir(session.path_inputs)) == 1

    # override
    inputs = iter(["y"])
    monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
    fetch_iaea_inputs(session)
    assert len(os.listdir(session.path_inputs)) > 1
    assert len(os.listdir(session.path_exp_res)) > 0
    assert os.path.exists(os.path.join(session.path_inputs, "Sphere", "mcnp"))
    assert os.path.exists(
        os.path.join(session.path_exp_res, "Oktavian", "Al", "Oktavian_Al_21.csv")
    )

    # override again, there could be a bug with single files instead of folders
    inputs = iter(["y"])
    monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
    fetch_iaea_inputs(session)
    assert len(os.listdir(session.path_inputs)) > 1

    # # check failed authentication (this can be used later for gitlab)
    # # try to get the token from local secret file
    # try:
    #     with open(os.path.join(cp, "secrets.json"), "r", encoding="utf-8") as infile:
    #         token = json.load(infile)["github"]
    # except FileNotFoundError:
    #     # Then try to get it from GitHub workflow secrets
    #     token = os.getenv("ACCESS_TOKEN_GITHUB")
    # inputs = iter(["y"])
    # monkeypatch.setattr("builtins.input", lambda msg: next(inputs))
    # ans = fetch_iaea_inputs(session, authorization_token="wrongtoken")
    # assert not ans
