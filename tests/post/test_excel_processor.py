from __future__ import annotations

from importlib.resources import as_file, files

import tests.dummy_structure
from jade.config.excel_config import ConfigExcelProcessor
from jade.post.excel_processor import ExcelProcessor
from jade.resources import default_cfg

ROOT_RAW = files(tests.dummy_structure).joinpath("raw_data")


class TestExcelProcessor:
    def test_process(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Sphere.yml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("mcnp", "ENDFB-VIII.0"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()
