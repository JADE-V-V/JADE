from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jade.config.run_config import Library
from jade.helper.aux_functions import PathLike, print_code_lib
from jade.helper.constants import CODE


class PathsTree:
    def __init__(self, root: PathLike):
        """Class to store the paths of the JADE project.

        Parameters
        ----------
        root : PathLike
            path to the root of the JADE project.
        """
        self.root = root
        # build all paths
        self.benchmark_input_templates = Path(root, "benchmark_templates")
        self.cfg = CfgTree(Path(root, "cfg"))
        self.simulations = Path(root, "simulations")
        self.raw = Path(root, "raw_data")
        self.logs = Path(root, "logs")
        self.postprocessing = Path(root, "post_processing")

        # if the experimental data folder is not available, create it
        exp_data = Path(self.raw, "_exp_-_exp_")

        self.exp_data = exp_data

    def check_not_installed_folders(self, path: PathLike) -> bool:
        """Checks that none of the layer 1 folders exist in the the specified path.

        Parameters
        ----------
        path : PathLike
            path to check

        Raises
        ------
        bool
            If True, none of the layer 1 folder is present in the path and jade can
            be installed.
        """
        to_check = [
            "simulations",
            "raw_data",
            "logs",
            "post_processing",
            "benchmark_templates",
            "cfg",
        ]
        for item in os.listdir(path):
            if item in to_check:
                return False
        return True

    def init_tree(self) -> None:
        """Initialize the JADE project tree."""
        # create the folders if they don't exist
        for folder in [
            self.benchmark_input_templates,
            Path(self.root, "cfg"),
            self.logs,
            self.raw,
            self.simulations,
            self.postprocessing,
            self.exp_data,
        ]:
            os.makedirs(folder, exist_ok=True)

    def get_bench_sim_folders(
        self, code: CODE, lib: str | Library, bench: str
    ) -> list[tuple[Path, str]]:
        """Get the simulation folders (single runs) for a given benchmark.

        Parameters
        ----------
        code : CODE
            code used for the simulations
        lib : str | Library
            library used for the simulations
        bench : str
            benchmark name

        Returns
        -------
        list[tuple[Path, str]]
            list of tuples with the folder path and the folder name of a single run
        """
        folders = []
        bench_simulations = Path(self.simulations, print_code_lib(code, lib), bench)
        for folder in os.listdir(bench_simulations):
            simfolder = Path(bench_simulations, folder)
            if simfolder.is_dir():
                folders.append((simfolder, folder))

        return folders

    def get_new_post_bench_path(self, bench: str) -> Path:
        """A new folder (date based) is provided for the postprocessing of
        a specific benchamrk.

        Parameters
        ----------
        bench : str
            benchmark name

        Returns
        -------
        Path
            path to the postprocessing folder
        """
        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = Path(self.postprocessing, bench, time)
        os.makedirs(path, exist_ok=True)
        return path


class CfgTree:
    def __init__(self, root: PathLike):
        """Class to store the paths of the configuration files.

        Parameters
        ----------
        root : PathLike
            path to the root of the JADE project.
        """
        self.path = root
        self.batch_templates = Path(root, "batch_templates")
        self.bench_additional_files = Path(root, "benchmarks")
        self.bench_pp = Path(root, "benchmarks_pp")
        self.bench_raw = Path(root, "benchmarks_pp/raw")
        self.exe_cfg = Path(root, "exe_cfg")
        self.env_vars_file = Path(root, "env_vars_cfg.yml")
        self.libs_cfg = Path(root, "libs_cfg.yml")
        self.run_cfg = Path(root, "run_cfg.yml")
        self.pp_cfg = Path(root, "pp_cfg.yml")
