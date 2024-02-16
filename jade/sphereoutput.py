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

import sys
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import jade.excelsupport as exsupp
import pandas as pd
import os
import shutil
import jade.plotter as plotter

# import pythoncom
import math

# import openpyxl
# from openpyxl.utils.dataframe import dataframe_to_rows
from tqdm import tqdm
import jade.atlas as at
import numpy as np
from jade.output import BenchmarkOutput
from jade.output import MCNPoutput
from jade.output import OpenMCOutput


class SphereOutput(BenchmarkOutput):
    def __init__(self, lib, config, session):
        super().__init__(lib, config, session)

        # Load the settings for zaids and materials
        mat_path = os.path.join(self.cnf_path, "MaterialsSettings.csv")
        self.mat_settings = pd.read_csv(mat_path, sep=",").set_index("Symbol")

        zaid_path = os.path.join(self.cnf_path, "ZaidSettings.csv")
        self.zaid_settings = pd.read_csv(zaid_path, sep=",").set_index("Z")

    def single_postprocess(self):
        """
        Execute the full post-processing of a single library (i.e. excel,
        raw data and atlas)

        Returns
        -------
        None.

        """
        # print(' Generating Excel Recap...')
        self.pp_excel_single()
        print(" Dumping Raw Data...")
        self.print_raw()
        print(" Generating plots...")
        # outpath = os.path.join(self.atlas_path, 'tmp')
        # os.mkdir(outpath)
        self._generate_single_plots()
        print(" Single library post-processing completed")

    def _generate_single_plots(self):
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

        for code, outputs in self.outputs.items():
            #outpath = os.path.join(self.atlas_path, "tmp")
            #if not os.path.exists(outpath):
                #os.mkdir(outpath)
            """
            if self.mcnp:
                outpath = os.path.join(self.atlas_path_mcnp, 'tmp')
                if not os.path.exists(outpath):
                    os.mkdir(outpath)
            if self.serpent:
                outpath = os.path.join(self.atlas_path_serpent, 'tmp')
                #if not os.path.exists(serpent_outpath):
                    #os.mkdir(serpent_outpath)
            if self.openmc:
                outpath = os.path.join(self.atlas_path_openmc, 'tmp')
                if not os.path.exists(outpath):
                    os.mkdir(outpath)
            if self.d1s:
                d1s_outpath = os.path.join(self.atlas_path_d1s, 'tmp')
                #if not os.path.exists(d1s_outpath):
                    #os.mkdir(d1s_outpath)
            """
            for tally, title, quantity, unit in [
                (4, "Averaged Neutron Flux (175 groups)", "Neutron Flux", r"$\#/cm^2$"),
                (14, "Averaged Gamma Flux (24 groups)", "Gamma Flux", r"$\#/cm^2$"),
            ]:               
                out_type = str(type(list(outputs.values())[0]).__name__)
                if out_type == "SphereMCNPoutput":
                    outpath = os.path.join(self.atlas_path_mcnp, 'tmp')
                if out_type == "SphereSerpentOutput":
                    outpath = os.path.join(self.atlas_path_serpent, 'tmp')
                if out_type == "SphereOpenMCOutput":
                    outpath = os.path.join(self.atlas_path_openmc, 'tmp')
                if out_type == "SphereD1Soutput":
                    outpath = os.path.join(self.atlas_path_d1s, 'tmp')
                if not os.path.exists(outpath):
                    os.mkdir(outpath)
                print(" Plotting tally n." + str(tally))
                for zaidnum, output in tqdm(outputs.items()):
                    title = title
                    tally_data = output.tallydata.set_index("Tally N.").loc[tally]
                    energy = tally_data["Energy"].values
                    values = tally_data["Value"].values
                    error = tally_data["Error"].values
                    lib_name = self.session.conf.get_lib_name(self.lib)
                    lib = {
                        "x": energy,
                        "y": values,
                        "err": error,
                        "ylabel": str(zaidnum) + " (" + lib_name + ")",
                    }
                    data = [lib]
                    outname = str(zaidnum) + "-" + self.lib + "-" + str(tally)
                    plot = plotter.Plotter(
                        data,
                        title,
                        outpath,
                        outname,
                        quantity,
                        unit,
                        "Energy [MeV]",
                        self.testname,
                    )
                    plot.plot("Binned graph")

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
        atlas_path = os.path.join(outpath, "..")
        # Printing Atlas
        template = os.path.join(self.path_templates, "AtlasTemplate.docx")
        if self.single:
            name = self.lib
        else:
            name = self.name

        atlas = at.Atlas(template, "Sphere " + name)
        atlas.build(outpath, self.session.lib_manager, self.mat_settings)
        atlas.save(atlas_path)
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
        print(" Generating Excel Recap...")
        self.pp_excel_comparison()
        print(" Creating Atlas...")
        # outpath = os.path.join(self.atlas_path, 'tmp')
        # os.mkdir(outpath)
        # Recover all libraries and zaids involved
        libraries, allzaids, outputs = self._get_organized_output()

        globalname = ""
        for lib in self.lib:
            globalname = globalname + lib + "_Vs_"

        globalname = globalname[:-4]

        # Plot everything
        print(" Generating Plots Atlas...")
        self._generate_plots(libraries, allzaids, outputs, globalname)
        print(" Comparison post-processing completed")

    def _generate_plots(self, libraries, allzaids, outputs, globalname):
        #for lib, outputs in self.outputs.items():
        #    print(lib, outputs)
        for code, code_outputs in self.outputs.items():
            for tally, title, quantity, unit in [
                (4, "Leakage Neutron Flux (175 groups)", "Neutron Flux", r"$\#/cm^2$"),
                (14, "Leakage Gamma Flux (24 groups)", "Gamma Flux", r"$\#/cm^2$"),
            ]:
                out_type = str(type(list(list(code_outputs.values())[0].values())[0]).__name__)
                if out_type == "SphereMCNPoutput":
                    outpath = os.path.join(self.atlas_path_mcnp, 'tmp')
                if out_type == "SphereSerpentOutput":
                    outpath = os.path.join(self.atlas_path_serpent, 'tmp')
                if out_type == "SphereOpenMCOutput":
                    outpath = os.path.join(self.atlas_path_openmc, 'tmp')
                if out_type == "SphereD1Soutput":
                    outpath = os.path.join(self.atlas_path_d1s, 'tmp')
                if not os.path.exists(outpath):
                    os.mkdir(outpath)
                print(" Plotting tally n." + str(tally))
                for zaidnum in tqdm(allzaids):
                    # title = title
                    data = []
                    for library, lib_outputs in code_outputs.items():
                        try:  # Zaid could not be common to the libraries
                            tally_data = lib_outputs[zaidnum].tallydata.set_index('Tally N.').loc[tally]
                            #print(lib_outputs[zaidnum])
                            energy = tally_data["Energy"].values
                            values = tally_data["Value"].values
                            error = tally_data["Error"].values
                            lib_name = self.session.conf.get_lib_name(library)
                            lib = {
                                "x": energy,
                                "y": values,
                                "err": error,
                                "ylabel": str(zaidnum) + " (" + str(lib_name) + ")",
                            }
                            data.append(lib)
                        except KeyError:
                            # It is ok, simply nothing to plot here
                            pass

                    outname = str(zaidnum) + "-" + globalname + "-" + str(tally)
                    plot = plotter.Plotter(
                        data,
                        title,
                        outpath,
                        outname,
                        quantity,
                        unit,
                        "Energy [MeV]",
                        self.testname,
                    )
                    plot.plot("Binned graph")


            self._build_atlas(outpath)

    def _get_organized_output(self):
        libraries = []
        outputs = []
        zaids = []
        for code, library_outputs in self.outputs.items():
            for libname, outputslib in library_outputs.items():
                libraries.append(libname)
                outputs.append(outputslib)
                zaids.append(list(outputslib.keys()))
        # Extend list to all zaids
        allzaids = zaids[0]
        for zaidlist in zaids[1:]:
            allzaids.extend(zaidlist)
        allzaids = set(allzaids)  # no duplicates

        return libraries, allzaids, outputs

    def _read_mcnp_output(self):
        # Get results
        results = []
        errors = []
        stat_checks = []
        outputs = {}
        test_path_mcnp = os.path.join(self.test_path, "mcnp")
        for folder in os.listdir(test_path_mcnp):
            results_path = os.path.join(test_path_mcnp, folder)
            pieces = folder.split("_")
            # Get zaid
            zaidnum = pieces[-2]
            # Check for material exception
            if zaidnum == "Sphere":
                zaidnum = pieces[-1].upper()
                zaidname = self.mat_settings.loc[zaidnum, "Name"]
            else:
                zaidname = pieces[-1]
            # Get mfile
            for file in os.listdir(results_path):
                if file[-1] == "m":
                    mfile = file
                elif file[-1] == "o":
                    ofile = file
            # Parse output
            output = SphereMCNPoutput(
                os.path.join(results_path, mfile), os.path.join(results_path, ofile)
            )
            outputs[zaidnum] = output
            # Adjourn raw Data
            self.raw_data["mcnp"][zaidnum] = output.tallydata
            # Recover statistical checks
            st_ck = output.stat_checks
            # Recover results and precisions
            res, err = output.get_single_excel_data(
                ["2", "4", "6", "12", "14", "24", "34", "22", "32", "44", "46"]
            )
            for dic in [res, err, st_ck]:
                dic["Zaid"] = zaidnum
                dic["Zaid Name"] = zaidname
            results.append(res)
            errors.append(err)
            stat_checks.append(st_ck)
        return outputs, results, errors, stat_checks

    def _read_serpent_output(self):
        # Get results
        results = []
        errors = []
        stat_checks = []
        outputs = {}
        test_path_serpent = os.path.join(self.test_path, "serpent")
        for folder in os.listdir(test_path_serpent):
            # Call parser here
            continue
        return outputs, results, errors, stat_checks

    def _read_openmc_output(self):
        # Get results
        results = []
        errors = []
        # stat_checks = []
        outputs = {}
        test_path_openmc = os.path.join(self.test_path, "openmc")
        for folder in os.listdir(test_path_openmc):
            results_path = os.path.join(test_path_openmc, folder)
            pieces = folder.split("_")
            # Get zaid
            zaidnum = pieces[-2]
            # Check for material exception
            if zaidnum == "Sphere":
                zaidnum = pieces[-1].upper()
                zaidname = self.mat_settings.loc[zaidnum, "Name"]
            else:
                zaidname = pieces[-1]
            # Parse output
            output = SphereOpenMCOutput(os.path.join(results_path, "tallies.out"))
            outputs[zaidnum] = output
            # Adjourn raw Data
            self.raw_data["openmc"][zaidnum] = output.tallydata
            # Recover statistical checks
            # st_ck = output.stat_checks
            # Recover results and precisions
            res, err = output.get_single_excel_data(["4", "14"])
            for dic in [res, err]:
                dic["Zaid"] = zaidnum
                dic["Zaid Name"] = zaidname
            results.append(res)
            errors.append(err)
            # stat_checks.append(st_ck)
        return (
            outputs,
            results,
            errors,
        )  # stat_checks

    def _generate_dataframe(self, results, errors, stat_checks=None):
        # Generate DataFrames
        results = pd.DataFrame(results)
        errors = pd.DataFrame(errors)

        # Swap Columns and correct zaid sorting
        # results
        for df in [results, errors]:
            df["index"] = pd.to_numeric(df["Zaid"].values, errors="coerce")
            df.sort_values("index", inplace=True)
            del df["index"]

            df.set_index(["Zaid", "Zaid Name"], inplace=True)
            df.reset_index(inplace=True)

        if stat_checks is not None:
            stat_checks = pd.DataFrame(stat_checks)
            stat_checks["index"] = pd.to_numeric(
                stat_checks["Zaid"].values, errors="coerce"
            )
            stat_checks.sort_values("index", inplace=True)
            del stat_checks["index"]

            stat_checks.set_index(["Zaid", "Zaid Name"], inplace=True)
            stat_checks.reset_index(inplace=True)
        return results, errors, stat_checks

    def pp_excel_single(self):
        """
        Generate the single library results excel

        Returns
        -------
        None.

        """
        self.outputs = {}
        self.results = {}
        self.errors = {}
        self.stat_checks = {}

        if self.mcnp:
            outfolder_path = self.excel_path_mcnp
            #os.makedirs(outfolder_path, exist_ok=True)
            # outpath = os.path.join(self.excel_path_mcnp,'Sphere_single_' + 'MCNP_' + self.lib+'.xlsx')
            outpath = os.path.join(
                outfolder_path, "Sphere_single_" + "MCNP_" + self.lib + ".xlsx"
            )
            outputs, results, errors, stat_checks = self._read_mcnp_output()
            results, errors, stat_checks = self._generate_dataframe(
                results, errors, stat_checks
            )
            self.outputs["mcnp"] = outputs
            self.results["mcnp"] = results
            self.errors["mcnp"] = errors
            self.stat_checks["mcnp"] = stat_checks
            # Generate DataFrames
            # results = pd.DataFrame(results)
            # errors = pd.DataFrame(errors)
            # stat_checks = pd.DataFrame(stat_checks)

            # Swap Columns and correct zaid sorting
            # results
            # for df in [results, errors, stat_checks]:
            #    df['index'] = pd.to_numeric(df['Zaid'].values, errors='coerce')
            #    df.sort_values('index', inplace=True)
            #    del df['index']

            #    df.set_index(['Zaid', 'Zaid Name'], inplace=True)
            #    df.reset_index(inplace=True)
            self.sphere_single_excel_writer(
                outpath, self.lib, results, errors, stat_checks
            )

        if self.serpent:
            pass

        if self.openmc:
            outfolder_path = self.excel_path_openmc
            #os.mkdir(outfolder_path)
            # outpath = os.path.join(self.excel_path_openmc,'Sphere_single_' + 'OpenMC_' + self.lib+'.xlsx')
            outpath = os.path.join(
                outfolder_path, "Sphere_single_" + "OpenMC_" + self.lib + ".xlsx"
            )
            outputs, results, errors = self._read_openmc_output()
            results, errors, stat_checks = self._generate_dataframe(results, errors)
            self.outputs["openmc"] = outputs
            self.results["openmc"] = results
            self.errors["openmc"] = errors
            self.stat_checks["openmc"] = stat_checks

            self.sphere_single_excel_writer(outpath, self.lib, results, errors)

        if self.d1s:
            pass

        # template = os.path.join(os.getcwd(), 'templates', 'Sphere_single.xlsx')
        # outpath = os.path.join(self.excel_path, 'Sphere_single_' +
        #                       self.lib+'.xlsx')
        """
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
        """
        """ Excel writer removed by S. Bradnam """
        ## Write excel
        # ex = SphereExcelOutputSheet(template, outpath)
        ## Results
        # ex.insert_df(9, 2, results, 0)
        # ex.insert_df(9, 2, errors, 1)
        # ex.insert_df(9, 2, stat_checks, 2)
        # lib_name = self.session.conf.get_lib_name(self.lib)
        # ex.wb.sheets[0].range('D1').value = lib_name
        # ex.save()

    def sphere_single_excel_writer(self, outpath, lib, values, errors, stats=None):
        """
        Produces single library summary excel file using XLSXwriter

        Parameters
        ----------
        outpath : path or str
            path to the output in Tests/Postprocessing.
        lib : str
            Shorthand representation of data library (i.e 00c, 31c).
        values : Dataframe
            Summary of tally values
        errors: Dataframe
            Errors on tally values
        stats: Dataframe
            Results of statistical checks

        Returns
        -------
        None
        """
        writer = pd.ExcelWriter(outpath, engine="xlsxwriter")

        for df in (values, errors):
            df.set_index("Zaid", inplace=True)

        values.to_excel(writer, startrow=8, startcol=1, sheet_name="Values")
        errors.to_excel(writer, startrow=8, startcol=1, sheet_name="Errors")

        wb = writer.book
        val_sheet = writer.sheets["Values"]
        err_sheet = writer.sheets["Errors"]

        values_len, values_width = values.shape
        errors_len, errors_width = errors.shape

        if stats is not None:
            stats.set_index("Zaid", inplace=True)
            stats.to_excel(
                writer, startrow=8, startcol=1, sheet_name="Statistical Checks"
            )
            stat_sheet = writer.sheets["Statistical Checks"]
            stats_len, stats_width = stats.shape

        # Formatting styles
        plain_format = wb.add_format({"bg_color": "#FFFFFF"})
        oob_format = wb.add_format(
            {
                "align": "center",
                "valign": "center",
                "bg_color": "#D9D9D9",
                "text_wrap": True,
            }
        )
        tally_format = wb.add_format({"bg_color": "#D9D9D9"})
        merge_format = wb.add_format(
            {"align": "center", "valign": "center", "border": 2}
        )
        title_merge_format = wb.add_format(
            {
                "font_size": "36",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
            }
        )
        subtitle_merge_format = wb.add_format(
            {
                "font_size": "16",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
            }
        )
        legend_text_format = wb.add_format({"align": "center", "bg_color": "white"})
        red_cell_format = wb.add_format({"bg_color": "red"})
        orange_cell_format = wb.add_format({"bg_color": "orange"})
        yellow_cell_format = wb.add_format({"bg_color": "yellow"})
        green_cell_format = wb.add_format({"bg_color": "#A6D86E"})
        value_allzero_format = wb.add_format({"bg_color": "#EDEDED"})
        value_belowzero_format = wb.add_format({"bg_color": "#FFC7CE"})
        value_abovezero_format = wb.add_format({"bg_color": "#C6EFCE"})

        # VALUES

        # Title Format
        val_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        val_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
        val_sheet.merge_range(
            "B3:L7", "SPHERE LEAKAGE TEST RESULTS RECAP: VALUES", title_merge_format
        )
        val_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        val_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)

        # Freeze title
        val_sheet.freeze_panes(9, 0)

        # out of bounds
        val_sheet.set_column(0, 0, 4, oob_format)
        val_sheet.set_column(values_width + 2, 1000, 18, oob_format)
        for i in range(9):
            val_sheet.set_row(i, None, oob_format)
        for i in range(9 + values_len, 1000):
            val_sheet.set_row(i, None, oob_format)

        # Column widths for values, set up to 15th col to ensure title format correct
        val_sheet.set_column(1, 14, 20)
        val_sheet.set_column(1, values_width + 2, 20)

        # Row Heights
        val_sheet.set_row(7, 31)
        val_sheet.set_row(8, 73.25)

        # Legend
        val_sheet.merge_range("N3:O3", "LEGEND", merge_format)
        val_sheet.merge_range("N8:O8", "According to MCNP manual", oob_format)
        val_sheet.write("N4", "", red_cell_format)
        val_sheet.write("O4", ">|5|%", legend_text_format)
        val_sheet.write("N5", "", orange_cell_format)
        val_sheet.write("O5", "|1|%≤|5|%", legend_text_format)
        val_sheet.write("N6", "", yellow_cell_format)
        val_sheet.write("O6", "|0.5|%≤|1|%", legend_text_format)
        val_sheet.write("N7", "", green_cell_format)
        val_sheet.write("O7", "<|0.5|%", legend_text_format)

        # Conditional Formatting
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {"type": "blanks", "format": plain_format},
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Value = 0",
                "format": value_allzero_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Value < 0",
                "format": value_belowzero_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Value > 0",
                "format": value_abovezero_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "greater than",
                "value": 0.05,
                "format": red_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.01,
                "maximum": 0.05,
                "format": orange_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.005,
                "maximum": 0.01,
                "format": yellow_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "less than",
                "value": -0.05,
                "format": red_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.05,
                "maximum": -0.01,
                "format": orange_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.01,
                "maximum": -0.005,
                "format": yellow_cell_format,
            },
        )
        val_sheet.conditional_format(
            9,
            3,
            8 + values_len,
            values_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.005,
                "maximum": 0.005,
                "format": green_cell_format,
            },
        )

        # ERRORS

        # Title
        err_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        err_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
        err_sheet.merge_range(
            "B3:L7", "SPHERE LEAKAGE TEST RESULTS RECAP: ERRORS", title_merge_format
        )
        err_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        err_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)

        # Freeze title
        err_sheet.freeze_panes(9, 0)

        # out of bounds
        err_sheet.set_column(0, 0, 4, oob_format)
        err_sheet.set_column(errors_width + 2, 1000, 18, oob_format)
        for i in range(9):
            err_sheet.set_row(i, None, oob_format)
        for i in range(9 + errors_len, 1000):
            err_sheet.set_row(i, None, oob_format)

        # Column widths for errors, set up to 15th col by default to ensure title format correct
        err_sheet.set_column(1, 14, 20)
        err_sheet.set_column(1, errors_width + 2, 20)

        # Row Heights
        err_sheet.set_row(7, 31)
        err_sheet.set_row(8, 73.25)

        # Legend
        err_sheet.merge_range("N3:O3", "LEGEND", merge_format)
        err_sheet.merge_range("N8:O8", "According to MCNP manual", oob_format)
        err_sheet.write("N4", "", red_cell_format)
        err_sheet.write("O4", "> 50%", legend_text_format)
        err_sheet.write("N5", "", orange_cell_format)
        err_sheet.write("O5", "20% ≤ 50%", legend_text_format)
        err_sheet.write("N6", "", yellow_cell_format)
        err_sheet.write("O6", "10% ≤ 20%", legend_text_format)
        err_sheet.write("N7", "", green_cell_format)
        err_sheet.write("O7", "< 10%", legend_text_format)

        # Conditional Formatting
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {"type": "blanks", "format": plain_format},
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {"type": "cell", "criteria": ">", "value": 0.5, "format": red_cell_format},
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.2,
                "maximum": 0.5,
                "format": orange_cell_format,
            },
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.1,
                "maximum": 0.2,
                "format": yellow_cell_format,
            },
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {"type": "cell", "criteria": "<", "value": -0.5, "format": red_cell_format},
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.5,
                "maximum": -0.2,
                "format": orange_cell_format,
            },
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.2,
                "maximum": -0.1,
                "format": yellow_cell_format,
            },
        )
        err_sheet.conditional_format(
            9,
            3,
            8 + errors_len,
            errors_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.1,
                "maximum": 0.1,
                "format": green_cell_format,
            },
        )

        # STAT CHECKS
        if stats is not None:
            # Title
            stat_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
            stat_sheet.merge_range("D1:D2", lib, subtitle_merge_format)
            stat_sheet.merge_range(
                "B3:L7",
                "SPHERE LEAKAGE TEST RESULTS RECAP: STATISTICAL CHECKS",
                title_merge_format,
            )
            stat_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
            stat_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)

            # Freeze title
            stat_sheet.freeze_panes(9, 0)

            # out of bounds
            stat_sheet.set_column(0, 0, 4, oob_format)
            stat_sheet.set_column(stats_width + 2, 1000, 18, oob_format)
            for i in range(9):
                stat_sheet.set_row(i, None, oob_format)
            for i in range(9 + stats_len, 1000):
                stat_sheet.set_row(i, None, oob_format)

            # Column widths for errors, set up to 15th col by default to ensure title format correct
            stat_sheet.set_column(1, 14, 20)
            stat_sheet.set_column(1, stats_width + 2, 20)

            # Row Heights
            stat_sheet.set_row(7, 31)
            stat_sheet.set_row(8, 73.25)

            # Formatting
            stat_sheet.conditional_format(
                9,
                3,
                8 + stats_len,
                stats_width + 1,
                {"type": "blanks", "format": plain_format},
            )
            stat_sheet.conditional_format(
                9,
                3,
                8 + stats_len,
                stats_width + 1,
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Passed",
                    "format": value_abovezero_format,
                },
            )
            stat_sheet.conditional_format(
                9,
                3,
                8 + stats_len,
                stats_width + 1,
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "All zeros",
                    "format": value_allzero_format,
                },
            )
            stat_sheet.conditional_format(
                9,
                3,
                8 + stats_len,
                stats_width + 1,
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Missed",
                    "format": value_belowzero_format,
                },
            )

        wb.close()

    def pp_excel_comparison(self):
        """
        Compute the data and create the excel for all libraries comparisons.
        In the meantime, additional data is stored for future plots.


        Returns
        ------- 
       6b  None.

        """
        # template = os.path.join(os.getcwd(), 'templates',
        #                        'Sphere_comparison.xlsx')
        
        code_outputs = {}

        if self.mcnp:
            iteration = 0
            outputs = {}
            for reflib, tarlib, name in self.couples:
                outfolder_path = self.excel_path_mcnp
                #os.mkdir(outfolder_path)
                outpath = os.path.join(
                    outfolder_path, "Sphere_comparison_" + name + "_mcnp.xlsx"
                )
                # outpath = os.path.join(self.excel_path_mcnp, 'Sphere_comparison_' +
                #                       name+'.xlsx')
                # Get results
                comp_dfs = []
                error_dfs = []
                
                for test_path in [
                    os.path.join(self.test_path[reflib], "mcnp"),
                    os.path.join(self.test_path[tarlib], "mcnp"),
                ]:
                    results = []
                    errors = []
                    iteration = iteration + 1
                    outputs_lib = {}
                    for folder in os.listdir(test_path):
                        results_path = os.path.join(test_path, folder)
                        pieces = folder.split("_")
                        # Get zaid
                        zaidnum = pieces[-2]
                        # Check for material exception
                        if zaidnum == "Sphere":
                            zaidnum = pieces[-1].upper()
                            zaidname = self.mat_settings.loc[zaidnum, "Name"]
                        else:
                            zaidname = pieces[-1]

                        # Get mfile
                        for file in os.listdir(results_path):
                            if file[-1] == "m":
                                mfile = file
                            elif file[-1] == "o":
                                outfile = file

                        # Parse output
                        mfile = os.path.join(results_path, mfile)
                        outfile = os.path.join(results_path, outfile)
                        output = SphereMCNPoutput(mfile, outfile)
                        outputs_lib[zaidnum] = output
                        res, err, columns = output.get_comparison_data(
                            ["4", "14"], "mcnp"
                        )
                        try:
                            zn = int(zaidnum)
                        except ValueError:  # Happens for typical materials
                            zn = zaidnum

                        res.append(zn)
                        err.append(zn)
                        res.append(zaidname)
                        err.append(zaidname)

                        results.append(res)
                        errors.append(err)
                
                    # Add reference library outputs
                    if iteration == 1:
                        outputs[reflib] = outputs_lib

                    if test_path == os.path.join(self.test_path[tarlib], "mcnp"):
                        outputs[tarlib] = outputs_lib

                    # Generate DataFrames
                    columns.extend(["Zaid", "Zaid Name"])
                    comp_df = pd.DataFrame(results, columns=columns)
                    error_df = pd.DataFrame(errors, columns=columns)
                    comp_df.set_index(["Zaid", "Zaid Name"], inplace=True)
                    error_df.set_index(["Zaid", "Zaid Name"], inplace=True)
                    comp_dfs.append(comp_df)
                    error_dfs.append(error_df)
                
                # outputs_couple = outputs
                code_outputs["mcnp"] = outputs
                self.outputs = code_outputs
                #self.results["mcnp"] = results
                #self.errors["mcnp"] = errors

                # Consider only common zaids
                idx1 = comp_dfs[0].index
                idx2 = comp_dfs[1].index
                newidx = idx1.intersection(idx2)

                # Build the final excel data
                final = (comp_dfs[0].loc[newidx] - comp_dfs[1].loc[newidx]) / comp_dfs[
                    0
                ].loc[newidx]
                absdiff = comp_dfs[0].loc[newidx] - comp_dfs[1].loc[newidx]

                #self.diff_data["mcnp"] = final
                #self.absdiff["mcnp"] = absdiff

                # Standard deviation
                idx1 = absdiff.index
                idx2 = error_dfs[0].index
                newidx = idx1.intersection(idx2)

                std_dev = absdiff.loc[newidx] / error_dfs[0].loc[newidx]

                #self.std_dev["mcnp"] = std_dev
                # Correct sorting
                for df in [final, absdiff, std_dev]:
                    df.reset_index(inplace=True)
                    df["index"] = pd.to_numeric(df["Zaid"].values, errors="coerce")
                    df.sort_values("index", inplace=True)
                    del df["index"]
                    df.set_index(["Zaid", "Zaid Name"], inplace=True)
                # Create and concat the summary
                old_l = 0
                old_lim = 0
                rows = []
                limits = [0, 0.05, 0.1, 0.2, 0.2]
                for i, sup_lim in enumerate(limits[1:]):
                    if i == len(limits) - 2:
                        row = {"Range": "% of cells > " + str(sup_lim * 100)}
                        for column in final.columns:
                            cleaned = final[column].replace("", np.nan).dropna()
                            l_range = len(cleaned[abs(cleaned) > sup_lim])
                            try:
                                row[column] = l_range / len(cleaned)
                            except ZeroDivisionError:
                                row[column] = np.nan
                    else:
                        row = {
                            "Range": str(old_lim * 100)
                            + " < "
                            + "% of cells"
                            + " < "
                            + str(sup_lim * 100)
                        }
                        for column in final.columns:
                            cleaned = final[column].replace("", np.nan).dropna()
                            lenght = len(cleaned[abs(cleaned) < sup_lim])
                            old_l = len(cleaned[abs(cleaned) < limits[i]])
                            l_range = lenght - old_l
                            try:
                                row[column] = l_range / len(cleaned)
                            except ZeroDivisionError:
                                row[column] = np.nan

                    old_lim = sup_lim
                    rows.append(row)

                summary = pd.DataFrame(rows)
                summary.set_index("Range", inplace=True)
                # If it is zero the CS are equal! (NaN if both zeros)
                for df in [final, absdiff, std_dev]:
                    # df[df == np.nan] = 'Not Available'
                    df.astype({col: float for col in df.columns[1:]})
                    df.replace(np.nan, "Not Available", inplace=True)
                    df.replace(float(0), "Identical", inplace=True)
                    df.replace(-np.inf, "Reference = 0", inplace=True)
                    df.replace(1, "Target = 0", inplace=True)

                # --- Write excel ---
                # Generate the excel
                self.sphere_comp_excel_writer(
                    outpath, name, final, absdiff, std_dev, summary
                )
                """
                # ex = SphereExcelOutputSheet(template, outpath)
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
                """
        if self.openmc:
            iteration = 0
            outputs = {}
            for reflib, tarlib, name in self.couples:
                outfolder_path = self.excel_path_openmc
                #os.mkdir(outfolder_path)
                outpath = os.path.join(
                    outfolder_path, "Sphere_comparison_" + name + "_openmc.xlsx"
                )
                # outpath = os.path.join(self.excel_path_openmc, 'Sphere_comparison_' +
                #                       name+'openmc.xlsx')
                # Get results
                comp_dfs = []
                error_dfs = []

                for test_path in [
                    os.path.join(self.test_path[reflib], "openmc"),
                    os.path.join(self.test_path[tarlib], "openmc"),
                ]:
                    results = []
                    errors = []
                    iteration = iteration + 1
                    outputs_lib = {}
                    for folder in os.listdir(test_path):
                        results_path = os.path.join(test_path, folder)
                        pieces = folder.split("_")
                        # Get zaid
                        zaidnum = pieces[-2]
                        # Check for material exception
                        if zaidnum == "Sphere":
                            zaidnum = pieces[-1].upper()
                            zaidname = self.mat_settings.loc[zaidnum, "Name"]
                        else:
                            zaidname = pieces[-1]

                        # Get mfile
                        for file in os.listdir(results_path):
                            if "tallies.out" in file:
                                outfile = file

                        # Parse output
                        outfile = os.path.join(results_path, outfile)
                        output = SphereOpenMCOutput(outfile)
                        outputs_lib[zaidnum] = output
                        res, err, columns = output.get_comparison_data(
                            ["4", "14"], "openmc"
                        )
                        try:
                            zn = int(zaidnum)
                        except ValueError:  # Happens for typical materials
                            zn = zaidnum

                        res.append(zn)
                        err.append(zn)
                        res.append(zaidname)
                        err.append(zaidname)

                        results.append(res)
                        errors.append(err)
                    # Add reference library outputs
                    if iteration == 1:
                        outputs[reflib] = outputs_lib

                    if test_path == os.path.join(self.test_path[tarlib], "openmc"):
                        outputs[tarlib] = outputs_lib

                    # Generate DataFrames
                    columns.extend(["Zaid", "Zaid Name"])
                    comp_df = pd.DataFrame(results, columns=columns)
                    error_df = pd.DataFrame(errors, columns=columns)
                    comp_df.set_index(["Zaid", "Zaid Name"], inplace=True)
                    error_df.set_index(["Zaid", "Zaid Name"], inplace=True)
                    comp_dfs.append(comp_df)
                    error_dfs.append(error_df)

                    # outputs_couple = outputs
                    # self.results = results
                code_outputs["openmc"] = outputs
                self.outputs = code_outputs
                #self.results["openmc"] = results
                #self.errors["openmc"] = errors
                # Consider only common zaids
                idx1 = comp_dfs[0].index
                idx2 = comp_dfs[1].index
                newidx = idx1.intersection(idx2)

                # Build the final excel data
                final = (comp_dfs[0].loc[newidx] - comp_dfs[1].loc[newidx]) / comp_dfs[
                    0].loc[newidx]
                absdiff = comp_dfs[0].loc[newidx] - comp_dfs[1].loc[newidx]

                #self.diff_data["openmc"] = final
                #self.absdiff["openmc"] = absdiff

                # Standard deviation
                idx1 = absdiff.index
                idx2 = error_dfs[0].index
                newidx = idx1.intersection(idx2)

                std_dev = absdiff.loc[newidx] / error_dfs[0].loc[newidx]

                #self.std_dev["openmc"] = std_dev

                # Correct sorting
                for df in [final, absdiff, std_dev]:
                    df.reset_index(inplace=True)
                    df["index"] = pd.to_numeric(df["Zaid"].values, errors="coerce")
                    df.sort_values("index", inplace=True)
                    del df["index"]
                    df.set_index(["Zaid", "Zaid Name"], inplace=True)
                # Create and concat the summary
                old_l = 0
                old_lim = 0
                rows = []
                limits = [0, 0.05, 0.1, 0.2, 0.2]
                for i, sup_lim in enumerate(limits[1:]):
                    if i == len(limits) - 2:
                        row = {"Range": "% of cells > " + str(sup_lim * 100)}
                        for column in final.columns:
                            cleaned = final[column].replace("", np.nan).dropna()
                            l_range = len(cleaned[abs(cleaned) > sup_lim])
                            try:
                                row[column] = l_range / len(cleaned)
                            except ZeroDivisionError:
                                row[column] = np.nan
                    else:
                        row = {
                            "Range": str(old_lim * 100)
                            + " < "
                            + "% of cells"
                            + " < "
                            + str(sup_lim * 100)
                        }
                        for column in final.columns:
                            cleaned = final[column].replace("", np.nan).dropna()
                            lenght = len(cleaned[abs(cleaned) < sup_lim])
                            old_l = len(cleaned[abs(cleaned) < limits[i]])
                            l_range = lenght - old_l
                            try:
                                row[column] = l_range / len(cleaned)
                            except ZeroDivisionError:
                                row[column] = np.nan

                    old_lim = sup_lim
                    rows.append(row)

                summary = pd.DataFrame(rows)
                summary.set_index("Range", inplace=True)
                # If it is zero the CS are equal! (NaN if both zeros)
                for df in [final, absdiff, std_dev]:
                    # df[df == np.nan] = 'Not Available'
                    df.astype({col: float for col in df.columns[1:]})
                    df.replace(np.nan, "Not Available", inplace=True)
                    df.replace(float(0), "Identical", inplace=True)
                    df.replace(-np.inf, "Reference = 0", inplace=True)
                    df.replace(1, "Target = 0", inplace=True)

                # --- Write excel ---
                # Generate the excel
                self.sphere_comp_excel_writer(
                    outpath, name, final, absdiff, std_dev, summary
                )
        if self.serpent:
            pass

    def sphere_comp_excel_writer(self, outpath, name, final, absdiff, std_dev, summary):
        writer = pd.ExcelWriter(
            outpath,
            engine="xlsxwriter",
            engine_kwargs={"options": {"strings_to_numbers": True}},
        )

        comp_len, comp_width = final.shape
        absdiff_len, absdiff_width = absdiff.shape
        std_dev_len, std_dev_width = std_dev.shape
        summ_len, summ_width = summary.shape

        # Insert DataFrame
        final.to_excel(writer, startrow=9, startcol=1, sheet_name="Comparison (%)")
        summary.to_excel(
            writer, startrow=comp_len + 12, startcol=2, sheet_name="Comparison (%)"
        )
        std_dev.to_excel(
            writer, startrow=9, startcol=1, sheet_name="Comparison (std. dev.)"
        )
        absdiff.to_excel(
            writer, startrow=9, startcol=1, sheet_name="Comparison (abs diff)"
        )

        wb = writer.book
        comp_sheet = writer.sheets["Comparison (%)"]
        std_dev_sheet = writer.sheets["Comparison (std. dev.)"]
        absdiff_sheet = writer.sheets["Comparison (abs diff)"]

        # Formatting styles
        plain_format = wb.add_format({"bg_color": "#FFFFFF"})
        oob_format = wb.add_format(
            {
                "align": "center",
                "valign": "center",
                "bg_color": "#D9D9D9",
                "text_wrap": True,
            }
        )
        tally_format = wb.add_format({"bg_color": "#D9D9D9"})
        merge_format = wb.add_format(
            {"align": "center", "valign": "center", "border": 2}
        )
        title_merge_format = wb.add_format(
            {
                "font_size": "36",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
            }
        )
        subtitle_merge_format = wb.add_format(
            {
                "font_size": "16",
                "align": "center",
                "valign": "center",
                "bold": True,
                "border": 2,
                "text_wrap": True,
            }
        )
        legend_text_format = wb.add_format({"align": "center", "bg_color": "white"})
        red_cell_format = wb.add_format({"bg_color": "FF6961"})
        orange_cell_format = wb.add_format({"bg_color": "FFB54C"})
        yellow_cell_format = wb.add_format({"bg_color": "F8D66D"})
        green_cell_format = wb.add_format({"bg_color": "#8CD47E"})
        not_avail_format = wb.add_format({"bg_color": "#B8B8B8"})
        target_ref_format = wb.add_format({"bg_color": "#8465C5"})
        identical_format = wb.add_format({"bg_color": "#7ABD7E"})

        """VALUES"""
        # Merged Cells
        comp_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        comp_sheet.merge_range("D1:E2", name, subtitle_merge_format)
        comp_sheet.merge_range(
            "B3:L7", "SPHERE LEAKAGE % COMPARISON RECAP", title_merge_format
        )
        comp_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        comp_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)
        comp_sheet.merge_range(
            "F1:L2",
            "Target library Vs Reference library\n(Reference-Target)/Reference",
            subtitle_merge_format,
        )
        comp_sheet.merge_range(
            11 + comp_len,
            3,
            11 + comp_len,
            11,
            "GLOBAL QUICK RESULT: % of cells per range of comparison differences",
            subtitle_merge_format,
        )
        # Freeze title
        comp_sheet.freeze_panes(10, 3)

        # out of bounds
        comp_sheet.set_column(0, 0, 4, oob_format)
        comp_sheet.set_column(comp_width + 3, 1000, 4, oob_format)
        for i in range(9):
            comp_sheet.set_row(i, None, oob_format)
        for i in range(9 + comp_len, 1000):
            comp_sheet.set_row(i, None, oob_format)

        # Column widths for values, set up to 15th col to ensure title format correct

        comp_sheet.set_column(1, 14, 18)
        comp_sheet.set_column(1, comp_width + 5, 18)

        # Summary background formatting workaround using conditional formatting
        comp_sheet.conditional_format(
            12 + comp_len,
            3,
            comp_len + summ_len + 12,
            summ_width + 3,
            {"type": "cell", "criteria": ">=", "value": 0, "format": plain_format},
        )
        comp_sheet.conditional_format(
            12 + comp_len,
            3,
            comp_len + summ_len + 22,
            summ_width + 3,
            {"type": "cell", "criteria": "<", "value": 0, "format": plain_format},
        )

        # Row Heights
        comp_sheet.set_row(0, 25, oob_format)
        comp_sheet.set_row(1, 25, oob_format)
        comp_sheet.set_row(7, 31, oob_format)
        comp_sheet.set_row(8, 40, oob_format)
        comp_sheet.set_row(9, 40, oob_format)

        # Legend
        comp_sheet.merge_range("N3:O3", "LEGEND", merge_format)
        comp_sheet.write("N4", "", red_cell_format)
        comp_sheet.write("O4", ">|20|%", legend_text_format)
        comp_sheet.write("N5", "", orange_cell_format)
        comp_sheet.write("O5", "|20|%≤|10|%", legend_text_format)
        comp_sheet.write("N6", "", yellow_cell_format)
        comp_sheet.write("O6", "|10|%≤|5|%", legend_text_format)
        comp_sheet.write("N7", "", green_cell_format)
        comp_sheet.write("O7", "<|5|%", legend_text_format)

        # Conditional Formatting
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {"type": "blanks", "format": plain_format},
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Not Available",
                "format": not_avail_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Target = 0",
                "format": target_ref_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Reference = 0",
                "format": target_ref_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Identical",
                "format": identical_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "greater than",
                "value": 0.2,
                "format": red_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.1,
                "maximum": 0.2,
                "format": orange_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 0.05,
                "maximum": 0.1,
                "format": yellow_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "less than",
                "value": -0.2,
                "format": red_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.5,
                "maximum": -0.1,
                "format": orange_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.1,
                "maximum": -0.05,
                "format": yellow_cell_format,
            },
        )
        comp_sheet.conditional_format(
            10,
            3,
            9 + comp_len,
            comp_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -0.05,
                "maximum": 0.05,
                "format": green_cell_format,
            },
        )

        # Summary totals
        for row in range(13 + comp_len, comp_len + summ_len + 13):
            start = xl_rowcol_to_cell(row, 3)
            stop = xl_rowcol_to_cell(row, summ_width + 2)
            comp_sheet.write_formula(
                row,
                summ_width + 3,
                "=SUM({start}:{stop})/{len}".format(
                    start=start, stop=stop, len=summ_width
                ),
            )

        """STANDARD DEVIATIONS FROM MEAN"""
        std_dev_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        std_dev_sheet.merge_range("D1:E2", name, subtitle_merge_format)
        std_dev_sheet.merge_range(
            "B3:L7", "SPHERE LEAKAGE % COMPARISON RECAP", title_merge_format
        )
        std_dev_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        std_dev_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)
        std_dev_sheet.merge_range(
            "F1:L2",
            "Target library Vs Reference library\n(Reference-Target)/Reference",
            subtitle_merge_format,
        )
        std_dev_sheet.merge_range(
            11 + std_dev_len,
            3,
            11 + std_dev_len,
            11,
            "GLOBAL QUICK RESULT: % of cells per range of comparison differences",
            subtitle_merge_format,
        )
        # Freeze title
        std_dev_sheet.freeze_panes(10, 3)

        # out of bounds
        std_dev_sheet.set_column(0, 0, 4, oob_format)
        std_dev_sheet.set_column(std_dev_width + 3, 1000, 4, oob_format)
        for i in range(9):
            std_dev_sheet.set_row(i, None, oob_format)
        for i in range(9 + std_dev_len, 1000):
            std_dev_sheet.set_row(i, None, oob_format)

        # Column widths for values, set up to 15th col to ensure title format correct

        std_dev_sheet.set_column(1, 14, 18)
        std_dev_sheet.set_column(1, std_dev_width + 5, 18)

        # Summary background formatting workaround using conditional formatting
        std_dev_sheet.conditional_format(
            12 + std_dev_len,
            3,
            std_dev_len + summ_len + 12,
            summ_width + 3,
            {"type": "cell", "criteria": ">=", "value": 0, "format": plain_format},
        )
        std_dev_sheet.conditional_format(
            12 + std_dev_len,
            3,
            std_dev_len + summ_len + 22,
            summ_width + 3,
            {"type": "cell", "criteria": "<", "value": 0, "format": plain_format},
        )

        # Row Heights
        std_dev_sheet.set_row(0, 25, oob_format)
        std_dev_sheet.set_row(1, 25, oob_format)
        std_dev_sheet.set_row(7, 31, oob_format)
        std_dev_sheet.set_row(8, 40, oob_format)
        std_dev_sheet.set_row(9, 40, oob_format)

        # Legend
        std_dev_sheet.merge_range("N3:O3", "LEGEND", merge_format)
        std_dev_sheet.write("N4", "", red_cell_format)
        std_dev_sheet.write("O4", ">|20|%", legend_text_format)
        std_dev_sheet.write("N5", "", orange_cell_format)
        std_dev_sheet.write("O5", "|20|%≤|10|%", legend_text_format)
        std_dev_sheet.write("N6", "", yellow_cell_format)
        std_dev_sheet.write("O6", "|10|%≤|5|%", legend_text_format)
        std_dev_sheet.write("N7", "", green_cell_format)
        std_dev_sheet.write("O7", "<|5|%", legend_text_format)

        # Conditional Formatting
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {"type": "blanks", "format": plain_format},
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Not Available",
                "format": not_avail_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Target = 0",
                "format": target_ref_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Reference = 0",
                "format": target_ref_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Identical",
                "format": identical_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "greater than",
                "value": 3,
                "format": red_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 3,
                "maximum": 2,
                "format": orange_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": 2,
                "maximum": 1,
                "format": yellow_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "less than",
                "value": -3,
                "format": red_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 1,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -3,
                "maximum": -2,
                "format": orange_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -2,
                "maximum": -1,
                "format": yellow_cell_format,
            },
        )
        std_dev_sheet.conditional_format(
            10,
            3,
            9 + std_dev_len,
            std_dev_width + 2,
            {
                "type": "cell",
                "criteria": "between",
                "minimum": -1,
                "maximum": 1,
                "format": green_cell_format,
            },
        )
        """ABS DIFF"""
        # Merged Cells
        absdiff_sheet.merge_range("B1:C2", "LIBRARY", subtitle_merge_format)
        absdiff_sheet.merge_range("D1:E2", name, subtitle_merge_format)
        absdiff_sheet.merge_range(
            "B3:L7", "SPHERE LEAKAGE % COMPARISON RECAP", title_merge_format
        )
        absdiff_sheet.merge_range("B8:C8", "ZAID", subtitle_merge_format)
        absdiff_sheet.merge_range("D8:L8", "TALLY", subtitle_merge_format)
        absdiff_sheet.merge_range(
            "F1:L2",
            "Target library Vs Reference library\n(Reference-Target)",
            subtitle_merge_format,
        )

        # Freeze title
        absdiff_sheet.freeze_panes(10, 3)

        # out of bounds
        absdiff_sheet.set_column(0, 0, 4, oob_format)
        absdiff_sheet.set_column(absdiff_width + 3, 1000, 4, oob_format)
        for i in range(9):
            absdiff_sheet.set_row(i, None, oob_format)
        for i in range(10 + absdiff_len, 1000):
            absdiff_sheet.set_row(i, None, oob_format)

        # Column widths for values, set up to 15th col to ensure title format correct
        absdiff_sheet.set_column(1, 14, 18)
        absdiff_sheet.set_column(1, absdiff_width + 2, 18)

        # Row Heights
        absdiff_sheet.set_row(0, 25, oob_format)
        absdiff_sheet.set_row(1, 25, oob_format)
        absdiff_sheet.set_row(7, 31, oob_format)
        absdiff_sheet.set_row(8, 40, oob_format)
        absdiff_sheet.set_row(9, 40, oob_format)

        # Conditional Formatting

        absdiff_sheet.conditional_format(
            10,
            3,
            9 + absdiff_len,
            absdiff_width + 2,
            {
                "type": "text",
                "criteria": "containing",
                "value": "Identical",
                "format": identical_format,
            },
        )

        wb.close()

    def print_raw(self):
        # for code in self.raw_data:
        #    for key, data in self.raw_data[code].items():
        #        file = os.path.join(self.raw_path, code, key+'.csv')
        #        data.to_csv(file, header=True, index=False)
        if self.mcnp:
            for key, data in self.raw_data["mcnp"].items():
                file = os.path.join(self.raw_path_mcnp, "mcnp" + key + ".csv")
                data.to_csv(file, header=True, index=False)
        if self.serpent:
            for key, data in self.raw_data["serpent"].items():
                file = os.path.join(self.raw_path_serpent, "serpent" + key + ".csv")
                data.to_csv(file, header=True, index=False)
        if self.openmc:
            for key, data in self.raw_data["openmc"].items():
                file = os.path.join(self.raw_path_openmc, "openmc" + key + ".csv")
                data.to_csv(file, header=True, index=False)
        if self.d1s:
            for key, data in self.raw_data["d1s"].items():
                file = os.path.join(self.raw_path_d1s, "d1s" + key + ".csv")
                data.to_csv(file, header=True, index=False)


class SphereTallyOutput:

    """SB to replace this next!"""

    def get_single_excel_data(self, tallies2pp):
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
        # tallies2pp = ['2', '32', '24', '14', '34']
        # heating_tallies = ['4', '6', '44', '46']
        # tallies2pp = ['4' '14']
        data = self.tallydata.set_index(["Energy"])
        totbins = self.totalbin.set_index("Tally Description")
        results = {}  # Store excel results of different tallies
        errors = {}  # Store average error in different tallies
        keys = {}  # Tally names and numbers
        # heating_res = {}  # Mid-process heating results
        notes = "Negative Bins:"  # Record negative bins here
        initial_notes_length = len(notes)  # To check if notes are registered
        tally_list = [d for _, d in data.groupby(["Tally N."])]
        for tally in tally_list:
            tally_num = str(tally["Tally N."].iloc[0])
            tally_description = tally["Tally Description"].iloc[0]
            mean_error = tally["Error"].mean()
            if tally_num in tallies2pp:
                tally_zero = tally[tally["Value"] == 0]
                original_length = len(tally)
                tally = tally[tally["Value"] < 0]
                if len(tally) > 0:
                    res = "Value < 0 in " + str(len(tally)) + " bin(s)"
                    # Get energy bins
                    bins = list(tally.reset_index()["Energy"].values)
                    notes = notes + "\n(" + str(tally_num) + "): "
                    for ebin in bins:
                        notes = notes + str(ebin) + ", "
                    notes = notes[:-2]  # Clear string from excess commas
                elif len(tally_zero) == original_length:
                    res = "Value = 0 for all bins"
                else:
                    res = "Value > 0 for all bins"
                results[tally_description] = res
                errors[tally_description] = mean_error
        # for tally in self.mctal.tallies:
        #    num = str(tally.tallyNumber)
        #    keys[num] = tally.tallyComment[0]
        #    # Isolate tally
        #    masked = data.loc[tally.tallyComment[0]]
        #    print(masked)
        #    # Get mean error among bins, different for single bin
        #    if tally.ergTC == 't':
        #        mean_error = totbins.loc[tally.tallyComment[0]]['Error']
        #    else:
        #        mean_error = masked['Error'].mean()
        #
        #    if num in tallies2pp:
        #        masked_zero = masked[masked['Value'] == 0]
        #        original_length = len(masked)
        #        masked = masked[masked['Value'] < 0]
        #        if len(masked) > 0:
        #            res = 'Value < 0 in '+str(len(masked))+' bin(s)'
        #            # Get energy bins
        #            bins = list(masked.reset_index()['Energy'].values)
        #            notes = notes+'\n('+str(num)+'): '
        #            for ebin in bins:
        #                notes = notes+str(ebin)+', '
        #            notes = notes[:-2]  # Clear string from excess commas
        #
        #        elif len(masked_zero) == original_length:
        #            res = 'Value = 0 for all bins'
        #        else:
        #            res = 'Value > 0 for all bins'
        #
        #        results[tally.tallyComment[0]] = res
        #        errors[tally.tallyComment[0]] = mean_error

        # elif num in heating_tallies:
        #    heating_res[num] = float(masked['Value'].values[0])
        #    errors[tally.tallyComment[0]] = mean_error

        # comp = 'Heating comparison [F4 vs F6]'
        # try:
        #    results['Neutron '+comp] = ((heating_res['6'] - heating_res['4']) /
        #                                heating_res['6'])
        # except ZeroDivisionError:
        #    results['Neutron '+comp] = 0
        #
        # try:
        #    results['Gamma '+comp] = ((heating_res['46'] - heating_res['44']) /
        #                              heating_res['46'])
        # except ZeroDivisionError:
        #    results['Gamma '+comp] = 0

        # Notes adding
        if len(notes) > initial_notes_length:
            results["Notes"] = notes
        else:
            results["Notes"] = ""
        return results, errors

    def get_comparison_data(self, tallies2pp, code):
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
        # tallies2pp = ['12', '22', '24', '14', '34', '6', '46']
        data = self.tallydata.set_index(["Energy"])
        totalbins = self.totalbin.set_index("Tally Description")
        results = []  # Store data to compare for different tallies
        errors = []
        columns = []  # Tally names and numbers
        # Reorder tallies
        tallies = []
        tally_list = [d for _, d in data.groupby(["Tally N."])]

        for tally in tally_list:
            tally = str(tally["Tally N."].iloc[0])
            if tally in tallies2pp:
                tallies.append(tally)

        """if code == "mcnp":
            for tally in tallies:
                tally_num = str(tally.tallyNumber)
                # Isolate tally
                masked = data.loc[tally.tallyComment[0]]

                if tally_num in ['12', '22', '4', '14']:  # Coarse Flux bins
                    masked_tot = totalbins.loc[tally.tallyComment[0]]
                    # Get energy bins
                    bins = list(masked.reset_index()['Energy'].values)
                    for ebin in bins:
                        # colname = '(T.ly '+str(num)+') '+str(ebin)
                        colname = str(ebin)+' [MeV]'+' [t'+tally_num+']'
                        columns.append(colname)
                        results.append(masked['Value'].loc[ebin])
                        errors.append(masked['Error'].loc[ebin])
                    # Add the total bin
                    colname = 'Total'+' [t'+tally_num+']'
                    columns.append(colname)
                    results.append(masked_tot['Value'])
                    errors.append(masked_tot['Error'])
                else:
                    columns.append(tally.tallyComment[0])
                    results.append(masked['Value'].values[0])
                    errors.append(masked['Error'].values[0])

        if code == "openmc":"""
        for tally in tally_list:
            tally_num = str(tally["Tally N."].iloc[0])
            tally_description = tally["Tally Description"].iloc[0]
            if tally_num in ["12", "22", "4", "14"]:  # Coarse Flux bins
                # Get energy bins
                bins = tally.index.tolist()
                for ebin in bins:
                    # colname = '(T.ly '+str(num)+') '+str(ebin)
                    colname = str(ebin) + " [MeV]" + " [t" + tally_num + "]"
                    columns.append(colname)
                    results.append(tally["Value"].loc[ebin])
                    errors.append(tally["Error"].loc[ebin])
                # Add the total bin
                colname = "Total" + " [t" + tally_num + "]"
                columns.append(colname)
                results.append(totalbins["Value"].loc[tally_description])
                errors.append(totalbins["Error"].loc[tally_description])
            else:
                columns.append(tally_description)
                results.append(tally["Value"])
                errors.append(tally["Error"])
        # print(results,errors,columns)
        return results, errors, columns


class SphereMCNPoutput(MCNPoutput, SphereTallyOutput):
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
                                                        val = t.getValue(
                                                            f,
                                                            d,
                                                            u,
                                                            s,
                                                            m,
                                                            c,
                                                            e,
                                                            nt,
                                                            i,
                                                            j,
                                                            k,
                                                            0,
                                                        )
                                                        err = t.getValue(
                                                            f,
                                                            d,
                                                            u,
                                                            s,
                                                            m,
                                                            c,
                                                            e,
                                                            nt,
                                                            i,
                                                            j,
                                                            k,
                                                            1,
                                                        )
                                                        if val <= 0:
                                                            err = np.nan

                                                        row = [num, des, erg, val, err]
                                                        rows.append(row)

            # If Energy binning is involved
            if t.ergTC == "t":
                # 7 steps to get to energy, + 4 for time and mesh directions
                totalbin = t.valsErrors[-1][-1][-1][-1][-1][-1][-1][-1][-1][-1][-1]
                totalvalue = totalbin[0]
                if totalvalue > 0:
                    totalerror = totalbin[-1]
                else:
                    totalerror = np.nan
                row = [num, des, totalvalue, totalerror]
                rowstotal.append(row)

        df = pd.DataFrame(
            rows, columns=["Tally N.", "Tally Description", "Energy", "Value", "Error"]
        )
        dftotal = pd.DataFrame(
            rowstotal, columns=["Tally N.", "Tally Description", "Value", "Error"]
        )
        return df, dftotal

        #    def get_single_excel_data(self, tallies2pp):
        #        """
        #        Get the excel data of a single MCNP output
        #
        #        Returns
        #        -------
        #        results : dic
        #            Excel result for different tallies
        #        errors : dic
        #            Error average in all tallies
        #
        #        """
        #        # Tallies to post process
        #        #tallies2pp = ['2', '32', '24', '14', '34']
        #        #heating_tallies = ['4', '6', '44', '46']
        #        #tallies2pp = ['4' '14']
        #        data = self.tallydata.set_index(['Tally Description', 'Energy'])
        #        totbins = self.totalbin.set_index('Tally Description')
        #        results = {}  # Store excel results of different tallies
        #        errors = {}  # Store average error in different tallies
        #        keys = {}  # Tally names and numbers
        #        #heating_res = {}  # Mid-process heating results
        #        notes = 'Negative Bins:'  # Record negative bins here
        #        initial_notes_length = len(notes)  # To check if notes are registered
        #        for tally in self.mctal.tallies:
        #            num = str(tally.tallyNumber)
        #            keys[num] = tally.tallyComment[0]
        #            # Isolate tally
        #            masked = data.loc[tally.tallyComment[0]]
        #
        #            # Get mean error among bins, different for single bin
        #            if tally.ergTC == 't':
        #                mean_error = totbins.loc[tally.tallyComment[0]]['Error']
        #            else:
        #                mean_error = masked['Error'].mean()
        #
        #            if num in tallies2pp:
        #                masked_zero = masked[masked['Value'] == 0]
        #                original_length = len(masked)
        #                masked = masked[masked['Value'] < 0]
        #                if len(masked) > 0:
        #                    res = 'Value < 0 in '+str(len(masked))+' bin(s)'
        #                    # Get energy bins
        #                    bins = list(masked.reset_index()['Energy'].values)
        #                    notes = notes+'\n('+str(num)+'): '
        #                    for ebin in bins:
        #                        notes = notes+str(ebin)+', '
        #                    notes = notes[:-2]  # Clear string from excess commas
        #
        #                elif len(masked_zero) == original_length:
        #                    res = 'Value = 0 for all bins'
        #                else:
        #                    res = 'Value > 0 for all bins'
        #
        #                results[tally.tallyComment[0]] = res
        #                errors[tally.tallyComment[0]] = mean_error
        #
        #            #elif num in heating_tallies:
        #            #    heating_res[num] = float(masked['Value'].values[0])
        #            #    errors[tally.tallyComment[0]] = mean_error
        #
        #        #comp = 'Heating comparison [F4 vs F6]'
        #        #try:
        #        #    results['Neutron '+comp] = ((heating_res['6'] - heating_res['4']) /
        #        #                                heating_res['6'])
        #        #except ZeroDivisionError:
        #        #    results['Neutron '+comp] = 0
        #        #
        #        #try:
        #        #    results['Gamma '+comp] = ((heating_res['46'] - heating_res['44']) /
        #        #                              heating_res['46'])
        #        #except ZeroDivisionError:
        #        #    results['Gamma '+comp] = 0
        #
        #        # Notes adding
        #        if len(notes) > initial_notes_length:
        #            results['Notes'] = notes
        #        else:
        #            results['Notes'] = ''
        #
        #        return results, errors
        #
        #    def get_comparison_data(self, tallies2pp):
        #        """
        #        Get Data for single zaid to be used in comparison.
        #
        #        Returns
        #        -------
        #        results : list
        #            All results per tally to compare
        #        columns : list
        #            Tally names
        #
        #        """
        #        # Tallies to post process
        #        #tallies2pp = ['12', '22', '24', '14', '34', '6', '46']
        #        data = self.tallydata.set_index(['Tally Description', 'Energy'])
        #        totalbins = self.totalbin.set_index('Tally Description')
        #        results = []  # Store data to compare for different tallies
        #        columns = []  # Tally names and numbers
        #        # Reorder tallies
        #        tallies = []
        #        for tallynum in tallies2pp:
        #            for tally in self.mctal.tallies:
        #                num = str(tally.tallyNumber)
        #                if num == tallynum:
        #                    tallies.append(tally)
        #
        #        for tally in tallies:
        #            num = str(tally.tallyNumber)
        #            # Isolate tally
        #
        #            masked = data.loc[tally.tallyComment[0]]
        #            if num in tallies2pp:
        #                if num in ['12', '22']:  # Coarse Flux bins
        #                    masked_tot = totalbins.loc[tally.tallyComment[0]]
        #                    # Get energy bins
        #                    bins = list(masked.reset_index()['Energy'].values)
        #                    for ebin in bins:
        #                        # colname = '(T.ly '+str(num)+') '+str(ebin)
        #                        colname = str(ebin)+' [MeV]'+' [t'+num+']'
        #                        columns.append(colname)
        #                        results.append(masked['Value'].loc[ebin])
        #                    # Add the total bin
        #                    colname = 'Total'+' [t'+num+']'
        #                    columns.append(colname)
        #                    results.append(masked_tot['Value'])
        #
        #                else:
        #                    columns.append(tally.tallyComment[0])
        #                    results.append(masked['Value'].values[0])
        #
        #        return results, columns


class SphereOpenMCOutput(OpenMCOutput, SphereTallyOutput):
    def _create_dataframe(self, rows):
        df = pd.DataFrame(
            rows, columns=["Tally N.", "Tally Description", "Energy", "Value", "Error"]
        )
        # rowstotal = [[rows[-1][0], rows[-1][1], 0.0, 0.0]]
        # for row in rows:
        #    rowstotal[0][2] += row[3]
        #    rowstotal[0][3] += row[4] ** 2
        # rowstotal[0][3] = np.sqrt(rowstotal[0][3])
        tallies = df["Tally N."].unique().tolist()
        descriptions = df["Tally Description"].unique().tolist()
        rowstotal = []
        for tally, description in zip(tallies, descriptions):
            value = df.loc[df["Tally N."] == tally, "Value"].sum()
            error = np.sqrt((df.loc[df["Tally N."] == tally, "Error"] ** 2).sum())
            rowstotal.append([tally, description, value, error])
        dftotal = pd.DataFrame(
            rowstotal, columns=["Tally N.", "Tally Description", "Value", "Error"]
        )
        return df, dftotal

    def process_tally(self):
        # tallydata = {}
        # totalbin = {}
        rows = []
        for line in self.output_file_data:
            if "tally" in line.lower():
                # if len(rows) > 0:
                #    tallydata[tally_n], totalbin[tally_n] = self._create_dataframe(rows)
                #    rows = []
                parts = line.split()
                tally_n = int(parts[2].replace(":", ""))
                tally_description = " ".join([parts[3].title(), parts[4].title()])
            if "incoming energy" in line.lower():
                parts = line.split()
                energy = 1e-6 * float(parts[3].replace(")", ""))
            if "flux" in line.lower():
                if ":" in line:
                    continue
                else:
                    parts = line.split()
                    value, error = float(parts[1]), float(parts[3])
                    rows.append([tally_n, tally_description, energy, value, error])
        tallydata, totalbin = self._create_dataframe(rows)
        return tallydata, totalbin


class SphereSDDRoutput(SphereOutput):
    times = ["0s", "2.7h", "24h", "11.6d", "30d", "10y"]
    timecols = {
        "0s": "1.0",
        "2.7h": "2.0",
        "24h": "3.0",
        "11.6d": "4.0",
        "30d": "5.0",
        "10y": "6.0",
    }

    def pp_excel_single(self):
        """
        Generate the single library results excel

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), "templates", "SphereSDDR_single.xlsx")
        outpath = os.path.join(
            self.excel_path, "SphereSDDR_single_" + self.lib + ".xlsx"
        )
        # compute the results
        results, errors, stat_checks = self._compute_single_results()

        # Write excel
        ex = SphereExcelOutputSheet(template, outpath)
        # Results
        ex.insert_df(11, 2, results, 0, header=False)
        ex.insert_df(11, 2, errors, 1, header=False)
        ex.insert_df(9, 2, stat_checks, 2, header=True)
        lib_name = self.session.conf.get_lib_name(self.lib)
        ex.wb.sheets[0].range("E1").value = lib_name
        ex.save()

    def pp_excel_comparison(self):
        """
        Generate the excel comparison output

        Returns
        -------
        None.

        """
        template = os.path.join(os.getcwd(), "templates", "SphereSDDR_comparison.xlsx")

        for reflib, tarlib, name in self.couples:
            outpath = os.path.join(
                self.excel_path, "Sphere_comparison_" + name + ".xlsx"
            )
            final, absdiff = self._compute_compare_result(reflib, tarlib)

            # --- Write excel ---
            # Generate the excel
            ex = SphereExcelOutputSheet(template, outpath)
            # Prepare the copy of the comparison sheet
            ws_comp = ex.wb.sheets["Comparison"]
            ws_diff = ex.wb.sheets["Comparison (Abs diff)"]

            # WRITE RESULTS
            # Percentage comparison
            rangeex = ws_comp.range("B11")
            rangeex.options(index=True, header=False).value = final
            ws_comp.range("E1").value = name

            # Absolute difference comparison
            rangeex = ws_diff.range("B11")
            rangeex.options(index=True, header=False).value = absdiff

            # Add single pp sheets
            for lib in [reflib, tarlib]:
                cp = self.session.state.get_path("single", [lib, "SphereSDDR", "Excel"])
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

    def _generate_plots(self, libraries, allzaids, outputs, globalname, outpath):
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
        template = os.path.join(self.code_path, "templates", "AtlasTemplate.docx")
        atlas = at.Atlas(template, "Sphere SDDR " + globalname)
        libmanager = self.session.lib_manager

        # ------------- Binned plots of gamma flux ------------
        atlas.doc.add_heading("Photon Flux (32)", level=1)
        fluxquantity = "Photon Flux"
        fluxunit = r"$p/(cm^2\cdot\#_S)$"
        allzaids.sort()
        # --- Binned plots of the gamma flux ---
        for zaidnum, mt in tqdm(allzaids, desc=" Binned flux plots"):
            # Get everything for the title of the zaid
            try:
                name, formula = libmanager.get_zaidname(zaidnum)
                args = [zaidnum, name, formula, mt]
                title = "Zaid: {} ({} {}), MT={}".format(*args)
                # For zaids cooldown time does not change anything
                # Keep the multiple times only for materials
                times = [self.times[0]]
            except ValueError:  # A material is passed instead of zaid
                matname = self.mat_settings.loc[zaidnum, "Name"]
                title = zaidnum + " (" + matname + ")"
                times = self.times
            atlas.doc.add_heading(title, level=2)

            for time in times:
                atlas.doc.add_heading("Cooldown time = {}".format(time), level=3)
                title = "Gamma Leakage flux after a {} cooldown".format(time)
                data = []
                for lib in libraries:
                    try:  # Zaid could not be common to the libraries
                        outp = self.outputs[zaidnum, mt, lib]
                    except KeyError:
                        # It is ok, simply nothing to plot here since zaid was
                        # not in library
                        continue
                    # Get the zaid flux
                    tally_data = outp.tallydata[32].set_index("Time")

                    # Select the correct time
                    t = "F" + self.timecols[time]
                    tally_data = tally_data.loc[t]
                    # If for some reason a total survived just kill him
                    tally_data = tally_data[tally_data.Energy != "total"]

                    energy = tally_data["Energy"].values
                    values = tally_data["Value"].values
                    error = tally_data["Error"].values
                    lib_name = self.session.conf.get_lib_name(lib)
                    ylabel = "{}_{} ({})".format(formula, mt, lib_name)
                    libdata = {"x": energy, "y": values, "err": error, "ylabel": ylabel}
                    data.append(libdata)

                outname = "{}-{}-{}-{}-{}".format(zaidnum, mt, globalname, 32, t)
                plot = plotter.Plotter(
                    data,
                    title,
                    outpath,
                    outname,
                    fluxquantity,
                    fluxunit,
                    "Energy [MeV]",
                    self.testname,
                )
                outfile = plot.plot("Binned graph")
                atlas.insert_img(outfile)

        # --- Wave plots flux ---
        # Do this block only if libs are more than one
        lim = 35  # limit of zaids to be in a single plot
        # Plot parameters which are not going to change
        quantity = ["Neutron Flux", "Photon Flux", "SDDR"]
        unit = [r"$n/(cm^2\cdot n_S)$", r"$p/(cm^2\cdot n_S)$", "Sv/h"]
        xlabel = "Zaid/Material and MT value"
        if len(libraries) > 1:
            atlas.doc.add_heading("Flux and SDDR ratio plots", level=1)
            # 1) collect zaid-mt couples in libraries and keep only the ones
            #    that appears on the reference + at least one lib
            # Build a df will all possible zaid, mt, lib combination
            allkeys = list(self.outputs.keys())
            df = pd.DataFrame(allkeys)
            df.columns = ["zaid", "mt", "lib"]
            df["zaid-mt"] = df["zaid"].astype(str) + "-" + df["mt"].astype(str)
            df.set_index("lib", inplace=True)
            # get the reference zaids
            refzaids = set(df.loc[self.lib[0]]["zaid-mt"].values)
            otherzaids = set(df.drop(self.lib[0])["zaid-mt"].values)
            # Get the final zaid-mt couples to consider
            zaid_couples = []
            mat_couples = []
            for zaidmt in refzaids:
                if zaidmt in otherzaids:
                    zaid, mt = zaidmt.split("-")
                    if zaid[0] in "mM":
                        mat_couples.append((zaid, mt))
                    else:
                        zaid_couples.append((zaid, mt))
            # sort it
            zaid_couples.sort(key=self._sortfunc_zaidMTcouples)
            mat_couples.sort(key=self._sortfunc_zaidMTcouples)

            # # There is going to be a plot for each cooldown time
            # Only one plot necessary for zaids at cd=0

            # 2) Recover/compute the data that needs to be plot for each lib
            data = []
            time = self.times[0]
            for lib in self.lib:
                nfluxs = []
                pfluxs = []
                sddrs = []
                xlabels = []
                ylabel = self.session.conf.get_lib_name(lib)
                for zaid, mt in zaid_couples:
                    # Extract values
                    nflux, pflux, sddr = self._extract_data4plots(zaid, mt, lib, time)
                    # Memorize values
                    nfluxs.append(nflux)
                    pfluxs.append(pflux)
                    sddrs.append(sddr)
                    name, formula = libmanager.get_zaidname(zaid)
                    xlabels.append(formula + " " + mt)

                # Split the data if its length is more then the limit
                datalenght = len(xlabels)
                sets = math.ceil(datalenght / lim)
                last_idx = 0
                idxs = []
                step = int(datalenght / sets)
                for _ in range(sets):
                    newidx = last_idx + step
                    idxs.append((last_idx, newidx))
                    last_idx = newidx

                for j, (start, end) in enumerate(idxs):
                    # build the dic
                    ydata = [nfluxs[start:end], pfluxs[start:end], sddrs[start:end]]
                    xlab = xlabels[start:end]
                    libdata = {"x": xlab, "y": ydata, "err": [], "ylabel": ylabel}
                    # try to append it to the data in the correct index
                    # if the index is not found, then the list still needs
                    # to be initialized
                    try:
                        data[j].append(libdata)
                    except IndexError:
                        data.append([libdata])

            # 3) Compute parameters for the plotter init
            refname = self.session.conf.get_lib_name(self.lib[0])
            for datapiece in data:
                title = "Ratio Vs {} (T0 + {})".format(refname, time)
                outname = "dummy"  # Does not matter if plot is added imm.
                testname = self.testname
                plot = plotter.Plotter(
                    datapiece, title, outpath, outname, quantity, unit, xlabel, testname
                )
                outfile = plot.plot("Waves")
                atlas.insert_img(outfile)

            # --- Single wave plot for each material ---
            atlas.doc.add_heading("Materials ratio plot", level=1)
            xlab = self.times
            quantity = ["Neutron Flux", "Photon Flux", "SDDR"]
            unit = ["", "", ""]
            xlabel = "Cooldown time"
            for material, _ in tqdm(mat_couples, desc=" Materials: "):
                atlas.doc.add_heading(material, level=2)
                data = []
                for lib in self.lib:
                    ylabel = self.session.conf.get_lib_name(lib)
                    nfluxs = []
                    pfluxs = []
                    sddrs = []
                    for time in self.times:
                        nflux, pflux, sddr = self._extract_data4plots(
                            material, "All", lib, time
                        )
                        # Memorize
                        nfluxs.append(nflux)
                        pfluxs.append(pflux)
                        sddrs.append(sddr)

                    # Build the lib data
                    ydata = [nfluxs, pfluxs, sddrs]

                    libdata = {"x": xlab, "y": ydata, "err": [], "ylabel": ylabel}
                    data.append(libdata)

                # Plot
                refname = self.session.conf.get_lib_name(self.lib[0])
                matname = self.mat_settings.loc[material, "Name"]
                title = "Ratio Vs {} ({})".format(refname, matname)
                outname = "dummy"  # Does not matter if plot is added imm.
                testname = self.testname
                plot = plotter.Plotter(
                    data, title, outpath, outname, quantity, unit, xlabel, testname
                )
                outfile = plot.plot("Waves")
                atlas.insert_img(outfile)

        ########
        print(" Building...")
        atlas.save(self.atlas_path)
        # Remove tmp images
        shutil.rmtree(outpath)

    def _extract_data4plots(self, zaid, mt, lib, time):
        tallies = self.outputs[zaid, mt, lib].tallydata
        # Extract values
        nflux = tallies[12].set_index("Energy").drop("total")
        nflux = nflux.sum().loc["Value"]
        pflux = tallies[22].groupby("Time").sum().loc[1, "Value"]
        sddr = tallies[104].set_index("Time")
        sddr = sddr.loc["D" + self.timecols[time], "Value"]
        # Memorize values
        return nflux, pflux, sddr

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
        desc = " Parsing Outputs: "
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
            df.set_index(["Parent", "Parent Name", "MT"], inplace=True)
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
        absdiff = ref - tar
        final = absdiff / ref

        # If it is zero the CS are equal! (NaN if both zeros)
        for df in [final, absdiff]:
            df[df == np.nan] = "Not Available"
            df[df == 0] = "Identical"

        return final, absdiff

    @staticmethod
    def _sort_df(df):
        df["index"] = pd.to_numeric(df["Parent"].values, errors="coerce")
        df.sort_values("index", inplace=True)
        del df["index"]

        df.set_index(["Parent", "Parent Name", "MT"], inplace=True)
        df.reset_index(inplace=True)

    @staticmethod
    def _sortfunc_zaidMTcouples(item):
        try:
            zaid = int(item[0])
        except ValueError:
            zaid = item[0]
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
        pieces = folder.split("_")
        # Get zaid
        zaidnum = pieces[1]
        # Check for material exception
        try:
            zaidname = self.mat_settings.loc[zaidnum, "Name"]
            mt = "All"
        except KeyError:
            # it is a simple zaid
            zaidname = pieces[2]
            mt = pieces[3]
        # Get mfile
        for file in os.listdir(results_path):
            if file[-1] == "m":
                mfile = file
            elif file[-1] == "o":
                ofile = file
        # Parse output
        output = SphereSDDRMCNPoutput(
            os.path.join(results_path, mfile), os.path.join(results_path, ofile)
        )
        self.outputs[zaidnum, mt, lib] = output
        # Adjourn raw Data
        self.raw_data[zaidnum, mt, lib] = output.tallydata
        # Recover statistical checks
        st_ck = output.stat_checks
        # Recover results and precisions
        res, err = output.get_single_excel_data()
        for series in [res, err, st_ck]:
            series["Parent"] = zaidnum
            series["Parent Name"] = zaidname
            series["MT"] = mt

        return res, err, st_ck

    def print_raw(self):
        for key, data in self.raw_data.items():
            # build a folder containing each tally of the reaction
            foldername = "{}_{}".format(key[0], key[1])
            folder = os.path.join(self.raw_path, foldername)
            os.mkdir(folder)
            # Dump all tallies
            for tallynum, df in data.items():
                filename = "{}_{}_{}.csv".format(key[0], key[1], tallynum)
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
        nflux = self.tallydata[12]
        pflux = self.tallydata[32]
        sddr = self.tallydata[104]
        heat = self.tallydata[46]

        # Differentiate time labels
        pflux["Time"] = "F" + pflux["Time"].astype(str)
        sddr["Time"] = "D" + sddr["Time"].astype(str)
        heat["Time"] = "H" + heat["Time"].astype(str)

        # Get the total values of the flux at different cooling times
        pfluxvals = pflux.groupby("Time").sum()["Value"]
        # Get the mean error of the flux at different cooling times
        pfluxerrors = pflux.groupby("Time").mean()["Error"]

        # Get the total values of the SDDR at different cooling times
        sddrvals = sddr.groupby("Time").sum()["Value"]
        # Get the mean error of the SDDR at different cooling times
        sddrerrors = sddr.groupby("Time").mean()["Error"]

        # Get the total Heating at different cooling times
        heatvals = heat.set_index("Time")["Value"]
        # Get the Heating mean error at different cooling times
        heaterrors = heat.set_index("Time")["Error"]

        # Neutron flux binned in energy
        nfluxvals = nflux.set_index("Energy")["Value"]
        # Errors of the neutron flux
        nfluxerrors = nflux.set_index("Energy")["Error"]

        # Delete the total row in case it is there
        for df, tag in zip(
            [pfluxvals, pfluxerrors, sddrvals, sddrerrors, heatvals, heaterrors],
            ["F", "F", "D", "D", "H", "H"],
        ):
            try:
                del df[tag + "total"]
            except KeyError:
                # If total value is not there it is ok
                pass

        # Do the same for the flux
        for df in [nfluxvals, nfluxerrors]:
            try:
                del df["total"]
            except KeyError:
                # If total value is not there it is ok
                pass

        # 2 series need to be built here, one for values and one for errors
        vals = pd.concat([pfluxvals, sddrvals, heatvals, nfluxvals], axis=0)
        errors = pd.concat([pfluxerrors, sddrerrors, heaterrors, nfluxerrors], axis=0)

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
        #        self.app = xw.App(visible=False)
        #        self.wb = self.app.books.open(outpath)
        # self.wb=openpyxl.load_workbook(filename=outpath)

    def insert_df(self, startrow, startcolumn, df, ws, header=True):
        """
        Insert a DataFrame (df) into a Worksheet (ws) using openpyxl.
        (startrow) and (startcolumn) identify the starting data entry
        """
        #        ws = self.wb.sheets[ws]
        ws = self.wb[self.wb.sheetnames[ws]]

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
            ws = self.wb.sheets(template_sheet.name + " (2)")
        # except pythoncom.com_error:
        except Exception as e:
            print("The available sheets are :" + str(self.wb.sheets))
        try:
            ws.name = newname
        # except pythoncom.com_error:
        except Exception as e:
            ws.Name = newname
        return ws

    def save(self):
        """
        Save Excel
        """
        #        self.app.calculate()
        self.wb.save(self.outpath)

    #        self.wb.close()
    #        self.app.quit()
