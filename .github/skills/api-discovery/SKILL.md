---
name: api-discovery
description: "Discover exact live public API signatures, types, defaults, units, modules, and return contracts before calling or wrapping structural_lib functions."
argument-hint: "Function name to look up, e.g. 'design_beam_is456' or '--all' to list everything"
---

# API Discovery

The discovery script inspects the installed workspace package through the public compatibility facade. Its output is authoritative for current names and signatures; this skill deliberately does not copy them.

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
.venv/bin/python scripts/discover_api_signatures.py --all
```

The count is derived at runtime. Do not copy it into instructions or documentation.

## Filter by Keyword

```bash
.venv/bin/python scripts/discover_api_signatures.py --filter beam
.venv/bin/python scripts/discover_api_signatures.py --filter rebar
.venv/bin/python scripts/discover_api_signatures.py --filter detailing
```

## JSON Output (for programmatic use)

```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456 --json
.venv/bin/python scripts/discover_api_signatures.py --all --json
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
