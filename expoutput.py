# -*- coding: utf-8 -*-
# Created on Wed Oct 21 17:18:07 2020

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
from abc import abstractmethod
from inputfile import D1S_Input
import re


class ExperimentalOutput(BenchmarkOutput):
    def __init__(self, *args, **kwargs):
        """
        This extends the Benchmark Output and creates an abstract class
        for all experimental outputs.
        Parameters
        ----------
        *args : TYPE
            see BenchmarkOutput doc.
        **kwargs : TYPE
            see BenchmarkOutput doc.
        multiplerun : bool
            this additional keyword specifies if the benchmark is composed
            by more than one MCNP run. It defaults to False.
        Returns
        -------
        None.
        """
        # Add a special keyword for experimental benchmarks
        try:
            multiplerun = kwargs.pop('multiplerun')
        except KeyError:
            # Default to False
            multiplerun = False
        # Recover session and testname
        session = args[2]
        testname = args[1]

        super().__init__(*args, **kwargs)
        # The experimental data needs to be loaded
        self.path_exp_res = os.path.join(session.path_exp_res, testname)

        # Add the raw path data (not created because it is a comparison)
        out = os.path.dirname(self.atlas_path)
        raw_path = os.path.join(out, 'Raw Data')
        os.mkdir(raw_path)
        self.raw_path = raw_path
        self.multiplerun = multiplerun

    def single_postprocess(self):
        """
        Always raise an Attribute Error since no single post-processing is
        foreseen for experimental benchmarks
        Raises
        ------
        AttributeError
            DESCRIPTION.
        Returns
        -------
        None.
        """
        raise AttributeError('\n No single pp is foreseen for exp benchmark')

    def compare(self):
        """
        Complete the routines that perform the comparison of one or more
        libraries results with the experimental ones.
        Returns
        -------
        None.
        """
        print(' Exctracting outputs...')
        self._extract_outputs()

        print(' Read experimental results....')
        self._read_exp_results()

        print(' Dumping raw data...')
        self._print_raw()

        print(' Generating Excel Recap...')
        self.pp_excel_comparison()

        print(' Creating Atlas...')
        self.build_atlas()

    def pp_excel_comparison(self):
        """
        At the moment everything is handled by _pp_excel_comparison that needs
        to be implemented in each child class. Some standard procedures may be
        added in the feature in order to reduce the amount of ex-novo coding
        necessary to implement a new experimental benchmark.
        Returns
        -------
        None.
        """
        self._pp_excel_comparison()

    def build_atlas(self):
        """
        Creation and saving of the atlas are handled by this function while
        the actual filling of the atlas is left to _build_atlas which needs
        to be implemented for each child class.
        Returns
        -------
        None.
        """
        # Build a temporary folder for images
        tmp_path = os.path.join(self.atlas_path, 'tmp')
        os.mkdir(tmp_path)

        globalname = ''
        for lib in self.lib:
            globalname = globalname + lib + '_Vs_'
        globalname = globalname[:-4]

        # Initialize the atlas
        template = os.path.join(self.code_path, 'templates',
                                'AtlasTemplate.docx')
        atlas = at.Atlas(template, globalname)

        # Fill the atlas
        atlas = self._build_atlas(tmp_path, atlas)

        # Save Atlas
        print(' Producing the PDF...')
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(tmp_path)

    def _extract_outputs(self):
        """
        Extract, organize and store the results coming from the MCNP runs
        Returns
        -------
        None.
        """
        outputs = {}
        results = {}
        # Iterate on the different libraries results except 'Exp'
        for lib, test_path in self.test_path.items():
            if lib != EXP_TAG:
                if self.multiplerun:
                    # Results are organized by folder and lib
                    for folder in os.listdir(test_path):
                        results_path = os.path.join(test_path, folder)
                        mfile, ofile = self._get_output_files(results_path)
                        # Parse output
                        output = MCNPoutput(mfile, ofile)
                        outputs[folder, lib] = output
                        # Adjourn raw Data
                        self.raw_data[folder, lib] = output.tallydata
                        # Get the meaningful results
                        results[folder, lib] = self._processMCNPdata(output)
                # Results are organized just by lib
                else:
                    mfile, ofile = self._get_output_files(test_path)
                    # Parse output
                    output = MCNPoutput(mfile, ofile)
                    outputs[lib] = output
                    # Adjourn raw Data
                    self.raw_data[lib] = output.tallydata
                    # Get the meaningful results
                    results[lib] = self._processMCNPdata(output)

        self.outputs = outputs
        self.results = results

    def _read_exp_results(self):
        """
        Read all experimental results and organize it in the self.exp_results
        dictionary.
        If multirun is set to true the first layer of the dictionary will
        consist in the different folders and the second layer will be the
        different files. If it is not multirun, insetead, only one layer of the
        different files will be generated.
        All files need to be in .csv format. If a more complex format is
        provided, the user should ovveride the _read_exp_file method.
        Returns
        -------
        None.
        """
        exp_results = {}
        if self.multiplerun:
            # Iterate on each folder and then in each file, read them and
            # build the result dic
            for folder in os.listdir(self.path_exp_res):
                exp_results[folder] = {}
                cp = os.path.join(self.path_exp_res, folder)
                for file in os.listdir(cp):
                    filename = file.split('.')[0]
                    filepath = os.path.join(cp, file)
                    df = self._read_exp_file(filepath)
                    exp_results[folder][filename] = df
        else:
            # Iterate on each each file, read it and
            # build the result dic
            for file in os.listdir(self.path_exp_res):
                filename = file.split('.')[0]
                filepath = os.path.join(self.path_exp_res, file)
                df = self._read_exp_file(filepath)
                exp_results[filename] = df

        self.exp_results = exp_results

    @staticmethod
    def _read_exp_file(filepath):
        """
        Default way of reading a csv file
        Parameters
        ----------
        filepath : path/str
            experimental file results to be read.
        Returns
        -------
        pd.DataFrame
            Contain the data read.
        """
        return pd.read_csv(filepath)

    def _print_raw(self):
        """
        Dump all the raw data
        Returns
        -------
        None.
        """
        # Multiple tests in the benchmark scope
        if self.multiplerun:
            for (folder, lib), item in self.raw_data.items():
                # Create the lib directory if it is not there
                cd_lib = os.path.join(self.raw_path, lib)
                if not os.path.exists(cd_lib):
                    os.mkdir(cd_lib)
                # Dump everything
                for key, data in item.items():
                    file = os.path.join(cd_lib,
                                        folder+' '+str(key)+'.csv')
                    data.to_csv(file, header=True, index=False)

        # Single test in the benchmark scope
        else:
            for lib, item in self.raw_data.items():
                # Create the lib directory if it is not there
                cd_lib = os.path.join(self.raw_path, lib)
                if not os.path.exists(cd_lib):
                    os.mkdir(cd_lib)

                # Dump everything
                for key, data in item.items():
                    file = os.path.join(cd_lib, str(key)+'.csv')
                    data.to_csv(file, header=True, index=False)

    @abstractmethod
    def _processMCNPdata(self, output):
        """
        Given an mctal file object return the meaningful data extracted. Some
        post-processing on the data may be foreseen at this stage.
        Parameters
        ----------
        output : MCNPoutput
            object representing an MCNP output.
        Returns
        -------
        item :
            the type of item can vary based on what the user intends to do
            whith it. It will be stored in an organized way in the self.results
            dictionary
        """
        item = None
        return item

    @abstractmethod
    def _pp_excel_comparison(self):
        '''
        Responsible for producing excel outputs
        Returns
        -------
        '''
        pass

    @abstractmethod
    def _build_atlas(self, tmp_path, atlas):
        """
        Fill the atlas with the customized plots. Creation and saving of the
        atlas are handled elsewhere.
        Parameters
        ----------
        tmp_path : path
            path to the temporary folder where to dump images.
        atlas : Atlas
            Object representing the plot Atlas.
        Returns
        -------
        atlas : Atlas
            After being filled the atlas is returned.
        """
        atlas = None
        return atlas


class FNGOutput(ExperimentalOutput):
    names = ['FNG1', 'FNG2']
    times = {'FNG1': ['1d', '7d', '15d', '30d', '60d'],
             'FNG2': ['1.22h', '1.72h', '2.08h', '3.22h', '4.80h', '6.80h',
                      '9.47h', '12.7h', '15.9h', '20.2h', '25.2h', '1.53d',
                      '2.46d', '4d', '5.55d', '8.20d', '12.2d', '19.3d',
                      '19.8d']}

    def _processMCNPdata(self, output):
        """
        Read All tallies and return them as a dictionary of DataFrames. This
        aslo needs to ovveride the raw data since unfortunately it appears
        that the user bins necessary for tracking daughters and parents are
        not correclty written to the mctal file.
        Parameters
        ----------
        output : MCNPoutput
            object representing the MCNP output.
        Returns
        -------
        df : pd.DataFrame
            table of the SDDR at different cooling timesbadi
        """
        res = {}
        mctal = output.mctal
        # Cutom of read of tallies due to errors in the mctal file
        for tally in mctal.tallies:
            tallyres = []
            tnum = int(tally.tallyNumber)

            # -- Get SDDR --
            if tnum == 4:
                for i, time in enumerate(tally.tim):
                    val = tally.getValue(0, 0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0)
                    err = tally.getValue(0, 0, 0, 0, 0, 0, 0, i, 0, 0, 0, 1)

                    # Store
                    time_res = [i+1, val, err]
                    tallyres.append(time_res)

                # Build and store the taly df
                df = pd.DataFrame(tallyres)
                df.columns = ['time', 'sddr', 'err']
                res[str(tnum)] = df

            # -- Parent tracker --
            if tnum in [14, 24]:
                for i in range(tally.nTim):
                    for j in range(tally.nUsr):
                        val = tally.getValue(0, 0, j, 0, 0, 0, 0, i, 0, 0, 0, 0)
                        err = tally.getValue(0, 0, j, 0, 0, 0, 0, i, 0, 0, 0, 1)

                        # Store
                        time_res = [i+1, j, val, err]
                        tallyres.append(time_res)

                # Build and store the taly df
                df = pd.DataFrame(tallyres)
                df.columns = ['time', 'tracked', 'sddr', 'err']
                # The first row is the complementary bin (0) and last row
                # is the total. They can be dropped
                df = df.set_index('tracked').drop([0, j]).reset_index()
                res[str(tnum)] = df

        # --- Override the raw data ---
        # Get the folder and lib
        path = mctal.mctalFileName
        folderpath = os.path.dirname(path)
        folder = os.path.basename(folderpath)
        lib = os.path.basename(os.path.dirname(os.path.dirname(folderpath)))

        self.raw_data[folder, lib] = res

        return res

    def _pp_excel_comparison(self):
        '''
        Responsible for producing excel outputs
        '''
        # Dump the global C/E table
        print(' Dump the C/E table in Excel...')
        ex_outpath = os.path.join(self.excel_path, 'C over E table.xlsx')
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        with pd.ExcelWriter(ex_outpath, engine='xlsxwriter') as writer:
            # --- build and dump the C/E table ---
            for folder in self.names:
                # collect all available data
                alldata = self._get_collected_data(folder)
                exp_err = alldata['Relative Error']
                exp_sddr = alldata['Experimental SDDR [Sv/h]']
                # build the C\E df
                df = pd.DataFrame(index=alldata.index)

                for lib in self.lib[1:]:
                    libname = self.session.conf.get_lib_name(lib)
                    # get computational data
                    com_err = alldata[lib+'err']
                    com_sddr = alldata[lib+'sddr']

                    # compute global error (SRSS)
                    gl_err = ((com_err**2+exp_err**2)**(1/2)).round(2).astype(str)
                    # compute C/E
                    gl_val = (com_sddr/exp_sddr).round(2).astype(str)

                    df[libname] = gl_val+' +/- '+gl_err

                # Dump the df
                df.to_excel(writer, sheet_name=folder, startrow=2)
                # Write description
                ws = writer.sheets[folder]
                ws.write_string(0, 0, '"C/E (mean +/- σ)"')

    def _get_collected_data(self, folder):
        """
        Given a campaign it builds a single table containing all experimental
        and computational data available for the total SDDR tally.
        Parameters
        ----------
        folder : str
            campaign name.
        tally : str
            tally number
        Returns
        -------
        df : pd.DataFrame
            collective data on the campaing.
        """
        idx = ['Cooldown Time [s]', 'Cooldown Time [d]']
        # Initialize the table with the experimental results
        df = self.exp_results[folder]['SDDR'].copy()
        df = df.set_index(idx).sort_index()

        # Avoid exp tag
        for lib in self.lib[1:]:
            libdf = self.results[folder, lib]['4'].set_index('time').sort_index()
            # add the SDDR and relative column of each library
            df[lib+'sddr'] = libdf['sddr'].values
            df[lib+'err'] = libdf['err'].values

        return df

    def _build_atlas(self, tmp_path, atlas):
        """
        Fill the atlas with the customized plots. Creation and saving of the
        atlas are handled elsewhere.
        Parameters
        ----------
        tmp_path : path
            path to the temporary folder where to dump images.
        atlas : Atlas
            Object representing the plot Atlas.
        Returns
        -------
        atlas : Atlas
            After being filled the atlas is returned.
        """
        patzaid = re.compile(r'(?<=[\s\-\t])\d+(?=[\s\t\n])')

        atlas.doc.add_heading('Shut Down Dose Rate', level=1)
        xlabel = 'Cooldown time'
        # Only two plots, one for each irradiation campaign
        for folder, title in zip(self.names, ['1st FNG Irradiation campaign',
                                              '2nd FNG Irradiation campaign']):
            atlas.doc.add_heading(title, level=2)
            # --- SDDR PLOT ---
            # -- Recover data to plot --
            data = []
            x = self.times[folder]
            for lib in self.lib:
                if lib == 'Exp':
                    df = self.exp_results[folder]['SDDR']
                    y = df['Experimental SDDR [Sv/h]'].values
                    err = (df['Relative Error']*y).values
                    ylabel = 'Experiment'
                else:
                    df = self.results[folder, lib]['4'].set_index('time').sort_index()
                    y = df.sddr.values
                    err = df.err.values*y
                    ylabel = self.session.conf.get_lib_name(lib)

                data.append({'x': x, 'y': y, 'err': err, 'ylabel': ylabel})
            # -- Plot --
            outname = 'tmp'
            quantity = 'SDDR'
            unit = 'Sv/h'
            plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                           xlabel, self.testname)
            img_path = plot.plot('Discreet Experimental points')
            # Insert the image in the atlas
            atlas.insert_img(img_path)

            # --- Tracking PLOTs ---
            # -- Recover data to plot --
            # There is the need to recover the tracked parents and daughters
            zaid_tracked = {}
            for lib in self.lib[1:]:
                file = os.path.join(self.test_path[lib], folder, folder)
                inp = D1S_Input.from_text(file)
                for tallynum in ['24', '14']:
                    card = inp.get_card_byID('settings', 'FU'+tallynum)
                    strings = []
                    for line in card.lines:
                        zaids = patzaid.findall(line)
                        for zaid in zaids:
                            if zaid != '0':
                                _, formula = self.session.lib_manager.get_zaidname(zaid)
                                strings.append(formula)

                    zaid_tracked[tallynum] = strings

            x = self.times[folder]
            titles = {'parent': title+', parent isotopes contribution ',
                      'daughter': title+', daughter isotopes contribution '}
            tallynums = {'parent': '24', 'daughter': '14'}

            for tracked in ['parent', 'daughter']:
                atlas.doc.add_heading(tracked+' tracking', level=3)
                for lib in self.lib[1:]:
                    libname = self.session.conf.get_lib_name(lib)

                    # Recover the data
                    tallynum = tallynums[tracked]
                    df = self.results[folder, lib][tallynum]
                    zaidstracked = set(df.tracked.values)
                    tot_dose = df.groupby('time').sum().sddr.values
                    df.set_index('tracked', inplace=True)
                    data = []
                    for i, zaid in enumerate(zaidstracked):
                        subset = df.loc[zaid]
                        assert len(subset.time.values) == len(x)
                        formula = zaid_tracked[tallynum][i]
                        y = subset.sddr.values/tot_dose*100
                        libdata = {'x': x, 'y': y, 'err': [],
                                   'ylabel': formula}
                        data.append(libdata)

                    outname = 'tmp'
                    newtitle = titles[tracked]+libname
                    quantity = 'SDDR contribution'
                    unit = '%'
                    xlabel = 'Cooldown time'

                    plot = Plotter(data, newtitle, tmp_path, outname,
                                   quantity, unit, xlabel, self.testname)
                    img_path = plot._contribution(legend_outside=True)

                    # Insert the image in the atlas
                    atlas.insert_img(img_path)

        return atlas

    def _read_exp_file(self, filepath):
        '''
        Override parent method since the separator for these experimental
        files is ";"
        '''
        return pd.read_csv(filepath, sep=';')


class OktavianOutput(ExperimentalOutput):

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """
        maintitle = ' Oktavian Experiment: '
        xlabel = 'Energy [MeV]'

        self.tables = []  # All C/E tables will be stored here and then concatenated

        # Tally numbers should be fixed
        for tallynum in ['21', '41']:
            if tallynum == '21':
                particle = 'Neutron'
                tit_tag = 'Neutron Leakage Current per Unit Lethargy'
                quantity = 'Neutron Leakage Current'
                msg = ' Printing the '+particle+' Letharghy flux...'
                unit = r'$ 1/u\cdot n_s$'
            else:
                particle = 'Photon'
                tit_tag = 'Photon Leakage Current per unit energy'
                quantity = 'Photon Leakage Current'
                msg = ' Printing the '+particle+' spectrum...'
                unit = r'$ 1/MeV\cdot n_s$'

            print(msg)

            atlas.doc.add_heading(quantity, level=1)

            for material in tqdm(self.materials, desc='Materials: '):

                atlas.doc.add_heading('Material: '+material, level=2)

                title = material+maintitle+tit_tag

                # Get the experimental data
                file = 'oktavian_'+material+'_tal'+tallynum+'.exp'
                filepath = os.path.join(self.path_exp_res, material, file)
                columns = {'21': ['Nominal Energy [MeV]', 'Upper Energy [MeV]',
                                  'Lower Energy [MeV]', 'C', 'Error'],
                           '41': ['Nominal Energy [MeV]', 'Lower Energy [MeV]',
                                  'Upper Energy [MeV]', 'C', 'Error']}
                # Skip the tally if no experimental data is available
                if os.path.isfile(filepath) == 0:
                    continue
                else:
                    data = self._data_collect(material, filepath, tallynum,
                                              particle, material, columns)

                # Once the data is collected it is passed to the plotter
                outname = 'tmp'
                plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                               xlabel, self.testname)
                img_path = plot.plot('Experimental points')
                # Insert the image in the atlas
                atlas.insert_img(img_path)

        self.mat_off_list = self.materials
        # Dump the global C/E table
        self._dump_ce_table()

        return atlas

    def _dump_ce_table(self):

        print(' Dump the C/E table in Excel...')
        final_table = pd.concat(self.tables)
        todump = final_table.set_index(['Material', 'Particle', 'Library'])
        ex_outpath = os.path.join(self.excel_path, 'C over E table.xlsx')

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(ex_outpath, engine='xlsxwriter')
        # dump global table
        todump = todump[['Min E', 'Max E', 'C/E', 'Standard Deviation (σ)', ]]

        todump.to_excel(writer, sheet_name='Global')

        # Elaborate table for better output format
        ft = final_table.set_index(['Material'])
        # ft['Energy Range [MeV]'] = (ft['Min E'].astype(str) + ' - ' +
        #                            ft['Max E'].astype(str))
        ft['E-min [MeV]'] = ft['Min E']
        ft['E-max [MeV]'] = ft['Max E']

        ft['C/E (mean +/- σ)'] = (ft['C/E'].round(2).astype(str) + ' +/- ' +
                                  ft['Standard Deviation (σ)'].round(2).astype(str))
        # Delete all confusing columns
        for column in ['Min E', 'Max E', 'C/E', 'Standard Deviation (σ)', ]:
            del ft[column]

        # Dump also table material by material
        for material in self.mat_off_list:
            # dump material table
            todump = ft.loc[material]
            todump = todump.pivot(index=['Particle', 'E-min [MeV]', 
                'E-max [MeV]'], columns='Library', values='C/E (mean +/- σ)')

            todump.sort_values(by=['E-min [MeV]'])

            todump.to_excel(writer, sheet_name=material, startrow=2)
            ws = writer.sheets[material]
            ws.write_string(0, 0, '"C/E (mean +/- σ)"')

            # adjust columns' width
            writer.sheets[material].set_column(0, 4, 18)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
        return

    def _data_collect(self, material, filepath, tallynum, particle,
                      mat_read_file, e_intervals, columns):

        x, y, err = self._read_Oktavian_expresult(filepath, tallynum, columns)

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
                values = self.results[mat_read_file, lib_tag][tallynum]
                lib = {'x': values['Energy [MeV]'],
                       'y': values['C'], 'err': values['Error'],
                       'ylabel': material + ' ('+lib_name+')'}
                data.append(lib)
                # data for the table
                table = _get_tablevalues(
                    values, interpolator, e_intervals=e_intervals)
                table['Particle'] = particle
                table['Material'] = material
                table['Library'] = lib_name
                self.tables.append(table)
            except KeyError:
                # The tally is not defined
                pass
        return data

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

                    mfile, ofile = self._get_output_files(results_path)
                    # Parse output
                    output = MCNPoutput(mfile, ofile)
                    outputs[material, lib] = output
                    # Adjourn raw Data
                    self.raw_data[material, lib] = output.tallydata
                    # Get the meaningful results
                    results[material, lib] = self._processMCNPdata(output)
                    if material not in materials:
                        materials.append(material)

        self.outputs = outputs
        self.results = results
        self.materials = materials

    def _pp_excel_comparison(self):
        # Excel is actually printed by the build atlas in this case
        pass

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

    def _processMCNPdata(self, output):
        """
        given the mctal file the lethargy flux and energies are returned
        both for the neutron and photon tally

        Parameters
        ----------
        output : MCNPoutput
            object representing the MCNP output.

        Returns
        -------
        res : dic
            contains the extracted lethargy flux and energies.

        """
        res = {}
        # Read tally energy binned fluxes
        for tallynum, data in output.tallydata.items():
            tallynum = str(tallynum)
            res2 = res[tallynum] = {}

            # Delete the total value
            data = data.set_index('Energy').drop('total').reset_index()

            flux = data['Value'].values
            energies = data['Energy'].values
            errors = data['Error'].values

            # Energies for lethargy computation
            ergs = [1e-10]  # Additional "zero" energy for lethargy computation
            ergs.extend(energies.tolist())
            ergs = np.array(ergs)

            # Different behaviour for photons and neutrons
            for tally in output.mctal.tallies:
                if tallynum == str(tally.tallyNumber):
                    particle = tally.particleList[np.where(
                        tally.tallyParticles == 1)[0][0]]
            if particle == 'Neutron':
                flux = flux/np.log((ergs[1:]/ergs[:-1]))
            elif particle == 'Photon':
                flux = flux/(ergs[1:]-ergs[:-1])

            res2['Energy [MeV]'] = energies
            res2['C'] = flux
            res2['Error'] = errors

            res[tallynum] = res2

        return res

    def _read_Oktavian_expresult(self, file, tallynum, columns):
        """
        Given a file containing the Oktavian experimental results read it and
        return the values to plot.

        The values equal to 1e-38 are eliminated since it appears that they
        are the zero values of the instrument used.

        Parameters
        ----------
        file : os.Path or str
            path to the file to be read.
        tallynum : str
            either '21' or '41'. the data is different for neutrons and
            photons

        Returns
        -------
        x : np.array
            energy values.
        y : np.array
            lethargy flux values.

        """
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
        df.columns = columns[tallynum]
        df = df[df['C'] > 2e-38]

        x = df['Nominal Energy [MeV]'].values
        y = df['C'].values

        err = df['Error'].values

        return x, y, err

    def _read_exp_results(self):
        """
        This is an older implementation and the reading was done somewhere
        else

        """
        pass


class TiaraBCOutput(OktavianOutput):

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """

        # Set plot axes details
        maintitle = ' Tiara Experiment: '
        xlabel = 'Energy [MeV]'
        particle = 'Neutron'
        tit_tag = 'Neutron Yield per Unit Lethargy'
        quantity = 'Yield per lethargy'
        msg = ' Printing the '+particle+' Letharghy flux...'
        unit = r'$ 1/u$'

        self.tables = []  # All C/E tables will be stored here and then concatenated
        mat_off_list = []
        print(msg)

        # Loop over benchmark cases
        for material in tqdm(self.materials, desc='Materials: '):
            # Loop over tallies
            for tally in self.outputs[(material, self.lib[1])].mctal.tallies:
                # Get tally number and info
                tallynum = tally.tallyNumber
                comment = str(tally.tallyComment)
                # Assign on/off axis value
                if 'on-axis' in comment:
                    offaxis_str = '00'
                    string_off_axis = 'on-axis'
                elif '20' in comment:
                    offaxis_str = '20'
                    string_off_axis = '20 cm off-axis'
                elif '40' in comment:
                    offaxis_str = '40'
                    string_off_axis = '40 cm off-axis'
                
                # Assign shielding material
                if material.split('-')[0] == 'cc':
                    material_name = 'Concrete'
                elif material.split('-')[0] == 'fe':
                    material_name = 'Iron'

                # Set title and header
                atlas.doc.add_heading('Material: ' + material_name + ', ' 
                    + material.split('-')[2] + ' cm, ' + material.split('-')[1] 
                    + ' MeV, ' + 'Additional collimator: ' + material.split('-'
                    )[3] + ' cm, ' + string_off_axis, level=2)
                title = '\n' + maintitle + tit_tag  
                # + ', '+'\nMaterial: ' + material_name + ', ' material.split('-')[2] + ' cm, ' + material.split(
                # '-')[1] + ' MeV, ' + 'Additional collimator: ' + material.split('-')[3] + ' cm, ' + string_off_axis + '\n'
                
                # Open the correspondent experimental data file
                mat_off_list.append(material + '-' + offaxis_str)
                file = 'Tiara-BC_' + material + '-' + offaxis_str + '.exp'
                filepath = os.path.join(self.path_exp_res, material + '-' +
                                        offaxis_str, file)
                columns = {'14': ['Nominal Energy [MeV]', 'C', 'Error'],
                           '24': ['Nominal Energy [MeV]', 'C', 'Error'],
                           '34': ['Nominal Energy [MeV]', 'C', 'Error']}
                # Skip the tally if no experimental data is available
                if os.path.isfile(filepath) == 0:
                    continue
                else:
                    # Collect data
                    data = self._data_collect(material + '-' + offaxis_str,
                        filepath, str(tallynum), particle, material,
                        e_intervals=[3.5, 10, 20, 30, 40, 50, 60, 70],
                        columns=columns)
                # Once the data is collected it is passed to the plotter
                outname = 'tmp'
                plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                               xlabel, self.testname)
                img_path = plot.plot('Experimental points')
                # Insert the image in the atlas
                atlas.insert_img(img_path)

        self.mat_off_list = mat_off_list
        # Dump C/E table
        self._dump_ce_table()

        return atlas


def _get_tablevalues(df, interpolator, x='Energy [MeV]', y='C',
                     e_intervals=[0.1, 1, 5, 10, 20]):
    """
    Given the benchmark and experimental results returns a df to compile the
    C/E table for energy intervals

    Parameters
    ----------
    df : dict
        benchmark data.
    interpolator : func
        interpolator from experimental data.
    x : str, optional
        x column. The default is 'Energy [MeV]'.
    y : str, optional
        y columns. The default is 'C'.
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
    # it is better here to drop inf values because it means that the
    # interpolated experiment was zero, i.e., no value available
    df.replace([np.inf, -np.inf], np.nan, inplace=True)  # replace inf with NaN
    df.dropna(subset=['C/E'], how='all', inplace=True)  # drop the inf rows

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


class TiaraOutput(OktavianOutput):

    def _processMCNPdata(self, output):

        return None

    def _case_tree_df_build(self):
        case_tree_dict = {}

        # Loop over libraries
        for lib in self.lib[1:]:
            # Declare empty dataframes
            case_tree = pd.DataFrame()
            for cont, case in enumerate(self.materials):
                # Get data from benchmark's cases' names
                mat_name_list = case.split('-')
                if mat_name_list[0] == 'cc':
                    case_tree.loc[cont, 'Shield Material'] = 'Concrete'
                elif mat_name_list[0] == 'fe':
                    case_tree.loc[cont, 'Shield Material'] = 'Iron'
                case_tree.loc[cont, 'Energy'] = int(mat_name_list[1])
                case_tree.loc[cont, 'Shield Thickness'] = int(mat_name_list[2])
                case_tree.loc[cont, 'Additional Collimator'] = int(
                    mat_name_list[3])
                
                # Put tally values in dataframe
                for tally in self.outputs[(case, lib)].mctal.tallies:
                    case_tree.loc[cont, tally.tallyComment] = self.raw_data[(
                        case, lib)][tally.tallyNumber].iloc[-1]['Value']
                    case_tree.loc[cont, str(tally.tallyComment[0]) + ' Error'
                        ] = self.raw_data[(case, lib)][tally.tallyNumber
                        ].iloc[-1]['Error']
            # Sort data in dataframe and assign to variable
            case_tree.sort_values(['Shield Material', 'Energy', 
                'Shield Thickness', 'Additional Collimator'], inplace=True)
            case_tree_dict[lib] = case_tree
        return case_tree_dict

    def exp_comp_case_check(self):
        """
        Removes experimental data which don't have correspondent mcnp inputs

        """
        comp_data = self.case_tree_dict[self.lib[1]]
        # Loop over benchmark cases
        for shield_material in comp_data['Shield Material'].unique().tolist():
            for energy in comp_data['Energy'].unique().tolist():
                # Get temporary dataframes
                data_list = comp_data.loc[(comp_data['Energy'] == energy) & 
                    (comp_data['Shield Material'] == shield_material)].copy()
                exp_data_list = self.exp_data.loc[(self.exp_data['Energy'] == 
                    energy) & (self.exp_data['Shield Material'] == 
                    shield_material)].copy()

                # Delete experimental data
                for index, row in exp_data_list.iterrows():
                    if row['Shield Thickness'] not in data_list[
                                                    'Shield Thickness'].values:
                        self.exp_data = self.exp_data[~((self.exp_data['Energy']
                            == energy) & (self.exp_data['Shield Material'] == 
                            shield_material) & (self.exp_data['Shield Thickness']
                            == row['Shield Thickness']))]
        return


class TiaraFCOutput(TiaraOutput):

    def _pp_excel_comparison(self):
        
        # Get computational data structure for each library
        self.case_tree_dict = self._case_tree_df_build()

        # Discard experimental data without a correspondent computational data
        self.exp_comp_case_check()

        # Copy computational and experimental data to be manipulated and put into the tables
        comp_data = pd.DataFrame()
        for idx, values in self.case_tree_dict.items():
            temp_df = values.copy()
            temp_df['Library'] = self.session.conf.get_lib_name(idx)
            comp_data = comp_data.append(temp_df, ignore_index=True)
        exp_data = self.exp_data.copy()

        # Match column names in experimental and computational dataframe
        column_name_list = ['U238 on Value', 'U238 on Error', 'Th232 on Value', 
            'Th232 on Error', 'U238 off Value','U238 off Error', 
            'Th232 off Value', 'Th232 off Error']
        on_ax_dict = {0: 'on', 20: 'off'}
        comp_data.rename(columns = dict(zip(comp_data.columns[4:-1], 
            column_name_list)), inplace=True)
        exp_data.rename(columns=dict(zip(exp_data.columns[3:], 
            comp_data.columns.to_list()[4:-1])), inplace=True)
        
        # Build ExcelWriter object
        filepath = self.excel_path + '\\Tiara_Fission_Cells_CE_tables.xlsx'
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        
        # Create 1 worksheet for each energy/material combination
        for shield_material in comp_data['Shield Material'].unique().tolist():
            for energy in comp_data['Energy'].unique().tolist():
                
                # Drop unnecessary columns from exp/computational dataframes
                comp_data_worksheet = comp_data[(comp_data['Energy'] == energy) 
                    & (comp_data['Shield Material'] == shield_material)].copy()
                exp_data_worksheet = exp_data[(exp_data['Energy'] == energy)
                    & (exp_data['Shield Material'] == shield_material)].copy()
                comp_data_worksheet.drop(['Energy', 'Shield Material', 
                    'Additional Collimator'], axis=1, inplace=True)
                exp_data_worksheet.drop(['Energy', 'Shield Material'], axis=1, 
                    inplace=True)
                
                # Set MultiIndex structure of the table
                # Set column names
                column_names = []
                for fission_cell in ['U238', 'Th232']:
                    column_names.append(('Exp', fission_cell, 'Value'))
                    column_names.append(('Exp', fission_cell, 'Error'))
                for lib in comp_data['Library'].unique().tolist():
                    for fission_cell in ['U238', 'Th232']:
                        column_names.append((lib, fission_cell, 'Value'))
                        column_names.append((lib, fission_cell, 'Error'))
                        column_names.append((lib, fission_cell, 'C/E'))
                column_index = pd.MultiIndex.from_tuples(column_names, 
                    names = ['Library', 'Fission Cell', ''])
                # Set row indexes
                row_idx_list = []
                for on_ax in on_ax_dict.keys():
                    thick_list = comp_data_worksheet['Shield Thickness'
                        ].unique().tolist()
                    for shield_thickness in thick_list:
                        row_idx_list.append((shield_thickness, on_ax))
                row_idx = pd.MultiIndex.from_tuples(row_idx_list, 
                    names = ['Shield Thickness','Axis Offset'])

                # Build new dataframe with desired multindex structure
                new_dataframe = pd.DataFrame(index = row_idx,
                    columns = column_index)

                # Fill the new dataframe with proper values
                for i, col in enumerate(new_dataframe.columns.to_list()):
                    for j, idx in enumerate(new_dataframe.index.to_list()):
                        
                        value_string = col[1] + ' ' + on_ax_dict[idx[1]
                            ] + ' ' + col[2]
                        if col[0] == 'Exp':
                            new_dataframe.iloc[j, i] = exp_data_worksheet.loc[
                                exp_data_worksheet['Shield Thickness'] == idx[0]
                                ][value_string].values[0]

                        else:
                            if col[2] == 'C/E':
                                value_string = col[1] + ' ' + on_ax_dict[idx[1]
                                    ] + ' ' + 'Value'
                                new_dataframe.iloc[j, i] = comp_data_worksheet.loc[
                                    (comp_data_worksheet['Library'] == col[0]) & 
                                    (comp_data_worksheet['Shield Thickness'] == 
                                    idx[0])][value_string].values[0
                                    ] / exp_data_worksheet.loc[
                                    exp_data_worksheet['Shield Thickness'] == 
                                    idx[0]][value_string].values[0]
                            else:
                                new_dataframe.iloc[j, i] = comp_data_worksheet.loc[
                                    (comp_data_worksheet['Library'] == col[0]) & 
                                    (comp_data_worksheet['Shield Thickness'] == 
                                    idx[0])][value_string].values[0]

                # Assign worksheet title and put into Excel
                sheet_name='Tiara FC {}, {} MeV'.format(shield_material, 
                    str(energy)) 
                new_dataframe.to_excel(writer, sheet_name = sheet_name)
        # Close the Pandas Excel writer object and output the Excel file
        writer.save()

    def _read_exp_results(self):
        """
        Reads conderc Excel file
        """

        # Read experimental data from CONDERC Excel file
        filepath = (self.path_exp_res + 
                    '\\FC_BS_Experimental-results-CONDERC.xlsx')
        FC_data = {('fe', '43'): pd.read_excel(filepath, 
                                                sheet_name='Fission cell', 
                                                usecols="A:E", 
                                                skiprows=2, 
                                                nrows=10),
                   ('fe', '68'): pd.read_excel(filepath, 
                                                sheet_name='Fission cell', 
                                                usecols="A:E", 
                                                skiprows=16, 
                                                nrows=10),
                   ('cc', '43'): pd.read_excel(filepath, 
                                                sheet_name='Fission cell', 
                                                usecols="A:E", 
                                                skiprows=30, 
                                                nrows=8),
                   ('cc', '68'): pd.read_excel(filepath, 
                                                sheet_name='Fission cell', 
                                                usecols="A:E", 
                                                skiprows=42, 
                                                nrows=8)}
        # Build experimental dataframe
        exp_data = pd.DataFrame()
        for idx, element in FC_data.items():
            # Build a first useful structure from CONDERC data
            if idx[0] == 'cc':
                element['Shield Material'] = 'Concrete'
            elif idx[0] == 'fe':
                element['Shield Material'] = 'Iron'

            element['Energy'] = int(idx[1])
            element[["Shield Thickness", "Axis offset"]
                    ] = element['Fission c./Position (shield t., axis offset)'
                    ].str.split(",", expand=True)
            element['Shield Thickness'] = element['Shield Thickness'].astype(
                'int')
            element['Axis offset'] = element['Axis offset'].astype('int')
            element.drop('Fission c./Position (shield t., axis offset)', 
                axis=1, inplace=True)
            # Move columns and sort values
            columns = element.columns.tolist()
            columns = columns[-4:] + columns[:-4]
            element = element[columns]
            element.sort_values(
                ['Shield Material', 'Energy', 'Axis offset', 'Shield Thickness'],
                inplace=True)
            exp_data = exp_data.append(element[columns], ignore_index=True)
        
        # Build new experimental dataframe with proper column names and structure
        # Move off-axis data to new columns (needed in _build_atlas routine)
        new_exp_data = pd.DataFrame()
        temp_df = pd.DataFrame()
        cont = 0
        for shield_material in exp_data['Shield Material'].unique().tolist():
            for energy in exp_data['Energy'].unique().tolist():

                # Build temporary dataframe to be manipulated
                temp_df = exp_data.loc[(exp_data['Energy'] == energy) & 
                    (exp_data['Shield Material'] == shield_material)].copy()
                thick_list = temp_df['Shield Thickness'].unique().tolist()

                # Loop over shield thicknesses of each energy/material combination
                for shield_thickness in thick_list:
                    new_exp_data.loc[cont, 'Energy'] = energy
                    new_exp_data.loc[cont, 'Shield Material'] = shield_material
                    new_exp_data.loc[cont,'Shield Thickness'] = shield_thickness
                    ax_off_list = temp_df.loc[temp_df['Shield Thickness'] == 
                        shield_thickness]['Axis offset'].unique().tolist()

                    # Move off axis data to new columns
                    for axis_off in ax_off_list:

                        # Put the proper values in the new dataframe
                        if axis_off == 0:
                            new_exp_data.loc[cont, 
                                'On-axis 238U FC'] = temp_df.loc[(
                                temp_df['Shield Thickness'] == shield_thickness)
                                & (temp_df['Axis offset'] == axis_off)][
                                '238 U [/1e24]'].iloc[0] * 1e24
                            new_exp_data.loc[cont, 
                                'On-axis 238U FC Error'] = temp_df.loc[(
                                temp_df['Shield Thickness'] == shield_thickness
                                ) & (temp_df['Axis offset'] == axis_off)][
                                'err [%]'].iloc[0] / 100
                            new_exp_data.loc[cont, 'On-axis 232Th FC'
                                ] = temp_df.loc[(temp_df['Shield Thickness'] == 
                                shield_thickness) & (temp_df['Axis offset'] == 
                                axis_off)]['232 Th [/1e24]'].iloc[0] * 1e24
                            new_exp_data.loc[cont, 'On-axis 232Th FC Error'
                                ] = temp_df.loc[(temp_df['Shield Thickness'] == 
                                shield_thickness) & (temp_df['Axis offset'] ==
                                axis_off)]['err [%].1'].iloc[0] / 100

                        if axis_off == 20:
                            new_exp_data.loc[cont, '20 cm off-axis 238U FC'
                                ] = temp_df.loc[(temp_df['Shield Thickness'] == 
                                shield_thickness) & (temp_df['Axis offset'] == 
                                axis_off)]['238 U [/1e24]'].iloc[0] * 1e24
                            new_exp_data.loc[cont, 
                                '20 cm off-axis 238U FC Error'] = temp_df.loc[(
                                temp_df['Shield Thickness'] == shield_thickness)
                                & (temp_df['Axis offset'] == axis_off)][
                                'err [%]'].iloc[0] / 100
                            new_exp_data.loc[cont, '20 cm off-axis 232Th FC'
                                ] = temp_df.loc[(temp_df['Shield Thickness'] ==
                                shield_thickness) & (temp_df['Axis offset'] ==
                                axis_off)]['232 Th [/1e24]'].iloc[0] * 1e24
                            new_exp_data.loc[cont, 
                                '20 cm off-axis 232Th FC Error'] = temp_df.loc[(
                                temp_df['Shield Thickness'] == shield_thickness)
                                & (temp_df['Axis offset'] == axis_off)][
                                'err [%].1'].iloc[0] / 100
                    cont += 1

        # Assign exp data variable
        self.exp_data = new_exp_data

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """
        
        # Set plot and axes details
        unit = '-'
        quantity = ['On-axis C/E', 'Off-axis 20 cm C/E']
        xlabel = 'Shield thickness [cm]'
        
        # Get computational data
        comp_data = self.case_tree_dict[self.lib[1]]

        # Loop over shield material/energy combinations
        for shield_material in comp_data['Shield Material'].unique().tolist():

            for energy in comp_data['Energy'].unique().tolist():
                # Put proper data in data dict to be sent to plotter
                data_U_p = []
                data_Th_p = []
                data_list = comp_data.loc[(comp_data['Energy'] == energy) & 
                    (comp_data['Shield Material'] == shield_material)]
                x = np.array(data_list['Shield Thickness'].unique().tolist())

                y_U = []
                y_Th = []
                err_U = []
                err_Th = []
                
                # Get experimental data
                en_mat_exp_dat = self.exp_data.loc[(self.exp_data['Energy'] ==
                    energy) & (self.exp_data['Shield Material'] ==
                    shield_material)]
                
                # This part can be modified to make it nicer...
                y_U.append(en_mat_exp_dat['On-axis 238U FC'].to_numpy())
                y_U.append(en_mat_exp_dat['20 cm off-axis 238U FC'].to_numpy())
                err_U.append(
                    en_mat_exp_dat['On-axis 238U FC Error'].to_numpy())
                err_U.append(
                    en_mat_exp_dat['20 cm off-axis 238U FC Error'].to_numpy())
                y_Th.append(en_mat_exp_dat['On-axis 232Th FC'].to_numpy())
                y_Th.append(
                    en_mat_exp_dat['20 cm off-axis 232Th FC'].to_numpy())
                err_Th.append(
                    en_mat_exp_dat['On-axis 232Th FC Error'].to_numpy())
                err_Th.append(
                    en_mat_exp_dat['20 cm off-axis 232Th FC Error'].to_numpy())

                # Append experimental data
                ylabel = 'Experiment'
                data_U = {'x': x, 'y': y_U, 'err': err_U, 'ylabel': ylabel}
                data_Th = {'x': x, 'y': y_Th, 'err': err_Th, 'ylabel': ylabel}
                data_U_p.append(data_U)
                data_Th_p.append(data_Th)

                # Loop over libraries
                for lib in self.lib[1:]:
                    # Get proper computational data
                    ylabel = self.session.conf.get_lib_name(lib)
                    mcnp_data = self.case_tree_dict[lib]
                    mcnp_thick_data = mcnp_data.loc[(mcnp_data['Energy'] ==
                    energy) & (mcnp_data['Shield Material'] == shield_material)]

                    # Save proper computational data in variables
                    x = np.array(
                        mcnp_thick_data['Shield Thickness'].unique().tolist())
                    y_U = []
                    y_Th = []
                    err_U = []
                    err_Th = []
                    y_U.append(mcnp_thick_data['On-axis 238U FC'].to_numpy())
                    y_U.append(mcnp_thick_data['20 cm off-axis 238U FC'
                        ].to_numpy())
                    err_U.append(mcnp_thick_data['On-axis 238U FC Error'
                        ].to_numpy())
                    err_U.append(mcnp_thick_data['20 cm off-axis 238U FC Error'
                        ].to_numpy())
                    y_Th.append(mcnp_thick_data['On-axis 232Th FC'].to_numpy())
                    y_Th.append(mcnp_thick_data['20 cm off-axis 232Th FC'
                        ].to_numpy())
                    err_Th.append(mcnp_thick_data['On-axis 232Th FC Error'
                        ].to_numpy())
                    err_Th.append(mcnp_thick_data[
                        '20 cm off-axis 232Th FC Error'].to_numpy())

                    # Append computational data to data dict
                    data_U = {'x': x, 'y': y_U, 'err': err_U, 'ylabel': ylabel}
                    data_Th = {'x': x, 'y': y_Th,
                               'err': err_Th, 'ylabel': ylabel}
                    data_U_p.append(data_U)
                    data_Th_p.append(data_Th)
                    fission_cell = ['Uranium-238', 'Thorium-232']

                for cont, data in enumerate([data_U_p, data_Th_p]):
                    # Set title and send to plotter
                    title = 'Tiara Experiment: {} Fission Cell detector,\nEnergy: {} MeV, Shield material: {}'.format(fission_cell[cont], str(energy), shield_material)
                    outname = 'tmp'
                    plot = Plotter(data, title, tmp_path, outname, quantity, 
                        unit, xlabel, self.testname)
                    img_path = plot.plot('Waves')
                    atlas.insert_img(img_path)
        return atlas


class TiaraBSOutput(TiaraOutput):

    def _pp_excel_comparison(self):
        """
        This method prints Tiara C/E tables for Bonner Spheres detectors
        """

        # Get main dataframe with computational data of all cases, their data and respective tallies, for each library

        self.case_tree_dict = self._case_tree_df_build()

        # Discard experimental data without correspondent computational data

        self.exp_comp_case_check()

        # Build copies of computational and experimental dataframes
        # They'll be manipulated to obtain Tiara's paper's tables

        comp_data = pd.DataFrame()
        for idx, values in self.case_tree_dict.items():
            temp_df = values.copy()
            temp_df['Library'] = self.session.conf.get_lib_name(idx)
            comp_data = comp_data.append(temp_df, ignore_index=True)

        exp_data = self.exp_data.copy()
        exp_data.rename(columns=dict(zip(exp_data.columns[-5:], 
            comp_data.columns.to_list()[4:-2:2])), 
            inplace=True)

        # Create ExcelWriter object

        filepath = self.excel_path + '\\Tiara_Bonner_Spheres_CE_tables.xlsx'
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

        

        for shield_material in comp_data['Shield Material'].unique().tolist():
            for energy in comp_data['Energy'].unique().tolist():

                # Select proper shield material/energy combination, discard columns which are not necessary

                comp_data_worksheet = comp_data[(comp_data['Energy'] == energy) 
                    & (comp_data['Shield Material'] == shield_material)].copy()
                exp_data_worksheet = exp_data[(exp_data['Energy'] == energy) &
                    (exp_data['Shield Material'] == shield_material)].copy()
                comp_data_worksheet.drop(['Energy', 'Shield Material', 
                    'Additional Collimator'], axis=1, inplace=True)
                exp_data_worksheet.drop(['Energy', 'Shield Material'], axis=1, 
                    inplace=True)

                # Build MultiIndex structure for the tables

                column_names = []
                thick_list = comp_data_worksheet['Shield Thickness'
                    ].unique().tolist()

                for shield_thickness in thick_list:
                    column_names.append(('Exp', shield_thickness, 'Value'))

                for lib in comp_data['Library'].unique().tolist():
                    for thickness in thick_list:
                        column_names.append((lib, thickness, 'Value'))
                        column_names.append((lib, thickness, 'Error'))
                        column_names.append((lib, thickness, 'C/E'))

                index = pd.MultiIndex.from_tuples(column_names, 
                    names=['Library', 'Shield Thickness', ''])

                # Create new dataframe with the MultiIndex structure

                new_dataframe = pd.DataFrame(index = 
                    comp_data_worksheet.columns.to_list()[1:-1:2], columns = 
                    index)
                
                # Add the proper values in the new dataframe with MultiIndex structure

                for i, col in enumerate(new_dataframe.columns.to_list()):

                    for j, idx in enumerate(new_dataframe.index.to_list()):

                        if col[0] == 'Exp':
                            new_dataframe.iloc[j, i] = exp_data_worksheet.loc[
                                exp_data_worksheet['Shield Thickness'] == 
                                col[1]][idx].values[0]

                        else:

                            if col[2] == 'Value' or col[2] == 'C/E':
                                add_string = ''
                            else:
                                add_string = ' Error'
                            if col[2] != 'C/E':
                                new_dataframe.iloc[j, i] = comp_data_worksheet.loc[
                                    (comp_data_worksheet['Library'] == col[0]) &
                                    (comp_data_worksheet['Shield Thickness'] == 
                                    col[1])][idx + add_string].values[0]

                            else:
                                new_dataframe.iloc[j, i] = comp_data_worksheet.loc[
                                    (comp_data_worksheet['Library'] == col[0]) &
                                    (comp_data_worksheet['Shield Thickness'] == 
                                    col[1])][idx + add_string].values[0
                                    ] / exp_data_worksheet.loc[
                                    exp_data_worksheet['Shield Thickness'] == 
                                    col[1]][idx].values[0]

                # Print the dataframe in a worksheet in Excel file

                new_dataframe.to_excel(writer, 
                    sheet_name='Tiara {}, {} MeV' .format(shield_material, 
                    str(energy)))

        # Close the Pandas Excel writer object and output the Excel file

        writer.save()
        pass

    def _read_exp_results(self):
        """
        Reads conderc Excel file

        """

        # Get experimental data filepath

        filepath = self.path_exp_res + '\\FC_BS_Experimental-results-CONDERC.xlsx'

        # Read exp data from CONDERC excel file

        BS_data = {('fe', '43'): pd.read_excel(filepath, 
                                                sheet_name = 'Bonner sphere',
                                                usecols="A:F", skiprows=2, 
                                                nrows=3),
                   ('fe', '68'): pd.read_excel(filepath, 
                                                sheet_name = 'Bonner sphere', 
                                                usecols="A:F", skiprows=9, 
                                                nrows=3),
                   ('cc', '43'): pd.read_excel(filepath, 
                                                sheet_name = 'Bonner sphere', 
                                                usecols="A:F", skiprows=16, 
                                                nrows=4),
                   ('cc', '68'): pd.read_excel(filepath, 
                                                sheet_name = 'Bonner sphere', 
                                                usecols="A:F", skiprows=24, 
                                                nrows=3)}
        
        for key, value in BS_data.items():
            if key[0] == 'cc':
                value['Shield Material'] = 'Concrete'
            if key[0] == 'fe':
                value['Shield Material'] = 'Iron'
            value['Energy'] = int(key[1])

        exp_data = pd.DataFrame()
        for value in BS_data.values():
            exp_data = exp_data.append(value, ignore_index=True)

        # Adjust experimental data dataframe's structure

        columns = exp_data.columns.tolist()
        columns = columns[-2:] + columns[:-2]
        exp_data = exp_data[columns]
        exp_data.rename(columns = {'Polyethylene t./Shield t.': 
            'Shield Thickness'}, inplace=True)
        exp_data.sort_values(['Shield Material', 'Energy', 'Shield Thickness'], 
            inplace=True)

        # Save experimental data

        self.exp_data = exp_data

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """
        
        # Set plot axes

        unit = '-'
        quantity = ['C/E']
        xlabel = 'Bonner Sphere Radius [mm]'
        x = ['Bare', '15', '30', '50', '90']
        
        # Loop over all benchmark cases (materials)

        for material in tqdm(self.materials, desc='Materials: '):

            # Get benchmark properties

            data = []
            mat_item_list = material.split('-')
            shield_material = mat_item_list[0]

            if shield_material == 'cc':
                shield_material = 'Concrete'
            elif shield_material == 'fe':
                shield_material = 'Iron'

            energy = int(mat_item_list[1])
            shield_thickness = int(mat_item_list[2])

            # Get experimental data and errors for the selected benchmark case

            y = [self.exp_data.loc[(self.exp_data['Energy'] == energy) &
                (self.exp_data['Shield Thickness'] == shield_thickness) &
                (self.exp_data['Shield Material'] == shield_material)
                ].iloc[:, -5:].to_numpy()[0]]
            err = [np.zeros(len(y))]
            
            # Append experimental data to data list (sent to plotter)

            ylabel = 'Experiment'
            data_p = {'x': x, 'y': y, 'err': err, 'ylabel': ylabel}
            data.append(data_p)

            # Loop over selected libraries

            for lib in self.lib[1:]:

                # Get library name, assign title to the plot

                ylabel = self.session.conf.get_lib_name(lib)
                title = 'Tiara Experiment: Bonner Spheres detector,\nEnergy: ' + \
                    str(energy) + ' MeV, Shield material: ' + shield_material + \
                    ', Shield thickness: ' + str(shield_thickness) + ' cm'

                # Get computational data and errors for the selected benchmark case

                y = [self.case_tree_dict[lib].loc[
                    (self.case_tree_dict[lib]['Energy'] == energy) &
                    (self.case_tree_dict[lib]['Shield Thickness'] == 
                    shield_thickness) & (self.case_tree_dict[lib][
                    'Shield Material'] == shield_material)].iloc[:, 4::2
                    ].to_numpy()[0]]
                err = [self.case_tree_dict[lib].loc[(self.case_tree_dict[lib][
                    'Energy'] == energy) & (self.case_tree_dict[lib][
                    'Shield Thickness'] == shield_thickness) & 
                    (self.case_tree_dict[lib]['Shield Material'] == 
                    shield_material)].iloc[:, 5::2].to_numpy()[0]]

                # Append computational data to data list (sent to plotter)

                data_p = {'x': x, 'y': y, 'err': err, 'ylabel': ylabel}
                data.append(data_p)

            # Send data to plotter

            outname = 'tmp'
            plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                           xlabel, self.testname)
            img_path = plot.plot('Waves')
            atlas.insert_img(img_path)

        return atlas