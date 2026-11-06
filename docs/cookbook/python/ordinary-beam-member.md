---
owner: Main Agent
status: active
last_updated: 2026-11-07
doc_type: guide
complexity: intermediate
tags: [beam, member, bbs, python]
---

# Run the single-layer and multilayer beam member examples

Use the same Python driver for both worked cases. It runs the required
member checks, resolves the actual reinforcement paths, and writes
`calculation.json`, `bbs.csv`, and `report.html`.
[Download complete_member_workflow.py](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/complete_member_workflow.py)

Both cases use a 300 × 500 mm M25/Fe415 rectangular section, a 5 m
centre-to-centre span, two 400 mm bearings, and two-leg Ø8 links at
150 mm. The examples keep the ULS and SLS load cases separate.

| Case | Longitudinal reinforcement | ULS / SLS load (N/mm) | Required checks | Physical bars | Scheduled steel |
|---|---|---:|---:|---:|---:|
| Single-layer | 2Ø20 bottom, 2Ø12 top | 12 / 8 | 19 | 39 | 56.952 kg |
| Multilayer | Bottom 2Ø25 at each of two depths, top 2Ø16 and 2Ø12 in separate layers | 36 / 24 | 27 | 43 | 129.915 kg |

Use Python 3.11 or newer in a virtual environment with a build that
contains the member workflow. To install from the repository and run both
cases from its root:

```bash
python -m pip install ./Python
python -m structural_lib install-preflight
python -I Python/examples/complete_member_workflow.py --case single-layer --output-dir beam-single
python -I Python/examples/complete_member_workflow.py --case multilayer --output-dir beam-multi
```

For an installed candidate wheel, copy the driver into a working directory
and use that environment's interpreter. The base install produces the
three files shown here. Use a distinct output directory per run to keep
each case's files together.

## Read the three outputs together

- Open `report.html` to see the engineering state, required checks, ULS
  per-bar resistance, and grouped schedule. SLS uses a cracked-section
  basis and a span/depth screen. The screen reports a ratio.
- Use `calculation.json` to inspect input provenance, the complete check
  set, physical path segments, and the retained calculation package.
- Use `bbs.csv` for one row per physical bar path. Each row carries the
  issue state, path and BBS result IDs, centreline length, and cut length.
  The HTML groups those paths by bar mark.

Both normal cases report member engineering `pass` and package
`issue_ready`. The result separately records professional approval as
`false`. The reconciliation checks that each required check is bound to
its actual result, that the topology and reinforcement revisions agree,
and that the schedule covers every path exactly once. It compares the
visible HTML tables and embedded package to the JSON and checks the
CSV identities, lengths, and scheduled mass.
[Replay receipt](../../verification/library-027-member-replay.json)

## Reproduce the admission and failure controls

Run the replay verifier with an installed package and an unused output
directory. It runs both examples, checks the files, and writes the controls
alongside the positive runs. Its JSON summary includes the hashes of the
reconciled outputs.

```bash
python -I docs/verification/replay_library_027_members.py \
  --example Python/examples/complete_member_workflow.py \
  --output-dir beam-member-replay
```

The supplied-beam V2 diagnostic holds the other inputs fixed for each
change. It records its outcomes as JSON.

| Control | Changed input | Observed result |
|---|---|---|
| Missing support width | Omit the support group | `HOLD` with `BEAM_SUPPORT_WIDTH_BASIS_NOT_SUPPLIED` |
| Conflicting depth | Supply 440 mm instead of the 442 mm depth derived from the bars, links, and cover | `FAIL` with `BEAM_SUPPLIED_EFFECTIVE_DEPTH_MISMATCH` |
| Insufficient reinforcement | Reduce four Ø20 bars to two at the same 150 kN·m demand | `FAIL` with `BEAM_TENSION_REINFORCEMENT_AREA_INSUFFICIENT`. Provided 628.319 mm², required 905.746 mm² |

The verifier also raises ULS demand to 40 N/mm for the single-layer case
and 100 N/mm for the multilayer case while preserving their respective
SLS inputs. Both existing bar layouts fail flexure under that demand. Their
calculation JSON, CSV and HTML all retain the package's `draft` state. The
multilayer HTML shows the actual overload used for the draft.
[Supplied-beam API guide](beam-supplied-check.md)
· [Multilayer reference](../../planning/multilayer-member-workflow.md)
