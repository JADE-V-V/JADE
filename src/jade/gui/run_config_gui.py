import tkinter as tk
from importlib.resources import as_file, files
from tkinter import TclError, filedialog, messagebox, ttk

import yaml
from ttkthemes import ThemedTk

import jade.resources as res
from jade.helper.aux_functions import PathLike, VerboseSafeDumper
from jade.helper.constants import CODE_TAGS


class ConfigGUI:
    def __init__(self, yaml_run: PathLike, yaml_libs: PathLike) -> None:
        self.yaml_run = yaml_run
        self.yaml_libs = yaml_libs

        self.window = ThemedTk(theme="radiance")
        with as_file(files(res).joinpath("Jade.ico")) as file:
            try:
                self.window.wm_iconbitmap(False, file)
            except TclError:
                pass  # it seems it does not work on linux
        self.window.title("Configuration GUI")
        self.window.geometry("1200x600")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill="both")

        self.benchmarks_tab = ttk.Frame(self.notebook)
        self.libraries_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.benchmarks_tab, text="Benchmarks")
        self.notebook.add(self.libraries_tab, text="Libraries")

        self.create_benchmarks_tab()
        self.create_libraries_tab()

        # Add a save button
        self.save_button = ttk.Button(
            self.window, text="Save Settings", command=self.save_settings
        )
        self.save_button.pack(side="bottom", pady=10)

        # Bind the tab switch event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_switch)

    def create_benchmarks_tab(self):
        columns = (
            "name",
            "description",
            "generate",
            "mcnp",
            "d1s",
            "openmc",
            "serpent",
            "nps",
            "custom_input",
        )
        self.bench_tree = ttk.Treeview(
            self.benchmarks_tab, columns=columns, show="headings"
        )
        self.bench_tree.heading("name", text="Benchmark Name")
        self.bench_tree.heading("description", text="Description")
        self.bench_tree.heading("generate", text="Only Input")
        self.bench_tree.heading("mcnp", text="MCNP")
        self.bench_tree.heading("d1s", text="D1SUNED")
        self.bench_tree.heading("openmc", text="OpenMC")
        self.bench_tree.heading("serpent", text="Serpent")
        self.bench_tree.heading("nps", text="NPS")
        self.bench_tree.heading("custom_input", text="Custom Input")

        self.bench_tree.column("name", width=150)
        self.bench_tree.column("description", width=250)
        for column in columns[2:]:
            self.bench_tree.column(column, width=100, anchor=tk.CENTER)

        self.bench_tree.pack(expand=True, fill="both")

        # Create a mapping from column identifiers to column names
        self.bench_column_mapping = {f"#{i+1}": col for i, col in enumerate(columns)}
        self.bench_id_column_mapping = {col: f"#{i+1}" for i, col in enumerate(columns)}

        self.load_yaml_run(self.yaml_run)

        self.bench_tree.bind("<Button-1>", self.on_benchmark_click)

    def create_libraries_tab(self):
        with open(self.yaml_libs) as f:
            cfg = yaml.safe_load(f)
        library_names = list(cfg.keys())
        columns = ["benchmark"]
        columns.extend(library_names)
        self.libraries_tree = ttk.Treeview(
            self.libraries_tab, columns=columns, show="headings"
        )
        for lib in library_names:
            self.libraries_tree.heading(lib, text=lib)
            self.libraries_tree.column(lib, width=100, anchor=tk.CENTER)

        self.libraries_tree.pack(expand=True, fill="both")
        # Create a mapping from column identifiers to column names
        self.lib_column_mapping = {f"#{i+1}": col for i, col in enumerate(columns)}
        self.lib_id_column_mapping = {col: f"#{i+1}" for i, col in enumerate(columns)}

    def load_yaml_run(self, yaml_file):
        with open(yaml_file) as f:
            cfg = yaml.safe_load(f)
        self.original_run_yaml = cfg

        benchmark_libs = {}
        for benchmark, values in cfg.items():
            codes = {"mcnp": "", "d1s": "", "openmc": "", "serpent": ""}

            if values["only_input"]:
                only_input = "X"
            else:
                only_input = ""

            custom_inp = values["custom_input"]
            if custom_inp is None:
                custom_inp = ""

            for code in CODE_TAGS:
                if code == "exp":
                    continue
                libs = values["codes"][code]
                if len(libs) > 0:
                    codes[code] = "X"
                    # store the libraries to be run for each benchmark
                    benchmark_libs[benchmark] = libs

            self.bench_tree.insert(
                "",
                "end",
                values=(
                    benchmark,
                    values["description"],
                    only_input,
                    codes["mcnp"],
                    codes["d1s"],
                    codes["openmc"],
                    codes["serpent"],
                    values["nps"],
                    custom_inp,
                ),
            )
        self.benchmark_libs = benchmark_libs

    def on_benchmark_click(self, event):
        # Identify the row and column under the cursor
        region = self.bench_tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.bench_tree.identify_row(event.y)
            column_id = self.bench_tree.identify_column(event.x)
            column_name = self.bench_column_mapping[column_id]

            # Get the current value of the cell
            item = self.bench_tree.item(row_id)
            column_index = int(column_id[1:]) - 1
            current_value = item["values"][column_index]

            if column_name in (
                "generate",
                "mcnp",
                "d1s",
                "openmc",
                "serpent",
            ):  # Checkboxes for "Generate Input" and "Run Benchmark"
                new_value = "X" if current_value == "" else ""
                self.bench_tree.set(row_id, column_id, new_value)
            elif column_name in ("name", "description"):
                pass  # Do nothing for the "Name" and "Description" columns
            else:  # Entry widgets for other columns
                x, y, width, height = self.bench_tree.bbox(row_id, column_id)
                entry = ttk.Entry(self.bench_tree)
                entry.place(x=x, y=y, width=width, height=height)
                # For NPS force it to be an integer
                entry.insert(0, current_value)
                entry.focus()

                def on_focus_out(event):
                    self.bench_tree.set(row_id, column_id, entry.get())
                    entry.destroy()

                entry.bind("<FocusOut>", on_focus_out)

    def on_library_click(self, event):
        # Identify the row and column under the cursor
        region = self.libraries_tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.libraries_tree.identify_row(event.y)
            column_id = self.libraries_tree.identify_column(event.x)
            column_name = self.lib_column_mapping[column_id]

            # Get the current value of the cell
            item = self.libraries_tree.item(row_id)
            column_index = int(column_id[1:]) - 1
            current_value = item["values"][column_index]

            # select libraries
            if column_name != "benchmark":
                new_value = "X" if current_value == "" else ""
                self.libraries_tree.set(row_id, column_id, new_value)

    def on_tab_switch(self, event):
        selected_tab = event.widget.tab(event.widget.index("current"))["text"]
        if selected_tab == "Libraries":
            self.update_libraries_tab()

    def update_libraries_tab(self):
        # Populate the table with selected benchmarks
        current_benchmarks = {
            self.libraries_tree.item(child)["values"][0]: child
            for child in self.libraries_tree.get_children()
        }

        # Get the selected benchmarks from the benchmarks_tree
        selected_benchmarks = {}
        for child in self.bench_tree.get_children():
            values = self.bench_tree.item(child, "values")
            if any(value == "X" for value in values[2:7]):
                benchmark_name = values[0]
                selected_benchmarks[benchmark_name] = values

        # Remove rows that do not have a selected benchmark
        for benchmark_name in list(current_benchmarks.keys()):
            if benchmark_name not in selected_benchmarks:
                self.libraries_tree.delete(current_benchmarks[benchmark_name])

        # Add new rows for newly selected benchmarks
        for benchmark_name, values in selected_benchmarks.items():
            if benchmark_name not in current_benchmarks:
                row_values = [benchmark_name]
                for lib in self.libraries_tree["columns"][1:]:
                    if benchmark_name not in self.benchmark_libs:
                        row_values.append("")
                    elif lib in self.benchmark_libs[benchmark_name]:
                        row_values.append("X")
                    else:
                        row_values.append("")
                self.libraries_tree.insert("", "end", values=row_values)

        # Bind single click event for library selection
        self.libraries_tree.bind("<Button-1>", self.on_library_click)

    def save_settings(self):
        # Gather the selected settings from the benchmarks_tree
        benchmarks = {}
        for child in self.bench_tree.get_children():
            values = self.bench_tree.item(child, "values")
            row = {"codes": {}}
            for i, value in enumerate(values):
                col = self.bench_column_mapping[f"#{i+1}"]
                if col == "name":
                    name = value
                    libs = self._get_lib_settings(name)
                elif col in CODE_TAGS:
                    if value == "X":
                        row["codes"][col] = libs
                    else:
                        row["codes"][col] = []
                elif col == "generate":
                    if value == "X":
                        val = True
                    else:
                        val = False
                    row["only_input"] = val
                else:
                    row[col] = value

            benchmarks[name] = row

        # Ask the user for a file path to save the settings
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml", filetypes=[("YAML files", "*.yml")]
        )
        if file_path:
            with open(file_path, "w") as file:
                yaml.dump(
                    benchmarks, file, default_flow_style=False, Dumper=VerboseSafeDumper
                )
            messagebox.showinfo("Success", "Settings saved successfully!")

    def _get_lib_settings(self, benchmark_name: str) -> list[str]:
        # get the row corresponding to the benchmark name in the lib tree
        libs = []
        for child in self.libraries_tree.get_children():
            values = self.libraries_tree.item(child, "values")
            # if the bench row is found, get the libraries
            if values[0] == benchmark_name:
                libs = []
                for i, value in enumerate(values[1:]):
                    if value == "X":
                        col = self.lib_column_mapping[f"#{i+2}"]
                        libs.append(col)

        return libs


if __name__ == "__main__":
    yaml_run = "src/jade/resources/default_cfg/run_cfg.yml"
    yaml_libs = "src/jade/resources/default_cfg/libs_cfg.yml"
    app = ConfigGUI(yaml_run, yaml_libs)
    app.window.mainloop()
