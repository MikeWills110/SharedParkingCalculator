Here you go, Mike — a clean, professional, future‑proof “Rebuild Notes” section you can paste directly into your README.It’s written to be durable, explicit, and deterministic — exactly the kind of documentation future‑you will thank present‑you for.

🧱 Rebuild Notes (Environment + Editor + Workflow)

This section documents the exact steps required to fully rebuild the SharedParkingCalculator development environment on any Windows machine.It ensures the project remains reproducible, stable, and easy to restore after OS resets, hardware changes, or environment drift.

🔧 1. Clone the Repository

git clone https://github.com/MikeWills110/SharedParkingCalculator.git
cd SharedParkingCalculator

🐍 2. Create and Activate the Virtual Environment

python -m venv .venv
.\.venv\Scripts\Activate

You should see the prompt change to:

(SharedParkingCalculator)

📦 3. Install All Required Python Packages

All dependencies are pinned in requirements.txt.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

This restores the exact environment used during development.

🧪 4. (Optional) Run Tests

pytest

If .pytest_cache appears and causes issues, it can be safely deleted.

🖥️ 5. Restore VS Code Settings

The project includes a backup of the user‑level VS Code settings:

vscode-settings-backup.json

To restore:

Open VS Code

Press Ctrl + Shift + P

Choose Preferences: Open Settings (JSON)

Replace the contents with the backup file

Save and restart VS Code

This restores:

Python interpreter path

Theme

Editor behavior

Any customizations you’ve added

🧭 6. Select the Correct Python Interpreter in VS Code

VS Code → Ctrl + Shift + P → “Python: Select Interpreter”Choose:

SharedParkingCalculator\.venv\Scripts\python.exe

This ensures linting, debugging, and testing all use the correct environment.

📁 7. Project Structure Overview

SharedParkingCalculator/
│
├── SharedParkingCalculator.py
├── requirements.txt
├── vscode-settings-backup.json
├── README.md
└── (other project files)

🔄 8. How to Freeze the Environment After Changes

Whenever new packages are installed:

python -m pip freeze > requirements.txt

Commit the updated file:

git add requirements.txt
git commit -m "Update dependencies"
git push

🛠️ 9. Clean Rebuild Procedure (Full System Reset)

If Windows is reinstalled or the machine is replaced:

Install Python

Install Git

Clone the repo

Create venv

Install requirements

Restore VS Code settings

Select interpreter

Run the script

This restores the entire development environment in minutes.

🚀 10. Running the Application

With the venv active:

python SharedParkingCalculator.py

