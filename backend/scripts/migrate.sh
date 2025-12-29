#!/usr/bin/env bash
set -euo pipefail

VENV_PATH=".venv"

if [ ! -d "$VENV_PATH" ]; then
  echo "[migrate] venv not found at $VENV_PATH"
  exit 1
fi

echo "[migrate] using venv at $VENV_PATH"
"$VENV_PATH/bin/python" -m alembic upgrade head
