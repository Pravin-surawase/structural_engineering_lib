import assert from "node:assert/strict";
import test from "node:test";

import {
  buildPreviewRequest,
  buildRunRequest,
  getWorkbenchApi,
  normalizeCalculationMode,
  postWorkbenchApi,
  projectLedgerRows,
  projectPassportRows,
  projectResultRows,
  reconciliationSummary,
  retainEvidence,
  sameSourceSnapshot,
} from "../taskpane-core.mjs";

const snapshot = {
  workbookInstanceId: "EXCEL-WORKBOOK-1",
  headers: ["Row ID", "Beam ID"],
  rows: [["R1", "B1"], [null, null]],
  firstDataRowNumber: 5,
  locale: "en-IN",
  calculationMode: "Automatic",
};

test("preview request binds exact workbook, table, rows, locale, and mode", () => {
  const request = buildPreviewRequest(snapshot);
  assert.equal(request.selection.worksheet_name, "Beam_Workbench");
  assert.equal(request.selection.table_name, "tbl_Beam_Workbench_V1");
  assert.equal(request.selection.first_data_row_number, 5);
  assert.equal(request.selection.calculation_mode, "AUTOMATIC");
  assert.deepEqual(request.rows, snapshot.rows);
  assert.notEqual(request.rows, snapshot.rows);
});

test("calculation modes are explicit and unknown modes fail closed", () => {
  assert.equal(normalizeCalculationMode("Manual"), "MANUAL");
  assert.equal(
    normalizeCalculationMode("AutomaticExceptDataTables"),
    "AUTOMATIC_EXCEPT_TABLES",
  );
  assert.throws(() => normalizeCalculationMode("Mystery"), /Unsupported/);
});

test("run request requires a reviewed mapping hash", () => {
  const preview = buildPreviewRequest(snapshot);
  assert.throws(() => buildRunRequest(preview, "bad"), /mapping hash/);
  const run = buildRunRequest(preview, "a".repeat(64));
  assert.equal(run.confirmed_mapping_hash, "a".repeat(64));
  assert.equal(run.schema_version, "excel-workbook-run-request/v1");
});

test("source snapshot detects any row or selection change", () => {
  const first = buildPreviewRequest(snapshot);
  const same = buildPreviewRequest(snapshot);
  const changed = buildPreviewRequest({ ...snapshot, rows: [["R2", "B1"]] });
  assert.equal(sameSourceSnapshot(first, same), true);
  assert.equal(sameSourceSnapshot(first, changed), false);
});

test("API client preserves canonical wrapper and rejects problem responses", async () => {
  const okFetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({ success: true, data: { mapping_hash: "a".repeat(64) } }),
  });
  assert.deepEqual(
    await postWorkbenchApi("/api/v1", "/preview", {}, { fetchImpl: okFetch }),
    { mapping_hash: "a".repeat(64) },
  );
  assert.deepEqual(
    await getWorkbenchApi("/api/v1", "/definition", { fetchImpl: okFetch }),
    { mapping_hash: "a".repeat(64) },
  );
  const badFetch = async () => ({
    ok: false,
    status: 422,
    json: async () => ({ success: false, data: null, error: { message: "blocked mapping" } }),
  });
  await assert.rejects(
    postWorkbenchApi("/api/v1", "/run", {}, { fetchImpl: badFetch }),
    /blocked mapping/,
  );
});

test("output projections keep ledger, result, and passport identities", () => {
  const passport = {
    row_id: "R1", beam_id: "B1", case_id: "ULS-1", raw_row_hash: "1",
    normalized_input_hash: "2", calculation_identity: "3", result_hash: "4",
    library_version: "0.1", library_content_identity: "5",
    workbook_selection_hash: "6", mapping_hash: "7", passport_hash: "8",
  };
  const result = {
    counts: { source_rows: 1, accepted_rows: 1, blocked_rows: 0, excluded_rows: 0 },
    row_ledger: [{
      source_row_number: 5, row_id: "R1", beam_id: "B1", disposition: "ACCEPTED",
      issues: [], raw_row_hash: "1", passport,
      result_envelope: { overall_status: "PASS" },
      result: {
        case_id: "ULS-1", Mu_knm: 150, Vu_kn: 100,
        result_envelope: { overall_status: "PASS" },
        effective_depth_resolution: { d_mm: 443 },
        flexure: { Ast_required: 800 }, shear: { is_safe: true },
      },
    }],
  };
  assert.equal(projectLedgerRows(result)[0][5], "PASS");
  assert.equal(projectResultRows(result)[0][7], 800);
  assert.equal(projectPassportRows(result)[0][11], "8");
  const evidence = retainEvidence({
    ...result,
    bundle_hash: "b",
    source_table_hash: "s",
    mapping: { mapping_hash: "m" },
    library_content_identity: "l",
  });
  assert.deepEqual(evidence, {
    schema_version: "excel-retained-evidence/v1",
    bundle_hash: "b",
    source_table_hash: "s",
    mapping_hash: "m",
    library_content_identity: "l",
  });
  assert.match(reconciliationSummary(result), /1 source = 1 accepted/);
});

test("non-reconciling API output is rejected", () => {
  assert.throws(
    () => reconciliationSummary({ counts: { source_rows: 2, accepted_rows: 1, blocked_rows: 0, excluded_rows: 0 } }),
    /non-reconciling/,
  );
});
