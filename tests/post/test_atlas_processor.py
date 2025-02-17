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
