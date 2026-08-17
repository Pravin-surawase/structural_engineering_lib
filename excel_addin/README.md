# Excel Routine Workbench V1 task pane

This macro-free Office.js task pane reads only `Beam_Workbench / tbl_Beam_Workbench_V1`, previews the strict mapping, and sends a confirmed snapshot through the local FastAPI Excel Workbench V1 endpoints. It writes the returned row ledger, canonical result projections, and calculation passports to their named workbook tables.

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
- A Run is rejected unless the current selected-table snapshot equals the previewed snapshot and the 64-character mapping hash is confirmed.
- The Office document settings retain the workbook instance ID, four-hash freshness evidence, and stale flag across task-pane sessions; complete ledgers, results, and passports remain in their workbook tables.
- Excel does not execute structural-design formulas. VBA/macros, torsion, serviceability, ETABS access, write-back, release claims, and professional approval are outside E1.

Installed Windows Excel evidence is a separate gate and remains `TO_VERIFY_WINDOWS` until executed on the supported environment.
