from __future__ import annotations

import os
from importlib.resources import files

from jade.config.excel_config import ConfigExcelProcessor
from jade.resources import default_cfg

EXCEL_ROOT = files(default_cfg).joinpath("benchmarks_pp/excel")


class TestConfigExcelProcessor:
    def test_all_default_files(self):
        for path in os.listdir(EXCEL_ROOT):
            if path.endswith(".yml") or path.endswith(".yaml"):
                ConfigExcelProcessor.from_yaml(EXCEL_ROOT.joinpath(path))
