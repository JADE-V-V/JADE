# -*- coding: utf-8 -*-

# Created on Thu Jan  2 10:36:38 2020

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


import jade.MCTAL_READER2 as mtal

# import xlwings as xw
import pandas as pd
import os
import shutil
import jade.plotter as plotter
import jade.excelsupport as exsupp
from tqdm import tqdm
import jade.atlas as at
import numpy as np
import string
from jade.outputFile import OutputFile
from jade.meshtal import Meshtal
import pickle
import sys
import abc

# RED color
CRED = "\033[91m"
CEND = "\033[0m"


class AbstractOutput(abc.ABC):
    @abc.abstractmethod
    def single_postprocess(self):
        """
        To be executed when a single pp is requested
        """
        pass

    @abc.abstractmethod
    def compare(self):
        """
        To be executed when a comparison is requested
        """

    @staticmethod
    def _get_output_files(results_path):
        """
        Recover the meshtal and outp file from a directory

        Parameters
        ----------
        results_path : str or path
            path where the MCNP results are contained.

        Raises
        ------
        FileNotFoundError
            if either meshtal or outp are not found.

        Returns
        -------
        mfile : path
            path to the meshtal file
        ofile : path
            path to the outp file

        """
        # Get mfile
        mfile = None
        ofile = None

        for file in os.listdir(results_path):
            if file[-1] == "m":
                mfile = file
            elif file[-1] == "o":
                ofile = file

        if mfile is None or ofile is None:
            raise FileNotFoundError(
                """
 The followig path does not contain either the .m or .o file:
 {}""".format(
                    results_path
                )
            )

        mfile = os.path.join(results_path, mfile)
        ofile = os.path.join(results_path, ofile)

        return mfile, ofile


class BenchmarkOutput(AbstractOutput):
    def __init__(self, lib, config, session):
        """
        General class for a Benchmark output

        Parameters
        ----------
        lib : str
            library to post-process
        config : pd.DataFrame (single row)
            configuration options for the test.
        session : Session
            Jade Session
        exp : str
            the benchmark is an experimental one

        Returns
        -------
        None.

        """
        self.raw_data = {}  # Raw data
        self.outputs = {}  # outputs linked to the benchmark
        self.testname = config["Folder Name"]  # test name
        self.code_path = os.getcwd()  # path to code
        self.state = session.state
        self.session = session
        self.path_templates = session.path_templates

        # Read specific configuration
        cnf_path = os.path.join(session.path_cnf, self.testname + ".xlsx")
        if os.path.isfile(cnf_path):
            self.cnf_path = cnf_path
        # It can be assumed that there is a folder containing multiple files
        else:
            self.cnf_path = os.path.join(session.path_cnf, self.testname)

        # Updated to handle multiple codes
        try:
            self.mcnp = bool(config["MCNP"])
            self.raw_data["mcnp"] = {}
            self.outputs["mcnp"] = {}
        except KeyError:
            self.mcnp = False
        try:
            self.serpent = bool(config["Serpent"])
            self.raw_data["serpent"] = {}
            self.outputs["serpent"] = {}
        except KeyError:
            self.serpent = False
        try:
            self.openmc = bool(config["OpenMC"])
            self.raw_data["openmc"] = {}
            self.outputs["openmc"] = {}
        except KeyError:
            self.openmc = False
        try:
            self.d1s = bool(config["d1S"])
            self.raw_data["d1s"] = {}
            self.outputs["d1s"] = {}
        except KeyError:
            self.d1s = False

        # COMPARISON
        if isinstance(lib, list) and len(lib) > 1:
            self.single = False  # Indicator for single or comparison
            self.lib = lib
            couples = []
            tp = os.path.join(session.path_run, lib[0], self.testname)
            self.test_path = {lib[0]: tp}
            refname = session.conf.get_lib_name(lib[0])
            name = refname
            dirname = lib[0]
            for library in lib[1:]:
                libname = session.conf.get_lib_name(library)
                # name_couple = lib[0]+'_Vs_'+library
                name_couple = lib[0] + "_Vs_" + library
                name = name + "_Vs_" + libname
                dirname = dirname + "_Vs_" + library
                couples.append((lib[0], library, name_couple))
                tp = os.path.join(session.path_run, library, self.testname)
                self.test_path[library] = tp

            self.name = name
            # Generate library output path
            out = os.path.join(session.path_comparison, dirname)
            if not os.path.exists(out):
                os.mkdir(out)

            out = os.path.join(out, self.testname)
            if os.path.exists(out):
                shutil.rmtree(out)
            os.mkdir(out)
            if self.mcnp:
                excel_path_mcnp = os.path.join(out, "mcnp" ,"Excel")
                atlas_path_mcnp = os.path.join(out, "mcnp" ,"Atlas")
                raw_path_mcnp = os.path.join(out, "mcnp" ,"Raw_Data")
                os.makedirs(excel_path_mcnp)
                os.makedirs(atlas_path_mcnp)
                os.makedirs(raw_path_mcnp)
                self.excel_path_mcnp = excel_path_mcnp
                self.raw_path_mcnp = raw_path_mcnp
                self.atlas_path_mcnp = atlas_path_mcnp
            if self.openmc:
                excel_path_openmc = os.path.join(out, "openmc" ,"Excel")
                atlas_path_openmc = os.path.join(out, "openmc" ,"Atlas")
                raw_path_openmc = os.path.join(out, "openmc" ,"Raw_Data")
                os.makedirs(excel_path_openmc)
                os.makedirs(atlas_path_openmc)
                os.makedirs(raw_path_openmc)
                self.excel_path_openmc = excel_path_openmc
                self.raw_path_openmc = raw_path_openmc
                self.atlas_path_openmc = atlas_path_openmc
            if self.serpent:
                excel_path_serpent = os.path.join(out, "serpent" ,"Excel")
                atlas_path_serpent = os.path.join(out, "serpent" ,"Atlas")
                raw_path_serpent = os.path.join(out, "serpent" ,"Raw_Data")
                os.makedirs(excel_path_serpent)
                os.makedirs(atlas_path_serpent)
                os.makedirs(raw_path_serpent)
                self.excel_path_serpent = excel_path_serpent
                self.raw_path_serpent = raw_path_serpent
                self.atlas_path_serpent = atlas_path_serpent
            if self.d1s:
                excel_path_d1s = os.path.join(out, "d1s" ,"Excel")
                atlas_path_d1s = os.path.join(out, "d1s" ,"Atlas")
                raw_path_d1s = os.path.join(out, "d1s" ,"Raw_Data")
                os.makedirs(excel_path_d1s)
                os.makedirs(atlas_path_d1s)
                os.makedirs(raw_path_d1s)
                self.excel_path_d1s = excel_path_d1s
                self.raw_path_d1s = raw_path_d1s
                self.atlas_path_d1s = atlas_path_d1s

            self.couples = couples  # Couples of libraries to post process
        # SINGLE-LIBRARY
        else:
            self.single = True  # Indicator for single or comparison
            if isinstance(lib, list) and len(lib) == 1:
                self.lib = lib[0]  # In case of 1-item list
            else:
                self.lib = lib
            self.test_path = os.path.join(session.path_run, lib, self.testname)

            # Generate library output path
            out = os.path.join(session.path_single, lib)
            if not os.path.exists(out):
                os.mkdir(out)

            out = os.path.join(out, self.testname)
            if os.path.exists(out):
                shutil.rmtree(out)
            os.mkdir(out)
            if self.mcnp:
                excel_path_mcnp = os.path.join(out, "mcnp" ,"Excel")
                atlas_path_mcnp = os.path.join(out, "mcnp" ,"Atlas")
                raw_path_mcnp = os.path.join(out, "mcnp" ,"Raw_Data")
                os.makedirs(excel_path_mcnp)
                os.makedirs(atlas_path_mcnp)
                os.makedirs(raw_path_mcnp)
                self.excel_path_mcnp = excel_path_mcnp
                self.raw_path_mcnp = raw_path_mcnp
                self.atlas_path_mcnp = atlas_path_mcnp
            if self.openmc:
                excel_path_openmc = os.path.join(out, "openmc" ,"Excel")
                atlas_path_openmc = os.path.join(out, "openmc" ,"Atlas")
                raw_path_openmc = os.path.join(out, "openmc" ,"Raw_Data")
                os.makedirs(excel_path_openmc)
                os.makedirs(atlas_path_openmc)
                os.makedirs(raw_path_openmc)
                self.excel_path_openmc = excel_path_openmc
                self.raw_path_openmc = raw_path_openmc
                self.atlas_path_openmc = atlas_path_openmc
            if self.serpent:
                excel_path_serpent = os.path.join(out, "serpent" ,"Excel")
                atlas_path_serpent = os.path.join(out, "serpent" ,"Atlas")
                raw_path_serpent = os.path.join(out, "serpent" ,"Raw_Data")
                os.makedirs(excel_path_serpent)
                os.makedirs(atlas_path_serpent)
                os.makedirs(raw_path_serpent)
                self.excel_path_serpent = excel_path_serpent
                self.raw_path_serpent = raw_path_serpent
                self.atlas_path_serpent = atlas_path_serpent
            if self.d1s:
                excel_path_d1s = os.path.join(out, "d1s" ,"Excel")
                atlas_path_d1s = os.path.join(out, "d1s" ,"Atlas")
                raw_path_d1s = os.path.join(out, "d1s" ,"Raw_Data")
                os.makedirs(excel_path_d1s)
                os.makedirs(atlas_path_d1s)
                os.makedirs(raw_path_d1s)
                self.excel_path_d1s = excel_path_d1s
                self.raw_path_d1s = raw_path_d1s
                self.atlas_path_d1s = atlas_path_d1s

    def single_postprocess(self):
        """
        Execute the full post-processing of a single library (i.e. excel,
        raw data and atlas)

        Returns
        -------
        None.

        """
        print(" Generating Excel Recap...")
        self._generate_single_excel_output()
        self._print_raw()

        print(" Creating Atlas...")
        if self.mcnp:
            outpath = os.path.join(self.atlas_path_mcnp, "tmp")
        os.mkdir(outpath)

        # Get atlas configuration
        atl_cnf = pd.read_excel(self.cnf_path, sheet_name="Atlas")
        atl_cnf.set_index("Tally", inplace=True)

        # Printing Atlas
        template = template = os.path.join(self.path_templates, "AtlasTemplate.docx")
        atlas = at.Atlas(template, self.testname + "_" + self.lib)

        # Iterate over each type of plot (first one is quantity
        # and second one the measure unit)
        for plot_type in list(atl_cnf.columns)[2:]:
            print(" Plotting : " + plot_type)
            atlas.doc.add_heading("Plot type: " + plot_type, level=1)
            # Keep only tallies to plot
            atl_cnf_plot = atl_cnf[atl_cnf[plot_type]]
            for tally_num in tqdm(atl_cnf_plot.index, desc="Tallies"):
                print(tally_num)
                try:
                    if self.mcnp:
                        print(self.outputs["mcnp"])
                        output = self.outputs["mcnp"][tally_num]
                except KeyError:
                    fatal_exception(
                        "tally n. "
                        + str(tally_num)
                        + " is in config but not in the MCNP output"
                    )
                vals_df = output["Value"]
                err_df = output["Error"]
                quantity = str(atl_cnf_plot["Quantity"].loc[tally_num])
                unit = str(atl_cnf_plot["Unit"].loc[tally_num])
                xlabel = output["x_label"]
                title = output["title"]

                atlas.doc.add_heading("Tally: " + title, level=2)

                columns = vals_df.columns
                x = np.array(vals_df.index)

                for column in tqdm(columns):
                    if len(columns) > 1:
                        try:
                            txt = str(int(column))
                        except ValueError:
                            # it is not convertible to int
                            txt = str(column)

                        atlas.doc.add_heading(txt, level=3)
                        newtitle = title + " (" + txt + ")"
                    else:
                        newtitle = title

                    # If total is present it has to be deleted
                    try:
                        vals_df.drop(["total"], inplace=True)
                        err_df.drop(["total"], inplace=True)
                        x = x[:-1]
                    except KeyError:
                        pass

                    try:
                        values = vals_df[column].values
                        error = err_df[column].values
                    except KeyError:
                        # this means that the column is only one and we have
                        # two distinct DFs for values and errors
                        values = vals_df["Value"]
                        error = err_df["Error"]

                    lib_name = self.session.conf.get_lib_name(self.lib)
                    lib = {
                        "x": x,
                        "y": values,
                        "err": error,
                        "ylabel": lib_name}
                    data = [lib]

                    outname = "tmp"
                    plot = plotter.Plotter(
                        data,
                        newtitle,
                        outpath,
                        outname,
                        quantity,
                        unit,
                        xlabel,
                        self.testname,
                    )
                    img_path = plot.plot(plot_type)

                    atlas.insert_img(img_path)
        if self.mcnp:
            atlas.save(self.atlas_path_mcnp)
        # Remove tmp images
        shutil.rmtree(outpath)

    def compare(self):
        """
        Generates the full comparison post-processing (excel and atlas)

        Returns
        -------
        None.

        """
        print(" Generating Excel Recap...")
        self._generate_comparison_excel_output()

        print(" Creating Atlas...")
        if self.mcnp:
            outpath = os.path.join(self.atlas_path_mcnp, "tmp")
        os.mkdir(outpath)

        # Get atlas configuration
        atl_cnf = pd.read_excel(self.cnf_path, sheet_name="Atlas")
        atl_cnf.set_index("Tally", inplace=True)

        # Printing Atlas
        template = os.path.join(self.path_templates, "AtlasTemplate.docx")

        atlas = at.Atlas(template, self.testname + "_" + self.name)

        # Recover data
        outputs_dic = {}
        for lib in self.lib:
            # Recover lib output
            if self.mcnp:
                out_path = os.path.join(
                    self.session.path_single,
                    lib, self.testname, 
                    "mcnp", "Raw_Data", 
                    lib + ".pickle"
                )
            with open(out_path, "rb") as handle:
                outputs = pickle.load(handle)
            outputs_dic[lib] = outputs

        # Iterate over each type of plot (first one is quantity
        # and second one the measure unit)
        for plot_type in list(atl_cnf.columns)[2:]:
            print(" Plotting : " + plot_type)
            atlas.doc.add_heading("Plot type: " + plot_type, level=1)
            # Keep only tallies to plot
            atl_cnf_plot = atl_cnf[atl_cnf[plot_type]]
            for tally_num in tqdm(atl_cnf_plot.index, desc="Tallies"):
                # The last 'outputs' can be easily used for common data
                try:
                    if self.mcnp:
                        output = self.outputs["mcnp"][tally_num]
                except KeyError:
                    fatal_exception(
                        "tally n. "
                        + str(tally_num)
                        + " is in config but not in the MCNP output"
                    )
                vals_df = output["Value"]
                err_df = output["Error"]
                quantity = str(atl_cnf_plot["Quantity"].loc[tally_num])
                unit = str(atl_cnf_plot["Unit"].loc[tally_num])
                xlabel = output["x_label"]
                title = output["title"]

                atlas.doc.add_heading("Tally: " + title, level=2)

                columns = vals_df.columns

                for column in tqdm(columns):
                    if len(columns) > 1:
                        try:
                            txt = str(int(column))
                        except ValueError:
                            # it is not convertible to int
                            txt = str(column)

                        atlas.doc.add_heading(txt, level=3)
                        newtitle = title + " (" + txt + ")"

                    else:
                        newtitle = title
                    data = []
                    for lib in self.lib:
                        output = outputs_dic[lib][tally_num]

                        # override values and errors
                        try:
                            vals_df = output["Value"]
                            err_df = output["Error"]
                            # If total is present it has to be deleted
                            try:
                                vals_df.drop(["total"], inplace=True)
                                err_df.drop(["total"], inplace=True)
                            except KeyError:
                                pass
                            values = vals_df[column].values
                            error = err_df[column].values

                        except KeyError:
                            # this means that the column is only one and we
                            # havetwo distinct DFs for values and errors
                            values = vals_df["Value"].values
                            error = err_df["Error"].values

                        x = np.array(vals_df.index)

                        lib_name = self.session.conf.get_lib_name(lib)
                        lib_data = {
                            "x": x,
                            "y": values,
                            "err": error,
                            "ylabel": lib_name,
                        }
                        data.append(lib_data)

                    outname = "tmp"
                    plot = plotter.Plotter(
                        data,
                        newtitle,
                        outpath,
                        outname,
                        quantity,
                        unit,
                        xlabel,
                        self.testname,
                    )
                    img_path = plot.plot(plot_type)

                    atlas.insert_img(img_path)
        if self.mcnp:
            atlas.save(self.atlas_path_mcnp)

        # Remove tmp images
        shutil.rmtree(outpath)

    @staticmethod
    def _reorder_df(df, x_set):
        # First of all try order by number
        df["index"] = pd.to_numeric(df[x_set], errors="coerce")

        # If they are all nan try with a normal sort
        if df["index"].isnull().values.all():
            df.sort_values(x_set, inplace=True)

        # Otherwise keep on with the number sorting
        else:
            df.sort_values("index", inplace=True)

        del df["index"]

        # Try to reorder the columns
        try:
            df = df.reindex(sorted(df.columns), axis=1)
        except TypeError:
            # They are a mix of strings and ints, let's ignore it for
            # the time being
            pass

        return df

    def _generate_single_excel_output(self):
        # Get excel configuration
        self.outputs = {}
        self.results = {}
        self.errors = {}
        self.stat_checks = {}
        ex_cnf = pd.read_excel(self.cnf_path, sheet_name="Excel")
        ex_cnf.set_index("Tally", inplace=True)

        # Open the excel file
        #name = "Generic_single.xlsx"
        #template = os.path.join(os.getcwd(), "templates", name)
        if self.mcnp:
            outpath = os.path.join(
                self.excel_path_mcnp, self.testname + "_" + self.lib + ".xlsx"
            )
            outputs = {}
            #ex = ExcelOutputSheet(template, outpath)
            # Get results
            # results = []
            # errors = []
            results_path = os.path.join(self.test_path, "mcnp")

            # Get mfile and outfile and possibly meshtal file
            meshtalfile = None
            for file in os.listdir(results_path):
                if file[-1] == "m":
                    mfile = os.path.join(results_path, file)
                elif file[-1] == "o":
                    ofile = os.path.join(results_path, file)
                elif file[-4:] == "msht":
                    meshtalfile = os.path.join(results_path, file)
            # Parse output
            mcnp_output = MCNPoutput(mfile, ofile, meshtal_file=meshtalfile)
            mctal = mcnp_output.mctal
            # Adjourn raw Data
            self.raw_data = mcnp_output.tallydata

            # res, err = output.get_single_excel_data()
           

            for label in ["Value", "Error"]:
                # keys = {}
                for tally in mctal.tallies:
                    num = tally.tallyNumber
                    key = tally.tallyComment[0]
                    # keys[num] = key  # Memorize tally descriptions
                    tdata = mcnp_output.tallydata[num].copy()  # Full tally data
                    try:
                        tally_settings = ex_cnf.loc[num]
                    except KeyError:
                        print(
                            " Warning!: tally n." +
                            str(num) +
                            " is not in configuration")
                        continue

                    # Re-Elaborate tdata Dataframe
                    x_name = tally_settings["x"]
                    x_tag = tally_settings["x name"]
                    y_name = tally_settings["y"]
                    y_tag = tally_settings["y name"]
                    ylim = tally_settings["cut Y"]

                    if label == "Value":
                        outputs[num] = {"title": key, "x_label": x_tag}

                    # select the index format
                    if x_name == "Energy":
                        idx_format = "0.00E+00"
                        # TODO all possible cases should be addressed
                    else:
                        idx_format = "0"

                    if y_name != "tally":
                        tdata.set_index(x_name, inplace=True)
                        x_set = list(set(tdata.index))
                        y_set = list(set(tdata[y_name].values))
                        rows = []
                        for xval in x_set:
                            try:
                                row = tdata.loc[xval, label].values
                                prev_len = len(row)
                            except AttributeError:
                                # There is only one total value, fill the rest with
                                # nan
                                row = []
                                for i in range(prev_len - 1):
                                    row.append(np.nan)
                                row.append(tdata.loc[xval, label])

                            rows.append(row)

                        try:
                            main_value_df = pd.DataFrame(
                                rows, columns=y_set, index=x_set)
                            main_value_df.index.name = x_name
                        except ValueError:
                            print(
                                CRED
                                + """
        A ValueError was triggered, a probable cause may be that more than 2 binnings
         are defined in tally {}. This is a fatal exception,  application will now
        close""".format(
                                    str(num)
                                )
                                + CEND
                            )
                            # Safely exit from excel and from application
                            #ex.save()
                            sys.exit()

                        # reorder index (quick reset of the index)
                        main_value_df.reset_index(inplace=True)
                        main_value_df = self._reorder_df(main_value_df, x_name)
                        main_value_df.set_index(x_name, inplace=True)
                        # memorize for atlas
                        outputs[num][label] = main_value_df
                        # insert the df in pieces
                        #ex.insert_cutted_df(
                        #    "B",
                        #    main_value_df,
                        #    label + "s",
                        #    ylim,
                        #    header=(key, "Tally n." + str(num)),
                        #    index_name=x_tag,
                        #    cols_name=y_tag,
                        #    index_num_format=idx_format,
                        #)
                    else:
                        # reorder df
                        try:
                            tdata = self._reorder_df(tdata, x_name)
                        except KeyError:
                            print(
                                CRED
                                + """
 {} is not available in tally {}. Please check the configuration file.
 The application will now exit """.format(
                                    x_name, str(num)
                                )
                                + CEND
                            )
                            # Safely exit from excel and from application
                            #ex.save()
                            sys.exit()

                        if label == "Value":
                            del tdata["Error"]
                        elif label == "Error":
                            del tdata["Value"]
                        # memorize for atlas and set index
                        tdata.set_index(x_name, inplace=True)
                        outputs[num][label] = tdata

                        # Insert DF
                        #ex.insert_df(
                        #    "B",
                        #    tdata,
                        #    label + "s",
                        #    print_index=True,
                        #    header=(key, "Tally n." + str(num)),
                        #)
                # memorize data for atlas
                self.outputs["mcnp"] = outputs
                # print(outputs)
                # Dump them for comparisons
                raw_outpath = os.path.join(self.raw_path_mcnp, self.lib + ".pickle")
                with open(raw_outpath, "wb") as outfile:
                    pickle.dump(outputs, outfile)

                # Compile general infos in the sheet
                #ws = ex.current_ws
                #title = self.testname + " RESULTS RECAP: " + label + "s"
                #ws.range("A3").value = title
                #ws.range("C1").value = self.lib

            # --- Compile statistical checks sheet ---
            #ws = ex.wb.sheets["Statistical Checks"]

            dic_checks = mcnp_output.out.stat_checks
            rows = []
            for tally in mctal.tallies:
                num = tally.tallyNumber
                key = tally.tallyComment[0]
                key_dic = key + " [" + str(num) + "]"
                try:
                    stat = dic_checks[key_dic]
                except KeyError:
                    stat = None
                rows.append([num, key, stat])

            stats = pd.DataFrame(rows)
            stats.columns = ["Tally Number", "Tally Description", "Result"]
            #ws.range("A9").options(index=False, header=False).value = df

            #ex.save()
            exsupp.single_excel_writer(self, outpath, self.lib, self.testname, outputs, stats)

    def _print_raw(self):
        if self.mcnp:    
            for key, data in self.raw_data.items():
                file = os.path.join(self.raw_path_mcnp, str(key) + ".csv")
                data.to_csv(file, header=True, index=False)

    def _generate_comparison_excel_output(self):
        # Get excel configuration
        self.outputs = {}
        self.results = {}
        self.errors = {}
        self.stat_checks = {}
        ex_cnf = pd.read_excel(self.cnf_path, sheet_name="Excel")
        ex_cnf.set_index("Tally", inplace=True)

        # Open the excel file
        #name_tag = "Generic_comparison.xlsx"
        #template = os.path.join(os.getcwd(), "templates", name_tag)

       
        if self.mcnp:
            mcnp_outputs = {}
            comps = {}
            abs_diffs  = {}
            std_devs = {}
            for reflib, tarlib, name in self.couples:
                lib_to_comp = name
                outfolder_path = self.excel_path_mcnp
                outpath = os.path.join(
                    outfolder_path, "Comparison_" + name + "_mcnp.xlsx"
                )

                #ex = ExcelOutputSheet(template, outpath)
                # Get results

                #for lib in to_read:
                #    results_path = self.test_path[lib]
                for lib, results_path in {
                    reflib: os.path.join(self.test_path[reflib], "mcnp"),
                    tarlib: os.path.join(self.test_path[tarlib], "mcnp"),
                }.items():
                    results = []
                    errors = []
                    # Get mfile and outfile and possibly meshtal file
                    meshtalfile = None
                    for file in os.listdir(results_path):
                        if file[-1] == "m":
                            mfile = os.path.join(results_path, file)
                        elif file[-1] == "o":
                            ofile = os.path.join(results_path, file)                        
                        elif file[-4:] == "msht":
                            meshtalfile = os.path.join(results_path, file)
                    # Parse output
                    mcnp_output = MCNPoutput(
                        mfile, ofile, meshtal_file=meshtalfile)
                    mcnp_outputs[lib] = mcnp_output
                # Build the comparison
                for label in ["Value", "Error"]:
                    for tally in mcnp_outputs[reflib].mctal.tallies:
                        num = tally.tallyNumber
                        key = tally.tallyComment[0]

                        # Full tally data
                        tdata_ref = mcnp_outputs[reflib].tallydata[num].copy()
                        tdata_tar = mcnp_outputs[tarlib].tallydata[num].copy()
                        try:
                            tally_settings = ex_cnf.loc[num]
                        except KeyError:
                            print(
                                " Warning!: tally n." +
                                str(num) +
                                " is not in configuration")
                            continue

                        # Re-Elaborate tdata Dataframe
                        x_name = tally_settings["x"]
                        x_tag = tally_settings["x name"]
                        y_name = tally_settings["y"]
                        y_tag = tally_settings["y name"]
                        ylim = tally_settings["cut Y"]
                        # select the index format
                        if label == "Value":
                            for dic in [comps, abs_diffs, std_devs]:
                                dic[num] = {"title": key, "x_label": x_tag}


                        if x_name == "Energy":
                            idx_format = "0.00E+00"
                            # TODO all possible cases should be addressed
                        else:
                            idx_format = "0"

                        if y_name != "tally":
                            tdata_ref.set_index(x_name, inplace=True)
                            tdata_tar.set_index(x_name, inplace=True)
                            x_set = list(set(tdata_ref.index))
                            y_set = list(set(tdata_ref[y_name].values))
                            rows_fin = []
                            rows_abs_diff = []
                            rows_std_dev = []
                            for xval in x_set:
                                try:
                                    ref = tdata_ref.loc[xval, "Value"].values
                                    ref_err = tdata_ref.loc[xval, "Error"].values
                                    tar = tdata_tar.loc[xval, "Value"].values
                                    # !!! True divide warnings are suppressed !!!
                                    with np.errstate(divide="ignore", invalid="ignore"):
                                        row_fin = (ref - tar) / ref
                                        row_abs_diff = (ref - tar)
                                        row_std_dev = row_abs_diff / (ref_err*ref)
                                    prev_len = len(ref)
                                except AttributeError:
                                    # This is raised when total values are
                                    # collected only for one bin.
                                    # the rest needs to be filled by nan
                                    ref = tdata_ref.loc[xval, "Value"]
                                    ref_err = tdata_ref.loc[xval, "Error"]
                                    tar = tdata_tar.loc[xval, "Value"]
                                    for i in range(prev_len - 1):
                                        row_fin.append(np.nan)
                                        row_abs_diff.append(np.nan)
                                        row_std_dev.append(np.nan)
                                    row_fin.append((ref - tar) / ref)
                                    row_abs_diff.append(ref - tar)
                                    row_std_dev.append((ref - tar)/(ref_err*ref))

                                rows_fin.append(row_fin)
                                rows_abs_diff.append(row_abs_diff)
                                rows_std_dev.append(row_std_dev)
                            try:
                                final = pd.DataFrame(
                                    rows_fin, columns=y_set, index=x_set)
                                abs_diff = pd.DataFrame(
                                    rows_abs_diff, columns=y_set, index=x_set)
                                std_dev = pd.DataFrame(
                                    rows_std_dev, columns=y_set, index=x_set)
                                for df in [final, abs_diff, std_dev]:
                                    df.index.name = x_name
                                    df.replace(np.nan, "Not Available", inplace=True)
                                    df.replace(float(0), "Identical", inplace=True)
                                    df.replace(-np.inf, "Reference = 0", inplace=True)
                                    df.replace(1, "Target = 0", inplace=True)
                            except ValueError:
                                print(
                                    CRED
                                    + """
            A ValueError was triggered, a probable cause may be that more than 2 binnings
             are defined in tally {}. This is a fatal exception,  application will now
            close""".format(
                                        str(num)
                                    )
                                    + CEND
                                )
                                # Safely exit from excel and from application
                                sys.exit()

                            # reorder index and quick index reset
                            for df in [final, abs_diff, std_dev]:
                                df.reset_index(inplace=True)
                                df = self._reorder_df(df, x_name)
                                df.set_index(x_name, inplace=True)
                            comps[num][label] = final
                            abs_diffs[num][label] = abs_diff
                            std_devs[num][label] = std_dev
                            # insert the df in pieces
                            #ex.insert_cutted_df(
                            #    "B",
                            #    main_value_df,
                            #    "Comparison",
                            #    ylim,
                            #    header=(key, "Tally n." + str(num)),
                            #    index_name=x_tag,
                            #    cols_name=y_tag,
                            #    index_num_format=idx_format,
                            #    values_format="0.00%",
                            #)
                        else:
                            # reorder dfs
                            try:
                                tdata_ref = self._reorder_df(tdata_ref, x_name)
                            except KeyError:
                                print(
                                    CRED
                                    + """
     {} is not available in tally {}. Please check the configuration file.
     The application will now exit """.format(
                                        x_name, str(num)
                                    )
                                    + CEND
                                )
                                # Safely exit from excel and from application
                                sys.exit()

                            del tdata_ref["Error"]
                            tdata_ref.set_index(x_name, inplace=True)

                            tdata_tar = self._reorder_df(tdata_tar, x_name)
                            del tdata_tar["Error"]
                            tdata_tar.set_index(x_name, inplace=True)

                            # !!! True divide warnings are suppressed !!!
                            with np.errstate(divide="ignore", invalid="ignore"):
                                comp_df = (tdata_ref - tdata_tar) / tdata_ref
                                abs_diff_df = (tdata_ref - tdata_tar)
                                std_dev_df = abs_diff_df
                            comps[num][label] = comp_df
                            abs_diffs[num][label] = abs_diff_df
                            std_devs[num][label] = abs_diff_df
                            # Insert DF
                            #ex.insert_df(
                            #    "B",
                            #    df,
                            #    "Comparison",
                            #    print_index=True,
                            #    header=(key, "Tally n." + str(num)),
                            #    values_format="0.00%",
                            #)

                # Compile general infos in the sheet
                #ws = ex.current_ws
                #title = self.testname + " RESULTS RECAP: Comparison"
                #ws.range("A3").value = title
                #ws.range("C1").value = tarlib + " Vs " + reflib

                # Add single pp sheets
                #for lib in [reflib, tarlib]:
                #    cp = self.state.get_path(
                #        "single", [lib, self.testname, "Excel"])
                #    file = os.listdir(cp)[0]
                #    cp = os.path.join(cp, file)
                #    ex.copy_sheets(cp)

                #ex.save()
                self.outputs["mcnp"] = comps
                exsupp.comp_excel_writer(self, outpath, lib_to_comp, self.testname, comps, abs_diffs, std_devs)


class MCNPoutput:
    def __init__(self, mctal_file, output_file, meshtal_file=None):
        """
        Class representing all outputs coming from and MCNP run

        Parameters
        ----------
        mctal_file : path like object
            path to the mctal file.
        output_file : path like object
            path to the outp file.
        meshtal_file : path like object, optional
            path to the meshtal file. The default is None.

        Returns
        -------
        None.

        """
        self.mctal_file = mctal_file  # path to mcnp mctal file
        self.output_file = output_file  # path to mcnp output file
        self.meshtal_file = meshtal_file  # path to mcnp meshtal file

        # Read and parse the mctal file
        mctal = mtal.MCTAL(mctal_file)
        mctal.Read()
        self.mctal = mctal
        self.tallydata, self.totalbin = self.organize_mctal()

        # Read the output file
        self.out = OutputFile(output_file)
        self.out.assign_tally_description(self.mctal.tallies)
        self.stat_checks = self.out.stat_checks

        # Read the meshtal file
        if meshtal_file is not None:
            self.meshtal = Meshtal(meshtal_file)
            # Extract the available 1D to be merged with normal tallies
            fmesh1D = self.meshtal.extract_1D()
            for tallynum, data in fmesh1D.items():
                tallynum = int(tallynum)  # Coherence with tallies
                # Add them to the tallly data
                self.tallydata[tallynum] = data["data"]
                self.totalbin[tallynum] = None

                # Create fake tallies to be added to the mctal
                faketally = mtal.Tally(tallynum)
                faketally.tallyComment = [data["desc"]]
                self.mctal.tallies.append(faketally)

    def organize_mctal(self):
        """
        Retrieve and organize mctal data into a DataFrame.

        Returns
        -------
        tallydata : pd.DataFrame
            organized tally data.
        totalbin : pd.DataFrame
            organized tally data (only total bins).

        """
        tallydata = {}
        totalbin = {}

        for t in self.mctal.tallies:
            rows = []

            # --- Reorganize values ---
            # You cannot recover the following from the mctal
            nDir = t.getNbins("d", False)
            nMul = t.getNbins("m", False)
            nSeg = t.getNbins("s", False)  # this can be used

            # Some checks for voids
            binnings = {
                "cells": t.cells,
                "user": t.usr,
                "segments": t.seg,
                "cosine": t.cos,
                "energy": t.erg,
                "time": t.tim,
                "cor A": t.cora,
                "cor B": t.corb,
                "cor C": t.corc,
            }

            # Cells may have a series of zeros, the last one may be for the
            # total
            cells = []
            # last_idx = len(binnings['cells'])-1
            for i, cell in enumerate(binnings["cells"]):
                if int(cell) == 0:
                    newval = "Input " + str(i + 1)
                    cells.append(newval)
                # Everything is fine, nothing to modify
                else:
                    cells.append(cell)
            binnings["cells"] = cells

            for name, binning in binnings.items():
                if len(binning) == 0:
                    binnings[name] = [np.nan]
            # Start iteration
            for f, fn in enumerate(binnings["cells"]):
                for d in range(nDir):  # Unused
                    for u, un in enumerate(binnings["user"]):
                        for sn in range(1, nSeg + 1):
                            for m in range(nMul):  # (unused)
                                for c, cn in enumerate(binnings["cosine"]):
                                    for e, en in enumerate(binnings["energy"]):
                                        for nt, ntn in enumerate(
                                                binnings["time"]):
                                            for k, kn in enumerate(
                                                    binnings["cor C"]):
                                                for j, jn in enumerate(
                                                    binnings["cor B"]
                                                ):
                                                    for i, ina in enumerate(
                                                        binnings["cor A"]
                                                    ):
                                                        val = t.getValue(
                                                            f,
                                                            d,
                                                            u,
                                                            sn - 1,
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
                                                            sn - 1,
                                                            m,
                                                            c,
                                                            e,
                                                            nt,
                                                            i,
                                                            j,
                                                            k,
                                                            1,
                                                        )
                                                        rows.append(
                                                            [
                                                                fn,
                                                                d,
                                                                un,
                                                                sn,
                                                                m,
                                                                cn,
                                                                en,
                                                                ntn,
                                                                ina,
                                                                jn,
                                                                kn,
                                                                val,
                                                                err,
                                                            ]
                                                        )

                # Only one total bin per cell is admitted
                val = t.getValue(f, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0)
                err = t.getValue(f, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1)
                if t.timTC is not None:
                    rows.append([fn, d, un, sn, m, cn, en,
                                 "total", ina, jn, kn, val, err])
                    total = "Time"

                elif t.ergTC is not None:
                    rows.append([fn, d, un, sn, m, cn, "total",
                                 ntn, ina, jn, kn, val, err])
                    total = "Energy"

                elif t.segTC is not None:
                    rows.append([fn, d, un, "total", m, cn, en,
                                 ntn, ina, jn, kn, val, err])
                    total = "Segments"

                elif t.cosTC is not None:
                    rows.append([fn, d, un, sn, m, "total", en,
                                 ntn, ina, jn, kn, val, err])
                    total = "Cosine"

                elif t.usrTC is not None:
                    rows.append([fn, d, "total", sn, m, cn, en,
                                 ntn, ina, jn, kn, val, err])
                    total = "User"

            # --- Build the tally DataFrame ---
            columns = [
                "Cells",
                "Dir",
                "User",
                "Segments",
                "Multiplier",
                "Cosine",
                "Energy",
                "Time",
                "Cor C",
                "Cor B",
                "Cor A",
                "Value",
                "Error",
            ]
            df = pd.DataFrame(rows, columns=columns)

            # Default drop of multiplier and Dir
            del df["Dir"]
            del df["Multiplier"]
            # --- Keep only meaningful binning ---
            # Drop NA
            df.dropna(axis=1, inplace=True)
            # Drop constant axes (if len is > 1)
            if len(df) > 1:
                for column in df.columns:
                    if column not in ["Value", "Error"]:
                        firstval = df[column].values[0]
                        # Should work as long as they are the exact same value
                        allequal = (df[column] == firstval).all()
                        if allequal:
                            del df[column]

            # Drop rows if they are exactly the same values
            # (untraced behaviour)
            df.drop_duplicates(inplace=True)

            # The double binning Surfaces/cells with segments can create
            # issues for JADE since if another binning is added
            # (such as energy) it is not supported. Nevertheless,
            # the additional segmentation can be quite useful and this can be
            # collapsed de facto in a single geometrical binning

            if "Cells" in df.columns and "Segments" in df.columns and len(
                    df) > 1:
                # Then we can collapse this in a single geometrical binning
                values = []
                for cell, segment in zip(df.Cells, df.Segments):
                    val = str(int(cell)) + "-" + str(int(segment))
                    values.append(val)
                df["Cells-Segments"] = values
                # delete the collapsed columns
                del df["Cells"]
                del df["Segments"]

            # Sub DF containing only total bins
            try:
                dftotal = df[df[total] == "total"]
            except (KeyError, NameError):
                # KeyError : there is no total bin in df
                # NameError: total variable was not defined
                dftotal = None

            tallydata[t.tallyNumber] = df
            totalbin[t.tallyNumber] = dftotal

        return tallydata, totalbin


class OpenMCOutput:
    def __init__(self, output_file):
        self.output_file = output_file
        self.output_file_data = self.read(output_file)
        self.tallydata, self.totalbin = self.process_tally()
        self.stat_checks = None

    def _create_dataframe(self, rows):
        columns = [
            "Cells",
            "User",
            "Segments",
            "Cosine",
            "Energy",
            "Time",
            "Cor C",
            "Cor B",
            "Cor A",
            "Value",
            "Error",
        ]
        df = pd.DataFrame(rows, columns=columns)
        cells = list(df.Cells.unique())
        total = "Energy"
        for cell in cells:
            value = df.loc[df["Cells"] == cell, "Values"].sum()
            error = np.sqrt(sum(df.loc[df["Cells"] == cell, "Values"] ** 2))
            row = [
                cell,
                False,
                False,
                False,
                total,
                False,
                False,
                False,
                False,
                value,
                error,
            ]
            df.loc[len(df)] = row
        dftotal = df[df[total] == "total"]
        return df, dftotal

    def read(self, output_file):
        with open(output_file, "r") as f:
            output_file_data = f.readlines()
        return output_file_data

    def process_tally(self):
        tallydata = {}
        totalbin = {}
        rows = []
        for line in self.output_file_data:
            if "tally" in line.lower():
                if len(rows) > 0:
                    tallydata[tallynum], totalbin[tallynum] = self._create_dataframe(
                        rows)
                    rows = []
                parts = line.split()
                tallynum = int(parts[2].replace(":", ""))
                cells = False
                user = False
                segments = False
                cosine = False
                energy = False
                time = False
                cor_c = False
                cor_b = False
                cor_a = False
                value = False
                error = False
            if "incoming energy" in line.lower():
                parts = line.split()
                energy = 1e-6 * float(parts[3].replace(")", ""))
            if "flux" in line.lower():
                parts = line.split()
                value, error = float(parts[1]), float(parts[2])
                rows.append(
                    [
                        cells,
                        user,
                        segments,
                        cosine,
                        energy,
                        time,
                        cor_c,
                        cor_b,
                        cor_a,
                        value,
                        error,
                    ]
                )
            tallydata[tallynum], totalbin[tallynum] = self._create_dataframe(
                rows)
        return tallydata, totalbin


class ExcelOutputSheet:
    # Common variables
    _starting_free_row = 10

    def __init__(self, template, outpath):
        """
        Excel workbook containing the post-processed results

        Parameters
        ----------
        template : path like object
            path to the sheet template.
        outpath : path like object
            dump path for the excel.

        Returns
        -------
        None.

        """
        self.outpath = outpath  # Path to the excel file
        # Open template
        shutil.copy(template, outpath)
        # self.app = xw.App(visible=False)
        self.wb = self.app.books.open(outpath)
        # The first open row in current ws
        self.free_row = self._starting_free_row
        self.ws_free_rows = {}
        self.current_ws = None

    def _switch_ws(self, ws_name):
        """
        Change active worksheet without loosing parameters informations.

        Parameters
        ----------
        ws_name : str
            Worksheet name.

        Returns
        -------
        ws : xlwings.Sheet
            Excel worksheet.

        """
        # Adjourn free row sheet
        if self.current_ws is not None:
            self.ws_free_rows[self.current_ws.name] = self.free_row

        # Select new sheet
        ws = self.wb.sheets[ws_name]
        self.current_ws = ws
        try:
            self.free_row = self.ws_free_rows[ws_name]
        except KeyError:
            self.free_row = self._starting_free_row

        return ws

    def insert_df(
        self,
        startcolumn,
        df,
        ws,
        startrow=None,
        header=None,
        print_index=True,
        idx_format="0",
        cols_head_size=12,
        values_format=None,
    ):
        """
        Insert a DataFrame (df) into a Worksheet (ws) using xlwings.

        Parameters
        ----------
        startcolumn : int or str
            Starting column where to insert the DataFrame. It can be expressed
            both as an integer as a letter in Excel fashion.
        df : pandas.DataFrame
            DataFrame to insert in the excel sheet
        ws : str
            name of the Excel worksheet where to put the DataFrame.
        startrow : int
            starting row where to put the DataFrame. Default is None that
            triggers the use of the memorized first free row in the excel sheet
        header : tuple (str, value)
            contains the tag of the header and the header value. DEAFAULT is
            None
        print_index : bool
            if True the DataFrame index is printed. DEAFAULT is True.
        idx_format : str
            how to format the index values. DEAFAULT is '0' (integer)
        cols_head_size : int
            Font size for columns header. DEAFAULT is 12
        values_format : str
            how to format the values. DEAFAULT is None

        Returns
        -------
        None

        """
        # Select the worksheet as first thing in order to have the correct
        # Free rows computed
        ws = self._switch_ws(ws)

        if startrow is None:
            startrow = self.free_row
            # adjourn free row
            add_space = 3  # Includes header
            self.free_row = self.free_row + len(df) + add_space

        # Start column can be provided as a letter or number (up to Z)
        if isinstance(startcolumn, str):
            startcolumn = ord(startcolumn.lower()) - 96

        anchor = (startrow, startcolumn)
        header_anchor_tag = (startrow, 1)
        header_anchor = (startrow + 1, 1)

        try:
            ws.range(anchor).options(index=print_index, header=True).value = df
            rng = ((startrow + 1, startcolumn),
                   (startrow + 1 + len(df), startcolumn))
            # Format values if requested
            if values_format is not None:
                rng_values = (
                    (startrow + 1, startcolumn + 1),
                    (startrow + 1 + len(df), startcolumn + 1 + len(df.columns)),
                )
                ws.range(*rng_values).number_format = values_format

            # Formatting
            ws.range(*rng).number_format = idx_format  # idx formatting
            # Columns headers
            anchor_columns = (
                anchor, (startrow, startcolumn + len(df.columns)))
            ws.range(*anchor_columns).api.Font.Size = cols_head_size
            ws.range(*anchor_columns).api.Font.Bold = True
            ws.range(*anchor_columns).color = (236, 236, 236)

            if header is not None:
                ws.range(header_anchor_tag).value = header[0]
                ws.range(header_anchor_tag).api.Font.Size = cols_head_size
                ws.range(header_anchor_tag).api.Font.Bold = True
                ws.range(header_anchor_tag).color = (236, 236, 236)

                ws.range(header_anchor).value = header[1]
                ws.range(header_anchor).api.Font.Size = cols_head_size
                ws.range(header_anchor_tag).api.Font.Bold = True
                ws.range(header_anchor_tag).color = (236, 236, 236)

        except Exception as e:
            print(vars(e))
            print(header)
            print(df)

    def insert_cutted_df(
        self,
        startcolumn,
        df,
        ws,
        ylim,
        startrow=None,
        header=None,
        index_name=None,
        cols_name=None,
        index_num_format="0",
        values_format=None,
    ):
        """
        Insert a DataFrame in the excel cutting its columns

        Parameters
        ----------
        startcolumn : str/int
            Excel column where to put the first DF column.
        df : pd.DataFrame
            global DF to insert.
        ws : str
            Excel worksheet where to insert the DF.
        ylim : int
            limit of columns to use to cut the DF.
        startrow : int, optional
            initial Excel row. The default is None,
            the first available is used.
        header : tuple (str, value)
            contains the tag of the header and the header value. DEAFAULT is
            None
        index_name : str
            Name of the Index. DEAFAULT is None
        cols_name : str
            Name of the columns. DEFAULT is None
        index_num_format: str
            format of index numbers
        values_format : str
            how to format the values. DEAFAULT is None

        Returns
        -------
        None.

        """
        # First of all we need to switch ws or all calculation of free row
        # will be wrongly affected
        self._switch_ws(ws)

        res_len = len(df.columns)
        start_col = 0
        ylim = int(ylim)
        # ws = self.wb.sheets[ws]
        # Decode columns for index and columns names
        if isinstance(startcolumn, int):
            index_col = string.ascii_uppercase[startcolumn]
            columns_col = string.ascii_uppercase[startcolumn + 1]
        elif isinstance(startcolumn, str):
            index_col = startcolumn
            columns_col = chr(ord(startcolumn) + 1)

        # Add each DataFrame piece
        new_ylim = ylim
        while res_len > ylim:
            curr_df = df.iloc[:, start_col:new_ylim]
            # Memorize anchors for headers name
            anchor_index = index_col + str(self.free_row)
            anchor_cols = columns_col + str(self.free_row - 1)
            end_anchor_cols = chr(ord(columns_col) + len(curr_df.columns) - 1) + str(
                self.free_row - 1
            )
            # Insert cutted df
            self.insert_df(
                startcolumn,
                curr_df,
                ws,
                header=header,
                idx_format=index_num_format,
                values_format=values_format,
            )
            # Insert columns name and index name
            self.current_ws.range(anchor_index).value = index_name
            self.current_ws.range(anchor_index).api.Font.Size = 12
            self.current_ws.range(anchor_index).api.Font.Bold = True
            self.current_ws.range(anchor_index).color = (236, 236, 236)

            self.current_ws.range(anchor_cols).value = cols_name
            self.current_ws.range(anchor_cols).api.Font.Size = 12
            self.current_ws.range(anchor_cols).api.Font.Bold = True
            self.current_ws.range(anchor_cols).color = (236, 236, 236)
            self.current_ws.range(anchor_cols + ":" + end_anchor_cols).merge()
            # Adjourn parameters
            start_col = start_col + ylim
            new_ylim = new_ylim + ylim
            res_len = res_len - ylim

        # Add the remaining piece
        if res_len != 0:
            curr_df = df.iloc[:, -res_len:]
            # Memorize anchors for headers name
            anchor_index = index_col + str(self.free_row)
            anchor_cols = columns_col + str(self.free_row - 1)
            end_anchor_cols = chr(ord(columns_col) + len(curr_df.columns) - 1) + str(
                self.free_row - 1
            )

            self.insert_df(
                startcolumn,
                curr_df,
                ws,
                header=header,
                idx_format=index_num_format,
                values_format=values_format,
            )
            # Insert columns name and index name
            self.current_ws.range(anchor_index).value = index_name
            self.current_ws.range(anchor_cols).value = cols_name
            # Merge the cols name
            self.current_ws.range(anchor_cols + ":" + end_anchor_cols).merge()

        # Adjust lenght
        self.current_ws.range(index_col + ":AAA").autofit()

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
        try:
            self.wb.save()
        except FileNotFoundError as e:
            print(" The following is the original exception:")
            print(e)
            print("\n it may be due to invalid characters in the file name")

        self.wb.close()
        self.app.quit()


def fatal_exception(message=None):
    """
    Use this function to exit with a code error from a handled exception

    Parameters
    ----------
    message : str, optional
        Message to display. The default is None.

    Returns
    -------
    None.

    """
    # RED color
    CRED = "\033[91m"
    CEND = "\033[0m"

    if message is None:
        message = "A Fatal exception have occured"

    message = message + ", the application will now exit"
    print(CRED + " FATAL EXCEPTION: \n" + message + CEND)
    sys.exit()
