from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import pandas as pd

from jade.config.excel_config import ConfigExcelProcessor
from jade.helper.aux_functions import PathLike, print_code_lib
from jade.helper.constants import CODE
from jade.post.excel_routines import TableFactory

TITLE = "{}-{} Vs {}-{}. Result: {}"
FILE_NAME = "{}_{}-{}_Vs_{}-{}.xlsx"


class ExcelProcessor:
    def __init__(
        self,
        raw_root: PathLike,
        excel_folder_path: PathLike,
        cfg: ConfigExcelProcessor,
        codelibs: list[tuple[str, str]],
    ) -> None:
        """Object responsible to produce the excel comparison results for a given
        benchmark.

        Parameters
        ----------
        raw_root : PathLike
            path to the raw data folder root
        excel_folder_path : PathLike
            path to the excel folder where the results will be stored
        cfg : ConfigExcelProcessor
            configuration options for the excel processor
        codelibs : list[tuple[str, str]]
            list of code-lib results that should be compared. The first one is
            interpreted as the reference data.
        """
        self.excel_folder_path = excel_folder_path
        self.raw_root = raw_root
        self.cfg = cfg
        self.codelibs = codelibs

    def process(self) -> None:
        """Process the excel comparison for the given benchmark. It will produce one
        excel file comparing the reference data with the other codelibs provided in
        the configuration file. Each excel file will contain all the requested tables.
        """
        reference_dfs = {}
        for i, (code_tag, lib) in enumerate(self.codelibs):
            code = CODE(code_tag)
            codelib = print_code_lib(code, lib)
            logging.info("Parsing reference data")
            raw_folder = Path(self.raw_root, codelib, self.cfg.benchmark)

            # First store all reference dfs
            if i == 0:
                ref_code = code
                ref_lib = lib
                for table_cfg in self.cfg.tables:
                    target_df = self._get_table_df(
                        table_cfg.results, raw_folder, subsets=table_cfg.subsets
                    )
                    # If requested, select only a subsets of the runs
                    if table_cfg.select_runs:
                        target_df = self._apply_select_runs(
                            re.compile(table_cfg.select_runs), target_df
                        )
                    reference_dfs[table_cfg.name] = target_df

            # then we can produce one excel comparison file for each target
            else:
                outfile = Path(
                    self.excel_folder_path,
                    FILE_NAME.format(
                        self.cfg.benchmark, ref_code.value, ref_lib, code.value, lib
                    ),
                )
                logging.info(f"Writing the resulting excel file {outfile}")
                with pd.ExcelWriter(outfile) as writer:
                    for table_cfg in self.cfg.tables:
                        # this gets a concatenated dataframe with all results that needs
                        # to be in the table
                        target_df = self._get_table_df(
                            table_cfg.results, raw_folder, subsets=table_cfg.subsets
                        )
                        # If requested, select only a subsets of the runs
                        if table_cfg.select_runs:
                            target_df = self._apply_select_runs(
                                re.compile(table_cfg.select_runs), target_df
                            )

                        title = TITLE.format(
                            ref_code.value, ref_lib, code.value, lib, table_cfg.name
                        )
                        ref_df = reference_dfs[table_cfg.name]
                        ref_pretty = print_code_lib(ref_code, ref_lib, pretty=True)
                        target_pretty = print_code_lib(code, lib, pretty=True)
                        table = TableFactory.create_table(
                            table_cfg.table_type,
                            [
                                title,
                                writer,
                                ref_df,
                                target_df,
                                table_cfg,
                                ref_pretty,
                                target_pretty,
                            ],
                        )
                        table.add_sheets()

    @staticmethod
    def _get_table_df(
        results: list[int | str],
        raw_folder: PathLike,
        subsets: list[dict] | None = None,
    ) -> pd.DataFrame:
        """given a list of results, get the concatenated dataframe"""
        dfs = []
        for result in results:
            # this gets a concatenated dataframe for each result for different runs
            subset = _check_for_subsets(subsets, result)
            df = ExcelProcessor._get_concat_df_results(
                result, raw_folder, subset=subset
            )
            # it may happen that a dataframe is empty since this result is not in the run
            if df.empty:
                continue
            df["Result"] = result
            dfs.append(df)
        return pd.concat(dfs)

    @staticmethod
    def _get_concat_df_results(
        target_result: int | str, folder: PathLike, subset: dict | None = None
    ) -> pd.DataFrame:
        """given a result ID, locate, read the dataframes and concat them (from different
        single runs)"""
        dfs = []
        for file in os.listdir(folder):
            if not file.endswith(".csv"):
                continue
            splits = file.split(" ")
            # ASSUMPTION: run name is continous, result name can have spaces
            run_name = splits[0]
            result = " ".join(splits[1:])[:-4]  # remove the .csv
            if result == target_result:
                df = pd.read_csv(Path(folder, file))
                # check here if only a subset of the dataframe is needed
                if subset:
                    for value, items in subset["values"].items():
                        try:
                            df = df.set_index(value).loc[items].reset_index()
                        except KeyError:
                            pass  # accept that in some tallies the column may not be present
                df["Case"] = run_name
                dfs.append(df)
        if len(dfs) == 0:
            logging.warning(f"No data found for {target_result}")
            return pd.DataFrame()
        return pd.concat(dfs)

    @staticmethod
    def _apply_select_runs(pattern: re.Pattern, df: pd.DataFrame) -> pd.DataFrame:
        to_drop = []
        for case in df["Case"].unique():
            if pattern.search(case) is None:
                to_drop.append(case)
        df = df[~df["Case"].isin(to_drop)]
        return df


def _check_for_subsets(subsets: list[dict] | None, curr_res) -> None | dict:
    if subsets:
        for subset in subsets:
            if curr_res == subset["result"]:
                return subset
    return None
