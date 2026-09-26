# Getting started

Python callers import bounded operations from `structural_lib.beam`:

```python
from structural_lib.beam import bar_area, mass_per_length

area = bar_area(16)
mass = mass_per_length(16, 7850)
assert area.outputs["area_mm2"] > 0
assert mass.outputs["mass_kg_per_m"] > 0
```

.NET callers reference the relevant pure package and receive the same semantic
operation and result-state meanings:

```csharp
using StructuralEngineering.Contracts;
using StructuralEngineering.Reinforcement;

var area = ReinforcementOperations.BarArea(new BarAreaRequest("IS456-WP01", 16));
if (area.Engineering == EngineeringState.Pass)
    Console.WriteLine(area.Outputs!.Value);
```

Read every result dimension independently. `rejected_input` is an execution
outcome, `not_applicable` is a supported-profile decision, and engineering
`fail` means a completed check did not satisfy its criteria. A result is usable
for the active project only when its completeness and freshness also qualify.

Coordinates use the physical section: x is measured from the left face and y
from the top face in millimetres. Each bar carries its physical face and layer.
This permits positive and negative bending to use actual bottom and top
arrangements without inferring geometry from the sign alone.

WP03 analysis uses a separate explicit N/mm boundary. A simply supported beam
with a downward 10 N/mm uniform load can be solved without Excel or ETABS:

```python
from structural_lib.beam import BeamElement, BeamLineRequest, BeamNode, solve_beam_line

request = BeamLineRequest(
    "model-1",
    "service-case-1",
    (BeamNode("A", 0, True, False), BeamNode("B", 5000, True, False)),
    (BeamElement("E1", "span-1", "A", "B", 200_000, 1_000_000_000, -10),),
)
response = solve_beam_line(request)
assert response.execution == "completed"
```

The same request can include prescribed support displacement, point loads, and
station intervals. See the [WP03 reference](reference/wp03-actions-analysis-topology.md)
for signs, limits, topology mapping, and excluded analysis profiles.

WP04 keeps span/depth screening separate from calculated deflection. A service
check that lacks load-history or stiffness evidence returns `not_evaluated`
instead of converting the screen into a displacement. Crack-width checks use
the actual tension-face bar coordinates, diameters, and supplied service strain.
See the [WP04 reference](reference/wp04-serviceability.md) for limits, component
aggregation, Annex F geometry, and result-state rules.

WP05 turns calculated requirements into checks of physical reinforcement. An
anchorage request carries the actual bar path and separate support face/centre;
a lap and curtailment request carries the station demand and continuing bar ids;
the seismic operation carries both joints and qualified upstream results; and
the arrangement operation receives every bar, link, obstacle, and conditional
placement opening. See the
[WP05 reference](reference/wp05-detailing-constructability.md) for the complete
signatures, normalized source rules, and construction-fit behavior.

WP06 freezes those decisions in a versioned project/profile, derives the
complete expected member-check set from that profile and topology scope, and
resolves physical reinforcement into marked tangent straights and bend arcs.
See the [WP06 reference](reference/wp06-project-member-paths.md) for the public
signatures, optional input rules, actual-depth convergence, and exact bar-path
geometry.

WP07 consumes those current physical paths to create BBS rows, cutting-stock
allocations, steel/concrete/formwork quantities, dated itemized direct cost,
and the renderer-neutral calculation package. Kerf, reusable offcuts, waste,
concrete overlap ownership, formwork contact faces, commercial scope, and real
human actions stay explicit. See the
[WP07 reference](reference/wp07-construction-calculation-package.md) for the
public signatures and reconciliation rules.

### Connect the physical operations in Python

The runnable [physical-member example](../../Python/examples/physical_member_workflow.py)
connects project/profile creation, genuine geometry/flexure/seismic checks,
member aggregation, physical paths, BBS, quantities, declared costs, and package
data. Install the current source build; the new helpers are not assumed to
exist in the older published wheel:

```bash
python3 -m pip install -e ./Python
python3 Python/examples/physical_member_workflow.py
```

Results keep their JSON-shaped `outputs` for serialization. Use
`result.output_as(key, OutputType)` to recover a typed record for another
operation, including nested dataclasses, tuples, and enums:

```python
project = project_result.output_as("project", BeamProject)
schedule = path_result.output_as("reinforcement_schedule", BarPathOutput)
bbs = bbs_result.output_as("bbs", BbsOutput)
```

Projection checks that the canonical payload is unchanged. A missing output
raises `KeyError`; a mismatched or lossy type raises `ValueError`. Inspect the
result states before proceeding; projection also permits inspection of partial
outputs and does not turn them into passing evidence.

Use `MemberLeafEvidence.from_result("flexure@B1", actual_check_result, ...)` to
retain the operation's exact identities, states, diagnostics and provenance.
Use `reporting.result_binding(result, output_key)` for construction-package
dependencies. Both helpers copy evidence; they do not run or approve a check.

The example's frozen teaching profile requires geometry, positive flexure, and
ordinary-frame seismic applicability. It is deliberately not a complete
building-design profile. It measures four supplied 20 mm straight bars in a
300 × 500 × 6000 mm prism: 59.187606 kg steel, 0.9 m³ concrete and 7.8 m² formwork.
Rates are explicit invented teaching inputs. Shear, torsion, serviceability,
anchorage, durability and actual construction approval remain outside that
fixture. A real integration supplies its approved complete profile and genuine
results for every required check.

Removing a required result keeps the member partial; marking its evidence
stale keeps the package a draft. `issue_ready` only describes the complete
declared semantic package. The example records no human approval and renders
no issued files. The native WP11 ETABS baseline in the reference is a separate
.NET application contract, not an automatic Python design entry point.

WP08 expands an explicit finite section/bar/link domain, binds each candidate
to the complete profile-derived member result and physical WP07 quantities,
and ranks only candidates with complete evidence. Fixed-action studies retain
their common-force assumption; coupled section, stiffness, release, offset,
self-weight, load, support, mesh, or analysis-setting changes require a fresh
candidate analysis snapshot. See the
[WP08 reference](reference/wp08-beam-optimization.md) for signatures,
objectives, tie breakers, cancellation, and optimum-claim rules.

WP10-01 accepts an immutable JSON snapshot produced by a later adapter and
validates it without opening ETABS. Python callers can replay the shared
conformance artifact through the normal public module:

```python
import json
from pathlib import Path

from structural_lib.analysis_snapshot import parse_analysis_snapshot_json

fixture = json.loads(
    Path("contracts/structural-engineering/conformance/wp10-vectors.json")
    .read_text(encoding="utf-8")
)
result = parse_analysis_snapshot_json(json.dumps(fixture["valid_snapshot"]))
assert result.execution == "completed"
assert result.snapshot is not None
```

The native .NET library replays the identical bytes and identities:

```csharp
using StructuralEngineering.Analysis;

var result = AnalysisSnapshotCodec.ParseAndValidate(snapshotJson);
if (result.Execution == ExecutionState.Completed)
    Console.WriteLine(result.Snapshot!.SnapshotId);
```

The snapshot keeps original units and one-time conversion factors, model and
result epochs, axes and physical faces, object/element/physical stations,
cases/combinations, all six signed force components from one source row, and
the getter call/source-row evidence. Inspect execution, completeness,
freshness, approval, and diagnostics independently. Offline replay establishes
portable integrity and mapping consistency; it is not a live-host compatibility
check, structural analysis, or engineering approval. See the
[WP10-01 reference](reference/wp10-analysis-snapshot.md).
