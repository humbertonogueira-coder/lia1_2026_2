# Setup rápido para apresentação no Cursor (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"

Write-Host ""
Write-Host "OK. No Cursor: abra Narrador_de_Cenas.ipynb e escolha o kernel Python (Narrador)."
Write-Host "Demo: streamlit run app/streamlit_app.py"
