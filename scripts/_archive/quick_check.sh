#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

if [[ "${1-}" == "docs" ]]; then
  "$PYTHON_BIN" "$ROOT_DIR/scripts/check_doc_versions.py"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/check_links.py"
  exit 0
fi

if [[ "${1-}" == "--cov" ]]; then
  cd "$ROOT_DIR/Python"
  "$PYTHON_BIN" -m pytest --cov=structural_lib --cov-branch --cov-fail-under=85 -q
  exit 0
fi

cd "$ROOT_DIR/Python"
"$PYTHON_BIN" -m pytest -q
