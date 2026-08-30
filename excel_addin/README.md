# Excel Routine Workbench V1 task pane

This macro-free Office.js task pane reads only `Beam_Workbench / tbl_Beam_Workbench_V1`, previews the strict mapping, and sends a confirmed snapshot through the local FastAPI Excel Workbench V1 endpoints. It writes the returned row ledger, canonical result projections, and calculation passports to their named workbook tables. After a current run or an explicit `CURRENT` freshness check, it can download a complete deterministic JSON review bundle whose bytes and result identities are verified before save.

The same pane also contains a separate Windows-only **ETABS beam pilot**. It
checks the local Python/library/COM bridge, attaches to an already-open copied
ETABS model, reads one exact result case or combination, designs up to five
horizontal rectangular beams, and writes only
`ETABS_Pilot / tbl_ETABS_Pilot_V1`. See the complete
[setup and boundary guide](../docs/guides/excel-etabs-python-bridge-pilot.md).

## Local development transport

The manifest requires HTTPS. Start the FastAPI application on `127.0.0.1:8000`, provide trusted localhost development certificate paths, and run:

```bash
E1_OFFICE_KEY_PATH=/absolute/path/to/localhost.key \
E1_OFFICE_CERT_PATH=/absolute/path/to/localhost.crt \
npm run serve
```

The HTTPS server exposes `https://localhost:3000/taskpane.html` and proxies same-origin `/api/` requests to the local FastAPI process. Sideload `manifest.xml` into Excel only in an authorized test environment.

## Safety boundary

- Any change on `Beam_Workbench` immediately marks retained output stale, clears the reviewed mapping, and disables Run.
- If the exact E1 worksheet/table is not open, the pane may prove the local API identity but remains read-only: it does not create document settings, register events, or enable calculation controls.
- A Run is rejected unless the current selected-table snapshot equals the previewed snapshot and the 64-character mapping hash is confirmed.
- The Office document settings retain the workbook instance ID, four-hash freshness evidence, and stale flag across task-pane sessions; complete ledgers, results, and passports remain in their workbook tables.
- Export sends the current source snapshot and retained identities back to Python. The service regenerates the canonical result, requires exact source/mapping/library/result agreement, and returns complete JSON evidence; Excel never packages a client-supplied old result.
- Any edit disables export immediately. A reopened workbook must pass an explicit freshness check before export is re-enabled.
- Excel does not execute structural-design formulas. VBA/macros, ETABS analysis
  or write-back, serviceability, continuity/congestion optimization, release
  claims, and professional approval remain outside the implemented surfaces.
- The ETABS pilot uses explicit task-pane buttons and a dedicated controlled
  table. It is independent of the E1 workbook surface and refuses to overwrite
  a colliding worksheet or changed table.

The prior installed Windows Excel journey does not prove this new COM bridge.
Installed Windows Excel + ETABS pilot evidence remains a separate gate until the
exact current implementation is executed on the supported environment.
# W3 calculation review (provider-neutral)

The W3 pane works without a running FastAPI or ETABS process. It imports a
saved dossier transport, verifies the complete source hashes, then publishes
sixteen formula-free `ETABS_W3_*` controlled tables. It never calculates
structural actions or treats a typed reviewer name as professional approval.

Export from the worktree-bound Python runtime:

```bash
./scripts/python_runtime.sh scripts/export_calculation_review.py --dossier /absolute/path/dossier.json --output /absolute/path/new-review.json
```

The input is the existing `CalculationDossierV1`. Its canonical `CATALOGUE`
artifact contains `ETABSResultCatalogueV1`; `DEMAND` contains
`{"schema_version":"beam-demand-review/v1","request":BeamDemandDerivationRequestV1,"snapshot":BeamDemandSnapshotV1}`;
`CALCULATION` contains `BeamAuditEvaluationResultV1`, or an explicit blocked
`BeamAuditInputBuildResultV1` with software status `HOLD`. No missing design
basis is defaulted. The exporter replays the catalogue and demand through
their existing owners. The dossier's artifact digests hash the **complete
canonical artifact bytes**; native catalogue/snapshot semantic digests remain
inside those artifacts and are displayed separately. The full baseline and
all signed station rows remain in the canonical demand artifact.

Open a disposable blank workbook, open the existing trusted task pane, select
the exported JSON, click **Verify saved dossier**, then **Publish all W3 review
tables**. **Read back saved review** checks every controlled calculated cell
and the complete rejoined JSON again. This is saved-evidence freshness only;
it does not attach to or claim current ETABS state. The blank routine E1 pane
may independently report its API unavailable; W3 saved review remains usable.

The write preflights all sheet/table/header collisions and the full write set,
snapshots existing touched ranges, uses ExcelApi 1.16 literal typed values,
checks all structured cells and exact canonical UTF-8 bytes/SHA-256, then
changes `PENDING` to `COMMITTED` and reads it back. Any failure removes only
newly created controlled sheets and restores existing ranges/dimensions.
Expansion into nonempty cells outside a controlled table is refused.
Shrinking clears only the former controlled footprint. A partial workbook is
not accepted.

Comments are user-owned: edit only disposition/comment/reviewer-label/UTC
columns of `ETABS_W3_Comments`. They remain bound to the original dossier SHA
and revision, survive refresh, and export separately without changing any
canonical calculation byte. Revision history is append-only and hash-bound.
Refresh accepts the same exact dossier content or its exact next revision;
new attestation bytes on the same dossier require a new workbook, preserving
the old record. Old proprietary payloads must remain in external evidence.

Bounds: 64 MiB canonical dossier, 50,000 projected rows across all tables,
30,000 UTF-16 units per cell, 15,000-unit JSON chunks. No silent truncation.
Empty projections use one explicitly blank table body row. The governor
table joins each reference to its exact signed station; it never combines
independent extrema into a concurrent action. Optional evidence preserves
all five states. Provider signing, credentials, professional/construction
approval and W3H/I/K/L acceptance remain separate and unapproved.
