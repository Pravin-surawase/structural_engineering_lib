---
owner: Main Agent
status: active
last_updated: 2026-08-24
doc_type: reference
complexity: intermediate
tags: [api, beta, compatibility]
---

# API Stability and Classification

**Type:** Reference
**Audience:** Developers
**Status:** Beta Maturity / Normal Software Release
**Importance:** High
**Version:** 0.25.0
**Last Updated:** 2026-08-24

StructLib is a pre-1.0 Beta-maturity project distributed under a normal final
package version. No exported Python symbol currently carries a post-1.0 stable
compatibility promise, and passing software tests do not imply complete IS 456
coverage, qualified structural review, or professional approval.

## Machine-readable classification

The maintained [API classification registry](api-classification.json) records
every symbol on these surfaces:

- `structural_lib`: recommended root facade; declared exports are `preview`;
- `structural_lib.services.api`: recommended service facade for explicit
  workflows; declared exports are `preview`;
- `structural_lib.api`: retained delegating facade; declared exports are
  `compatibility`;
- any public-looking callable present on those modules but absent from
  `__all__`: `internal` and unsupported as a dependency.

The four classifications mean:

| Class | Current promise |
|---|---|
| `stable` | Reserved for a separately approved compatibility commitment; none exist in this pre-1.0 release. |
| `preview` | Deliberately exported and documented, but may change before 1.0. |
| `compatibility` | Retained migration facade; new callers should use the recommended facade. |
| `internal` | No public compatibility promise. |

Each tracked symbol also has one claim disposition:

| Disposition | Meaning |
|---|---|
| `canonical` | Small capability-bound task API; currently the reference beam journey |
| `advanced` | Maintained specialist/capability tool outside the small task API |
| `compatibility` | Retained public migration surface without a canonical-task claim |
| `hold` | Callable preview whose broader advertised use is blocked by a named gate |
| `internal` | Undeclared implementation detail |

Artifact claims are separate. The wheel ships the `structural_lib` Python API and
CLI. `fastapi_app` and `react_app` are exact-head application surfaces and are not
inside the wheel. The checked-in development clients under `clients/` are also
repository artifacts, not wheel contents.

CI regenerates the registry from the installed candidate and fails when a
declared export, public-looking callable, facade classification, or package
version changes without an intentional registry update.

The maintained [compatibility ledger](api-compatibility-ledger.json) separately
records canonical object ownership, identity/signature proof, retained root
stubs, `api_hub`, maintained callers, P5 held compatibility, and deletion
authorization. Its projection total must reconcile exactly with this registry;
an ambiguous maintained caller fails the generator check. The checked-in ledger
uses a lossless column-dictionary JSON encoding to retain every record within
the repository's small-file boundary.

## Compatibility policy

Within the pre-1.0 release series, changes remain surgical and documented. Confirmed
unsafe behavior is corrected even if permissive callers used it: a
compatibility route may map known aliases, but it may not fill missing
structural inputs, hide import loss, or convert missing status to PASS.
An identity-only public facade is not deprecated just because it re-exports an
object. Deprecation requires a real replacement and an owner-approved removal
schedule; held compatibility may instead carry explicit limitation metadata
with no warning or removal version.

Use exact release pins for reproducibility:

```bash
python3 -m pip install "structural-lib-is456==0.25.0"
python3 -c "import structural_lib; print(structural_lib.__version__, structural_lib.__file__)"
```

See [Which API should I use?](api-levels.md), the [P7 migration
guide](../migration/lib-pro-007-p7-compatibility-convergence.md), the
[deprecation policy](deprecation-policy.md), and the [release
policy](../getting-started/releases.md#current-release-process-29-october-2026).

## S3 contract review and migration — 29 October 2026

The S3 audit reconciles 14 Python surfaces, 1,308 classified projections,
60 typed facade functions, 115 compatibility functions, 13 family requests
with 564 field leaves, 92 HTTP operations and 488 OpenAPI components. The
[contract matrix](../verification/library-s3-contract-matrix.json) records every
HTTP owner and schema role, required/default/null/enum counts and maintained
instance-test locations. Its component names resolve directly into the existing
OpenAPI baseline; family field policies remain in the classification registry.
Run `./scripts/python_runtime.sh scripts/audit_public_contracts.py` to check it.
Schema reachability and meta-validation establish structure; selected positive,
negative and round-trip tests establish the named software behavior. Neither
establishes independent engineering or native-host acceptance.

The review uses [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html),
[JSON Schema 2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation)
and [Pydantic strict-mode behavior](https://docs.pydantic.dev/latest/concepts/strict_mode/).
Required, default and nullable are separate decisions: a schema default does
not itself insert a runtime value, and JSON Schema does not evaluate engineering
units or cross-field physical relationships. Owning request validators perform
those checks. Strict family requests reject numeric booleans/strings, non-finite
values and unknown fields. Legacy wall and WebSocket numeric-string conversion
remains an explicit compatibility policy. Python's
[PEP 387](https://peps.python.org/pep-0387/) informs the review of argument order,
return meaning and exceptions; its CPython policy is not a new library guarantee.

The [signature exceptions](api-signature-exceptions.json) retain all 32 existing
compatibility functions with more than three positional parameters, plus the
root-only ETABS observation-evidence API. Each exact owner/signature has an
explicit retention reason. The maintained classifier rejects unexplained new,
changed or stale exceptions. Existing positional binding remains intact; new
callers should use the documented keyword arguments.

### Beam HTTP and WebSocket quantities

Both transports now use one response projection, including the same physical
effective-depth basis, canonical result envelope, calculation identity and shear
quantity `Asv/s` in mm²/mm. Previously WebSocket omitted the division by effective
depth and omitted the envelope, causing a wrong shear quantity and a synthetic
React HOLD. These are transport corrections; IS 456 mathematics is unchanged.

`utilization_ratio` remains a required number capped at 2.0 for legacy display
compatibility and is marked deprecated. New responses always include
`governing_utilization`: the uncapped finite ratio, or `null` with
`unavailable_utilizations` carrying the existing typed reason. Use the actual
field for decisions; rolling clients may read `evidence.exact_utilization` from
older servers. An explicit null must survive that fallback. Missing evidence or
a mismatch between projection and evidence remains HOLD for export purposes.
Known React consumers preserve null and show “Unavailable”; they never infer a
capacity or PASS from the capped display field. Unidentified old records carrying
only a display ratio show unavailable until rerun. Saved batch-v1 finite ratios
remain readable because that contract has always carried an uncapped quantity.

Batch service/SSE/polling now serialize non-finite ratios as null with reasons.
This corrects previously invalid JSON containing `Infinity`. Dashboard intake
accepts the actual uncapped ratio or null; unavailable members are excluded from
ratio statistics, while their status still contributes to the outcome counts.
If every member ratio is unavailable, min/mean/max are null. Zero is an observed
ratio and participates in the statistics. An empty dashboard retains its existing
empty-state zeros. Building export remains gated by current qualified results.

The compatibility WebSocket rejects duplicate JSON keys, numeric booleans,
non-finite values, conflicting cover aliases and unknown structural inputs.
Previously those inputs could silently change the action/depth basis. Supply
all nine calculation-bearing fields; `cover` and `clear_cover` remain equivalent
aliases when consistent. Optional `length` is viewport metadata in mm and does
not request a serviceability check. Torsion/serviceability use canonical HTTP;
this adapter's existing material/range limits are unchanged. Its
[machine schema](beam-design-websocket-v1.schema.json) is checked with the OpenAPI
and supplied-check V2 snapshots. Rejected input is a structured problem and the
connection remains usable for a corrected message.

No removal date, public release, new support scope, native application mutation
or professional approval is selected by S3. S4 engineering/output qualification,
S5 final-version artifact qualification and S6 per-release authorization remain
separate programme gates.
