---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: intermediate
tags: [verification, boq, etabs, evidence]
---

# Bundled Sample BOQ Evidence

This is the reproducible software record for the bundled ETABS sample. It is
not a bill approved for procurement or construction and is not professional
structural-engineering approval.

## Accepted software record

| Field | Value |
|---|---|
| Dataset | `bundled-etabs-beam-sample` |
| Dataset version | `etabs-csv-v1` |
| Source files | `Etabs_CSV/beam_forces.csv`, `Etabs_CSV/frames_geometry.csv` |
| Dataset SHA-256 | `b95a056c411eeaf4c714713dcf7edfa402ceadb2efdcfd4382f454cc82c5f43e` |
| Hash framing | `sha256-framed-files-v1` |
| Library artifact | `0.23.0` |
| Beams | 153 imported, 153 calculated PASS, 0 FAIL |
| Steel | 1,928.49 kg |
| Concrete | 48.7319 m³ |
| Estimated cost | ₹408,101.16 |
| BOQ input hash | `c5dbdfafe608de56aa0bf71ab897b62863219855e23dc3361e4efcc0d6041b16` |
| Calculation identity | `1def25864ef5107b6c879c312564d2f94dfced04b66c54473d2c3895b907a40d` |

Steel uses the current UI `frontend-standard-bar-layout-v1` policy: select the
first standard diameter in 12, 16, 20, 25, 32 mm that provides two to eight
bars, then multiply provided area by the actual member length and 7,850 kg/m³.
Concrete uses each imported 230 × 450 mm section and actual imported span.

Run the executable record from the repository root:

```bash
.venv/bin/pytest fastapi_app/tests/test_bundled_sample_evidence.py -q
```

## Reconciliation of the older record

The older 114.8 m³ total is reproducible as 153 beams × the former fallback
300 mm width × 500 mm depth × 5,000 mm span = 114.75 m³. It therefore did not
identify the tracked sample's actual 230 × 450 mm sections and actual spans.
The paired 2,663.4 kg steel value was not bound to a dataset hash, normalized
BOQ input, library artifact, or calculation identity and is not reproducible
from the current tracked sample pipeline.

Those older values remain historical session evidence only. They are
superseded for current software acceptance by the identity-bound record above.
Any change to the dataset, bar-layout policy, library version, normalized BOQ
input, or totals changes at least one recorded identity and requires a new
reviewed evidence record.
