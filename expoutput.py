# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 17:18:07 2020

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
import pandas as pd
import numpy as np
import os
import atlas as at
import shutil

from output import BenchmarkOutput
from output import MCNPoutput
from tqdm import tqdm
from status import EXP_TAG
from plotter import Plotter
from scipy.interpolate import interp1d


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
        """
        Produce the C/E excel file and the ATLAS containing the comparison
        of the tested libraries with the experimental results

        Returns
        -------
        None.

        """
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
        template = os.path.join(self.code_path, 'templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, globalname)

        maintitle = ' Oktavian Experiment: '
        unit = r'$ 1/cm^2\cdot n_s\cdot u$'
        xlabel = 'Energy [MeV]'

        tables = []  # All C/E tables will be stored here and then concatenated

        # Tally numbers should be fixed
        for tallynum in ['21', '41']:
            if tallynum == '21':
                particle = 'Neutron'
            else:
                particle = 'Photon'

            print(' Printing the '+particle+' Letharghy flux...')
            tit_tag = particle+'  Leakage Current per Unit Lethargy'
            quantity = particle+' Leakage Current'

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
                # lib will be passed to the plotter
                lib = {'x': x, 'y': y, 'err': err,
                       'ylabel': material + ' (Experiment)'}
                # Get also the interpolator
                interpolator = interp1d(x, y, fill_value=0, bounds_error=False)

                # Collect the data to be plotted
                data = [lib]  # The first one should be the exp one
                for lib_tag in self.lib[1:]:  # Avoid exp
                    lib_name = self.session.conf.get_lib_name(lib_tag)
                    try:  # The tally may not be defined
                        # Data for the plotter
                        values = self.results[material, lib_tag][tallynum]
                        lib = {'x': values['Energy [MeV]'],
                               'y': values['Lethargy'], 'err': values['Error'],
                               'ylabel': material + ' ('+lib_name+')'}
                        data.append(lib)
                        # data for the table
                        table = _get_tablevalues(values, interpolator)
                        table['Particle'] = particle
                        table['Material'] = material
                        table['Library'] = lib_name
                        tables.append(table)
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

        # Dump the global C/E table
        print(' Dump the C/E table in Excel...')
        final_table = pd.concat(tables)
        todump = final_table.set_index(['Material', 'Particle', 'Library'])
        ex_outpath = os.path.join(self.excel_path, 'C over E table.xlsx')

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(ex_outpath, engine='xlsxwriter')
        # dump global table
        todump.to_excel(writer, sheet_name='Global')

        # Elaborate table for better output format
        ft = final_table.set_index(['Material'])
        ft['Energy Range [MeV]'] = (ft['Min E'].astype(str) + ' - ' +
                                    ft['Max E'].astype(str))
        ft['C/E (mean +/- σ)'] = (ft['C/E'].round(2).astype(str) + ' +/- ' +
                                  ft['Standard Deviation (σ)'].round(2).astype(str))
        # Delete all confusing columns
        for column in ['C/E', 'Standard Deviation (σ)', 'Max E', 'Min E']:
            del ft[column]

        # Dump also table material by material
        for material in self.materials:
            # dump material table
            todump = ft.loc[material]
            todump = todump.pivot(index=['Particle', 'Energy Range [MeV]'],
                                  columns='Library', values='C/E (mean +/- σ)')
            todump.to_excel(writer, sheet_name=material, startrow=2)
            ws = writer.sheets[material]
            ws.write_string(0, 0, '"C/E (mean +/- σ)"')

            # adjust columns' width
            writer.sheets[material].set_column(0, 4, 18)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # atlas.insert_df(final_table)

        # Save Atlas
        print(' Producing the PDF...')
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
            errors = []
            for i, t in enumerate(energies):
                val = tally.getValue(0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0, 0)
                err = tally.getValue(0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0, 1)
                flux.append(val)
                errors.append(err)

            # Energies for lethargy computation
            ergs = [1e-10]  # Additional "zero" energy for lethargy computation
            ergs.extend(energies.tolist())
            ergs = np.array(ergs)

            flux = flux/np.log((ergs[1:]/ergs[:-1]))
            res2['Energy [MeV]'] = energies
            res2['Lethargy'] = flux
            res2['Error'] = errors

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
        columns = ['Upper Energy [MeV]', 'Nominal Energy [MeV]',
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
                         header=None, sep=r'\s+')
        df.columns = columns

        df = df[df['Lethargy Flux'] > 2e-38]

        x = df['Nominal Energy [MeV]'].values
        y = df['Lethargy Flux'].values
        err = df['Error'].values

        return x, y, err


def _get_tablevalues(df, interpolator, x='Energy [MeV]', y='Lethargy',
                     e_intervals=[0.1, 1, 5, 10, 20]):
    """
    Given the benchmark and experimental results returns a df to compile the
    C/E table for energy intervals

    Parameters
    ----------
    df : pd.DataFrame
        benchmark data.
    interpolator : func
        interpolator from experimental data.
    x : str, optional
        x column. The default is 'Energy [MeV]'.
    y : str, optional
        y columns. The default is 'Lethargy'.
    e_intervals : list, optional
        energy intervals to be used. The default is [0, 0.1, 1, 5, 10, 20].

    Returns
    -------
    pd.DataFrame
        C/E table per energy interval.

    """
    rows = []
    df = pd.DataFrame(df)
    df['Exp'] = interpolator(df[x])
    df['C/E'] = df[y]/df['Exp']
    e_min = e_intervals[0]
    for e_max in e_intervals[1:]:
        red = df[e_min < df[x]]
        red = red[red[x] < e_max]
        mean = red['C/E'].mean()
        std = red['C/E'].std()
        row = {'C/E': mean, 'Standard Deviation (σ)': std,
               'Max E': e_max, 'Min E': e_min}
        rows.append(row)
        # adjourn min energy
        e_min = e_max

    return pd.DataFrame(rows)
