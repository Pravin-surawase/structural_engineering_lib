---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, continuous, concurrent-actions, is456]
---

# Check a two-span rectangular beam

Use `beam.load_continuous` and `beam.check_continuous` when you have signed
actions at physical stations and an actual reinforcement layout. The Python
workflow checks sagging, hogging, shear and straight support anchorage. The
result retains each supplied combination and its analysis revision.

## Run the worked example

Use the matching 0.29 candidate. Copy the
[Python script](../../../Python/examples/continuous_beam_check.py) and the
[frozen reference](../../verification/library-029-beam01-flow01.json) to a
working directory. Run `python -m structural_lib install-preflight` to check
which package your interpreter will use.

```bash
python continuous_beam_check.py --reference library-029-beam01-flow01.json \
  --case two_span --output-dir beam-pass
python continuous_beam_check.py --reference library-029-beam01-flow01.json \
  --case strength_failure --output-dir beam-fail
python continuous_beam_check.py --reference library-029-beam01-flow01.json \
  --case missing_anchorage --output-dir beam-hold
```

Each run writes `result.json` and `report.html`. The report and JSON share
the input hash and analysis and reinforcement revisions. Use a fresh output
directory for each run. Supply your own complete request with `--input`.

## Read the example

The specimen is a 300 × 550 mm M25 beam with two 4 m spans measured between
support centrelines. It has three Ø20 Fe415 bars on each face, 50 mm from the
nearest concrete face, with two-leg Ø8 links at 300 mm. The checked section
uses `d = 500 mm` in either bending direction.

| Station and row | Concurrent actions | Check |
|---|---|---|
| B01 left and right midspan | +90 kN·m, 0 kN | Bottom-face tension. Each span uses 57.3% of the 157.006 kN·m flexural resistance. |
| U1 at the right face of the middle support | −120 kN·m, +70 kN | Top-face tension. This row governs hogging at 76.4%. |
| U2 at that same physical face | −85 kN·m, +115 kN | This row governs shear at 82.1% of the 140.154 kN resistance. |
| Pattern at the internal centreline | −40 kN·m on both sides, −70 kN on the left and +30 kN on the right | The 100 kN jump remains visible across two diagnostic rows. The two physical faces at 3850 and 4150 mm govern their own checks. |

The [independent replay](../../verification/check_library_029_beam01_reference.py)
solves compression and tension equilibrium from the IS 456 rectangular block
and actual steel positions. The neutral axis is **66.907 mm** and each tension
face contains **942.478 mm²**. Table 19 gives 79.659 kN concrete shear resistance.
The two Ø8 legs provide another 60.495 kN, below the Table 20 section limit.

At the right face of the internal support, the top bars extend 4368 mm toward
the left from the checked face. The required full-stress development is
805.915 mm. The simple end support checks also apply the end extension and
same-row moment-resistance-to-shear criterion. In the short-anchorage control,
the left end has 750 mm available for the governing criterion and fails the
805.915 mm requirement.

## Use the Python API

```python
import json
from pathlib import Path

from structural_lib.design.is456 import beam

fixture = json.loads(Path("library-029-beam01-flow01.json").read_text())
request = beam.load_continuous(fixture["cases"]["two_span"]["request"])
result = beam.check_continuous(request)
assert result.ultimate_status == "PASS"
assert result.governing_rows["hogging"] == "U1:B-RIGHT-FACE"
assert result.governing_rows["shear"] == "U2:B-RIGHT-FACE"
assert result.serviceability_status == "HOLD"
Path("two-span.html").write_text(beam.render_continuous_html(result), encoding="utf-8")
```

Use mm, kN and kN·m. Longitudinal coordinates increase from the first
support toward the last. Section bar coordinates are measured from the left
and top edges. Positive moment gives bottom-face tension and negative moment
gives top-face tension. Shear retains its sign in the report. Capacity uses
its magnitude. At zero moment the shear check uses the weaker face basis.

Supply a required station inventory for each combination. At least one ULS
combination must cover both spans, all four physical support faces and both
sides of the internal support centreline. Each row has a unique source ID.
A separate source analysis must establish which combinations and stations
are needed for the project. Omitting a declared row holds the applicable
scope. Duplicate station IDs or combination-station rows raise a structured
`InputContractError`.

`ultimate_status` covers the supplied ultimate and anchorage checks.
`serviceability_status` stays HOLD for supplied service combinations. The
`missing_sustained` case preserves the ULS outcome and identifies the missing
S2 row. A revision mismatch keeps the rows visible and withholds the calculations.

The supported scope is a prismatic, ordinary rectangular section with two
spans, simple outer supports, one longitudinal layer per face, vertical
two-leg links and continuous straight longitudinal bars. The workflow takes
no near-support shear enhancement. Stability, frame analysis, deflection,
crack width, splices, curtailment, seismic checks and a fabrication BBS require
separate evidence. The result always requires qualified review.
