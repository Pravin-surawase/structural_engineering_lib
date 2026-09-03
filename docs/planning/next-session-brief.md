# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-03
- Focus: Define and document PF0–PF11 for the reusable Python/.NET libraries and their Excel/ETABS boundaries before further product implementation.
- Git receipt: docs/verification/library-definition-programme-git-handoff-receipt.json | sha256:9c0811a4aa8e2c0988dc52b85cb4149980d4b3e03140582061af940a228475ad | HOLD
- Git identity: codex/library-definition-programme@3e7c8ee7c2d6cae8babc60e6bb1c315b0e6b3d09 | upstream=NONE@UNKNOWN | base=origin/main@3e7c8ee7c2d6cae8babc60e6bb1c315b0e6b3d09 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

[Structural Library Definition Programme PF0–PF11](xll-product/library-definition/README.md)
is the current work authority. It defines the reusable Python/.NET libraries and
their Excel/ETABS boundaries before further implementation. The existing Python
package, C# foundation, automation catalogue and historical projects are inputs
to the programme; none can silently become the normative public API.

| State | Next action / claim boundary |
|---|---|
| **Current** | The 12-phase programme, 58 deliverables, 23 decisions, 17 capability families and AO01–AO26 traceability are defined and validated. No PF phase has yet been executed. |
| **Next** | Complete PF0's charter, owner map, success measures and glossary; review its exit evidence before PF1/PF2 discovery closes. |
| Definition boundary | Requirements, semantics, signatures, assurance, application contracts, packaging, migration and implementation ordering are decided through PF0–PF11. |
| Application boundary | Excel and ETABS remain adapters. Worksheet calculations consume immutable validated data; live COM and mutations are explicit application commands. |
| Implementation boundary | Further product implementation begins only from the integrated PF11 blueprint. Existing code remains usable evidence during definition. |
| Release boundary | Package publication and GitHub releases retain the repository's separate per-release authorization and evidence process. |

## Next decision order

1. PF0: settle purpose, users, owners and measurable success.
2. PF1 and PF2: document real workflows while auditing existing assets and
   failure-prevention evidence.
3. PF3–PF5: settle capability boundaries, engineering semantics and public
   operations before choosing language signatures.
4. PF6–PF8: settle Python/.NET parity, assurance and Excel/ETABS contracts.
5. PF9–PF11: settle packaging/performance, migration/documentation and the
   ordered implementation blueprint.

## Required Reading

1. [Structural Library Definition Programme](xll-product/library-definition/README.md)
2. [Machine-readable programme](xll-product/library-definition/programme.json)
3. [Decision register](xll-product/library-definition/decision-register.json)
4. [Current XLL plan](xll-product/current-plan.md)
5. [Automation requirements](xll-product/automation/README.md)
6. [Reusable Python/.NET library research](xll-product/reusable-library-research.md)
7. [Newest session entry](../SESSION_LOG.md)
8. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
