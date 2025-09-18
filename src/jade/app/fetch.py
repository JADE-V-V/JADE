from __future__ import annotations

import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import gitlab
import requests

from jade.helper.aux_functions import PathLike

BRANCH = "main"  # TODO change in main once merged the PR
IAEA_URL = f"https://github.com/IAEA-NDS/open-benchmarks/archive/{BRANCH}.zip"


def _fetch_from_git(
    url: str, authorization_token: str | None = None
) -> PathLike | bool:
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
    extracted_folder = _extract_zip(response.content, os.path.basename(url))
    return extracted_folder


def _extract_zip(zip_content, dest: PathLike) -> PathLike:
    tmpdirname = tempfile.gettempdir()
    tmp_zip = os.path.join(tmpdirname, dest)
    extracted_folder = os.path.join(tmpdirname, "extracted")
    with open(tmp_zip, "wb") as f:
        f.write(zip_content)
    # Extract the zip file
    with zipfile.ZipFile(tmp_zip, "r") as zip_ref:
        main_folder_name = zip_ref.namelist()[0]
        zip_ref.extractall(extracted_folder)

    return Path(extracted_folder, main_folder_name)


def fetch_from_gitlab(
    url: str, path: str, branch: str, authorization_token: str = None
) -> PathLike | bool:
    """Download a repository from GitLab and extract
    it to a temporary folder. It can also deal with authentication. Supported
    authentication is by token.
    Parameters
    ----------
    url : str
        path to the gitlab website (e.g. https://git.oecd-nea.org/)
    path : str
        path to the repository (e.g. /sinbad/sinbad.v2/sinbad-version-2-volume-1/FUS-ATN-BLK-STR-PNT-001-FNG-Osaka-Aluminium-Sphere-OKTAVIAN-oktav_al)
    branch : str, optional
        Branch to download. Default is jade.
    authorization_token : str, optional
        Authorization token to access the IAEA repository. Default is None.
    Returns
    -------
    extracted_folder: Pathlike | bool
        path to the extracted folder. False if the download was not successful.
    """
    gl = gitlab.Gitlab(url=url, private_token=authorization_token, ssl_verify=False)
    try:
        gl.auth()
    except gitlab.exceptions.GitlabAuthenticationError:
        logging.error("Gitlab authentication failed")
        return False

    # select the correct project
    found = False
    for project in gl.projects.list():
        if path == project.path_with_namespace:
            found = True
            break
    if not found:
        logging.error(f"Successful authentication but project {path} not found")
        return False

    binary = project.repository_archive(sha=branch, format="zip")
    return _extract_zip(binary, os.path.basename(path) + ".zip")


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


def _install_standard_folder_structure(
    extracted_folder: str | os.PathLike,
    inputs_root: PathLike,
    exp_data_root: PathLike,
    path_to_inputs: str | os.PathLike,
    path_to_exp_data: str | os.PathLike,
) -> bool:
    if isinstance(extracted_folder, bool):
        return False

    for fetched_folder, install_folder in [
        (path_to_inputs, inputs_root),
        (path_to_exp_data, exp_data_root),
    ]:
        _install_data(fetched_folder, install_folder)

    # Once done, delete the src folder
    shutil.rmtree(extracted_folder)

    return True


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
    extracted_folder = str(_fetch_from_git(IAEA_URL))  # no token required anymore

    path_to_inputs = Path(extracted_folder, "jade_open_benchmarks", "inputs")
    path_to_exp_data = Path(
        extracted_folder,
        "jade_open_benchmarks",
        "exp_results",
    )
    success = _install_standard_folder_structure(
        extracted_folder, inputs_root, exp_data_root, path_to_inputs, path_to_exp_data
    )
    return success


def fetch_f4e_inputs(
    inputs_root: PathLike, exp_data_root: PathLike, access_token: str
) -> bool:
    """Fetch F4E benchmark inputs and experimental data and copy them to
    the correct folder in jade structure. This will always override the available
    data.

    Parameters
    ----------
    inputs_root : PathLike
        path to the root folder where the inputs will be stored.
    exp_data_root : PathLike
        path to the root folder where the experimental data will be stored.
    access_token : str
        Authorization token to access the F4E GitLab.

    Returns
    -------
    bool
        True if the inputs were successfully fetched, False otherwise.
    """
    extracted_folder = fetch_from_gitlab(
        "https://eng-gitlab.f4e.europa.eu/",
        "f4e-projects/jade-benchmarks",
        "main",
        authorization_token=access_token,
    )
    if not extracted_folder:  # authentication went wrong
        return False
    if not isinstance(extracted_folder, PathLike):  # anything else that went wrong
        return False
    path_to_inputs = Path(extracted_folder, "inputs")
    path_to_exp_data = Path(
        extracted_folder,
        "exp_results",
    )
    success = _install_standard_folder_structure(
        extracted_folder, inputs_root, exp_data_root, path_to_inputs, path_to_exp_data
    )
    return success
