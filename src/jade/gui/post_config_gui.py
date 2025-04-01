from __future__ import annotations

import tkinter as tk
from importlib.resources import as_file, files
from tkinter import TclError, filedialog, messagebox, ttk

import yaml

import jade.resources as res
from jade.config.status import GlobalStatus
from jade.helper.aux_functions import VerboseSafeDumper


class PostConfigGUI(tk.Tk):
    def __init__(self, status: GlobalStatus):
        super().__init__()
        self.title("Post-Processing Configuration")
        self.geometry("600x600")
        self.status = status

        with as_file(files(res).joinpath("Jade.ico")) as file:
            try:
                self.wm_iconbitmap(False, file)
            except TclError:
                pass  # seems like it does not work on linux

        self.create_widgets()

    def create_widgets(self):
        self.benchmark_label = ttk.Label(self, text="Select Benchmarks:")
        self.benchmark_label.pack(pady=5)

        self.benchmark_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.benchmark_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        self.code_lib_label = ttk.Label(self, text="Select Code Libraries:")
        self.code_lib_label.pack(pady=5)

        self.code_lib_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.code_lib_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.update_button = ttk.Button(
            button_frame, text="Update Selections", command=self.update_selections
        )
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            button_frame, text="Reset Selections", command=self._reset_selections
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(
            button_frame,
            text="Save Selections",
            command=self._save_selections,
            style="Green.TButton",
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        style = ttk.Style()
        style.configure("Green.TButton", foreground="green")

        self._reset_selections()

    def _save_selections(self):
        selected_benchmarks = list(self.displayed_benchmarks)
        selected_code_libs = list(self.displayed_code_libs)

        # At least two libraries should be selected
        if len(selected_code_libs) < 2:
            messagebox.showerror(
                "Error", "Please select at least two code-libraries to proceed."
            )
            self._reset_selections()
            return

        data = {
            "benchmarks": selected_benchmarks,
            "code_libs": selected_code_libs,
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yml"), ("All files", "*.*")],
        )

        if file_path:
            with open(file_path, "w") as file:
                yaml.dump(
                    data, file, default_flow_style=False, Dumper=VerboseSafeDumper
                )
            messagebox.showinfo("Success", "Settings saved successfully!")

    def _reset_selections(self):
        libs, benchmarks = self.status.get_all_raw()
        self._init_list(self.benchmark_listbox, benchmarks)
        self._init_list(self.code_lib_listbox, libs)
        self.displayed_benchmarks = benchmarks
        self.displayed_code_libs = libs

    @staticmethod
    def _init_list(listbox: tk.Listbox, items: list | set):
        # clear the listbox first
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def update_selections(self):
        selected_benchmarks = [
            self.benchmark_listbox.get(i) for i in self.benchmark_listbox.curselection()
        ]
        selected_code_libs = [
            self.code_lib_listbox.get(i) for i in self.code_lib_listbox.curselection()
        ]

        if selected_benchmarks:
            # Get the available code libraries for the selected benchmarks
            available_code_libs = self.status.get_codelibs_from_raw_benchmark(
                selected_benchmarks
            )
            self.code_lib_listbox.delete(0, tk.END)
            codelib2display = []
            for code_lib in available_code_libs:
                if code_lib in self.displayed_code_libs:
                    self.code_lib_listbox.insert(tk.END, code_lib)
                    codelib2display.append(code_lib)

            # Only display the selected benchmarks
            self.benchmark_listbox.delete(0, tk.END)
            for benchmark in selected_benchmarks:
                self.benchmark_listbox.insert(tk.END, benchmark)

            self.displayed_benchmarks = selected_benchmarks
            self.displayed_code_libs = codelib2display

        if selected_code_libs:
            # Get the available benchmarks for the selected code libraries
            available_benchmarks = self.status.get_benchmark_from_raw_codelib(
                selected_code_libs
            )
            self.benchmark_listbox.delete(0, tk.END)
            benchmark2display = []
            for benchmark in available_benchmarks:
                if benchmark in self.displayed_benchmarks:
                    self.benchmark_listbox.insert(tk.END, benchmark)
                    benchmark2display.append(benchmark)

            # Only display the selected code libraries
            self.code_lib_listbox.delete(0, tk.END)
            for code_lib in selected_code_libs:
                self.code_lib_listbox.insert(tk.END, code_lib)

            self.displayed_benchmarks = benchmark2display
            self.displayed_code_libs = selected_code_libs


if __name__ == "__main__":
    status = GlobalStatus(
        r"D:\DATA\laghida\Documents\GitHub\JADE\Code\tests\dummy_structure\simulations",
        r"D:\DATA\laghida\Documents\GitHub\JADE\Code\tests\dummy_structure\raw_data",
    )
    app = PostConfigGUI(status)
    app.mainloop()
