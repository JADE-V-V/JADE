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

from output import BenchmarkOutput
from output import MCNPoutput


class ExperimentalOutput(BenchmarkOutput):
    def __init__(self, lib, testname, session):
        # Act on lib to ensure a comparison is always triggered
        if type(lib) == list:
            newlib = ['Exp']
            newlib.extend(lib)
        else:
            newlib = ['Exp', lib]
        super().__init__(newlib, testname, session)
        # The experimental data needs to be loaded
        self.path_exp_res = os.path.join(session.path_exp_res, testname)

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

        # print(' Creating Atlas...')
        # outpath = os.path.join(self.atlas_path, 'tmp')
        # os.mkdir(outpath)

        # libraries = []
        # outputs = []
        # materials = []
        # for libname, outputslib in self.outputs.items():
        #     libraries.append(libname)
        #     outputs.append(outputslib)
        #     materials.append(list(outputslib.keys()))

        # # Extend list to all zaids
        # allzaids = zaids[0]
        # for zaidlist in zaids[1:]:
        #     allzaids.extend(zaidlist)
        # allzaids = set(allzaids)  # no duplicates

        # globalname = ''
        # for lib in libraries:
        #     globalname = globalname + lib + '_Vs_'

        # globalname = globalname[:-4]

        # for tally, title, quantity, unit in \
        #     [(2, 'Leakage Neutron Flux (175 groups)',
        #       'Neutron Flux', '$\#/cm^2$'),
        #      (32, 'Leakage Gamma Flux (24 groups)',
        #       'Gamma Flux', '$\#/cm^2$')]:

        #     print(' Plotting tally n.'+str(tally))
        #     for zaidnum in tqdm(allzaids):
        #         # title = title
        #         data = []
        #         for idx, output in enumerate(outputs):
        #             try:  # Zaid could not be common to the libraries
        #                 tally_data = output[zaidnum].tallydata.set_index('Tally N.').loc[tally]
        #                 energy = tally_data['Energy'].values
        #                 values = tally_data['Value'].values
        #                 error = tally_data['Error'].values
        #                 lib_name = self.session.conf.get_lib_name(libraries[idx])
        #                 lib = {'x': energy, 'y': values, 'err': error,
        #                        'ylabel': str(zaidnum)+' ('+lib_name+')'}
        #                 data.append(lib)
        #             except KeyError:
        #                 # It is ok, simply nothing to plot here
        #                 pass

        #         outname = str(zaidnum)+'-'+globalname+'-'+str(tally)
        #         plot = plotter.Plotter(data, title, outpath, outname, quantity,
        #                                unit, 'Energy [MeV]', self.testname)
        #         plot.plot('Binned graph')

        # print(' Generating Plots Atlas...')
        # # Printing Atlas
        # template = os.path.join(self.code_path, 'Templates',
        #                         'AtlasTemplate.docx')
        # atlas = at.Atlas(template, globalname)
        # atlas.build(outpath, self.session.lib_manager)
        # atlas.save(self.atlas_path)
        # # Remove tmp images
        # shutil.rmtree(outpath)

    def _extract_outputs(self):
        # Get results
        results = []
        errors = []
        stat_checks = []
        outputs = {}
        results = {}
        for folder in os.listdir(self.test_path):
            results_path = os.path.join(self.test_path, folder)
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
            outputs[material] = output
            # Adjourn raw Data
            self.raw_data[material] = output.tallydata
            # Get the meaningful results
            result[material] = self._processMCNPdata(output.mctal)
        
        self.outputs = outputs
        self.results = results

    def _print_raw(self):
        for key, data in self.raw_data.items():
            file = os.path.join(self.raw_path, key+'.csv')
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
