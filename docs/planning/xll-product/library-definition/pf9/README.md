---
owner: Main Agent
last_updated: 2026-09-04
doc_type: spec
phase_id: PF9
---

# PF9 — packaging, deployment and performance

PF9 is complete. [baseline.json](baseline.json) fixes the supported runtime and
host targets, package/dependency boundaries, deployment diagnostics, six
performance budgets, benchmark method and release evidence. The official-source
basis is retained in [research-source.md](research-source.md).

## D19 and D20 decisions

The compatibility target is CPython 3.11–3.14. Python 3.14 becomes a package
claim only after its release matrix passes. New .NET libraries and the Windows
adapter use .NET 10 LTS. The primary XLL target is Windows 11 x64, 64-bit
Microsoft 365 Excel, Excel-DNA 1.9.0 and current .NET 10 Desktop Runtime x64.
Office LTSC 2024 x64 is secondary after separate installed acceptance.

ETABS live support begins with the exact installed ETABS 23.3.1.4563 and
API 2.16.0.0 tuple. Other versions can produce/consume the portable snapshot
only after schema conformance; live support requires their own method-signature
and installed E5 packet. The target matrix does not claim that the final XLL or
coupled workflow has already passed.

Pure Python wheels and .NET NuGet packages load without Excel-DNA, CSI, COM,
FastAPI or UI dependencies. Windows adapters are separate artifacts. Candidate
builds lock dependencies, carry schema/data/build versions, SBOM/licenses and
preflight diagnostics, and never download runtimes from inside Excel.

Performance has six independent classes: scalar kernels, member batches,
candidate search, serialization, workbook work and ETABS acquisition. Each has
a frozen workload, numerical budget, memory limit and measurement method. The
important user targets are a typical warm 20-member workbook p95 at or below
one second and progress/cancellation response within 250 ms. These are future
acceptance budgets, not inferred speed claims.

## Exit review

- Seven runtime/host surfaces name exact targets and current evidence state.
- Pure, optional, Excel and ETABS dependencies are physically separable.
- Python, NuGet, XLL and ETABS adapter distribution contents are defined.
- Six performance classes and eight benchmark datasets have explicit budgets.
- Release evidence binds source, packages, XLL, hosts, engineering and timing.

PF10 now gives all existing callers an adoption path and makes the documentation
usable from Python, .NET, Excel and ETABS workflows.
