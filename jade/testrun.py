# -*- coding: utf-8 -*-

# Created on Mon Nov  4 16:52:09 2019

# @author: Davide Laghi

# Copyright 2021, the JADE Development Team. All rights reserved.

# This file is part of JADE.

# JADE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# JADE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with JADE.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import jade.inputfile as ipt
import jade.matreader as mat
import jade.unix as unix
import numpy as np
import pandas as pd
from jade.parsersD1S import IrradiationFile, Reaction, ReactionFile
from tqdm import tqdm

# colors
CRED = "\033[91m"
CORANGE = "\033[93m"
CEND = "\033[0m"


class Test:
    def __init__(self, inp, lib, config, log, confpath, runoption):
        """
        Class representing a general test. This class will have to be extended
        for specific tests.

        Parameters
        ----------
        inp : str
            path to inputfile blueprint.
        lib : str
            library suffix to use (e.g. 31c).
        config : pd.DataFrame (single row)
            configuration options for the test.
        log : Log
            Jade log file access.
        confpath : path like object
            path to the test configuration folder.

        Raises
        ------
        ValueError
            if the code specified in config is not admissible.

        Returns
        -------
        None.

        """
        # Test Library
        self.lib = lib

        # Parallel execution
        self.runoption = runoption

        # Configuration options for the test
        self.config = config

        # MCNP original input
        self.original_inp = inp

        # Log for warnings
        self.log = log

        # VRT path
        self.path_VRT = inp

        # Get the configuration files path
        self.test_conf_path = confpath

        # Input variables
        self.mcnp_ipt = None
        self.serpent_ipt = None
        self.openmc_ipt = None
        self.d1s_ipt = None

        self.irrad = None
        self.react = None

        # Path variables
        self.run_dir = None

        config = config.dropna()

        # self.name = config["Folder Name"]

        try:
            self.nps = config["NPS cut-off"]
        except KeyError:
            self.nps = None
        if self.nps is np.nan:
            self.nps = None

        # Updated to handle multiple codes
        try:
            self.mcnp = bool(config["MCNP"])
        except KeyError:
            self.mcnp = False
        try:
            self.serpent = bool(config["Serpent"])
        except KeyError:
            self.serpent = False
        try:
            self.openmc = bool(config["OpenMC"])
        except KeyError:
            self.openmc = False
        try:
            self.d1s = bool(config["d1S"])
        except KeyError:
            self.d1s = False

        # Generate input file template according to transport code
        if self.d1s:
            d1s_ipt = os.path.join(inp, "d1s",  os.path.basename(inp) + ".i")
            self.d1s_inp = ipt.D1S5_InputFile.from_text(d1s_ipt)
            irrfile = os.path.join(inp, "d1s", os.path.basename(inp) + "_irrad")
            reacfile = os.path.join(
                inp, "d1s", os.path.basename(inp) + "_react"
            )
            try:
                self.irrad = IrradiationFile.from_text(irrfile)
                self.react = ReactionFile.from_text(reacfile)
            except FileNotFoundError:
                self.log.adjourn(
                    "d1S irradition and reaction files not found, skipping..."
                )
            self.name = self.d1s_inp.name
        if self.mcnp:
            mcnp_ipt = os.path.join(inp, "mcnp", os.path.basename(inp) + ".i")
            self.mcnp_inp = ipt.InputFile.from_text(mcnp_ipt)
            self.name = self.mcnp_inp.name
        if self.serpent:
            serpent_ipt = os.path.join(inp, "serpent", os.path.basename(inp) + ".i")
            self.serpent_inp = ipt.SerpentInputFile.from_text(serpent_ipt)
        if self.openmc:
            openmc_ipt = os.path.join(inp, "openmc")
            self.openmc_inp = ipt.OpenMCInputFiles.from_path(openmc_ipt)

    def _translate_input(self, lib, libmanager):
        """
        Translate the input template to selected library

        Parameters
        ----------
        lib : str or dic
            There are many ways to provide a librart to be translated
            check the matreader doc for more details.
        libmanager : libmanager.LibManager
            Manager dealing with libraries operations..

        Returns
        -------
        None.

        """

        if self.d1s:
            # Then it was the translation of a D1S input, additional
            # actions are required
            add = self.d1s_inp.translate(
                lib,
                libmanager,
                original_irradfile=self.irrad,
                original_reacfile=self.react,
            )
            newirradiations = add[0]
            newreactions = add[1]
            self.irrad.irr_schedules = newirradiations
            self.react.reactions = newreactions
            self.d1s_inp.update_zaidinfo(libmanager)
        if self.mcnp:
            self.mcnp_inp.translate(lib, libmanager, "mcnp")
            self.mcnp_inp.update_zaidinfo(libmanager)
        if self.serpent:
            # Add serpent file translation here
            pass
        if self.openmc:
            # Add openmc file translation here
            pass

    def generate_test(self, lib_directory, libmanager, run_dir=None):
        """
        Generate the test input files

        Parameters
        ----------
        lib_directory : path or string
            Path to lib benchmarks input folders.
        libmanager : libmanager.LibManager
            Manager dealing with libraries operations.
        MCNPdir : str or path
            allows to ovewrite the MCNP dir if needed. The default is None

        Returns
        -------
        None.

        """
        # Translate the input
        self._translate_input(self.lib, libmanager)

        # Add stop card
        if self.d1s:
            self.d1s_inp.add_stopCard(self.nps)
        if self.mcnp:
            self.mcnp_inp.add_stopCard(self.nps)
        if self.serpent:
            self.serpent_inp.add_stopCard(self.nps)
        if self.openmc:
            self.openmc_inp.add_stopCard(self.nps)

        # Identify working directory
        # testname = self.inp.name
        testname = self.name
        if run_dir is None:
            motherdir = os.path.join(lib_directory, testname)
        else:
            motherdir = run_dir
        self.run_dir = motherdir
        # If previous results are present they are cancelled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        # Allow space for personalization getting additional modification
        self.custom_inp_modifications()

        if self.d1s:
            d1s_dir = os.path.join(motherdir, "d1s")
            os.mkdir(d1s_dir)
            outinpfile = os.path.join(d1s_dir, testname)
            self.d1s_inp.write(outinpfile)
            # And accessory files if needed
            if self.irrad is not None:
                self.irrad.write(d1s_dir)
            if self.react is not None:
                self.react.write(d1s_dir)
            # Get WW files if available
            wwinp = os.path.join(self.original_inp, "d1s", "wwinp")
            if os.path.exists(wwinp):
                outfile = os.path.join(motherdir, "d1s", "wwinp")
                shutil.copyfile(wwinp, outfile)

        if self.mcnp:
            os.mkdir(os.path.join(motherdir, "mcnp"))
            outinpfile = os.path.join(motherdir, "mcnp", testname)
            self.mcnp_inp.write(outinpfile)
            # Get WW files if available
            wwinp = os.path.join(self.original_inp, "mcnp", "wwinp")
            if os.path.exists(wwinp):
                outfile = os.path.join(motherdir, "mcnp", "wwinp")
                shutil.copyfile(wwinp, outfile)

        if self.serpent:
            # Implement serpent outputfile generation here
            pass

        if self.openmc:
            # Implement openmc outputfile generation here
            pass

    def custom_inp_modifications(self):
        """
        Perform additional operation on the input before generation. In this
        parent object actually does nothing

        Returns
        -------
        None.

        """
        # It does not do anything in the default benchmark
        pass

    def run(self, config, libmanager, runoption: str) -> None:
        """
        run the input

        Parameters
        ----------
        config :
            Configuration settings
        libmanager :
            libmanager
        runoption : str
        """

        directory = self.run_dir
        name = self.name

        if self.d1s:
            d1s_directory = os.path.join(directory, "d1s")
            if pd.isnull(config.d1s_exec) is not True:
                self.run_d1s(config, libmanager, name, d1s_directory)

        if self.mcnp:
            mcnp_directory = os.path.join(directory, "mcnp")
            if pd.isnull(config.mcnp_exec) is not True:
                self.run_mcnp(config, libmanager, name, mcnp_directory, runoption)

        if self.serpent:
            serpent_directory = os.path.join(directory, "serpent")
            if pd.isnull(config.serpent_exec) is not True:
                self.run_serpent(config, libmanager, name, serpent_directory, runoption)

        if self.openmc:
            openmc_directory = os.path.join(directory, "openmc")
            if pd.isnull(config.openmc_exec) is not True:
                self.run_openmc(config, libmanager, name, openmc_directory, runoption)

    # Edited by D.Wheeler, UKAEA
    # Job submission currently tailored for LoadLeveler, may be applicable to other submission systems with equivalent dummy variables
    def job_submission(
        self,
        config,
        directory: str,
        run_command: list,
        mpi_tasks: int,
        omp_threads: int,
        env_variables: str,
        data_command=str(),
    ) -> None:
        """Submits a job script to the users batch system for running in parallel.

        Parameters
        ----------
        config :
            Configuration settings
        directory :
            Job working directory
        run_command : list
            Executable command
        mpi_tasks : int
            Number of MPI tasks
        omp_threads : int
            Number of OMP threads
        env_variables : str
            user specified/ code specific environment variables
        data_command : str, optional
            user specified/ code specific environment variables, by default str()
        """

        # Read contents of batch file template.
        with open(env_variables, "r") as f:
            config_script = ""
            for line in f:
                if not line.startswith("#!"):
                    config_script += line
        user = (
            subprocess.run("whoami", capture_output=True).stdout.decode("utf-8").strip()
        )
        os.chdir(directory)
        job_script = directory + "/" + os.path.basename(directory) + "_job_script"
        fout = open(job_script, "wt")
        essential_commands = ["COMMAND", "OUT_FILE"]
        with open(config.batch_file, "rt") as fin:
            # Replace placeholders in batch file template with actual values
            contents = fin.read()
            for cmd in essential_commands:
                if cmd not in contents:
                    raise Exception(
                        "Unable to find essential dummy variable {} in job "
                        "script template, please check and re-run".format(cmd)
                    )
            contents = contents.replace("COMMAND", " ".join(run_command))
            contents = contents.replace("ENV_VARIABLES", str(data_command))
            contents = contents.replace("INITIAL_DIR", directory)
            contents = contents.replace("OUT_FILE", job_script + ".out")
            contents = contents.replace("ERROR_FILE", job_script + ".err")
            contents = contents.replace("MPI_TASKS", str(mpi_tasks))
            contents = contents.replace("OMP_THREADS", str(omp_threads))
            contents = contents.replace("CONFIG_SCRIPT", config_script)
            contents = contents.replace("USER", user)
            fout.write(contents)

        fin.close()
        fout.close()

        # Submit the job using the specified batch system
        subprocess.run(
            config.batch_system + " " + job_script, cwd=directory, shell=True
        )

    def run_d1s(
        self,
        config,
        lib_manager,
        name: str,
        directory: Path,
        runoption: str,
        timeout=None,
    ) -> bool:
        """Run D1S simulation either on the command line or submitted as a job.

        Parameters
        ----------
        config :
            Configuration settings
        lib_manager :
            libmanager
        name : str
            Name of the simulation
        directory : str, path
            Directory where the simulation will be executed
        runoption: str
            Whether JADE run in parallel or command line
        timeout : float, optional
            Maximum time to wait for simulation of complete, by default None

        Returns
        -------
        bool
            Flag if simulation not run
        """

        # Calculate MPI tasks and OpenMP threads
        mpi_tasks = int(config.openmp_threads) * int(config.mpi_tasks)
        omp_threads = 1
        run_mpi = False
        if mpi_tasks > 1:
            run_mpi = True

        executable = config.d1s_exec
        env_variables = config.d1s_config
        inputstring = "i=" + name
        outputstring = "n=" + name

        #TODO change for D1S
        if isinstance(self.lib, dict):
            lib = list(self.lib.values())[0]
        elif isinstance(self.lib, str):
            lib = self.lib

        xsstring = "xs=" + str(lib_manager.data["mcnp"][lib].filename)

        if run_mpi:
            run_command = [
                "mpirun",
                "-n",
                str(mpi_tasks),
                executable,
                inputstring,
                outputstring,
                xsstring,
            ]
        else:
            run_command = [executable, inputstring, outputstring, xsstring]

        flagnotrun = False

        try:
            cwd = os.getcwd()
            os.chdir(directory)
            # cancel eventual previous output file
            outputfile = name + ".o"
            if os.path.exists(outputfile):
                os.remove(outputfile)

            # check if runtpe exists
            runtpe = name + ".r"
            if os.path.exists(runtpe):
                command = command + " runtpe=" + name + ".r"

            if runoption.lower() == "c":
                try:
                    if not sys.platform.startswith("win"):
                        unix.configure(env_variables)
                    print(" ".join(run_command))
                    subprocess.run(
                        " ".join(run_command), cwd=directory, shell=True, timeout=43200
                    )

                except subprocess.TimeoutExpired:
                    print(
                        "Sesion timed out after 12 hours. Consider submitting as a job."
                    )
                    flagnotrun = True

            elif runoption.lower() == "s":
                # Run MCNP as a job
                cwd = os.getcwd()
                os.chdir(directory)
                self.job_submission(
                    config,
                    directory,
                    run_command,
                    mpi_tasks,
                    omp_threads,
                    env_variables,
                )
                os.chdir(cwd)
        except subprocess.TimeoutExpired:
            pass

        return flagnotrun

    def run_mcnp(
        self,
        config,
        lib_manager,
        name: str,
        directory: Path,
        runoption: str,
        timeout=None,
    ) -> bool:
        """Run MCNP simulation either on the command line or submitted as a job.

        Parameters
        ----------
        config :
            Configuration settings
        lib_manager :
            libmanager
        name : str
            Name of the simulation
        directory : str, path
            Directory where the simulation will be executed
        runoption: str
            Whether JADE run in parallel or command line
        timeout : float, optional
            Maximum time to wait for simulation of complete, by default None

        Returns
        -------
        bool
            Flag if simulation not run
        """

        # Calculate MPI tasks and OpenMP threads
        mpi_tasks = int(config.openmp_threads) * int(config.mpi_tasks)
        omp_threads = 1
        run_mpi = False
        if mpi_tasks > 1:
            run_mpi = True

        executable = config.mcnp_exec
        env_variables = config.mcnp_config
        inputstring = "i=" + name
        outputstring = "n=" + name

        if isinstance(self.lib, dict):
            lib = list(self.lib.values())[0]
        elif isinstance(self.lib, str):
            lib = self.lib

        xsstring = "xs=" + str(lib_manager.data["mcnp"][lib].filename)

        if run_mpi:
            run_command = [
                "mpirun",
                "-n",
                str(mpi_tasks),
                executable,
                inputstring,
                outputstring,
                xsstring,
            ]
        else:
            run_command = [executable, inputstring, outputstring, xsstring]

        flagnotrun = False

        try:
            cwd = os.getcwd()
            os.chdir(directory)
            # cancel eventual previous output file
            outputfile = name + ".o"
            if os.path.exists(outputfile):
                os.remove(outputfile)

            # check if runtpe exists
            runtpe = name + ".r"
            if os.path.exists(runtpe):
                command = command + " runtpe=" + name + ".r"

            if runoption.lower() == "c":
                try:
                    if not sys.platform.startswith("win"):
                        unix.configure(env_variables)
                    print(" ".join(run_command))
                    subprocess.run(
                        " ".join(run_command), cwd=directory, shell=True, timeout=43200
                    )

                except subprocess.TimeoutExpired:
                    print(
                        "Sesion timed out after 12 hours. Consider submitting as a job."
                    )
                    flagnotrun = True

            elif runoption.lower() == "s":
                # Run MCNP as a job
                cwd = os.getcwd()
                os.chdir(directory)
                self.job_submission(
                    config,
                    directory,
                    run_command,
                    mpi_tasks,
                    omp_threads,
                    env_variables,
                )
                os.chdir(cwd)
        except subprocess.TimeoutExpired:
            pass

        return flagnotrun

    def run_serpent(
        self,
        config,
        lib_manager,
        name: str,
        directory: Path,
        runoption: str,
        timeout=None,
    ) -> bool:
        """Run Serpent simulation either on the command line or submitted as a job.

        Parameters
        ----------
        config :
            Configuration settings
        lib_manager :
            libmanager
        name : str
            Name of the simulation
        directory : str, path
            Directory where the simulation will be executed
        runoption: str
            Whether JADE run in parallel or command line
        timeout : float, optional
            Maximum time to wait for simulation of complete, by default None

        Returns
        -------
        bool
            Flag if simulation not run
        """
        # Calculate MPI tasks and OpenMP threads
        mpi_tasks = int(config.mpi_tasks)
        omp_threads = int(config.openmp_threads)
        run_mpi = False
        run_omp = False

        if mpi_tasks > 1:
            run_mpi = True
        if omp_threads > 1:
            run_omp = True

        executable = config.serpent_exec
        env_variables = config.serpent_config
        inputstring = name
        libpath = Path(str(lib_manager.data["serpent"][self.lib].filename))
        data_command = (
            "export SERPENT_DATA="
            + str(libpath.parent)
            + " \nexport SERPENT_ACELIB="
            + str(libpath)
        )
        # Construct the run commands based on user OMP and MPI inputs.
        if run_omp:
            if run_mpi:
                run_command = [
                    "mpirun",
                    "-np",
                    str(mpi_tasks),
                    executable,
                    "-omp",
                    str(omp_threads),
                    inputstring,
                ]
            else:
                run_command = [executable, "-omp", str(omp_threads), inputstring]
        else:
            if run_mpi:
                run_command = ["mpirun", "-np", str(mpi_tasks), executable, inputstring]
            else:
                run_command = [executable, inputstring]

        flagnotrun = False

        if runoption.lower() == "c":
            try:
                os.environ["SERPENT_DATA"] = str(libpath.parent)
                os.environ["SERPENT_ACELIB"] = str(str(libpath))
                unix.configure(env_variables)
                print(" ".join(run_command))
                # subprocess.Popen(" ".join(run_command), cwd=directory, shell=True)
                subprocess.run(
                    " ".join(run_command), cwd=directory, shell=True, timeout=43200
                )

            except subprocess.TimeoutExpired:
                print("Sesion timed out after 12 hours. Consider submitting as a job.")
                flagnotrun = True

        elif runoption.lower() == "s":
            # Run Serpent as a job
            cwd = os.getcwd()
            os.chdir(directory)
            self.job_submission(
                config,
                directory,
                run_command,
                mpi_tasks,
                omp_threads,
                env_variables,
                data_command,
            )
            os.chdir(cwd)

        return flagnotrun

    def run_openmc(
        self, config, lib_manager, name: str, directory, runoption, timeout=None
    ) -> bool:
        """Run OpenMC simulation either on the command line or submitted as a job.

        Parameters
        ----------
        config :
            Configuration settings
        lib_manager :
            libmanager
        name : str
            Name of the simulation
        directory : str, path
            Directory where the simulation will be executed
        runoption: str
            Whether JADE run in parallel or command line
        timeout : float, optional
            Maximum time to wait for simulation of complete, by default None

        Returns
        -------
        bool
            Flag if simulation not run
        """

        # Calculate MPI tasks and OpenMP threads
        mpi_tasks = int(config.mpi_tasks)
        omp_threads = int(config.openmp_threads)
        run_mpi = False
        run_omp = False

        if mpi_tasks > 1:
            run_mpi = True
        if omp_threads > 1:
            run_omp = True

        executable = config.openmc_exec
        env_variables = config.openmc_config
        libpath = Path(str(lib_manager.data["openmc"][self.lib].filename))
        data_command = "export OPENMC_CROSS_SECTIONS=" + str(libpath)

        # Run OpenMC from command line either OMP, MPI or hybrid MPI-OMP
        if run_omp:
            if run_mpi:
                run_command = [
                    "mpirun",
                    "-np",
                    str(mpi_tasks),
                    executable,
                    "--threads",
                    str(omp_threads),
                ]
            else:
                run_command = [executable, "--threads", str(omp_threads)]
        else:
            if run_mpi:
                run_command = ["mpirun", "-np", str(mpi_tasks), executable]
            else:
                run_command = [executable]

        flagnotrun = False

        if runoption.lower() == "c":
            try:
                os.environ["OPENMC_CROSS_SECTIONS"] = str(libpath)
                unix.configure(env_variables)
                print(" ".join(run_command))
                subprocess.run(
                    " ".join(run_command), cwd=directory, shell=True, timeout=43200
                )

            except subprocess.TimeoutExpired:
                print("Sesion timed out after 12 hours. Consider submitting as a job.")
                flagnotrun = True

        elif runoption.lower() == "s":
            # Run Serpent as a job
            cwd = os.getcwd()
            os.chdir(directory)
            self.job_submission(
                config,
                directory,
                run_command,
                mpi_tasks,
                omp_threads,
                env_variables,
                data_command,
            )
            os.chdir(cwd)

        return flagnotrun


class SphereTest(Test):
    """
    Class handling the sphere test
    """

    def generate_test(self, directory, libmanager, limit=None, lib=None):
        """
        Generated all the sphere test for a selected library

        Parameters
        ----------
        directory : str or path
            path to the sphere input folder.
        libmanager : LibManager
            manager of the nuclear data operations.
        limit : int, optional
            limit the test to the first n zaids and materials.
            The default is None.

        Returns
        -------
        None.

        """
        if lib is None:
            lib = self.lib
        # Get typical materials input
        dirmat = os.path.dirname(self.original_inp)
        matpath = os.path.join(dirmat, "TypicalMaterials")
        inpmat = ipt.InputFile.from_text(matpath)
        matlist = inpmat.matlist
        # Get zaids available into the selected library
        zaids = libmanager.get_libzaids(lib, "mcnp")

        # testname = self.inp.name
        if self.d1s:
            testname = "SphereSDDR"
        else:  
            testname = "Sphere"

        motherdir = os.path.join(directory, testname)
        # If previous results are present they are canceled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        if self.d1s:
            os.mkdir(os.path.join(motherdir, "d1s"))
        if self.mcnp:
            os.mkdir(os.path.join(motherdir, "mcnp"))
        if self.serpent:
            os.mkdir(os.path.join(motherdir, "serpent"))
        if self.openmc:
            os.mkdir(os.path.join(motherdir, "openmc"))

        # GET SETTINGS
        # Zaids
        settings = os.path.join(self.test_conf_path, "ZaidSettings.csv")
        settings = pd.read_csv(settings, sep=",").set_index("Z")
        # Materials
        settings_mat = os.path.join(self.test_conf_path, "MaterialsSettings.csv")
        settings_mat = pd.read_csv(settings_mat, sep=",").set_index("Symbol")

        self.run_dir = motherdir

        print(" Zaids:")
        # for zaid in tqdm(zaids):
        for zaid in tqdm(zaids[:limit]):
            Z = int(zaid[:-3])
            # Get Density
            density = settings.loc[Z, "Density [g/cc]"]

            if settings.loc[Z, "Let Override"]:
                # get stop parameters
                if self.nps is None:
                    nps = settings.loc[Z, "NPS cut-off"]
                    if nps is np.nan:
                        nps = None
                else:
                    nps = self.nps

            # Zaid local settings are prioritized
            else:
                nps = settings.loc[Z, "NPS cut-off"]
                if nps is np.nan:
                    nps = None

            self.generate_zaid_test(
                zaid, libmanager, testname, motherdir, -1 * density, nps
            )

        print(" Materials:")
        # for material in tqdm(matlist.materials):
        for material in tqdm(matlist.materials[:limit]):
            # Get density
            density = settings_mat.loc[material.name.upper(), "Density [g/cc]"]

            self.generate_material_test(
                material, -1 * density, libmanager, testname, motherdir
            )

    def generate_zaid_test(
        self,
        zaid,
        libmanager,
        testname,
        motherdir,
        density,
        nps,
        addtag=None,
        parentlist=None,
        lib=None,
    ):
        """
        Generate input for a single zaid sphere leakage benchmark run.

        Parameters
        ----------
        zaid : str
            zaid in string format.
        libmanager : Libmanager
            Jade Libmanager.
        testname : str
            name of the benchmark.
        motherdir : str/path
            Path to the benchmark folder.
        density : (str/float)
            Density value for the sphere.
        nps : float
            number of particles cut-off
        addtag : str, optional
            add tag at the end of the single zaid test name. The default is
            None
        parentlist : list, optional
            add the PIKMT if requested (list of parent zaids)

        Returns
        -------
        None.

        """
        if lib is None:
            lib = self.lib

        # Adjourn the material cards for the zaid
        zaid = mat.Zaid(1, zaid[:-3], zaid[-3:], lib)
        name, formula = libmanager.get_zaidname(zaid)
        if self.d1s:
            # Retrieve wwinp & other misc files if they exist
            directoryVRT = os.path.join(
                self.path_VRT, "d1s", zaid.element + zaid.isotope
            )
            edits_file = os.path.join(directoryVRT, "inp_edits.txt")
            ww_file = os.path.join(directoryVRT, "wwinp")
            # Create MCNP material card
            submat = mat.SubMaterial("M1", [zaid], header="C " + name + " " + formula)
            material = mat.Material([zaid], None, "M1", submaterials=[submat])
            matlist = mat.MatCardsList([material])

            # Generate the new input
            newinp = deepcopy(self.d1s_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # assign stop card
            newinp.add_stopCard(nps)
            # add PIKMT if requested
            if parentlist is not None:
                newinp.add_PIKMT_card(parentlist)

            # Write new input file
            outfile, outdir = self._get_zaidtestname(
                testname, zaid, formula, addtag=addtag
            )
            outpath = os.path.join(motherdir, "d1s", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, "wwinp")
                shutil.copyfile(ww_file, outwwfile)

        if self.mcnp:
            # Retrieve wwinp & other misc files if they exist
            directoryVRT = os.path.join(
                self.path_VRT, "mcnp", zaid.element + zaid.isotope
            )
            edits_file = os.path.join(directoryVRT, "inp_edits.txt")
            ww_file = os.path.join(directoryVRT, "wwinp")
            # Create MCNP material card
            submat = mat.SubMaterial("M1", [zaid], header="C " + name + " " + formula)
            material = mat.Material([zaid], None, "M1", submaterials=[submat])
            matlist = mat.MatCardsList([material])

            # Generate the new input
            newinp = deepcopy(self.mcnp_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # assign stop card
            newinp.add_stopCard(nps)
            # Write new input file
            outfile, outdir = self._get_zaidtestname(
                testname, zaid, formula, addtag=addtag
            )
            outpath = os.path.join(motherdir, "mcnp", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, "wwinp")
                shutil.copyfile(ww_file, outwwfile)

        if self.serpent:
            # Create Serpent material card
            submat = mat.SubMaterial(
                "mat 1", [zaid], header="% " + name + " " + formula
            )
            material = mat.Material(
                [zaid], None, "mat 1", submaterials=[submat], density=density
            )
            matlist = mat.MatCardsList([material])

            # Generate the new input
            newinp = deepcopy(self.serpent_inp)
            newinp.matlist = matlist  # Assign material

            # assign stop card
            newinp.add_stopCard(nps)

            # Write new input file
            outfile, outdir = self._get_zaidtestname(
                testname, zaid, formula, addtag=addtag
            )
            outpath = os.path.join(motherdir, "serpent", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

        if self.openmc:
            # Create MCNP material card
            submat = mat.SubMaterial("m1", [zaid])
            material = mat.Material(
                [zaid], None, "m1", submaterials=[submat], density=density
            )
            matlist = mat.MatCardsList([material])

            # Generate the new input
            newinp = deepcopy(self.openmc_inp)
            newinp.matlist = matlist  # Assign material

            # assign stop card
            newinp.add_stopCard(nps)

            # Write new input file
            outfile, outdir = self._get_zaidtestname(
                testname, zaid, formula, addtag=addtag
            )
            outpath = os.path.join(motherdir, "openmc", outdir)
            os.mkdir(outpath)
            newinp.write(outpath, libmanager)

    @staticmethod
    def _get_zaidtestname(testname, zaid, formula, addtag=None):
        outfile = testname + "_" + zaid.element + zaid.isotope + "_" + formula + "_"
        outdir = testname + "_" + zaid.element + zaid.isotope + "_" + formula

        if addtag is not None:
            outfile = outfile + addtag + "_"
            outdir = outdir + "_" + addtag

        return outfile, outdir

    def generate_material_test(
        self,
        material,
        density,
        libmanager,
        testname,
        motherdir,
        parentlist=None,
        lib=None,
    ):
        """
        Generate a sphere leakage benchmark input for a single typical
        material.

        Parameters
        ----------
        material : matreader.Material
            material object to be used for the new input.
        density : float
            densitiy value in g/cc
        libmanager : Libmanager
            Jade Libmanager.
        testname : str
            name of the benchmark.
        motherdir : str/path
            Path to the benchmark folder.
        parentlist : list, optional
            add the PIKMT if requested (list of parent zaids)

        Returns
        -------
        None.

        """
        if lib is None:
            lib = self.lib
        truename = material.name

        if self.d1s:
            # Retrieve wwinp & other misc files if they exist
            directoryVRT = os.path.join(self.path_VRT, "d1s", truename)
            edits_file = os.path.join(directoryVRT, "inp_edits.txt")
            ww_file = os.path.join(directoryVRT, "wwinp")
            newmat = deepcopy(material)
            # Translate and assign the material
            newmat.translate(lib, libmanager, "mcnp")
            newmat.header = material.header + "C\nC True name:" + truename
            newmat.name = "M1"
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.d1s_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # add stop card
            newinp.add_stopCard(self.nps) 
            # Add PIKMT card if required
            if parentlist is not None:
                newinp.add_PIKMT_card(parentlist)

            # Write new input file
            outfile = testname + "_" + truename + "_"
            outdir = testname + "_" + truename
            outpath = os.path.join(motherdir, "d1s", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, "wwinp")
                shutil.copyfile(ww_file, outwwfile)
            pass

        if self.mcnp:
            # Retrieve wwinp & other misc files if they exist
            directoryVRT = os.path.join(self.path_VRT, "mcnp", truename)
            edits_file = os.path.join(directoryVRT, "inp_edits.txt")
            ww_file = os.path.join(directoryVRT, "wwinp")
            newmat = deepcopy(material)
            # Translate and assign the material
            newmat.translate(lib, libmanager, "mcnp")
            newmat.header = material.header + "C\nC True name:" + truename
            newmat.name = "M1"
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.mcnp_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # add stop card
            newinp.add_stopCard(self.nps)  
            # Add PIKMT card if required
            if parentlist is not None:
                newinp.add_PIKMT_card(parentlist)

            # Write new input file
            outfile = testname + "_" + truename + "_"
            outdir = testname + "_" + truename
            outpath = os.path.join(motherdir, "mcnp", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, "wwinp")
                shutil.copyfile(ww_file, outwwfile)

        if self.serpent:
            newmat = deepcopy(material)
            # Translate and assign the material
            newmat.translate(lib, libmanager, "serpent")
            newmat.header = material.header + "%\n% True name:" + truename
            newmat.name = "mat 1"
            newmat.density = density
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.serpent_inp)
            newinp.matlist = matlist  # Assign material
            # add stop card
            newinp.add_stopCard(self.nps)  # , self.ctme, self.precision)

            # Write new input file
            outfile = testname + "_" + truename + "_"
            outdir = testname + "_" + truename
            outpath = os.path.join(motherdir, "serpent", outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

        if self.openmc:
            newmat = deepcopy(material)
            # Translate and assign the material (not supported yet for openmc)
            # newmat.translate(lib, libmanager, 'openmc')
            newmat.name = "m1"
            newmat.density = density
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.openmc_inp)
            newinp.matlist = matlist  # Assign material
            # add stop card
            newinp.add_stopCard(self.nps)  # , self.ctme, self.precision)

            # Write new input file
            outfile = testname + "_" + truename + "_"
            outdir = testname + "_" + truename
            outpath = os.path.join(motherdir, "openmc", outdir)
            os.mkdir(outpath)
            newinp.write(outpath, libmanager)

    def run(self, config, libmanager, runoption: str) -> None:
        """Sphere leakage requries ad-hoc run method.

        Parameters
        ----------
        config :
            Configuration settings
        libmanager :
            libmanager
        runoption : str
        """

        directory = self.run_dir

        if self.d1s:
            d1s_directory = os.path.join(directory, "d1s")
            if pd.isnull(config.d1s_exec) is not True:
                for folder in tqdm(os.listdir(d1s_directory)):
                    run_directory = os.path.join(d1s_directory, folder)
                    self.run_d1s(config, libmanager, folder + "_", run_directory)

        if self.mcnp:
            mcnp_directory = os.path.join(directory, "mcnp")
            if pd.isnull(config.mcnp_exec) is not True:
                for folder in tqdm(os.listdir(mcnp_directory)):
                    run_directory = os.path.join(mcnp_directory, folder)
                    self.run_mcnp(
                        config, libmanager, folder + "_", run_directory, runoption
                    )

        if self.serpent:
            serpent_directory = os.path.join(directory, "serpent")
            if pd.isnull(config.serpent_exec) is not True:
                for folder in tqdm(os.listdir(serpent_directory)):
                    run_directory = os.path.join(serpent_directory, folder)
                    self.run_serpent(
                        config, libmanager, folder + "_", run_directory, runoption
                    )

        if self.openmc:
            openmc_directory = os.path.join(directory, "openmc")
            if pd.isnull(config.openmc_exec) is not True:
                for folder in tqdm(os.listdir(openmc_directory)):
                    run_directory = os.path.join(openmc_directory, folder)
                    self.run_openmc(
                        config, libmanager, folder + "_", run_directory, runoption
                    )


class SphereTestSDDR(SphereTest):
    def __init__(self, *args, **keyargs):
        super().__init__(*args, **keyargs)
        # Lib needs to be provided in the {activation lib}-{transportlib}
        activationlib, transportlib = check_transport_activation(self.lib)
        self.activationlib = activationlib
        self.transportlib = transportlib

    def generate_test(self, directory, libmanager, limit=None, lib=None):
        super().generate_test(
            directory, libmanager, limit=limit, lib=self.activationlib
        )

    def generate_zaid_test(
        self, zaid, libmanager, testname, motherdir, density, nps
    ):
        """
        Generate input for a single zaid sphere SDDR benchmark run.
        Depending on the number of reactions, multiple inputs may be generated
        from a single zaid.

        Parameters
        ----------
        zaid : str
            zaid in string format.
        libmanager : Libmanager
            Jade Libmanager.
        testname : str
            name of the benchmark.
        motherdir : str/path
            Path to the benchmark folder.
        density : (str/float)
            Density value for the sphere.
        nps : float
            number of particles cut-off

        Returns
        -------
        None.
        """

        # Recover the available reactions
        reactions = libmanager.get_reactions(self.activationlib, zaid)

        # Genearate a different test for each reaction
        for reaction in reactions:
            MT = reaction[0]
            daughter = reaction[1]
            # generate the input file
            super().generate_zaid_test(
                zaid,
                libmanager,
                testname,
                motherdir,
                density,
                nps,
                addtag=MT,
                parentlist=[zaid],
                lib=self.activationlib,
            )

            # --- Add the irradiation file ---
            # generate file
            reacfile = self._generate_reaction_file([(zaid, MT, daughter)])
            # Recover ouput directory
            name, formula = libmanager.get_zaidname(zaid)
            zaidob = mat.Zaid(1, zaid[:-3], zaid[-3:], self.activationlib)
            _, outdir = self._get_zaidtestname(testname, zaidob, formula, addtag=MT)
            outpath = os.path.join(motherdir, outdir)
            reacfile.write(outpath)

            # --- Add the irradiation file ---
            irrfile, ans = self._generate_irradiation_file([daughter])
            irrfile.write(outpath)
            if not ans:
                print(
                    CORANGE
                    + " Warning: {} irr file was not generated".format(outdir)
                    + CEND
                )

    def generate_material_test(
        self, material, density, libmanager, testname, motherdir
    ):
        """
        Generate a sphere leakage benchmark input for a single typical
        material.

        Parameters
        ----------
        material : matreader.Material
            material object to be used for the new input.
        density : float
            densitiy value in g/cc
        libmanager : Libmanager
            Jade Libmanager.
        testname : str
            name of the benchmark.
        motherdir : str/path
            Path to the benchmark folder.

        Returns
        -------
        None.

        """
        # there will only be one test for each material that includes
        # all the possible reactions
        truename = material.name

        # --- Add the reaction file ---
        # Recover all the reactions (for each isotope) in the material
        reactions = []
        parentlist = []
        daughterlist = []
        transportlist = []
        for submat in material.submaterials:
            for zaid in submat.zaidList:
                parent = zaid.element + zaid.isotope
                zaidreactions = libmanager.get_reactions(self.activationlib, parent)
                if len(zaidreactions) > 0:
                    # it is a parent only if reactions are available
                    parentlist.append(parent)
                else:
                    # normal transport
                    transportlist.append(parent)

                for MT, daughter in zaidreactions:
                    reactions.append((parent, MT, daughter))
                    daughterlist.append(daughter)

        # eliminate duplicates
        daughterlist = list(set(daughterlist))
        parentlist = list(set(parentlist))
        transportlist = list(set(transportlist))

        # The generation of the inputs has to be done only if there is at
        # least one parent
        if len(parentlist) == 0:
            return
        else:
            # generate the input
            libs = {self.activationlib: parentlist, self.transportlib: transportlist}
            super().generate_material_test(
                material,
                density,
                libmanager,
                testname,
                motherdir,
                parentlist=parentlist,
                lib=libs,
            )
            # Generate the reaction file
            reac_file = self._generate_reaction_file(reactions)
            # recover output directory and write file
            outdir = testname + "_" + truename
            outpath = os.path.join(motherdir, outdir)
            reac_file.write(outpath)

            # --- Add the irradiation file ---
            irrfile, ans = self._generate_irradiation_file(set(daughterlist))
            irrfile.write(outpath)
            if not ans:
                print(
                    CORANGE
                    + " Warning: {} irr file was not generated".format(outdir)
                    + CEND
                )

    def _generate_reaction_file(self, reactions):
        """
        Generate a reaction file object given the parents and reactions
        selected

        Parameters
        ----------
        parent : str
            parent zaid num (e.g. 1001).
        reactions : list
            list of reactions (parent, MT, daughter) to be used.

        Returns
        -------
        ReactionFile
            Reaction file associated with the test.

        """
        reaction_list = []
        for parent, MT, daughter in reactions:
            parent = parent + "." + self.activationlib
            rx = Reaction(parent, MT, daughter)
            reaction_list.append(rx)

        return ReactionFile(reaction_list)

    def _generate_irradiation_file(self, daughters):
        """
        Generate a D1S irradiation file selecting irradiation schedules from
        an existing file.

        Parameters
        ----------
        daughters : list.
            daughter zaids to be selected

        Returns
        -------
        irradfile : IrradiationFile
            newly generated irradiation file
        ans : bool
            the object was created without issues

        """
        try:
            filepath = os.path.join(self.test_conf_path, "irrad_" + self.activationlib)
        except FileNotFoundError:
            print(
                CRED
                + """
 Please provide an irradiation file summary for lib {}. Check the documentation
 for additional details. The application will now exit.
                  """.format(
                    self.activationlib
                )
                + CEND
            )
            sys.exit()

        irradfile = IrradiationFile.from_text(filepath)
        # Keep only useful irradiations
        new_irradiations = []
        for irradiation in irradfile.irr_schedules:
            if irradiation.daughter in daughters:
                new_irradiations.append(irradiation)

        if len(new_irradiations) != len(daughters):
            print(
                CORANGE
                + """
 Warning: irradiation schedules were not found for all specified daughters.
 """
                + CEND
            )
            ans = False
        else:
            ans = True

        irradfile.irr_schedules = new_irradiations
        return irradfile, ans


class FNGTest(Test):
    def custom_inp_modifications(self):
        # Add the tracking for daughters in tally 14
        zaids = self.irrad.get_daughters()
        self.d1s_inp.add_track_contribution("F14:p", zaids, who="daughter")
        # Add the tracking for daughters in tally 24
        zaids = self.react.get_parents()
        self.d1s_inp.add_track_contribution("F24:p", zaids, who="parent")


class MultipleTest:
    def __init__(self, inpsfolder, lib, config, log, confpath, runoption, TestOb=Test):
        """
        A collection of Tests

        Parameters
        ----------
        inpsfolder : path-like object
            folder that contains all inputs of the tests.
        lib : str
            library suffix to use (e.g. 31c).
        config : pd.DataFrame (single row)
            configuration options for the test.
        log : Log
            Jade log file access.
        confpath : path like object
            path to the test configuration folder.
        TestOb : testrun.Test, optional
            type of test object to be used. The default is Test.

        Returns
        -------
        None.

        """
        tests = []
        for folder in os.listdir(inpsfolder):
            inp = os.path.join(inpsfolder, folder)
            test = TestOb(inp, lib, config, log, confpath, runoption)
            tests.append(test)
        self.tests = tests
        self.name = os.path.basename(inpsfolder)

    def generate_test(self, lib_directory, libmanager):
        """
        Generate all the tests of the collection

        Parameters
        ----------
        lib_directory : path-like
            output directory where to generate the tests.
        libmanager : libmanager.LibManager
            object handling libraries operations.

        Returns
        -------
        None.

        """
        self.MCNPdir = os.path.join(lib_directory, self.name)
        safe_override(self.MCNPdir)
        for test in self.tests:
            mcnp_dir = os.path.join(self.MCNPdir, test.name)
            test.generate_test(lib_directory, libmanager, run_dir=mcnp_dir)

    def run(self, config, libmanager, runoption: str) -> None:
        """Run all tests

        Parameters
        ----------
        config :
            Configuration settings
        libmanager :
            libmanager
        runoption : str
            command line or as a job
        """
        for test in tqdm(self.tests):
            test.run(config, libmanager, runoption)


def safe_mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def safe_override(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


def check_transport_activation(lib):
    # Operate on the newlib, should arrive in the 99c-31c format
    errmsg = """
 Please define the pair activation-transport lib for the FNG benchmark
 (e.g. 99c-31c). See additional details on the documentation.
            """
    try:
        activationlib = lib.split("-")[0]
        transportlib = lib.split("-")[1]
    except IndexError:
        raise ValueError(errmsg)
    # Check that libraries have been correctly defined
    if activationlib + "-" + transportlib != lib:
        raise ValueError(errmsg)

    return activationlib, transportlib
