---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: beginner
tags: [installation, react, fastapi, python]
---

# Installation Notes

## Evaluate the exact public Alpha

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456===0.24.0a1"
python3 -m structural_lib install-preflight
```

The exact pin resolves the immutable public Alpha prerelease. Later `main`
source, including B0/F0/R0 work, is not that published artifact.

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
python3 -m pip install "structural-lib-is456[dxf]===0.24.0a1"
python3 -m pip install "structural-lib-is456[report,pdf]===0.24.0a1"
python3 -m pip install "structural-lib-is456[render]===0.24.0a1"
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

Windows Excel and ETABS require their separately bound evidence lanes. This
guide does not claim Windows application acceptance, professional approval,
engineering-use approval, release authorization, or publication of current
`main`.
