from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from jade.helper.aux_functions import (
    CODE_CHECKERS,
    PathLike,
    get_code_lib,
    get_code_lib_version,
    print_code_lib,
    version_sort_key,
)
from jade.helper.constants import CODE
from jade.helper.errors import VersionInconsistencyError


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
        raw_data : dict[tuple[CODE, str, str | None, str], list[str]]
            dictionary with the list of benchmarks for which the raw results where
            processed. keys are tuples with the code, library, code version and
            benchmark name. The code version is None for raw results stored without
            version (e.g. experimental data or results produced by older JADE
            versions).
        """
        self.simulations_path = simulations_path
        self.raw_results_path = raw_results_path
        self._simulations = None
        self._raw_data = None
        self._raw_metadata = None

    @property
    def simulations(self) -> dict[tuple[CODE, str, str], CodeLibRunStatus]:
        if self._simulations is None:
            self._simulations = self._parse_simulations_folder(self.simulations_path)
        return self._simulations

    @property
    def raw_data(self) -> dict[tuple[CODE, str, str | None, str], list[str]]:
        if self._raw_data is None:
            self._raw_data, self._raw_metadata = self._parse_raw_results_folder(
                self.raw_results_path
            )
        return self._raw_data

    @property
    def raw_metadata(self) -> dict[tuple[CODE, str, str | None, str], dict]:
        if self._raw_metadata is None:
            self._raw_data, self._raw_metadata = self._parse_raw_results_folder(
                self.raw_results_path
            )
        return self._raw_metadata

    def update_raw_results(self) -> None:
        """Update the raw results by re-parsing the raw results folder. It should be used
        after processing new raw results to update the status.
        """
        self._raw_data, self._raw_metadata = self._parse_raw_results_folder(
            self.raw_results_path
        )

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
                    success = CODE_CHECKERS[code].check_success(
                        os.listdir(sub_bench_path)
                    )
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
    ) -> tuple[
        dict[tuple[CODE, str, str | None, str], list[str]],
        dict[tuple[CODE, str, str | None, str], dict],
    ]:
        # simply store a dictionary with the processed raw results
        available_raw_data = {}
        metadata = {}
        for code_lib in os.listdir(path_raw):
            codelib_path = Path(path_raw, code_lib)
            if not codelib_path.is_dir():
                continue
            code, lib, version = get_code_lib_version(code_lib)
            for benchmark in os.listdir(codelib_path):
                bench_path = Path(codelib_path, benchmark)
                if not bench_path.is_dir():
                    continue
                key = (CODE(code), lib, version, benchmark)
                available_raw_data[key] = os.listdir(bench_path)
                if lib != "exp":  # for the experiments we don't have metadata
                    with open(os.path.join(bench_path, "metadata.json")) as infile:
                        metadata[key] = json.load(infile)
        return available_raw_data, metadata

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
            True if the simulation was performed and successful, False otherwise.
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

    def get_all_raw(self) -> tuple[set[str], set[str]]:
        """Get all the code-libraries and benchmarks for which the
        at least one raw data is available.

        Returns
        -------
        set[str]
            list of code-libraries (including the code version when available)
            for which the raw data was processed.
        set[str]
            list of benchmarks for which the raw data was processed.
        """
        code_libs = []
        benchmarks = []
        for code, lib, version, benchmark in self.raw_data:
            code_libs.append(print_code_lib(code, lib, version=version))
            benchmarks.append(benchmark)
        return set(code_libs), set(benchmarks)

    def get_codelibs_from_raw_benchmark(self, benchmarks: str | list[str]) -> set[str]:
        """Get the list of codelib for which the raw data of the requested benchmark
        is available.

        Parameters
        ----------
        benchmark : str | list[str]
            benchmark name.

        Returns
        -------
        set[str]
            list of codelib (including the code version when available) for which
            the raw data of the requested benchmark is available.
        """
        if isinstance(benchmarks, str):
            benchmarks = [benchmarks]

        codelibs = []
        for code, lib, version, bench in self.raw_data:
            if bench in benchmarks:
                codelibs.append(print_code_lib(code, lib, version=version))
        return set(codelibs)

    def get_benchmark_from_raw_codelib(self, codelibs: str | list[str]) -> set[str]:
        """Get the list of benchmarks for which the raw data of the requested codelib
        is available.

        Parameters
        ----------
        codelib : str | list[str]
            codelib name. If a codelib does not specify the code version, any
            available version is matched.

        Returns
        -------
        set[str]
            list of benchmarks for which the raw data of the requested codelib is available.
        """
        if isinstance(codelibs, str):
            codelibs = [codelibs]
        requests = [get_code_lib_version(codelib) for codelib in codelibs]

        benchmarks = []
        for code, lib, version, bench in self.raw_data:
            for req_code, req_lib, req_version in requests:
                if (
                    code.value == req_code
                    and lib == req_lib
                    and (req_version is None or req_version == version)
                ):
                    benchmarks.append(bench)
                    break
        return set(benchmarks)

    def get_raw_versions(
        self, code: CODE, lib: str, benchmark: str
    ) -> list[str | None]:
        """Get all the code versions for which raw data is available for a given
        code, library and benchmark.

        Parameters
        ----------
        code : CODE
            code used in the simulation.
        lib : str
            library name.
        benchmark : str
            benchmark name.

        Returns
        -------
        list[str | None]
            available code versions sorted from the oldest to the most recent. None
            indicates raw data stored without code version.
        """
        versions = [
            version
            for raw_code, raw_lib, version, bench in self.raw_data
            if raw_code == code and raw_lib == lib and bench == benchmark
        ]
        return sorted(versions, key=version_sort_key)

    def resolve_codelib(
        self, codelib: str, benchmark: str
    ) -> tuple[CODE, str, str | None] | None:
        """Resolve a code-lib string into the raw data to use for a benchmark.

        If the code-lib string specifies a code version, that exact version is
        required. Otherwise the most recent available code version is selected.

        Parameters
        ----------
        codelib : str
            codelib string, e.g. _openmc_-_FENDL 3.2c_ or
            _openmc_-_0.15.0_-_FENDL 3.2c_
        benchmark : str
            benchmark name.

        Returns
        -------
        tuple[CODE, str, str | None] | None
            code, library and code version of the raw data to use. None if no raw
            data is available.
        """
        code_tag, lib, version = get_code_lib_version(codelib)
        code = CODE(code_tag)
        available = self.get_raw_versions(code, lib, benchmark)
        if len(available) == 0:
            return None
        if version is not None:
            if version in available:
                return code, lib, version
            return None
        return code, lib, available[-1]

    def is_raw_available(self, codelib: str, benchmark: str) -> bool:
        """Check if the raw data is available for the given codelib and benchmark.

        Parameters
        ----------
        codelib : str
            codelib string. If no code version is specified, any version is
            accepted.
        benchmark : str
            benchmark name.

        Returns
        -------
        bool
            True if the raw data is available, False otherwise.
        """
        return self.resolve_codelib(codelib, benchmark) is not None

    def is_simulation_processed(self, code: CODE, lib: str, benchmark: str) -> bool:
        """Check if the raw data for a given simulation has already been produced.

        Simulations generated by recent JADE versions carry a ``run_id`` that is
        propagated to the raw results metadata, so that a new run (e.g. with a
        different code version) is recognized as not processed yet. For older
        simulations without ``run_id``, the simulation is considered processed if
        any raw data is available for the same code, library and benchmark.

        Parameters
        ----------
        code : CODE
            code used in the simulation.
        lib : str
            library name.
        benchmark : str
            benchmark name.

        Returns
        -------
        bool
            True if the simulation was already processed.
        """
        candidates = [
            key
            for key in self.raw_data
            if key[0] == code and key[1] == lib and key[3] == benchmark
        ]
        if len(candidates) == 0:
            return False

        run_id = None
        sim = self.simulations.get((code, lib, benchmark))
        if sim is not None and sim.metadata is not None:
            run_id = sim.metadata.get("run_id")
        if run_id is None:
            return True

        for key in candidates:
            if self.raw_metadata.get(key, {}).get("run_id") == run_id:
                return True
        return False

    def _validate_libs_processing(
        self,
        code: CODE,
        benchmark: str,
        libs: list[str | tuple[str, str | None]],
    ) -> None:
        """Check that the post-processing can be performed for the given code and
        benchmark. This is true if the benchmark version for the requested libs
        are the same.

        Parameters
        ----------
        code : CODE
            code used in the simulation.
        benchmark : str
            benchmark name.
        libs : list[str | tuple[str, str | None]]
            list of libraries to check. Each element is either a library name (the
            most recent code version is used) or a (library, code version) tuple.

        Raises
        ------
        VersionInconsistencyError
            if the benchmark versions are not consistent.
        """
        versions = {}
        for lib in libs:
            if isinstance(lib, str):
                lib_name = lib
                code_version = self.get_raw_versions(code, lib, benchmark)[-1]
            else:
                lib_name, code_version = lib
            label = print_code_lib(code, lib_name, pretty=True, version=code_version)
            # I want only the major version
            versions[label] = self.raw_metadata[
                (code, lib_name, code_version, benchmark)
            ]["benchmark_version"].split(".")[0]
        if len(set(versions.values())) > 1:
            raise VersionInconsistencyError(
                f"The versions of the requested libraries for {code} and benchmark {benchmark} are not consistent: {versions}"
            )

    def validate_codelibs(
        self,
        codelibs: list[tuple[CODE, str] | tuple[CODE, str, str | None]],
        benchmarks: str,
    ) -> None:
        """Check that a list of codelibs can be post-processed together for a given benchmark.
        This is true if the benchmark version for the requested libs are the same.

        Parameters
        ----------
        codelibs : list[tuple[CODE, str] | tuple[CODE, str, str | None]]
            list of codelibs to check. Each codelib is a tuple with the code, the
            library and, optionally, the code version.
        benchmark : str
            benchmark name.
        """
        libs = {}
        for codelib in codelibs:
            code = CODE(codelib[0])
            lib = codelib[1]
            if lib == "exp":  # for the experiments we don't have metadata
                continue
            if len(codelib) > 2:
                entry = (lib, codelib[2])
            else:
                entry = lib
            libs.setdefault(code, []).append(entry)

        for code, lib_list in libs.items():
            self._validate_libs_processing(code, benchmarks, lib_list)


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
