# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 10:36:38 2020

@author: Davide Laghi
"""

import xlwings as xw
import excel_support as exsupp
import pandas as pd
import os
import shutil
import plotter
from tqdm import tqdm
import atlas as at
import numpy as np
from output import BenchmarkOutput
from output import MCNPoutput


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
            [(2, 'Leakage Neutron Flux (175 groups)',
              'Neutron Flux $[\#/cm^2]$'),
             (32, 'Leakage Gamma Flux (24 groups)',
              'Gamma Flux $[\#/cm^2]$')]:

            print(' Plotting tally n.'+str(tally))
            for zaidnum, output in tqdm(self.outputs.items()):
                title = title
                tally_data = output.tallydata.set_index('Tally N.').loc[tally]
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
        atlas.build(outpath, self.session.lib_manager)
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

        print(' Single library post-processing completed')

    def compare(self):
        print(' Generating Excel Recap...')
        self.pp_excel_comparison(self.session.state)
        print(' Creating Atlas...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)

        libraries = []
        outputs = []
        zaids = []
        for libname, outputslib in self.outputs.items():
            libraries.append(libname)
            outputs.append(outputslib)
            zaids.append(list(outputslib.keys()))

        # Extend list to all zaids
        allzaids = zaids[0]
        for zaidlist in zaids[1:]:
            allzaids.extend(zaidlist)
        allzaids = set(allzaids)  # no duplicates

        globalname = ''
        for lib in libraries:
            globalname = globalname + lib + '_Vs_'

        globalname = globalname[:-4]

        for tally, title, ylabel in \
            [(2, 'Leakage Neutron Flux (175 groups)',
              'Neutron Flux $[\#/cm^2]$'),
             (32, 'Leakage Gamma Flux (24 groups)',
              'Gamma Flux $[\#/cm^2]$')]:

            print(' Plotting tally n.'+str(tally))
            for zaidnum in tqdm(allzaids):
                # title = title
                data = []
                for idx, output in enumerate(outputs):
                    try:  # Zaid could not be common to the libraries
                        tally_data = output[zaidnum].tallydata.set_index('Tally N.').loc[tally]
                        energy = tally_data['Energy'].values
                        values = tally_data['Value'].values
                        error = tally_data['Error'].values
                        lib = {'x': energy, 'y': values, 'err': error,
                               'ylabel': str(zaidnum)+'.'+libraries[idx]}
                        data.append(lib)
                    except KeyError:
                        # It is ok, simply nothing to plot here
                        pass

                outname = str(zaidnum)+'-'+globalname+'-'+str(tally)
                plot = plotter.Plotter(data, title, outpath, outname)
                plot.binned_plot(ylabel)

        print(' Generating Plots Atlas...')
        # Printing Atlas
        template = os.path.join(self.code_path, 'Templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, globalname)
        atlas.build(outpath, self.session.libmanager)
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
        stat_checks = []
        outputs = {}
        for folder in os.listdir(self.test_path):
            results_path = os.path.join(self.test_path, folder)
            pieces = folder.split('_')
            # Get zaid
            zaidnum = pieces[-2]
            # Check for material exception
            if zaidnum == 'Sphere':
                zaidnum = pieces[-1]
                zaidname = 'Typical Material'
            else:
                zaidname = pieces[-1]
            # Get mfile
            for file in os.listdir(results_path):
                if file[-1] == 'm':
                    mfile = file
                elif file[-1] == 'o':
                    ofile = file
            # Parse output
            output = SphereMCNPoutput(os.path.join(results_path, mfile),
                                      os.path.join(results_path, ofile))
            outputs[zaidnum] = output
            # Adjourn raw Data
            self.raw_data[zaidnum] = output.tallydata
            # Recover statistical checks
            st_ck = output.stat_checks
            # Recover results and precisions
            res, err = output.get_single_excel_data()
            for dic in [res, err, st_ck]:
                dic['Zaid'] = zaidnum
                dic['Zaid Name'] = zaidname
            results.append(res)
            errors.append(err)
            stat_checks.append(st_ck)

        # Generate DataFrames
        results = pd.DataFrame(results)
        errors = pd.DataFrame(errors)
        stat_checks = pd.DataFrame(stat_checks)

        # Swap Columns and correct zaid sorting
        # results
        for df in [results, errors, stat_checks]:
            df['index'] = pd.to_numeric(df['Zaid'].values, errors='coerce')
            df.sort_values('index', inplace=True)
            del df['index']

            df.set_index(['Zaid', 'Zaid Name'], inplace=True)
            df.reset_index(inplace=True)

        self.outputs = outputs
        self.results = results
        self.errors = errors
        self.stat_checks = stat_checks

        # Write excel
        ex = SphereExcelOutputSheet(template, outpath)
        # Results
        ex.insert_df(9, 2, results, 0)
        ex.insert_df(9, 2, errors, 1)
        ex.insert_df(9, 2, stat_checks, 2)
        ex.wb.sheets[0].range('D1').value = self.lib
        ex.save()

    def pp_excel_comparison(self):
        """
        Compute the data and create the excel for all libraries comparisons.
        In the meantime, additional data is stored for future plots.


        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'Templates',
                                'Sphere_comparison.xlsx')

        outputs = {}
        iteration = 0
        for reflib, tarlib, name in self.couples:
            outpath = os.path.join(self.excel_path, 'Sphere_comparison_' +
                                   name+'.xlsx')
            # Get results
            dfs = []

            for test_path in [self.test_path[reflib], self.test_path[tarlib]]:
                results = []
                iteration = iteration+1
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
                        elif file[-1] == 'o':
                            outfile = file

                    # Parse output
                    mfile = os.path.join(results_path, mfile)
                    outfile = os.path.join(results_path, outfile)
                    output = SphereMCNPoutput(mfile, outfile)
                    outputs_lib[zaidnum] = output

                    res, columns = output.get_comparison_data()
                    try:
                        zn = int(zaidnum)
                    except ValueError:  # Happens for typical materials
                        zn = zaidnum

                    res.append(zn)
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

            self.diff_data = final

            # Correct sorting
            final.reset_index(inplace=True)
            final['index'] = pd.to_numeric(final['Zaid'].values,
                                           errors='coerce')
            final.sort_values('index', inplace=True)
            del final['index']
            final.set_index(['Zaid', 'Zaid Name'], inplace=True)

            # Create and concat the summary
            old_l = 0
            old_lim = 0
            rows = []
            limits = [0, 0.05, 0.1, 0.2, 0.2]
            for i, sup_lim in enumerate(limits[1:]):
                if i == len(limits)-2:
                    row = {'Range': '% of cells > '+str(sup_lim*100)}
                    for column in final.columns:
                        cleaned = final[column].replace('', np.nan).dropna()
                        l_range = len(cleaned[abs(cleaned) > sup_lim])
                        try:
                            row[column] = l_range/len(cleaned)
                        except ZeroDivisionError:
                            row[column] = np.nan
                else:
                    row = {'Range': str(old_lim*100)+' < '+'% of cells' +
                           ' < ' + str(sup_lim*100)}
                    for column in final.columns:
                        cleaned = final[column].replace('', np.nan).dropna()
                        lenght = len(cleaned[abs(cleaned) < sup_lim])
                        old_l = len(cleaned[abs(cleaned) < limits[i]])
                        l_range = lenght-old_l
                        try:
                            row[column] = l_range/len(cleaned)
                        except ZeroDivisionError:
                            row[column] = np.nan

                old_lim = sup_lim
                rows.append(row)

            summary = pd.DataFrame(rows)
            summary.set_index('Range', inplace=True)

            # If it is zero the CS are equal! (NaN if both zeros)
            final[final == np.nan] = 'Not Available'
            final[final == 0] = 'Identical'

            # Write excel
            ex = SphereExcelOutputSheet(template, outpath)
            # Results
            rangeex = ex.wb.sheets[0].range('B10')
            rangeex.options(index=True, header=True).value = final
            ex.wb.sheets[0].range('D1').value = name
            rangeex2 = ex.wb.sheets[0].range('V10')
            rangeex2.options(index=True, header=True).value = summary

            # Add single pp sheets
            for lib in [reflib, tarlib]:
                cp = self.session.state.get_path('single',
                                                 [lib, 'Sphere', 'Excel'])
                file = os.listdir(cp)[0]
                cp = os.path.join(cp, file)
                ex.copy_sheets(cp)

            ex.save()

    def print_raw(self):
        for key, data in self.raw_data.items():
            file = os.path.join(self.raw_path, key+'.csv')
            data.to_csv(file, header=True, index=False)


class SphereMCNPoutput(MCNPoutput):

    def organize_mctal(self):
        """
        Retrieve and organize mctal data. Simplified for sphere leakage case

        Returns: DataFrame containing the organized data
        """
        # Extract data
        rows = []
        rowstotal = []
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
                                                        if val <= 0:
                                                            err = np.nan

                                                        row = [num, des,
                                                               erg,
                                                               val, err]
                                                        rows.append(row)

            # If Energy binning is involved
            if t.ergTC == 't':
                # 7 steps to get to energy, + 4 for time and mesh directions
                totalbin = t.valsErrors[-1][-1][-1][-1][-1][-1][-1][-1][-1][-1][-1]
                totalvalue = totalbin[0]
                if totalvalue > 0:
                    totalerror = totalbin[-1]
                else:
                    totalerror = np.nan
                row = [num, des, totalvalue, totalerror]
                rowstotal.append(row)

        df = pd.DataFrame(rows, columns=['Tally N.', 'Tally Description',
                                         'Energy', 'Value', 'Error'])
        dftotal = pd.DataFrame(rowstotal, columns=['Tally N.',
                                                   'Tally Description',
                                                   'Value', 'Error'])
        return df, dftotal

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
        data = self.tallydata.set_index(['Tally Description', 'Energy'])
        totbins = self.totalbin.set_index('Tally Description')
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

            # Get mean error among bins, different for single bin
            if tally.ergTC == 't':
                mean_error = totbins.loc[tally.tallyComment[0]]['Error']
            else:
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
        data = self.tallydata.set_index(['Tally Description', 'Energy'])
        totalbins = self.totalbin.set_index('Tally Description')
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
                    masked_tot = totalbins.loc[tally.tallyComment[0]]
                    # Get energy bins
                    bins = list(masked.reset_index()['Energy'].values)
                    for ebin in bins:
                        # colname = '(T.ly '+str(num)+') '+str(ebin)
                        colname = str(ebin)+' [MeV]'+' [t'+num+']'
                        columns.append(colname)
                        results.append(masked['Value'].loc[ebin])
                    # Add the total bin
                    colname = 'Total'+' [t'+num+']'
                    columns.append(colname)
                    results.append(masked_tot['Value'])

                else:
                    columns.append(tally.tallyComment[0])
                    results.append(masked['Value'].values[0])

        return results, columns


class SphereExcelOutputSheet:
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
