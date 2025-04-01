from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path

import pandas as pd

from jade.config.atlas_config import ConfigAtlasProcessor, PlotConfig
from jade.helper.aux_functions import PathLike, print_code_lib
from jade.helper.constants import CODE
from jade.post.atlas import Atlas
from jade.post.excel_processor import ExcelProcessor
from jade.post.plotter import PlotFactory


class AtlasProcessor:
    def __init__(
        self,
        raw_root: PathLike,
        atlas_folder_path: PathLike,
        cfg: ConfigAtlasProcessor,
        codelibs: list[tuple[str, str]],
        word_templatee_path: PathLike,
    ) -> None:
        """Object responsible to produce the excel comparison results for a given
        benchmark.

        Parameters
        ----------
        raw_root : PathLike
            path to the raw data folder root
        atlas_folder_path : PathLike
            path to the atlas folder where the results will be stored
        cfg : ConfigAtlasProcessor
            configuration options for the excel processor
        codelibs : list[tuple[str, str]]
            list of code-lib results that should be compared. The first one is
            interpreted as the reference data.
        word_templatee_path : PathLike
            path to the word template to be used in the atlas generation.
        """
        self.atlas_folder_path = atlas_folder_path
        self.raw_root = raw_root
        self.cfg = cfg
        self.codelibs = codelibs
        self.word_template_path = word_templatee_path

    def process(self) -> None:
        """Process the atlas comparison for the given benchmark. It will produce one
        atlas file comparing all requested code-lib results in each plot.
        """
        # instantiate the atlas
        atlas = Atlas(self.word_template_path, self.cfg.benchmark)

        for plot_cfg in self.cfg.plots:
            # Add a chapter for each plo type
            atlas.doc.add_heading(plot_cfg.name, level=1)

            dfs = []
            cases = {}
            # get global df results for each code-lib
            for code_tag, lib in self.codelibs:
                code = CODE(code_tag)
                codelib_pretty = print_code_lib(code, lib, pretty=True)
                codelib = print_code_lib(code, lib)
                logging.info("Parsing reference data")
                raw_folder = Path(self.raw_root, codelib, self.cfg.benchmark)

                df = ExcelProcessor._get_table_df(
                    plot_cfg.results, raw_folder, subsets=plot_cfg.subsets
                )
                _dfs, _cases = self._select_runs(plot_cfg, df, codelib_pretty)
                dfs.extend(_dfs)
                for case in _cases:
                    if case in cases:
                        cases[case].extend(_cases[case])
                    else:
                        cases[case] = _cases[case]

            # create the plot
            if plot_cfg.expand_runs:  # one plot for each case/run
                self._generate_expanded_plots(plot_cfg, cases, atlas)
            else:
                self._generate_plot(plot_cfg, dfs, atlas)

        # Save the atlas
        atlas.save(self.atlas_folder_path)

    def _generate_expanded_plots(
        self,
        plot_cfg: PlotConfig,
        cases: dict[str, list[tuple[str, pd.DataFrame]]],
        atlas: Atlas,
    ):
        """Generate a plot for each case/run"""
        for case, data in cases.items():
            atlas.doc.add_heading(case, level=2)
            cfg = deepcopy(plot_cfg)
            cfg.name = f"{cfg.name} {case}"
            cfg.title = f"{cfg.title} - {case}"
            self._generate_plot(cfg, data, atlas)

    @staticmethod
    def _generate_plot(
        plot_cfg: PlotConfig, dfs: list[tuple[str, pd.DataFrame]], atlas: Atlas
    ):
        """Generate a single plot (that can be composed by more figures)"""
        plot = PlotFactory.create_plot(plot_cfg, dfs)
        item = plot.plot()
        for fig, _ in item:
            atlas.insert_img(fig)

    @staticmethod
    def _select_runs(
        plot_cfg: PlotConfig, df: pd.DataFrame, codelib_pretty: str
    ) -> tuple[
        list[tuple[str, pd.DataFrame]], dict[str, list[tuple[str, pd.DataFrame]]]
    ]:
        """Select the runs to be plotted depending on the configuration. The logic
        differs if the runs should be expanded or not."""
        cases = {}
        dfs = []
        if plot_cfg.expand_runs:
            for run in df["Case"].unique():
                # skip the cases that are not in select_runs
                if plot_cfg.select_runs and plot_cfg.select_runs.search(run) is None:
                    continue

                run_df = df[df["Case"] == run]
                if run in cases:
                    cases[run].append((codelib_pretty, run_df))
                else:
                    cases[run] = [(codelib_pretty, run_df)]
        else:
            # skip the cases that are not in select_runs
            to_drop = []
            for case in df["Case"].unique():
                if plot_cfg.select_runs and plot_cfg.select_runs.search(case) is None:
                    to_drop.append(case)
            df = df[~df["Case"].isin(to_drop)]
            dfs.append((codelib_pretty, df))
        return dfs, cases
