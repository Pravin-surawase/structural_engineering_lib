---
name: new-structural-element
description: "Deliver one bounded, evidence-backed vertical slice for a new IS 456 structural element using the repository's current subpackage and layer patterns."
argument-hint: "Element and first supported design case"
---

# New Structural Element

Use this only when the user has approved adding a new element or a clearly new supported design case. A full element is a program of work; begin with one independently verifiable main process.

## Scope Contract

Define before implementation:

- first supported case and its user outcome;
- governing code edition, clauses, assumptions, and exclusions;
- explicit input/output units;
- trusted benchmark and acceptance tolerance;
- required consumers: library only, API, or full UI;
- non-goals for later cases such as biaxial, slender, seismic, optimization, or export behavior.

Do not imply professional approval. Record governing assumptions and benchmark
interpretation for cumulative qualified review before the final stable or
engineering-use approval; a development slice does not need its own separate
qualified sign-off.

## 1. Prove It Is New

```bash
rg -n "<element>" Python/structural_lib Python/tests fastapi_app react_app/src
./run.sh find --api <candidate_function>
```

Use `./run.sh context show is456`, then inspect the nearest existing element
subpackage and targeted callers. Current complex elements use subpackages such
as `codes/is456/beam/`, `column/`, and `footing/`; do not assume a flat
`<element>.py` layout.

## 2. Prepare the Implementation Packet

The packet must contain objective, non-goals, exact initial files, source
evidence, pitfalls, acceptance criteria, narrow commands, and return format.
Identify owner-only decisions and evidence that must be retained for the final
qualified review.

Sequence work by dependency:

1. minimum shared input/result types in `core/`;
2. pure calculation functions in `codes/is456/<element>/`;
3. element orchestration in an existing or new `services/<element>_api.py`;
4. public exports only for the approved API;
5. FastAPI request/response/route only if an API consumer is in scope;
6. React hook/view only if the end-user UI is in scope.

Do not create downstream layers before the calculation contract and benchmark are accepted.

## 3. Implement the Smallest Complete Slice

Use `/function-quality-pipeline` for each new calculation. Reuse neighboring conventions rather than creating new frameworks. Keep conversions explicit and structural math out of Services, FastAPI, and React.

If the task is delegated, use at most the repository's allowed bounded workers. Each worker receives only its exact layer/files and cannot merge, release, close issues, or expand the supported engineering case. The parent integrates and independently verifies every return.

## 4. Verify at Each Boundary

- Calculation: exact benchmark and governing limit.
- Service: public signature and result mapping.
- FastAPI, when in scope: request → service → response.
- React, when in scope: browser input → API → rendered or downloaded result.

Use targeted checks while editing. Then run:

```bash
./scripts/python_runtime.sh scripts/check_architecture_boundaries.py
./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib
./run.sh check --quick
```

Run `./run.sh check` once at stable closeout. Do not run release preflight unless this is also an approved release task.

## Acceptance

The slice is complete only when:

- its stated supported case produces the benchmarked result;
- unsupported cases are not advertised as supported;
- units and assumptions are visible at the public boundary;
- requested consumers complete the same main process end to end;
- targeted and closeout checks are green;
- docs describe only the implemented capability;
- remaining cases are explicitly out of scope or separately tracked.

## Handoff

Return the supported case, source/benchmark, changed files by layer, public
signatures, verification evidence, exclusions, owner decisions, and evidence
deferred to the final qualified review.
