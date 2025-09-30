from __future__ import annotations

import os

import pytest

from jade.app.fetch import fetch_f4e_inputs, fetch_iaea_inputs

# By default this should set the token to None if not found
F4E_GITLAB_TOKEN = os.getenv("F4E_GITLAB_TOKEN")


def test_fetch_iaea_inputs(tmpdir):
    """ " Test that benchmarks can be correctly fetched from the IAEA website.
    test also the overwriting"""
    # test correct fetching in an empty folder
    inp_path = tmpdir.mkdir("inputs")
    exp_path = tmpdir.mkdir("exp")
    success = fetch_iaea_inputs(inp_path, exp_path)
    assert success
    assert len(os.listdir(inp_path)) > 0
    assert len(os.listdir(exp_path)) > 0

    # test that there no problems when the folder is not empty
    success = fetch_iaea_inputs(inp_path, exp_path)
    assert success
    assert len(os.listdir(inp_path)) > 0
    assert len(os.listdir(exp_path)) > 0

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


def test_wrong_fetch_f4e_inputs(tmpdir):
    """ " Test that benchmarks can be correctly fetched from the IAEA website.
    test also the overwriting"""
    # test correct fetching in an empty folder
    inp_path = tmpdir.mkdir("inputs")
    exp_path = tmpdir.mkdir("exp")
    success = fetch_f4e_inputs(inp_path, exp_path, access_token="wrongtoken")
    assert not success


@pytest.mark.skipif(F4E_GITLAB_TOKEN is None, reason="No token found")
def test_fetch_f4e_inputs(tmpdir):
    assert F4E_GITLAB_TOKEN is not None
    # test correct fetching in an empty folder
    inp_path = tmpdir.mkdir("inputs")
    exp_path = tmpdir.mkdir("exp")
    success = fetch_f4e_inputs(inp_path, exp_path, F4E_GITLAB_TOKEN)
    assert success
    assert len(os.listdir(inp_path)) > 0
    assert len(os.listdir(exp_path)) > 0

    # test that there no problems when the folder is not empty
    success = fetch_f4e_inputs(inp_path, exp_path, F4E_GITLAB_TOKEN)
    assert success
    assert len(os.listdir(inp_path)) > 0
    assert len(os.listdir(exp_path)) > 0
