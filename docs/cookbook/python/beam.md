---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: guide
complexity: beginner
tags: [beam, canonical-api, lib-pro-013-b0]
---

# Canonical IS 456 Beam Journey

Workflow ID: `is456.beam.design/v1` (design, design-and-detail, and BBS modes)

Minimum artifact: `structural-lib-is456==0.24.0`, which contains
`structural_lib.design.is456.beam`. Confirm the installed version and package
origin with `python -m structural_lib install-preflight`.

Supported case: one rectangular beam, caller-supplied factored non-negative
action magnitudes, explicit effective depth, IS 456 materials, explicit
detailing choices, and BBS composition. Load generation, flanged sections, and
signed action conventions are outside this recipe.
Canonical serviceability request models remain explicitly held in B0 until
their strict typed field contracts freeze; passing `serviceability` returns
`SERVICEABILITY_SCOPE_HOLD` rather than silently accepting a partial model.

```python
from structural_lib.design.is456 import beam

detailing = beam.BeamDetailingOptionsV1(
    standard=beam.DetailingStandard.IS456,
    clear_cover_mm=40,
    tension_bar_diameter_mm=20,
    compression_bar_diameter_mm=16,
    nominal_top_steel_ratio=0.25,
    stirrup_diameter_mm=8,
    stirrup_legs=2,
    stirrup_spacing_support_mm=150,
    stirrup_spacing_mid_mm=200,
)

request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=detailing.asv_mm2,
    detailing=detailing,
)

result = beam.design_and_detail(
    request,
    detailing_standard=beam.DetailingStandard.IS456,
)
schedule = beam.bbs(result)

print(result.engineering_status)
print(schedule.total_weight_kg)
```

An engineering `FAIL` is a valid result, not an input error. Check the
orthogonal envelope instead of treating object creation as a pass:

```python
result = beam.design(request)
print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)
print(result.to_dict()["envelope"]["overall_status"])
```

Invalid intake raises the library-owned structured exception. Raw Pydantic
errors do not escape the facade:

```python
from structural_lib.core.errors import InputContractError

try:
    beam.input(
        member_id="B1",
        story="GF",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=300,
        D_mm=550,
        d_mm=500,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm="150",  # rejected: numeric strings are not coerced
        vu_kn=80,
        d_dash_mm=50,
        asv_mm2=100,
    )
except InputContractError as error:
    for issue in error.issues:
        print(issue.code, issue.path)
```

The same nested request is accepted by `POST /api/v2/design/beam` and by the
CLI:

```bash
python -m structural_lib beam-v1 request.json --mode design
python -m structural_lib beam-v1 request.json --mode design-and-detail
python -m structural_lib beam-v1 request.json --mode bbs
```

The result retains a final-review state field for claim truth. The published
software has not received the deferred cumulative practicing-engineer review;
every project result still requires independent qualified review.
