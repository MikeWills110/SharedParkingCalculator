# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020
# REVISED: May 2026 — removed module-level side effects, converted class to
#          functions, added type hints, lazy-loaded inputs.

from __future__ import annotations

import numpy as np
import pandas as pd

from get_inputs import get_inputs

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TIMES: list[str] = [str(i) for i in range(24)]
MONTHS: list[str] = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
_COL_NAMES: list[str] = ["Land Use"] + TIMES + ["Month"]

# ---------------------------------------------------------------------------
# Lazy-loaded data cache (populated on first call to parking_demand)
# ---------------------------------------------------------------------------
_data_cache: dict | None = None


def _load_data() -> dict:
    """Load and cache all input DataFrames. Safe to call multiple times."""
    global _data_cache
    if _data_cache is not None:
        return _data_cache

    (
        base_parking_demand,
        customer_employee_split,
        tod_weekday,
        tod_weekend,
        noncaptive_weekday,
        noncaptive_weekend,
        monthly_factors,
    ) = get_inputs()

    _data_cache = {
        "base_parking_demand": base_parking_demand,
        "customer_employee_split": customer_employee_split,
        "tod_weekday": tod_weekday,
        "tod_weekend": tod_weekend,
        "noncaptive_weekday": noncaptive_weekday,
        "noncaptive_weekend": noncaptive_weekend,
        "monthly_factors": monthly_factors,
    }
    return _data_cache


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------
def _compute_parking(
    name: str,
    context: str,
    base_parking_demand: pd.DataFrame,
    customer_employee_split: pd.DataFrame,
    tod: pd.DataFrame,
    noncaptive: pd.DataFrame,
    monthly: pd.DataFrame,
) -> list[list]:
    """
    Calculate hourly parking demand for a single land use across all 12 months.

    Returns a list of 12 rows, each containing 24 hourly demand values plus the
    month name.
    """
    customer_key = name + "Customer"
    employee_key = name + "Employee"

    # Base daily demand
    daily_demand = base_parking_demand.loc[name, context]

    # Customer / employee split ratios
    customer_split = customer_employee_split.loc[name, "Customer" + context]
    employee_split = customer_employee_split.loc[name, "Employee" + context]

    # Time-of-day profiles
    customer_tod = tod.loc[customer_key, :]
    employee_tod = tod.loc[employee_key, :]

    # Non-captive adjustment factors
    customer_noncaptive = noncaptive.loc[customer_key, :]
    employee_noncaptive = noncaptive.loc[employee_key, :]

    # Monthly adjustment factors
    customer_monthly = monthly.loc[customer_key, :]
    employee_monthly = monthly.loc[employee_key, :]

    # Build hourly demand for each month
    parking_demand_yearly: list[list] = []
    for month in MONTHS:
        customer_demand = (
            daily_demand * customer_split * customer_tod
            * customer_noncaptive * customer_monthly[month]
        )
        employee_demand = (
            daily_demand * employee_split * employee_tod
            * employee_noncaptive * employee_monthly[month]
        )
        total_demand = customer_demand + employee_demand
        total_demand = total_demand.fillna(0)

        hourly_values = np.rint(total_demand.values).astype(int).tolist()
        hourly_values.append(month)
        parking_demand_yearly.append(hourly_values)

    return parking_demand_yearly


def _reshape_data(data_dictionary: dict[str, list[list]]) -> pd.DataFrame:
    """
    Reshape the per-land-use yearly demand lists into a single pivot table
    indexed by (Month, Time) with one column per land use plus a Total column.
    """
    data_list: list[list] = []
    for i in range(12):
        for key, value in data_dictionary.items():
            row = [key] + value[i]
            data_list.append(row)

    df = pd.DataFrame(data_list, columns=_COL_NAMES)
    df = df.melt(
        ["Land Use", "Month"],
        value_vars=TIMES,
        var_name="Time",
        value_name="Parking",
    )
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    df["Time"] = pd.Categorical(df["Time"], categories=TIMES, ordered=True)
    df.sort_values(by=["Month", "Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    df = df.pivot_table(
        values="Parking",
        index=["Month", "Time"],
        columns=["Land Use"],
        fill_value=0,
        aggfunc="first",
    )

    df["Total"] = df.sum(axis=1)
    return df


# ---------------------------------------------------------------------------
# Public API (signature unchanged — drop-in replacement)
# ---------------------------------------------------------------------------
def parking_demand(context: str) -> pd.DataFrame:
    """
    Calculate shared parking demand for all land uses.

    Parameters
    ----------
    context : str
        Either ``"Weekday"`` or ``"Weekend"``.

    Returns
    -------
    pd.DataFrame
        Pivot table indexed by (Month, Time) with columns per land use
        and a Total column.
    """
    data = _load_data()

    if context == "Weekday":
        tod = data["tod_weekday"]
        noncaptive = data["noncaptive_weekday"]
    else:
        tod = data["tod_weekend"]
        noncaptive = data["noncaptive_weekend"]

    base = data["base_parking_demand"]
    split = data["customer_employee_split"]
    monthly = data["monthly_factors"]

    parking_demand_dict: dict[str, list[list]] = {}
    for name in base.index:
        parking_demand_dict[name] = _compute_parking(
            name, context, base, split, tod, noncaptive, monthly,
        )

    return _reshape_data(parking_demand_dict)
