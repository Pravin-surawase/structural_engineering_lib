---
owner: Main Agent
status: active
last_updated: 2026-11-12
doc_type: guide
---

# Select a column from a finite catalogue

Use `structural_lib.design.is456.column` to choose an oriented rectangular
size, one diameter for all eight longitudinal bars, and one complete hoop
and midpoint link option. Supply only the options approved for the project.
The workflow checks short braced members with symmetric eight-bar cages
and ordinary nonseismic restraint.

## Run the worked example

Install the matching 0.29 candidate and check its origin with
`python -m structural_lib install-preflight --json`. The catalogue profile
appears in `python -m structural_lib capabilities --json`. Copy the
[example script](../../../Python/examples/column_catalogue_selection.py) and
[matching reference JSON](../../verification/library-029-col06-column-catalogue.json)
into your working directory and run:

```bash
python column_catalogue_selection.py --reference library-029-col06-column-catalogue.json --case nominal --output-dir col06-nominal
python column_catalogue_selection.py --reference library-029-col06-column-catalogue.json --case multiple_combinations --output-dir col06-two-combinations
python column_catalogue_selection.py --reference library-029-col06-column-catalogue.json --case changed_size --output-dir col06-refresh
```

Each run writes `result.json` and `report.html`. A selection also writes
`section.svg` with the checked bar and link geometry. The drawing shows
HOLD if the selection needs analysis refresh. Use a fresh output directory
for each run. For your own inputs, pass a request JSON with `--input`.

## Read the results

The 3 m, fixed-fixed braced example uses M25 concrete, Fe415 longitudinal
steel and 40 mm cover to the outside of the hoop. The catalogue combines
three section sizes (300 × 400, 350 × 450 and 400 × 500 mm), bar diameters
16, 20 and 25 mm, and three supplied tie options. That gives 27 candidates.

1. For U1 at 1500 mm, supply 500 kN and signed moments +50 and +35 kN·m.
   The selected 300 × 400 mm section uses 8Ø16 and Ø8 ties at 150 mm.
   The bar centres at the corners are 58 mm from the adjacent faces:
   40 mm cover + 8 mm hoop + 8 mm bar radius + 2 mm inset. The governing
   utilization is **0.74718**. The 300 mm pitch option fails with Ø16
   longitudinal bars: the 16-bar-diameter limit is 256 mm.
2. Add U2 at 750 mm with 500 kN and moments −75 and +55 kN·m. The selection
   becomes **300 × 400 mm, 8Ø20, Ø8 ties at 300 mm**, governed by U2 at
   **0.98501**. Each signed triplet is checked together at its station.
   Positive Mx compresses the top face and positive My the left face.
3. Run `changed_size` to supply actions from a 400 × 500 mm analysis
   section. The locally feasible 300 × 400 mm candidate remains **HOLD**.
   Update the model, rerun the analysis and supply its new actions and
   revision before accepting that member. The same rule applies when
   the material or geometry basis differs. This selector cannot bind
   reinforcement-dependent stiffness, so that basis stays HOLD and needs
   a separate member check. Use `stale_analysis` to see a revision mismatch.

The selector ranks by least gross area, then least longitudinal steel
area, then width, depth, bar diameter, tie diameter, larger tie pitch, tie
option ID and size ID. This rule makes the result independent of catalogue
order. It does not estimate cost or build a member reinforcement schedule.

Use `no_feasible` for a complete search in which every option fails on the
supplied actions. `budget_exhausted` leaves the search incomplete even if a
visited option passed. `missing_restraint` shows a complete enumeration
with unresolved mandatory checks on options that have not already failed.
One failed row rules out its option; any other held rows stay visible.
The latter two cases return HOLD; none of these three selects or draws a section.

## Call it from Python

```python
import json
from pathlib import Path

from structural_lib.design.is456 import column

fixture = json.loads(Path("library-029-col06-column-catalogue.json").read_text())
request = column.load_column_catalogue(fixture["cases"]["multiple_combinations"]["request"])
result = column.select_column_from_catalogue(request)
calculation = result.to_dict()["calculation"]
print(result.engineering_status.value, calculation["terminal_state"])
print(calculation["selected_id"], calculation["analysis_status"])
```

Inspect `column.ColumnCatalogueInputV1.model_json_schema()` for the request
fields. The loader reports invalid inputs through `InputContractError`.
Provide mm, kN, kN·m and N/mm² as named in the fields. Use up to 128
candidate combinations and eight uniquely identified action rows at
stations within the member. The catalogue enumerates only the supplied
sizes, bar diameters and complete tie options.

In the result, `evaluated` records every visited candidate in rank order,
with per-combination status, utilization, issue codes and check input
hash. `eligible_ids` lists local passes; read `terminal_state` and
`analysis_status` before using `selected_id`. When there is a selection,
`selected.checked_member` carries the full governing strength and cage
check. The HTML and SVG identify the same catalogue and governing check.

The [independent replay](../../verification/check_library_029_col06_reference.py)
checks the frozen candidates without importing the library. The workflow
does not establish the completeness of your action combinations or
stations. Slender and circular sizing, column shear, joints, seismic
details, splices and fabrication schedules need separate checks.
