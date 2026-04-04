<a id="readme-top"></a>

<div align="center">

# IS 456 RC Design Library

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Downloads](https://img.shields.io/pypi/dm/structural-lib-is456)](https://pypi.org/project/structural-lib-is456/)
[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![Fast PR Checks](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/fast-checks.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/fast-checks.yml)
[![CodeQL](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/codeql.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/codeql.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Pravin-surawase/structural_engineering_lib/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Pravin-surawase/structural_engineering_lib)

**Open-source reinforced concrete design toolkit for IS 456:2000.**
Use it as a Python package, a CLI, a FastAPI backend, or a React app.

[Documentation](docs/README.md) · [PyPI Package](https://pypi.org/project/structural-lib-is456/) · [Report Bug](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new) · [Request Feature](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new)

</div>

---

<details>
<summary>Table of Contents</summary>

- [Features](#features)
- [Quick Start: Python Package](#quick-start-python-package)
- [Quick Start: Run From Source](#quick-start-run-from-source)
- [Architecture](#architecture)
- [Built With](#built-with)
- [API Surface](#api-surface)
- [Repository Layout](#repository-layout)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Engineering Disclaimer](#engineering-disclaimer)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

</details>

---

## Features

- 🏗️ **Beam Design** — Design and check RC beams to IS 456:2000 (flexure, shear, torsion)
- 🏛️ **Column Design** — Classification, effective length (Table 28), axial capacity (Cl 39.3), uniaxial bending (Cl 39.5), P-M interaction curves, biaxial check (Cl 39.6), slender columns (Cl 39.7), helical reinforcement (Cl 39.4), detailing (Cl 26.5.3), IS 13920 Cl 7 ductile detailing
- 🧱 **Footing Design** — Bearing pressure sizing (Cl 34.1), flexure (Cl 34.2.3), one-way shear (Cl 34.2.4), punching shear (Cl 31.6.1)
- 📋 **Bar Bending Schedules** — Auto-generate BBS from design results
- 📐 **DXF Export** — CAD-ready reinforcement drawings
- 📊 **Batch Processing** — Design hundreds of beams from CSV/JSON inputs
- 🌐 **REST & WebSocket API** — 59 endpoints via FastAPI
- 🎨 **3D Visualization** — Interactive rebar geometry in React Three Fiber
- 📑 **HTML & PDF Reports** — Comprehensive design reports
- ⚡ **CLI Pipeline** — From input to design → detail → BBS → DXF in one flow

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Project Stats

| Metric | Value |
|--------|-------|
| **Python tests** | 4,200+ tests across Ubuntu, Windows, macOS |
| **Test matrix** | Python 3.11, 3.12 × Linux, Windows, macOS |
| **API functions** | 37 public functions in `structural_lib.api` |
| **REST endpoints** | 59 endpoints across 13 routers + WebSocket |
| **React hooks** | 12 hook files (20+ exported functions) for CSV, geometry, export, live design |
| **IS 456 clauses** | Flexure (Cl 38), shear (Cl 40), torsion (Cl 41), detailing (Cl 26), serviceability (Cl 43), columns (Cl 39), footings (Cl 34) + IS 13920 ductile detailing |
| **AI agents** | 16 VS Code Copilot agents with 10 skills |
| **CSV column mappings** | 40+ column names auto-detected |
| **Export formats** | BBS CSV, DXF drawings, HTML/PDF reports |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Quick Start: Python Package

### Install from PyPI

```bash
pip install structural-lib-is456
```

<details>
<summary>Optional extras</summary>

```bash
pip install "structural-lib-is456[dxf]"       # DXF drawing export
pip install "structural-lib-is456[report]"     # HTML/PDF report generation
pip install "structural-lib-is456[validation]" # Input validation
pip install "structural-lib-is456[render]"     # DXF render to image
```

> **💡 Package Naming:** Install with `pip install structural-lib-is456`, but import as `structural_lib` in Python code. CLI: `python3 -m structural_lib`.

</details>

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

Column and footing design are also available:

```python
result = api.design_column_is456(b_mm=300, D_mm=450, fck=25, fy=415, pu_kn=1200, mux_knm=60)
```

The API uses explicit engineering parameter names: `b_mm`, `D_mm`, `mu_knm`, `fck_nmm2`.

### CLI Pipeline

```bash
python3 -m structural_lib design Python/examples/sample_beam_design.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
python3 -m structural_lib report results.json --format=html -o report/
```

More examples in [Python/examples/README.md](Python/examples/README.md) and [docs/getting-started/python-quickstart.md](docs/getting-started/python-quickstart.md).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Quick Start: Run From Source

### Clone & Setup

```bash
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib

python3.11 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e Python/
```

### Start Backend

```bash
.venv/bin/uvicorn fastapi_app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Start Frontend

```bash
cd react_app && npm install && npm run dev
```

- React dev server: http://localhost:5173

Routes include `/design`, `/import`, `/editor`, `/dashboard`, and `/batch`. The editor is the primary workstation — click any beam for full 3D reinforcement, cross-section, and IS 456 code checks.

### Docker

```bash
docker compose up --build    # FastAPI on port 8000
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

```
React 19 + R3F ──HTTP/WS──▶ FastAPI ──Python──▶ structural_lib
(react_app/)               (fastapi_app/)       (Python/structural_lib/)
```

The Python code follows a strict 4-layer architecture:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Core types** | `Python/structural_lib/core/` | Base classes, types, constants — no IS 456 math |
| **IS 456 Code** | `Python/structural_lib/codes/is456/` | Pure math, NO I/O, explicit units (mm, N/mm², kN, kNm) |
| **Services** | `Python/structural_lib/services/` | Orchestration: `api.py`, `adapters.py`, `beam_pipeline.py` |
| **UI / IO** | `react_app/`, `fastapi_app/` | Interfaces — React frontend and FastAPI backend |

Units are explicit at the API boundary: `mm`, `kN`, `kN·m`, and `N/mm²`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Built With

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-000000?logo=threedotjs&logoColor=white)](https://docs.pmnd.rs/react-three-fiber)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

## API Surface

The Python library exposes 37 public functions through `structural_lib.api`. The FastAPI backend provides 59 REST/WebSocket/SSE endpoints across 13 routers.

- [Python API Reference](docs/reference/api.md)
- [FastAPI Swagger UI](http://localhost:8000/docs) (when running locally)
- [Full endpoint list](docs/getting-started/agent-bootstrap.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

## Documentation

- [docs/README.md](docs/README.md) — top-level documentation index
- [docs/getting-started/python-quickstart.md](docs/getting-started/python-quickstart.md) — Python install and usage
- [docs/reference/api.md](docs/reference/api.md) — public API reference
- [docs/getting-started/agent-bootstrap.md](docs/getting-started/agent-bootstrap.md) — canonical bootstrap for coding agents
- [docs/TASKS.md](docs/TASKS.md) — current task board
- [llms.txt](llms.txt) — compact repo summary for language models
- [CHANGELOG.md](CHANGELOG.md) — release history
- [CITATION.cff](CITATION.cff) — cite this project

## Roadmap

- [x] Beam flexure, shear, and torsion design (IS 456 Cl 38, 40, 41)
- [x] Column classification and short-column axial capacity (IS 456 Cl 39.3)
- [x] Column biaxial bending and P-M interaction (IS 456 Cl 39.5–39.6)
- [x] Column slender/long column design, helical reinforcement, detailing (IS 456 Cl 39.7, 39.4, 26.5.3)
- [x] IS 13920 ductile detailing — beam (Cl 6) and column (Cl 7)
- [x] Footing design — bearing, flexure, one-way shear, punching shear (IS 456 Cl 31.6, 34)
- [x] PDF export, load calculator, project BOQ
- [ ] Slab design module

See [docs/TASKS.md](docs/TASKS.md) for the full task board.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Engineering Disclaimer

This software is a design aid for qualified engineers. It does not replace professional judgment, independent verification, or project-specific code compliance review.

Before using output for construction:

- review the design independently
- confirm local code amendments and authority requirements
- verify critical cases with hand calculations or trusted reference software

See [LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md) and [docs/legal/verification-checklist.md](docs/legal/verification-checklist.md).

## Contributing

Contributions are welcome! This repo has strong automation around validation, task handoff, and git workflow.

```bash
./run.sh session start               # Begin work
./run.sh check --quick               # Fast validation
./run.sh test                        # Run test suite
./run.sh commit "type: description"  # Safe commit + push
```

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/contributing/development-guide.md](docs/contributing/development-guide.md)
- [docs/contributing/testing-strategy.md](docs/contributing/testing-strategy.md)

[![Contributors](https://contrib.rocks/image?repo=Pravin-surawase/structural_engineering_lib)](https://github.com/Pravin-surawase/structural_engineering_lib/graphs/contributors)

## License

MIT for the software. See [LICENSE](LICENSE) and [LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md).

## References

- IS 456:2000, Plain and Reinforced Concrete — Code of Practice
- SP:16, Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016, Ductile Design and Detailing of RC Structures (Cl 6 beams, Cl 7 columns)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
