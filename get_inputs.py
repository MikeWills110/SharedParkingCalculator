# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020
# REVISED: May 2026 — removed os.chdir, added type hints, reduced repetition.

from __future__ import annotations

import argparse
import os

import pandas as pd


def normalize_text(text: str) -> str:
    """Normalize unicode characters to handle curly apostrophes and other special characters."""
    text = text.replace("\u2019", "'")  # Right single quotation mark
    text = text.replace("\u2018", "'")  # Left single quotation mark
    text = text.replace("\u00b4", "'")  # Acute accent
    text = text.replace("\u0060", "'")  # Grave accent
    return text


def normalize_dataframe_index(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize all index values in a dataframe and remove NaN indices."""
    df = df[df.index.notna()]
    df.index = df.index.map(normalize_text)
    df = df[~df.index.duplicated(keep="first")]
    return df


def _read_csv(path: str) -> pd.DataFrame:
    """Read a CSV with the first column as index and normalize the index."""
    df = pd.read_csv(path, index_col=0)
    return normalize_dataframe_index(df)


def get_working_directory() -> argparse.Namespace:
    """
    Parse the ``--dir`` command-line argument for the project working directory.

    Returns
    -------
    argparse.Namespace
        Namespace with a ``dir`` attribute containing the working directory path.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        type=str,
        help="path to shared parking program in your project folder",
    )
    return parser.parse_args()


def get_inputs(
    input_directory: str | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load all required CSV input files.

    Parameters
    ----------
    input_directory : str or None
        Path to the Inputs folder. If ``None``, falls back to parsing
        ``--dir`` from the command line (legacy behaviour).

    Returns
    -------
    tuple of 7 DataFrames
        base_parking_demand, customer_employee_split, tod_weekday,
        tod_weekend, noncaptive_weekday, noncaptive_weekend, monthly_factors
    """
    if input_directory is None:
        in_arg = get_working_directory()
        input_directory = os.path.join(in_arg.dir, "Inputs")

    return (
        _read_csv(os.path.join(input_directory, "BaseParkingDemand.csv")),
        _read_csv(os.path.join(input_directory, "CustomerEmployeeSplit.csv")),
        _read_csv(os.path.join(input_directory, "TimeOfDayWeekday.csv")),
        _read_csv(os.path.join(input_directory, "TimeOfDayWeekend.csv")),
        _read_csv(os.path.join(input_directory, "NoncaptiveAdjustmentWeekday.csv")),
        _read_csv(os.path.join(input_directory, "NoncaptiveAdjustmentWeekend.csv")),
        _read_csv(os.path.join(input_directory, "MonthlyAdjustment.csv")),
    )
