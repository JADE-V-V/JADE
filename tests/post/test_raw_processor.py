from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import pandas as pd
import pytest

import tests.dummy_structure as dummy_struct
from jade.config.raw_config import (
    ConfigRawProcessor,
    ResultConfig,
    TallyConcatOption,
    TallyModOption,
)
from jade.post.raw_processor import RawProcessor
from jade.resources import default_cfg

SIMULATION_FOLDER = files(dummy_struct).joinpath("simulations")
RAW_CFG_FILES = files(default_cfg).joinpath("benchmarks_pp/raw/mcnp")


class TestRawProcessor:
    def test_process_raw_data(self, tmpdir):
        res1 = ResultConfig(
            name=1,
            modify={
                21: [(TallyModOption.LETHARGY, {})],
                41: [(TallyModOption.NO_ACTION, {})],
            },
            concat_option=TallyConcatOption.CONCAT,
        )
        res2 = ResultConfig(
            name=2,
            modify={
                41: [
                    (TallyModOption.SCALE, {"factor": 2}),
                    # just to see that subsequent modifications are applied correctly
                    (TallyModOption.SCALE, {"factor": 10}),
                ],
            },
            concat_option=TallyConcatOption.NO_ACTION,
        )
        cfg = ConfigRawProcessor(results=[res1, res2])
        folder = Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Oktavian", "Oktavian_Al"
        )
        processor = RawProcessor(cfg, folder, tmpdir)
        processor.process_raw_data()
        res1path = Path(tmpdir, f"{processor.single_run_name} 1.csv")
        df1 = pd.read_csv(res1path)
        res2path = Path(tmpdir, f"{processor.single_run_name} 2.csv")
        df2 = pd.read_csv(res2path)
        assert df2.iloc[0]["Value"] == pytest.approx(2 * 10 * 1.12099e-01, 1e-3)
        assert len(df1) == 191


def test_oktavian_raw(tmpdir):
    with as_file(RAW_CFG_FILES.joinpath("Oktavian.yaml")) as f:
        cfg = ConfigRawProcessor.from_yaml(f)

    folder = Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Oktavian", "Oktavian_Al")
    processor = RawProcessor(cfg, folder, tmpdir)
    processor.process_raw_data()


def test_ITER1D_raw(tmpdir):
    with as_file(RAW_CFG_FILES.joinpath("ITER_1D.yaml")) as f:
        cfg = ConfigRawProcessor.from_yaml(f)
    folders = [
        Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "ITER_1D", "ITER_1D"),
        Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 2.1c_", "ITER_1D", "ITER_1D"),
    ]
    for i, folder in enumerate(folders):
        path = tmpdir.join(str(i))
        os.makedirs(path)
        processor = RawProcessor(cfg, folder, path)
        processor.process_raw_data()
