from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import yaml

from jade.helper.aux_functions import PathLike


class ConfigRawProcessor:
    def __init__(self, results: list[ResultConfig]) -> None:
        """Config for the post-processing of the tallies into raw results.

        Parameters
        ----------
        results : list[ResultConfig]
            List of results to build from the simulation tallies.
        """
        self.results = results

    @classmethod
    def from_yaml(cls, config_file: PathLike) -> ConfigRawProcessor:
        with open(config_file) as f:
            cfg = yaml.safe_load(f)

        results = []
        for res_name, dict in cfg.items():
            # discard keys that start with _, they are aliases
            if isinstance(res_name, str) and res_name.startswith("_"):
                continue
            results.append(ResultConfig.from_dict(dict, res_name))

        return ConfigRawProcessor(results)


@dataclass
class ResultConfig:
    """A Result is a combination of one or more tallies. This configures how to build
    it from the tallies of the simulation.

    Parameters
    ----------
    name : int
        Unique identifier of the result
    modify : dict[int, list[tuple[TallyModOption, dict]]]
        dictionary of tallies to be modified. For each specify the list of modifications
        to apply. For each modification, the keyarguments to pass to the modification
        function should also be provided.
    concat_option : TallyConcatOption
        How to combine the tallies
    """

    name: int
    modify: dict[int, list[tuple[TallyModOption, dict]]]
    concat_option: TallyConcatOption

    @classmethod
    def from_dict(cls, dictionary: dict, name) -> ResultConfig:
        mods = {}
        concat_option = TallyConcatOption(dictionary.pop("concat_option"))
        for tallyid, modifications in dictionary.items():
            new_modifications = []
            for option, keyargs in modifications:
                mod_option = TallyModOption(option)
                new_modifications.append((mod_option, keyargs))
            mods[tallyid] = new_modifications

        return ResultConfig(
            name=name,
            modify=mods,
            concat_option=concat_option,
        )


class TallyModOption(Enum):
    """Available options to modify the tally dataframes."""

    LETHARGY = "lethargy"
    SCALE = "scale"
    NO_ACTION = "no_action"
    BY_ENERGY = "by_energy"
    CONDENSE_GROUPS = "condense_groups"
    REPLACE = "replace"
    ADD_COLUMN = "add_column"
    KEEP_LAST_ROW = "keep_last_row"
    GROUPBY = "groupby"
    DELETE_COLS = "delete_cols"
    FORMAT_DECIMALS = "format_decimals"
    TOF_TO_ENERGY = "tof_to_energy"


class TallyConcatOption(Enum):
    """Available options to concatenate different tally dataframes"""

    SUM = "sum"
    CONCAT = "concat"
    NO_ACTION = "no_action"
    SUBTRACT = "subtract"
    RATIO = "ratio"
