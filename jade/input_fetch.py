from __future__ import annotations
from typing import TYPE_CHECKING
import tempfile
import os
import shutil
import zipfile
import requests

from jade.utilitiesgui import input_with_options

if TYPE_CHECKING:
    import jade.main


IAEA_URL = r"https://github.com/IAEA-NDS/open-benchmarks/archive/main.zip"


def fetch_from_git(
    url: str, authorization_token: str = None, user: str = None, password: str = None
) -> str:
    """Download a repository from GitHub/GitLab and extract
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
