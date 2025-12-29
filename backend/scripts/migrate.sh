#!/usr/bin/env bash
set -euo pipefail

VENV_PATH=".venv"

if [ -x "$VENV_PATH/bin/python" ]; then
  echo "[migrate] using venv at $VENV_PATH"
  PYTHON="$VENV_PATH/bin/python"
else
  echo "[migrate] using system python"
  PYTHON="python"
fi

$PYTHON -m alembic upgrade head
