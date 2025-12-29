#!/usr/bin/env bash
set -euo pipefail

APP_MODULE="${APP_MODULE:-app.main:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "[dev] starting uvicorn ${APP_MODULE} on ${HOST}:${PORT}"
exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"
