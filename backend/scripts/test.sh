#!/usr/bin/env bash
set -euo pipefail

VENV_PATH=".venv"

if [ -x "$VENV_PATH/bin/python" ]; then
  echo "[test] using venv at $VENV_PATH"
  PYTHON="$VENV_PATH/bin/python"
else
  echo "[test] using system python"
  PYTHON="python"
fi

PYTHONPATH=. $PYTHON -m pytest -q
