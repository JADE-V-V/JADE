# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 17:18:07 2020

@author: Davide Laghi
"""
import pandas as pd
import MCTAL_READER as mctal
import numpy as np
import math
import os
import atlas as at
import shutil

from output import BenchmarkOutput
from output import MCNPoutput
from tqdm import tqdm
from status import EXP_TAG
from plotter import Plotter


class ExperimentalOutput(BenchmarkOutput):
    def __init__(self, lib, testname, session):
        super().__init__(lib, testname, session)
        # The experimental data needs to be loaded
        self.path_exp_res = os.path.join(session.path_exp_res, testname)

        # Add the raw path data (not created because it is a comparison)
        out = os.path.dirname(self.atlas_path)
        raw_path = os.path.join(out, 'Raw Data')
        os.mkdir(raw_path)
        self.raw_path = raw_path

    def single_postprocess(self):
        raise AttributeError('No single pp is foreseen for exp benchmark')

    def compare(self):
        # Shall be implemented in the specific output
        pass


class OktavianOutput(ExperimentalOutput):
    def compare(self):
        self._extract_outputs()
        self._print_raw()
        # # print(' Generating Excel Recap...')
        # # self.pp_excel_comparison()

        print(' Creating Atlas...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)

        globalname = ''
        for lib in self.lib:
            globalname = globalname + lib + '_Vs_'
        globalname = globalname[:-4]

        # Initialize the atlas
        template = os.path.join(self.code_path, 'Templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, globalname)
        
        maintitle = ' Oktavian Experiment: '
        unit = '#/Lethargy'
        xlabel = 'Energy [MeV]'

        # Tally numbers should be fixed
        for tallynum in ['21', '41']:
            if tallynum == '21':
                print(' Printing the Neutron Letharghy flux...')
                tit_tag = 'Neutron Flux per Unit Lethargy'
                quantity = 'Neutron Flux'
            else:
                print(' Printing the Photon Letharghy flux...')
                tit_tag = 'Photon Flux per Unit Lethargy'
                quantity = 'Photon Flux'
            
            atlas.doc.add_heading(quantity, level=1)

            for material in tqdm(self.materials, desc='Materials: '):

                atlas.doc.add_heading('Material: '+material, level=2)

                title = material+maintitle+tit_tag

                # Get the experimental data
                file = 'oktavian_'+material+'_tal'+tallynum+'.exp'
                filepath = os.path.join(self.path_exp_res, material, file)
                if os.path.isfile(filepath):
                    x, y, err = self._read_Oktavian_expresult(filepath)
                else:
                    # Skip the tally if no experimental data is available
                    continue
                lib = {'x': x, 'y': y, 'err': [],
                       'ylabel': material +' (Experiment)'}

                # Collect the data to be plotted
                data = [lib]  #  The first one should be the exp one
                for lib_tag in self.lib[1:]:  # Avoid exp
                    lib_name = self.session.conf.get_lib_name(lib_tag)
                    try:  # The tally may not be defined
                        values = self.results[material, lib_tag][tallynum]
                        lib = {'x': values['Energy [MeV]'],
                               'y': values['Lethargy'], 'err': [],
                               'ylabel': material +' ('+lib_name+')'}
                        data.append(lib)
                    except KeyError:
                        # The tally is not defined
                        pass

                # Once the data is collected it is passed to the plotter
                outname = material+'-'+globalname+'-'+tallynum
                plot = Plotter(data, title, outpath, outname, quantity, unit,
                               xlabel, self.testname)
                img_path = plot.plot('Experimental points')
                # Insert the image in the atlas
                atlas.insert_img(img_path)

        # Save Atlas
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

    def _extract_outputs(self):
        # Get results
        # results = []
        # errors = []
        # stat_checks = []
        outputs = {}
        results = {}
        materials = []
        # Iterate on the different libraries results except 'Exp'
        for lib, test_path in self.test_path.items():
            if lib != EXP_TAG:                
                for folder in os.listdir(test_path):
                    results_path = os.path.join(test_path, folder)
                    pieces = folder.split('_')
                    # Get zaid
                    material = pieces[-1]
        
                    # Get mfile
                    for file in os.listdir(results_path):
                        if file[-1] == 'm':
                            mfile = file
                        elif file[-1] == 'o':
                            ofile = file
                    # Parse output
                    output = MCNPoutput(os.path.join(results_path, mfile),
                                        os.path.join(results_path, ofile))
                    outputs[material, lib] = output
                    # Adjourn raw Data
                    self.raw_data[material, lib] = output.tallydata
                    # Get the meaningful results
                    results[material, lib] = self._processMCNPdata(output.mctal)
                    if material not in materials:
                        materials.append(material)
                
        self.outputs = outputs
        self.results = results
        self.materials = materials

    def _print_raw(self):
        # Generate a folder for each library
        for lib_name in self.lib[1:]:  # Avoid Exp
            cd_lib = os.path.join(self.raw_path, lib_name)
            os.mkdir(cd_lib)
            # result for each material
            for material in self.materials:
                for key, data in self.raw_data[material, lib_name].items():
                    file = os.path.join(cd_lib, material+' '+str(key)+'.csv')
                    data.to_csv(file, header=True, index=False)
            

    # def pp_excel_comparison():
    #     pass

    @staticmethod
    def _processMCNPdata(mtal):
        """
        given the mctal file the lethargy flux and energies are returned
        both for the neutron and photon tally

        Parameters
        ----------
        mtal : mctal.MCTAL
            mctal object file containing the results.

        Returns
        -------
        res : dic
            contains the extracted lethargy flux and energies.

        """
        res = {}
        # Read tally energy binned fluxes
        for tally in mtal.tallies:
            res2 = res[str(tally.tallyNumber)] = {}

            energies = tally.erg
            flux = []
            for i, t in enumerate(energies):
                val = tally.getValue(0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0, 0)
                flux.append(val)

            # Energies for lethargy computation
            ergs = [1e-10]  # Addtional "zero" energy for lethargy computation
            ergs.extend(energies.tolist())
            ergs = np.array(ergs)

            flux = flux/np.log((ergs[1:]/ergs[:-1]))
            res2['Energy [MeV]'] = energies
            res2['Lethargy'] = flux

        return res
    
    @staticmethod
    def _read_Oktavian_expresult(file):
        """
        Given a file containing the Oktavian experimental results read it and
        return the values to plot.
    
        The values equal to 1e-38 are eliminated since it appears that they
        are the zero values of the instrument used.

        Parameters
        ----------
        file : os.Path or str
            path to the file to be read.

        Returns
        -------
        x : np.array
            energy values.
        y : np.array
            lethargy flux values.

        """
        columns =  ['Upper Energy [MeV]', 'Nominal Energy [MeV]',
                    'Lower Energy [MeV]', 'Lethargy Flux', 'Error']
        # First of all understand how many comment lines there are
        with open(file, 'r') as infile:
            counter = 0
            for line in infile:
                if line[0] == '#':
                    counter += 1
                else:
                    break
        # then read the file accordingly
        df = pd.read_csv(file, skiprows=counter, skipfooter=1, engine='python',
                         header=None, sep='\s+')
        df.columns = columns
        
        df = df[df['Lethargy Flux'] > 2e-38]

        x = df['Nominal Energy [MeV]'].values
        y = df['Lethargy Flux'].values
        err = df['Error'].values

        return x, y, err