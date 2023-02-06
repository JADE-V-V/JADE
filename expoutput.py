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
import xlsxwriter

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

    def _dump_ce_table (self):

        print(' Dump the C/E table in Excel...')
        final_table = pd.concat(self.tables)
        todump = final_table.set_index(['Material', 'Particle', 'Library'])
        ex_outpath = os.path.join(self.excel_path, 'C over E table.xlsx')

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(ex_outpath, engine='xlsxwriter')
        # dump global table
        todump = todump[['Min E', 'Max E','C/E','Standard Deviation (σ)',]]

        todump.to_excel(writer, sheet_name='Global')

        # Elaborate table for better output format
        ft = final_table.set_index(['Material'])
        #ft['Energy Range [MeV]'] = (ft['Min E'].astype(str) + ' - ' +
        #                            ft['Max E'].astype(str))
        ft['E-min [MeV]'] = ft['Min E']
        ft['E-max [MeV]'] = ft['Max E']

        ft['C/E (mean +/- σ)'] = (ft['C/E'].round(2).astype(str) + ' +/- ' +
                                  ft['Standard Deviation (σ)'].round(2).astype(str))
        # Delete all confusing columns
        for column in [ 'Min E', 'Max E','C/E', 'Standard Deviation (σ)',]:
            del ft[column]
        
        # Dump also table material by material
        for material in self.mat_off_list:
            # dump material table
            todump = ft.loc[material]
            todump = todump.pivot(index=['Particle', 'E-min [MeV]','E-max [MeV]'],
                                  columns='Library', values='C/E (mean +/- σ)')

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
                table = _get_tablevalues(values, interpolator, e_intervals = e_intervals)
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
                    particle = tally.particleList[np.where(tally.tallyParticles == 1)[0][0]]
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
        for material in tqdm(self.materials, desc='Materials: '):
            for tally in self.outputs[(material, self.lib[1])].mctal.tallies:
                tallynum = tally.tallyNumber
                comment = str(tally.tallyComment)
                if 'on-axis' in comment:
                    offaxis_str = '00'
                    string_off_axis = 'on-axis'
                elif '20' in comment:
                    offaxis_str = '20'
                    string_off_axis = '20 cm off-axis'
                elif '40' in comment:
                    offaxis_str = '40'
                    string_off_axis = '40 cm off-axis'
                if material.split('-')[0] == 'cc':
                    material_name = 'Concrete'
                elif material.split('-')[0] == 'fe':
                    material_name = 'Iron'
                atlas.doc.add_heading('Material: ' + material_name + ', ' + 
                                      material.split('-')[2] + ' cm, ' + 
                                      material.split('-')[1] + ' MeV, ' + 
                                      'Additional collimator: ' + 
                                      material.split('-')[3] + ' cm, ' + 
                                      string_off_axis, level=2)
                title = '\n' + maintitle + tit_tag + ', '+'\nMaterial: Iron, ' + material.split('-')[2] + ' cm, ' + material.split('-')[1] + ' MeV, ' + 'Additional collimator: ' + material.split('-')[3] + ' cm, ' + string_off_axis + '\n'
                    
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
                    data = self._data_collect(material + '-' + offaxis_str,
                                    filepath, str(tallynum), particle, material,
                                    e_intervals=[3.5, 10, 20, 30, 40, 50, 60, 70],
                                    columns = columns)
                # Once the data is collected it is passed to the plotter
                outname = 'tmp'
                plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                               xlabel, self.testname)
                img_path = plot.plot('Experimental points')
                # Insert the image in the atlas
                atlas.insert_img(img_path)

        self.mat_off_list = mat_off_list
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
        for lib in self.lib[1:]:
            case_tree = pd.DataFrame()

            for cont, case in enumerate(self.materials):
                mat_name_list = case.split('-')
                if mat_name_list[0] == 'cc':
                    case_tree.loc[cont, 'Shield Material'] = 'Concrete'
                elif mat_name_list[0] == 'fe':
                    case_tree.loc[cont, 'Shield Material'] = 'Iron'

                case_tree.loc[cont, 'Energy'] = int(mat_name_list[1])
                case_tree.loc[cont, 'Shield Thickness'] = int(mat_name_list[2])
                case_tree.loc[cont, 'Additional Collimator'] = int(mat_name_list[3])

                for tally in self.outputs[(case,lib)].mctal.tallies:
                    case_tree.loc[cont, tally.tallyComment] =  self.raw_data[(case,lib)][tally.tallyNumber].iloc[-1]['Value']
                    case_tree.loc[cont, str(tally.tallyComment[0]) + ' Error'] =  self.raw_data[(case,lib)][tally.tallyNumber].iloc[-1]['Error']
            case_tree.fillna(value=pd.np.nan, inplace=True)
            case_tree.sort_values(['Shield Material', 'Energy', 'Shield Thickness', 'Additional Collimator'])
            case_tree_dict[lib] = case_tree
        return case_tree_dict


class TiaraFCOutput(TiaraOutput):

    def _pp_excel_comparison(self):
        # This method prints FC output tables in Excel
        # Initializing containers
        #case_tree = self._case_tree_df_build()
        # sort_matlist = []
        # sort_dict = {}
        # lib_names = {}
        # exp_data_dict = {}
        # #Create ordered shield thickness list for each energy and material
        # for mat in ['cc','fe']:
        #     for energy in ['43', '68']:
        #         aux_list = []
        #         for material in self.materials:
        #             mat1 = material.split('-')[0]
        #             energy1 = material.split('-')[1]
        #             thickness = int(material.split('-')[2])
        #             if mat == mat1 and energy == energy1:
        #                aux_list.append(thickness)
        #         aux_list.sort()
        #         sort_dict[(mat,energy)] = aux_list
        # # Collect exp data in ordered dict
        # i = 0
        # for mat in ['fe','cc']:
        #     for energy in ['43','68']:
        #         exp_data_dict[(mat,energy)] = i
        #         i += 1
        # #Collect extended name of libraries for better visualization
        # for x in range(0, len(self.lib)):
        #     lib_names[x] = self.name.split('_Vs_')[x]

        # #Create ordered case list
        # for mat in ['cc','fe']:
        #     for energy in ['43', '68']:
        #         for thickness1 in sort_dict[(mat,energy)]:
        #             for material in self.materials:
        #                 mat1 = material.split('-')[0]
        #                 energy1 = material.split('-')[1]
        #                 if mat == mat1 and energy == energy1:
        #                     thickness = int(material.split('-')[2])
        #                     if thickness1 == thickness:
        #                         sort_matlist.append(material)
        
        # #Create Excel tables
        # for energy in ['43', '68']:
        #     for mat in ['cc','fe']:
        #         filepath = self.excel_path + '\\' + self.name + '_' + energy + 'MeV_' + mat + '.xlsx'
        #         if os.path.exists(filepath):
        #             os.remove(filepath)
        #         workbook = xlsxwriter.Workbook(filepath,{'nan_inf_to_errors': True})
        #         worksheet = workbook.add_worksheet()
        #         # Formats and alignment for title and library columns   
        #         merge_format = workbook.add_format({
        #         'align':    'center',
        #         'valign':   'vcenter',
        #         })
        #         title_format = workbook.add_format({
        #         'bold': True,
        #         })
        #         worksheet.merge_range(0,0,0,4, 'Tiara Fission Chambers Benchmark: ' + energy + ' MeV, ' + mat + ' shield', title_format)
        #         worksheet.write(3,1, 'Axis offset')
        #         worksheet.write(3,0, 'Shield thickness')
        #         for counter, lib in enumerate(lib_names.values()):
        #             # Insert Exp data in table
        #             if lib == 'Exp':
        #                 worksheet.merge_range(1,2,1,5, 'Exp', merge_format)
        #                 worksheet.merge_range(2,2,2,3, 'U', merge_format)
        #                 worksheet.merge_range(2,4,2,5, 'Th', merge_format)
        #                 worksheet.write(3,2, 'Value')
        #                 worksheet.write(3,3, 'Error [ % ]')
        #                 worksheet.write(3,4, 'Value')
        #                 worksheet.write(3,5, 'Error [ % ]')
        #             #Insert computational data in table
        #             else:
        #                 worksheet.merge_range(1, 2+counter * 4, 1, 5 + counter * 4, lib, merge_format)
        #                 worksheet.merge_range(2,2  + counter * 4,2,3  + counter * 4, 'U', merge_format)
        #                 worksheet.merge_range(2,4  + counter * 4,2,5  + counter * 4, 'Th', merge_format)
        #                 worksheet.write(3,2 + counter * 4, 'Value')
        #                 worksheet.write(3,3 + counter * 4, 'C/E')
        #                 worksheet.write(3,4 + counter * 4, 'Value')
        #                 worksheet.write(3,5 + counter * 4, 'C/E')


        #         for thick_counter, thickness in enumerate(sort_dict[(mat,energy)]):
        #             worksheet.write(4 + thick_counter, 0, thickness)
        #             worksheet.write(4 + thick_counter, 1, 0)
        #             worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 0, thickness)
        #             worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 1, 20)
                    
        #             for material in sort_matlist:

        #                 mat1 = material.split('-')[0]
        #                 energy1 = material.split('-')[1]

        #                 if mat == mat1 and energy == energy1:
        #                     thickness1 = int(material.split('-')[2])
        #                     if thickness1 == thickness:
        #                         for lib_counter,lib in enumerate(self.lib):
        #                             if lib != 'Exp':
        #                                 exp_df = self.exp_data[exp_data_dict[mat,energy]]
        #                                 if thickness != 130:
        #                                     worksheet.write(4 + thick_counter, 6 + 4 * (lib_counter-1), self.raw_data[(material,lib)][14]['Value'])
        #                                     worksheet.write(4 + thick_counter, 8 + 4 * (lib_counter-1), self.raw_data[(material,lib)][24]['Value'])
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 6 + 4 * (lib_counter-1), self.raw_data[(material,lib)][34]['Value'])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 6 + 4 * (lib_counter-1), '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 8 + 4 * (lib_counter-1), self.raw_data[(material,lib)][44]['Value'])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 8 + 4 * (lib_counter-1), '-')
        #                                     worksheet.write(4 + thick_counter, 7 + 4 * (lib_counter-1), self.raw_data[(material,lib)][14]['Value'] / exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[0]/1e24)
        #                                     worksheet.write(4 + thick_counter, 9 + 4 * (lib_counter-1), self.raw_data[(material,lib)][24]['Value'] / exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[0]/1e24)
        #                                     try:                                     
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 7 + 4 * (lib_counter-1), self.raw_data[(material,lib)][34]['Value'] / exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[1]/1e24)
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 7 + 4 * (lib_counter-1), '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 9 + 4 * (lib_counter-1), self.raw_data[(material,lib)][44]['Value'] /exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[1]/1e24)
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 9 + 4 * (lib_counter-1), '-')
        #                                 else:
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 6 + 4 * (lib_counter-1), self.raw_data[(material,lib)][34]['Value'])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 6 + 4 * (lib_counter-1), '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 8 + 4 * (lib_counter-1), self.raw_data[(material,lib)][44]['Value'])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 8 + 4 * (lib_counter-1), '-')
        #                                     try:                                     
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 7 + 4 * (lib_counter-1), self.raw_data[(material,lib)][34]['Value'] / exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[0]/1e24)
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 7 + 4 * (lib_counter-1), '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 9 + 4 * (lib_counter-1), self.raw_data[(material,lib)][44]['Value'] /exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[0]/1e24)
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 9 + 4 * (lib_counter-1), '-')
        #                             else:
        #                                 exp_df = self.exp_data[exp_data_dict[mat,energy]]
        #                                 if thickness != 130:
        #                                     worksheet.write(4 + thick_counter, 2, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[0])
        #                                     worksheet.write(4 + thick_counter, 4, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[0])
        #                                     worksheet.write(4 + thick_counter, 3, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%]'].values[0])
        #                                     worksheet.write(4 + thick_counter, 5, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%].1'].values[0])
                                            
        #                                     try:                                      
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 2, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[1])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 2, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 4, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[1])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 4, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 3, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%]'].values[1])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 3, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 5, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%].1'].values[1])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 5, '-')
        #                                 else:
        #                                     try:                                      
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 2, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '238 U [/1e24]'].values[0])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 2, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 4, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), '232 Th [/1e24]'].values[0])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 4, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 3, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%]'].values[0])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 3, '-')
        #                                     try:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 5, exp_df.loc[(exp_df['Shield thickness'] == str(thickness)), 'err [%].1'].values[0])
        #                                     except:
        #                                         worksheet.write(4 + thick_counter + len(sort_dict[(mat,energy)]), 5, '-')                                                                             
        #         workbook.close()
        pass

    def _read_exp_results(self):
        """
        Reads conderc Excel file

        """
        filepath = self.path_exp_res +'\\FC_BS_Experimental-results-CONDERC.xlsx'

        FC_data = [pd.read_excel(filepath, sheet_name = 'Fission cell', usecols = "A:E", skiprows = 2, nrows = 10), 
                    pd.read_excel(filepath, sheet_name = 'Fission cell', usecols = "A:E", skiprows = 16, nrows = 10), 
                    pd.read_excel(filepath, sheet_name = 'Fission cell', usecols = "A:E", skiprows = 30, nrows = 8), 
                    pd.read_excel(filepath, sheet_name = 'Fission cell', usecols = "A:E", skiprows = 42, nrows = 8) 
                   ] 
        
        for element in FC_data:
            element[["Shield thickness","Axis offset"]] = element['Fission c./Position (shield t., axis offset)'].str.split(",", expand=True)
        
        self.exp_data = FC_data

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """
        for lib in self.lib[1:]:
            for idx, row in self.case_tree_dict[lib].iterrows():
                plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                               xlabel, self.testname)
                img_path = plot.plot('Waves')
        return

class TiaraBSOutput(TiaraOutput):

    def _pp_excel_comparison(self):
        # This method prints Tiara BS output tables in Excel
        # Initialization of needed containers
        # case_tree = self._case_tree_df_build()
        # sort_matlist = []
        # sort_dict = {}
        # lib_names = {}

        # #Make an ordered dict, to print results in increasing order of thickness
        # for mat in ['cc','fe']:
        #     for energy in ['43', '68']:
        #         aux_list = []
        #         for material in self.materials:
        #             mat1 = material.split('-')[0]
        #             energy1 = material.split('-')[1]
        #             thickness = int(material.split('-')[2])
        #             if mat == mat1 and energy == energy1:
        #                aux_list.append(thickness)
        #         aux_list.sort()
        #         sort_dict[(mat,energy)] = aux_list

        # #Make a list with extended names of libraries, for visualization purposes
        # for x in range(0, len(self.lib)):
        #     lib_names[x] = self.name.split('_Vs_')[x]
        
        # #Produce an ordered list of benchmark cases
        # for mat in ['cc','fe']:
        #     for energy in ['43', '68']:
        #         for thickness1 in sort_dict[(mat,energy)]:
        #             for material in self.materials:
        #                 mat1 = material.split('-')[0]
        #                 energy1 = material.split('-')[1]
        #                 if mat == mat1 and energy == energy1:
        #                     thickness = int(material.split('-')[2])
        #                     if thickness1 == thickness:
        #                         sort_matlist.append(material)
        
        # # For each energy, shield thickness material, produce Excel tables
        # for energy in ['43', '68']:
        #     for mat in ['cc','fe']:
        #         # Name of output file, create output file
        #         filepath = self.excel_path + '\\' + self.name + '_' + energy + 'MeV_' + mat + '.xlsx'
        #         if os.path.exists(filepath):
        #             os.remove(filepath)
        #         workbook = xlsxwriter.Workbook(filepath,{'nan_inf_to_errors': True})
        #         worksheet = workbook.add_worksheet()
        #         # title/alignment formats
        #         merge_format = workbook.add_format({
        #         'align':    'center',
        #         'valign':   'vcenter',
        #         })
        #         title_format = workbook.add_format({
        #         'bold': True,
        #         })
        #         #Create table
        #         worksheet.merge_range(0,0,0,4, 'Tiara Bonner Spheres Benchmark: ' + energy + ' MeV, ' + mat + ' shield', title_format)     
        #         worksheet.write(2,0, 'Polyethylene Thickness/Shield thickness')
        #         worksheet.write(4,0, 'Bare')
        #         worksheet.write(5,0, '15 mm')
        #         worksheet.write(6,0, '30 mm')
        #         worksheet.write(7,0, '50 mm')
        #         worksheet.write(8,0, '90 mm')
        #         for counter_lib, lib in enumerate(self.lib):
        #             # Write Exp data in table
        #             if lib == 'Exp':
        #                 worksheet.merge_range(1,1,1,len(sort_dict[(mat,energy)]), 'Exp', merge_format)                       
        #                 for cont_thick, thickness in enumerate(sort_dict[(mat,energy)]):
        #                     worksheet.write(2, 1 + cont_thick, thickness)
        #                     worksheet.write(4, 1 + cont_thick, self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['Bare'].values[0])
        #                     worksheet.write(5, 1 + cont_thick, self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['15 mm'].values[0])
        #                     worksheet.write(6, 1 + cont_thick, self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['30 mm'].values[0])
        #                     worksheet.write(7, 1 + cont_thick, self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['50 mm'].values[0])
        #                     worksheet.write(8, 1 + cont_thick, self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['90 mm'].values[0])   

        #             else:
        #                 #Write computational data in table
        #                 cont_thick = 0
        #                 worksheet.merge_range(1, 1 + len(sort_dict[(mat,energy)]) + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, 1, 3*len(sort_dict[(mat,energy)]) + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, lib_names[counter_lib], merge_format)
        #                 for thickness in sort_dict[((mat,energy))]:      
        #                     for material in sort_matlist:
        #                         mat1 = material.split('-')[0]
        #                         energy1 = material.split('-')[1]
        #                         thickness1 = int(material.split('-')[2])
        #                         if mat1 == mat and energy1 == energy and thickness1 == thickness:
        #                             #Write computational data
        #                             worksheet.merge_range(2, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, 2, 2 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib  - 1)* len(sort_dict[(mat,energy)])*2, thickness, merge_format)
        #                             worksheet.write(3, 1 +len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, 'Value')
        #                             worksheet.write(4, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][14]['Value'].iloc[-1])
        #                             worksheet.write(5, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][24]['Value'].iloc[-1])
        #                             worksheet.write(6, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][34]['Value'].iloc[-1])
        #                             worksheet.write(7, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1 ) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][44]['Value'].iloc[-1])
        #                             worksheet.write(8, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][54]['Value'].iloc[-1])
        #                     cont_thick += 2

        #                 cont_thick = 1
        #                 for thickness in sort_dict[((mat,energy))]:                         
        #                     for material in sort_matlist:
        #                         mat1 = material.split('-')[0]
        #                         energy1 = material.split('-')[1]
        #                         thickness1 = int(material.split('-')[2])
        #                         if mat1 == mat and energy1 == energy and thickness1 == thickness:
        #                             #Write C/E
        #                             worksheet.write(3, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, 'C/E')
        #                             worksheet.write(4, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][14]['Value'].iloc[-1]/self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['Bare'].values[0])
        #                             worksheet.write(5, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][24]['Value'].iloc[-1]/self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['15 mm'].values[0])
        #                             worksheet.write(6, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][34]['Value'].iloc[-1]/self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['30 mm'].values[0])
        #                             worksheet.write(7, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][44]['Value'].iloc[-1]/self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['50 mm'].values[0])
        #                             worksheet.write(8, 1 + len(sort_dict[(mat,energy)]) + cont_thick + (counter_lib - 1) * len(sort_dict[(mat,energy)])*2, self.raw_data[(material,lib)][54]['Value'].iloc[-1]/self.exp_data[(mat,energy)][self.exp_data[(mat,energy)]['Polyethylene t./Shield t.'] == thickness]['90 mm'].values[0])
        #                     cont_thick += 2
        #         #Create Excel file
        #         workbook.close()
        pass

    def _read_exp_results(self):
        """
        Reads conderc Excel file

        """
        # Get experimental data filepath
        filepath = self.path_exp_res +'\\FC_BS_Experimental-results-CONDERC.xlsx'

        # Read exp data
        BS_data = {('fe', '43') : pd.read_excel(filepath, sheet_name = 'Bonner sphere', usecols = "A:F", skiprows = 2, nrows = 3), 
                    ('fe', '68') : pd.read_excel(filepath, sheet_name = 'Bonner sphere', usecols = "A:F", skiprows = 9, nrows = 3), 
                    ('cc', '43') : pd.read_excel(filepath, sheet_name = 'Bonner sphere', usecols = "A:F", skiprows = 16, nrows = 4), 
                    ('cc', '68') : pd.read_excel(filepath, sheet_name = 'Bonner sphere', usecols = "A:F", skiprows = 24, nrows = 3) 
                   }

        for key, value in BS_data.items():
            if key[0] == 'cc':
               value['Shield Material'] = 'Concrete'
            if key[0] == 'fe':
               value['Shield Material'] = 'Iron'
            value['Energy'] = int(key[1])

        exp_data = pd.DataFrame()
        for value in BS_data.values():
            exp_data = exp_data.append(value, ignore_index = True)
        
        # get the columns in the dataframe
        columns = exp_data.columns.tolist()
        # move the last two columns to the first two positions
        columns = columns[-2:] + columns[:-2]
        # reorder the columns
        exp_data = exp_data[columns]
        exp_data.rename(columns={'Polyethylene t./Shield t.': 'Shield Thickness'}, inplace=True)
        exp_data.sort_values(['Shield Material', 'Energy', 'Shield Thickness'])
        self.exp_data = exp_data

    def _build_atlas(self, tmp_path, atlas):
        """
        See ExperimentalOutput documentation
        """
        self.case_tree_dict = self._case_tree_df_build()
        unit = '-'
        quantity = ['C/E']
        xlabel = 'Bonner Sphere Radius'
        
        x = self.exp_data.columns[-5:].to_numpy()
        
        for material in self.materials:
            data = []
            mat_item_list = material.split('-')
            shield_material = mat_item_list[0]
            if shield_material == 'cc':
                shield_material = 'Concrete'
            elif shield_material == 'fe':
                shield_material = 'Iron'
            energy = int(mat_item_list[1])
            shield_thickness = int(mat_item_list[2])
            try:
                y = [self.exp_data.loc[(self.exp_data['Energy'] == energy) & 
                                        (self.exp_data['Shield Thickness'] == shield_thickness) &
                                        (self.exp_data['Shield Material'] == shield_material)].iloc[:,-5:].to_numpy()[0]]
                err = [np.zeros(len(y))]
                ylabel = 'Experiment'
            except:
                continue
            data_p = {'x': x, 'y': y, 'err': err,
                'ylabel': ylabel}
            data.append(data_p)
            for lib in self.lib[1:]:
                ylabel = self.session.conf.get_lib_name(lib)
                title = 'Tiara Experiment: Bonner Spheres detector,\nEnergy: ' + str(energy) + ' MeV, Shield material: ' + shield_material + ', Shield thickness: ' + str(shield_thickness) + ' cm'
                 
                try:
                    y = [self.case_tree_dict[lib].loc[(self.case_tree_dict[lib]['Energy'] == energy) & 
                                        (self.case_tree_dict[lib]['Shield Thickness'] == shield_thickness) &
                                        (self.case_tree_dict[lib]['Shield Material'] == shield_material)].iloc[:, 4::2].to_numpy()[0]]
                    err = [self.case_tree_dict[lib].loc[(self.case_tree_dict[lib]['Energy'] == energy) & 
                                        (self.case_tree_dict[lib]['Shield Thickness'] == shield_thickness) &
                                        (self.case_tree_dict[lib]['Shield Material'] == shield_material)].iloc[:, 5::2].to_numpy()[0]]
                    data_p = {'x': x, 'y': y, 'err': err, 'ylabel': ylabel}
                    data.append(data_p)
                except KeyError:
                    continue
            outname = 'tmp'
            plot = Plotter(data, title, tmp_path, outname, quantity, unit,
                               xlabel, self.testname)
            img_path = plot.plot('Waves')
            atlas.insert_img(img_path)      
        return atlas
        

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
        return None