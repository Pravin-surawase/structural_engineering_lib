import { ETABS_PILOT_HEADERS } from "./taskpane-core.mjs";

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
