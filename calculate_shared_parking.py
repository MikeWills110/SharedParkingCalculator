# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020
# PURPOSE: Create a function that calculates shared parking demand for different land uses at a mixed-use site
#          on an hourly basis within a day, for each month of the year. Plot the results in a seaborn facet grid
#          object to show seasonal trends. Command line arguments:
#              1. Working directory where scripts and inputs are stored as --dir

from __future__ import annotations

import logging
import os
import subprocess
import sys
from datetime import datetime

import pandas as pd

from LandUse import parking_demand
from get_inputs import get_working_directory

logger = logging.getLogger(__name__)

# Required inputs (the *_original backup file is intentionally ignored)
REQUIRED_INPUT_FILES = [
    os.path.join("Inputs", "BaseParkingDemand.csv"),
    os.path.join("Inputs", "CustomerEmployeeSplit.csv"),
    os.path.join("Inputs", "LandUseProgram.csv"),
    os.path.join("Inputs", "MonthlyAdjustment.csv"),
    os.path.join("Inputs", "NoncaptiveAdjustmentWeekday.csv"),
    os.path.join("Inputs", "NoncaptiveAdjustmentWeekend.csv"),
    os.path.join("Inputs", "TimeOfDayWeekday.csv"),
    os.path.join("Inputs", "TimeOfDayWeekend.csv"),
]


def _find_existing_path_case_insensitive(base_dir: str, relative_path: str) -> str | None:
    """
    Return an existing path on disk that matches relative_path, ignoring case of
    directory and file names. Returns None if not found.

    This is especially useful when a file might be named .CSV vs .csv (or other
    case differences) and the project is run on different platforms/filesystems.
    """
    parts = relative_path.replace("\\", "/").split("/")
    current_dir = os.path.abspath(base_dir)

    for part in parts:
        if not os.path.isdir(current_dir):
            return None

        try:
            entries = os.listdir(current_dir)
        except OSError:
            return None

        match = None
        part_lower = part.lower()
        for entry in entries:
            if entry.lower() == part_lower:
                match = entry
                break

        if match is None:
            return None

        current_dir = os.path.join(current_dir, match)

    return current_dir


def _resolve_required_files(
    base_dir: str, required_relative_paths: list[str]
) -> list[tuple[str, str]]:
    """
    For each relative path, find the actual on-disk path (case-insensitive).
    Returns a list of tuples: (original_relative_path, resolved_full_path).
    Raises FileNotFoundError if any are missing.
    """
    resolved = []
    missing = []

    for rel in required_relative_paths:
        full = _find_existing_path_case_insensitive(base_dir, rel)
        if full is None or not os.path.isfile(full):
            missing.append(rel)
        else:
            resolved.append((rel, full))

    if missing:
        missing_list = "\n".join(f"  - {p}" for p in missing)
        raise FileNotFoundError(
            "Missing required input file(s) under the working directory.\n"
            f"Working directory: {os.path.abspath(base_dir)}\n"
            "Expected to find (case-insensitive match):\n"
            f"{missing_list}\n\n"
            "Fix:\n"
            "  - confirm you ran with the correct --dir\n"
            "  - confirm the Inputs/ folder contains the required CSVs\n"
        )

    return resolved


def _print_inputs_snapshot(resolved_required_files: list[tuple[str, str]]) -> None:
    logger.info("Inputs snapshot (file, modified, size):")
    for rel, full in resolved_required_files:
        stat = os.stat(full)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size = stat.st_size
        logger.info(f"  - {rel} -> {full} | {modified} | {size} bytes")
    logger.info("")


def _build_inputs_snapshot_rows(
    resolved_required_files: list[tuple[str, str]],
) -> list[dict[str, str | int]]:
    rows = []
    for rel, full in resolved_required_files:
        stat = os.stat(full)
        rows.append(
            {
                "required_file": rel,
                "resolved_path": os.path.abspath(full),
                "modified_local": datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "size_bytes": stat.st_size,
            }
        )
    return rows


def _get_git_commit_hash(repo_dir: str) -> str | None:
    """
    Best-effort: return current git commit hash (short) for the repo at repo_dir.
    Returns None if git isn't available or repo_dir isn't a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return None


def _write_excel_with_metadata(
    df: pd.DataFrame,
    out_path: str,
    resolved_required_files: list[tuple[str, str]],
    *,
    mode: str,
    working_directory: str,
) -> None:
    """
    Write the main results plus a Metadata sheet containing run info and a full
    inputs snapshot, so the workbook is self-describing.

    df: pandas DataFrame
    out_path: .xlsx file path to write
    resolved_required_files: list of (relative_required_path, resolved_full_path)
    mode: "Weekday" or "Weekend"
    working_directory: base working directory used for the run
    """
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    git_hash = _get_git_commit_hash(working_directory)

    df_kv = pd.DataFrame(
        [
            {"key": "run_timestamp_local", "value": run_ts},
            {"key": "working_directory", "value": os.path.abspath(working_directory)},
            {"key": "mode", "value": mode},
            {"key": "git_commit", "value": git_hash if git_hash else ""},
        ]
    )

    df_inputs = pd.DataFrame(_build_inputs_snapshot_rows(resolved_required_files))

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        # Main results
        df.to_excel(writer, sheet_name="Results", index=True)

        # Metadata (key/value + inputs table)
        df_kv.to_excel(writer, sheet_name="Metadata", index=False, startrow=0)
        df_inputs.to_excel(
            writer, sheet_name="Metadata", index=False, startrow=len(df_kv) + 2
        )


def main() -> None:
    """Entry point: parse args, validate inputs, run calculations, write output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    # Get working directory from command line input
    in_arg = get_working_directory()
    working_directory = in_arg.dir

    # Ensure Outputs directory exists (prevents OSError on fresh clones)
    outputs_dir = os.path.join(working_directory, "Outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # Validate required inputs exist BEFORE running calculations (case-insensitive)
    try:
        resolved_required_files = _resolve_required_files(
            working_directory, REQUIRED_INPUT_FILES
        )
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    # Print snapshot so you can confirm which input set produced the outputs
    _print_inputs_snapshot(resolved_required_files)

    # Calculate weekday parking tables and export to Excel (with metadata)
    weekday_parking_demand = parking_demand("Weekday")
    weekday_filepath = os.path.join(outputs_dir, "WeekdayParking.xlsx")
    _write_excel_with_metadata(
        weekday_parking_demand,
        weekday_filepath,
        resolved_required_files,
        mode="Weekday",
        working_directory=working_directory,
    )

    # Calculate weekend parking tables and export to Excel (with metadata)
    weekend_parking_demand = parking_demand("Weekend")
    weekend_filepath = os.path.join(outputs_dir, "WeekendParking.xlsx")
    _write_excel_with_metadata(
        weekend_parking_demand,
        weekend_filepath,
        resolved_required_files,
        mode="Weekend",
        working_directory=working_directory,
    )

    logger.info("Shared parking calculations complete.")
    logger.info(f"Weekday output saved to: {os.path.abspath(weekday_filepath)}")
    logger.info(f"Weekend output saved to: {os.path.abspath(weekend_filepath)}")


if __name__ == "__main__":
    main()
