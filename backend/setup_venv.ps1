# PowerShell Script to setup Python 3.12 Virtual Environment

$PythonVersion = "3.12"
Write-Host "Setting up Virtual Environment for CreatorOS AI Backend using Python $PythonVersion..."

# Create venv
python -m venv venv

# Activate and install dependencies
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Virtual Environment setup complete! Run '.\venv\Scripts\Activate.ps1' to activate." -ForegroundColor Green
