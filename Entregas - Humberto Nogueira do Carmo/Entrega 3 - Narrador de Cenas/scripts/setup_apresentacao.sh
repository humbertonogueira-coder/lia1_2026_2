#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"
echo "OK — kernel Python (Narrador) pronto."
