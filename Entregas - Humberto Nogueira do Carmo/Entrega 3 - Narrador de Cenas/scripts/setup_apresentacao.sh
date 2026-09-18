#!/usr/bin/env bash
# Setup rápido para apresentação no Cursor (Linux/macOS)
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"

echo
echo "OK. No Cursor: abra Narrador_de_Cenas.ipynb e escolha o kernel Python (Narrador)."
echo "Demo web: streamlit run app/streamlit_app.py"
