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

import jade.inputfile as ipt
import jade.matreader as mat
import os
import subprocess
import shutil
import pandas as pd
import numpy as np
import sys

from pathlib import Path
from copy import deepcopy
from tqdm import tqdm
from jade.parsersD1S import (IrradiationFile, ReactionFile, Reaction)


CODE_TAGS = {'mcnp6': 'mcnp6', 'D1S5': 'd1suned3.1.2'}
D1S_CODES = ['D1S5']

# colors
CRED = '\033[91m'
CORANGE = '\033[93m'
CEND = '\033[0m'


class Test():

    def __init__(self, inp, lib, config, log, VRTpath, confpath):
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
        VRTpath : path like object
           path to the variance reduction folder.
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

        # Configuration options for the test
        self.config = config

        # MCNP original input
        self.original_inp = inp

        # Log for warnings
        self.log = log

        # VRT path
        self.path_VRT = VRTpath

        # Get the configuration files path
        self.test_conf_path = confpath

        # Inout variables
        self.mcnp_ipt = None
        self.serpent_ipt = None
        self.openmc_ipt = None
        self.d1s_ipt = None

        self.irrad = None
        self.react = None

        # Path variables
        self.run_dir = None
        #self.serpent_dir = None
        #self.openmc_dir = None
        #self.d1s_dir = None

        config = config.dropna()

        self.name = config['Folder Name']

        try:
            self.nps = config['NPS cut-off']
        except KeyError:
            self.nps = None
        if self.nps is np.nan:
            self.nps = None        
        
        # Updated to handle multiple codes
        try:
            self.mcnp = bool(config['MCNP'])
        except KeyError:
            self.mcnp = False
        try:
            self.serpent = bool(config['Serpent'])
        except KeyError:
            self.serpent = False
        try:
            self.openmc = bool(config['OpenMC'])
        except KeyError:
            self.openmc = False
        try:
            self.d1s = bool(config['d1S'])
        except KeyError:
            self.d1s = False

        """
        # Chek for valid code
        code = config['Code']
        if code not in CODE_TAGS.keys():
            raise ValueError(code+' is not an admissible value for code.\n' +
                             'Please double check the configuration file.')
        else:
            self.code = code  # transport code to be used for the benchmark
        """
        # Generate input file template according to code
        #if code == 'D1S5':
        if self.d1s:
            d1s_ipt = os.path.join(inp, 'd1s', self.name+'.i')
            self.d1s_inp = ipt.D1S5_InputFile.from_text(d1s_ipt)
            # It also have additional files then that must be in the
            # VRT folder (irradiation and reaction files)
            irrfile = os.path.join(VRTpath, self.d1s_inp.name,
                                   self.inp.name+'_irrad')
            reacfile = os.path.join(VRTpath, self.d1s_inp.name,
                                    self.d1s_inp.name+'_react')
            try:
                self.irrad = IrradiationFile.from_text(irrfile)
                self.react = ReactionFile.from_text(reacfile)
            except FileNotFoundError:
                self.log.adjourn('d1S irradition and reaction files not found, skipping...')
                # For instance in sphere test they are not provided
                # There may be reasons why these files are not provided, it is
                # responsability of the user to make them available or not.
                #self.irrad = None
                #self.react = None
        if self.mcnp:
            mcnp_ipt = os.path.join(inp, 'mcnp',  self.name+'.i')
            self.mcnp_inp = ipt.InputFile.from_text(mcnp_ipt)
            #self.irrad = None
            #self.react = None
        if self.serpent:
            # Add serpent initialisation here
            #self.log.adjourn('Serpent running not implimented yet, skipping...')
            serpent_ipt = os.path.join(inp, 'serpent',  self.name+'.i')
            self.serpent_inp = ipt.SerpentInputFile.from_text(serpent_ipt)           
        if self.openmc:
            # Add openmc initialisation here
            self.log.adjourn('Serpent running not implimented yet, skipping...')

        # Name of input file
        #self.name = self.inp.name

        # Add the stop card according to config
        """
        config = config.dropna()
        try:
            nps = config['NPS cut-off']
        except KeyError:
            nps = None
        if nps is np.nan:
            nps = None
        try:
            ctme = config['CTME cut-off']
        except KeyError:
            ctme = None
        if ctme is np.nan:
            ctme = None
        try:
            tally = config['Relative Error cut-off'].split('-')[0]
            error = config['Relative Error cut-off'].split('-')[1]
            precision = (tally, error)
        except KeyError:
            precision = None

        self.nps = nps
        self.ctme = ctme
        self.precision = precision

        # Directory where the MCNP run will be performed
        self.MCNPdir = None
        """

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
        #if isinstance(self.inp, ipt.D1S_Input):
        if self.d1s:
            # Then it was the translation of a D1S input, additional
            # actions are required
            add = self.d1s_inp.translate(lib, libmanager, 'd1s',
                                         original_irradfile=self.irrad,
                                         original_reacfile=self.react)
            newirradiations = add[0]
            newreactions = add[1]
            self.irrad.irr_schedules = newirradiations
            self.react.reactions = newreactions
            self.d1s_inp.update_zaidinfo(libmanager)
        if self.mcnp:
            self.mcnp_inp.translate(lib, libmanager, 'mcnp')
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
        #self.inp.add_stopCard(self.nps, self.ctme, self.precision)
        if self.d1s:
            self.d1s_inp.add_stopCard(self.nps)
        if self.mcnp:
            self.mcnp_inp.add_stopCard(self.nps)
        if self.serpent:
            self.serpent_inp.add_stopCard(self.nps)
        if self.openmc:
            pass

        # Identify working directory
        #testname = self.inp.name
        testname = self.name
        if run_dir is None:
            motherdir = os.path.join(lib_directory, testname) 
        else:
            motherdir = run_dir
        self.run_dir = motherdir
        # If previous results are present they are canceled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        # edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        # ww_file = os.path.join(directoryVRT, 'wwinp')
        # if os.path.exists(directoryVRT):
        #     # This was tested only for sphere... be careful
        #     self.inp.add_edits(edits_file)  # Add variance reduction

        # Allow space for personalization getting additional modification
        self.custom_inp_modifications()

        if self.d1s:
            os.mkdir(os.path.join(motherdir, 'd1s'))
            outinpfile = os.path.join(motherdir, testname, 'd1s')
            self.d1s_inp.write(outinpfile)
            # And accessory files if needed
            if self.irrad is not None:
                self.irrad.write(motherdir, testname, 'd1s')
            if self.react is not None:
                self.react.write(motherdir, testname, 'd1s')
            # Get VRT files if available
            wwinp = os.path.join(self.path_VRT, testname, 'wwinp')
            if os.path.exists(wwinp):
                outfile = os.path.join(motherdir, testname, 'mcnp', 'wwinp')
                shutil.copyfile(wwinp, outfile)

        if self.mcnp:
            os.mkdir(os.path.join(motherdir, 'mcnp'))
            outinpfile = os.path.join(motherdir, testname, 'mcnp')
            self.mcnp_inp.write(outinpfile)
            # Get VRT files if available
            wwinp = os.path.join(self.path_VRT, testname, 'wwinp')
            if os.path.exists(wwinp):
                outfile = os.path.join(motherdir, testname, 'mcnp', 'wwinp')
                shutil.copyfile(wwinp, outfile)
        
        if self.serpent:
            # Impliment serpent outputfile generation here
            pass

        if self.openmc:
            # Impliment openmc outputfile generation here
            pass            

        """
        # Write new input file
        outinpfile = os.path.join(motherdir, testname)
        self.inp.write(outinpfile)
        # And accessory files if needed
        if self.irrad is not None:
            self.irrad.write(motherdir)
        if self.react is not None:
            self.react.write(motherdir)

        # Get VRT files if available
        wwinp = os.path.join(self.path_VRT, testname, 'wwinp')
        if os.path.exists(wwinp):
            outfile = os.path.join(motherdir, 'wwinp')
            shutil.copyfile(wwinp, outfile)
        """

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

    #def run(self, cpu=1, timeout=None):
    def run(self, config, lib_manager):
        """
        run the input

        Parameters
        ----------
        cpu : int, optional
            number of CPU to be used. The default is 1.
        timeout : int, optional
            number of seconds after the simulation should be killed.
            The default is None.def run

        Returns
        -------
        None.

        """
        """
        name = self.name
        directory = self.MCNPdir
        code_tag = CODE_TAGS[self.code]

        self._runMCNP(code_tag, name, directory, cpu=cpu, timeout=timeout)

        """
        name = self.name
        directory = self.run_dir

        if self.d1s:
            d1s_directory = os.path.join(directory, name, 'd1s')
            if config.d1s_exec != '':
                self.run_d1s(config, name, d1s_directory)
        if self.mcnp:
            mcnp_directory = os.path.join(directory, name, 'mcnp')
            if config.mcnp_exec != '':
                self.run_mcnp(config, name, mcnp_directory)
        if self.serpent:
            serpent_directory = os.path.join(directory, name, 'serpent')
            if config.serpent_exec != '':
                self.run_serpent(config, name, serpent_directory)
        if self.openmc:
            openmc_directory = os.path.join(directory, name, 'openmc')
            if config.openmc_exec != '':
                self.run_openmc(config, name, openmc_directory)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Edited by D. Wheeler ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #job submission currently tailored for LoadLeveler, may be applicable to other submission systems with equivalent dummy variables
    def job_submission(self, config, name, directory, command, env_variables, mpi_tasks):
        fout = open(directory + os.path.basename(config.batch_file), "wt")
        with open(config.batch_file, "rt") as fin:
            contents = fin.read()
        contents.replace("COMMAND", command)
        contents.replace("ENV_VARIABLES", "source "+env_variables)
        contents.replace("INITIAL_DIR", directory)
        contents.replace("OUT_FILE", name+"_job_out")
        contents.replace("ERR_FILE", name+"_job_error")
        fout.write(contents)
        
        fin.close()
        fout.close()

        subprocess.run(config.batch_system + os.path.basename(config.batch_file), cwd=directory)
            
    #@staticmethod
    def run_d1s(self, config, lib_manager, name, directory):
        pass
 
    #@staticmethod
    def run_mcnp(self, config, lib_manager, name, directory, timeout=None):
        mpi_tasks = int(config.openmp_threads) * int(config.mpi_tasks)
        run_mpi = False
        if mpi_tasks > 1:
            mpistring = 'mpirun -n ' + str(mpi_tasks)
            run_mpi = True
        executable = config.mcnp_exec
        env_variables = config.mcnp_config
        inputstring = 'i=' + name
        outputstring = 'n=' + name
        xsstring = 'xs='+lib_manager.XS.mcnp_data[self.lib].filename
        if run_mpi:
            #command = ' '.join([mpistring, executable, inputstring, outputstring])
            command = ['mpirun', '-n', str(mpi_tasks), executable, inputstring, outputstring, xsstring]
        else:
            command = [executable, inputstring, outputstring, xsstring]
        flagnotrun = False
        try:
            cwd = os.getcwd()
            os.chdir(directory)
            # cancel eventual previous output file
            outputfile = name+'.o'
            if os.path.exists(outputfile):
                os.remove(outputfile)

            # check if runtpe exits
            runtpe = name+'.r'
            if os.path.exists(runtpe):
                command = command+' runtpe='+name+'.r'

            print(command)
            print(cwd)
            # Execution
            if pd.isnull(config.batch_system) is True:
                subprocess.run(command, cwd=directory,
                           #creationflags=subprocess.CREATE_NEW_CONSOLE,
                            timeout=timeout)
            else:
                self.job_submission(config, name, directory, command, env_variables, mpi_tasks)
            os.chdir(cwd)
        except subprocess.TimeoutExpired:
            pass

        return flagnotrun

    #@staticmethod
    def run_serpent(self, config, lib_manager, name, directory, timeout=None):
        mpi_tasks = int(config.openmp_threads) * int(config.mpi_tasks)
        run_mpi = False
        if mpi_tasks > 1:
            mpistring = 'mpirun -n ' + str(mpi_tasks)
            run_mpi = True
        executable = config.serpent_exec
        env_variables = config.serpent_config
        inputstring = name
        libpath = Path(str(lib_manager.XS.serpent_data[self.lib].filename))
        print(str(lib_manager.XS.serpent_data[self.lib].filename))
        datastring = 'SERPENT_DATA='+str(libpath.parent) + "\n export SERPENT_DATA"
        xsstring = 'SERPENT_ACELIB='+str(libpath.stem) + ".xsdata \n export SERPENT_ACELIB"
        decstring = 'SERPENT_DECLIB='+str(libpath.stem) + ".dec \n export SERPENT_DECLIB"
        nfystring = 'SERPENT_NFYLIB='+str(libpath.stem) + ".nfy \n export SERPENT_NFYLIB"
        if run_mpi:
            #command = ' '.join([mpistring, executable, inputstring, outputstring])
            command = ['mpirun', '-n', str(mpi_tasks), executable, inputstring]
        else:
            command = [executable, inputstring]
        flagnotrun = False
        try:
            cwd = os.getcwd()
            os.chdir(directory)

            print(command)
            print(cwd)
            # Execution
            if pd.isnull(config.batch_system) is True:
                os.system("bash "+ env_variables)
                print(datastring + " \n " + xsstring + " \n "+ decstring + " \n "+ nfystring)
                subprocess.run(command, cwd=directory, timeout=timeout)
            else:
                self.job_submission(config, name, directory, command, env_variables, mpi_tasks)
            os.chdir(cwd)
        except subprocess.TimeoutExpired:
            pass

        return flagnotrun
        pass

    #@staticmethod
    def run_openmc(self, config, lib_manager, name, directory):
        pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Legacy MCNP runner
    @staticmethod
    def _runMCNP(code, name, directory, cpu=1, timeout=None):
        """
        Run or continue test execution

        Parameters
        ----------
        code : str
            tag of the code to be used (e.g. mcnp6)
        name : str
            MCNP inputfile name.
        directory : str/path
            path to the test.
        cpu : int, optional
            Number of CPU to use. The default is 1.
        timeout : int, optional
            Time in s for emergency timeout. The default is None.

        Returns
        -------
        flagnotrun : Bool
            If true the timeout was reached.

        """
        command = 'name='+name+' wwinp=wwinp tasks '+str(cpu)
        flagnotrun = False
        try:
            # cancel eventual previous output file
            outputfile = os.path.join(directory, name+'o')
            if os.path.exists(outputfile):
                os.remove(outputfile)

            # check if runtpe exits
            runtpe = os.path.join(directory, name+'r')
            if os.path.exists(runtpe):
                command = command+' runtpe='+name+'r'

            # Execution
            subprocess.run([shutil.which(code), command], cwd=directory,
                           #creationflags=subprocess.CREATE_NEW_CONSOLE,
                            timeout=timeout)

        except subprocess.TimeoutExpired:
            pass

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
        matpath = os.path.join(dirmat, 'TypicalMaterials')
        inpmat = ipt.InputFile.from_text(matpath)
        matlist = inpmat.matlist
        # Get zaids available into the selected library
        zaids = libmanager.get_libzaids(lib, 'mcnp')

        #testname = self.inp.name
        testname = self.name
        
        motherdir = os.path.join(directory, testname)
        # If previous results are present they are canceled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        if self.d1s:
            os.mkdir(os.path.join(motherdir, 'd1s'))
        if self.mcnp:
            os.mkdir(os.path.join(motherdir, 'mcnp'))       
        if self.serpent:
            os.mkdir(os.path.join(motherdir, 'serpent'))
        if self.openmc:
            os.mkdir(os.path.join(motherdir, 'openmc'))

        # GET SETTINGS
        # Zaids
        settings = os.path.join(self.test_conf_path, 'ZaidSettings.csv')
        settings = pd.read_csv(settings, sep=',').set_index('Z')
        # Materials
        settings_mat = os.path.join(self.test_conf_path,
                                    'MaterialsSettings.csv')
        settings_mat = pd.read_csv(settings_mat, sep=',').set_index('Symbol')

        self.run_dir = motherdir

        print(' Zaids:')
        # for zaid in tqdm(zaids):
        for zaid in tqdm(zaids[:limit]):
            Z = int(zaid[:-3])
            # Get Density
            density = settings.loc[Z, 'Density [g/cc]']

            if settings.loc[Z, 'Let Override']:
                # get stop parameters
                if self.nps is None:
                    nps = settings.loc[Z, 'NPS cut-off']
                    if nps is np.nan:
                        nps = None
                else:
                    nps = self.nps

                #if self.ctme is None:
                #    ctme = settings.loc[Z, 'CTME cut-off']
                #    if ctme is np.nan:
                #        ctme = None
                #else:
                #    ctme = self.ctme
                #
                #if self.precision is None:
                #    prec = settings.loc[Z, 'Relative Error cut-off']
                #    if prec is np.nan:
                #        precision = None
                #    else:
                #        tally = prec.split('-')[0]
                #        error = prec.split('-')[1]
                #        precision = (tally, error)
                #else:
                #    precision = self.precision

            # Zaid local settings are prioritized
            else:
                nps = settings.loc[Z, 'NPS cut-off']
                if nps is np.nan:
                    nps = None

                #ctme = settings.loc[Z, 'CTME cut-off']
                #if ctme is np.nan:
                #    ctme = None
                #
                #prec = settings.loc[Z, 'Relative Error cut-off']
                #if prec is np.nan:
                #    precision = None
                #else:
                #    tally = prec.split('-')[0]
                #    error = prec.split('-')[1]
                #    precision = (tally, error)

            self.generate_zaid_test(zaid, libmanager, testname,
                                    motherdir, -1*density, nps)

        print(' Materials:')
        # for material in tqdm(matlist.materials):
        for material in tqdm(matlist.materials[:limit]):
            # Get density
            density = settings_mat.loc[material.name.upper(), 'Density [g/cc]']

            self.generate_material_test(material, -1*density, libmanager,
                                        testname, motherdir)

#    def generate_zaid_test(self, zaid, libmanager, testname, motherdir,
#                           density, nps, ctme, precision, addtag=None,
#                           parentlist=None, lib=None):
    def generate_zaid_test(self, zaid, libmanager, testname, motherdir,
                           density, nps, addtag=None,
                           parentlist=None, lib=None):
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
        ctme : float
            computer time cut-off
        precision : float
            precision cut-off
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

        # Get VRT files
        directoryVRT = os.path.join(self.path_VRT, zaid)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')

        # Adjourn the material cards for the zaid
        zaid = mat.Zaid(1, zaid[:-3], zaid[-3:], lib)
        name, formula = libmanager.get_zaidname(zaid)

        if self.d1s:
            # Add d1s function here
            pass           
        
        if self.mcnp:
            # Create MCNP material card
            submat = mat.SubMaterial('M1', [zaid],
                                     header='C '+name+' '+formula)
            material = mat.Material([zaid], None, 'M1', submaterials=[submat])
            matlist = mat.MatCardsList([material])            
            
            # Generate the new input
            newinp = deepcopy(self.mcnp_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # assign stop card
            newinp.add_stopCard(nps)#, ctme, precision)
            # add PIKMT if requested
            if parentlist is not None:
                newinp.add_PIKMT_card(parentlist)

            if os.path.exists(directoryVRT):
                newinp.add_edits(edits_file)  # Add variance reduction

            # Write new input file
            outfile, outdir = self._get_zaidtestname(testname, zaid, formula,
                                                    addtag=addtag)
            outpath = os.path.join(motherdir, 'mcnp', outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, 'wwinp')
                shutil.copyfile(ww_file, outwwfile)

        if self.serpent:
            # Create MCNP material card
            submat = mat.SubMaterial('mat 1', [zaid],
                                     header='% '+name+' '+formula)
            material = mat.Material([zaid], None, 'mat 1', submaterials=[submat], density=density)
            matlist = mat.MatCardsList([material])

            # Generate the new input
            newinp = deepcopy(self.serpent_inp)
            newinp.matlist = matlist  # Assign material
            
            # assign stop card
            newinp.add_stopCard(nps)

            # Write new input file
            outfile, outdir = self._get_zaidtestname(testname, zaid, formula,
                                                    addtag=addtag)
            outpath = os.path.join(motherdir, 'serpent', outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

        if self.openmc:
            # Add openmc function here
            pass


    @staticmethod
    def _get_zaidtestname(testname, zaid, formula, addtag=None):

        outfile = (testname+'_'+zaid.element+zaid.isotope+'_'+formula+'_')
        outdir = testname+'_'+zaid.element+zaid.isotope+'_'+formula

        if addtag is not None:
            outfile = outfile+addtag+'_'
            outdir = outdir+'_'+addtag

        return outfile, outdir

    def generate_material_test(self, material, density, libmanager, testname,
                               motherdir, parentlist=None, lib=None):
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
        # Get VRT file
        directoryVRT = os.path.join(self.path_VRT, truename)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')

        if self.d1s:
            # Add d1s function here
            pass
        
        if self.mcnp:
            newmat = deepcopy(material)
            # Translate and assign the material
            newmat.translate(lib, libmanager, 'mcnp')
            newmat.header = material.header+'C\nC True name:'+truename
            newmat.name = 'M1'
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.mcnp_inp)
            newinp.matlist = matlist  # Assign material
            # adjourn density
            newinp.change_density(density)
            # add stop card
            newinp.add_stopCard(self.nps)#, self.ctme, self.precision)
            # Add PIKMT card if required
            if parentlist is not None:
                newinp.add_PIKMT_card(parentlist)

            if os.path.exists(directoryVRT):
                newinp.add_edits(edits_file)  # Add variance reduction

            # Write new input file
            outfile = testname+'_'+truename+'_'
            outdir = testname+'_'+truename
            outpath = os.path.join(motherdir, 'mcnp', outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

            # Copy also wwinp file
            if os.path.exists(directoryVRT):
                outwwfile = os.path.join(outpath, 'wwinp')
                shutil.copyfile(ww_file, outwwfile)

        if self.serpent:
            newmat = deepcopy(material)
            # Translate and assign the material
            newmat.translate(lib, libmanager, 'serpent')
            newmat.header = material.header+'%\n% True name:'+truename
            newmat.name = 'mat 1'
            newmat.density = density
            matlist = mat.MatCardsList([newmat])

            # Generate the new input
            newinp = deepcopy(self.serpent_inp)
            newinp.matlist = matlist  # Assign material
            # add stop card
            newinp.add_stopCard(self.nps)#, self.ctme, self.precision)

            # Write new input file
            outfile = testname+'_'+truename+'_'
            outdir = testname+'_'+truename
            outpath = os.path.join(motherdir, 'serpent', outdir)
            os.mkdir(outpath)
            outinpfile = os.path.join(outpath, outfile)
            newinp.write(outinpfile)

        if self.openmc:
            # Add openmc function here
            pass

#    def run(self, cpu=1, timeout=None):
    def run(self, config, lib_manager):
        """
        Sphere test needs an ad-hoc run method to run all zaids tests
        """
        """
        flagnotrun = False
        for folder in tqdm(os.listdir(self.run_dir)):
            path = os.path.join(self.MCNPdir, folder)
            name = folder+'_'
            code = 'mcnp6'
            command = 'name='+name+' wwinp=wwinp tasks '+str(cpu)
            try:
                subprocess.run([code, command], cwd=path,
                               #creationflags=subprocess.CREATE_NEW_CONSOLE,
                               timeout=timeout)

            except subprocess.TimeoutExpired:
                flagnotrun = True
                self.log.adjourn(name+' reached timeout, eliminate folder')
                continue

        """
 #       if flagnotrun:
 #           print("""
 #Some MCNP run reached timeout, they are listed in the log file.
 #Please remove their folders before attempting to postprocess the library""")

        
        directory = self.run_dir

        if self.d1s:
            d1s_directory = os.path.join(directory, 'd1s')
            if pd.isnull(config.d1s_exec) is not True:
                for folder in tqdm(os.listdir(d1s_directory)):
                    run_directory = os.path.join(d1s_directory, folder)
                    self.run_d1s(config, lib_manager, folder+'_', run_directory)
        if self.serpent:
            serpent_directory = os.path.join(directory, 'serpent')
            if pd.isnull(config.serpent_exec) is not True:
                for folder in tqdm(os.listdir(serpent_directory)):
                    run_directory = os.path.join(serpent_directory, folder)                 
                    self.run_serpent(config, lib_manager, folder+'_', run_directory)
        if self.mcnp:
            mcnp_directory = os.path.join(directory, 'mcnp')
            if pd.isnull(config.mcnp_exec) is not True:
                for folder in tqdm(os.listdir(mcnp_directory)):
                    run_directory = os.path.join(mcnp_directory, folder)           
                    self.run_mcnp(config, lib_manager, folder+'_', run_directory)
        if self.openmc:
            openmc_directory = os.path.join(directory, 'openmc')
            if pd.isnull(config.openmc_exec) is not True:
                for folder in tqdm(os.listdir(openmc_directory)):
                    run_directory = os.path.join(openmc_directory, folder)                 
                    self.run_openmc(config, lib_manager, folder+'_', run_directory)

# Fix from here
class SphereTestSDDR(SphereTest):

    def __init__(self, *args, **keyargs):
        super().__init__(*args, **keyargs)
        # Lib needs to be provided in the {activation lib}-{transportlib}
        activationlib, transportlib = check_transport_activation(self.lib)
        self.activationlib = activationlib
        self.transportlib = transportlib

    def generate_test(self, directory, libmanager, limit=None, lib=None):

        super().generate_test(directory, libmanager, limit=limit,
                              lib=self.activationlib)

    def generate_zaid_test(self, zaid, libmanager, testname, motherdir,
                           density, nps, ctme, precision):
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
        ctme : float
            computer time cut-off
        precision : float
            precision cut-off

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
            super().generate_zaid_test(zaid, libmanager, testname,
                                       motherdir, density, nps, ctme,
                                       precision, addtag=MT,
                                       parentlist=[zaid],
                                       lib=self.activationlib)

            # --- Add the irradiation file ---
            # generate file
            reacfile = self._generate_reaction_file([(zaid, MT, daughter)])
            # Recover ouput directory
            name, formula = libmanager.get_zaidname(zaid)
            zaidob = mat.Zaid(1, zaid[:-3], zaid[-3:], self.activationlib)
            _, outdir = self._get_zaidtestname(testname, zaidob, formula,
                                               addtag=MT)
            outpath = os.path.join(motherdir, outdir)
            reacfile.write(outpath)

            # --- Add the irradiation file ---
            irrfile, ans = self._generate_irradiation_file([daughter])
            irrfile.write(outpath)
            if not ans:
                print(CORANGE +
                      ' Warning: {} irr file was not generated'.format(outdir)+
                      CEND)

    def generate_material_test(self, material, density, libmanager, testname,
                               motherdir):
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
                parent = zaid.element+zaid.isotope
                zaidreactions = libmanager.get_reactions(self.activationlib,
                                                         parent)
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
            libs = {self.activationlib: parentlist,
                    self.transportlib: transportlist}
            super().generate_material_test(material, density, libmanager,
                                           testname,
                                           motherdir, parentlist=parentlist,
                                           lib=libs)
            # Generate the reaction file
            reac_file = self._generate_reaction_file(reactions)
            # recover output directory and write file
            outdir = testname+'_'+truename
            outpath = os.path.join(motherdir, outdir)
            reac_file.write(outpath)

            # --- Add the irradiation file ---
            irrfile, ans = self._generate_irradiation_file(set(daughterlist))
            irrfile.write(outpath)
            if not ans:
                print(CORANGE +
                      ' Warning: {} irr file was not generated'.format(outdir)+
                      CEND)

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
            parent = parent+'.'+self.activationlib
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
            filepath = os.path.join(self.test_conf_path, 'irrad_'+self.activationlib)
        except FileNotFoundError:
            print(CRED+"""
 Please provide an irradiation file summary for lib {}. Check the documentation
 for additional details. The application will now exit.
                  """.format(self.activationlib)+CEND)
            sys.exit()

        irradfile = IrradiationFile.from_text(filepath)
        # Keep only useful irradiations
        new_irradiations = []
        for irradiation in irradfile.irr_schedules:
            if irradiation.daughter in daughters:
                new_irradiations.append(irradiation)

        if len(new_irradiations) != len(daughters):
            print(CORANGE+"""
 Warning: irradiations schedules were not find for all specified daughters.
 """+CEND)
            ans = False
        else:
            ans = True

        irradfile.irr_schedules = new_irradiations
        return irradfile, ans


class FNGTest(Test):
    def custom_inp_modifications(self):
        # Add the tracking for daughters in tally 14
        zaids = self.irrad.get_daughters()
        self.inp.add_track_contribution('F14:p', zaids, who='daughter')
        # Add the tracking for daughters in tally 24
        zaids = self.react.get_parents()
        self.inp.add_track_contribution('F24:p', zaids, who='parent')


class MultipleTest:
    def __init__(self, inpsfolder, lib, config, log, VRTpath, confpath,
                 TestOb=Test):
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
        VRTpath : path like object
           path to the variance reduction folder.
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
            test = TestOb(inp, lib, config, log, VRTpath, confpath)
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
            test.generate_test(lib_directory, libmanager, MCNP_dir=mcnp_dir)

    def run(self, cpu=1, timeout=None):
        """
        Run all the tests

        Parameters
        ----------
        cpu : int, optional
            number of CPU to be used. The default is 1.
        timeout : int, optional
            number of seconds after each simulation is killed. The default is
            None.

        Returns
        -------
        None.

        """
        for test in tqdm(self.tests):
            test.run(cpu=cpu, timeout=timeout)


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
        activationlib = lib.split('-')[0]
        transportlib = lib.split('-')[1]
    except IndexError:
        raise ValueError(errmsg)
    # Check that libraries have been correctly defined
    if activationlib+'-'+transportlib != lib:
        raise ValueError(errmsg)

    return activationlib, transportlib
