from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path

from jade.config.atlas_config import ConfigAtlasProcessor
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
        """
        self.atlas_folder_path = atlas_folder_path
        self.raw_root = raw_root
        self.cfg = cfg
        self.codelibs = codelibs

    def process(self) -> None:
        """Process the atlas comparison for the given benchmark. It will produce one
        atlas file comparing all requested code-lib results in each plot.
        """
        # instantiate the atlas
        # atlas = Atlas(self.atlas_folder_path, self.cfg.benchmark)

        for plot_cfg in self.cfg.plots:
            dfs = []
            # get global df results for each code-lib
            for code_tag, lib in self.codelibs:
                code = CODE(code_tag)
                codelib = print_code_lib(code, lib)
                logging.info("Parsing reference data")
                raw_folder = Path(self.raw_root, codelib, self.cfg.benchmark)

                df = ExcelProcessor._get_table_df(plot_cfg.results, raw_folder)
                if plot_cfg.expand_runs:
                    run_dfs = []
                    df = df.reset_index()
                    for run in df["Case"].unique():
                        run_df = df[df["Case"] == run]
                        run_dfs.append((run, run_df))
                    dfs.append((plot_cfg.name, run_dfs))
                else:
                    dfs.append((plot_cfg.name, df.reset_index()))

            # create the plot
            if plot_cfg.expand_runs:  # one plot for each case/run
                for case, df in dfs:
                    cfg = deepcopy(plot_cfg)
                    cfg.name = f"{cfg.name} {case}"
                    plot = PlotFactory.create_plot(plot_cfg, df)
            else:
                plot = PlotFactory.create_plot(plot_cfg, dfs)
