---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: beginner
tags: [installation, react, fastapi, python]
---

# Installation Notes

## Install the current public release

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456===0.24.0"
python3 -m structural_lib install-preflight
```

The exact pin resolves the immutable `v0.24.0` normal release. The preflight
prints the interpreter, installed version, package origin, and optional extras
so an editable checkout cannot be mistaken for the published wheel.

## Run the current repository workbench

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e Python/
cd react_app && npm install && cd ..
./run.sh dev
```

Open the React workbench at <http://localhost:5173> and FastAPI documentation at
<http://localhost:8000/docs>. Stop the services with:

```bash
./run.sh dev --kill-only
```

Streamlit is retired and is not an installation or runtime surface. Do not
restore or follow `streamlit_app` commands from historical release records.

## Optional package capabilities

```bash
python3 -m pip install "structural-lib-is456[dxf]===0.24.0"
python3 -m pip install "structural-lib-is456[report,pdf]===0.24.0"
python3 -m pip install "structural-lib-is456[render]===0.24.0"
```

Optional extras should be selected only for their stated purpose. An installed
extra does not broaden the supported engineering cases.

## Diagnostics

```bash
python3 -m structural_lib install-preflight
./scripts/python_runtime.sh --diagnose
./run.sh frontend runtime
```

Use the first command for an installed wheel. The repository-bound commands
apply only in a source checkout.

## Boundaries

Windows Excel and ETABS require their separately bound evidence lanes. The
published package remains a design aid: installation is not professional,
engineering-use, construction-use, or Windows application approval.
