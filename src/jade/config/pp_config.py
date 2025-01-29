from __future__ import annotations

import os
from pathlib import Path

from jade.config.atlas_config import ConfigAtlasProcessor
from jade.config.excel_config import ConfigExcelProcessor
from jade.helper.aux_functions import PathLike


class PostProcessConfig:
    def __init__(self, root_cfg_pp: PathLike):
        # get all available config excel processors
        excel_cfgs = {}
        for file in os.listdir(Path(root_cfg_pp, "excel")):
            if file.endswith(".yaml") or file.endswith(".yml"):
                cfg = ConfigExcelProcessor.from_yaml(Path(root_cfg_pp, "excel", file))
                excel_cfgs[cfg.benchmark] = cfg
        self.excel_cfgs = excel_cfgs
        # Get all available config atlas processors
        atlas_cfgs = {}
        for file in os.listdir(Path(root_cfg_pp, "atlas")):
            if file.endswith(".yaml") or file.endswith(".yml"):
                cfg = ConfigAtlasProcessor.from_yaml(Path(root_cfg_pp, "atlas", file))
                atlas_cfgs[cfg.benchmark] = cfg
        self.atlas_cfgs = atlas_cfgs
