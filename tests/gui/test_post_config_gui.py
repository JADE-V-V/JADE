from __future__ import annotations

from importlib.resources import files

import jade.resources
from jade.config.status import GlobalStatus
from jade.gui.post_config_gui import PostConfigGUI
from tests import dummy_structure

DUMMY_STRUCT = files(dummy_structure)

DEFAULT_CFG = files(jade.resources).joinpath("default_cfg")


class TestConfigGui:
    def test_init(self):
        status = GlobalStatus(
            DUMMY_STRUCT.joinpath("simulations"),
            DUMMY_STRUCT.joinpath("raw_data"),
        )

        return PostConfigGUI(status)
