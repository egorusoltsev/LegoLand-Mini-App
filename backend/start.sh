#!/bin/bash
set -euo pipefail

if [ -d /app ]; then
  cd /app
else
  cd "$(dirname "$0")"
fi

alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
