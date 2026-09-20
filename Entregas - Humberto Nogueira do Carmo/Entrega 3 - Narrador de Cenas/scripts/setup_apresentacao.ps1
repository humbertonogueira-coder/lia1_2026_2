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
Write-Host "OK. Ambiente pronto."
Write-Host "1) Coloque o ONNX do Colab em: models\narrador_cenas.onnx"
Write-Host "2) Rode: streamlit run app/streamlit_app.py"
Write-Host "Guia: CURSOR_POS_COLAB.md"
