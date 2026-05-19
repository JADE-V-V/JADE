from __future__ import annotations

from importlib.resources import files
from unittest.mock import patch

import jade.resources
from jade.config.status import GlobalStatus
from tests import dummy_structure

import pytest

from jade.helper.__optionals__ import TKINTER_AVAIL

if TKINTER_AVAIL:
    from jade.gui.post_config_gui import PostConfigGUI

DUMMY_STRUCT = files(dummy_structure)

DEFAULT_CFG = files(jade.resources).joinpath("default_cfg")

@pytest.mark.skipif(not TKINTER_AVAIL, reason="tkinter is not available")
class TestPostConfigGui:
    def test_init(self):
        status = GlobalStatus(
            DUMMY_STRUCT.joinpath("simulations"),
            DUMMY_STRUCT.joinpath("raw_data"),
        )

        with patch("jade.gui.post_config_gui.tk.Tk", autospec=True):
            gui = PostConfigGUI(status)

        assert gui is not None
