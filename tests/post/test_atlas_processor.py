from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

import pandas as pd

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
