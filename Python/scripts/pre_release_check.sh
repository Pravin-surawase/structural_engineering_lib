#!/usr/bin/env bash
set -euo pipefail

# Run from anywhere; anchor to the repo's Python package directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PYTHON_DIR}"

python -m black --check .
python -m ruff check .
python -m mypy
python -m pytest
python -m build

# Smoke-test the built wheel in the current environment.
python -m pip install --force-reinstall dist/*.whl
python -c "import structural_lib; import structural_lib.api"

echo "OK: pre-release checks passed"