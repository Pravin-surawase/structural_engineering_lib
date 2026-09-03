---
name: beam-automation
description: Build or review the requirements-first ETABS-to-Excel reinforced-concrete beam workflow, including C# contracts, bounded analysis, constructible detailing, quantities, and reports.
---

# Beam automation

Use this workflow for the C# Excel beam product and its ETABS integration path. Start with the current requirements-first contracts and the active C# solution; do not infer a completed installed Excel or ETABS workflow from planning or Python reference code.

Keep engineering ownership in the typed C# kernel. Excel maps inputs, displays current status, and produces report artifacts; it does not reproduce structural formulas. Discover an existing Python reference API before relying on it:

```bash
./run.sh find --api <function>
./scripts/python_runtime.sh scripts/discover_api_signatures.py <function>
```

For each public operation, retain its request/result contract, source and example identity, explicit units/signs, applicability, and a current input/result identity. ETABS-derived actions also retain model/runtime/result epoch, case/combination, station, local-axis and physical-face identity. Identify missing or changed inputs precisely and recalculate dependent results before design completion.

Treat a beam as design-complete only after its declared profile has evaluated all required strength, serviceability, detailing and constructability checks against actual selected bars. Preserve bar face, layer, count, diameter, centroid, length/termination, stirrup zones, anchorage and lap inputs. Area-only selection, a bounded solver result, or an Excel export is not an issued member design.

Use bounded solvers only inside their declared applicability envelope; do not replace ETABS global analysis. Keep candidate generation deterministic and report incomplete search or no-feasible-candidate states truthfully. Build BBS, formwork, quantities, cost and reports from the same current detailed-member identity.

For C# changes, use the locked .NET 10 commands from repository root:

```bash
cd CSharp
dotnet restore StructAutomate.slnx --locked-mode
dotnet build StructAutomate.slnx -c Release --no-restore
dotnet test --project tests/StructAutomate.Tests/StructAutomate.Tests.csproj -c Release --no-build
```

The packed x64 XLL is a required build artifact, but it is not installed-Excel acceptance. Do not add ETABS mutation, report issuance, or package publication without the task's explicit authorization and evidence gate.
