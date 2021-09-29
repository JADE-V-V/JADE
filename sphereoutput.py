# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 10:36:38 2020

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

import xlwings as xw
import excel_support as exsupp
import pandas as pd
import os
import shutil
import plotter
import pythoncom
import math

from tqdm import tqdm
import atlas as at
import numpy as np
from output import BenchmarkOutput
from output import MCNPoutput


class SphereOutput(BenchmarkOutput):

    def __init__(self, lib, testname, session):
        super().__init__(lib, testname, session)

        # Load the settings for zaids and materials
        mat_path = os.path.join(self.cnf_path, 'MaterialsSettings.csv')
        self.mat_settings = pd.read_csv(mat_path, sep=';').set_index('Symbol')

        zaid_path = os.path.join(self.cnf_path, 'ZaidSettings.csv')
        self.zaid_settings = pd.read_csv(zaid_path, sep=';').set_index('Z')

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
        print(' Dumping Raw Data...')
        self.print_raw()
        print(' Generating plots...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)
        self._generate_single_plots(outpath)
        print(' Single library post-processing completed')

    def _generate_single_plots(self, outpath):
        """
        Generate all the requested plots in a temporary folder

        Parameters
        ----------
        outpath : str or path
            path to the temporary folder where to store plots.

        Returns
        -------
        None.

        """
        for tally, title, quantity, unit in \
            [(2, 'Leakage Neutron Flux (175 groups)',
              'Neutron Flux', r'$\#/cm^2$'),
             (32, 'Leakage Gamma Flux (24 groups)',
              'Gamma Flux', r'$\#/cm^2$')]:

            print(' Plotting tally n.'+str(tally))
            for zaidnum, output in tqdm(self.outputs.items()):
                title = title
                tally_data = output.tallydata.set_index('Tally N.').loc[tally]
                energy = tally_data['Energy'].values
                values = tally_data['Value'].values
                error = tally_data['Error'].values
                lib_name = self.session.conf.get_lib_name(self.lib)
                lib = {'x': energy, 'y': values, 'err': error,
                       'ylabel': str(zaidnum)+' ('+lib_name+')'}
                data = [lib]
                outname = str(zaidnum)+'-'+self.lib+'-'+str(tally)
                plot = plotter.Plotter(data, title, outpath, outname, quantity,
                                       unit, 'Energy [MeV]', self.testname)
                plot.plot('Binned graph')

        self._build_atlas(outpath)

    def _build_atlas(self, outpath):
        """
        Build the atlas using all plots contained in directory

        Parameters
        ----------
        outpath : str or path
            temporary folder containing all plots.

        Returns
        -------
        None.

        """
        # Printing Atlas
        template = os.path.join(self.code_path, 'templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, 'Sphere '+self.lib)
        atlas.build(outpath, self.session.lib_manager, self.mat_settings)
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

    def compare(self):
        """
        Execute the full post-processing of a comparison of libraries
        (i.e. excel, and atlas)

        Returns
        -------
        None.

        """
        print(' Generating Excel Recap...')
        self.pp_excel_comparison()
        print(' Creating Atlas...')
        outpath = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(outpath)
        # Recover all libraries and zaids involved
        allzaids, libraries, outputs = self._get_organized_output()

        globalname = ''
        for lib in self.lib:
            globalname = globalname + lib + '_Vs_'

        globalname = globalname[:-4]

        # Plot everything
        print(' Generating Plots Atlas...')
        self._generate_plots(libraries, allzaids, outputs, globalname, outpath)
        print(' Comparison post-processing completed')

    def _generate_plots(self, libraries, allzaids, outputs, globalname,
                        outpath):

        for tally, title, quantity, unit in [(2, 'Leakage Neutron Flux (175 groups)',
                                             'Neutron Flux', r'$\#/cm^2$'),
                                             (32, 'Leakage Gamma Flux (24 groups)',
                                             'Gamma Flux', r'$\#/cm^2$')]:

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
                        lib_name = self.session.conf.get_lib_name(libraries[idx])
                        lib = {'x': energy, 'y': values, 'err': error,
                               'ylabel': str(zaidnum)+' ('+lib_name+')'}
                        data.append(lib)
                    except KeyError:
                        # It is ok, simply nothing to plot here
                        pass

                outname = str(zaidnum)+'-'+globalname+'-'+str(tally)
                plot = plotter.Plotter(data, title, outpath, outname, quantity,
                                       unit, 'Energy [MeV]', self.testname)
                plot.plot('Binned graph')

        self._build_atlas(outpath)

    def _get_organized_output(self):
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

        return libraries, zaids, outputs

    def pp_excel_single(self):
        """
        Generate the single library results excel

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'templates', 'Sphere_single.xlsx')
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
                zaidnum = pieces[-1].upper()
                zaidname = self.mat_settings.loc[zaidnum, 'Name']
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
        lib_name = self.session.conf.get_lib_name(self.lib)
        ex.wb.sheets[0].range('D1').value = lib_name
        ex.save()

    def pp_excel_comparison(self):
        """
        Compute the data and create the excel for all libraries comparisons.
        In the meantime, additional data is stored for future plots.


        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'templates',
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
                    # Check for material exception
                    if zaidnum == 'Sphere':
                        zaidnum = pieces[-1].upper()
                        zaidname = self.mat_settings.loc[zaidnum, 'Name']
                    else:
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
            absdiff = (dfs[0].loc[newidx]-dfs[1].loc[newidx])

            self.diff_data = final
            self.absdiff = absdiff

            # Correct sorting
            for df in [final, absdiff]:
                df.reset_index(inplace=True)
                df['index'] = pd.to_numeric(df['Zaid'].values, errors='coerce')
                df.sort_values('index', inplace=True)
                del df['index']
                df.set_index(['Zaid', 'Zaid Name'], inplace=True)

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
            for df in [final, absdiff]:
                df[df == np.nan] = 'Not Available'
                df[df == 0] = 'Identical'

            # --- Write excel ---
            # Generate the excel
            ex = SphereExcelOutputSheet(template, outpath)
            # Prepare the copy of the comparison sheet
            template_sheet = 'Comparison'
            template_absdiff = 'Comparison (Abs diff)'
            ws_comp = ex.wb.sheets[template_sheet]
            ws_diff = ex.wb.sheets[template_absdiff]

            # WRITE RESULTS
            # Percentage comparison
            rangeex = ws_comp.range('B10')
            rangeex.options(index=True, header=True).value = final
            ws_comp.range('D1').value = name
            rangeex2 = ws_comp.range('V10')
            rangeex2.options(index=True, header=True).value = summary
            # Absolute difference comparison
            rangeex = ws_diff.range('B10')
            rangeex.options(index=True, header=True).value = absdiff
            ws_diff.range('D1').value = name

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


class SphereSDDRoutput(SphereOutput):

    times = ['0s', '2.7h', '24h', '11.6d', '30d', '10y']
    timecols = {'0s': '1.0', '2.7h': '2.0', '24h': '3.0',
                '11.6d': '4.0', '30d': '5.0', '10y': '6.0'}

    def pp_excel_single(self):
        """
        Generate the single library results excel

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'templates',
                                'SphereSDDR_single.xlsx')
        outpath = os.path.join(self.excel_path, 'SphereSDDR_single_' +
                               self.lib+'.xlsx')
        # compute the results
        results, errors, stat_checks = self._compute_single_results()

        # Write excel
        ex = SphereExcelOutputSheet(template, outpath)
        # Results
        ex.insert_df(11, 2, results, 0, header=False)
        ex.insert_df(11, 2, errors, 1, header=False)
        ex.insert_df(9, 2, stat_checks, 2, header=True)
        lib_name = self.session.conf.get_lib_name(self.lib)
        ex.wb.sheets[0].range('E1').value = lib_name
        ex.save()

    def pp_excel_comparison(self):
        """
        Generate the excel comparison output

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), 'templates',
                                'SphereSDDR_comparison.xlsx')

        for reflib, tarlib, name in self.couples:
            outpath = os.path.join(self.excel_path, 'Sphere_comparison_' +
                                   name+'.xlsx')
            final, absdiff = self._compute_compare_result(reflib, tarlib)

            # --- Write excel ---
            # Generate the excel
            ex = SphereExcelOutputSheet(template, outpath)
            # Prepare the copy of the comparison sheet
            ws_comp = ex.wb.sheets['Comparison']
            ws_diff = ex.wb.sheets['Comparison (Abs diff)']

            # WRITE RESULTS
            # Percentage comparison
            rangeex = ws_comp.range('B11')
            rangeex.options(index=True, header=False).value = final
            ws_comp.range('E1').value = name

            # Absolute difference comparison
            rangeex = ws_diff.range('B11')
            rangeex.options(index=True, header=False).value = absdiff

            # Add single pp sheets
            for lib in [reflib, tarlib]:
                cp = self.session.state.get_path('single',
                                                 [lib, 'SphereSDDR', 'Excel'])
                file = os.listdir(cp)[0]
                cp = os.path.join(cp, file)
                ex.copy_sheets(cp)

            ex.save()

    def _get_organized_output(self):
        """
        Simply recover a list of the zaids and libraries involved
        """
        zaids = []
        for (zaidnum, mt, lib), _ in self.outputs.items():
            zaids.append((zaidnum, mt))

        zaids = list(set(zaids))
        libs = []  # Not used
        outputs = []  # Not used

        return zaids, libs, outputs

    def _generate_single_plots(self, outpath):
        allzaids, libs, outputs = self._get_organized_output()
        globalname = self.lib
        self._generate_plots(libs, allzaids, outputs, globalname, outpath)

    def _generate_plots(self, libraries, allzaids, outputs, globalname,
                        outpath):
        """
        Generate all the plots requested by the Sphere SDDR benchmark

        Parameters
        ----------
        libraries : dummy
            here only for compatibility issues.
        allzaids : list
            list of all zaids resulting from the union of the results from
            both libraries.
        outputs : dummy
            here only for compatibility reasons.
        globalname : str
            name for the output.
        outpath : str
            path to use for the dumping of imgs.

        Returns
        -------
        None.

        """
        # Check if self libraries is already a list
        if type(self.lib) != list:
            libraries = [self.lib]
        else:
            libraries = self.lib

        # Initialize atlas
        template = os.path.join(self.code_path, 'templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, 'Sphere SDDR '+globalname)
        libmanager = self.session.lib_manager

        # ------------- Binned plots of gamma flux ------------
        atlas.doc.add_heading('Photon Flux (32)', level=1)
        fluxquantity = 'Photon Flux'
        fluxunit = r'$p/(cm^2\cdot\#_S)$'
        allzaids.sort()
        # --- Binned plots of the gamma flux ---
        for (zaidnum, mt) in tqdm(allzaids, desc=' Binned flux plots'):
            # Get everything for the title of the zaid
            try:
                name, formula = libmanager.get_zaidname(zaidnum)
                args = [zaidnum, name, formula, mt]
                title = 'Zaid: {} ({} {}), MT={}'.format(*args)
            except ValueError:  # A material is passed instead of zaid
                matname = self.mat_settings.loc[zaidnum, 'Name']
                title = zaidnum+' ('+matname+')'
            atlas.doc.add_heading(title, level=2)

            # Now create a plot for each time
            for time in self.times:
                atlas.doc.add_heading('Cooldown time = {}'.format(time),
                                      level=3)
                title = 'Gamma Leakage flux after a {} cooldown'.format(time)
                data = []
                for lib in libraries:
                    try:  # Zaid could not be common to the libraries
                        outp = self.outputs[zaidnum, mt, lib]
                    except KeyError:
                        # It is ok, simply nothing to plot here since zaid was
                        # not in library
                        continue
                    # Get the zaid flux
                    tally_data = outp.tallydata[32].set_index('Time')

                    # Select the correct time
                    t = 'F'+self.timecols[time]
                    tally_data = tally_data.loc[t]
                    # If for some reason a total survived just kill him
                    tally_data = tally_data[tally_data.Energy != 'total']

                    energy = tally_data['Energy'].values
                    values = tally_data['Value'].values
                    error = tally_data['Error'].values
                    lib_name = self.session.conf.get_lib_name(lib)
                    ylabel = '{}_{} ({})'.format(formula, mt, lib_name)
                    libdata = {'x': energy, 'y': values, 'err': error,
                               'ylabel': ylabel}
                    data.append(libdata)

                outname = '{}-{}-{}-{}-{}'.format(zaidnum, mt, globalname,
                                                  32, t)
                plot = plotter.Plotter(data, title, outpath, outname,
                                       fluxquantity, fluxunit, 'Energy [MeV]',
                                       self.testname)
                outfile = plot.plot('Binned graph')
                atlas.insert_img(outfile)

        # --- Wave plots flux ---
        # Do this block only if libs are more than one
        lim = 35  # limit of zaids to be in a single plot
        # Plot parameters which are not going to change
        quantity = ['Neutron Flux', 'Photon Flux', 'SDDR']
        unit = [r'$n/(cm^2\cdot n_S)$', r'$p/(cm^2\cdot n_S)$', 'Sv/h']
        xlabel = 'Zaid/Material and MT value'
        if len(libraries) > 1:
            atlas.doc.add_heading('Flux and SDDR ratio plots', level=1)
            # 1) collect zaid-mt couples in libraries and keep only the ones
            #    that appears on the reference + at least one lib
            # Build a df will all possible zaid, mt, lib combination
            allkeys = list(self.outputs.keys())
            df = pd.DataFrame(allkeys)
            df.columns = ['zaid', 'mt', 'lib']
            df['zaid-mt'] = df['zaid'].astype(str)+'-'+df['mt'].astype(str)
            df.set_index('lib', inplace=True)
            # get the reference zaids
            refzaids = set(df.loc[self.lib[0]]['zaid-mt'].values)
            otherzaids = set(df.drop(self.lib[0])['zaid-mt'].values)
            # Get the final zaid-mt couples to consider
            couples = []
            for zaidmt in refzaids:
                if zaidmt in otherzaids:
                    zaid, mt = zaidmt.split('-')
                    couples.append((zaid, mt))
            # sort it
            couples.sort(key=self._sortfunc_zaidMTcouples)

            # There is going to be a plot for each cooldown time
            for i, time in enumerate(tqdm(self.times, desc=' Ratio plots')):
                atlas.doc.add_heading('Cooldown time = {}'.format(time),
                                      level=2)
                # 2) Recover/compute the data tha needs to be plot for each lib
                data = []
                for lib in self.lib:
                    nfluxs = []
                    pfluxs = []
                    sddrs = []
                    xlabels = []
                    ylabel = self.session.conf.get_lib_name(lib)
                    for zaid, mt in couples:
                        tallies = self.outputs[zaid, mt, lib].tallydata
                        # Extract values
                        nflux = tallies[12].set_index('Energy').drop('total')
                        nflux = nflux.sum().loc['Value']
                        pflux = tallies[22].groupby('Time').sum().loc[i+1,
                                                                      'Value']
                        sddr = tallies[104].set_index('Time')
                        sddr = sddr.loc['D'+self.timecols[time], 'Value']
                        # Memorize values
                        nfluxs.append(nflux)
                        pfluxs.append(pflux)
                        sddrs.append(sddr)
                        try:
                            name, formula = libmanager.get_zaidname(zaid)
                        except ValueError:
                            formula = zaid
                        xlabels.append(formula+' '+mt)

                    # Split the data if its length is more then the limit
                    datalenght = len(xlabels)
                    sets = math.ceil(datalenght/lim)
                    last_idx = 0
                    idxs = []
                    step = int(datalenght/sets)
                    for i in range(sets):
                        newidx = last_idx+step
                        idxs.append((last_idx, newidx))
                        last_idx = newidx

                    for j, (start, end) in enumerate(idxs):
                        # build the dic
                        ydata = [nfluxs[start:end],
                                 pfluxs[start:end],
                                 sddrs[start:end]]
                        libdata = {'x': xlabels, 'y': ydata, 'err': [],
                                   'ylabel': ylabel}
                        # try to append it to the data in the correct index
                        # if the index is not found, then the list still needs
                        # to be initialized
                        try:
                            data[j].append(libdata)
                        except IndexError:
                            data.append([libdata])

                # 3) Compute parameters for the plotter init
                for datapiece in data:
                    title = 'Ratio Vs FENDL3.1 (T0 + {})'.format(time)
                    outname = 'dummy'  # Does not matter if plot is added imm.
                    testname = self.testname
                    plot = plotter.Plotter(datapiece, title, outpath, outname,
                                           quantity, unit, xlabel, testname)
                    outfile = plot.plot('Waves')
                    atlas.insert_img(outfile)

        ########
        print(' Building...')
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

    def _compute_single_results(self):
        """
        Compute the excel single post processing results and memorize them

        Parameters
        ----------

        Returns
        -------
        results : pd.DataFrame
            global excel datataframe of all values.
        errors : pd.DataFrame
            global excel dataframe of all errors.
        stat_checks : pd.DataFrame
            global excel dataframe of all statistical checks.

        """
        # Get results
        results = []
        errors = []
        stat_checks = []
        desc = ' Parsing Outputs: '
        for folder in tqdm(os.listdir(self.test_path), desc=desc):
            res, err, st_ck = self._parserun(self.test_path, folder, self.lib)
            results.append(res)
            errors.append(err)
            stat_checks.append(st_ck)

        # Generate DataFrames
        results = pd.concat(results, axis=1).T
        errors = pd.concat(errors, axis=1).T
        stat_checks = pd.DataFrame(stat_checks)

        # Swap Columns and correct zaid sorting
        # results
        for df in [results, errors, stat_checks]:
            self._sort_df(df)  # it is sorted in place

        # self.outputs = outputs
        self.results = results
        self.errors = errors
        self.stat_checks = stat_checks

        return results, errors, stat_checks

    def _compute_compare_result(self, reflib, tarlib):
        """
        Given a refere4nce lib and a target lib, both absolute and relative
        comparison are computed

        Parameters
        ----------
        reflib : str
            reference library suffix.
        tarlib : str
            target library suffix.

        Returns
        -------
        final : pd.DataFrame
            relative comparison table.
        absdiff : pd.DataFrame
            absolute comparison table.

        """
        # Get results both of the reflib and tarlib
        dfs = []
        test_paths = [self.test_path[reflib], self.test_path[tarlib]]
        libs = [reflib, tarlib]
        for test_path, lib in zip(test_paths, libs):
            results = []
            # Extract all the series from the different reactions
            for folder in os.listdir(test_path):
                # Collect the data
                res, _, _ = self._parserun(test_path, folder, lib)
                results.append(res)

            # Build the df and sort
            df = pd.concat(results, axis=1).T
            self._sort_df(df)
            # They need to be indexed
            df.set_index(['Parent', 'Parent Name', 'MT'], inplace=True)
            # Add the df to the list
            dfs.append(df)

        # Consider only common zaids
        idx1 = dfs[0].index
        idx2 = dfs[1].index
        newidx = idx1.intersection(idx2)
        # For some reason they arrive here as objects triggering
        # a ZeroDivisionError
        ref = dfs[0].loc[newidx].astype(float)
        tar = dfs[1].loc[newidx].astype(float)

        # Build the final excel data
        absdiff = ref-tar
        final = absdiff/ref

        # If it is zero the CS are equal! (NaN if both zeros)
        for df in [final, absdiff]:
            df[df == np.nan] = 'Not Available'
            df[df == 0] = 'Identical'

        return final, absdiff

    @staticmethod
    def _sort_df(df):
        df['index'] = pd.to_numeric(df['Parent'].values, errors='coerce')
        df.sort_values('index', inplace=True)
        del df['index']

        df.set_index(['Parent', 'Parent Name', 'MT'], inplace=True)
        df.reset_index(inplace=True)

    @staticmethod
    def _sortfunc_zaidMTcouples(item):
        try:
            zaid = int(item[0])
        except ValueError:
            zaid = (item[0])
        try:
            mt = int(item[1])
        except ValueError:
            mt = item[1]

        if isinstance(zaid, str):
            flag = True
        else:
            flag = False

        return (flag, zaid, mt)

    def _parserun(self, test_path, folder, lib):
        """
        given a MCNP run folder the parsing of the different outputs is
        performed

        Parameters
        ----------
        test_path : path or str
            path to the test.
        folder : str
            name of the folder to parse inside test_path.
        lib : str
            library.

        Returns
        -------
        res : TYPE
            DESCRIPTION.
        err : TYPE
            DESCRIPTION.
        st_ck : TYPE
            DESCRIPTION.

        """
        results_path = os.path.join(test_path, folder)
        pieces = folder.split('_')
        # Get zaid
        zaidnum = pieces[1]
        # Check for material exception
        try:
            zaidname = self.mat_settings.loc[zaidnum, 'Name']
            mt = 'All'
        except KeyError:
            # it is a simple zaid
            zaidname = pieces[2]
            mt = pieces[3]
        # Get mfile
        for file in os.listdir(results_path):
            if file[-1] == 'm':
                mfile = file
            elif file[-1] == 'o':
                ofile = file
        # Parse output
        output = SphereSDDRMCNPoutput(os.path.join(results_path, mfile),
                                      os.path.join(results_path, ofile))
        self.outputs[zaidnum, mt, lib] = output
        # Adjourn raw Data
        self.raw_data[zaidnum, mt, lib] = output.tallydata
        # Recover statistical checks
        st_ck = output.stat_checks
        # Recover results and precisions
        res, err = output.get_single_excel_data()
        for series in [res, err, st_ck]:
            series['Parent'] = zaidnum
            series['Parent Name'] = zaidname
            series['MT'] = mt

        return res, err, st_ck

    def print_raw(self):
        for key, data in self.raw_data.items():
            # build a folder containing each tally of the reaction
            foldername = '{}_{}'.format(key[0], key[1])
            folder = os.path.join(self.raw_path, foldername)
            os.mkdir(folder)
            # Dump all tallies
            for tallynum, df in data.items():
                filename = '{}_{}_{}.csv'.format(key[0], key[1], tallynum)
                file = os.path.join(folder, filename)
                df.to_csv(file, header=True, index=False)


class SphereSDDRMCNPoutput(SphereMCNPoutput):
    def organize_mctal(self):
        """
        Reorganize the MCTAL data in dataframes

        Returns
        -------
        tallydata : dic of DataFrame
            contains the tally data in a df format.
        totalbin : dic of DataFrame
            contain the total bin data.
        """
        # This should use the original MCNPotput organization of
        # MCTAL
        tallydata, totalbin = super(SphereMCNPoutput, self).organize_mctal()

        return tallydata, totalbin

    def get_single_excel_data(self):
        """
        Return the data that will be used in the single
        post-processing excel output for a single reaction

        Returns
        -------
        vals : pd.Series
            series reporting the result of a single reaction.
        errors : pd.Series
            series containing the errors associated with the
            reactions.

        """
        # 32 -> fine gamma flux
        # 104 -> Dose rate
        flux = self.tallydata[32]
        sddr = self.tallydata[104]
        heat = self.tallydata[46]

        # Differentiate time labels
        flux['Time'] = 'F' + flux['Time'].astype(str)
        sddr['Time'] = 'D' + sddr['Time'].astype(str)
        heat['Time'] = 'H' + heat['Time'].astype(str)

        # Get the total values of the flux at different cooling times
        fluxvals = flux.groupby('Time').sum()['Value']
        # Get the mean error of the flux at different cooling times
        fluxerrors = flux.groupby('Time').mean()['Error']

        # Get the total values of the SDDR at different cooling times
        sddrvals = sddr.groupby('Time').sum()['Value']
        # Get the mean error of the SDDR at different cooling times
        sddrerrors = sddr.groupby('Time').mean()['Error']

        # Get the total Heating at different cooling times
        heatvals = heat.set_index('Time')['Value']
        # Get the Heating mean error at different cooling times
        heaterrors = heat.set_index('Time')['Error']

        # Delete the total row in case it is there
        for df, tag in zip([fluxvals, fluxerrors, sddrvals, sddrerrors,
                            heatvals, heaterrors],
                           ['F', 'F', 'D', 'D', 'H', 'H']):
            try:
                del df[tag+'total']
            except KeyError:
                # If total value is not there it is ok
                pass

        # 2 series need to be built here, one for values and one for errors
        vals = pd.concat([fluxvals, sddrvals, heatvals], axis=0)
        errors = pd.concat([fluxerrors, sddrerrors, heaterrors],
                           axis=0)

        return vals, errors


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

    def insert_df(self, startrow, startcolumn, df, ws, header=True):
        '''
        Insert a DataFrame (df) into a Worksheet (ws) using openpyxl.
        (startrow) and (startcolumn) identify the starting data entry
        '''
        ws = self.wb.sheets[ws]
        exsupp.insert_df(startrow, startcolumn, df, ws, header=header)

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

    def copy_internal_sheet(self, template_sheet, newname):
        """
        Return a renamed copy of a particular sheet

        Parameters
        ----------
        template_sheet : xw.Sheet
            sheet to copy.
        newname : str
            name of the new sheet.

        Returns
        -------
        ws : xw.Sheet
            copied sheet.

        """
        # Copy the template sheet
        try:  # Should work from v0.22 of xlwings
            template_sheet.copy(before=template_sheet)
        except AttributeError:
            # Fall Back onto the native object
            template_sheet.api.Copy(Before=template_sheet.api)
        try:
            ws = self.wb.sheets(template_sheet.name+' (2)')
        except pythoncom.com_error:
            print('The available sheets are :'+str(self.wb.sheets))
        try:
            ws.name = newname
        except pythoncom.com_error:
            ws.Name = newname
        return ws

    def save(self):
        """
        Save Excel
        """
        self.app.calculate()
        self.wb.save()
        self.wb.close()
        self.app.quit()
