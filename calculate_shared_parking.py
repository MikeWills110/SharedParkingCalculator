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
    directory and