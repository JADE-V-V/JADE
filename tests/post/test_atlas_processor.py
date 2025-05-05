from __future__ import annotations

from importlib.resources import as_file, files

import tests.dummy_structure
from jade import resources
from jade.config.atlas_config import ConfigAtlasProcessor
from jade.post.atlas_processor import AtlasProcessor
from jade.resources import default_cfg

ROOT_RAW = files(tests.dummy_structure).joinpath("raw_data")


class TestAtlasProcessor:
    def test_sphere(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Sphere.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")

        codelibs = [("mcnp", "ENDFB-VIII.0"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_oktavian(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Oktavian.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")

        codelibs = [("exp", "exp"), ("mcnp", "ENDFB-VIII.0"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_iter1d(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/ITER_1D.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("mcnp", "ENDFB-VIII.0"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TiaraBC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Tiara-BC.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TiaraBS(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Tiara-BS.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_SphereSDDR(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/SphereSDDR.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("d1s", "lib 1"), ("d1s", "lib 2")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TiaraFC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Tiara-FC.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNS_TOF(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNS-TOF.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_WCLL(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/WCLL_TBM_1D.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_ITER_Cyl_SDDR(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/ITER_Cyl_SDDR.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("d1s", "lib 1"), ("d1s", "lib 2")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_Simple_Tokamak(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/Simple_Tokamak.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("mcnp", "FENDL 3.2c"), ("mcnp", "ENDFB-VIII.0")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TUD_W(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/TUD-W.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("openmc", "FENDL 3.1d"), ("mcnp", "FENDL 3.1d")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_ASPIS_Fe88(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/ASPIS-Fe88.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "FENDL 3.1d")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TUD_FNG(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/TUD-FNG.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.1d"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_SiC(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-SiC.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c"), ("mcnp", "JEFF 3.3")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_W(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-W.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 2.1c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_SS(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-SS.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "JEFF 3.3")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_HCPB(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-HCPB.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "JEFF 3.3")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_BKT(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-BKT.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "JEFF 3.3")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_FNG_SDDR(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/FNG-SDDR.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("d1s", "lib 2")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_TUD_Fe(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/TUD-Fe.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.1d")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_IPPEDT(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/IPPE-DT.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")

        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()

    def test_ASPIS_PCA_Replica(self, tmpdir):
        with as_file(
            files(default_cfg).joinpath("benchmarks_pp/atlas/ASPIS-PCA-Replica.yaml")
        ) as file:
            cfg = ConfigAtlasProcessor.from_yaml(file)

        word_template_path = files(resources).joinpath("atlas_template.docx")
        codelibs = [("exp", "exp"), ("mcnp", "FENDL 3.2c")]
        processor = AtlasProcessor(ROOT_RAW, tmpdir, cfg, codelibs, word_template_path)
        processor.process()
