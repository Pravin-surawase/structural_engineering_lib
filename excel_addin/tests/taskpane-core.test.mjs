import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import test from "node:test";

import {
  buildPreviewRequest,
  buildReviewBundleExportRequest,
  buildRunRequest,
  downloadReviewBundle,
  getWorkbenchApi,
  normalizeCalculationMode,
  postWorkbenchApi,
  postReviewBundleApi,
  projectLedgerRows,
  projectPassportRows,
  projectResultRows,
  reconciliationSummary,
  reviewBundleExportEligible,
  retainEvidence,
  sameSourceSnapshot,
} from "../taskpane-core.mjs";

const HASH_A = "a".repeat(64);
const HASH_B = "b".repeat(64);
const HASH_C = "c".repeat(64);
const HASH_D = "d".repeat(64);

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

test("review-bundle request requires complete retained and mapping identities", () => {
  const current = buildPreviewRequest(snapshot);
  const evidence = {
    schema_version: "excel-retained-evidence/v1",
    bundle_hash: HASH_A,
    source_table_hash: HASH_B,
    mapping_hash: HASH_C,
    library_content_identity: HASH_D,
  };
  assert.throws(
    () => buildReviewBundleExportRequest(current, null, HASH_C),
    /retained result evidence/,
  );
  assert.throws(
    () => buildReviewBundleExportRequest(current, evidence, "bad"),
    /mapping hash/,
  );
  assert.deepEqual(buildReviewBundleExportRequest(current, evidence, HASH_C), {
    schema_version: "excel-review-bundle-export-request/v1",
    current_request: current,
    previous_evidence: evidence,
    confirmed_mapping_hash: HASH_C,
  });
});

test("review-bundle eligibility is fail-closed for busy, stale, and reopened state", () => {
  const ready = {
    workbookSurfaceAvailable: true,
    busy: false,
    previousEvidence: { bundle_hash: HASH_A },
    stale: false,
    freshnessVerified: true,
  };
  assert.equal(reviewBundleExportEligible(ready), true);
  assert.equal(reviewBundleExportEligible({ ...ready, busy: true }), false);
  assert.equal(reviewBundleExportEligible({ ...ready, stale: true }), false);
  assert.equal(reviewBundleExportEligible({ ...ready, previousEvidence: null }), false);
  assert.equal(
    reviewBundleExportEligible({ ...ready, freshnessVerified: false }),
    false,
  );
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

function headerBag(values) {
  const normalized = new Map(
    Object.entries(values).map(([key, value]) => [key.toLowerCase(), value]),
  );
  return { get: (name) => normalized.get(name.toLowerCase()) ?? null };
}

function reviewBundleResponse({ fileHashOverride } = {}) {
  const bundle = {
    schema_version: "excel-review-bundle/v1",
    export_disposition: "EVIDENCE_FOR_QUALIFIED_REVIEW",
    freshness_check: { freshness_status: "CURRENT" },
    result: { qualified_review_required: true, bundle_hash: HASH_A },
    review_bundle_hash: HASH_B,
  };
  const bytes = new TextEncoder().encode(`${JSON.stringify(bundle)}\n`);
  const fileHash = createHash("sha256").update(bytes).digest("hex");
  return {
    ok: true,
    status: 200,
    headers: headerBag({
      "Content-Type": "application/json",
      "Content-Disposition": `attachment; filename="e1-review-bundle-${HASH_A}.json"`,
      "X-E1-File-SHA256": fileHashOverride ?? fileHash,
      "X-E1-Review-Bundle-Hash": HASH_B,
      "X-E1-Result-Bundle-Hash": HASH_A,
    }),
    arrayBuffer: async () => bytes.buffer.slice(
      bytes.byteOffset,
      bytes.byteOffset + bytes.byteLength,
    ),
  };
}

test("review-bundle download verifies exact bytes and logical identities", async () => {
  const payload = { previous_evidence: { bundle_hash: HASH_A } };
  const download = await postReviewBundleApi(
    "/api/v1",
    "/review-bundle",
    payload,
    { fetchImpl: async () => reviewBundleResponse(), cryptoImpl: webcrypto },
  );

  assert.equal(download.resultBundleHash, HASH_A);
  assert.equal(download.reviewBundleHash, HASH_B);
  assert.equal(download.filename, `e1-review-bundle-${HASH_A}.json`);
  assert.equal(download.fileHash.length, 64);
  await assert.rejects(
    postReviewBundleApi("/api/v1", "/review-bundle", payload, {
      fetchImpl: async () => reviewBundleResponse({ fileHashOverride: HASH_D }),
      cryptoImpl: webcrypto,
    }),
    /failed SHA-256/,
  );
});

test("verified review bundle triggers exactly one temporary download", () => {
  let clicks = 0;
  let removals = 0;
  let appends = 0;
  let revocations = 0;
  const anchor = {
    click() { clicks += 1; },
    remove() { removals += 1; },
  };
  const documentImpl = {
    createElement: () => anchor,
    body: { append: () => { appends += 1; } },
  };
  const urlImpl = {
    createObjectURL: () => "blob:e1",
    revokeObjectURL: () => { revocations += 1; },
  };
  class FakeBlob {
    constructor(parts, options) {
      this.parts = parts;
      this.options = options;
    }
  }

  downloadReviewBundle(
    { bytes: new Uint8Array([1, 2, 3]), filename: `e1-review-bundle-${HASH_A}.json` },
    { documentImpl, urlImpl, BlobImpl: FakeBlob },
  );

  assert.equal(appends, 1);
  assert.equal(clicks, 1);
  assert.equal(removals, 1);
  assert.equal(revocations, 1);
});
