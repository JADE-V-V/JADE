from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pytest
from ttkthemes import ThemedTk

import jade.resources
from jade.gui.run_config_gui import ConfigGUI

DEFAULT_CFG = files(jade.resources).joinpath("default_cfg")


class TestConfigGui:
    @pytest.fixture
    def config_gui(self):
        run_cfg = Path(DEFAULT_CFG, "run_cfg.yml")
        libs_cfg = Path(DEFAULT_CFG, "libs_cfg.yml")

        return ConfigGUI(run_cfg, libs_cfg)

    def test_init(self, config_gui):
        assert isinstance(config_gui.window, ThemedTk)
        assert config_gui.window.title() == "Configuration GUI"
        assert isinstance(config_gui.notebook, ttk.Notebook)
        assert isinstance(config_gui.benchmarks_tab, ttk.Frame)
        assert isinstance(config_gui.libraries_tab, ttk.Frame)
        assert config_gui.notebook.index("end") == 2  # Two tabs added
        assert config_gui.notebook.tab(0, "text") == "Benchmarks"
        assert config_gui.notebook.tab(1, "text") == "Libraries"
        assert isinstance(config_gui.save_button, ttk.Button)

    def test_save_settings(self, config_gui, monkeypatch, tmpdir):
        def mock_return_file(defaultextension=None, filetypes=None):
            return tmpdir.join("test_output.yml")

        monkeypatch.setattr(
            filedialog,
            "asksaveasfilename",
            mock_return_file,
        )

        def mock_showinfo(title, message):
            return

        monkeypatch.setattr(messagebox, "showinfo", mock_showinfo)

        config_gui.save_settings()
        assert Path(tmpdir, "test_output.yml").exists()

    #     def test_on_benchmark_click(self, config_gui: ConfigGUI, monkeypatch):
    #         # Simulate a click on the first cell of the benchmarks tree
    #         first_item = config_gui.bench_tree.get_children()[0]
    #         config_gui.bench_tree.selection_set(first_item)
    #         config_gui.bench_tree.focus(first_item)

    #         # Get the bounding box of the first cell
    #         bbox = config_gui.bench_tree.bbox(first_item, "#1")
    #         x, y = bbox[0] + 1, bbox[1] + 1

    #         # Create a mock event with the coordinates
    #         event = tk.Event()
    #         event.x = x
    #         event.y = y
    #         event.widget = config_gui.bench_tree

    #         # Call the event handler directly
    #         config_gui.on_benchmark_click(event)

    #         # Verify the cell value is updated
    #         value, row = _get_cell_value(config_gui.bench_tree, event)
    #         assert "X" not in row

    #         config_gui.on_benchmark_click(event)
    #         value, row = _get_cell_value(config_gui.bench_tree, event)
    #         assert value == "X"

    # def _get_cell_value(tree, event):
    #     row_id = tree.identify_row(event.y)
    #     column_id = tree.identify_column(event.x)

    #     # Get the current value of the cell
    #     item = tree.item(row_id)
    #     column_index = int(column_id[1:]) - 1
    #     current_value = item["values"][column_index]

    # return current_value, item["values"]
