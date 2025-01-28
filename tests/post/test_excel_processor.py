from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import pandas as pd

import tests.dummy_structure
from jade.config.excel_config import ConfigExcelProcessor
from jade.post.excel_processor import ExcelProcessor
from jade.resources import default_cfg

ROOT_RAW = files(tests.dummy_structure).joinpath("raw_data")


class TestExcelProcessor:
    def test_process(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Sphere.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("mcnp", "ENDFB-VIII.0"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_oktavian(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Oktavian.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()
        assert len(os.listdir(tmpdir)) == 2
        path_to_file = Path(tmpdir, "Oktavian_exp-exp_Vs_mcnp-FENDL 3.2c.xlsx")
        df = pd.read_excel(path_to_file, skiprows=3)
        assert df["C/E"].max() < 1.2
        assert df["C/E"].min() > 0.9
