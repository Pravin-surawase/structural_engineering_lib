const TEMPLATE = Object.freeze({
  template_id: "structural-lib-rectangular-beam-workbench",
  template_version: "1.0",
  worksheet_name: "Beam_Workbench",
  table_name: "tbl_Beam_Workbench_V1",
});
const SHA256_PATTERN = /^[0-9a-f]{64}$/;

export const ETABS_PILOT_HEADERS = Object.freeze([
  "Frame",
  "Story",
  "Section",
  "Material",
  "Span (mm)",
  "b (mm)",
  "D (mm)",
  "Result selection",
  "Force rows",
  "V2 signed (kN)",
  "|V2| (kN)",
  "T signed (kN.m)",
  "|T| (kN.m)",
  "M3 signed (kN.m)",
  "|M3| (kN.m)",
  "Overall status",
  "Ast required (mm2)",
  "Shear spacing (mm)",
  "Canonical result JSON",
]);

export const ETABS_BASELINE_TABLES = Object.freeze({
  summary: Object.freeze({
    sheetName: "ETABS_W2_Summary",
    tableName: "tbl_ETABS_W2_Summary_V1",
    headers: Object.freeze([
      "Baseline SHA-256",
      "Model name",
      "Model path",
      "Model file SHA-256",
      "Model bytes",
      "Model modified UTC",
      "ETABS version",
      "ETABS version number",
      "Model locked",
      "Original units enum",
      "Restored units enum",
      "Stories",
      "Frames",
      "Connectivity rows",
      "Result sets",
      "Result stations",
      "Dispositions",
      "Projected Excel rows",
      "Library version",
      "Library identity",
      "Python version",
      "Platform",
      "COM provider",
      "Getter matrix SHA-256",
      "Frame analysis verdict",
      "Hash-basis UTF-8 bytes",
      "JSON chunks",
      "Review boundary",
    ]),
  }),
  stories: Object.freeze({
    sheetName: "ETABS_W2_Stories",
    tableName: "tbl_ETABS_W2_Stories_V1",
    headers: Object.freeze([
      "Story ID",
      "Name",
      "Elevation (mm)",
      "Height (mm)",
      "Master story",
      "Similar to story",
      "Splice above",
      "Splice height (mm)",
    ]),
  }),
  frames: Object.freeze({
    sheetName: "ETABS_W2_Frames",
    tableName: "tbl_ETABS_W2_Frames_V1",
    headers: Object.freeze([
      "Member ID",
      "Source unique name",
      "Label",
      "Story",
      "Kind",
      "Point I",
      "I X (mm)",
      "I Y (mm)",
      "I Z (mm)",
      "Point J",
      "J X (mm)",
      "J Y (mm)",
      "J Z (mm)",
      "Local rotation (deg)",
      "Advanced axes",
      "Direction X",
      "Direction Y",
      "Direction Z",
      "Length (mm)",
      "Section",
      "Auto-select list",
      "Material property label",
      "Depth T3 (mm)",
      "Width T2 (mm)",
    ]),
  }),
  connectivity: Object.freeze({
    sheetName: "ETABS_W2_Links",
    tableName: "tbl_ETABS_W2_Links_V1",
    headers: Object.freeze([
      "Connection ID",
      "Kind",
      "Point",
      "Member A ID",
      "Member B ID",
    ]),
  }),
  stations: Object.freeze({
    sheetName: "ETABS_W2_Stations",
    tableName: "tbl_ETABS_W2_Stations_V1",
    headers: Object.freeze([
      "Station ID",
      "Member ID",
      "Source frame",
      "Source row index",
      "Selection kind",
      "Selection name",
      "Selection status",
      "Case status code",
      "Object name",
      "Object station (mm)",
      "Element name",
      "Element station (mm)",
      "Step type",
      "Step number",
      "P (kN)",
      "V2 (kN)",
      "V3 (kN)",
      "T (kN.m)",
      "M2 (kN.m)",
      "M3 (kN.m)",
    ]),
  }),
  dispositions: Object.freeze({
    sheetName: "ETABS_W2_Dispositions",
    tableName: "tbl_ETABS_W2_Dispositions_V1",
    headers: Object.freeze([
      "Row ID",
      "Row kind",
      "Source ID",
      "Disposition",
      "Reason code",
      "Canonical ID",
      "Message",
    ]),
  }),
  json: Object.freeze({
    sheetName: "ETABS_W2_JSON",
    tableName: "tbl_ETABS_W2_JSON_V1",
    headers: Object.freeze([
      "Chunk ID",
      "Baseline SHA-256",
      "Chunk index",
      "Chunk count",
      "Hash-basis UTF-8 bytes",
      "Hash-basis JSON chunk",
    ]),
  }),
});

export const SETTINGS_KEYS = Object.freeze({
  workbookId: "excel_workbench_v1.workbook_instance_id",
  previousEvidence: "excel_workbench_v1.previous_evidence",
  stale: "excel_workbench_v1.stale",
});

export function normalizeCalculationMode(value) {
  const key = String(value ?? "").replaceAll("_", "").toLowerCase();
  if (key === "automatic") return "AUTOMATIC";
  if (key === "manual") return "MANUAL";
  if (
    key === "automaticexcepttables" ||
    key === "automaticexceptdatatables"
  ) {
    return "AUTOMATIC_EXCEPT_TABLES";
  }
  throw new Error(`Unsupported Excel calculation mode: ${value}`);
}

function requiredNumber(name, value, { minimum = 0, integer = false } = {}) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= minimum) {
    throw new Error(`${name} must be a finite number greater than ${minimum}.`);
  }
  if (integer && !Number.isInteger(parsed)) {
    throw new Error(`${name} must be an integer.`);
  }
  return parsed;
}

export function buildEtabsPilotRequest(values) {
  const selectionName = String(values.selectionName ?? "").trim();
  if (!selectionName) throw new Error("An exact ETABS case or combination name is required.");
  const selectionKind = String(values.selectionKind ?? "");
  if (!new Set(["CASE", "COMBINATION"]).has(selectionKind)) {
    throw new Error("ETABS result selection must be CASE or COMBINATION.");
  }
  const standard = String(values.standard ?? "");
  if (!new Set(["IS456", "IS13920"]).has(standard)) {
    throw new Error("Detailing standard must be IS456 or IS13920.");
  }
  const limit = requiredNumber("Beam limit", values.limit, { integer: true });
  if (limit > 5) throw new Error("Beam limit must not exceed 5.");
  const clearCover = requiredNumber("Clear cover", values.clearCover);
  const stirrupDiameter = requiredNumber("Stirrup diameter", values.stirrupDiameter);
  const tensionBarDiameter = requiredNumber("Tension bar diameter", values.tensionBarDiameter);
  const detailing = {
    standard,
    clear_cover_mm: clearCover,
    tension_bar_diameter_mm: tensionBarDiameter,
    compression_bar_diameter_mm: requiredNumber(
      "Compression bar diameter",
      values.compressionBarDiameter,
    ),
    nominal_top_steel_ratio: requiredNumber(
      "Nominal top steel ratio",
      values.nominalTopSteelRatio,
    ),
    stirrup_diameter_mm: stirrupDiameter,
    stirrup_legs: requiredNumber("Stirrup legs", values.stirrupLegs, { integer: true }),
    stirrup_spacing_support_mm: requiredNumber(
      "Support stirrup spacing",
      values.stirrupSpacingSupport,
    ),
    stirrup_spacing_mid_mm: requiredNumber(
      "Midspan stirrup spacing",
      values.stirrupSpacingMid,
    ),
  };
  return {
    schema_version: "etabs-beam-pilot/v1",
    result_selection: { kind: selectionKind, name: selectionName },
    design_basis: {
      materials: {
        fck_nmm2: requiredNumber("fck", values.fck),
        fy_nmm2: requiredNumber("fy", values.fy),
      },
      effective_depth_basis: {
        clear_cover_mm: clearCover,
        stirrup_diameter_mm: stirrupDiameter,
        tension_bar_diameter_mm: tensionBarDiameter,
      },
      d_dash_mm: requiredNumber("Compression steel depth d'", values.dDash),
      detailing,
    },
    limit,
  };
}

export function buildEtabsBaselineRequest(
  preflight,
  { selectionKind, selectionName, approvedCopyConfirmed },
) {
  if (preflight?.schema_version !== "etabs-beam-baseline-preflight/v1") {
    throw new Error("A current W2 baseline preflight is required.");
  }
  if (preflight.model_locked !== true) {
    throw new Error("The approved copied ETABS model must be locked.");
  }
  if (approvedCopyConfirmed !== true) {
    throw new Error("Confirm the exact copied model identity before reading results.");
  }
  const kind = String(selectionKind ?? "");
  const name = String(selectionName ?? "").trim();
  if (!new Set(["CASE", "COMBINATION"]).has(kind)) {
    throw new Error("ETABS result selection must be CASE or COMBINATION.");
  }
  if (!name) throw new Error("An exact ETABS case or combination name is required.");
  if (!SHA256_PATTERN.test(preflight.getter_matrix_sha256 ?? "")) {
    throw new Error("The W2 getter-matrix identity is invalid.");
  }
  if (!SHA256_PATTERN.test(preflight.observed_model_file?.sha256 ?? "")) {
    throw new Error("The copied-model identity is invalid.");
  }
  return {
    schema_version: "etabs-beam-baseline-run-request/v1",
    authorized_model_file: structuredClone(preflight.observed_model_file),
    expected_etabs_version: preflight.etabs_version,
    expected_etabs_version_number: preflight.etabs_version_number,
    expected_present_units_enum: preflight.present_units_enum,
    expected_runtime_provenance: structuredClone(preflight.runtime_provenance),
    expected_getter_matrix_sha256: preflight.getter_matrix_sha256,
    result_selections: [{ kind, name }],
    orientation_tolerance_mm: 1,
    require_locked_model: true,
    approved_copy_confirmed: true,
  };
}

function assertUniqueRows(rows, idIndex, label) {
  const ids = rows.map((row) => row[idIndex]);
  if (ids.some((value) => typeof value !== "string" || !value)) {
    throw new Error(`${label} contains a blank stable row identity.`);
  }
  if (new Set(ids).size !== ids.length) {
    throw new Error(`${label} contains duplicate stable row identities.`);
  }
}

function splitJsonByCodePoints(value, chunkCharacters) {
  const codePoints = Array.from(value);
  const chunks = [];
  for (let index = 0; index < codePoints.length; index += chunkCharacters) {
    chunks.push(codePoints.slice(index, index + chunkCharacters).join(""));
  }
  return chunks.length ? chunks : [""];
}

export async function verifyEtabsBaselineTransport(
  transport,
  { cryptoImpl = globalThis.crypto } = {},
) {
  const baseline = transport?.build_result?.baseline;
  const basis = transport?.baseline_hash_basis_json;
  if (
    transport?.schema_version !== "etabs-beam-baseline-transport/v1" ||
    transport?.build_result?.status !== "ACCEPTED" ||
    !baseline ||
    typeof basis !== "string" ||
    !SHA256_PATTERN.test(baseline.baseline_sha256 ?? "")
  ) {
    throw new Error("The W2 baseline response is blocked or incomplete.");
  }
  const bytes = new TextEncoder().encode(basis);
  if (bytes.length !== transport.baseline_hash_basis_utf8_bytes) {
    throw new Error("The W2 baseline hash-basis byte count does not match.");
  }
  const digest = await sha256Hex(bytes, { cryptoImpl });
  if (digest !== baseline.baseline_sha256) {
    throw new Error("The W2 baseline hash-basis digest does not match.");
  }
  return { baselineSha256: digest, utf8Bytes: bytes.length };
}

export function projectEtabsBaselineTables(transport) {
  const baseline = transport?.build_result?.baseline;
  if (
    transport?.schema_version !== "etabs-beam-baseline-transport/v1" ||
    transport?.build_result?.status !== "ACCEPTED" ||
    !baseline ||
    typeof transport.baseline_hash_basis_json !== "string"
  ) {
    throw new Error("Only a complete accepted W2 baseline can be written to Excel.");
  }
  if (
    baseline.model?.model_locked !== true ||
    baseline.units?.restoration_status !== "RESTORED" ||
    baseline.units?.original_present_units_enum !==
      baseline.units?.restored_present_units_enum ||
    baseline.frame_analysis_verdict !== "HELD_NOT_SUPPORTED"
  ) {
    throw new Error("The W2 lock, unit-restoration, or frame-analysis boundary is invalid.");
  }
  const capacity = transport.capacity;
  const chunks = splitJsonByCodePoints(
    transport.baseline_hash_basis_json,
    capacity.excel_json_chunk_characters,
  );
  const storyRows = baseline.stories.map((story) => [
    story.story_id,
    story.name,
    story.elevation_mm,
    story.height_mm,
    story.is_master_story,
    story.similar_to_story,
    story.splice_above,
    story.splice_height_mm,
  ]);
  const frameRows = baseline.frames.map((frame) => [
    frame.member_id,
    frame.source_unique_name,
    frame.label,
    frame.story,
    frame.kind,
    frame.point_i.point_name,
    frame.point_i.x_mm,
    frame.point_i.y_mm,
    frame.point_i.z_mm,
    frame.point_j.point_name,
    frame.point_j.x_mm,
    frame.point_j.y_mm,
    frame.point_j.z_mm,
    frame.local_axis.local_axis_rotation_deg,
    frame.local_axis.advanced_axes_active,
    frame.local_axis.direction_x,
    frame.local_axis.direction_y,
    frame.local_axis.direction_z,
    frame.local_axis.length_mm,
    frame.section.section_name,
    frame.section.auto_select_list,
    frame.section.material_property_label,
    frame.section.depth_t3_mm,
    frame.section.width_t2_mm,
  ]);
  const connectionRows = baseline.connectivity.map((item) => [
    item.connection_id,
    item.kind,
    item.point_name,
    item.member_a_id,
    item.member_b_id,
  ]);
  const stationRows = baseline.results.flatMap((result) =>
    result.stations.map((station) => [
      station.station_id,
      station.member_id,
      station.source_frame_name,
      station.source_row_index,
      result.selection_evidence.selection.kind,
      result.selection_evidence.selection.name,
      result.selection_evidence.status,
      result.selection_evidence.case_status_code,
      station.object_name,
      station.object_station_mm,
      station.element_name,
      station.element_station_mm,
      station.step_type,
      station.step_number,
      station.p_kn,
      station.v2_kn,
      station.v3_kn,
      station.t_knm,
      station.m2_knm,
      station.m3_knm,
    ]),
  );
  const dispositionRows = baseline.dispositions.map((item) => [
    item.row_id,
    item.row_kind,
    item.source_id,
    item.disposition,
    item.reason_code,
    item.canonical_id,
    item.message,
  ]);
  const jsonRows = chunks.map((chunk, index) => [
    `${baseline.baseline_sha256}:${String(index + 1).padStart(6, "0")}`,
    baseline.baseline_sha256,
    index + 1,
    chunks.length,
    transport.baseline_hash_basis_utf8_bytes,
    chunk,
  ]);
  assertUniqueRows(storyRows, 0, "ETABS stories");
  assertUniqueRows(frameRows, 0, "ETABS frames");
  assertUniqueRows(connectionRows, 0, "ETABS connectivity");
  assertUniqueRows(stationRows, 0, "ETABS stations");
  assertUniqueRows(dispositionRows, 0, "ETABS dispositions");
  assertUniqueRows(jsonRows, 0, "ETABS JSON chunks");
  const counts = transport.counts;
  if (
    storyRows.length !== counts.stories ||
    frameRows.length !== counts.frames ||
    connectionRows.length !== counts.connectivity_rows ||
    baseline.results.length !== counts.result_sets ||
    stationRows.length !== counts.result_station_rows ||
    dispositionRows.length !== counts.disposition_rows
  ) {
    throw new Error("The W2 baseline row counts do not reconcile.");
  }
  const projectedRows =
    1 +
    storyRows.length +
    frameRows.length +
    connectionRows.length +
    stationRows.length +
    dispositionRows.length +
    jsonRows.length;
  if (projectedRows > capacity.max_projected_excel_rows) {
    throw new Error("The W2 baseline exceeds the controlled Excel row limit.");
  }
  if (projectedRows !== counts.projected_excel_rows) {
    throw new Error("The W2 projected Excel row count does not reconcile.");
  }
  const file = baseline.model.file_evidence.after_read;
  const runtime = baseline.runtime_provenance;
  const summaryRows = [[
    baseline.baseline_sha256,
    baseline.model.model_name,
    baseline.model.model_path,
    file.sha256,
    file.byte_count,
    file.modified_at_utc,
    baseline.model.etabs_version,
    baseline.model.etabs_version_number,
    baseline.model.model_locked,
    baseline.units.original_present_units_enum,
    baseline.units.restored_present_units_enum,
    counts.stories,
    counts.frames,
    counts.connectivity_rows,
    counts.result_sets,
    counts.result_station_rows,
    counts.disposition_rows,
    projectedRows,
    runtime.library_version,
    runtime.library_content_identity,
    runtime.python_version,
    runtime.platform,
    runtime.com_provider,
    baseline.getter_matrix_sha256,
    baseline.frame_analysis_verdict,
    transport.baseline_hash_basis_utf8_bytes,
    jsonRows.length,
    "QUALIFIED_STRUCTURAL_ENGINEER_REVIEW_REQUIRED",
  ]];
  return {
    baselineSha256: baseline.baseline_sha256,
    projectedRows,
    tables: {
      summary: summaryRows,
      stories: storyRows,
      frames: frameRows,
      connectivity: connectionRows,
      stations: stationRows,
      dispositions: dispositionRows,
      json: jsonRows,
    },
  };
}

export function buildPreviewRequest({
  workbookInstanceId,
  headers,
  rows,
  firstDataRowNumber,
  locale,
  calculationMode,
}) {
  if (!Array.isArray(headers) || headers.length === 0) {
    throw new Error("The selected Excel table has no headers.");
  }
  if (!Array.isArray(rows)) {
    throw new Error("The selected Excel table rows are unavailable.");
  }
  return {
    schema_version: "excel-workbook-preview-request/v1",
    selection: {
      workbook_instance_id: workbookInstanceId,
      template_id: TEMPLATE.template_id,
      template_version: TEMPLATE.template_version,
      worksheet_name: TEMPLATE.worksheet_name,
      table_name: TEMPLATE.table_name,
      first_data_row_number: firstDataRowNumber,
      locale: locale || "en-IN",
      decimal_separator: ".",
      calculation_mode: normalizeCalculationMode(calculationMode),
      unit_system: "IS456",
      trust_mode: "MACRO_FREE_OFFICE_JS",
    },
    headers: [...headers],
    rows: rows.map((row) => [...row]),
  };
}

export function buildRunRequest(previewRequest, confirmedMappingHash) {
  if (!SHA256_PATTERN.test(String(confirmedMappingHash ?? ""))) {
    throw new Error("A reviewed 64-character mapping hash is required.");
  }
  return {
    ...previewRequest,
    schema_version: "excel-workbook-run-request/v1",
    confirmed_mapping_hash: confirmedMappingHash,
  };
}

export function buildReviewBundleExportRequest(
  currentRequest,
  previousEvidence,
  confirmedMappingHash,
) {
  if (!currentRequest || currentRequest.schema_version !== "excel-workbook-preview-request/v1") {
    throw new Error("A current selected-table snapshot is required for export.");
  }
  if (
    !previousEvidence ||
    previousEvidence.schema_version !== "excel-retained-evidence/v1" ||
    ![
      previousEvidence.bundle_hash,
      previousEvidence.source_table_hash,
      previousEvidence.mapping_hash,
      previousEvidence.library_content_identity,
    ].every((value) => SHA256_PATTERN.test(String(value ?? "")))
  ) {
    throw new Error("Complete retained result evidence is required for export.");
  }
  if (!SHA256_PATTERN.test(String(confirmedMappingHash ?? ""))) {
    throw new Error("A confirmed current mapping hash is required for export.");
  }
  return {
    schema_version: "excel-review-bundle-export-request/v1",
    current_request: currentRequest,
    previous_evidence: previousEvidence,
    confirmed_mapping_hash: confirmedMappingHash,
  };
}

export function sameSourceSnapshot(left, right) {
  if (!left || !right) return false;
  return JSON.stringify(left) === JSON.stringify(right);
}

export function reviewBundleExportEligible({
  workbookSurfaceAvailable,
  busy,
  previousEvidence,
  stale,
  freshnessVerified,
}) {
  return Boolean(
    workbookSurfaceAvailable &&
      !busy &&
      previousEvidence &&
      !stale &&
      freshnessVerified,
  );
}

export function unwrapApiResponse(body) {
  if (!body || body.success !== true || body.data == null) {
    const message = body?.error?.message || "The local API rejected the request.";
    throw new Error(message);
  }
  return body.data;
}

export async function postWorkbenchApi(
  baseUrl,
  path,
  payload,
  { token = "", fetchImpl = globalThis.fetch } = {},
) {
  const root = String(baseUrl || "").replace(/\/$/, "");
  if (!root) throw new Error("The local API base URL is required.");
  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  if (token.trim()) headers.Authorization = `Bearer ${token.trim()}`;
  const response = await fetchImpl(`${root}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(`The local API returned non-JSON HTTP ${response.status}.`);
  }
  if (!response.ok) {
    throw new Error(body?.error?.message || `The local API returned HTTP ${response.status}.`);
  }
  return unwrapApiResponse(body);
}

export async function getWorkbenchApi(
  baseUrl,
  path,
  { token = "", fetchImpl = globalThis.fetch } = {},
) {
  const root = String(baseUrl || "").replace(/\/$/, "");
  if (!root) throw new Error("The local API base URL is required.");
  const headers = { Accept: "application/json" };
  if (token.trim()) headers.Authorization = `Bearer ${token.trim()}`;
  const response = await fetchImpl(`${root}${path}`, { method: "GET", headers });
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(`The local API returned non-JSON HTTP ${response.status}.`);
  }
  if (!response.ok) {
    throw new Error(body?.error?.message || `The local API returned HTTP ${response.status}.`);
  }
  return unwrapApiResponse(body);
}

function responseHeader(response, name) {
  return response.headers?.get?.(name) ?? null;
}

export function reviewBundleFilename(contentDisposition, resultBundleHash) {
  if (!SHA256_PATTERN.test(String(resultBundleHash ?? ""))) {
    throw new Error("The review-bundle response has an invalid result identity.");
  }
  const expected = `e1-review-bundle-${resultBundleHash}.json`;
  const match = /^attachment;\s*filename="([A-Za-z0-9._-]+)"$/i.exec(
    String(contentDisposition ?? ""),
  );
  if (!match || match[1] !== expected) {
    throw new Error("The review-bundle response has an invalid attachment filename.");
  }
  return expected;
}

export async function sha256Hex(bytes, { cryptoImpl = globalThis.crypto } = {}) {
  if (!cryptoImpl?.subtle) throw new Error("WebCrypto SHA-256 is unavailable.");
  const view = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  const digest = await cryptoImpl.subtle.digest("SHA-256", view);
  return Array.from(new Uint8Array(digest), (value) =>
    value.toString(16).padStart(2, "0"),
  ).join("");
}

export async function postReviewBundleApi(
  baseUrl,
  path,
  payload,
  { token = "", fetchImpl = globalThis.fetch, cryptoImpl = globalThis.crypto } = {},
) {
  const root = String(baseUrl || "").replace(/\/$/, "");
  if (!root) throw new Error("The local API base URL is required.");
  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  if (token.trim()) headers.Authorization = `Bearer ${token.trim()}`;
  const response = await fetchImpl(`${root}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error(`The local API returned non-JSON HTTP ${response.status}.`);
    }
    throw new Error(body?.error?.message || `The local API returned HTTP ${response.status}.`);
  }

  if (!String(responseHeader(response, "Content-Type") ?? "").includes("application/json")) {
    throw new Error("The review-bundle response is not JSON.");
  }
  const fileHash = responseHeader(response, "X-E1-File-SHA256");
  const reviewBundleHash = responseHeader(response, "X-E1-Review-Bundle-Hash");
  const resultBundleHash = responseHeader(response, "X-E1-Result-Bundle-Hash");
  if (![fileHash, reviewBundleHash, resultBundleHash].every((value) => SHA256_PATTERN.test(String(value ?? "")))) {
    throw new Error("The review-bundle response is missing a valid identity header.");
  }
  if (resultBundleHash !== payload.previous_evidence?.bundle_hash) {
    throw new Error("The exported result identity does not match retained evidence.");
  }

  const bytes = new Uint8Array(await response.arrayBuffer());
  const actualFileHash = await sha256Hex(bytes, { cryptoImpl });
  if (actualFileHash !== fileHash) {
    throw new Error("The downloaded review-bundle bytes failed SHA-256 verification.");
  }
  let bundle;
  try {
    bundle = JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    throw new Error("The downloaded review bundle is not valid JSON.");
  }
  if (
    bundle?.schema_version !== "excel-review-bundle/v1" ||
    bundle?.export_disposition !== "EVIDENCE_FOR_QUALIFIED_REVIEW" ||
    bundle?.freshness_check?.freshness_status !== "CURRENT" ||
    bundle?.result?.qualified_review_required !== true ||
    bundle?.review_bundle_hash !== reviewBundleHash ||
    bundle?.result?.bundle_hash !== resultBundleHash
  ) {
    throw new Error("The downloaded review-bundle content failed identity validation.");
  }
  return {
    bytes,
    fileHash,
    reviewBundleHash,
    resultBundleHash,
    filename: reviewBundleFilename(
      responseHeader(response, "Content-Disposition"),
      resultBundleHash,
    ),
  };
}

export function downloadReviewBundle(
  download,
  {
    documentImpl = globalThis.document,
    urlImpl = globalThis.URL,
    BlobImpl = globalThis.Blob,
  } = {},
) {
  if (!download?.bytes || !download?.filename) {
    throw new Error("Verified review-bundle bytes are required for download.");
  }
  const blob = new BlobImpl([download.bytes], { type: "application/json" });
  const href = urlImpl.createObjectURL(blob);
  const anchor = documentImpl.createElement("a");
  anchor.href = href;
  anchor.download = download.filename;
  anchor.hidden = true;
  documentImpl.body.append(anchor);
  try {
    anchor.click();
  } finally {
    anchor.remove();
    urlImpl.revokeObjectURL(href);
  }
}

export function projectMappingRows(preview) {
  const rows = preview.mapped_fields.map((field) => [
    field.canonical_field,
    field.source_header,
    "READY",
    `Column ${field.source_column_index + 1}`,
  ]);
  for (const issue of preview.issues) {
    rows.push([issue.path, "-", "BLOCKED", `${issue.code}: ${issue.message}`]);
  }
  return rows;
}

export function projectLedgerRows(result) {
  return result.row_ledger.map((row) => [
    row.source_row_number,
    row.row_id,
    row.beam_id,
    row.disposition,
    row.issues.map((issue) => issue.code).join(", "),
    row.result_envelope?.overall_status ?? row.disposition,
    row.raw_row_hash,
    row.passport?.result_hash ?? null,
    row.passport?.passport_hash ?? null,
  ]);
}

export function projectResultRows(result) {
  return result.row_ledger
    .filter((row) => row.result != null)
    .map((row) => [
      row.row_id,
      row.beam_id,
      row.result.case_id,
      row.result.result_envelope?.overall_status ?? null,
      row.result.Mu_knm,
      row.result.Vu_kn,
      row.result.effective_depth_resolution?.d_mm ?? null,
      row.result.flexure?.Ast_required ?? null,
      row.result.shear?.is_safe === true
        ? "PASS"
        : row.result.shear?.is_safe === false
          ? "FAIL"
          : null,
      JSON.stringify(row.result),
    ]);
}

export function projectEtabsPilotRows(result) {
  if (
    result?.schema_version !== "etabs-beam-pilot/v1" ||
    result?.pilot_status !== "COMPLETED" ||
    !Array.isArray(result?.beams) ||
    result.beams.length === 0
  ) {
    throw new Error("The ETABS pilot response is incomplete.");
  }
  return result.beams.map((item) => {
    const geometry = item.geometry;
    const forces = item.forces;
    const design = item.design_result;
    return [
      geometry.frame_name,
      geometry.story,
      geometry.section_name,
      geometry.material_property,
      geometry.span_mm,
      geometry.b_mm,
      geometry.D_mm,
      `${forces.selection.kind}:${forces.selection.name}`,
      forces.result_row_count,
      forces.governing_v2.signed_value,
      forces.governing_v2.absolute_value,
      forces.governing_t.signed_value,
      forces.governing_t.absolute_value,
      forces.governing_m3.signed_value,
      forces.governing_m3.absolute_value,
      design?.envelope?.overall_status ?? null,
      design?.design?.calculation?.flexure?.Ast_required ?? null,
      design?.design?.calculation?.shear?.spacing ?? null,
      JSON.stringify(item),
    ];
  });
}

export function projectPassportRows(result) {
  return result.row_ledger
    .filter((row) => row.passport != null)
    .map((row) => [
      row.passport.row_id,
      row.passport.beam_id,
      row.passport.case_id,
      row.passport.raw_row_hash,
      row.passport.normalized_input_hash,
      row.passport.calculation_identity,
      row.passport.result_hash,
      row.passport.library_version,
      row.passport.library_content_identity,
      row.passport.workbook_selection_hash,
      row.passport.mapping_hash,
      row.passport.passport_hash,
    ]);
}

export function retainEvidence(result) {
  return {
    schema_version: "excel-retained-evidence/v1",
    bundle_hash: result.bundle_hash,
    source_table_hash: result.source_table_hash,
    mapping_hash: result.mapping.mapping_hash,
    library_content_identity: result.library_content_identity,
  };
}

export function reconciliationSummary(result) {
  const counts = result.counts;
  if (
    counts.source_rows !==
    counts.accepted_rows + counts.blocked_rows + counts.excluded_rows
  ) {
    throw new Error("The API returned a non-reconciling row count.");
  }
  return `${counts.source_rows} source = ${counts.accepted_rows} accepted + ${counts.blocked_rows} blocked + ${counts.excluded_rows} excluded`;
}
