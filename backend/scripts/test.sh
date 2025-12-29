#!/usr/bin/env bash
set -euo pipefail

VENV=".venv"
if [ -x "$VENV/bin/python" ]; then
  PYTHONPATH=. "$VENV/bin/python" -m pytest -q
else
  PYTHONPATH=. python -m pytest -q
fi
