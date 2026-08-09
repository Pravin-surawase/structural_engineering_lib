---
name: development-rules
description: "Apply the small set of outcome-critical project rules for Python, IS 456, FastAPI, React, documentation, and review without turning them into generic hardening."
---

# Development Rules

Load only the section for the changed domain. Existing project automation and adjacent code are the source of implementation patterns; this file defines the decisions that must remain consistent.

## Universal

1. Trace a confirmed defect to its root cause. Do not suppress the symptom or introduce a fallback that silently changes an engineering result.
2. Search before adding a public function, hook, component, route, adapter, or script.
3. Preserve the dependency direction: Core → IS 456 → Services → UI/IO.
4. Preserve explicit units at every calculation and API boundary.
5. During review, report only confirmed defects whose fix changes the scoped main-process outcome. Ignore comments, coverage gaps, edge-case speculation, generic hardening, and adjacent cleanup. Do not add tests in review-only work.

## Python and IS 456

- Put base types and shared primitives in `core/`, pure code calculations in `codes/is456/`, and orchestration/I/O in `services/`.
- Use the live neighboring module and `./run.sh find --api <name>` before choosing parameter names or result shapes.
- Use lowercase unit suffixes that match the public API, such as `_mm`, `_mm2`, `_kn`, `_knm`, and `_nmm2`.
- Validate a denominator according to the formula's domain. If `safe_divide()` is used, choose its `default` deliberately; never treat an invalid denominator as a valid zero result by accident.
- A changed IS 456 formula needs a clause identifier, dimensional reasoning, and an independent benchmark with a source-specific tolerance. Tests are software evidence, not professional certification.
- Keep imports quiet and public exports importable. Packaging data needed by the main process must be declared in the package configuration.

## FastAPI

- Routers validate transport input, call public/service functions, and serialize results. They do not reimplement structural math.
- Preserve the established request, response, error, and units contract of the route being changed.
- Log diagnostic details server-side; do not return internal exception text, paths, or tracebacks to the client.
- When an endpoint changes, verify the actual request → service → response path, not only model construction.

## React

- Structural calculations come from FastAPI. Client code manages input, state, visualization, and presentation.
- Search existing hooks and components before creating another abstraction.
- Keep request/response types aligned with the live FastAPI contract and preserve explicit units in field names.
- When a user-visible flow changes, verify the browser → API → rendered/downloaded result.

## Tests and Verification

- During implementation, change or add the narrow evidence required by the requested behavior; do not add tests during review-only work.
- Use real structural result types when their behavior is part of the process. Do not use mocks that make impossible states appear valid.
- Run targeted checks while editing, `./run.sh check --quick` once before commit, and `./run.sh check` once at closeout.
- Use release/UAT automation only for release or packaging scope.

## Documentation and State

- Update public docs when the changed public contract makes them false.
- Update task/handoff files only when their state changes or another session needs a durable handoff.
- Do not regenerate global indexes, metrics, release notes, or logs as adjacent maintenance.

## Review Question

For every possible finding, answer: **Would fixing this change the outcome of the main process in scope?** If not, leave it out of the review. Preserve a non-essential concern as a follow-up task only when losing it would materially obstruct later work.
