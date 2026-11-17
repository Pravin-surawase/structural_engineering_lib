<a id="readme-top"></a>

<div align="center">

<img src="react_app/public/structlib.svg" alt="StructLib logo" width="72" height="72">

# StructLib

**A Python library for reinforced-concrete design and checking under IS 456:2000.**

Supply geometry, materials, reinforcement and actions to the supported
calculation. StructLib returns structured results for engineering scripts,
notebooks and other tools. The CLI, FastAPI service and visual workbench are
optional ways to use the same library.

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Release](https://img.shields.io/badge/status-normal%20release-2563eb)](https://github.com/Pravin-surawase/structural_engineering_lib/releases/latest)
[![PR Gate](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/fast-checks.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/fast-checks.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e)](LICENSE)

[Quick start](#quick-start) · [Product tour](docs/getting-started/product-tour.md) · [Documentation](docs/README.md) · [API reference](docs/reference/api.md) · [Contributing](CONTRIBUTING.md)

</div>

> [!IMPORTANT]
> Target release classification (publication state is separate):
> **v0.30.1 is a normal software release of the audited supported scope.**
> The 0.30.1 candidate is unpublished. The verified public release is 0.30.0.
> This describes the version format and scope. Publication state and verified
> artifact identities are recorded in the [release ledger](docs/getting-started/releases.md)
> and matching registry/release assets. Support is case-qualified; complete IS 456 coverage
> and professional design approval are not claimed.
> Outputs require independent review by a qualified structural engineer before
> engineering or construction use. Broader library development and the one
> cumulative practicing-engineer review remain in progress. Confirm available
> artifacts on [PyPI](https://pypi.org/project/structural-lib-is456/)
> and [GitHub Releases](https://github.com/Pravin-surawase/structural_engineering_lib/releases/latest);
> the [current-release page](docs/getting-started/release-status.md) links its
> append-only artifact and verification evidence.

## Quick start

### Install the Python package

**0.30.0 is published and verified** on
[PyPI](https://pypi.org/project/structural-lib-is456/0.30.0/) and
[GitHub](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.30.0).
Install the exact public version:

```bash
python3 -m pip install "structural-lib-is456==0.30.0"
```

The package is installed as `structural-lib-is456` and imported as
`structural_lib`.

`0.30.0` uses the final PEP 440 version format; that format alone does not
establish registry availability.
The project's development-maturity classifier remains **Beta**. Pin the exact
version for reproducible work. See the
[release status and policy](docs/getting-started/release-status.md) before
selecting a build.

This example supplies section dimensions in mm, strengths in N/mm², moments
in kN·m and shear in kN. It evaluates one beam strength calculation.

```python
import json

from structural_lib.design.is456 import beam

request = beam.load(
    {
        "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS-1"},
        "section": {
            "span_mm": 5000.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 442.0,
        },
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
        "actions": {"mu_knm": 150.0, "vu_kn": 80.0, "tu_knm": 0.0},
        "calculation_basis": {"d_dash_mm": 58.0, "asv_mm2": 100.0},
        "source_provenance": "analysis-envelope:ULS-1",
    }
)
result = beam.design(request)

print(json.dumps(result.to_dict(), allow_nan=False, indent=2))
```

The result reports a strength **PASS** and requires qualified engineering
review. Serviceability, physical cage detailing and provided reinforcement
are outside this example. Use the
[beam calculation and status recipe](https://github.com/Pravin-surawase/structural_engineering_lib/blob/v0.30.0/docs/cookbook/python/beam-design.md)
to inspect the result and run the failure and input-error controls.

## Use StructLib in your own tools

| Surface | Use |
| --- | --- |
| **Python** | Call typed functions with explicit units and consume structured results. |
| **CLI** | Run repeatable input, design and export jobs. |
| **FastAPI** | Connect applications over REST or streaming routes. |
| **React workbench** | Inspect geometry and reinforcement and review supported batch results. |

See the [API chooser](docs/reference/api-levels.md), [Python examples](Python/examples/README.md)
and [product tour](docs/getting-started/product-tour.md) for the workflow you need.

### Need the shortest beam-to-BBS path?

The canonical facade above is recommended for new integrations. Existing
scripts and first-time evaluations can use the retained compatibility facade
for a compact design, detailing, and bar-bending-schedule journey:

```python
from structural_lib import api

result = api.design_and_detail_beam_is456(
    units="IS456", beam_id="B1", story="GF",
    span_mm=5500, mu_knm=160, vu_kn=85, b_mm=300, D_mm=500, d_mm=444,
)
print(result.summary())
bbs = api.compute_bbs(result)
print(f"BBS weight: {bbs.summary.total_weight_kg:.1f} kg")
```

The example depth is `500 - 40 - 8 - 16/2 = 444 mm`, matching the generated
single-layer 16 mm tension bars. Combined design/detailing rejects mismatched
depths and multiple-layer layouts whose row centroids are not defined. Use
explicit supplied reinforcement when layer positions are needed.

Identity names differ on two retained service functions:
`design_and_detail_beam_is456()` uses `beam_id`, while
`design_beam_is456()` uses `case_id`. Both routes require independent review;
neither result is professional or construction approval.

Parameter names carry their units—`b_mm`, `mu_knm`, `fck_nmm2`—so the API
boundary stays explicit.

Use the [13 family recipes](docs/cookbook/python/family-facades.md) for every
advertised construction journey, including exact enums, evidence fields,
structured errors, and valid `PASS`/`FAIL`/`HOLD` handling.

Optional capabilities:

```bash
pip install "structural-lib-is456[dxf]"        # DXF export
pip install "structural-lib-is456[pdf]"        # PDF export through the Python API
pip install "structural-lib-is456[render]"     # DXF rendering
```

The CLI `report` command exports JSON and HTML. The Python
`api.generate_calculation_report()` function exports HTML, JSON and Markdown.
For PDF, use `structural_lib.services.report.export_pdf(ReportData)` with the
`pdf` extra.

### Run the full workbench

The workbench requires **Node.js 24.x and npm 11.x**, matching the
[repository Node version](.nvmrc) and
[frontend package engines](react_app/package.json). Check
`node --version` and `npm --version` before installing frontend dependencies.

```bash
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e Python/

cd react_app && npm install && cd ..
./run.sh dev
```

Then open:

- React workbench: <http://localhost:5173>
- Interactive API docs: <http://localhost:8000/docs>

Choose **Explore**, load the bundled sample building, and open the Building
Editor. See the [product tour](docs/getting-started/product-tour.md) for the
complete path.

### Run a CLI pipeline

The sample uses the strict CLI v1 input contract: every member supplies its
identity, materials, actions, detailing dimensions, and either effective depth
or a complete derivation basis. A blocked row prevents calculation of the
whole file; diagnostics use stderr and result JSON remains machine-readable.

```bash
python3 -m structural_lib design Python/examples/sample_beam_design.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
python3 -m structural_lib report results.json --format=html -o report/
```

For the bounded one-storey gravity workflow, start from the maintained open-hall
example and review its explicit assumptions before changing it. The generated
request contains no hidden engineering defaults.

```bash
python3 -m structural_lib gravity-v1 example > gravity-request.json
python3 -m structural_lib gravity-v1 gravity-request.json > gravity-result.json
```

The same request is available from Python with
`structural_lib.get_gravity_workflow_example_request_v1()` and through the
Building Gravity review page's **Load maintained example** action.

## Supported scope

The project deliberately states its boundaries instead of hiding them behind a
single “IS 456 compliant” label.

| Element | Supported-case focus | Important boundary |
|---|---|---|
| **Beams** | Rectangular flexure and shear in the primary combined route; bounded torsion, flanged, doubly reinforced, detailing, and serviceability utilities | Torsion is not added automatically to the primary combined route |
| **Columns** | Rectangular/square sections, symmetric two-face interaction, directional slenderness, minimum eccentricity, and bounded detailing checks | Circular/helical utilities do not constitute complete circular-column design |
| **Isolated footings** | Concentric square/rectangular sizing, flexure, one-way shear, punching shear, bearing, and dowel transfer | Eccentric and combined-footing systems are outside the current supported route |
| **Solid slabs** | Simply supported and coefficient-method continuous one-way strips; common oriented two-way beam/wall-supported panels with built-in bounded coefficient lookup/interpolation, strips, corner torsion, detailing, span/depth and ordinary one-way shear checks | Direct deflection, irregular/concentrated-load panels, automatic shear reinforcement, flat slabs and column-supported punching remain outside the supported route |

The auditable scope, source identities, unsafe cases, limitations, and release
evidence are collected in the
[IS 456 evidence crosswalk](docs/verification/is456-library-first-evidence.md).

## Capabilities

- **Design and detailing:** supported beam, column, isolated-footing, and slab utilities
- **Batch processing:** lossless, accounted ETABS/SAFE/STAAD/Generic import into the strict beam project command
- **Visual review:** interactive React Three Fiber building and reinforcement views
- **Engineering outputs:** BBS CSV, DXF drawings, calculation reports, summaries, and BOQ
- **Integration:** declared Python, command-line, HTTP, WebSocket, and SSE surfaces
- **Traceability:** structured issues, explicit units, clause references, source identities, and bounded evidence

## Architecture

```text
React 19 + R3F  ── HTTP / WS / SSE ──▶  FastAPI  ──▶  structural_lib
react_app/                                fastapi_app/     Python/structural_lib/
```

The Python code follows a strict dependency direction:

```text
Core types  →  IS 456 pure math  →  Services  →  UI / I/O
```

| Layer | Location | Responsibility |
|---|---|---|
| Core types | `Python/structural_lib/core/` | Shared types and constants; no IS 456 math |
| IS 456 code | `Python/structural_lib/codes/is456/` | Pure calculations with explicit units and no I/O |
| Services | `Python/structural_lib/services/` | Orchestration, adapters, pipelines, and exports |
| UI / I/O | `react_app/`, `fastapi_app/` | Human and application interfaces |

## Quality and transparency

- CI covers Python 3.11 and 3.12 across Linux, Windows, and macOS.
- Golden vectors, contract checks, unsafe-case tests, artifact verification,
  protected-content gates, and an SBOM support the normal release evidence.
- Public APIs and outputs use explicit engineering units.
- Known exclusions are documented alongside supported cases.
- Passing software checks are evidence of implementation behavior, not a
  substitute for professional verification.

Start with the [verification index](docs/verification/README.md),
[engineering-use checklist](docs/legal/verification-checklist.md), and
[engineering disclaimer](LICENSE_ENGINEERING.md).

## Documentation

| Goal | Start here |
|---|---|
| Evaluate the project visually | [Product tour](docs/getting-started/product-tour.md) |
| Use the Python package | [Python quick start](docs/getting-started/python-quickstart.md) |
| Integrate the platform | [Developer platform guide](docs/developers/platform-guide.md) |
| Look up an API | [Python API reference](docs/reference/api.md) |
| Understand the architecture | [Project overview](docs/architecture/project-overview.md) |
| Verify supported evidence | [Evidence crosswalk](docs/verification/is456-library-first-evidence.md) |
| Find all documentation | [Documentation hub](docs/README.md) |

## Community

Questions, bug reports, feature proposals, and contributions are welcome.

- [Ask a question](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=support.yml)
- [Report a bug](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=bug_report.yml)
- [Request a feature](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=feature_request.yml)
- [Report a vulnerability privately](SECURITY.md)
- [Read the contribution guide](CONTRIBUTING.md)
- [Review the code of conduct](CODE_OF_CONDUCT.md)

If this project supports your research, cite it using [CITATION.cff](CITATION.cff).

## License and engineering use

The software is available under the [MIT License](LICENSE). The additional
[engineering-use notice](LICENSE_ENGINEERING.md) explains the responsibilities
that remain with the qualified engineer and project authority.

Primary references include IS 456:2000, SP:16, and IS 13920:2016. Standards
text is not redistributed by this repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
