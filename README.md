# Shared Parking Calculator

A Python tool that estimates hourly parking demand for mixed-use developments using the **ULI (Urban Land Institute) Shared Parking** methodology. It accounts for customer/employee splits, time-of-day profiles, non-captive adjustments, and monthly seasonal variation to produce realistic hourly demand estimates across all 12 months.

## How It Works

The ULI shared parking model recognises that different land uses (retail, office, restaurant, etc.) peak at different times of day and year. By analysing each land use separately and summing the results, the calculator determines the **actual peak parking needed** — which is typically lower than the sum of individual peaks.

For each land use, the hourly parking demand is calculated as:

```
Demand(hour) = Base Demand
             × Customer/Employee Split
             × Time-of-Day Factor(hour)
             × Non-Captive Adjustment(hour)
             × Monthly Factor(month)
```

Customer and employee components are computed separately and summed, since they follow different arrival/departure patterns.

## Project Structure

```
SharedParkingCalculator/
├── calculate_shared_parking.py   # Main entry point
├── LandUse.py                    # Core parking demand calculations
├── get_inputs.py                 # CSV loading and argument parsing
├── Inputs/                       # Input CSV files (see below)
│   ├── BaseParkingDemand.csv
│   ├── CustomerEmployeeSplit.csv
│   ├── LandUseProgram.csv
│   ├── MonthlyAdjustment.csv
│   ├── NoncaptiveAdjustmentWeekday.csv
│   ├── NoncaptiveAdjustmentWeekend.csv
│   ├── TimeOfDayWeekday.csv
│   └── TimeOfDayWeekend.csv
├── Outputs/                      # Generated Excel workbooks
│   ├── WeekdayParking.xlsx
│   └── WeekendParking.xlsx
└── requirements.txt
```

## Setup

**Prerequisites:** Python 3.10+

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/SharedParkingCalculator.git
   cd SharedParkingCalculator
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv

   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the calculator from the project root:

```bash
python calculate_shared_parking.py --dir .
```

The `--dir` argument specifies the project folder containing the `Inputs/` directory. Use `.` when running from the project root.

**Output:** Two Excel workbooks are saved to the `Outputs/` folder:

| File | Contents |
|------|----------|
| `WeekdayParking.xlsx` | Hourly parking demand for a typical weekday, all 12 months |
| `WeekendParking.xlsx` | Hourly parking demand for a typical weekend day, all 12 months |

Each workbook contains a pivot table indexed by **(Month, Hour)** with one column per land use and a **Total** column showing the combined demand.

## Input Files

All inputs are CSV files stored in the `Inputs/` folder. The first column of each CSV is used as the row index.

| File | Description |
|------|-------------|
| `BaseParkingDemand.csv` | Base daily parking demand per land use, with columns for Weekday and Weekend |
| `CustomerEmployeeSplit.csv` | Proportion of demand from customers vs. employees for each land use |
| `LandUseProgram.csv` | Land use program details for the development |
| `TimeOfDayWeekday.csv` | Hourly demand profiles (0–23) for customers and employees on weekdays |
| `TimeOfDayWeekend.csv` | Hourly demand profiles (0–23) for customers and employees on weekends |
| `NoncaptiveAdjustmentWeekday.csv` | Non-captive reduction factors by hour for weekdays |
| `NoncaptiveAdjustmentWeekend.csv` | Non-captive reduction factors by hour for weekends |
| `MonthlyAdjustment.csv` | Seasonal adjustment factors (January–December) per land use |

### Customising Inputs

To model a different development, edit the CSV files in the `Inputs/` folder:

1. **Add or remove land uses** — Add/remove rows in `BaseParkingDemand.csv` and corresponding rows in all other CSVs. Time-of-day and non-captive CSVs require two rows per land use (one suffixed `Customer`, one suffixed `Employee`).
2. **Adjust demand levels** — Change the base demand values in `BaseParkingDemand.csv`.
3. **Modify seasonal patterns** — Edit `MonthlyAdjustment.csv` to reflect local seasonal variation.

> **Note:** Land use names must match exactly across all CSV files, including capitalisation and apostrophes. The tool normalises common unicode apostrophe variants automatically.

## Credits

- **Programmer:** Joshua Cayanan
- **Date Created:** May 25, 2020
- **Methodology:** Based on the ULI Shared Parking model

## License

This project is not currently licensed. Contact the author before reuse or distribution.
