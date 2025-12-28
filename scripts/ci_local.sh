#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ -d "${REPO_ROOT}/.venv" ]]; then
    # shellcheck source=/dev/null
    source "${REPO_ROOT}/.venv/bin/activate"
  else
    echo "No virtualenv detected. Creating .venv for isolation." >&2
    cd "${REPO_ROOT}"
    python3 -m venv .venv
    # shellcheck source=/dev/null
    source "${REPO_ROOT}/.venv/bin/activate"
  fi
fi

cd "${REPO_ROOT}/Python"

python3 -m pip install -e ".[dev,dxf]"

python3 -m black --check .
python3 -m ruff check .
python3 -m mypy

python3 -m pytest --cov=structural_lib --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=85

cd "${REPO_ROOT}"
python3 scripts/check_doc_versions.py --ci

cd "${REPO_ROOT}/Python"
python3 -m pip install build
python3 -m build
LATEST_WHL=$(ls -t dist/*.whl | head -1)
python3 -m pip install --force-reinstall "${LATEST_WHL}"
python3 -c "import structural_lib; import structural_lib.api"

echo "OK: local CI checks passed"
