import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import test from "node:test";

import {
  ETABS_BASELINE_TABLES,
  buildEtabsBaselineRequest,
  buildEtabsPilotRequest,
  buildPreviewRequest,
  buildReviewBundleExportRequest,
  buildRunRequest,
  downloadReviewBundle,
  getWorkbenchApi,
  normalizeCalculationMode,
  postWorkbenchApi,
  postReviewBundleApi,
  projectEtabsBaselineTables,
  projectEtabsPilotRows,
  projectLedgerRows,
  projectPassportRows,
  projectResultRows,
  reconciliationSummary,
  reviewBundleExportEligible,
  retainEvidence,
  sameSourceSnapshot,
  verifyEtabsBaselineTransport,
} from "../taskpane-core.mjs";

const etabsValues = {
  selectionKind: "COMBINATION",
  selectionName: "ULS-1",
  limit: "5",
  standard: "IS456",
  fck: "25",
  fy: "500",
  clearCover: "40",
  stirrupDiameter: "8",
  tensionBarDiameter: "20",
  compressionBarDiameter: "16",
  dDash: "40",
  nominalTopSteelRatio: "0.25",
  stirrupLegs: "2",
  stirrupSpacingSupport: "150",
  stirrupSpacingMid: "200",
};

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

test("ETABS pilot request makes result, material, depth, and detailing basis explicit", () => {
  const request = buildEtabsPilotRequest(etabsValues);
  assert.equal(request.schema_version, "etabs-beam-pilot/v1");
  assert.deepEqual(request.result_selection, {
    kind: "COMBINATION",
    name: "ULS-1",
  });
  assert.equal(request.design_basis.materials.fck_nmm2, 25);
  assert.equal(request.design_basis.effective_depth_basis.clear_cover_mm, 40);
  assert.equal(request.design_basis.detailing.stirrup_legs, 2);
  assert.equal(request.limit, 5);
  assert.throws(
    () => buildEtabsPilotRequest({ ...etabsValues, limit: "6" }),
    /must not exceed 5/,
  );
  assert.throws(
    () => buildEtabsPilotRequest({ ...etabsValues, selectionName: " " }),
    /exact ETABS case or combination/,
  );
});

test("ETABS projection preserves signed actions, design status, and full JSON", () => {
  const beam = {
    geometry: {
      frame_name: "B1", story: "L1", section_name: "R1", material_property: "M25",
      span_mm: 5000, b_mm: 300, D_mm: 500,
    },
    forces: {
      selection: { kind: "COMBINATION", name: "ULS-1" }, result_row_count: 3,
      governing_v2: { signed_value: -110, absolute_value: 110 },
      governing_t: { signed_value: 1.5, absolute_value: 1.5 },
      governing_m3: { signed_value: -150, absolute_value: 150 },
    },
    design_result: {
      envelope: { overall_status: "PASS" },
      design: { calculation: { flexure: { Ast_required: 900 }, shear: { spacing: 175 } } },
    },
  };
  const rows = projectEtabsPilotRows({
    schema_version: "etabs-beam-pilot/v1",
    pilot_status: "COMPLETED",
    beams: [beam],
  });
  assert.equal(rows[0][9], -110);
  assert.equal(rows[0][15], "PASS");
  assert.equal(rows[0][16], 900);
  assert.match(rows[0][18], /"frame_name":"B1"/);
});

function baselinePreflight() {
  return {
    schema_version: "etabs-beam-baseline-preflight/v1",
    observed_model_file: {
      model_path: "C:\\Models\\W2.edb",
      model_name: "W2.edb",
      sha256: HASH_A,
      byte_count: 100,
      modified_at_utc: "2026-08-29T05:00:00Z",
      observed_at_utc: "2026-08-29T05:01:00Z",
    },
    etabs_version: "ETABS 23.3.1",
    etabs_version_number: 23.31,
    model_locked: true,
    present_units_enum: 6,
    runtime_provenance: {
      adapter_version: "etabs-beam-baseline-adapter/v1",
      library_version: "0.24.0",
      library_content_identity: HASH_B,
      python_version: "3.11.15",
      platform: "Windows-11",
      com_provider: "comtypes/1.4.16;64-bit",
    },
    getter_matrix_sha256: HASH_C,
  };
}

function acceptedBaselineTransport() {
  const basis = '{"contract":"W2","value":1.0}';
  const baselineHash = createHash("sha256").update(basis).digest("hex");
  const file = baselinePreflight().observed_model_file;
  const station = {
    station_id: "station:1",
    member_id: "member:1",
    source_frame_name: "B1",
    source_row_index: 0,
    object_name: "B1",
    object_station_mm: 0,
    element_name: "E1",
    element_station_mm: 0,
    step_type: "Max",
    step_number: 0,
    p_kn: 1,
    v2_kn: 2,
    v3_kn: 3,
    t_knm: 4,
    m2_knm: 5,
    m3_knm: 6,
  };
  return {
    schema_version: "etabs-beam-baseline-transport/v1",
    build_result: {
      status: "ACCEPTED",
      baseline: {
        baseline_sha256: baselineHash,
        model: {
          model_name: "W2.edb",
          model_path: "C:\\Models\\W2.edb",
          file_evidence: { before_read: file, after_read: file },
          etabs_version: "ETABS 23.3.1",
          etabs_version_number: 23.31,
          model_locked: true,
        },
        units: {
          original_present_units_enum: 6,
          restored_present_units_enum: 6,
          restoration_status: "RESTORED",
        },
        stories: [{
          story_id: "story:1", name: "L1", elevation_mm: 0, height_mm: 3000,
          is_master_story: true, similar_to_story: "", splice_above: false,
          splice_height_mm: 0,
        }],
        frames: [{
          member_id: "member:1", source_unique_name: "B1", label: "B1-L1",
          story: "L1", kind: "BEAM",
          point_i: { point_name: "P1", x_mm: 0, y_mm: 0, z_mm: 0 },
          point_j: { point_name: "P2", x_mm: 5000, y_mm: 0, z_mm: 0 },
          local_axis: {
            local_axis_rotation_deg: 0, advanced_axes_active: false,
            direction_x: 1, direction_y: 0, direction_z: 0, length_mm: 5000,
          },
          section: {
            section_name: "R300x500", auto_select_list: "",
            material_property_label: "M25", depth_t3_mm: 500, width_t2_mm: 300,
          },
        }],
        connectivity: [{
          connection_id: "connection:1", kind: "BEAM_TO_COLUMN", point_name: "P1",
          member_a_id: "member:1", member_b_id: "member:2",
        }],
        results: [{
          member_id: "member:1", source_frame_name: "B1",
          selection_evidence: {
            selection: { kind: "COMBINATION", name: "ULS-1" },
            status: "COMBINATION_ROWS_REQUIRED", case_status_code: null,
          },
          stations: [station],
        }],
        dispositions: [{
          row_id: "row:1", row_kind: "FRAME", source_id: "B1",
          disposition: "ACCEPTED", reason_code: "FRAME_ACCEPTED_BEAM",
          canonical_id: "member:1", message: "Accepted beam.",
        }],
        runtime_provenance: baselinePreflight().runtime_provenance,
        getter_matrix_sha256: HASH_C,
        frame_analysis_verdict: "HELD_NOT_SUPPORTED",
      },
    },
    counts: {
      stories: 1,
      frames: 1,
      connectivity_rows: 1,
      result_sets: 1,
      result_station_rows: 1,
      disposition_rows: 1,
      projected_excel_rows: 7,
    },
    capacity: {
      max_projected_excel_rows: 100000,
      excel_json_chunk_characters: 15000,
    },
    baseline_hash_basis_json: basis,
    baseline_hash_basis_utf8_bytes: Buffer.byteLength(basis),
  };
}

test("W2 request is bound to a locked approved preflight and exact selection", () => {
  const request = buildEtabsBaselineRequest(baselinePreflight(), {
    selectionKind: "COMBINATION",
    selectionName: "ULS-1",
    approvedCopyConfirmed: true,
  });
  assert.equal(request.schema_version, "etabs-beam-baseline-run-request/v1");
  assert.equal(request.authorized_model_file.sha256, HASH_A);
  assert.equal(request.expected_runtime_provenance.library_content_identity, HASH_B);
  assert.deepEqual(request.result_selections, [{ kind: "COMBINATION", name: "ULS-1" }]);
  assert.equal(request.require_locked_model, true);
  assert.throws(
    () => buildEtabsBaselineRequest(baselinePreflight(), {
      selectionKind: "CASE", selectionName: "DEAD", approvedCopyConfirmed: false,
    }),
    /Confirm the exact copied model/,
  );
});

test("W2 projection verifies canonical bytes and reconciles every stable row", async () => {
  const transport = acceptedBaselineTransport();
  const verified = await verifyEtabsBaselineTransport(transport, { cryptoImpl: webcrypto });
  const projection = projectEtabsBaselineTables(transport);

  assert.equal(verified.baselineSha256, transport.build_result.baseline.baseline_sha256);
  assert.equal(projection.hashBasisJson, transport.baseline_hash_basis_json);
  assert.equal(projection.projectedRows, 7);
  assert.deepEqual(Object.keys(projection.tables), Object.keys(ETABS_BASELINE_TABLES));
  assert.equal(projection.tables.frames[0][0], "member:1");
  assert.equal(projection.tables.stations[0][0], "station:1");
  assert.equal(projection.tables.dispositions[0][0], "row:1");
  assert.equal(
    projection.tables.json.map((row) => row[5]).join(""),
    transport.baseline_hash_basis_json,
  );
});

test("W2 projection rejects blocked and duplicate-row responses before Excel", () => {
  const blocked = acceptedBaselineTransport();
  blocked.build_result.status = "BLOCKED";
  blocked.build_result.baseline = null;
  assert.throws(() => projectEtabsBaselineTables(blocked), /complete accepted/);

  const duplicate = acceptedBaselineTransport();
  duplicate.build_result.baseline.stories.push({
    ...duplicate.build_result.baseline.stories[0],
  });
  duplicate.counts.stories = 2;
  assert.throws(() => projectEtabsBaselineTables(duplicate), /duplicate stable row/);
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
