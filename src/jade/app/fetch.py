from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

from jade.helper.aux_functions import PathLike

BRANCH = "jadev4"  # TODO change in main once merged the PR
IAEA_URL = f"https://github.com/IAEA-NDS/open-benchmarks/archive/{BRANCH}.zip"


def _fetch_from_git(url: str, authorization_token: str | None = None) -> str | bool:
    """Download a repository from GitHub/GitLab and extract
    it to a temporary folder. It can also deal with authentication.

    Parameters
    ----------
    url : str
        pointer for the zip download
    authorization_token : str, optional
        Authorization token to access the IAEA repository. Default is None.

    Returns
    -------
    extracted_folder: str | bool
        path to the extracted folder. returns False if the download was not successful.
    """
    if authorization_token:
        headers = {"Authorization": f"token {authorization_token}"}
    else:
        headers = None
    # Download the repository as a zip file
    response = requests.get(
        url,
        timeout=1000,
        headers=headers,
    )
    # Ceck if the download was successful
    if response.status_code != 200:
        return False
    # Save the downloaded zip file
    tmpdirname = tempfile.gettempdir()
    tmp_zip = os.path.join(tmpdirname, os.path.basename(url))
    extracted_folder = os.path.join(tmpdirname, "extracted")
    with open(tmp_zip, "wb") as f:
        f.write(response.content)
    # Extract the zip file
    with zipfile.ZipFile(tmp_zip, "r") as zip_ref:
        zip_ref.extractall(extracted_folder)

    return extracted_folder


def _install_data(fetch_folder: str | os.PathLike, install_folder: str | os.PathLike):
    for item in os.listdir(fetch_folder):
        # The old folder needs to be deleted first, otherwise the new folder
        # is saved inside instead of substituting it
        newpath = os.path.join(install_folder, item)
        if os.path.exists(newpath) and os.path.isdir(newpath):
            shutil.rmtree(newpath)
        # Move the desired folder to the local directory
        shutil.move(
            os.path.join(fetch_folder, item),
            os.path.join(install_folder, item),
        )


def fetch_iaea_inputs(inputs_root: PathLike, exp_data_root: PathLike) -> bool:
    """Fetch IAEA benchmark inputs and experimental data and copy them to
    the correct folder in jade structure. This will always override the available
    data.

    Parameters
    ----------
    inputs_root : PathLike
        path to the root folder where the inputs will be stored.
    exp_data_root : PathLike
        path to the root folder where the experimental data will be stored.

    Returns
    -------
    bool
        True if the inputs were successfully fetched, False otherwise.
    """
    extracted_folder = _fetch_from_git(IAEA_URL)  # no token required anymore
    if isinstance(extracted_folder, bool):
        return False

    path_to_inputs = Path(
        extracted_folder, f"open-benchmarks-{BRANCH}", "jade_open_benchmarks", "inputs"
    )
    path_to_exp_data = os.path.join(
        extracted_folder,
        f"open-benchmarks-{BRANCH}",
        "jade_open_benchmarks",
        "exp_results",
    )

    for fetched_folder, install_folder in [
        (path_to_inputs, inputs_root),
        (path_to_exp_data, exp_data_root),
    ]:
        _install_data(fetched_folder, install_folder)

    return True
