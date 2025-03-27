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
        assert df["C/E"].max() < 1.07
        assert df["C/E"].min() > 0.877

    def test_ITER1D(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/ITER_1D.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_TiaraBC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Tiara-BC.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_TiaraBS(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Tiara-BS.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_SphereSDDR(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/SphereSDDR.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("d1s", "lib 1"), ("d1s", "lib 2")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_TiaraFC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Tiara-FC.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

        file = Path(tmpdir, "Tiara-FC_exp-exp_Vs_mcnp-FENDL 3.2c.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 5

    def test_FNS_TOF(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/FNS-TOF.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_WCLL(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/WCLL_TBM_1D.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_ITER_Cyl_SDDR(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/ITER_Cyl_SDDR.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("d1s", "lib 1"), ("d1s", "lib 2")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_tud_w(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/TUD-W.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.1d"), ("openmc", "FENDL 3.1d")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()
        file = Path(tmpdir, "TUD-W_exp-exp_Vs_mcnp-FENDL 3.1d.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 144
        file = Path(tmpdir, "TUD-W_exp-exp_Vs_openmc-FENDL 3.1d.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 144

    def test_Simple_Tokamak(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/Simple_Tokamak.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

    def test_ASPIS_Fe88(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/ASPIS-Fe88.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "FENDL 3.1d")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

        file = Path(tmpdir, "ASPIS-Fe88_exp-exp_Vs_mcnp-FENDL 3.2c.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 15
        file = Path(tmpdir, "ASPIS-Fe88_exp-exp_Vs_mcnp-FENDL 3.1d.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 15

    def test_TUD_FNG(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/TUD-FNG.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "FENDL 3.1d")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

        file = Path(tmpdir, "TUD-FNG_exp-exp_Vs_mcnp-FENDL 3.2c.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 212
        file = Path(tmpdir, "TUD-FNG_exp-exp_Vs_mcnp-FENDL 3.1d.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 212

    def test_FNG_SiC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/excel/FNG-SiC.yaml")
        ) as file:
            cfg = ConfigExcelProcessor.from_yaml(file)
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "JEFF 3.3")]
        processor = ExcelProcessor(ROOT_RAW, tmpdir, cfg, codelibs)
        processor.process()

        file = Path(tmpdir, "FNG-SiC_exp-exp_Vs_mcnp-FENDL 3.2c.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 6
        file = Path(tmpdir, "FNG-SiC_exp-exp_Vs_mcnp-JEFF 3.3.xlsx")
        assert file.exists()
        df = pd.read_excel(file, skiprows=3)
        assert len(df) == 6
