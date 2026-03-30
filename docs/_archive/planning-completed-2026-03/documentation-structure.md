# Professional Documentation Structure

**Type:** Plan
**Audience:** All Agents, Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** LIB-IMPROVEMENT

---

## Overview

This document defines the target documentation structure for the Structural SDK. Professional documentation is critical for adoption and trust.

---

## Documentation Goals

1. **Discoverable** — Engineers find what they need quickly
2. **Progressive** — From quickstart to advanced topics
3. **Accurate** — Auto-generated from code where possible
4. **Tested** — Code examples are validated
5. **Versioned** — Documentation matches library version

---

## Target Structure

```
docs/
├── index.md                         # Landing page
├── changelog.md                     # Version history
├── license.md                       # MIT license
│
├── getting-started/                 # Onboarding path
│   ├── installation.md              # pip install, requirements
│   ├── quickstart.md                # 5-minute beam design
│   ├── concepts.md                  # Key concepts explained
│   └── streamlit-ui.md              # Using the web interface
│
├── tutorials/                       # Step-by-step guides
│   ├── single-beam-design.md        # Complete beam design walkthrough
│   ├── batch-processing.md          # Process 100+ beams
│   ├── cost-optimization.md         # Find optimal designs
│   ├── 3d-visualization.md          # Using the 3D viewer
│   ├── etabs-integration.md         # Import from ETABS
│   ├── custom-reports.md            # Generate professional reports
│   └── multi-code-design.md         # Using ACI 318 / EC2
│
├── api-reference/                   # Auto-generated + manual
│   ├── overview.md                  # API structure overview
│   ├── engine/                      # sk.engine.*
│   │   ├── design_beam.md
│   │   ├── verify_beam.md
│   │   ├── batch_design.md
│   │   ├── optimize_beam.md
│   │   └── analyze_beam.md
│   ├── viz/                         # sk.viz.*
│   │   ├── beam_3d.md
│   │   ├── plot_bmd_sfd.md
│   │   └── compliance_panel.md
│   ├── io/                          # sk.io.*
│   │   ├── read_csv.md
│   │   ├── read_etabs.md
│   │   ├── export_dxf.md
│   │   ├── export_bbs.md
│   │   └── export_report.md
│   ├── codes/                       # sk.codes.*
│   │   ├── is456.md
│   │   ├── aci318.md
│   │   └── ec2.md
│   └── data-types/                  # Input/Output types
│       ├── inputs.md
│       ├── results.md
│       └── geometry.md
│
├── examples/                        # Runnable examples
│   ├── README.md                    # Example index
│   ├── basic_beam.py
│   ├── batch_from_csv.py
│   ├── cost_optimization.py
│   ├── 3d_viewer_demo.py
│   └── notebooks/                   # Jupyter notebooks
│       ├── beam_design_intro.ipynb
│       ├── sensitivity_analysis.ipynb
│       └── multi_code_comparison.ipynb
│
├── technical/                       # For contributors
│   ├── architecture.md              # System design
│   ├── code-structure.md            # Module organization
│   ├── design-patterns.md           # Patterns used
│   ├── error-handling.md            # Error architecture
│   ├── testing-strategy.md          # How we test
│   ├── contributing.md              # Contribution guide
│   └── code-style.md                # Code standards
│
├── planning/                        # Project planning (internal)
│   ├── roadmap.md
│   ├── library-improvement-master-plan.md
│   ├── multi-code-architecture.md
│   ├── automation-platform-vision.md
│   └── brainstorming_platform_pivot.md
│
└── reference/                       # Detailed references
    ├── sdk-api-contract-v1.md       # API contract
    ├── 3d-json-contract.md          # 3D geometry schema
    ├── structjson-schema.md         # Data interchange format
    ├── is456-clauses.md             # IS 456 clause index
    ├── aci318-clauses.md            # ACI 318 clause index
    └── glossary.md                  # Terminology
```

---

## Page Templates

### Getting Started Page

```markdown
# [Topic Name]

Brief introduction (1-2 sentences).

## Prerequisites

- Python 3.10+
- pip install structural-sdk

## Steps

### Step 1: [Action]

Description of what to do.

```python
# Code example
import structural_sdk as sk
```

### Step 2: [Action]

...

## Next Steps

- Link to next topic
- Link to related tutorial
```

### API Reference Page

```markdown
# sk.engine.design_beam

Design a reinforced concrete beam.

## Signature

```python
def design_beam(
    beam: BeamInput,
    include_detailing: bool = True,
    include_3d: bool = False,
) -> DesignResult
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `beam` | `BeamInput` | Required | Beam specification |
| `include_detailing` | `bool` | `True` | Include bar arrangements |
| `include_3d` | `bool` | `False` | Include 3D geometry |

## Returns

`DesignResult` — Complete design results.

## Raises

| Exception | Condition |
|-----------|-----------|
| `ValidationError` | Invalid beam input |
| `DesignError` | Design calculation failed |

## Example

```python
import structural_sdk as sk
from structural_sdk.types import BeamInput, BeamGeometryInput, MaterialsInput, LoadsInput

beam = BeamInput(
    beam_id="B1",
    geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
    materials=MaterialsInput.M25_FE500(),
    loads=LoadsInput(mu_knm=200, vu_kn=100)
)

result = sk.engine.design_beam(beam)

print(f"Status: {'PASS' if result.is_ok else 'FAIL'}")
print(f"Steel required: {result.flexure.ast_required_mm2:.0f} mm²")
```

## See Also

- `verify_beam` — Verify with provided reinforcement
- `batch_design` — Design multiple beams
- `optimize_beam` — Find optimal dimensions

## References

- IS 456:2000 Clause 38 (Flexure)
- IS 456:2000 Clause 40 (Shear)
```

### Tutorial Page

```markdown
# [Tutorial Title]

What you'll learn in this tutorial.

## Overview

Brief explanation of the workflow.

## Prerequisites

- Completed: Previous tutorial (TBD)
- Installed: structural-sdk

## Step 1: [Action]

Explanation.

```python
# Code
```

Output:
```
Expected output
```

## Step 2: [Action]

...

## Complete Code

```python
# Full example
```

## What You Learned

- Point 1
- Point 2

## Next Steps

- Next tutorial (TBD)
- Related API reference (TBD)
```

---

## Documentation Tools

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: Structural SDK
site_description: Professional RC design library
site_author: Pravin Surawase
repo_url: https://github.com/pravin/structural-sdk
repo_name: structural-sdk

theme:
  name: material
  features:
    - navigation.instant
    - navigation.sections
    - navigation.tabs
    - navigation.indexes
    - search.suggest
    - search.highlight
    - content.code.copy
  palette:
    - scheme: default
      primary: indigo
      accent: indigo

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [Python/structural_lib]
          options:
            show_source: true
            show_signature_annotations: true
            members_order: source
  - autorefs

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quickstart: getting-started/quickstart.md
    - Concepts: getting-started/concepts.md
  - Tutorials:
    - Single Beam Design: tutorials/single-beam-design.md
    - Batch Processing: tutorials/batch-processing.md
    - Cost Optimization: tutorials/cost-optimization.md
    - 3D Visualization: tutorials/3d-visualization.md
  - API Reference:
    - Overview: api-reference/overview.md
    - Engine: api-reference/engine/
    - Visualization: api-reference/viz/
    - I/O: api-reference/io/
    - Codes: api-reference/codes/
    - Data Types: api-reference/data-types/
  - Examples: examples/
  - Technical: technical/
  - Changelog: changelog.md

markdown_extensions:
  - admonition
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - tables
```

### Auto-Generation Script

```python
# scripts/generate_api_docs.py
"""Generate API reference documentation from docstrings."""

import ast
from pathlib import Path

def extract_functions(module_path: Path) -> list[dict]:
    """Extract public functions from a Python module."""
    with open(module_path) as f:
        tree = ast.parse(f.read())

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
            functions.append({
                'name': node.name,
                'docstring': ast.get_docstring(node) or '',
                'args': [arg.arg for arg in node.args.args],
            })
    return functions

def generate_api_page(func: dict, output_dir: Path):
    """Generate a markdown page for a function."""
    content = f"""# {func['name']}

{func['docstring']}

## Parameters

| Parameter | Description |
|-----------|-------------|
{format_params(func['args'])}

"""
    output_path = output_dir / f"{func['name']}.md"
    output_path.write_text(content)
```

---

## Quality Checklist

### Per-Page Checklist

- [ ] Title is clear and descriptive
- [ ] Introduction explains purpose
- [ ] Code examples are tested
- [ ] Links work
- [ ] Metadata is correct
- [ ] Spelling checked
- [ ] Technical accuracy verified

### Per-Release Checklist

- [ ] All new APIs documented
- [ ] Changelog updated
- [ ] Version numbers consistent
- [ ] Examples run without error
- [ ] Search index updated
- [ ] Links validated (CI check)

---

## Documentation CI

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'Python/structural_lib/**'
  pull_request:
    paths:
      - 'docs/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings[python]
          pip install -e Python/

      - name: Build docs
        run: mkdocs build --strict

      - name: Check links
        run: |
          pip install linkchecker
          linkchecker site/

      - name: Deploy (main only)
        if: github.ref == 'refs/heads/main'
        run: mkdocs gh-deploy --force
```

---

## Immediate Actions

1. **Create `docs/getting-started/quickstart.md`** — 5-minute intro
2. **Create `docs/tutorials/single-beam-design.md`** — Complete walkthrough
3. **Set up MkDocs** — Install and configure
4. **Add docstrings** — Ensure all public functions have docstrings
5. **Generate API reference** — Auto-generate from code

---

*Professional documentation is a competitive advantage.*
