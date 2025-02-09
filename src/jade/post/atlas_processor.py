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
                if plot_cfg.expand_runs:
                    df = df.reset_index()
                    for run in df["Case"].unique():
                        # skip the cases that are not in select_runs
                        if (
                            plot_cfg.select_runs
                            and plot_cfg.select_runs.search(run) is None
                        ):
                            continue

                        run_df = df[df["Case"] == run]
                        if run in cases:
                            cases[run].append((codelib_pretty, run_df))
                        else:
                            cases[run] = [(codelib_pretty, run_df)]
                else:
                    dfs.append((codelib_pretty, df.reset_index()))

            # create the plot
            if plot_cfg.expand_runs:  # one plot for each case/run
                for case, data in cases.items():
                    atlas.doc.add_heading(case, level=2)
                    cfg = deepcopy(plot_cfg)
                    cfg.name = f"{cfg.name} {case}"
                    cfg.title = f"{cfg.title} - {case}"
                    plot = PlotFactory.create_plot(cfg, data)
                    fig, _ = plot.plot()
                    atlas.insert_img(fig)
            else:
                plot = PlotFactory.create_plot(plot_cfg, dfs)
                fig, _ = plot.plot()
                atlas.insert_img(fig)

        # Save the atlas
        atlas.save(self.atlas_folder_path)
