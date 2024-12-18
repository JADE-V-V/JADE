from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from jade.helper.aux_functions import (
    CODE_CHECKERS,
    PathLike,
    get_code_lib,
)
from jade.helper.constants import CODE


class GlobalStatus:
    def __init__(self, simulations_path: PathLike, raw_results_path: PathLike):
        """Class to store the global status of the simulations.

        Parameters
        ----------
        simulations_path : PathLike
            path to the simulations folder.
        raw_results_path : PathLike
            path to the raw results folder.

        Attributes
        ----------
        simulations : dict[tuple[CODE, str, str], CodeLibRunStatus]
            dictionary with the status of the simulations. eys are tuples with the code,
            library and benchmark name.
        raw_data : dict[tuple[CODE, str, str], list[str]]
            dictionary with the list of benchmarks for which the raw results where
            processed. keys are tuples with the code, library and benchmark name.
        """
        self.simulations_path = simulations_path
        self.raw_results_path = raw_results_path
        self.update()

    def update(self):
        """Update the status of the simulations and raw results"""
        self.simulations = self._parse_simulations_folder(self.simulations_path)
        self.raw_data = self._parse_raw_results_folder(self.raw_results_path)

    def _parse_simulations_folder(
        self, simulations_path: PathLike
    ) -> dict[tuple[CODE, str, str], CodeLibRunStatus]:
        simulations = {}
        for code_lib in os.listdir(simulations_path):
            # Do it only for folders, you never know
            codelibpath = Path(simulations_path, code_lib)
            if not codelibpath.is_dir():
                continue
            code_tag, lib = get_code_lib(code_lib)
            code = CODE(code_tag)

            for benchmark in os.listdir(codelibpath):
                metadata = None
                bench_path = Path(codelibpath, benchmark)
                if not bench_path.is_dir():
                    continue
                successful = []
                failed = []
                for sub_bench in os.listdir(bench_path):
                    # check if the run was successful
                    sub_bench_path = Path(bench_path, sub_bench)
                    success = CODE_CHECKERS[code](sub_bench_path)
                    if success:
                        successful.append(sub_bench)
                    else:
                        failed.append(sub_bench)

                    if metadata is None:
                        # They should all be the same, so just read the first one
                        with open(
                            os.path.join(sub_bench_path, "metadata.json")
                        ) as infile:
                            metadata = json.load(infile)

                # store the status
                status = CodeLibRunStatus(
                    code=code,
                    lib=lib,
                    metadata=metadata,
                    path=os.path.join(simulations_path, code_lib),
                    successful_simulations=successful,
                    failed_simulations=failed,
                )
                # store the status
                simulations[(code, lib, benchmark)] = status
        return simulations

    def _parse_raw_results_folder(
        self, path_raw: PathLike
    ) -> dict[tuple[CODE, str, str], list[str]]:
        # simply store a dictionary with the processed raw results
        available_raw_data = {}
        for code_lib in os.listdir(path_raw):
            codelib_path = Path(path_raw, code_lib)
            if not codelib_path.is_dir():
                continue
            code, lib = get_code_lib(code_lib)
            for benchmark in os.listdir(codelib_path):
                bench_path = Path(codelib_path, benchmark)
                if not bench_path.is_dir():
                    continue
                available_raw_data[(CODE(code), lib, benchmark)] = os.listdir(
                    bench_path
                )
        return available_raw_data

    def was_simulated(self, code: CODE, lib: str, benchmark: str) -> bool:
        """Check if a simulation was already performed and if it was successful.

        Parameters
        ----------
        code : CODE
            code used in the simulation.
        lib : str
            library used in the simulation. Extended name.
        benchmark : str
            (short) name of the benchmark.

        Returns
        -------
        bool
            Treu if the simulation was performed and successful, False otherwise.
        """
        try:
            result = self.simulations[(code, lib, benchmark)]
            return result.success
        except KeyError:  # not simulated then
            return False

    def get_successful_simulations(
        self,
    ) -> dict[tuple[CODE, str, str], CodeLibRunStatus]:
        """Get the list of successful simulations.

        Returns
        -------
        dict[tuple[CODE, str, str], CodeLibRunStatus]
            dictionary of only successful simulations.
        """
        successful_simulations = {}
        for key, result in self.simulations.items():
            if result.success:
                successful_simulations[key] = result

        return successful_simulations


@dataclass
class CodeLibRunStatus:
    """Status of a simulation for a given code and library.

    Attributes
    ----------
    code : CODE
        code used in the simulation.
    lib : str
        library used in the simulation. Extended name
    metadata : dict
        metadata of the simulation.
    path : PathLike
        path to the simulation folder.
    successful_simulations : list[str], optional
        list of successful simulations (subfolder names)
    failed_simulations : list[str], optional
        list of failed simulations (subfolder names)
    success : bool
        flag indicating if the simulation was successful or not. It is True if
        there are no failed simulations, False otherwise.
    """

    code: CODE
    lib: str
    metadata: dict
    path: PathLike
    # the list of successful / failed simulations
    successful_simulations: list[str]
    failed_simulations: list[str]

    def __post_init__(self):
        if self.failed_simulations is not None and len(self.failed_simulations) > 0:
            self.success = False
        else:
            self.success = True
