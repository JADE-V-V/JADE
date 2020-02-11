# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 10:36:38 2020

@author: Davide Laghi
"""

import MCTAL_READER as mtal
import xlwings as xw
import excel_support as exsupp
import pandas as pd
import os
import shutil
import plotter
from tqdm import tqdm
import atlas as at
import numpy as np


class BenchmarkOutput:

    def __init__(self, lib, testname):
        """
        General class for a Benchmark output

        Parameters
        ----------
        lib : str
            library to post-process
        testname : str
            Name of the benchmark

        Returns
        -------
        None.

        """
        self.raw_data = {}  # Raw data
        self.testname = testname  # test name
        test_path = r'Tests\01_MCNP_Run'  # path to runned tests
        cp = os.path.dirname(os.getcwd())
        self.code_path = os.path.join(cp, 'Code')

        # COMPARISON
        if type(lib) == list and len(lib) > 1:
            self.single = False  # Indicator for single or comparison
            self.lib = lib
            couples = []
            tp = os.path.join(cp, test_path, lib[0], testname)
            self.test_path = {lib[0]: tp}
            output_path = r'Tests\02_Output\Comparisons'
            for library in lib[1:]:
                name = library+'_Vs_'+lib[0]
                couples.append((lib[0], library, name))
                tp = os.path.join(cp, test_path, library, testname)
                self.test_path[library] = tp

                # Generate library output path
                out = os.path.join(cp, output_path, name)
                if not os.path.exists(out):
                    os.mkdir(out)

                out = os.path.join(out, testname)
                if os.path.exists(out):
                    shutil.rmtree(out)
                os.mkdir(out)
                excel_path = os.path.join(out, 'Excel')
                atlas_path = os.path.join(out, 'Atlas')
                # raw_path = os.path.join(out, 'Raw Data')
                os.mkdir(excel_path)
                os.mkdir(atlas_path)
                # os.mkdir(raw_path)
                self.excel_path = excel_path
                # self.raw_path = raw_path
                self.atlas_path = atlas_path

            self.couples = couples  # Couples of libraries to post process

        # SINGLE-LIBRARY
        else:
            self.single = True  # Indicator for single or comparison
            self.lib = str(lib)  # In case of 1-item list
            self.test_path = os.path.join(cp, test_path, lib, testname)
            output_path = r'Tests\02_Output\Single Libraries'

            # Generate library output path
            out = os.path.join(cp, output_path, lib)
            if not os.path.exists(out):
                os.mkdir(out)

            out = os.path.join(out, testname)
            if os.path.exists(out):
                shutil.rmtree(out)
            os.mkdir(out)
            excel_path = os.path.join(out, 'Excel')
            atlas_path = os.path.join(out, 'Atlas')
            raw_path = os.path.join(out, 'Raw Data')
            os.mkdir(excel_path)
            os.mkdir(atlas_path)
            os.mkdir(raw_path)
            self.excel_path = excel_path
            self.raw_path = raw_path
            self.atlas_path = atlas_path


class SphereOutput(BenchmarkOutput):

    def single_postprocess(self):
        """
        Execute the full post-processing of a single library (i.e. excel,
        raw data and atlas)

        Returns
        -------
        None.

        """
        print(' Generating Excel Recap...')
        self.pp_excel_single()
        self.print_raw()
        print(' Creating Atlas...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)

        for tally, title, ylabel in \
            [(2, 'Leakage Neutron Flux (175 groups)', 'Neutron Flux'),
             (32, 'Leakage Gamma Flux (24 groups)', 'Gamma Flux')]:

            print(' Plotting tally n.'+str(tally))
            for zaidnum, output in tqdm(self.outputs.items()):
                title = title
                tally_data = output.mdata.set_index('Tally N.').loc[tally]
                energy = tally_data['Energy'].values
                values = tally_data['Value'].values
                error = tally_data['Error'].values
                lib = {'x': energy, 'y': values, 'err': error,
                       'ylabel': str(zaidnum)+'.'+self.lib}
                data = [lib]
                outname = str(zaidnum)+'-'+self.lib+'-'+str(tally)
                plot = plotter.Plotter(data, title, outpath, outname)
                plot.binned_plot(ylabel)

        print(' Generating Plots Atlas...')
        # Printing Atlas
        template = os.path.join(self.code_path, 'Templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, self.lib)
        atlas.build(outpath)
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

        print(' Single library post-processing completed')

    def compare(self, state):
        print(' Generating Excel Recap...')
        self.pp_excel_comparison(state)
        print(' Creating Atlas...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)

        libraries = []
        outputs = []
        for libname, outputslib in self.outputs.items():
            libraries.append(libname)
            outputs.append(outputslib)

        globalname = ''
        for lib in libraries:
            globalname = globalname + lib + '_Vs_'

        globalname = globalname[:-4]
        print(globalname)

        for tally, title, ylabel in \
            [(2, 'Leakage Neutron Flux (175 groups)', 'Neutron Flux'),
             (32, 'Leakage Gamma Flux (24 groups)', 'Gamma Flux')]:

            print(' Plotting tally n.'+str(tally))
            for zaidnum, outputdummy in tqdm(outputs[0].items()):
                title = title
                data = []
                for idx, output in enumerate(outputs):
                    tally_data = output[zaidnum].mdata.set_index('Tally N.').loc[tally]
                    energy = tally_data['Energy'].values
                    values = tally_data['Value'].values
                    error = tally_data['Error'].values
                    lib = {'x': energy, 'y': values, 'err': error,
                           'ylabel': str(zaidnum)+'.'+libraries[idx]}
                    data.append(lib)

                outname = str(zaidnum)+'-'+globalname+'-'+str(tally)
                plot = plotter.Plotter(data, title, outpath, outname)
                plot.binned_plot(ylabel)

        print(' Generating Plots Atlas...')
        # Printing Atlas
        template = os.path.join(self.code_path, 'Templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, globalname)
        atlas.build(outpath)
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

        # print(' Single library post-processing completed')

    def pp_excel_single(self):
        """
        Generate the single library results excel

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'Templates', 'Sphere_single.xlsx')
        outpath = os.path.join(self.excel_path, 'Sphere_single_' +
                               self.lib+'.xlsx')
        # Get results
        results = []
        errors = []
        outputs = {}
        for folder in os.listdir(self.test_path):
            results_path = os.path.join(self.test_path, folder)
            pieces = folder.split('_')
            # Get zaid
            zaidnum = pieces[-2]
            zaidname = pieces[-1]
            # Get mfile
            for file in os.listdir(results_path):
                if file[-1] == 'm':
                    mfile = file
            # Parse output
            output = MCNPoutput(os.path.join(results_path, mfile))
            outputs[zaidnum] = output
            # Adjourn raw Data
            self.raw_data[zaidnum] = output.mdata

            res, err = output.get_single_excel_data()
            for dic in [res, err]:
                dic['Zaid'] = zaidnum
                dic['Zaid Name'] = zaidname
            results.append(res)
            errors.append(err)
        # Generate DataFrames
        results = pd.DataFrame(results)
        errors = pd.DataFrame(errors)
        # Swap Columns
        res_cols = list(results.columns)
        nres_cols = [res_cols[-2], res_cols[-1]] + res_cols
        err_cols = list(errors.columns)
        nerr_cols = [err_cols[-2], err_cols[-1]] + err_cols
        del nres_cols[-2:], nerr_cols[-2:]
        results = results[nres_cols]
        errors = errors[nerr_cols]

        self.outputs = outputs
        self.results = results
        self.errors = errors
        # Write excel
        ex = ExcelOutputSheet(template, outpath)
        # Results
        ex.insert_df(9, 2, results, 0)
        ex.insert_df(9, 2, errors, 1)
        ex.wb.sheets[0].range('D1').value = self.lib
        ex.save()

    def pp_excel_comparison(self, state):
        template = os.path.join(os.getcwd(), 'Templates',
                                'Sphere_comparison.xlsx')

        outputs = {}
        iteration = 0
        for reflib, tarlib, name in self.couples:
            outpath = os.path.join(self.excel_path, 'Sphere_comparison_' +
                                   name+'.xlsx')
            # Get results
            dfs = []
            iteration = iteration+1

            for test_path in [self.test_path[reflib], self.test_path[tarlib]]:
                results = []

                outputs_lib = {}
                for folder in os.listdir(test_path):
                    results_path = os.path.join(test_path, folder)
                    pieces = folder.split('_')
                    # Get zaid
                    zaidnum = pieces[-2]
                    zaidname = pieces[-1]
                    # Get mfile
                    for file in os.listdir(results_path):
                        if file[-1] == 'm':
                            mfile = file

                    # Parse output
                    output = MCNPoutput(os.path.join(results_path, mfile))
                    outputs_lib[zaidnum] = output

                    res, columns = output.get_comparison_data()
                    res.append(int(zaidnum))
                    res.append(zaidname)

                    results.append(res)

                # Add reference library outputs
                if iteration == 1:
                    outputs[reflib] = outputs_lib

                if test_path == self.test_path[tarlib]:
                    outputs[tarlib] = outputs_lib

                # Generate DataFrames
                columns.extend(['Zaid', 'Zaid Name'])
                df = pd.DataFrame(results, columns=columns)
                df.set_index(['Zaid', 'Zaid Name'], inplace=True)
                dfs.append(df)

                # outputs_couple = outputs
                # self.results = results

            self.outputs = outputs
            # Consider only common zaids
            idx1 = dfs[0].index
            idx2 = dfs[1].index
            newidx = idx1.intersection(idx2)

            # Build the final excel data
            final = (dfs[0].loc[newidx]-dfs[1].loc[newidx])/dfs[0].loc[newidx]
            # If it is zero the CS are equal! (NaN if both zeros)
            final[final == np.nan] = 'Not Available'
            final[final == 0] = 'Identical'

            final.sort_index(level=0, inplace=True)

            # Write excel
            ex = ExcelOutputSheet(template, outpath)
            # Results
            rangeex = ex.wb.sheets[0].range('B10')
            rangeex.options(index=True, header=True).value = final
            ex.wb.sheets[0].range('D1').value = name

            # Add single pp sheets
            for lib in [reflib, tarlib]:
                cp = state.get_path('single', [lib, 'Sphere', 'Excel'])
                file = os.listdir(cp)[0]
                cp = os.path.join(cp, file)
                ex.copy_sheets(cp)

            ex.save()

    def print_raw(self):
        for key, data in self.raw_data.items():
            file = os.path.join(self.raw_path, key+'.csv')
            data.to_csv(file, header=True, index=False)


class MCNPoutput:
    def __init__(self, mctal_file):
        """
        Class handling an MCNP run Output

        mctal_file: (str/path) path to the mctal file
        """
        self.mctal_file = mctal_file  # path to mctal file

        # Read and parse the mctal file
        mctal = mtal.MCTAL(mctal_file)
        mctal.Read()
        self.mctal = mctal
        self.mdata = self.organize_mctal()

    def organize_mctal(self):
        """
        Retrieve and organize mctal data. Simplified for sphere leakage case

        Returns: DataFrame containing the organized data
        """
        # Extract data
        rows = []
        for t in self.mctal.tallies:
            num = t.tallyNumber
            des = t.tallyComment[0]
            nCells = t.getNbins("f", False)
            nCora = t.getNbins("i", False)
            nCorb = t.getNbins("j", False)
            nCorc = t.getNbins("k", False)
            nDir = t.getNbins("d", False)
            # usrAxis = t.getAxis("u")
            nUsr = t.getNbins("u", False)
            # segAxis = t.getAxis("s")
            nSeg = t.getNbins("s", False)
            nMul = t.getNbins("m", False)
            # cosAxis = t.getAxis("c")
            nCos = t.getNbins("c", False)
            # ergAxis = t.getAxis("e")
            nErg = t.getNbins("e", False)
            # timAxis = t.getAxis("t")
            nTim = t.getNbins("t", False)

            for f in range(nCells):
                for d in range(nDir):
                    for u in range(nUsr):
                        for s in range(nSeg):
                            for m in range(nMul):
                                for c in range(nCos):
                                    for e in range(nErg):
                                        try:
                                            erg = t.erg[e]
                                        except IndexError:
                                            erg = None

                                        for nt in range(nTim):
                                            for k in range(nCorc):
                                                for j in range(nCorb):
                                                    for i in range(nCora):
                                                        val = t.getValue(f, d,
                                                                         u, s,
                                                                         m, c,
                                                                         e, nt,
                                                                         i, j,
                                                                         k, 0)
                                                        err = t.getValue(f, d,
                                                                         u, s,
                                                                         m, c,
                                                                         e, nt,
                                                                         i, j,
                                                                         k, 1)

                                                        row = [num, des,
                                                               erg,
                                                               val, err]
                                                        rows.append(row)

        df = pd.DataFrame(rows, columns=['Tally N.', 'Tally Description',
                                         'Energy', 'Value', 'Error'])
        return df

    def get_single_excel_data(self):
        """
        Get the excel data of a single MCNP output

        Returns
        -------
        results : dic
            Excel result for different tallies
        errors : dic
            Error average in all tallies

        """
        # Tallies to post process
        tallies2pp = ['2', '32', '24', '14', '34']
        heating_tallies = ['4', '6', '44', '46']
        data = self.mdata.set_index(['Tally Description', 'Energy'])
        results = {}  # Store excel results of different tallies
        errors = {}  # Store average error in different tallies
        keys = {}  # Tally names and numbers
        heating_res = {}  # Mid-process heating results
        notes = 'Negative Bins:'  # Record negative bins here
        initial_notes_length = len(notes)  # To check if notes are registered
        for tally in self.mctal.tallies:
            num = str(tally.tallyNumber)
            keys[num] = tally.tallyComment[0]
            # Isolate tally
            masked = data.loc[tally.tallyComment[0]]
            # Get mean error among bins
            mean_error = masked['Error'].mean()
            if num in tallies2pp:
                masked_zero = masked[masked['Value'] == 0]
                original_length = len(masked)
                masked = masked[masked['Value'] < 0]
                if len(masked) > 0:
                    res = 'Value < 0 in '+str(len(masked))+' bin(s)'
                    # Get energy bins
                    bins = list(masked.reset_index()['Energy'].values)
                    notes = notes+'\n('+str(num)+'): '
                    for ebin in bins:
                        notes = notes+str(ebin)+', '
                    notes = notes[:-2]  # Clear string from excess commas

                elif len(masked_zero) == original_length:
                    res = 'Value = 0 for all bins'
                else:
                    res = 'Value > 0 for all bins'

                results[tally.tallyComment[0]] = res
                errors[tally.tallyComment[0]] = mean_error

            elif num in heating_tallies:
                heating_res[num] = float(masked['Value'].values[0])
                errors[tally.tallyComment[0]] = mean_error

        comp = 'Heating comparison [F4 vs F6]'
        try:
            results['Neutron '+comp] = ((heating_res['6'] - heating_res['4']) /
                                        heating_res['6'])
        except ZeroDivisionError:
            results['Neutron '+comp] = 0

        try:
            results['Gamma '+comp] = ((heating_res['46'] - heating_res['44']) /
                                      heating_res['46'])
        except ZeroDivisionError:
            results['Gamma '+comp] = 0

        # Notes adding
        if len(notes) > initial_notes_length:
            results['Notes'] = notes
        else:
            results['Notes'] = ''

        return results, errors

    def get_comparison_data(self):
        """
        Get Data for single zaid to be used in comparison.

        Returns
        -------
        results : list
            All results per tally to compare
        columns : list
            Tally names

        """
        # Tallies to post process
        tallies2pp = ['12', '22', '24', '14', '34', '6', '46']
        data = self.mdata.set_index(['Tally Description', 'Energy'])
        results = []  # Store data to compare for different tallies
        columns = []  # Tally names and numbers
        # Reorder tallies
        tallies = []
        for tallynum in tallies2pp:
            for tally in self.mctal.tallies:
                num = str(tally.tallyNumber)
                if num == tallynum:
                    tallies.append(tally)

        for tally in tallies:
            num = str(tally.tallyNumber)
            # Isolate tally

            masked = data.loc[tally.tallyComment[0]]
            if num in tallies2pp:
                if num in ['12', '22']:  # Coarse Flux bins
                    # Get energy bins
                    bins = list(masked.reset_index()['Energy'].values)
                    for ebin in bins:
                        colname = '(T.ly '+str(num)+') '+str(ebin)
                        columns.append(colname)
                        results.append(masked['Value'].loc[ebin])
                else:
                    columns.append(tally.tallyComment[0])
                    results.append(masked['Value'].values[0])

        return results, columns


class ExcelOutputSheet:
    def __init__(self, template, outpath):
        """
        Excel sheet reporting the outcome of an MCNP test

        template: (str/path) path to the sheet template
        """
        self.outpath = outpath  # Path to the excel file
        # Open template
        shutil.copy(template, outpath)
        self.app = xw.App(visible=False)
        self.wb = self.app.books.open(outpath)

    def insert_df(self, startrow, startcolumn, df, ws):
        '''
        Insert a DataFrame (df) into a Worksheet (ws) using openpyxl.
        (startrow) and (startcolumn) identify the starting data entry
        '''
        ws = self.wb.sheets[ws]
        exsupp.insert_df(startrow, startcolumn, df, ws)

    def copy_sheets(self, wb_origin_path):
        """
        Copy all sheets of the selected excel file into the current one

        Parameters
        ----------
        wb_origin_path : str/path
            Path to excel file containing sheets to add.

        Returns
        -------
        None.

        """
        wb = self.app.books.open(wb_origin_path)
        for sheet in wb.sheets:

            # copy to a new workbook
            sheet.api.Copy()

            # copy to an existing workbook by putting it in front of a
            # worksheet object
            sheet.api.Copy(Before=self.wb.sheets[0].api)

    def save(self):
        """
        Save Excel
        """
        self.app.calculate()
        self.wb.save()
        self.wb.close()
        self.app.quit()
