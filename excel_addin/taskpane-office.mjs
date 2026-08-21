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
