# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020
# PURPSOSE: Create a function that calculates shared parking demand for different land uses at a mixed-use site
#           on an hourly basis within a day, for each month of the year. Plot the results in a seaborn facet grid
#           object to show seasonal trends. Command line arguments:
#               1. Working directory where scripts and inputs are stored as --dir

import os
import sys
from datetime import datetime

from LandUse import parking_demand
from get_inputs import get_working_directory


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


def _find_existing_path_case_insensitive(base_dir, relative_path):
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


def _resolve_required_files(base_dir, required_relative_paths):
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


def _print_inputs_snapshot(resolved_required_files):
    print("Inputs snapshot (file, modified, size):")
    for rel, full in resolved_required_files:
        stat = os.stat(full)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size = stat.st_size
        print(f"  - {rel} -> {full} | {modified} | {size} bytes")
    print("")


# Get working directory from command line input
in_arg = get_working_directory()
working_directory = in_arg.dir

# Ensure Outputs directory exists (prevents OSError on fresh clones)
outputs_dir = os.path.join(working_directory, "Outputs")
os.makedirs(outputs_dir, exist_ok=True)

# Validate required inputs exist BEFORE running calculations (case-insensitive)
try:
    resolved_required_files = _resolve_required_files(working_directory, REQUIRED_INPUT_FILES)
except FileNotFoundError as e:
    print(str(e), file=sys.stderr)
    raise

# Print snapshot so you can confirm which input set produced the outputs
_print_inputs_snapshot(resolved_required_files)

# Calculate weekday parking tables and export to Excel
weekday_parking_demand = parking_demand("Weekday")
weekday_filepath = os.path.join(outputs_dir, "WeekdayParking.xlsx")
weekday_parking_demand.to_excel(weekday_filepath)

# Calculate weekend parking tables and export to Excel
weekend_parking_demand = parking_demand("Weekend")
weekend_filepath = os.path.join(outputs_dir, "WeekendParking.xlsx")
weekend_parking_demand.to_excel(weekend_filepath)

print("Shared parking calculations complete.")
print(f"Weekday output saved to: {os.path.abspath(weekday_filepath)}")
print(f"Weekend output saved to: {os.path.abspath(weekend_filepath)}")