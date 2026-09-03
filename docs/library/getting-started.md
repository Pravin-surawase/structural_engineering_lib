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
