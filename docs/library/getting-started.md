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
