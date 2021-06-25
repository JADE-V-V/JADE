# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 16:52:09 2019

@author: Davide Laghi

Copyright 2021, the JADE Development Team. All rights reserved.

This file is part of JADE.

JADE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JADE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JADE.  If not, see <http://www.gnu.org/licenses/>.
"""
import inputfile as ipt
import matreader as mat
import os
import subprocess
import shutil
import pandas as pd
import numpy as np

from copy import deepcopy
from tqdm import tqdm


class Test():
    """
    Class representing a general test. This class will have to be extended for
    specific tests.
    """

    def __init__(self, inp, lib, config, log, VRTpath, confpath):
        """
        inp: (str) path to inputfile blueprint
        lib: (str) library suffix to use
        config: (DataFrame row) configuration options for the test
        log: (Log) Jade log file access
        VRTpath: (str/path) path to the variance reduction folder
        confpath: (str/path) path to the test configuration folder
        """
        # Test Library
        self.lib = lib

        # Configuration options for the test
        self.config = config

        # MCNP original input
        self.original_inp = inp

        # Generate input file template
        self.inp = ipt.InputFile.from_text(inp)

        # Name of input file
        self.name = self.inp.name

        # Log for warnings
        self.log = log

        # VRT path
        self.path_VRT = VRTpath

        # Get the configuration files path
        self.test_conf_path = confpath

        # Add the stop card according to config
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

    def _translate_input(self, libmanager):
        """
        Translate the input template to selected library

        Parameters
        ----------
        libmanager : libmanager.LibManager
            Manager dealing with libraries operations.

        Returns
        -------
        None.

        """
        self.inp.translate(self.lib, libmanager)
        self.inp.update_zaidinfo(libmanager)

    def generate_test(self, lib_directory, libmanager, MCNP_dir=None):
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
        self._translate_input(libmanager)

        # Add stop card
        self.inp.add_stopCard(self.nps, self.ctme, self.precision)

        # Identify working directory
        testname = self.inp.name
        if MCNP_dir is None:
            motherdir = os.path.join(lib_directory, testname)
        else:
            motherdir = MCNP_dir
        self.MCNPdir = motherdir
        # If previous results are present they are canceled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        # Get VRT files if available
        directoryVRT = os.path.join(self.path_VRT, testname)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')
        if os.path.exists(directoryVRT):
            # This was tested only for sphere... be careful
            self.inp.add_edits(edits_file)  # Add variance reduction

        # Write new input file
        outinpfile = os.path.join(motherdir, testname)
        self.inp.write(outinpfile)

        # Copy also wwinp file if available
        if os.path.exists(directoryVRT):
            outwwfile = os.path.join(motherdir, 'wwinp')
            shutil.copyfile(ww_file, outwwfile)

    def run(self, cpu=1, timeout=None):
        name = self.name
        directory = self.MCNPdir
        self._run(name, directory, cpu=cpu, timeout=timeout)

    @staticmethod
    def _run(name, directory, cpu=1, timeout=None):
        """
        Run or continue test execution

        Parameters
        ----------
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
        code = 'mcnp6'
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
            subprocess.run([code, command], cwd=directory,
                           creationflags=subprocess.CREATE_NEW_CONSOLE,
                           timeout=timeout)

        except subprocess.TimeoutExpired:
            pass

        return flagnotrun


class MultipleTest:
    def __init__(self, inpsfolder, lib, config, log, VRTpath, confpath):
        """
        This simply a collection of Test objects, see the single Test object,
        for methods and attributes descriptions
        """
        tests = []
        for folder in os.listdir(inpsfolder):
            inp = os.path.join(inpsfolder, folder)
            test = Test(inp, lib, config, log, VRTpath, confpath)
            tests.append(test)
        self.tests = tests
        self.name = os.path.basename(inpsfolder)

    def generate_test(self, lib_directory, libmanager):
        self.MCNPdir = os.path.join(lib_directory, self.name)
        safe_override(self.MCNPdir)
        for test in self.tests:
            mcnp_dir = os.path.join(self.MCNPdir, test.name)
            test.generate_test(lib_directory, libmanager, MCNP_dir=mcnp_dir)

    def run(self, cpu=1, timeout=None):
        for test in tqdm(self.tests):
            test.run(cpu=cpu, timeout=timeout)


class SphereTest(Test):
    """
    Class handling the sphere test
    """

    def generate_test(self, directory, libmanager):
        '''
        Generate all sphere test for a selected library

        libmanager: (LibManager) libraries handler
        directory: (str) path to sphere input folder
        '''
        # Get typical materials input
        dirmat = os.path.dirname(self.original_inp)
        matpath = os.path.join(dirmat, 'TypicalMaterials')
        inpmat = ipt.InputFile.from_text(matpath)
        matlist = inpmat.matlist
        # Get zaids available into the selected library
        zaids = libmanager.get_libzaids(self.lib)

        testname = self.inp.name
        motherdir = os.path.join(directory, testname)
        # If previous results are present they are canceled
        if os.path.exists(motherdir):
            shutil.rmtree(motherdir)
        os.mkdir(motherdir)

        # GET SETTINGS
        # Zaids
        settings = os.path.join(self.test_conf_path, 'ZaidSettings.csv')
        settings = pd.read_csv(settings, sep=';').set_index('Z')
        # Materials
        settings_mat = os.path.join(self.test_conf_path,
                                    'MaterialsSettings.csv')
        settings_mat = pd.read_csv(settings_mat, sep=';').set_index('Symbol')

        self.MCNPdir = motherdir

        print(' Zaids:')
        # for zaid in tqdm(zaids):
        for zaid in tqdm(zaids[:10]):
            Z = int(zaid[:-3])
            # Get Density
            if zaid[-3:] == '235':  # Special treatment for U235
                density = 1
            else:
                density = settings.loc[Z, 'Density [g/cc]']

            if settings.loc[Z, 'Let Override']:
                # get stop parameters
                if self.nps is None:
                    nps = settings.loc[Z, 'NPS cut-off']
                    if nps is np.nan:
                        nps = None
                else:
                    nps = self.nps

                if self.ctme is None:
                    ctme = settings.loc[Z, 'CTME cut-off']
                    if ctme is np.nan:
                        ctme = None
                else:
                    ctme = self.ctme

                if self.precision is None:
                    prec = settings.loc[Z, 'Relative Error cut-off']
                    if prec is np.nan:
                        precision = None
                    else:
                        tally = prec.split('-')[0]
                        error = prec.split('-')[1]
                        precision = (tally, error)
                else:
                    precision = self.precision

            # Zaid local settings are prioritized
            else:
                nps = settings.loc[Z, 'NPS cut-off']
                if nps is np.nan:
                    nps = None

                ctme = settings.loc[Z, 'CTME cut-off']
                if ctme is np.nan:
                    ctme = None

                prec = settings.loc[Z, 'Relative Error cut-off']
                if prec is np.nan:
                    precision = None
                else:
                    tally = prec.split('-')[0]
                    error = prec.split('-')[1]
                    precision = (tally, error)

            self.generate_zaid_test(zaid, libmanager, testname,
                                    motherdir, -1*density, nps, ctme,
                                    precision)

        print(' Materials:')
        # for material in tqdm(matlist.materials):
        for material in tqdm(matlist.materials[:2]):
            # Get density
            density = settings_mat.loc[material.name.upper(), 'Density [g/cc]']

            self.generate_material_test(material, -1*density, libmanager,
                                        testname, motherdir)

    def generate_zaid_test(self, zaid, libmanager, testname, motherdir,
                           density, nps, ctme, precision):
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

        Returns
        -------
        None.

        """
        # Get VRT files
        directoryVRT = os.path.join(self.path_VRT, zaid)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')

        # Adjourn the material cards for the zaid
        zaid = mat.Zaid(1, zaid[:-3], zaid[-3:], self.lib)
        name, formula = libmanager.get_zaidname(zaid)
        submat = mat.SubMaterial('M1', [zaid],
                                 header='C '+name+' '+formula)
        material = mat.Material([zaid], None, 'M1', submaterials=[submat])
        matlist = mat.MatCardsList([material])

        # Generate the new input
        newinp = deepcopy(self.inp)
        newinp.matlist = matlist  # Assign material
        # adjourn density
        newinp.change_density(density)
        # assign stop card
        newinp.add_stopCard(nps, ctme, precision)

        if os.path.exists(directoryVRT):
            newinp.add_edits(edits_file)  # Add variance reduction

        # Write new input file
        outfile = testname+'_'+zaid.element+zaid.isotope+'_'+formula+'_'
        outdir = testname+'_'+zaid.element+zaid.isotope+'_'+formula
        outpath = os.path.join(motherdir, outdir)
        os.mkdir(outpath)
        outinpfile = os.path.join(outpath, outfile)
        newinp.write(outinpfile)

        # Copy also wwinp file
        if os.path.exists(directoryVRT):
            outwwfile = os.path.join(outpath, 'wwinp')
            shutil.copyfile(ww_file, outwwfile)

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
        truename = material.name
        # Get VRT file
        directoryVRT = os.path.join(self.path_VRT, truename)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')

        # Translate and assign the material
        material.translate(self.lib, libmanager)
        material.header = material.header+'C\nC True name:'+truename
        material.name = 'M1'
        matlist = mat.MatCardsList([material])

        # Generate the new input
        newinp = deepcopy(self.inp)
        newinp.matlist = matlist  # Assign material
        # adjourn density
        newinp.change_density(density)
        # add stop card
        newinp.add_stopCard(self.nps, self.ctme, self.precision)

        if os.path.exists(directoryVRT):
            newinp.add_edits(edits_file)  # Add variance reduction

        # Write new input file
        outfile = testname+'_'+truename+'_'
        outdir = testname+'_'+truename
        outpath = os.path.join(motherdir, outdir)
        os.mkdir(outpath)
        outinpfile = os.path.join(outpath, outfile)
        newinp.write(outinpfile)

        # Copy also wwinp file
        if os.path.exists(directoryVRT):
            outwwfile = os.path.join(outpath, 'wwinp')
            shutil.copyfile(ww_file, outwwfile)

    def run(self, cpu=1, timeout=None):
        """
        Sphere test needs an ad-hoc run method to run all zaids tests
        """
        flagnotrun = False
        for folder in tqdm(os.listdir(self.MCNPdir)):
            path = os.path.join(self.MCNPdir, folder)
            name = folder+'_'
            code = 'mcnp6'
            command = 'name='+name+' wwinp=wwinp tasks '+str(cpu)
            try:
                subprocess.run([code, command], cwd=path,
                               creationflags=subprocess.CREATE_NEW_CONSOLE,
                               timeout=timeout)

            except subprocess.TimeoutExpired:
                flagnotrun = True
                self.log.adjourn(name+' reached timeout, eliminate folder')
                continue

        if flagnotrun:
            print("""
 Some MCNP run reached timeout, they are listed in the log file.
 Please remove their folders before attempting to postprocess the library""")


def safe_mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def safe_override(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


def check_true(obj):
    # It may not work! check needed
    if obj is True:
        return True
    elif obj == 'True':
        return True
    elif obj == 'true':
        return True
    else:
        return False
