#!/usr/bin/env bash
# Small helper script to run the backend test workflow locally.
# - creates a venv in ./venv if missing
# - installs requirements
# - runs migrations
# - runs pytest

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/venv"
PY=python3

cd "$ROOT_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv at $VENV_DIR"
  $PY -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools
fi

# activate venv for this script
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing requirements into venv..."
python -m pip install -r requirements.txt

echo "Applying migrations..."
python backend/manage.py migrate --noinput

echo "Running pytest..."
pytest -q
