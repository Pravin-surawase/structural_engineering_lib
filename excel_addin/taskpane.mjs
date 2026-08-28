import {
  SETTINGS_KEYS,
  buildEtabsPilotRequest,
  buildPreviewRequest,
  buildReviewBundleExportRequest,
  buildRunRequest,
  downloadReviewBundle,
  getWorkbenchApi,
  postWorkbenchApi,
  postReviewBundleApi,
  projectEtabsPilotRows,
  projectLedgerRows,
  projectMappingRows,
  projectPassportRows,
  projectResultRows,
  reconciliationSummary,
  reviewBundleExportEligible,
  retainEvidence,
  sameSourceSnapshot,
} from "./taskpane-core.mjs";
import {
  ensureWorkbookId,
  inspectWorkbookSurface,
  officeErrorDetail,
  registerWorksheetChange,
  saveDocumentSettings,
  writeEtabsPilotResults,
} from "./taskpane-office.mjs";

const INPUT_SHEET = "Beam_Workbench";
const INPUT_TABLE = "tbl_Beam_Workbench_V1";
const API_ROOT = `${window.location.origin}/api/v1`;

const state = {
  workbookId: null,
  previewRequest: null,
  mapping: null,
  previousEvidence: null,
  definition: null,
  stale: true,
  freshnessVerified: false,
  confirmedMappingHash: null,
  inputRevision: 0,
  eventRegistered: false,
  workbookSurfaceAvailable: false,
  etabsBridgeStatus: null,
  etabsConnected: false,
};

const ui = {};

function setStatus(kind, title, detail = "") {
  ui.status.className = `status ${kind}`;
  ui.statusTitle.textContent = title;
  ui.statusDetail.textContent = detail;
}

function setBusy(busy) {
  const unavailable = !state.workbookSurfaceAvailable;
  ui.preview.disabled = busy || unavailable;
  ui.freshness.disabled = busy || unavailable || !state.previousEvidence;
  ui.review.disabled = busy || unavailable || !state.mapping || state.mapping.is_blocked;
  ui.run.disabled = busy || unavailable || !ui.review.checked || state.stale;
  ui.export.disabled = !reviewBundleExportEligible({
    workbookSurfaceAvailable: !unavailable,
    busy,
    previousEvidence: state.previousEvidence,
    stale: state.stale,
    freshnessVerified: state.freshnessVerified,
  });
  ui.status.setAttribute("aria-busy", busy ? "true" : "false");
}

function setPilotStatus(kind, title, detail = "") {
  ui.etabsStatus.className = `status ${kind}`;
  ui.etabsStatusTitle.textContent = title;
  ui.etabsStatusDetail.textContent = detail;
}

function setPilotBusy(busy) {
  ui.etabsConnect.disabled =
    busy || state.etabsBridgeStatus?.bridge_status !== "READY_TO_CONNECT";
  ui.etabsRun.disabled = busy || !state.etabsConnected;
  ui.etabsStatus.setAttribute("aria-busy", busy ? "true" : "false");
}

function captureEtabsPilotValues() {
  return {
    selectionKind: ui.etabsSelectionKind.value,
    selectionName: ui.etabsSelectionName.value,
    limit: ui.etabsLimit.value,
    standard: ui.etabsStandard.value,
    fck: ui.etabsFck.value,
    fy: ui.etabsFy.value,
    clearCover: ui.etabsClearCover.value,
    stirrupDiameter: ui.etabsStirrupDiameter.value,
    tensionBarDiameter: ui.etabsTensionBarDiameter.value,
    compressionBarDiameter: ui.etabsCompressionBarDiameter.value,
    dDash: ui.etabsDDash.value,
    nominalTopSteelRatio: ui.etabsTopRatio.value,
    stirrupLegs: ui.etabsStirrupLegs.value,
    stirrupSpacingSupport: ui.etabsSpacingSupport.value,
    stirrupSpacingMid: ui.etabsSpacingMid.value,
  };
}

async function refreshEtabsStatus() {
  setPilotBusy(true);
  try {
    const status = await getWorkbenchApi(
      API_ROOT,
      "/etabs-bridge/v1/status",
      { token: ui.token.value },
    );
    state.etabsBridgeStatus = status;
    state.etabsConnected = false;
    const available = status.bridge_status === "READY_TO_CONNECT";
    setPilotStatus(
      available ? "hold" : "blocked",
      status.bridge_status,
      available
        ? `Python library ${status.library_version} is ready. Open the copied model in ETABS, then connect.`
        : status.issues.join(" "),
    );
  } catch (error) {
    state.etabsBridgeStatus = null;
    state.etabsConnected = false;
    setPilotStatus("blocked", "BRIDGE STATUS FAILED", error.message);
  } finally {
    setPilotBusy(false);
  }
}

async function connectEtabs() {
  setPilotBusy(true);
  setPilotStatus("working", "CONNECTING", "Attaching to an already-open ETABS model.");
  try {
    const connection = await postWorkbenchApi(
      API_ROOT,
      "/etabs-bridge/v1/connect",
      {},
      { token: ui.token.value },
    );
    state.etabsConnected = true;
    setPilotStatus(
      "ready",
      "ETABS CONNECTED",
      `${connection.model.model_name} · ${connection.model.etabs_version} · library ${connection.library_version}`,
    );
  } catch (error) {
    state.etabsConnected = false;
    setPilotStatus("blocked", "ETABS CONNECTION FAILED", error.message);
  } finally {
    setPilotBusy(false);
  }
}

async function runEtabsPilot() {
  setPilotBusy(true);
  setPilotStatus(
    "working",
    "READING ETABS",
    "Extracting the exact selected result and running canonical beam design.",
  );
  try {
    const request = buildEtabsPilotRequest(captureEtabsPilotValues());
    const result = await postWorkbenchApi(
      API_ROOT,
      "/etabs-bridge/v1/beam-pilot",
      request,
      { token: ui.token.value },
    );
    const rows = projectEtabsPilotRows(result);
    const write = await writeEtabsPilotResults(Excel, rows);
    setPilotStatus(
      "ready",
      "PILOT COMPLETED",
      `${result.designed_beam_count} beam(s) from ${result.model.model_name} written to ${write.sheetName} (${write.disposition}). Qualified review is required.`,
    );
  } catch (error) {
    setPilotStatus("blocked", "PILOT BLOCKED", officeErrorDetail(error));
  } finally {
    setPilotBusy(false);
  }
}

async function persistEvidence(evidence, stale) {
  const settings = Office.context.document.settings;
  settings.set(SETTINGS_KEYS.previousEvidence, evidence);
  settings.set(SETTINGS_KEYS.stale, stale);
  await saveDocumentSettings(Office);
}

async function captureInput() {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(INPUT_SHEET);
    const table = sheet.tables.getItem(INPUT_TABLE);
    const header = table.getHeaderRowRange();
    const body = table.getDataBodyRange();
    const application = context.workbook.application;
    header.load(["values", "rowIndex"]);
    body.load("values");
    application.load("calculationMode");
    await context.sync();
    return buildPreviewRequest({
      workbookInstanceId: state.workbookId,
      headers: header.values[0],
      rows: body.values,
      firstDataRowNumber: header.rowIndex + 2,
      locale: Office.context.contentLanguage || "en-IN",
      calculationMode: application.calculationMode,
    });
  });
}

async function replaceTableRows(context, sheetName, tableName, rows) {
  const sheet = context.workbook.worksheets.getItem(sheetName);
  const table = sheet.tables.getItem(tableName);
  const header = table.getHeaderRowRange();
  header.load(["rowIndex", "columnIndex", "columnCount"]);
  await context.sync();
  const rowCount = Math.max(rows.length, 1);
  table.resize(
    sheet.getRangeByIndexes(
      header.rowIndex,
      header.columnIndex,
      rowCount + 1,
      header.columnCount,
    ),
  );
  await context.sync();
  const body = table.getDataBodyRange();
  body.values = rows.length
    ? rows
    : [Array.from({ length: header.columnCount }, () => null)];
}

async function writeMapping(preview) {
  await Excel.run(async (context) => {
    await replaceTableRows(
      context,
      "Mapping_Preview",
      "tbl_Mapping_Preview_V1",
      projectMappingRows(preview),
    );
    await context.sync();
  });
}

async function writeRunResult(result) {
  await Excel.run(async (context) => {
    const specs = [
      ["Row_Ledger", "tbl_Row_Ledger_V1", projectLedgerRows(result)],
      ["Results", "tbl_Results_V1", projectResultRows(result)],
      ["Passports", "tbl_Passports_V1", projectPassportRows(result)],
    ].map(([sheetName, tableName, rows]) => {
      const sheet = context.workbook.worksheets.getItem(sheetName);
      const table = sheet.tables.getItem(tableName);
      const header = table.getHeaderRowRange();
      header.load(["rowIndex", "columnIndex", "columnCount"]);
      return { sheet, table, header, rows };
    });
    await context.sync();
    for (const spec of specs) {
      spec.table.resize(
        spec.sheet.getRangeByIndexes(
          spec.header.rowIndex,
          spec.header.columnIndex,
          Math.max(spec.rows.length, 1) + 1,
          spec.header.columnCount,
        ),
      );
    }
    await context.sync();
    for (const spec of specs) {
      spec.table.getDataBodyRange().values = spec.rows.length
        ? spec.rows
        : [Array.from({ length: spec.header.columnCount }, () => null)];
    }
    await context.sync();
  });
}

let staleTimer;
function markStale() {
  state.inputRevision += 1;
  state.stale = true;
  state.freshnessVerified = false;
  state.confirmedMappingHash = null;
  state.previewRequest = null;
  state.mapping = null;
  ui.review.checked = false;
  ui.mapping.textContent = "Mapping review required after the latest input edit.";
  ui.exportDetail.textContent = "Export is disabled until the edited table is recalculated.";
  setStatus("hold", "STALE", "Preview and review the mapping before running again.");
  setBusy(false);
  clearTimeout(staleTimer);
  staleTimer = setTimeout(() => {
    if (state.previousEvidence) void persistEvidence(state.previousEvidence, true);
  }, 300);
}

async function registerInputChange() {
  if (state.eventRegistered) return;
  await registerWorksheetChange(Excel, {
    worksheetName: INPUT_SHEET,
    handler: markStale,
  });
  state.eventRegistered = true;
}

async function previewMapping() {
  setBusy(true);
  setStatus("working", "Reading selected table", "No calculation is running yet.");
  try {
    const request = await captureInput();
    const preview = await postWorkbenchApi(
      API_ROOT,
      "/excel-workbench/v1/mapping-preview",
      request,
      { token: ui.token.value },
    );
    await writeMapping(preview);
    state.previewRequest = request;
    state.mapping = preview;
    state.stale = true;
    state.freshnessVerified = false;
    state.confirmedMappingHash = null;
    ui.review.checked = false;
    ui.exportDetail.textContent = "Run a reviewed current mapping before export.";
    ui.mapping.textContent = preview.is_blocked
      ? `${preview.issues.length} mapping issue(s); Run remains blocked.`
      : `${preview.mapped_fields.length} fields mapped. Hash ${preview.mapping_hash}`;
    ui.context.textContent = `${request.selection.workbook_instance_id} · ${request.selection.worksheet_name}/${request.selection.table_name} · ${request.rows.length} source rows · ${request.selection.unit_system} · ${request.selection.calculation_mode}`;
    setStatus(
      preview.is_blocked ? "blocked" : "hold",
      preview.is_blocked ? "MAPPING BLOCKED" : "REVIEW REQUIRED",
      preview.is_blocked
        ? "Correct the source headers and preview again."
        : "Confirm that the displayed mapping is correct.",
    );
  } catch (error) {
    setStatus("blocked", "PREVIEW FAILED", error.message);
  } finally {
    setBusy(false);
  }
}

function mappingReviewChanged() {
  state.stale = !ui.review.checked;
  setStatus(
    ui.review.checked ? "ready" : "hold",
    ui.review.checked ? "READY TO RUN" : "REVIEW REQUIRED",
    ui.review.checked
      ? "Run will use the current selected-table snapshot and reviewed mapping hash."
      : "Confirm the mapping before calculation.",
  );
  setBusy(false);
}

async function runCalculation() {
  setBusy(true);
  setStatus("working", "Running canonical library", "Excel is not calculating structural formulas.");
  try {
    const current = await captureInput();
    if (!sameSourceSnapshot(current, state.previewRequest)) {
      markStale();
      throw new Error("The selected table changed after preview. Preview it again.");
    }
    const request = buildRunRequest(current, state.mapping?.mapping_hash);
    const result = await postWorkbenchApi(
      API_ROOT,
      "/excel-workbench/v1/run",
      request,
      { token: ui.token.value },
    );
    const summary = reconciliationSummary(result);
    await writeRunResult(result);
    state.previousEvidence = retainEvidence(result);
    state.stale = false;
    state.freshnessVerified = true;
    state.confirmedMappingHash = result.mapping.mapping_hash;
    await persistEvidence(state.previousEvidence, false);
    ui.exportDetail.textContent = "The current result is eligible for deterministic evidence export.";
    setStatus("ready", "RESULT CURRENT", `${summary}. Qualified review remains required.`);
  } catch (error) {
    setStatus("blocked", "RUN FAILED", error.message);
  } finally {
    setBusy(false);
  }
}

async function checkFreshness() {
  setBusy(true);
  setStatus("working", "Checking freshness", "Comparing retained evidence with the selected table.");
  try {
    const current = await captureInput();
    const check = await postWorkbenchApi(
      API_ROOT,
      "/excel-workbench/v1/freshness",
      { previous_evidence: state.previousEvidence, current_request: current },
      { token: ui.token.value },
    );
    state.stale = check.freshness_status === "STALE";
    state.freshnessVerified = !state.stale;
    state.confirmedMappingHash = state.stale ? null : check.current_mapping_hash;
    if (state.stale) {
      state.previewRequest = null;
      state.mapping = null;
      ui.review.checked = false;
    }
    ui.exportDetail.textContent = state.stale
      ? "Export is blocked because retained evidence is stale."
      : "Retained evidence is current and eligible for export.";
    setStatus(
      state.stale ? "hold" : "ready",
      check.freshness_status,
      state.stale ? check.reasons.join(", ") : "Source, mapping, and library identity match.",
    );
  } catch (error) {
    state.freshnessVerified = false;
    state.confirmedMappingHash = null;
    ui.exportDetail.textContent = "Freshness could not be verified; export remains disabled.";
    setStatus("blocked", "FRESHNESS CHECK FAILED", error.message);
  } finally {
    setBusy(false);
  }
}

async function exportReviewBundle() {
  setBusy(true);
  setStatus(
    "working",
    "EXPORTING",
    "Regenerating and verifying the current review evidence.",
  );
  const revision = state.inputRevision;
  try {
    const current = await captureInput();
    const request = buildReviewBundleExportRequest(
      current,
      state.previousEvidence,
      state.confirmedMappingHash,
    );
    const download = await postReviewBundleApi(
      API_ROOT,
      "/excel-workbench/v1/review-bundle",
      request,
      { token: ui.token.value },
    );
    if (state.inputRevision !== revision || state.stale) {
      throw new Error("The selected table changed during export; no file was saved.");
    }
    downloadReviewBundle(download);
    ui.exportDetail.textContent = `${download.filename} · SHA-256 ${download.fileHash}`;
    setStatus(
      "ready",
      "REVIEW BUNDLE SAVED",
      "The complete current JSON evidence was verified before download. Qualified review remains required.",
    );
  } catch (error) {
    state.freshnessVerified = false;
    state.confirmedMappingHash = null;
    ui.exportDetail.textContent = "Check freshness or recalculate before trying export again.";
    setStatus("blocked", "EXPORT BLOCKED", error.message);
    ui.status.focus();
  } finally {
    setBusy(false);
  }
}

async function initialize() {
  ui.status = document.getElementById("status");
  ui.statusTitle = document.getElementById("status-title");
  ui.statusDetail = document.getElementById("status-detail");
  ui.preview = document.getElementById("preview");
  ui.review = document.getElementById("review");
  ui.run = document.getElementById("run");
  ui.freshness = document.getElementById("freshness");
  ui.export = document.getElementById("export");
  ui.exportDetail = document.getElementById("export-detail");
  ui.mapping = document.getElementById("mapping");
  ui.context = document.getElementById("context");
  ui.token = document.getElementById("token");
  ui.etabsStatus = document.getElementById("etabs-status");
  ui.etabsStatusTitle = document.getElementById("etabs-status-title");
  ui.etabsStatusDetail = document.getElementById("etabs-status-detail");
  ui.etabsConnect = document.getElementById("etabs-connect");
  ui.etabsRun = document.getElementById("etabs-run");
  ui.etabsSelectionKind = document.getElementById("etabs-selection-kind");
  ui.etabsSelectionName = document.getElementById("etabs-selection-name");
  ui.etabsLimit = document.getElementById("etabs-limit");
  ui.etabsStandard = document.getElementById("etabs-standard");
  ui.etabsFck = document.getElementById("etabs-fck");
  ui.etabsFy = document.getElementById("etabs-fy");
  ui.etabsClearCover = document.getElementById("etabs-cover");
  ui.etabsStirrupDiameter = document.getElementById("etabs-stirrup-dia");
  ui.etabsTensionBarDiameter = document.getElementById("etabs-tension-dia");
  ui.etabsCompressionBarDiameter = document.getElementById("etabs-compression-dia");
  ui.etabsDDash = document.getElementById("etabs-d-dash");
  ui.etabsTopRatio = document.getElementById("etabs-top-ratio");
  ui.etabsStirrupLegs = document.getElementById("etabs-stirrup-legs");
  ui.etabsSpacingSupport = document.getElementById("etabs-spacing-support");
  ui.etabsSpacingMid = document.getElementById("etabs-spacing-mid");
  ui.preview.addEventListener("click", previewMapping);
  ui.review.addEventListener("change", mappingReviewChanged);
  ui.run.addEventListener("click", runCalculation);
  ui.freshness.addEventListener("click", checkFreshness);
  ui.export.addEventListener("click", exportReviewBundle);
  ui.etabsConnect.addEventListener("click", connectEtabs);
  ui.etabsRun.addEventListener("click", runEtabsPilot);
  setBusy(true);
  setPilotBusy(true);

  let surface;
  try {
    surface = await inspectWorkbookSurface(Excel, {
      worksheetName: INPUT_SHEET,
      tableName: INPUT_TABLE,
    });
  } catch (error) {
    setStatus("blocked", "WORKBOOK CHECK FAILED", officeErrorDetail(error));
    setBusy(false);
    return;
  }

  try {
    state.definition = await getWorkbenchApi(
      API_ROOT,
      "/excel-workbench/v1/definition",
      { token: ui.token.value },
    );
  } catch (error) {
    setStatus("blocked", "LOCAL API CONNECTION FAILED", error.message);
    setBusy(false);
    return;
  }

  ui.context.textContent = `Connected · library ${state.definition.library_version} · engine ${state.definition.library_content_identity.slice(0, 12)}… · workbook ${state.definition.workbook_artifact_sha256.slice(0, 12)}… · Windows ${state.definition.installed_windows_excel_evidence}`;
  await refreshEtabsStatus();
  if (!surface.available) {
    setStatus("hold", "E1 WORKBOOK NOT OPEN", surface.detail);
    setBusy(false);
    return;
  }

  try {
    state.workbookId = await ensureWorkbookId(Office, SETTINGS_KEYS.workbookId);
    state.previousEvidence = Office.context.document.settings.get(
      SETTINGS_KEYS.previousEvidence,
    );
    state.stale =
      Office.context.document.settings.get(SETTINGS_KEYS.stale) !== false;
    state.freshnessVerified = false;
    state.confirmedMappingHash = null;
    await registerInputChange();
    state.workbookSurfaceAvailable = true;
    setStatus(
      state.previousEvidence && !state.stale ? "ready" : "hold",
      state.previousEvidence && !state.stale ? "RETAINED RESULT" : "PREVIEW REQUIRED",
      state.previousEvidence && !state.stale
        ? "Use Check freshness before relying on retained evidence."
        : "Start by previewing the exact selected-table mapping.",
    );
    ui.exportDetail.textContent = state.previousEvidence && !state.stale
      ? "Check retained-result freshness before export."
      : "Export becomes available after a current reviewed run.";
  } catch (error) {
    setStatus("blocked", "WORKBOOK INITIALIZATION FAILED", officeErrorDetail(error));
  }
  setBusy(false);
}

Office.onReady((info) => {
  if (info.host !== Office.HostType.Excel) {
    document.body.textContent = "Excel Routine Workbench V1 requires Microsoft Excel.";
    return;
  }
  void initialize();
});
