#!/bin/bash
set -euo pipefail

# Quick pre-commit preparation: format (black/isort) then lint (flake8)
# Usage: ./scripts/prepare_commit.sh

echo "[INFO] Running code formatters (black, isort)"
if command -v black >/dev/null 2>&1; then
  black .
else
  echo "[WARN] black not installed; skipping formatting. Install with: pip install black"
fi

if command -v isort >/dev/null 2>&1; then
  isort .
else
  echo "[WARN] isort not installed; skipping import sorting. Install with: pip install isort"
fi

echo "[INFO] Running flake8 (will fail the commit if issues found)"
if command -v flake8 >/dev/null 2>&1; then
  flake8 app/ --max-line-length=100 --exclude=migrations
else
  echo "[WARN] flake8 not installed; skipping lint. Install with: pip install flake8"
fi

echo "[OK] prepare_commit completed"
