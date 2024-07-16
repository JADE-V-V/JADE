from __future__ import annotations
from typing import TYPE_CHECKING
import tempfile
import os
import shutil
import zipfile
import requests
import logging

from jade.utilitiesgui import input_with_options
from jade.constants import NEA_TREE
import gitlab

if TYPE_CHECKING:
    import jade.main


IAEA_URL = r"https://github.com/IAEA-NDS/open-benchmarks/archive/main.zip"


def fetch_from_git(
    url: str, authorization_token: str = None, user: str = None, password: str = None
) -> str:
    """Download a repository from GitHub and extract
    it to a temporary folder. It can also deal with authentication. Supported
    authentication is either by token or by username and password.

    Parameters
    ----------
    url : str
        pointer for the zip download
    authorization_token : str, optional
        Authorization token to access the IAEA repository. Default is None.
    user : str, optional
        Username for authentication. Default is None.
    password : str, optional
        Password for authentication. Default is None.

    Returns
    -------
    extracted_folder: str
        path to the extracted folder
    """
    if authorization_token:
        headers = {"Authorization": f"token {authorization_token}"}
    elif user and password:
        headers = {"Authorization": f"Basic {user}:{password}"}
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

    return _extract_zip(response.content, os.path.basename(url))


def _extract_zip(binary_zip, dest_name) -> str:
    # Save the downloaded zip file
    tmpdirname = tempfile.gettempdir()
    tmp_zip = os.path.join(tmpdirname, dest_name)
    extracted_folder = os.path.join(tmpdirname, "extracted")
    # be sure to clean the folder before extracting
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)
    with open(tmp_zip, "wb") as f:
        f.write(binary_zip)
    # Extract the zip file
    with zipfile.ZipFile(tmp_zip, "r") as zip_ref:
        zip_ref.extractall(extracted_folder)

    return extracted_folder


def fetch_from_gitlab(
    url: str, path: str, authorization_token: str = None, branch: str = "jade"
) -> str:
    """Download a repository from GitLab and extract
    it to a temporary folder. It can also deal with authentication. Supported
    authentication is by token.

    Parameters
    ----------
    url : str
        path to the gitlab website (e.g. https://git.oecd-nea.org/)
    path : str
        path to the repository (e.g. /sinbad/sinbad.v2/sinbad-version-2-volume-1/FUS-ATN-BLK-STR-PNT-001-FNG-Osaka-Aluminium-Sphere-OKTAVIAN-oktav_al)
    authorization_token : str, optional
        Authorization token to access the IAEA repository. Default is None.
    branch : str, optional
        Branch to download. Default is jade.

    Returns
    -------
    extracted_folder: str
        path to the extracted folder
    """
    gl = gitlab.Gitlab(url=url, private_token=authorization_token)
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
        logging.error("Successful authentication but project %s not found" % path)
        return False

    binary = project.repository_archive(sha=branch, format="zip")
    return _extract_zip(binary, os.path.basename(path) + ".zip")


def _check_override(session: jade.main.Session, new_inputs: str | os.PathLike) -> bool:
    """Check if the inputs are already present"""
    # check which inputs are available and prompt for overwriting
    new = list(os.listdir(new_inputs))
    current = list(os.listdir(session.path_inputs))
    overwriting = False
    for benchmark in new:
        if benchmark in current:
            overwriting = True
            break

    return overwriting


def _install_data(fetch_folder: str | os.PathLike, install_folder: str | os.PathLike):
    for item in os.listdir(fetch_folder):
        # if install folder does not exist, create it
        if not os.path.exists(install_folder):
            os.makedirs(install_folder)
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


def fetch_iaea_inputs(session: jade.main.Session) -> bool:
    """Fetch IAEA benchmark inputs and experimental data and copy them to
    the correct folder in jade structure. In case the inputs
    were already present, the user is asked if they want to overwrite them.

    Parameters
    ----------
    session : jade.main.Session
        JADE session.

    Returns
    -------
    bool
        True if the inputs were successfully fetched, False otherwise.
    """
    extracted_folder = fetch_from_git(IAEA_URL)  # no token required anymore
    path_to_inputs = os.path.join(
        extracted_folder, "open-benchmarks-main", "jade_open_benchmarks", "inputs"
    )
    path_to_exp_data = os.path.join(
        extracted_folder, "open-benchmarks-main", "jade_open_benchmarks", "exp_results"
    )
    # Check if the new files are already present (only for inputs, we can fetch
    # the experimental data every time)
    overwriting = _check_override(session, path_to_inputs)

    # this should not be prompted during installation since no inputs are present
    if overwriting:
        msg = "The IAEA inputs are already present. Do you want to overwrite them? [y/n] -> "
        ans = input_with_options(msg, ["y", "n"])
        if ans == "n":
            return False

    for fetched_folder, install_folder in [
        (path_to_inputs, session.path_inputs),
        (path_to_exp_data, session.path_exp_res),
    ]:
        _install_data(fetched_folder, install_folder)

    return True


def fetch_nea_inputs(session: jade.main.Session) -> bool:
    """Fetch NEA benchmark inputs and experimental data and copy them to
    the correct folder in jade structure. In case the inputs
    were already present, the user is asked if they want to overwrite them.

    Parameters
    ----------
    session : jade.main.Session
        JADE session.

    Returns
    -------
    bool
        True if the inputs were successfully fetched, False otherwise.
    """
    # iterate on all the benchmarks
    yes_all = False
    for key, benchmark in NEA_TREE.items():
        # check if the benchmark is already present
        if key in os.listdir(session.path_inputs):
            # check for override only if the user did not select yes_all
            if not yes_all:
                msg = (
                    f"{key} is already present. Do you want to overwrite it? [y/n] -> "
                )
                ans = input_with_options(msg, ["y", "n", "y_all"])
                if ans == "n":
                    continue
                elif ans == "y_all":
                    yes_all = True
        # fetch the benchmark
        path = benchmark["path"]
        extracted_folder = fetch_from_gitlab(
            "https://git.oecd-nea.org/",
            path,
            authorization_token=session.conf.nea_token,
        )
        # there should only be one folder in the extraction folder
        root = os.listdir(extracted_folder)[0]
        # all benchmarks should have the same format
        exp_data = os.path.join(extracted_folder, root, "01_Experiment_Input", "jade")
        inputs = os.path.join(extracted_folder, root, "03_Benchmark_Model", "jade")
        # install the data
        _install_data(exp_data, os.path.join(session.path_exp_res, key))
        _install_data(inputs, os.path.join(session.path_inputs, key))
