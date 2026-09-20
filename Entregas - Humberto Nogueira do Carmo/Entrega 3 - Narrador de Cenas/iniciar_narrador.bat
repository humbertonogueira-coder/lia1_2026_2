@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo Ambiente .venv nao encontrado.
  echo Crie com: python -m venv .venv
  echo Depois:   .venv\Scripts\activate.bat ^&^& pip install -r requirements.txt
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python Narrar.py
pause
