# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020
# PURPSOSE: Create a function that calculates shared parking demand for different land uses at a mixed-use site
#           on an hourly basis within a day, for each month of the year. Plot the results in a seaborn facet grid
#           object to show seasonal trends. Command line arguments:
#               1. Working directory where scripts and inputs are stored as --dir

import os
from LandUse import parking_demand
from get_inputs import get_working_directory


def _format_for_excel(df):
    """
    Ensure Month and Time are the first two columns in Excel output.

    - If df has a MultiIndex (e.g., Month x Time), move index levels into columns.
    - If df has Month/Time already as columns, keep them.
    - Finally, reorder so Month and Time come first when present.
    """
    # Move index into columns so Excel doesn't get an unlabeled index column
    if getattr(df.index, "nlevels", 1) > 1:
        df = df.reset_index()
    elif df.index.name is not None:
        df = df.reset_index()

    # Normalize common index column names if they came from reset_index()
    rename_map = {}
    if "level_0" in df.columns and "Month" not in df.columns:
        rename_map["level_0"] = "Month"
    if "level_1" in df.columns and "Time" not in df.columns:
        rename_map["level_1"] = "Time"
    if rename_map:
        df = df.rename(columns=rename_map)

    # Reorder columns so Month then Time are first (when they exist)
    first_cols = [c for c in ["Month", "Time"] if c in df.columns]
    if first_cols:
        remaining = [c for c in df.columns if c not in first_cols]
        df = df[first_cols + remaining]

    return df


# Get working directory from command line input
in_arg = get_working_directory()
working_directory = in_arg.dir

# Ensure Outputs directory exists (prevents OSError on fresh clones)
outputs_dir = os.path.join(working_directory, "Outputs")
os.makedirs(outputs_dir, exist_ok=True)

# Calculate weekday parking tables and export to Excel
weekday_parking_demand = parking_demand("Weekday")
weekday_parking_demand = _format_for_excel(weekday_parking_demand)
weekday_filepath = os.path.join(outputs_dir, "WeekdayParking.xlsx")
weekday_parking_demand.to_excel(weekday_filepath, index=False)

# Calculate weekend parking tables and export to Excel
weekend_parking_demand = parking_demand("Weekend")
weekend_parking_demand = _format_for_excel(weekend_parking_demand)
weekend_filepath = os.path.join(outputs_dir, "WeekendParking.xlsx")
weekend_parking_demand.to_excel(weekend_filepath, index=False)

print("Shared parking calculations complete.")
print(f"Weekday output saved to: {weekday_filepath}")
print(f"Weekend output saved to: {weekend_filepath}")