from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from jade.config.raw_config import ConfigRawProcessor
from jade.helper.aux_functions import PathLike, get_jade_version
from jade.helper.constants import CODE
from jade.post.manipulate_tally import CONCAT_FUNCTIONS, MOD_FUNCTIONS
from jade.post.sim_output import MCNPSimOutput, OpenMCSimOutput


class RawProcessor:
    def __init__(
        self, cfg: ConfigRawProcessor, sim_folder: PathLike, out_folder: PathLike
    ) -> None:
        """Object in charge of processing the raw data from the simulation and to obtain
        the final raw csv results.

        Parameters
        ----------
        cfg : ConfigRawProcessor
            Instructions on how to process the raw data.
        sim_folder : PathLike
            Path to the simulation folder containing the output files.
        out_folder : PathLike
            path to the output folder where the .csv will be stored.

        Raises
        ------
        NotImplementedError
            If the code is not implemented yet for raw data processing.
        """
        self.cfg = cfg
        self.sim_folder = sim_folder
        self.out_folder = out_folder
        self.single_run_name = os.path.basename(sim_folder)

        # adjourn the metadata
        self.metadata = self._read_metadata_run()
        self.code = CODE(self.metadata["code"])

        # decide the proper simulation parser depending on codes
        if self.code in (CODE.MCNP, CODE.D1S):
            self.sim_output = MCNPSimOutput(sim_folder)
        elif self.code == CODE.OPENMC:
            self.sim_output = OpenMCSimOutput(sim_folder)
        else:
            raise NotImplementedError(
                f"Code {self.code} not implemented yet for raw data processing"
            )

    def process_raw_data(self) -> None:
        """Process the raw data from the simulation and store the results in the output
        folder as .csv files.
        """
        # dump the metadata
        metadatafile = Path(self.out_folder, "metadata.json")
        # if it is still not present, dump the metadata
        if not metadatafile.exists():
            self.metadata["jade_version"] = get_jade_version()
            self.metadata["code_version"] = self.sim_output._read_code_version()
            with open(metadatafile, "w") as file:
                json.dump(self.metadata, file, indent=4)

        for result in self.cfg.results:
            mod_tallies = []
            # first apply the modifications to the requested tallies
            for tallyid, modifications in result.modify.items():
                try:
                    tally = self.sim_output.tallydata[tallyid].copy()
                except KeyError:
                    # for some benchmarks it may happen that the tally is not found
                    logging.warning(
                        "Tally %s not found for %s", tallyid, self.single_run_name
                    )
                    continue
                for mod_option, keyargs in modifications:
                    tally = MOD_FUNCTIONS[mod_option](tally, **keyargs)
                mod_tallies.append(tally)
            # in case the number of found tallies is zero skip the df printing
            if len(mod_tallies) == 0:
                continue
            # then combine them as requested and dump them
            df = CONCAT_FUNCTIONS[result.concat_option](mod_tallies)
            outfile = Path(self.out_folder, f"{self.single_run_name} {result.name}.csv")
            df.to_csv(outfile, header=True, index=False)

    def _read_metadata_run(self) -> dict:
        """
        Retrieve the metadata from the run
        """
        try:
            with open(
                os.path.join(self.sim_folder, "metadata.json"),
            ) as file:
                metadata = json.load(file)
        except FileNotFoundError:
            logging.warning("No metadata file found at %s", self.sim_folder)
            metadata = {}

        return metadata
