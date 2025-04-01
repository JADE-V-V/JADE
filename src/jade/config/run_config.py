from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from f4enix.input.MCNPinput import LibManager

from jade.config.paths_tree import PathsTree
from jade.helper.aux_functions import PathLike
from jade.helper.constants import CODE, CODE_TAGS
from jade.helper.errors import ConfigError


class RunConfig:
    def __init__(
        self,
        env_vars: EnvironmentVariables,
        benchmarks: dict[str, BenchmarkRunConfig],
    ):
        """Stores the configuration option for a session of JADE run.

        Parameters
        ----------
        env_vars : EnvironmentVariables
            environment variables for the session.
        benchmarks : dict[str, BenchmarkRunConfig]
            options of execution for the different benchmarks.
        """
        self.env_vars = env_vars
        self.benchmarks = benchmarks

    @classmethod
    def from_root(cls, paths_tree: PathsTree) -> RunConfig:
        """Create a RunConfig object from the root path of the configuration files.

        Parameters
        ----------
        paths_tree: PathsTree
            tree of paths in JADE.

        Returns
        -------
        RunConfig
            configuration object for the JADE run.
        """
        env_vars_file = paths_tree.cfg.env_vars_file
        run_cfg_file = paths_tree.cfg.run_cfg
        lib_cfg_file = paths_tree.cfg.libs_cfg
        additional_settings_root = paths_tree.cfg.bench_additional_files

        return cls.from_yamls(
            env_vars_file,
            run_cfg_file,
            lib_cfg_file,
            additional_settings_root,
        )

    @classmethod
    def from_yamls(
        cls,
        env_vars_file: PathLike,
        run_cfg_file: PathLike,
        lib_cfg_file: PathLike,
        additional_settings_root: PathLike,
    ) -> RunConfig:
        """Create a RunConfig object from single configuration files.

        Parameters
        ----------
        env_vars_file : PathLike
            path to the environment variables configuration file
        run_cfg_file : PathLike
            path to the benchmark run configuration file
        lib_cfg_file : PathLike
            path to the library configuration file
        additional_settings_root : PathLike
            path to the additional settings for benchmarks inputs

        Returns
        -------
        RunConfig
            configuration object for the JADE run.
        """
        lib_factory = LibraryFactory(lib_cfg_file)
        env_vars = EnvironmentVariables.from_yaml(env_vars_file)

        with open(run_cfg_file) as f:
            cfg = yaml.safe_load(f)
        run_cfg = {}
        for name, options in cfg.items():
            additional_settings_path = Path(additional_settings_root, name)
            benchmark = BenchmarkRunConfig.from_yaml_dict(
                options, name, lib_factory, additional_settings_path
            )
            if len(benchmark.run) > 0:
                # add only benchmarks on which some operations are needed
                run_cfg[name] = benchmark

        return cls(env_vars, run_cfg)


def _cast_to_code(dict: dict | list) -> dict[CODE, Any]:
    # depending on how the yaml is written instead of a unique dict we can have a list
    # of one value dictionaries
    if isinstance(dict, list):
        # merge all dictionaries in the list
        dict = {k: v for d in dict for k, v in d.items()}

    new_dict = {}
    for key, value in dict.items():
        if isinstance(key, str):
            key = CODE(key)
        new_dict[key] = value
    return new_dict


@dataclass
class EnvironmentVariables:
    """Configuration for the environment variables needed for the JADE run.

    Parameters
    ----------
    mpi_tasks : int | None
        number of mpi tasks to use in the run. If different from zero and a parallel
        run is requested, the run will use MPI.
    openmp_threads : int | None
        number of openmp threads to use in the run. If different from zero, the
        openmp threading will be used.
    executables : dict[CODE, str]
        dictionary of the codes and their executables. (e.g. "mcnp6.2")
    run_mode : RunMode
        mode of execution of the run. Either serial or job submission.
    code_configurations : dict[CODE, PathLike] | None
        path to the configuration files for the codes. If None, the default configuration
        will be used which can be found at cfg/exe_config. By default is None.
    batch_template : PathLike | None
        relative path to the batch template for job submission. location is cfg/batch_templates.
        By default is None.
    batch_system : str | None
        name of the batch system to use for job submission. e.g. "slurm". By default is
        None.
    mpi_prefix : str | None
        prefix for the mpi command. e.g. "srun", by default None
    """

    # parallel options
    mpi_tasks: int | None
    openmp_threads: int | None
    # codes executables
    executables: dict[CODE, str]
    run_mode: RunMode
    # codes configurations
    code_configurations: dict[CODE, PathLike] | None = None
    # run params
    batch_template: PathLike | None = None
    batch_system: str | None = None
    mpi_prefix: str | None = None

    def __post_init__(self):
        if self.mpi_tasks is not None:
            self.mpi_tasks = int(self.mpi_tasks)
        if self.openmp_threads is not None:
            self.openmp_threads = int(self.openmp_threads)
        # Check if the batch template exists if submission is requested
        if self.run_mode == RunMode.JOB_SUMISSION:
            if self.batch_template is None:
                raise ConfigError(
                    "Batch template is needed for job submission, please provide one"
                )
            elif not os.path.exists(self.batch_template):
                raise ConfigError(f"Batch template {self.batch_template} not found")

            if self.batch_system is None:
                raise ConfigError(
                    "Batch system is needed for job submission, please provide one"
                )

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> EnvironmentVariables:
        """Create an EnvironmentVariables object from a yaml configuration file.

        Parameters
        ----------
        config_file : PathLike
            path to the yaml configuration file for environment variables.

        Returns
        -------
        EnvironmentVariables
            _description_
        """
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        return EnvironmentVariables(
            mpi_tasks=cfg["mpi_tasks"],
            openmp_threads=cfg["openmp_threads"],
            executables=_cast_to_code(cfg["executables"]),
            run_mode=RunMode(cfg["run_mode"]),
            code_configurations=_cast_to_code(cfg["code_configurations"]),
            batch_template=cfg["batch_template"],
            batch_system=cfg["batch_system"],
            mpi_prefix=cfg["mpi_prefix"],
        )


@dataclass
class Library(ABC):
    """Configuration for a library to be used in the benchmarking process.

    Attributes
    ----------
    name : str
        extended name of the library.
    path : PathLike
        path to the libraries or to the xsdir containing it.
    """

    name: str
    path: PathLike

    @abstractmethod
    def get_lib_zaids(self) -> list[str]:
        """Return the list of available zaids in the library.

        Returns
        -------
        list[str]
            list of zaids available in the library. Zaid numbers to be used
        """
        pass


@dataclass
class LibraryOpenMC(Library):
    """Configuration for a library to be used in the benchmarking process for OpenMC.

    Attributes
    ----------
    name : str
        extended name of the library.
    path : PathLike
        path to the libraries or to the xsdir containing it.
    """

    def __post_init__(self):
        # in OpenMC the path points to a folder where a number of hdf files are stored.
        # I am assuming here that the format is always something like Cd116.h5
        # If this is not the case, we will be forced in the future to parse each single
        # table to get the correct zaid name. This could be expensive.
        lm = LibManager(defaultlib="00c")  # Just for name conversions
        self._available_zaids = []
        root = ET.parse(self.path).getroot()
        for type_tag in root.findall("library"):
            zaidname = type_tag.get("materials")
            try:
                zaidnum = lm.get_zaidnum(str(zaidname))
            except ValueError:
                continue  # ignore the files that we cannot understand for the moment
            except KeyError:
                continue  # ignore the files that we cannot understand for the moment
            self._available_zaids.append(zaidnum)

    def get_lib_zaids(self) -> list[str]:
        return self._available_zaids


@dataclass
class LibrarySerpent(Library):
    """Configuration for a library to be used in the benchmarking process for Serpent.

    Attributes
    ----------
    name : str
        extended name of the library.
    path : PathLike
        path to the libraries or to the xsdir containing it.
    """

    def get_lib_zaids(self) -> list[str]:
        raise NotImplementedError("Serpent library not implemented yet")


@dataclass
class LibraryMCNP(Library):
    """Configuration for a library to be used in the benchmarking process for MCNP.

    Attributes
    ----------
    name : str
        extended name of the library.
    path : PathLike
        path to the libraries or to the xsdir containing it.
    suffix : str
        suffix used in the xsdir (only for MCNP), by default None
    """

    suffix: str

    def __post_init__(self):
        # we can create a libmanager for this library
        self.libman = LibManager(xsdir_path=self.path)

    def get_lib_zaids(self) -> list[str]:
        return self.libman.get_libzaids(self.suffix)


@dataclass
class LibraryD1S(LibraryMCNP):
    """Configuration for a library to be used in the benchmarking process for D1S.

    Attributes
    ----------
    name : str
        extended name of the library.
    path : PathLike
        path to the libraries or to the xsdir containing it.
    suffix : str
        suffix used in the xsdir (only for MCNP), by default None
    transport_library_path : PathLike
        path to the transport library, by default None. this is used only for
        direct one step calculations.
    transport_suffix : str
        suffix used in the transport library (only for MCNP), by default None
    """

    transport_library_path: PathLike
    transport_suffix: str


class LibraryFactory:
    def __init__(self, lib_cfg: PathLike) -> None:
        """Factory objects which helps to create the correct Library for each code

        Parameters
        ----------
        lib_cfg : PathLike
            path to the file containing information on the parameters for the
            different libraries.
        """
        with open(lib_cfg) as f:
            self.cfg = yaml.safe_load(f)
        # The ace.Library object in MCNP is a full parser of the ace file
        # if we are not careful, spamming the creation of libraries could create
        # some performance issues. Better store already parsed libraries.
        self._openmc_libs = {}

    def create(self, code: CODE, name: str) -> Library:
        """generate a Library object from the configuration file.

        Parameters
        ----------
        code : CODE
            code for which the library is intended.
        name : str
            extended name of the library to create.

        Returns
        -------
        Library
            library object created from the configuration file

        Raises
        ------
        ConfigError
            If the configuration for the library is not found in the configuration file.
        ConfigError
            If the code is not supported.
        """
        try:
            kwargs = self.cfg[name][code.value]
        except KeyError:
            raise ConfigError(
                f"Config for library {name} not found for code {code}, please provide one"
            )
        if code == CODE.MCNP:
            return LibraryMCNP(name, **kwargs)
        elif code == CODE.OPENMC:
            if name not in self._openmc_libs:
                self._openmc_libs[name] = LibraryOpenMC(name, **kwargs)
            return self._openmc_libs[name]
        elif code == CODE.SERPENT:
            return LibrarySerpent(name, **kwargs)
        elif code == CODE.D1S:
            return LibraryD1S(name, **kwargs)
        else:
            raise ConfigError(f"Code {code} not supported")


@dataclass
class BenchmarkRunConfig:
    """Configuration for the JADE execution of a benchmark.

    Attributes
    ----------
    description : str
        description of the benchmark. E.g. 'Oktavian Experiment'
    name : str
        name of the benchmark. E.g. 'Oktavian'
    run : list[tuple[CODE, Library]]
        list of couples code-library to run for the benchmark.
    nps : int
        number of particles to simulate in the benchmark.
    only_input: bool
        if True, only the input files will be generated, by default False.
    cutom_inp : str | int | None, optional
        custom input for the benchmark, by default None.
    additional_settings_path : PathLike | None, optional
        path to additional settings for the benchmark, by default None.
        This for instance is used in the sphere benchmark to provide additional files
        where the settings for the materials and zaids are provided.
    """

    description: str
    name: str
    run: Sequence[tuple[CODE, Library]]
    nps: int
    only_input: bool = False
    custom_inp: str | int | None = None
    additional_settings_path: PathLike | None = None

    def __post_init__(self):
        if self.name in ["Sphere", "SphereSDDR"]:
            if self.additional_settings_path is None:
                raise ConfigError(
                    f"Additional settings path is needed for the {self.name} benchmark, please provide one"
                )
            # try to convert the custom input to a number in this case
            if self.custom_inp is not None:
                try:
                    self.custom_inp = int(self.custom_inp)
                except ValueError:
                    if self.custom_inp == "":
                        self.custom_inp = None
                    else:
                        raise ConfigError(
                            f"Custom input for the Sphere should be an integer, not {self.custom_inp}"
                        )
        # force nps to be an integer
        self.nps = int(float(self.nps))

    @classmethod
    def from_yaml_dict(
        cls,
        options: dict,
        name: str,
        lib_factory: LibraryFactory,
        additional_settings_path: PathLike | None,
    ) -> BenchmarkRunConfig:
        """Create a BenchmarkRunConfig object from a dictionary. These dictionaries
        normally come from a yaml configuration file.

        Parameters
        ----------
        options : dict
            dictionary with the options for the benchmark.
        name : str
            (short) name of the benchmark.
        lib_factory : LibraryFactory
            factory object to create the libraries for the benchmark.
        additional_settings_path : PathLike | None
            path to additional settings for the benchmark, by default None.

        Returns
        -------
        BenchmarkRunConfig
            configuration object for the benchmark.
        """
        run = []
        for code_tag in CODE_TAGS:
            # skip the experiment tag
            if code_tag == "exp":
                continue
            libs = options["codes"][code_tag]
            for lib in libs:
                run.append((CODE(code_tag), lib_factory.create(CODE(code_tag), lib)))

        if additional_settings_path is not None and not os.path.exists(
            additional_settings_path
        ):
            additional_settings_path = None

        return BenchmarkRunConfig(
            description=options["description"],
            name=name,
            run=run,
            nps=options["nps"],
            only_input=options["only_input"],
            custom_inp=options["custom_input"],
            additional_settings_path=additional_settings_path,
        )


class RunMode(Enum):
    """Enumeration of the possible run modes for JADE."""

    SERIAL = "serial"
    JOB_SUMISSION = "job"
