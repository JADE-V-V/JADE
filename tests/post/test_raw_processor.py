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
from jade.helper.__openmc__ import OMC_AVAIL
from jade.post.raw_processor import RawProcessor
from jade.resources import default_cfg

SIMULATION_FOLDER = files(dummy_struct).joinpath("simulations")
RAW_CFG_FILES_MCNP = files(default_cfg).joinpath("benchmarks_pp/raw/mcnp")
RAW_CFG_FILES_D1S = files(default_cfg).joinpath("benchmarks_pp/raw/d1s")
RAW_CFG_FILES_OPENMC = files(default_cfg).joinpath("benchmarks_pp/raw/openmc")


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

    def test_Sphere_mcnp(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Sphere.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folder = Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Sphere", "Sphere_m101"
        )

        processor = RawProcessor(cfg, folder, tmpdir)
        processor.process_raw_data()
    
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
    def test_Sphere_openmc(self, tmpdir):
        with as_file(RAW_CFG_FILES_OPENMC.joinpath("Sphere.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folder = Path(
            SIMULATION_FOLDER, "_openmc_-_FENDL 3.2b_", "Sphere", "Sphere_m101"
        )

        processor = RawProcessor(cfg, folder, tmpdir)
        processor.process_raw_data()


    def test_oktavian_raw(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Oktavian.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folder = Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Oktavian", "Oktavian_Al"
        )
        processor = RawProcessor(cfg, folder, tmpdir)
        processor.process_raw_data()

    def test_ITER1D_raw(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("ITER_1D.yaml")) as f:
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

    def test_TiaraBC(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Tiara-BC.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        for folder in Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Tiara-BC"
        ).iterdir():
            processor = RawProcessor(cfg, folder, tmpdir)
            processor.process_raw_data()

    def test_TiaraBS(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Tiara-BS.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        for folder in Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Tiara-BS"
        ).iterdir():
            processor = RawProcessor(cfg, folder, tmpdir)
            processor.process_raw_data()

    def test_SphereSDDR(self, tmpdir):
        with as_file(RAW_CFG_FILES_D1S.joinpath("SphereSDDR.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        for folder in Path(SIMULATION_FOLDER, "_d1s_-_lib 1_", "SphereSDDR").iterdir():
            processor = RawProcessor(cfg, folder, tmpdir)
            processor.process_raw_data()

    def test_TiaraFC(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Tiara-FC.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        for folder in Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "Tiara-FC"
        ).iterdir():
            processor = RawProcessor(cfg, folder, tmpdir)
            processor.process_raw_data()

    def test_FNS_TOF(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("FNS-TOF.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        for folder in Path(
            SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "FNS-TOF"
        ).iterdir():
            processor = RawProcessor(cfg, folder, tmpdir)
            processor.process_raw_data()

    def test_WCLL(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("WCLL_TBM_1D.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(
                SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "WCLL_TBM_1D", "WCLL_TBM_1D"
            ),
            Path(
                SIMULATION_FOLDER, "_mcnp_-_FENDL 2.1c_", "WCLL_TBM_1D", "WCLL_TBM_1D"
            ),
        ]
        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            processor = RawProcessor(cfg, folder, path)
            processor.process_raw_data()

    def test_ITER_Cyl_SDDR(self, tmpdir):
        with as_file(RAW_CFG_FILES_D1S.joinpath("ITER_Cyl_SDDR.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_d1s_-_lib 1_", "ITER_Cyl_SDDR", "ITER_Cyl_SDDR"),
            Path(SIMULATION_FOLDER, "_d1s_-_lib 2_", "ITER_Cyl_SDDR", "ITER_Cyl_SDDR"),
        ]
        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            processor = RawProcessor(cfg, folder, path)
            processor.process_raw_data()

    def test_TUD_W_mcnp(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("TUD-W.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.1d_", "TUD-W"),
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "TUD-W"),
        ]

        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            for subfolder in folder.iterdir():
                processor = RawProcessor(cfg, subfolder, path)
                processor.process_raw_data()

    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
    def test_TUD_W_openmc(self, tmpdir):
        with as_file(RAW_CFG_FILES_OPENMC.joinpath("TUD-W.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_openmc_-_FENDL 3.1d_", "TUD-W"),
        ]

        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            for subfolder in folder.iterdir():
                processor = RawProcessor(cfg, subfolder, path)
                processor.process_raw_data()

    def test_Simple_Tokamak(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("Simple_Tokamak.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(
                SIMULATION_FOLDER,
                "_mcnp_-_FENDL 3.2c_",
                "Simple_Tokamak",
                "Simple_Tokamak",
            ),
        ]
        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            processor = RawProcessor(cfg, folder, path)
            processor.process_raw_data()
    
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC not available")
    def test_Simple_Tokamak_openmc(self, tmpdir):
        with as_file(RAW_CFG_FILES_OPENMC.joinpath("Simple_Tokamak.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(
                SIMULATION_FOLDER,
                "_openmc_-_FENDL 3.2b_",
                "Simple_Tokamak",
                "Simple_Tokamak",
            ),
        ]
        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            processor = RawProcessor(cfg, folder, path)
            processor.process_raw_data()

    def test_ASPIS_Fe88(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("ASPIS-Fe88.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.1d_", "ASPIS-Fe88"),
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "ASPIS-Fe88"),
        ]

        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            for subfolder in folder.iterdir():
                processor = RawProcessor(cfg, subfolder, path)
                processor.process_raw_data()

    def test_TUD_FNG(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("TUD-FNG.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.1d_", "TUD-FNG"),
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "TUD-FNG"),
        ]

        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            for subfolder in folder.iterdir():
                processor = RawProcessor(cfg, subfolder, path)
                processor.process_raw_data()

    def test_FNG_SiC(self, tmpdir):
        with as_file(RAW_CFG_FILES_MCNP.joinpath("FNG-SiC.yaml")) as f:
            cfg = ConfigRawProcessor.from_yaml(f)

        folders = [
            Path(SIMULATION_FOLDER, "_mcnp_-_JEFF 3.3_", "FNG-SiC"),
            Path(SIMULATION_FOLDER, "_mcnp_-_FENDL 3.2c_", "FNG-SiC"),
        ]

        for i, folder in enumerate(folders):
            path = tmpdir.join(str(i))
            os.makedirs(path)
            for subfolder in folder.iterdir():
                processor = RawProcessor(cfg, subfolder, path)
                processor.process_raw_data()
