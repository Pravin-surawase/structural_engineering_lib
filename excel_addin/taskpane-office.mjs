import {
  ETABS_BASELINE_TABLES,
  ETABS_PILOT_HEADERS,
  sha256Hex,
} from "./taskpane-core.mjs";

const ETABS_PILOT_SHEET = "ETABS_Pilot";
const ETABS_PILOT_TABLE = "tbl_ETABS_Pilot_V1";

function officeAsyncError(error) {
  const wrapped = new Error(
    error?.message || "Office document settings could not be saved.",
  );
  if (error?.code) wrapped.code = error.code;
  if (error?.debugInfo) wrapped.debugInfo = error.debugInfo;
  return wrapped;
}

export function officeErrorDetail(error) {
  const details = [error?.message || String(error)];
  if (error?.code) details.push(`code ${error.code}`);
  if (error?.debugInfo?.errorLocation) {
    details.push(`at ${error.debugInfo.errorLocation}`);
  }
  return details.join(" · ");
}

export async function inspectWorkbookSurface(
  excelApi,
  { worksheetName, tableName },
) {
  return excelApi.run(async (context) => {
    const sheet = context.workbook.worksheets.getItemOrNullObject(worksheetName);
    sheet.load("isNullObject");
    await context.sync();
    if (sheet.isNullObject) {
      return {
        available: false,
        missing: "worksheet",
        detail: `Open the packaged E1 workbook containing ${worksheetName} / ${tableName}.`,
      };
    }

    const table = sheet.tables.getItemOrNullObject(tableName);
    table.load("isNullObject");
    await context.sync();
    if (table.isNullObject) {
      return {
        available: false,
        missing: "table",
        detail: `${worksheetName} is open, but ${tableName} is missing. Use the packaged E1 workbook.`,
      };
    }

    return { available: true, missing: null, detail: "" };
  });
}

export function saveDocumentSettings(officeApi) {
  return new Promise((resolve, reject) => {
    officeApi.context.document.settings.saveAsync((result) => {
      if (result.status === officeApi.AsyncResultStatus.Failed) {
        reject(officeAsyncError(result.error));
      } else {
        resolve();
      }
    });
  });
}

export async function ensureWorkbookId(
  officeApi,
  settingKey,
  createId = () =>
    globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
) {
  const settings = officeApi.context.document.settings;
  let value = settings.get(settingKey);
  if (!value) {
    value = `EXCEL-${createId()}`.replace(/[^A-Za-z0-9_.:-]/g, "-");
    settings.set(settingKey, value);
    await saveDocumentSettings(officeApi);
  }
  return value;
}

export async function registerWorksheetChange(
  excelApi,
  { worksheetName, handler },
) {
  await excelApi.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(worksheetName);
    sheet.onChanged.add(handler);
    await context.sync();
  });
}

export async function writeEtabsPilotResults(excelApi, rows) {
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error("At least one completed ETABS pilot row is required.");
  }
  if (rows.some((row) => !Array.isArray(row) || row.length !== ETABS_PILOT_HEADERS.length)) {
    throw new Error("ETABS pilot rows do not match the controlled output contract.");
  }
  return excelApi.run(async (context) => {
    const worksheets = context.workbook.worksheets;
    let sheet = worksheets.getItemOrNullObject(ETABS_PILOT_SHEET);
    sheet.load("isNullObject");
    await context.sync();

    if (sheet.isNullObject) {
      sheet = worksheets.add(ETABS_PILOT_SHEET);
      const range = sheet.getRangeByIndexes(
        0,
        0,
        rows.length + 1,
        ETABS_PILOT_HEADERS.length,
      );
      range.values = [ETABS_PILOT_HEADERS, ...rows];
      const table = sheet.tables.add(range, true);
      table.name = ETABS_PILOT_TABLE;
      sheet.activate();
      await context.sync();
      return { disposition: "CREATED", sheetName: ETABS_PILOT_SHEET };
    }

    const table = sheet.tables.getItemOrNullObject(ETABS_PILOT_TABLE);
    table.load("isNullObject");
    await context.sync();
    if (table.isNullObject) {
      throw new Error(
        `${ETABS_PILOT_SHEET} already exists without ${ETABS_PILOT_TABLE}; no cells were overwritten.`,
      );
    }
    const header = table.getHeaderRowRange();
    header.load(["values", "rowIndex", "columnIndex", "columnCount"]);
    await context.sync();
    if (JSON.stringify(header.values[0]) !== JSON.stringify(ETABS_PILOT_HEADERS)) {
      throw new Error("The existing ETABS pilot table headers do not match V1; no cells were overwritten.");
    }
    table.resize(
      sheet.getRangeByIndexes(
        header.rowIndex,
        header.columnIndex,
        rows.length + 1,
        header.columnCount,
      ),
    );
    await context.sync();
    table.getDataBodyRange().values = rows;
    sheet.activate();
    await context.sync();
    return { disposition: "UPDATED", sheetName: ETABS_PILOT_SHEET };
  });
}

function primitiveToCellValue(value) {
  if (value === null || value === undefined || value === "") return { type: "Empty" };
  if (typeof value === "string") return { type: "String", basicValue: value };
  if (typeof value === "boolean") return { type: "Boolean", basicValue: value };
  if (typeof value === "number" && Number.isFinite(value)) {
    return { type: "Double", basicValue: value };
  }
  throw new Error("The W2 Excel projection contains an unsupported cell value.");
}

function toCellValueMatrix(rows) {
  return rows.map((row) => row.map(primitiveToCellValue));
}

function cellValueToPrimitive(value) {
  if (value === null || value === undefined) return null;
  if (typeof value !== "object") return value;
  if (value.type === "Empty") return null;
  if (Object.hasOwn(value, "basicValue")) return value.basicValue;
  throw new Error(`The W2 Excel read-back contains unsupported cell type ${value.type}.`);
}

function fromCellValueMatrix(rows) {
  return rows.map((row) => row.map(cellValueToPrimitive));
}

function cloneCellValueMatrix(rows) {
  return rows.map((row) => row.map((cell) => ({ ...cell })));
}

function matricesMatch(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function firstMatrixMismatch(actual, expected) {
  for (let row = 0; row < expected.length; row += 1) {
    for (let column = 0; column < expected[row].length; column += 1) {
      if (JSON.stringify(actual[row][column]) !== JSON.stringify(expected[row][column])) {
        return {
          row: row + 1,
          column: column + 1,
          expected: expected[row][column],
          actual: actual[row][column],
        };
      }
    }
  }
  return null;
}

function normalizeExpectedExcelMatrix(rows) {
  return rows.map((row) => row.map((value) => (value === "" ? null : value)));
}

async function restoreEtabsBaselineTransaction(context, states) {
  const worksheets = context.workbook.worksheets;
  const recovery = states.map((state) => {
    const sheet = worksheets.getItemOrNullObject(state.spec.sheetName);
    sheet.load("isNullObject");
    return { state, sheet, table: null, touchedRange: null };
  });
  await context.sync();

  for (const item of recovery) {
    if (!item.state.exists) continue;
    if (item.sheet.isNullObject) {
      throw new Error(`Rollback could not find ${item.state.spec.sheetName}.`);
    }
    item.table = item.sheet.tables.getItemOrNullObject(item.state.spec.tableName);
    item.table.load("isNullObject");
  }
  await context.sync();

  for (const item of recovery) {
    const { state, sheet } = item;
    if (!state.exists) {
      if (!sheet.isNullObject) sheet.delete();
      continue;
    }
    if (item.table.isNullObject) {
      throw new Error(`Rollback could not find ${state.spec.tableName}.`);
    }
    item.table.resize(
      sheet.getRangeByIndexes(
        state.header.rowIndex,
        state.header.columnIndex,
        state.originalRowCount,
        state.header.columnCount,
      ),
    );
    item.touchedRange = sheet.getRangeByIndexes(
      state.header.rowIndex,
      state.header.columnIndex,
      state.touchedRowCount,
      state.header.columnCount,
    );
    item.touchedRange.valuesAsJson = cloneCellValueMatrix(state.snapshotValuesAsJson);
  }
  await context.sync();

  const createdChecks = [];
  for (const item of recovery) {
    const { state } = item;
    if (!state.exists) {
      const sheet = worksheets.getItemOrNullObject(state.spec.sheetName);
      sheet.load("isNullObject");
      createdChecks.push(sheet);
      continue;
    }
    const tableRange = item.table.getRange();
    tableRange.load(["rowCount", "columnCount"]);
    item.touchedRange.load(["valuesAsJson", "rowCount", "columnCount"]);
    item.tableRange = tableRange;
  }
  await context.sync();

  if (createdChecks.some((sheet) => !sheet.isNullObject)) {
    throw new Error("Rollback left a newly created W2 worksheet behind.");
  }
  for (const item of recovery) {
    const { state } = item;
    if (!state.exists) continue;
    if (
      item.tableRange.rowCount !== state.originalRowCount ||
      item.tableRange.columnCount !== state.header.columnCount ||
      item.touchedRange.rowCount !== state.touchedRowCount ||
      item.touchedRange.columnCount !== state.header.columnCount ||
      !matricesMatch(item.touchedRange.valuesAsJson, state.snapshotValuesAsJson)
    ) {
      throw new Error(`Rollback did not exactly restore ${state.spec.tableName}.`);
    }
  }
}

async function verifyEtabsBaselineWrite(context, states, projection, cryptoImpl) {
  for (const state of states) {
    state.verificationRange = state.table.getRange();
    state.verificationRange.load(["valuesAsJson", "rowCount", "columnCount"]);
  }
  await context.sync();

  let verifiedProjectedRows = 0;
  for (const state of states) {
    const expected = normalizeExpectedExcelMatrix([state.spec.headers, ...state.rows]);
    const actual = fromCellValueMatrix(state.verificationRange.valuesAsJson);
    if (
      state.verificationRange.rowCount !== expected.length ||
      state.verificationRange.columnCount !== state.spec.headers.length ||
      !matricesMatch(actual, expected)
    ) {
      const mismatch = firstMatrixMismatch(actual, expected);
      const detail = mismatch
        ? ` First mismatch: row ${mismatch.row}, column ${mismatch.column}, expected ${JSON.stringify(mismatch.expected)}, actual ${JSON.stringify(mismatch.actual)}.`
        : " The table dimensions differ from the controlled contract.";
      throw new Error(
        `The W2 ${state.key} table failed exact Excel read-back verification.${detail}`,
      );
    }
    state.verifiedRows = actual.slice(1);
    verifiedProjectedRows += state.verifiedRows.length;
  }
  if (verifiedProjectedRows !== projection.projectedRows) {
    throw new Error("The verified W2 Excel row total does not reconcile.");
  }

  const reconstructedJson = states
    .find((state) => state.key === "json")
    .verifiedRows.map((row) => row[5])
    .join("");
  if (reconstructedJson !== projection.hashBasisJson) {
    throw new Error("The W2 JSON chunks did not rejoin to the exact hash-basis text.");
  }
  const bytes = new TextEncoder().encode(reconstructedJson);
  const digest = await sha256Hex(bytes, { cryptoImpl });
  if (digest !== projection.baselineSha256) {
    throw new Error("The reconstructed W2 JSON failed SHA-256 verification.");
  }
  return { verifiedProjectedRows, verifiedHashBasisUtf8Bytes: bytes.length };
}

export async function writeEtabsBaselineResults(
  excelApi,
  projection,
  { cryptoImpl = globalThis.crypto } = {},
) {
  if (
    !projection ||
    typeof projection.baselineSha256 !== "string" ||
    typeof projection.hashBasisJson !== "string" ||
    !projection.tables
  ) {
    throw new Error("A complete projected W2 baseline is required.");
  }
  const entries = Object.entries(ETABS_BASELINE_TABLES).map(([key, spec]) => {
    const rows = projection.tables[key];
    if (!Array.isArray(rows)) {
      throw new Error(`The W2 ${key} table is missing.`);
    }
    if (rows.some((row) => !Array.isArray(row) || row.length !== spec.headers.length)) {
      throw new Error(`The W2 ${key} rows do not match the controlled V1 headers.`);
    }
    return { key, spec, rows };
  });
  const projectedRows = entries.reduce((total, entry) => total + entry.rows.length, 0);
  if (projectedRows !== projection.projectedRows) {
    throw new Error("The W2 projected Excel row total does not reconcile.");
  }
  if (projection.tables.json.map((row) => row[5]).join("") !== projection.hashBasisJson) {
    throw new Error("The projected W2 JSON chunks do not rejoin exactly.");
  }

  return excelApi.run(async (context) => {
    const worksheets = context.workbook.worksheets;
    const states = entries.map((entry) => {
      const sheet = worksheets.getItemOrNullObject(entry.spec.sheetName);
      sheet.load("isNullObject");
      return {
        ...entry,
        sheet,
        exists: false,
        table: null,
        header: null,
        tableRange: null,
        originalRowCount: null,
        touchedRowCount: null,
        snapshotValuesAsJson: null,
      };
    });
    await context.sync();

    for (const state of states) {
      state.exists = !state.sheet.isNullObject;
      if (state.exists) {
        state.table = state.sheet.tables.getItemOrNullObject(state.spec.tableName);
        state.table.load("isNullObject");
      }
    }
    await context.sync();

    for (const state of states) {
      if (!state.exists) continue;
      if (state.table.isNullObject) {
        throw new Error(
          `${state.spec.sheetName} already exists without ${state.spec.tableName}; no cells were overwritten.`,
        );
      }
      state.header = state.table.getHeaderRowRange();
      state.header.load(["values", "rowIndex", "columnIndex", "columnCount"]);
      state.tableRange = state.table.getRange();
      state.tableRange.load(["rowCount", "columnCount"]);
    }
    await context.sync();

    for (const state of states) {
      if (
        state.exists &&
        JSON.stringify(state.header.values[0]) !== JSON.stringify(state.spec.headers)
      ) {
        throw new Error(
          `${state.spec.sheetName} headers do not match the controlled V1 contract; no cells were overwritten.`,
        );
      }
    }

    for (const state of states) {
      if (!state.exists) continue;
      state.originalRowCount = state.tableRange.rowCount;
      state.touchedRowCount = Math.max(state.originalRowCount, state.rows.length + 1);
      state.snapshotRange = state.sheet.getRangeByIndexes(
        state.header.rowIndex,
        state.header.columnIndex,
        state.touchedRowCount,
        state.header.columnCount,
      );
      state.snapshotRange.load(["valuesAsJson", "rowCount", "columnCount"]);
    }
    await context.sync();

    for (const state of states) {
      if (!state.exists) continue;
      state.snapshotValuesAsJson = cloneCellValueMatrix(state.snapshotRange.valuesAsJson);
      if (
        state.snapshotRange.rowCount !== state.touchedRowCount ||
        state.snapshotRange.columnCount !== state.header.columnCount
      ) {
        throw new Error(`Could not snapshot ${state.spec.tableName} before mutation.`);
      }
    }

    try {
      for (const state of states) {
        const rowCount = state.rows.length + 1;
        if (!state.exists) {
          state.sheet = worksheets.add(state.spec.sheetName);
        }
        const range = state.sheet.getRangeByIndexes(
          state.exists ? state.header.rowIndex : 0,
          state.exists ? state.header.columnIndex : 0,
          rowCount,
          state.spec.headers.length,
        );
        if (state.exists) {
          state.table.resize(range);
        }
        range.valuesAsJson = toCellValueMatrix([state.spec.headers, ...state.rows]);
        if (!state.exists) {
          state.table = state.sheet.tables.add(range, true);
          state.table.name = state.spec.tableName;
        }
      }
      await context.sync();

      states.find((state) => state.key === "summary").sheet.activate();
      await context.sync();
      const verification = await verifyEtabsBaselineWrite(
        context,
        states,
        projection,
        cryptoImpl,
      );

      const created = states.filter((state) => !state.exists).length;
      const disposition =
        created === states.length ? "CREATED" : created === 0 ? "UPDATED" : "RECONCILED";
      return {
        disposition,
        baselineSha256: projection.baselineSha256,
        verifiedProjectedRows: verification.verifiedProjectedRows,
        verifiedHashBasisUtf8Bytes: verification.verifiedHashBasisUtf8Bytes,
        sheets: states.map((state) => state.spec.sheetName),
      };
    } catch (error) {
      try {
        await restoreEtabsBaselineTransaction(context, states);
      } catch (rollbackError) {
        throw new Error(
          `${error.message} Transaction rollback also failed: ${rollbackError.message}`,
          { cause: error },
        );
      }
      throw error;
    }
  });
}
