from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import f4enix.input.MCNPinput as ipt
import pandas as pd
from f4enix.input.libmanager import LibManager
from f4enix.input.materials import MatCardsList
from tqdm import tqdm

from jade.config.run_config import (
    BenchmarkRunConfig,
    EnvironmentVariables,
    Library,
    LibraryD1S,
    LibraryMCNP,
    RunMode,
)
from jade.helper.aux_functions import PathLike, get_jade_version, print_code_lib
from jade.helper.constants import CODE
from jade.helper.errors import ConfigError
from jade.run import unix
from jade.run.input import (
    Input,
    InputD1S,
    InputD1SSphere,
    InputMCNP,
    InputMCNPSphere,
    InputOpenMC,
    InputOpenMcSphere,
    InputSerpent,
)


class SingleRun(ABC):
    def __init__(
        self,
        input: Input,
        library: Library,
        nps: int,
    ):
        """Handles a single simulation in a benchmark.

        Parameters
        ----------
        input: Input
            input object for the code. This may encompass multiple input files.
            needed for the simulation.
        template_folder : PathLike
            path to the folder containing the input template.
        library : Library
            library to be used in the run.
        nps : int
            number of particles to simulate.
        """
        self.input = input
        self.name = self.input.name
        self.lib = library
        # Translate the input to the requested library
        input.translate()
        # Set nps
        input.set_nps(int(nps))

    @property
    @abstractmethod
    def code(self) -> CODE:
        pass

    @abstractmethod
    def _build_command(self, config: EnvironmentVariables) -> list[str]:
        """Build the command to run the code. This is code-dependent.

        Parameters
        ----------
        config : EnvironmentVariables
            environment variables for JADE execution in general.

        Returns
        -------
        str
            command to run the code.
        """
        # This method needs to build the command to run the code, will be different
        # depending on codes
        pass

    @abstractmethod
    def _get_lib_data_command(self) -> tuple[str, str]:
        """Get the command to export env variables for libraries data

        Returns
        -------
        str, str
            name of the environmental variable, value of the environmental variable
        """

    def write(self, output_folder: PathLike):
        """Write the input files to the output folder. All other additional files
        should also be written here.

        Parameters
        ----------
        output_folder : PathLike
            path to the output folder.
        """
        # write the input to the output folder
        self.input._write(output_folder)

    def print_metadata(self, outpath: PathLike, metadata_file: PathLike):
        """Print the metadata of the run to the output folder.

        Parameters
        ----------
        outpath : PathLike
            path to the output folder for the run metadata file.
        metadata_file : PathLike
            path to the input metadata file.
        """
        # read, update and add metadata file to the run directory
        with open(metadata_file) as f:
            metadata_inp = json.load(f)

        metadata = {}
        metadata["benchmark_name"] = metadata_inp["name"]
        metadata["benchmark_version"] = metadata_inp["version"][self.code.value]
        metadata["jade_run_version"] = get_jade_version()
        metadata["library"] = self.lib.name
        metadata["code"] = self.code.value
        outfile = os.path.join(outpath, "metadata.json")
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    def run(
        self, env_vars: EnvironmentVariables, sim_folder: PathLike, test=False
    ) -> bool:
        """Run the simulation.

        Parameters
        ----------
        env_vars : EnvironmentVariables
            environment variables for JADE execution in general.
        sim_folder : PathLike
            path to the simulation folder.
        test : bool, optional
            flag to run the simulation in test mode, by default False.

        Returns
        -------
        bool
            True if the simulation run correctly, False otherwise.
        """
        run_command = self._build_command(env_vars)
        name, value = self._get_lib_data_command()
        lib_data_command = f"export {name}={value}"

        flagnotrun = False
        if env_vars.run_mode == RunMode.JOB_SUMISSION:
            if self._is_mpi_run(env_vars):
                run_command.insert(0, env_vars.mpi_prefix)
            command = self._submit_job(
                env_vars, sim_folder, run_command, lib_data_command, test=test
            )
            if test:
                return command

        elif env_vars.run_mode == RunMode.SERIAL:
            # in case of run in console dump the prints to a file
            # to get the code version in the metadata
            run_command.append("> dump.out")
            if self._is_mpi_run(env_vars):
                run_command.insert(0, f"-np {env_vars.mpi_tasks}")
                run_command.insert(0, env_vars.mpi_prefix)
            if not sys.platform.startswith("win"):
                unix.configure(env_vars.code_configurations[self.code])
            print(" ".join(run_command))
            if test:
                return " ".join(run_command)
            else:
                # Be sure that the datapath has been set correctly
                os.environ[name] = value
                subprocess.run(
                    " ".join(run_command),
                    cwd=sim_folder,
                    shell=True,
                    check=True,
                    # timeout=43200, serial can also last days on workstations
                )

        return flagnotrun

    def _is_mpi_run(self, env_vars: EnvironmentVariables) -> bool:
        if env_vars.mpi_tasks is not None and env_vars.mpi_tasks > 1:
            if env_vars.mpi_prefix is None:
                raise ConfigError(
                    "MPI prefix is needed for MPI job submission, please provide one"
                )
            return True
        return False

    def _submit_job(
        self,
        env_vars: EnvironmentVariables,
        directory: PathLike,
        run_command: list,
        data_command: str,
        test: bool = False,
    ) -> None:
        """Submits a job script to the users batch system for running in parallel.

        Parameters
        ----------
        env_vars : EnvironmentVariables
            Environment variables for JADE execution in general
        directory : Pathlike
            Job working directory
        run_command : list
            Executable command
        data_command : str
            user specified/ code specific environment variables
        test : bool, optional
            flag to run the simulation in test mode, by default False
        """
        # store cwd to get back to it after job submission
        cwd = os.getcwd()
        # Read contents of batch file template.
        with open(env_vars.code_configurations[self.code]) as f:
            config_script = ""
            for line in f:
                if not line.startswith("#!"):
                    config_script += line
        user = (
            subprocess.run("whoami", capture_output=True).stdout.decode("utf-8").strip()
        )
        os.chdir(directory)
        job_script = os.path.join(
            directory, os.path.basename(directory) + "_job_script"
        )
        essential_commands = ["MPI_TASKS"]

        # that the file exists it has been checked in the post_init already
        with open(env_vars.batch_template) as fin, open(job_script, "w") as fout:
            # Replace placeholders in batch file template with actual values
            contents = fin.read()
            for cmd in essential_commands:
                if cmd not in contents:
                    raise ConfigError(
                        f"Unable to find essential dummy variable {cmd} in job "
                        "script template, please check and re-run"
                    )
            contents = contents.replace("INITIAL_DIR", str(directory))
            contents = contents.replace("OUT_FILE", job_script + ".out")
            contents = contents.replace("ERROR_FILE", job_script + ".err")
            contents = contents.replace("MPI_TASKS", str(env_vars.mpi_tasks))
            contents = contents.replace("OMP_THREADS", str(env_vars.openmp_threads))
            contents = contents.replace("USER", user)

            contents += "\n\n" + config_script
            contents += "\n\n" + str(data_command)
            contents += "\n\n" + " ".join(run_command)

            fout.write(contents)

        # Submit the job using the specified batch system (checked for existence in post_init)
        if not test:
            subprocess.run(
                f"{env_vars.batch_system} {job_script}", cwd=directory, shell=True
            )
        else:
            return f"{env_vars.batch_system} {job_script}"
        # return to the original directory
        os.chdir(cwd)


class SingleRunMCNP(SingleRun):
    """Implementation of the SingleRun class for MCNP runs."""

    @property
    def code(self) -> CODE:
        return CODE.MCNP

    def _build_command(self, config: EnvironmentVariables) -> list[str]:
        # Calculate MPI tasks and OpenMP threads
        omp_threads = config.openmp_threads

        # Build the command
        executable = config.executables[self.code]
        inputstring = f"i={self.input.name}.i"
        outputstring = f"n={self.input.name}."
        if omp_threads is not None and omp_threads > 1:
            tasks = "tasks " + str(omp_threads)
        else:
            tasks = ""
        xsstring = f"xsdir={Path(self.lib.path).name}"

        run_command = [executable, inputstring, outputstring, xsstring, tasks]

        return run_command

    def _get_lib_data_command(self) -> tuple[str, str]:
        return "DATAPATH", str(Path(self.lib.path).parent)


class SingleRunOpenMC(SingleRun):
    """Implementation of the SingleRun class for OpenMC runs."""

    @property
    def code(self) -> CODE:
        return CODE.OPENMC

    def _build_command(self, config: EnvironmentVariables) -> list[str]:
        executable = config.executables[self.code]
        # Run OpenMC from command line either OMP, MPI or hybrid MPI-OMP
        omp_threads = config.openmp_threads
        if omp_threads is not None and omp_threads > 1:
            run_command = [executable, "--threads", str(omp_threads)]
        else:
            run_command = [executable]

        return run_command

    def _get_lib_data_command(self) -> tuple[str, str]:
        return "OPENMC_CROSS_SECTIONS", str(self.lib.path)


class SingleRunSerpent(SingleRun):
    """Implementation of the SingleRun class for Serpent runs."""

    @property
    def code(self) -> CODE:
        return CODE.SERPENT

    def _build_command(self, config: EnvironmentVariables) -> list[str]:
        raise NotImplementedError

    def _get_lib_data_command(self) -> str:
        raise NotImplementedError


class SingleRunD1S(SingleRunMCNP):
    """Implementation of the SingleRun class for D1S runs."""

    @property
    def code(self) -> CODE:
        return CODE.D1S


class SingleRunFactory:
    @staticmethod
    def create(
        code: CODE,
        template_folder: PathLike,
        lib: Library,
        nps: int,
    ) -> SingleRun:
        """Factory method to create a SingleRun object.

        Parameters
        ----------
        code : CODE
            code for the simulation.
        template_folder : PathLike
            path to the folder containing the input template of the benchmark.
        library : Library
            library to be used in the run.
        nps : int
            number of particle histories to simulate.
        """
        if code == CODE.MCNP:
            single_run_class = SingleRunMCNP
            if not isinstance(lib, LibraryMCNP):
                raise ConfigError("An MCNP library needs to be provided for MCNP runs")
            inp = InputMCNP(template_folder, lib)
        elif code == CODE.OPENMC:
            single_run_class = SingleRunOpenMC
            inp = InputOpenMC(template_folder, lib)
        elif code == CODE.SERPENT:
            single_run_class = SingleRunSerpent
            inp = InputSerpent(template_folder, lib)
        elif code == CODE.D1S:
            single_run_class = SingleRunD1S
            if not isinstance(lib, LibraryD1S):
                raise ConfigError("A D1S library needs to be provided for D1S runs")
            inp = InputD1S(template_folder, lib)
        else:
            raise ValueError(f"Code {code} not supported")

        return single_run_class(inp, lib, nps)


class BenchmarkRun:
    def __init__(
        self,
        config: BenchmarkRunConfig,
        simulation_root: PathLike,
        input_root: PathLike,
        env_vars: EnvironmentVariables,
    ):
        """Object handling the run of an entire benchmark.

        Parameters
        ----------
        config : BenchmarkExecConfig
            configuration of the benchmark.
        simulation_root : PathLike
            path to the root of the simulations.
        input_root : PathLike
            path to the root of the input templates.
        env_vars : EnvironmentVariables
            environment variables for JADE execution
        """
        # Each benchmark is composed by a list of single runs. This can be also only one
        self.benchmark_templates_root = os.path.join(input_root, config.name)

        self.config = config
        self.env_vars = env_vars
        self.simulation_root = simulation_root

    def run(self):
        """Run the benchmark. This creates the inputs and runs the simulations for each
        single run included in the benchmark.

        Raises
        ------
        ConfigError
            The executable for the code to be used was not set in the main config file.
        """
        # first we run the benchmark for each code-lib couple
        for code, lib in self.config.run:
            # --- perform some consistency checks here ---
            # if a code is requested, its executable should also be provided
            try:
                self.env_vars.executables[code]
            except KeyError:
                raise ConfigError(
                    f"An assessment was requested using {code.value} but the executable was not set in the main config file"
                )

            code_lib = print_code_lib(code, lib)

            # this is the level 0 of the benchmark
            root_benchmark = os.path.join(
                self.simulation_root, code_lib, self.config.name
            )
            try:
                os.makedirs(root_benchmark, exist_ok=False)
            except OSError:
                # if the folder already exists, we remove all the content. The GUI should
                # have already warned the user that results will be overwritten
                shutil.rmtree(root_benchmark)
                os.mkdir(root_benchmark)

            self._run_sub_benchmarks(root_benchmark, code, lib)

    def _run_sub_benchmarks(self, root_benchmark: PathLike, code: CODE, lib: Library):
        # now create a single run for each of the benchmark subfolders
        for sub_bench in os.listdir(self.benchmark_templates_root):
            # create the folder
            sub_bench_folder = os.path.join(root_benchmark, sub_bench)
            if not os.path.isdir(Path(self.benchmark_templates_root, sub_bench)):
                continue  # skip files like the metadata.json
            os.mkdir(sub_bench_folder)
            # recover the input template
            template_folder = os.path.join(
                self.benchmark_templates_root, sub_bench, code.value
            )
            # create the single run
            single_run = SingleRunFactory.create(
                code, template_folder, lib, int(self.config.nps)
            )
            self._run_single_run(
                sub_bench_folder, self.benchmark_templates_root, single_run
            )

    def _run_single_run(
        self,
        sub_bench_folder: PathLike,
        root_templates: PathLike,
        single_run: SingleRun,
    ):
        single_run.write(sub_bench_folder)
        input_metadata_file = os.path.join(root_templates, "benchmark_metadata.json")
        single_run.print_metadata(sub_bench_folder, input_metadata_file)

        if not self.config.only_input:
            single_run.run(self.env_vars, sub_bench_folder)


class SphereBenchmarkRun(BenchmarkRun):
    """Subclass of the BenchmarkRun which implements some specifities of the Sphere
    benchmark. In fact, the multiple generation of runs here is not given by multiple
    template files, but from automatic generation of inputs depending on zaids
    avaialble in the libraries.
    """

    def _run_sub_benchmarks(self, root_benchmark: PathLike, code: CODE, lib: Library):
        # we need to do things differntly here as there is only one template that
        # will be used for all the sub-benchmarks

        zaids, materials, zaid_settings, settings_mat, limit, lm, template_folder = (
            self._recover_settings(lib, code)
        )

        for zaid in tqdm(zaids[:limit], desc="Zaids"):
            nps, density = self._recover_zaids_nps_density(zaid, zaid_settings)
            # derive the sub-benchmark folder name
            _, formula = lm.get_zaidname(zaid)
            sub_bench_folder_name = (
                self.config.name + "_" + zaid[:-3] + zaid[-3:] + "_" + formula
            )
            sub_bench_folder = Path(root_benchmark, sub_bench_folder_name)
            # need to create the folder
            os.mkdir(sub_bench_folder)

            if code == CODE.MCNP:
                if not isinstance(lib, LibraryMCNP):
                    raise ConfigError(
                        "An MCNP library needs to be provided for MCNP runs"
                    )
                inp = InputMCNPSphere(template_folder, lib, zaid, str(-1 * density))
                single_run = SingleRunMCNP(inp, lib, nps)
            elif code == CODE.OPENMC:
                inp = InputOpenMcSphere(template_folder, lib, zaid, str(-1 * density))
                single_run = SingleRunOpenMC(inp, lib, nps)
            else:
                raise NotImplementedError(f"Code {code} not supported for Sphere")
            self._run_single_run(
                sub_bench_folder, self.benchmark_templates_root, single_run
            )

        for material in tqdm(materials.materials[:limit], desc="Materials"):
            # Get density
            density = settings_mat.loc[material.name.upper(), "Density [g/cc]"]

            # derive the sub-benchmark folder name
            sub_bench_folder_name = f"{self.config.name}_{material.name}"
            sub_bench_folder = Path(root_benchmark, sub_bench_folder_name)
            os.mkdir(sub_bench_folder)

            if code == CODE.MCNP:
                if not isinstance(lib, LibraryMCNP):
                    raise ConfigError(
                        "An MCNP library needs to be provided for MCNP runs"
                    )
                inp = InputMCNPSphere(
                    template_folder, lib, material, str(-1 * float(density))
                )
                single_run = SingleRunMCNP(inp, lib, int(self.config.nps))
            elif code == CODE.OPENMC:
                inp = InputOpenMcSphere(
                    template_folder, lib, material, str(-1 * float(density))
                )
                single_run = SingleRunOpenMC(inp, lib, int(self.config.nps))
            else:
                raise NotImplementedError(f"Code {code} not supported for Sphere")
            self._run_single_run(
                sub_bench_folder, self.benchmark_templates_root, single_run
            )

    def _recover_settings(
        self, lib: Library, code: CODE
    ) -> tuple[
        list[str],
        MatCardsList,
        pd.DataFrame,
        pd.DataFrame,
        int,
        LibManager,
        PathLike,
    ]:
        # first of all retrieve the typical material file which is at the root of the
        # benchmarks folder
        matpath = Path(Path(self.benchmark_templates_root).parent, "TypicalMaterials")
        inpmat = ipt.Input.from_input(matpath)
        materials = inpmat.materials

        # init a libmanager to get the zaid names
        lm = LibManager()
        zaids = lib.get_lib_zaids()

        # GET SETTINGS
        # These paths not being None have been checked in the post_init of the Config Object
        settings_path = Path(self.config.additional_settings_path, "ZaidSettings.csv")
        settings_mat_path = Path(
            self.config.additional_settings_path, "MaterialsSettings.csv"
        )

        zaid_settings = pd.read_csv(settings_path, sep=",").set_index("Z")
        settings_mat = pd.read_csv(settings_mat_path, sep=",").set_index("Symbol")

        limit = self.config.custom_inp
        if limit is not None and not isinstance(limit, int):
            raise ConfigError(
                "The custom input for the Sphere benchmark should be an integer"
            )

        # recover the input template. There is going to be only one run
        template_folder = os.path.join(
            self.benchmark_templates_root, self.config.name, code.value
        )

        return zaids, materials, zaid_settings, settings_mat, limit, lm, template_folder

    def _recover_zaids_nps_density(
        self, zaid: str, zaid_settings: pd.DataFrame
    ) -> tuple[int, float]:
        # --- get some config parameters ---
        Z = int(zaid[:-3])
        # Get Density
        density = zaid_settings.loc[Z, "Density [g/cc]"]
        if zaid_settings.loc[Z, "Let Override"]:
            # get stop parameters
            if self.config.nps == 0:
                nps = zaid_settings.loc[Z, "NPS cut-off"]
            else:
                nps = self.config.nps
        # Zaid local settings are prioritized
        else:
            nps = zaid_settings.loc[Z, "NPS cut-off"]

        return int(nps), float(density)


class SphereSDDRBenchmarkRun(SphereBenchmarkRun):
    """Subclass of the SphereBenchmarkRun which implements some further specificities
    of the Sphere SDDR benchmark. This is because not only a run is generated for
    each isotope in the library, but also for each reaction channel available in each
    isotope.
    """

    def _run_sub_benchmarks(
        self, root_benchmark: PathLike, code: CODE, lib: LibraryD1S
    ):
        # we need to do things differntly here as there is only one template that
        # will be used for all the sub-benchmarks
        zaids, materials, zaid_settings, settings_mat, limit, lm, template_folder = (
            self._recover_settings(lib, code)
        )

        # Retrieve the irradaition file template for the library
        irrad_file = Path(
            self.config.additional_settings_path, f"irrad_{lib.suffix}.txt"
        )
        if not irrad_file.exists():
            raise ConfigError(
                f"An irradiation file template for the library {lib.suffix} was not found"
            )

        for zaid in tqdm(zaids[:limit], desc="Zaids"):
            reactions = lm.get_reactions(lib.suffix, zaid)
            nps, density = self._recover_zaids_nps_density(zaid, zaid_settings)
            _, formula = lm.get_zaidname(zaid)

            for reaction in reactions:
                MT = reaction[0]
                daughter = reaction[1]

                # derive the sub-benchmark folder name
                sub_bench_folder_name = f"{self.config.name}_{zaid}_{formula}_{MT}"
                sub_bench_folder = Path(root_benchmark, sub_bench_folder_name)
                os.mkdir(sub_bench_folder)

                if code == CODE.D1S:
                    inp = InputD1SSphere(
                        template_folder,
                        lib,
                        zaid,
                        str(-1 * density),
                        MT=MT,
                        daughter=daughter,
                        irrad_file=irrad_file,
                    )
                    single_run = SingleRunD1S(inp, lib, nps)
                else:
                    raise NotImplementedError(f"Code {code} not supported for Sphere")
                self._run_single_run(
                    sub_bench_folder, self.benchmark_templates_root, single_run
                )

        for material in tqdm(materials.materials[:limit], desc="Materials"):
            # Get density
            density = settings_mat.loc[material.name.upper(), "Density [g/cc]"]

            # derive the sub-benchmark folder name
            sub_bench_folder_name = f"{self.config.name}_{material.name}_All"
            sub_bench_folder = Path(root_benchmark, sub_bench_folder_name)
            os.mkdir(sub_bench_folder)

            if code == CODE.D1S:
                inp = InputD1SSphere(
                    template_folder,
                    lib,
                    material,
                    str(-1 * float(density)),
                    irrad_file=irrad_file,
                )
                single_run = SingleRunD1S(inp, lib, int(self.config.nps))
            else:
                raise NotImplementedError(f"Code {code} not supported for Sphere")

            # it may happen that the material does not have any reaction channel
            if inp.inp.reac_file is None or len(inp.inp.reac_file.reactions) == 0:
                # remove the created subfolder
                shutil.rmtree(sub_bench_folder)
                continue

            self._run_single_run(
                sub_bench_folder, self.benchmark_templates_root, single_run
            )


class BenchmarkRunFactory:
    @staticmethod
    def create(
        config: BenchmarkRunConfig,
        simulation_root: PathLike,
        input_root: PathLike,
        env_vars: EnvironmentVariables,
    ) -> BenchmarkRun:
        """Factory method to create a BenchmarkRun object.

        Parameters
        ----------
        config : BenchmarkRunConfig
            configuration of the benchmark.
        simulation_root : PathLike
            path to the root of the simulations.
        input_root : PathLike
            path to the root of the input templates.
        env_vars : EnvironmentVariables
            environment variables for JADE execution
        """
        if config.name == "Sphere":
            return SphereBenchmarkRun(config, simulation_root, input_root, env_vars)
        elif config.name == "SphereSDDR":
            return SphereSDDRBenchmarkRun(config, simulation_root, input_root, env_vars)
        else:
            return BenchmarkRun(config, simulation_root, input_root, env_vars)
