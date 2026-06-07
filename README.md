Shared Parking Calculator
A deterministic Python tool for modeling hourly shared‑parking demand for mixed‑use developments using the ULI Shared Parking methodology. The calculator integrates land‑use program data, customer/employee behavior, time‑of‑day profiles, seasonal adjustments, and non‑captive factors to produce realistic hourly parking demand for both weekdays and weekends.

1. Purpose
Traditional parking studies sum the peak demand of each land use independently, which overstates actual need.
The ULI Shared Parking model recognizes that:

Land uses peak at different times

Customer and employee patterns differ

Seasonal variation matters

Not all demand is captive to the site

This tool automates the full ULI workflow and outputs hour‑by‑hour demand for all 12 months, enabling right‑sized parking design.

2. How the Model Works
For each land use and each hour, demand is calculated as:

Code
Hourly Demand =
    Base Demand
  × Customer/Employee Split
  × Time‑of‑Day Factor (hour)
  × Non‑Captive Adjustment (hour)
  × Monthly Adjustment (month)
Customer and employee components are computed separately and then summed.
All land uses are aggregated to produce the total shared‑parking demand.

3. Repository Layout
Code
SharedParkingCalculator/
│
├── calculate_shared_parking.py     # Main execution script
├── LandUse.py                      # Core demand calculations
├── get_inputs.py                   # Input loading and validation
│
├── Inputs/                         # All required CSV inputs
│   ├── BaseParkingDemand.csv
│   ├── CustomerEmployeeSplit.csv
│   ├── LandUseProgram.csv
│   ├── MonthlyAdjustment.csv
│   ├── NoncaptiveAdjustmentWeekday.csv
│   ├── NoncaptiveAdjustmentWeekend.csv
│   ├── TimeOfDayWeekday.csv
│   └── TimeOfDayWeekend.csv
│
├── Outputs/                        # Auto‑generated Excel results
│   ├── WeekdayParking.xlsx
│   └── WeekendParking.xlsx
│
└── requirements.txt
4. Environment Setup (Python 3.14 recommended)
Create and activate a virtual environment
powershell
python -m venv .venv
.\.venv\Scripts\activate
Install dependencies
powershell
pip install -r requirements.txt
If rebuilding manually:

powershell
pip install numpy pandas openpyxl matplotlib
5. Running the Calculator
From the project root:

powershell
python calculate_shared_parking.py --dir .
The --dir argument tells the script where to find the Inputs/ folder.
Using . is correct when running from the repository root.

Outputs
Two Excel workbooks are generated in Outputs/:

File	Description
WeekdayParking.xlsx	Hour‑by‑hour shared parking demand for a typical weekday (all 12 months)
WeekendParking.xlsx	Hour‑by‑hour shared parking demand for a typical weekend day (all 12 months)


Each workbook includes:

Input snapshot (file names, timestamps, sizes)

Metadata block (run time, working directory, environment info)

Hourly demand table with one column per land use and a Total column

6. Input File Specifications
All inputs must be placed in the Inputs/ folder.
The first column of each CSV is treated as the index.

Required Input Files
File	Purpose
BaseParkingDemand.csv	Base daily parking demand per land use (weekday + weekend columns)
CustomerEmployeeSplit.csv	Fraction of demand from customers vs. employees
LandUseProgram.csv	Land‑use quantities for the development
TimeOfDayWeekday.csv	Hourly customer/employee factors for weekdays
TimeOfDayWeekend.csv	Hourly customer/employee factors for weekends
NoncaptiveAdjustmentWeekday.csv	Hourly non‑captive factors for weekdays
NoncaptiveAdjustmentWeekend.csv	Hourly non‑captive factors for weekends
MonthlyAdjustment.csv	Seasonal multipliers for each land use (Jan–Dec)


Naming Rules
Land‑use names must match exactly across all CSVs.

Time‑of‑day and non‑captive files require two rows per land use:

<LandUse> Customer

<LandUse> Employee

Unicode apostrophes are normalized automatically.

7. Customizing the Model
To model a different development:

Modify land‑use quantities  
Edit LandUseProgram.csv.

Add or remove land uses  
Update all CSVs to include matching rows.

Adjust demand patterns

Change base demand

Edit customer/employee splits

Modify time‑of‑day curves

Update seasonal factors

Tune non‑captive behavior  
Adjust hourly reduction factors for weekday/weekend.

8. Reproducibility
This project is designed for deterministic execution:

All inputs are version‑controlled

Outputs are timestamped

The environment is isolated via .venv

No external APIs or nondeterministic sources

To rebuild the environment:

powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
9. Credits
Original Programmer: Joshua Cayanan

Created: May 25, 2020

Methodology: ULI Shared Parking Model

10. License
This project is not currently licensed.
Contact the author before reuse or distribution.