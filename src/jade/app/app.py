from __future__ import annotations

import logging
import os
import shutil
import time
from importlib.resources import files
from pathlib import Path

import yaml
from tqdm import tqdm

import jade.resources as res
from jade import resources
from jade.app.fetch import fetch_f4e_inputs, fetch_iaea_inputs, fetch_nonIAEA_exp_data
from jade.config.paths_tree import PathsTree
from jade.config.pp_config import PostProcessConfig
from jade.config.raw_config import ConfigRawProcessor
from jade.config.run_config import RunConfig, RunMode
from jade.config.status import GlobalStatus
from jade.helper.__optionals__ import TKINTER_AVAIL, OMC_AVAIL

if TKINTER_AVAIL:
    from jade.gui.post_config_gui import PostConfigGUI
    from jade.gui.run_config_gui import ConfigGUI
from jade.helper.aux_functions import PathLike, add_rmode0, get_code_lib, print_code_lib
from jade.helper.constants import CODE, EXP_TAG, FIRST_INITIALIZATION, JADE_TITLE
from jade.post.atlas_processor import AtlasProcessor
from jade.post.excel_processor import ExcelProcessor
from jade.post.raw_processor import RawProcessor
from jade.run.benchmark import BenchmarkRunFactory, launch_global_jobs

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS_PATH = files(res).joinpath("default_cfg")


class JadeApp:
    def __init__(
        self,
        root: PathLike | None = None,
        skip_init: bool = False,
    ):
        if root is None:
            root = os.getcwd()

        # Initialize the local installation if it was never done
        self.tree = PathsTree(root)
        if self.tree.check_not_installed_folders(root) and not skip_init:
            self.tree.init_tree()
            self.restore_default_cfg(FIRST_INITIALIZATION)
            self.update_inputs()
            return

        # parse the config files
        self.run_cfg = RunConfig.from_root(self.tree)
        # parse the post-processing config
        self.pp_cfg = PostProcessConfig(self.tree.cfg.bench_pp)

        self._status = None

    @property
    def status(self) -> GlobalStatus:
        """Lazy-load the global status on first access."""
        if self._status is None:
            logger.info("Initializing the global status (lazy-loaded)")
            self._status = GlobalStatus(
                simulations_path=self.tree.simulations,
                raw_results_path=self.tree.raw,
            )
        return self._status

    def initialize_log(self) -> None:
        """Initialize the custom python logger for JADE."""
        log = os.path.join(
            self.tree.logs, "Log " + time.ctime().replace(":", "-") + ".txt"
        )
        jade_logger = logging.getLogger("jade")
        jade_logger.setLevel(logging.DEBUG)

        # Clear any existing handlers and prevent propagation to root logger
        jade_logger.handlers.clear()
        jade_logger.propagate = False

        # set the logging to a file and keep warnings to video
        # Create a file handler for logging INFO level messages
        file_handler = logging.FileHandler(log, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        # Create a console handler for logging WARNING and ERROR level messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%H:%M:%S",
            )
        )

        jade_logger.addHandler(file_handler)
        jade_logger.addHandler(console_handler)

        jade_logger.debug(JADE_TITLE)

    def update_inputs(self):
        """Update the benchmark inputs for the simulations.

        This will re-fetch inputs from the various repositories that feed JADE.
        """
        # install IAEA inputs and experimental data
        success = fetch_iaea_inputs(
            self.tree.benchmark_input_templates, self.tree.exp_data
        )
        if not success:
            logger.error("Failed to update the IAEA benchmark inputs.")

        # Install F4E exp data
        success = fetch_nonIAEA_exp_data(self.tree.exp_data)
        if not success:
            logger.error("Failed to update the F4E experimental data.")

        # Install F4E inputs
        f4e_gitlab_token = os.getenv("F4E_GITLAB_TOKEN")

        if f4e_gitlab_token is not None:
            success = fetch_f4e_inputs(
                self.tree.benchmark_input_templates,
                f4e_gitlab_token,
            )
            if not success:
                logger.error("Failed to update the F4E benchmark inputs.")
        else:
            logger.info("No F4E token found. Skipping F4E inputs update.")

    def restore_default_cfg(self, msg: str = ""):
        """Reset the configuration files to installation default. The session
        is re-initialized.
        """
        # Remove the user configurations
        shutil.rmtree(self.tree.cfg.path)
        # Copy default configurations
        shutil.copytree(DEFAULT_SETTINGS_PATH, self.tree.cfg.path)
        print(msg)

    def rmv_runtpe(self):
        """Remove the runtpe files from the simulation folders of mcnp."""
        # Walk through the root folder and remove the runtpe files
        for pathroot, folder, files in os.walk(self.tree.simulations):
            if len(files) > 0 and len(folder) == 0:  # only files and no folders
                # get the code
                codelib = Path(pathroot).parent.parent.name
                code, _ = get_code_lib(codelib)
                if CODE(code) == CODE.MCNP:  # only for mcnp
                    for file in os.listdir(pathroot):
                        if file.endswith(".r"):
                            os.remove(os.path.join(pathroot, file))
        logger.info("Runtpe files were removed successfully")

    def run_benchmarks(self, testing: bool = False) -> list[str] | None:
        """Run the benchmarks according to the configuration."""
        logger.info("Running benchmarks")
        # first thing do to is to check if the benchmarks were already run
        simulated = []
        for bench_name, cfg in self.run_cfg.benchmarks.items():
            for code, lib in cfg.run:
                # First of all check if the benchmark was already run for some of the
                # benchmarks
                if self.status.was_simulated(code, lib.name, bench_name):
                    simulated.append((code, lib, bench_name))

        # if yes, ask for confirmation before overriding
        proceed_flag = True
        if len(simulated) > 0:
            logger.warning("The following benchmarks were already simulated:")
            for code, lib, bench_name in simulated:
                logger.warning(f"{code} - {lib.name}: {bench_name}")
            logger.warning("If you continue, the results will be overwritten.")
            proceed_flag = input("Do you want to continue? [y/n]: ").lower() == "y"

        if proceed_flag:
            run_commands = []
            for bench_name, cfg in self.run_cfg.benchmarks.items():
                benchmark = BenchmarkRunFactory.create(
                    cfg,
                    self.tree.simulations,
                    self.tree.benchmark_input_templates,
                    self.run_cfg.env_vars,
                )
                commands = benchmark.run()
                run_commands.extend(commands)
            # In case only one job is requested, build it after all commands
            # have been collected
            if self.run_cfg.env_vars.run_mode == RunMode.GLOBAL_JOB:
                jobs = launch_global_jobs(
                    run_commands, self.run_cfg.env_vars, test=testing
                )
                logger.info("Benchmarks run have been submitted.")
                return jobs
        logger.info("Benchmarks run completed.")

    def continue_run(self, testing: bool = False):
        """Continue the run of the benchmarks that were not completed."""
        commands = []
        for bench_name, cfg in self.run_cfg.benchmarks.items():
            benchmark = BenchmarkRunFactory.create(
                cfg,
                self.tree.simulations,
                self.tree.benchmark_input_templates,
                self.run_cfg.env_vars,
            )
            command = benchmark.continue_run(testing=testing)
            commands.append(command)
        logger.info("Benchmarks run have been submitted.")
        return commands

    def raw_process(self, force: bool = False, subset: list[str] | None = None):
        """Process the raw data from the simulations.

        Parameters
        ----------
        force : bool, optional
            Whether to force the processing on all available simulations overriding
            previous results, by default False
        subset : list[str] | None, optional
            A list of specific benchmarks to process, by default None
        """
        logger.info("Processing raw data")
        # first identify all simulations that were successful but were not processed
        root_cfg = self.tree.cfg.bench_raw
        successful = self.status.get_successful_simulations()

        def get_config(
            root_cfg: Path, code: CODE, bench: str
        ) -> ConfigRawProcessor | None:
            # get the correspondent raw processor configuration
            cfg_file = Path(root_cfg, f"{code.value}/{bench}.yaml")
            try:
                raw_cfg = ConfigRawProcessor.from_yaml(cfg_file)
            except FileNotFoundError:
                logger.warning(f"Configuration file for {code.value} {bench} not found")
                return None
            return raw_cfg

        to_process = {}
        for code, lib, bench in successful:
            # if openmc is not available in system, skip processing
            if code == CODE.OPENMC and not OMC_AVAIL:
                logger.warning(f"OpenMC not installed. Skipping {bench} processing.")
                continue

            if force:
                # process all the successful simulations, force override
                raw_cfg = get_config(root_cfg, code, bench)
                if raw_cfg is None:
                    continue
                to_process[(code, lib, bench)] = raw_cfg
                logger.info(f"Processing {code.value} {lib} {bench} benchmarks")
            else:
                # only process if not already done
                if (code, lib, bench) not in self.status.raw_data:
                    if subset is not None and bench not in subset:
                        continue

                    raw_cfg = get_config(root_cfg, code, bench)
                    if raw_cfg is None:
                        continue
                    to_process[(code, lib, bench)] = raw_cfg
                    logger.info(f"Processing {code.value} {lib} {bench} benchmarks")

        # process the raw data
        for (code, lib, bench), cfg in tqdm(to_process.items(), desc="Process raw"):
            folders = self.tree.get_bench_sim_folders(code, lib, bench)
            out_folder = Path(self.tree.raw, print_code_lib(code, lib), bench)
            # always ovveride eventual previous results here
            if out_folder.exists():
                shutil.rmtree(out_folder)
            os.makedirs(out_folder, exist_ok=True)
            for sim_folder, _ in folders:
                processor = RawProcessor(cfg, sim_folder, out_folder)
                processor.process_raw_data()

        logger.info("Raw data processing completed.")

    def post_process(self):
        """Post-process the data."""
        logger.info("Post-processing data")
        # load the pp code-lib requests
        with open(self.tree.cfg.pp_cfg) as f:
            to_pp = yaml.safe_load(f)
        codelibs_tags = to_pp["code_libs"]
        benchmarks = to_pp["benchmarks"]

        for benchmark in tqdm(benchmarks, desc="Benchmarks"):
            logger.info(f"Post-processing {benchmark}")
            # get the benchmark configurations
            excel_cfg = self.pp_cfg.excel_cfgs[benchmark]
            atlas_cfg = self.pp_cfg.atlas_cfgs[benchmark]

            code_libs = []
            # if exp is in the libraries, put it always first
            if EXP_TAG in codelibs_tags:
                codelibs_tags.remove(EXP_TAG)
                codelibs_tags.insert(0, EXP_TAG)

            for codelib in codelibs_tags:
                # Check if the code-lib is available in this benchmark
                # if yes, append it to the list
                code, lib = get_code_lib(codelib)
                if self.status.is_raw_available(codelib, benchmark):
                    code_libs.append((code, lib))
                else:
                    logger.info(f"{codelib} is not available for {benchmark}")

            # in case there are less than two code-libs skip the comparison
            if len(code_libs) < 2:
                logger.warning(
                    f"Less than two code-libs available for {benchmark}, skipped"
                )
                continue

            # check that the benchmark versions are consistent with each other
            self.status.validate_codelibs(code_libs, benchmark)

            # prepare the new paths
            pp_path = self.tree.get_new_post_bench_path(benchmark)
            excel_folder = Path(pp_path, "excel")
            atlas_folder = Path(pp_path, "atlas")
            os.mkdir(excel_folder)
            os.mkdir(atlas_folder)

            # perform the excel processing
            logger.info("Processing Excel files for %s", benchmark)
            excel_processor = ExcelProcessor(
                self.tree.raw,
                excel_folder,
                excel_cfg,
                code_libs,
            )
            excel_processor.process()

            # perform the atlas processing
            logger.info("Processing Atlas files for %s", benchmark)
            atlas_processor = AtlasProcessor(
                self.tree.raw,
                atlas_folder,
                atlas_cfg,
                code_libs,
                files(resources).joinpath("atlas_template.docx"),
            )
            atlas_processor.process()

    def start_run_config_gui(self):
        """Start the configuration GUI."""
        if not TKINTER_AVAIL:
            logger.error("Tkinter is not available. Cannot start the GUI.")
        else:
            logger.info("Starting the configuration GUI")
            app = ConfigGUI(self.tree.cfg.run_cfg, self.tree.cfg.libs_cfg)
            app.window.mainloop()

    def start_pp_config_gui(self):
        """Start the post-processing configuration GUI."""
        if not TKINTER_AVAIL:
            logger.error("Tkinter is not available. Cannot start the GUI.")
        else:
            logger.info("Starting the post-processing configuration GUI")
            app = PostConfigGUI(self.status)
            app.mainloop()

    def add_rmode(self):
        """Add the rmode=0 to the mcnp input files."""
        logger.info("Adding RMODE 0 to the MCNP input files")
        add_rmode0(self.tree.benchmark_input_templates)

    def print_unfinished_runs(self):
        """Print the simulations that were not completed."""
        for key, status in self.status.simulations.items():
            if len(status.failed_simulations) > 0:
                code, lib, bench = key
                logging.info(f"Unfinished simulations for {code} {lib} {bench}:")
                for sim in status.failed_simulations:
                    logging.info(f"\t{sim}")
