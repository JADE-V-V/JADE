from __future__ import annotations

import os

from jade.app.fetch import fetch_iaea_inputs


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
