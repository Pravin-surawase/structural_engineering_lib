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
