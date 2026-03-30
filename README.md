# IS 456 RC Beam Design Library

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Open-source reinforced concrete beam design toolkit for IS 456:2000.

Use it as a Python package, a CLI, a FastAPI backend, or a React app.

Current packaged release: `0.20.0`
Current repo focus: `v0.21` React UX overhaul and library expansion

</div>

## What This Repository Contains

This repository is broader than the published Python package. It includes:

- `Python/structural_lib/`: the engineering core and CLI
- `fastapi_app/`: REST, WebSocket, and SSE interfaces for the frontend
- `react_app/`: the primary UI, built with React 19, TypeScript, and React Three Fiber
- `docs/`: user docs, API reference, architecture notes, and agent bootstrap material

The Python code follows a strict 4-layer architecture:

1. Core types in `Python/structural_lib/core/`
2. IS 456 math in `Python/structural_lib/codes/is456/`
3. Orchestration in `Python/structural_lib/services/`
4. UI and I/O in `react_app/` and `fastapi_app/`

Units are explicit at the API boundary: `mm`, `kN`, `kN*m`, and `N/mm^2`.

## What You Can Do With It

- Design and check reinforced concrete beams to IS 456:2000
- Generate detailing outputs, bar bending schedules, and DXF drawings
- Run batch workflows from CSV or JSON inputs
- Import beam data through API adapters and frontend upload flows
- Visualize beams and rebar geometry in React and Streamlit
- Expose the design engine through FastAPI for web applications and automation

Core Python entry points live behind `structural_lib.api` for users and in `Python/structural_lib/services/api.py` for contributors.

## Engineering Disclaimer

This software is a design aid for qualified engineers. It does not replace professional judgment, independent verification, or project-specific code compliance review.

Before using output for construction:

- review the design independently
- confirm local code amendments and authority requirements
- verify critical cases with hand calculations or trusted reference software

See [LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md) and [docs/legal/verification-checklist.md](docs/legal/verification-checklist.md).

## Quick Start: Python Package

### Install from PyPI

```bash
python3 -m pip install --upgrade pip
python3 -m pip install structural-lib-is456
```

Optional extras:

```bash
python3 -m pip install "structural-lib-is456[dxf]"
python3 -m pip install "structural-lib-is456[report]"
python3 -m pip install "structural-lib-is456[validation]"
python3 -m pip install "structural-lib-is456[render]"
```

Package naming:

- install: `structural-lib-is456`
- import: `structural_lib`
- CLI: `python3 -m structural_lib`

### First API Call

```python
from structural_lib import api

result = api.design_and_detail_beam_is456(
    units="IS456",
    beam_id="B1",
    story="GF",
    span_mm=5000,
    mu_knm=150,
    vu_kn=80,
    b_mm=300,
    D_mm=500,
)

print(result.summary())
print(result.is_ok)
```

The high-level API uses explicit engineering parameter names such as `b_mm`, `D_mm`, `mu_knm`, and `fck_nmm2`.

### CLI Pipeline

The unified CLI can take you from input data to design, detailing, schedules, and drawings:

```bash
python3 -m structural_lib design Python/examples/sample_beam_design.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Optional outputs:

```bash
python3 -m structural_lib report results.json --format=html -o report/
python3 -m structural_lib validate results.json
```

Typical artifacts:

- `results.json`: design and compliance output
- `detailing.json`: bar and stirrup detailing
- `schedule.csv`: bar bending schedule
- `drawings.dxf`: CAD-ready reinforcement drawing
- `report/`: HTML report output

More examples live in [Python/examples/README.md](Python/examples/README.md) and [docs/getting-started/python-quickstart.md](docs/getting-started/python-quickstart.md).

## Quick Start: Run The Apps From Source

### 1. Clone and set up Python

```bash
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e Python/
```

For contributor workflows, the repo standard entry point is:

```bash
./run.sh session start
```

### 2. Start FastAPI

```bash
.venv/bin/uvicorn fastapi_app.main:app --reload --port 8000
```

Useful URLs:

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 3. Start React

```bash
cd react_app
npm install
npm run dev
```

React dev server:

- `http://localhost:5173`

Current top-level routes in the React app include `/design`, `/import`, `/editor`, `/dashboard`, and `/batch`. The editor page is the primary workstation — click any beam to see its full 3D reinforcement, cross-section, and IS 456 code checks inline.

### 4. Docker

For a containerized backend:

```bash
docker compose up --build
```

This currently brings up the FastAPI service on port `8000`.

## API And App Surface

### Python library

Representative public functions exposed through `structural_lib.api` include:

- `design_beam_is456`
- `check_beam_is456`
- `detail_beam_is456`
- `design_and_detail_beam_is456`
- `optimize_beam_cost`
- `smart_analyze_design`
- `compute_bbs`
- `compute_dxf`
- `compute_report`

The real implementation lives in `Python/structural_lib/services/api.py`. The top-level `Python/structural_lib/api.py` module exists for backward compatibility.

### FastAPI

The backend groups endpoints by responsibility, including:

- design
- detailing
- analysis
- geometry
- imports
- insights
- optimization
- rebar
- export
- streaming
- websocket
- health

The current routing setup is assembled in `fastapi_app/main.py`, with REST routers mounted under `/api/v1`, the WebSocket endpoint under `/ws/design/{session_id}`, and SSE endpoints under `/stream/...`.

### React

The React app is the primary UI and currently includes:

- single-beam design with dynamic layout (3D expands when no result)
- CSV import flows
- batch design page
- dashboard insights with BentoGrid layout and export buttons
- building editor with inline BeamDetailPanel (click beam → 3D rebar + results + export)
- 3D visualization and annotated cross-section views (utilization color coding)
- export actions for BBS, DXF, and reports
- macOS-style FloatingDock navigation

Reusable frontend integration points are organized in `react_app/src/hooks/`, including hooks for CSV import, beam geometry, live design, exports, insights, and rebar editing.

## Repository Layout

```text
structural_engineering_lib/
├── Python/         # Published Python package and tests
├── fastapi_app/    # REST/WebSocket/SSE backend
├── react_app/      # Primary frontend
├── docs/           # User, developer, and architecture docs
├── scripts/        # Repo automation and validation
└── run.sh          # Unified repo CLI
```

## Documentation Map

Start here, depending on what you need:

- [docs/README.md](docs/README.md): top-level documentation index
- [docs/getting-started/python-quickstart.md](docs/getting-started/python-quickstart.md): Python install and usage
- [docs/reference/api.md](docs/reference/api.md): public API reference
- [docs/getting-started/agent-bootstrap.md](docs/getting-started/agent-bootstrap.md): canonical bootstrap for coding agents
- [docs/TASKS.md](docs/TASKS.md): current task board
- [docs/planning/next-session-brief.md](docs/planning/next-session-brief.md): latest handoff and next priorities
- [llms.txt](llms.txt): compact repo summary for language models

## Contributing And Repo Workflow

This repo has strong automation around validation, task handoff, and git workflow.

Useful commands:

```bash
./run.sh session start
./run.sh check --quick
./run.sh check
./run.sh test
./run.sh find --api design_beam_is456
./run.sh commit "docs: update readme"
```

Important conventions:

- use `.venv/bin/python`, not bare `python`, for repo scripts
- use `./run.sh commit` or `./scripts/ai_commit.sh`, not manual git commit flows
- read folder `index.md` or `index.json` files before diving into large areas
- treat `Python/structural_lib/api.py` as a compatibility layer, not the primary implementation target

Contributor docs:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/contributing/development-guide.md](docs/contributing/development-guide.md)
- [docs/contributing/testing-strategy.md](docs/contributing/testing-strategy.md)

## License

MIT for the software. See [LICENSE](LICENSE) and [LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md).

## References

- IS 456:2000, Plain and Reinforced Concrete - Code of Practice
- SP:16, Design Aids for Reinforced Concrete to IS 456
- IS 13920, ductile detailing requirements used by the detailing layer
