# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 16:52:09 2019

@author: Davide Laghi
"""
import inputfile as ipt
import matreader as mat
import os
import subprocess
import shutil

from copy import deepcopy
from tqdm import tqdm


class Test():
    """
    Class representing a general test. This class will have to be extended for
    specific tests.
    """

    def __init__(self, inp, lib, config, log, VRTpath):
        """
        inp: (str) path to inputfile blueprint
        lib: (str) library suffix to use
        config: (DataFrame row) configuration options for the test
        log: (Log) Jade log file access
        VRTpath: (str/path) path to the variance reduction folder
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

        # Add the stop card according to config
        config = config.dropna()
        try:
            nps = config['NPS cut-off']
        except KeyError:
            nps = None
        try:
            ctme = config['CTME cut-off']
        except KeyError:
            ctme = None
        try:
            tally = config['Relative Error cut-off'].split('-')[0]
            error = config['Relative Error cut-off'].split('-')[1]
            precision = (tally, error)
        except KeyError:
            precision = None
        self.inp.add_stopCard(nps, ctme, precision)

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
        self.inp = self.inp.translate(self.lib, libmanager)

    def generate_test(self, lib_directory, libmanager):
        """
        Generate the test input files

        Parameters
        ----------
        lib_directory : path or string
            Path to lib benchmarks input folders.

        libmanager : libmanager.LibManager
            Manager dealing with libraries operations.

        Returns
        -------
        None.

        """

        self._translate_input(libmanager)  # Translate the input

        # Identify working directory
        testname = self.inp.name
        motherdir = os.path.join(lib_directory, testname)
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


class SphereTest(Test):
    """
    Class handling the sphere test
    """

    def generate_test(self, libmanager, directory):
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

        self.MCNPdir = motherdir

        print(' Zaids:')
        for zaid in tqdm(zaids[:10]):
            # for zaid in tqdm(zaids):
            self.generate_zaid_test(zaid, libmanager, testname,
                                    motherdir)

        print(' Materials:')
        for material in tqdm(matlist.materials[:2]):
            # for material in tqdm(matlist.materials):
            self.generate_material_test(material, libmanager, testname,
                                        motherdir)

    def generate_zaid_test(self, zaid, libmanager, testname, motherdir):
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

        Returns
        -------
        None.

        """
        # Get VRT files
        directoryVRT = os.path.join(self.path_VRT, zaid)
        edits_file = os.path.join(directoryVRT, 'inp_edits.txt')
        ww_file = os.path.join(directoryVRT, 'wwinp')

        # Adjourn the material cars for the zaid
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
        newinp.change_density(zaid)

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

    def generate_material_test(self, material, libmanager, testname,
                               motherdir):
        """
        Generate a sphere leakage benchmark input for a single typical
        material.

        Parameters
        ----------
        material : str
            Name of the material (e.g. m101).
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
        # # adjourn density
        # newinp.change_density(zaid)

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
