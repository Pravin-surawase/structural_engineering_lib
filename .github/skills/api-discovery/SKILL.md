---
name: api-discovery
description: "Discover exact structural_lib or ETABS API signatures, defaults, return contracts and workflow owners before calling unfamiliar functions or building integrations."
---

# API Discovery

Choose the API first. Python discovery inspects the workspace package; ETABS discovery reads a portable, version-bound assembly/help catalogue. Neither requires copying the full inventory into agent context.

## ETABS: Task → Method → Existing Implementation

```bash
./run.sh etabs-api search "beam forces"
./run.sh etabs-api workflow forces
./run.sh etabs-api show cAnalysisResults.FrameForce
./run.sh etabs-api interface cSapModel
./run.sh etabs-api enum eItemTypeElm
./run.sh etabs-api coverage --filter Load
```

1. Search the task, then read its workflow and maintained source owners. Reuse the existing adapter and smallest acquisition scope.
2. Inspect each exact method's object path, return type, parameter names/directions/defaults, enums and effect. Missing methods and unknown effects remain explicit; a `Get` prefix is not a permission decision.
3. Before using an installation, run `./run.sh etabs-api check --assembly <ETABSv1.dll> --chm <matching-help.chm>`. A repository-only check does not verify installed identity.
4. For units, constraints, return meaning and examples, follow the pinned topic or use `./run.sh etabs-api help <interface.method> --root <extracted-help> --section parameters`. Use `returns` or paginated `all` when needed. Metadata cannot supply undocumented semantics.
5. Verify new usage through the scoped existing adapter/tests and required installed evidence. A registered signature match is not live qualification. Discovery does not authorize mutation or method invocation.

`coverage` enumerates all interfaces, including those without a recipe; filter by interface, object path or recipe and page with `--offset`/`--limit`. Global totals remain independent of the page. Workflow `verification` links focused tests, retained evidence and qualification limits; inspect those limits before reusing a receipt. `check` detects broken references, not every semantic change in an adapter.

Use the [completion plan and setup map](../../../docs/guides/etabs-api-integration.md#completion-plan-and-current-knowledge-boundary) for project setup, next work and known rework controls. Update the active plan's state, evidence and next action after each completed step or outcome-changing blocker. Preserve the repository's candidate freeze: later verdicts belong in the delivery ledger until a repair/replan or next task.

`summary` reports complete surface/coverage and source hashes; `workflows` lists recipes. See the [ETABS integration guide](../../../docs/guides/etabs-api-integration.md) for source authority, refresh and use boundaries. Never paste the entire catalogue or vendor manual into every task.

## Python Public API

## When to Use

- Before calling an unfamiliar public function
- Before wrapping an API function in FastAPI or React
- When creating new endpoints or forms
- When unsure about parameter names or types
- NEVER guess parameter names — always verify

## Look Up a Specific Function

```bash
./run.sh find --api design_beam_is456
```

Output includes:
- Full function signature with all parameters
- Parameter types and defaults
- Return type
- Docstring summary

## List All Public API Functions

```bash
./scripts/python_runtime.sh scripts/discover_api_signatures.py --all
```

The count is derived at runtime. Do not copy it into instructions or documentation.

## Filter by Keyword

```bash
./scripts/python_runtime.sh scripts/discover_api_signatures.py --filter beam
./scripts/python_runtime.sh scripts/discover_api_signatures.py --filter rebar
./scripts/python_runtime.sh scripts/discover_api_signatures.py --filter detailing
```

## JSON Output (for programmatic use)

```bash
./scripts/python_runtime.sh scripts/discover_api_signatures.py design_beam_is456 --json
./scripts/python_runtime.sh scripts/discover_api_signatures.py --all --json
```

## Required Use Pattern

1. Run discovery for the exact callable.
2. Copy parameter spelling, case, units, required/default status, and return contract from that output.
3. Inspect the implementation or public type only when the returned attributes are insufficient.
4. After wiring a wrapper, exercise the scoped main-process call with the narrow existing check.

If discovery says the function is missing, stop. Find the current public equivalent; do not guess or silently call an internal replacement.

## Important Warnings

- **Stub file:** `Python/structural_lib/api.py` is a backward-compat stub. Real code is in `services/api.py`.
- **Units are explicit:** preserve suffixes and conversions shown by the live signature.
- **Adapters moved:** `adapters.py` → `services/adapters.py`
- **Geometry moved:** `geometry_3d.py` → `visualization/geometry_3d.py`

## Quick Grep (alternative)

If the script itself fails, locate the definition and inspect it directly:
```bash
rg -n "^def <function_name>\(" Python/structural_lib/services Python/structural_lib/codes
```

Report the discovery-script failure so the control plane can be repaired; do not make the fallback a second source of truth.
