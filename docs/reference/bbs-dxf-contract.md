# BBS + DXF Contract (v1.x)

This document defines the stable contracts for Bar Bending Schedule (BBS) and
DXF outputs. It is beam-only (IS 456) and is intended for integrators who need
predictable outputs across releases.

## 1) Bar Mark Identity (Project-Unique)

Each BBS line item has a `bar_mark` that is unique across the project and is
used in DXF callouts.

**Format (v1.x target):**
```
<beam_id>-<loc>-<zone>-D<dia>-<seq>
```

**Tokens:**
- `beam_id`: normalized to uppercase, spaces -> "-", non-alnum stripped.
- `loc`: `B` (bottom), `T` (top), `S` (stirrup).
- `zone`: `S` (start), `M` (mid), `E` (end), `F` (full length).
- `dia`: integer diameter in mm (e.g., `D16`).
- `seq`: 2-digit sequence number assigned deterministically.

**Deterministic assignment:**
Sort all line items by:
`beam_id`, `loc`, `zone`, `diameter_mm`, `shape_code`, `cut_length_mm`,
then assign `seq` in order. This guarantees stable, project-unique marks.

**Example:**
```
B1-B-S-D16-01
B1-B-M-D16-02
B1-S-S-D8-01
```

## 2) BBS Line Item Schema (CSV)

Columns are stable and ordered as follows:

```
bar_mark,member_id,location,zone,shape_code,diameter_mm,no_of_bars,
cut_length_mm,total_length_mm,unit_weight_kg,total_weight_kg,remarks
```

**Units:**
- Lengths: mm
- Weights: kg

**Rounding rules (v1.x target):**
- `cut_length_mm`: round to nearest 1 mm.
- `total_length_mm`: `no_of_bars * cut_length_mm` (mm).
- `unit_weight_kg`: round to 0.01 kg.
- `total_weight_kg`: `no_of_bars * unit_weight_kg`, round to 0.01 kg.
- Summary totals: round to 0.01 kg after summing.

## 3) DXF Contract

**DXF version:** R2010 (AC1024)
**Units:** mm
**Views:** elevation + section (if enabled)

**Required layers (minimum):**
- `BEAM_OUTLINE`
- `REBAR_MAIN`
- `REBAR_STIRRUP`
- `DIMENSIONS`
- `TEXT`
- `CENTERLINE`

**Required text content:**
- Beam ID + Story (title or header).
- Bar marks for top/bottom/stirrups.
- Zone labels for start/mid/end where applicable.

**Callout format (minimum):**
```
<bar_mark>  (and zone, if not already encoded)
```

## 4) Consistency Rules

- Every `bar_mark` in BBS must appear in DXF callouts for the same beam.
- Every DXF callout mark must exist in the BBS for that beam.
- Ordering of callouts is deterministic (no random shuffling).

## 5) Change Policy

Breaking changes to this contract require:
- A `schema_version` bump (where applicable).
- A migration note in CHANGELOG/RELEASES.
- Backward-compatibility guidance for consumers.
