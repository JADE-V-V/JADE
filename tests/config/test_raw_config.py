from __future__ import annotations

import os
from importlib.resources import files, as_file
from pathlib import Path

import jade.resources.default_cfg.benchmarks_pp as res
import tests.config.resources.raw_config as raw_res
from jade.config.raw_config import (
    ConfigRawProcessor,
    ResultConfig,
    TallyConcatOption,
)

CFG_ROOT = files(res).joinpath("raw")


class TestConfigRawProcessor:
    def test_config_raw_processor_init(self):
        results = [
            ResultConfig(name=1, modify={}, concat_option=TallyConcatOption.NO_ACTION)
        ]
        processor = ConfigRawProcessor(results)
        assert processor.results == results

    def test_result_config_init(self):
        result = ResultConfig(
            name=1, modify={}, concat_option=TallyConcatOption.NO_ACTION
        )
        assert result.name == 1
        assert result.modify == {}
        assert result.concat_option == TallyConcatOption.NO_ACTION

    def test_from_yaml(self):
        # test all configuration file for correct parsing without errors
        for code in os.listdir(CFG_ROOT):
            code_folder = Path(CFG_ROOT, code)
            for file in os.listdir(code_folder):
                cfg = ConfigRawProcessor.from_yaml(Path(code_folder, file))

    def test_aliases(self):
        file = Path(CFG_ROOT, "mcnp", "ITER_1D.yaml")
        cfg = ConfigRawProcessor.from_yaml(file)
        assert len(cfg.results) == 23
        assert len(cfg.results[0].modify[4][0][1]["values"]) == 104

    def test_apply_to(self):
        file = files(raw_res).joinpath("apply_to.yaml")
        with as_file(file) as f:
            cfg = ConfigRawProcessor.from_yaml(f)
        assert cfg.results[0].name == cfg.results[1].name
