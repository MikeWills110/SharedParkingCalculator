\## Quick start



```bash

\# from repo root

python calculate\_shared\_parking.py --dir .

```



The script will:

\- validate required CSV files exist under `Inputs/`

\- print an "Inputs snapshot" (filename, modified timestamp, size)

\- write results to:

&nbsp; - `Outputs/WeekdayParking.xlsx`

&nbsp; - `Outputs/WeekendParking.xlsx`

For the overall workflow (editing inputs, running the model, committing changes), see `../README.md`.
For detailed model setup/background, see `../Model_SETUP.md`.

> Note: `Outputs/` is intentionally ignored by Git (generated artifacts).



\## Recommended workflow (when the project gets refined)



1\) Update one or more CSVs in `Inputs/` (see `Inputs/README.md` for what each file controls).

2\) Run the calculator:

&nbsp;  ```bash

&nbsp;  python calculate\_shared\_parking.py --dir .

&nbsp;  ```

3\) Confirm outputs look correct (open the Excel files in `Outputs/`).

4\) Review your changes:

&nbsp;  ```bash

&nbsp;  git diff

&nbsp;  ```

5\) Commit the updated inputs (and/or code) with a clear message:

&nbsp;  ```bash

&nbsp;  git add Inputs/\*.csv

&nbsp;  git commit -m "Update inputs for <scenario/date/assumption>"

&nbsp;  git push origin master

&nbsp;  ```



\## Notes / conventions



\- \*\*Inputs are source-of-truth\*\*: CSVs in `Inputs/` are version-controlled so changes are traceable over time.

\- \*\*Generated outputs are not version-controlled\*\*: Excel files in `Outputs/` are reproducible artifacts.

\- If results differ unexpectedly, compare the "Inputs snapshot" printed by the script between runs to confirm the same input set was used.

