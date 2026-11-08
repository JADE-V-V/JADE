"""Migration of raw results folders to the code-lib-version naming convention.

Raw results produced by older JADE versions are stored as
``<raw_root>/_<code>_-_<lib>_/<benchmark>``. The code version is now part of the
raw results identity, i.e. ``<raw_root>/_<code>_-_<version>_-_<lib>_/<benchmark>``.
The code version of the old results is recovered from the ``code_version`` field
of their ``metadata.json`` file.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from jade.helper.aux_functions import (
    PathLike,
    get_code_lib_version,
    print_code_lib,
    sanitize_code_version,
)
from jade.helper.constants import CODE

logger = logging.getLogger(__name__)


@dataclass
class RawMove:
    """A planned (or performed) move of a benchmark raw results folder.

    Attributes
    ----------
    source : Path
        current benchmark raw results folder.
    destination : Path | None
        new benchmark raw results folder. None if the folder cannot be migrated.
    reason : str
        explanation when the folder cannot be migrated, empty otherwise.
    """

    source: Path
    destination: Path | None
    reason: str = ""


def plan_raw_migration(raw_root: PathLike) -> list[RawMove]:
    """Identify the raw results folders that need to be renamed to include the
    code version.

    Parameters
    ----------
    raw_root : PathLike
        root of the raw results (e.g. the JADE_RAW_RESULTS repository).

    Returns
    -------
    list[RawMove]
        planned moves. Moves with a None destination cannot be migrated.
    """
    moves = []
    for codelib in sorted(os.listdir(raw_root)):
        codelib_path = Path(raw_root, codelib)
        if not codelib_path.is_dir():
            continue
        try:
            code_tag, lib, version = get_code_lib_version(codelib)
            code = CODE(code_tag)
        except ValueError:
            continue  # not a code-lib folder
        if version is not None or code == CODE.EXPERIMENT:
            continue  # already migrated or experimental data

        for benchmark in sorted(os.listdir(codelib_path)):
            bench_path = Path(codelib_path, benchmark)
            if not bench_path.is_dir():
                continue
            metadata_file = Path(bench_path, "metadata.json")
            try:
                with open(metadata_file) as f:
                    code_version = json.load(f).get("code_version")
            except (OSError, json.JSONDecodeError):
                moves.append(RawMove(bench_path, None, "missing metadata.json"))
                continue

            code_version = sanitize_code_version(code_version)
            if code_version is None:
                moves.append(RawMove(bench_path, None, "no code_version in metadata"))
                continue

            destination = Path(
                raw_root, print_code_lib(code, lib, version=code_version), benchmark
            )
            if destination.exists():
                moves.append(RawMove(bench_path, None, f"{destination} already exists"))
                continue
            moves.append(RawMove(bench_path, destination))
    return moves


def migrate_raw_results(raw_root: PathLike, dry_run: bool = False) -> list[RawMove]:
    """Rename old raw results folders so that they include the code version.

    Folders whose code version cannot be determined, or whose destination
    already exists, are left untouched.

    Parameters
    ----------
    raw_root : PathLike
        root of the raw results (e.g. the JADE_RAW_RESULTS repository).
    dry_run : bool, optional
        if True, only log the planned moves, by default False.

    Returns
    -------
    list[RawMove]
        all the planned moves, including the ones that could not be performed.
    """
    moves = plan_raw_migration(raw_root)
    for move in moves:
        if move.destination is None:
            logger.warning("Skipping %s: %s", move.source, move.reason)
            continue
        logger.info("Moving %s -> %s", move.source, move.destination)
        if dry_run:
            continue
        os.makedirs(move.destination.parent, exist_ok=True)
        shutil.move(move.source, move.destination)
        # remove the old code-lib folder if nothing is left
        if not any(move.source.parent.iterdir()):
            move.source.parent.rmdir()
    return moves
