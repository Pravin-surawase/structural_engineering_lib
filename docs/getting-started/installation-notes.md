---
owner: Main Agent
status: active
last_updated: 2026-11-24
doc_type: guide
complexity: beginner
tags: [installation, react, fastapi, python]
---

# Installation Notes

## Install the current public release

The pin follows the [verified public version](release-status.md).
For a development checkout, use the [source-install route](#run-the-current-repository-workbench).

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456==0.31.1"
python3 -m structural_lib install-preflight
```

Check that preflight reports the intended interpreter and package version.
For a wheel install, the package origin should be in that environment's
`site-packages`. Add `--json` to inspect the execution mode and the
boolean `optional_extras` values.

Exit code `0` means preflight produced a report, even when optional
dependencies are missing. Each extra reports whether every required Python
module is discoverable. Run the intended export to verify it works with the
installed versions and native libraries.
[Runtime and optional dependencies](../reference/third-party-licenses.md#runtime-dependencies)

The reported repair command uses the same interpreter and the reported
package version. Run it in a POSIX shell on macOS or Linux, or in PowerShell
on Windows.

## Run the current repository workbench

The workbench requires **Node.js 24.x and npm 11.x**, matching the
[repository Node version](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/.nvmrc) and
[frontend package engines](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/react_app/package.json). Check
`node --version` and `npm --version` before installing frontend dependencies.

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
python3 -m pip install "structural-lib-is456[dxf]==0.31.1"
python3 -m pip install "structural-lib-is456[report,pdf]==0.31.1"
python3 -m pip install "structural-lib-is456[render]==0.31.1"
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
