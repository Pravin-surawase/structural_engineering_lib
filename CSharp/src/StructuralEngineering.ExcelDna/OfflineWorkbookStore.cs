using System.Globalization;
using System.Text.Json;
using System.Xml.Linq;

namespace StructuralEngineering.ExcelDna;

public sealed record OfflineDocumentState(
    string SchemaVersion, string DocumentId, bool HasAssumptions,
    string? StoreDirectory, OfflineSnapshotReference? SnapshotReference, int ReportRows,
    string? AssumptionRevision, string? ReportSnapshotSha256);

/// <summary>Small workbook metadata and explicitly requested public projections; no snapshot payload in Excel.</summary>
internal sealed class OfflineWorkbookStore(object workbook)
{
    public const string Schema = "structural-excel-offline/v1";
    public const string XmlNamespace = "urn:structautomate:offline-session:v1";
    public const string ReportSheet = "Beam Review";
    private readonly dynamic _workbook = workbook;

    public OfflineDocumentState? ReadState()
    {
        var xml = ReadXml();
        if (xml is null) return null;
        var state = JsonSerializer.Deserialize<OfflineDocumentState>(XElement.Parse(xml).Value, WorkbookContract.Json)
            ?? throw new InvalidOperationException("Workbook session metadata is empty.");
        if (state.SchemaVersion != Schema || !Guid.TryParseExact(state.DocumentId, "N", out _) || state.ReportRows is < 0 or > 10010)
            throw new InvalidOperationException("Workbook session metadata is incompatible.");
        return state;
    }

    public OfflineDocumentState CreateAssumptions(int failAfterWrite = 0)
    {
        var state = ReadState();
        if (state is not null)
        {
            _ = ReadAssumptions(state);
            Activate(OfflineAssumptions.SheetName);
            return state;
        }
        RequireWritable();
        var initial = new OfflineDocumentState(Schema, Guid.NewGuid().ToString("N"), true, null, null, 0, null, null);
        WriteTransaction(initial, OfflineAssumptions.SheetName, OfflineAssumptions.CreateSheet(), 0, failAfterWrite,
            sheet =>
            {
                for (var i = 0; i < OfflineAssumptions.Definitions.Count; i++)
                    SetFormula(sheet, $"D{i + OfflineAssumptions.FirstValueRow}", OfflineAssumptions.OriginFormula(i));
            });
        Activate(OfflineAssumptions.SheetName);
        return initial;
    }

    public OfflineAssumptionInput ReadAssumptions(OfflineDocumentState state)
    {
        if (!state.HasAssumptions) throw new InvalidOperationException("Create Assumptions before opening a snapshot.");
        dynamic? sheet = FindSheet(OfflineAssumptions.SheetName);
        dynamic? range = null;
        try
        {
            if (sheet is null) throw new InvalidOperationException("The owned Assumptions sheet is missing.");
            range = sheet.Range[$"A6:C{5 + OfflineAssumptions.Definitions.Count}"];
            object[,] cells = range.Value2;
            object[,] formulas = range.Formula;
            var values = new List<string?>();
            for (var i = 0; i < OfflineAssumptions.Definitions.Count; i++)
            {
                var definition = OfflineAssumptions.Definitions[i];
                if (Text(cells[i + 1, 1]) != definition.Label || Text(cells[i + 1, 3]) != definition.Unit)
                    throw new InvalidOperationException($"Assumptions row {i + 6} has changed labels or units. Restore the original layout.");
                if (Text(formulas[i + 1, 2]).StartsWith('='))
                    throw new InvalidOperationException($"Assumptions!B{i + 6}: enter an explicit value, not a formula.");
                values.Add(cells[i + 1, 2] is null ? null : Text(cells[i + 1, 2]));
            }
            return OfflineAssumptions.Read(values);
        }
        finally { Release(range); Release(sheet); }
    }

    public void CommitImport(OfflineDocumentState state, OfflineSnapshotReference reference, string directory,
        OfflineAssumptionInput assumptions, int failAfterWrite = 0)
    {
        var updated = state with { StoreDirectory = directory, SnapshotReference = reference, AssumptionRevision = assumptions.Revision };
        // Existing reports remain explicitly historical after a source replacement.
        object[,]? report = null;
        if (state.ReportRows > 0)
        {
            dynamic? sheet = FindSheet(ReportSheet);
            dynamic? cell = null;
            try
            {
                if (sheet is null) throw new InvalidOperationException("The owned Beam Review sheet is missing.");
                cell = sheet.Range["A1:A2"];
                object[,] values = cell.Formula;
                report = new object[,] { { values[1, 1] }, { "Historical review — snapshot replaced; review again" } };
            }
            finally { Release(cell); Release(sheet); }
        }
        WriteTransaction(updated, report is null ? null : ReportSheet, report, report is null ? 0 : 2, failAfterWrite);
    }

    public void WriteReport(OfflineDocumentState state, object[,] rows, int failAfterWrite = 0)
    {
        var assumptions = ReadAssumptions(state);
        var updated = state with
        {
            ReportRows = rows.GetLength(0),
            AssumptionRevision = assumptions.Revision,
            ReportSnapshotSha256 = state.SnapshotReference?.SnapshotSha256
        };
        WriteTransaction(updated, ReportSheet, rows, state.ReportRows, failAfterWrite,
            sheet => SetFormula(sheet, "A2", OfflineAssumptions.ReportFreshnessFormula(assumptions)));
        Activate(ReportSheet);
    }

    // The exact controlled footprint and metadata share a verified rollback boundary.
    private void WriteTransaction(OfflineDocumentState state, string? sheetName, object[,]? values,
        int oldRows, int failAfterWrite, Action<dynamic>? finalize = null)
    {
        RequireWritable();
        var oldXml = ReadXml();
        dynamic? sheet = null;
        dynamic? range = null;
        dynamic? app = null;
        object? preimage = null;
        object? preimageValues = null;
        var formulaAreas = new List<(string Address, object Formula)>();
        var created = false;
        var changed = false;
        try
        {
            if (sheetName is not null && values is not null)
            {
                sheet = FindSheet(sheetName);
                if (sheet is not null && oldRows == 0) throw new InvalidOperationException($"The worksheet '{sheetName}' already exists and is not owned by this session.");
                if (sheet is null && oldRows > 0) throw new InvalidOperationException($"The owned worksheet '{sheetName}' is missing.");
                if (sheet is null)
                {
                    dynamic sheets = _workbook.Worksheets;
                    try { sheet = sheets.Add(); created = true; sheet.Name = sheetName; }
                    finally { Release(sheets); }
                }
                if ((bool)sheet.ProtectContents) throw new InvalidOperationException($"Unprotect '{sheetName}' before updating it.");
                var height = Math.Max(oldRows, values.GetLength(0));
                range = SizedRange(sheet, "A1", height, values.GetLength(1));
                if (!created && height > oldRows)
                {
                    dynamic? extra = null;
                    try
                    {
                        extra = SizedRange(sheet, $"A{oldRows + 1}", height - oldRows, values.GetLength(1));
                        if (HasContent(extra.Formula)) throw new InvalidOperationException("The report would overwrite content outside its owned footprint.");
                    }
                    finally { Release(extra); }
                }
                preimage = range.Formula;
                preimageValues = range.Value2;
                CaptureFormulaAreas(range, formulaAreas);
                if (created) FormatNewSheet(sheet, height, values.GetLength(1), sheetName == OfflineAssumptions.SheetName);
                changed = true;
                range.ClearContents();
                dynamic? target = null;
                try
                {
                    target = SizedRange(sheet, "A1", values.GetLength(0), values.GetLength(1));
                    target.Value2 = values;
                    if (!SameValues(target.Value2, values)) throw new InvalidOperationException("Projection readback failed.");
                }
                finally { Release(target); }
                finalize?.Invoke(sheet);
                if (failAfterWrite == 1) throw new InvalidOperationException("OFFLINE.INJECTED_WRITE_FAILURE");
            }
            WriteXml(Serialize(state));
            if (failAfterWrite == 2) throw new InvalidOperationException("OFFLINE.INJECTED_METADATA_FAILURE");
            if (ReadState() != state) throw new InvalidOperationException("Workbook metadata readback failed.");
            HostEffectLedger.Record("excel.offline.projection.commit");
        }
        catch (Exception error)
        {
            try
            {
                WriteXml(oldXml);
                if (created && sheet is not null)
                {
                    app = _workbook.Application;
                    var alerts = (bool)app.DisplayAlerts;
                    try { app.DisplayAlerts = false; sheet.Delete(); }
                    finally { app.DisplayAlerts = alerts; }
                }
                else if (changed && range is not null)
                {
                    // Formula returns empty text for blank cells. Restoring that matrix
                    // alone changes genuinely empty cells into stored empty strings.
                    range.Value2 = preimageValues;
                    foreach (var area in formulaAreas)
                    {
                        dynamic restored = sheet!.Range[area.Address];
                        try { restored.Formula = area.Formula; }
                        finally { Release(restored); }
                    }
                    if (!SameMatrix(range.Formula, preimage) || !SameStoredValues(range.Value2, preimageValues))
                        throw new InvalidOperationException("Projection rollback readback differs.");
                }
                if (ReadXml() != oldXml) throw new InvalidOperationException("Metadata rollback readback differs.");
            }
            catch (Exception rollback) { throw new InvalidOperationException($"RESTORATION_UNVERIFIED: {error.Message}; {rollback.Message}", rollback); }
            throw;
        }
        finally { Release(app); Release(range); Release(sheet); }
    }

    public void Activate(string name)
    {
        dynamic? sheet = FindSheet(name);
        try { if (sheet is not null) sheet.Activate(); }
        finally { Release(sheet); }
    }

    private dynamic? FindSheet(string name)
    {
        dynamic sheets = _workbook.Worksheets;
        try
        {
            for (var i = 1; i <= (int)sheets.Count; i++)
            {
                dynamic sheet = sheets.Item(i);
                if ((string)sheet.Name == name) return sheet;
                Release(sheet);
            }
            return null;
        }
        finally { Release(sheets); }
    }

    private string? ReadXml()
    {
        dynamic? parts = null; dynamic? selected = null; dynamic? part = null;
        try
        {
            parts = _workbook.CustomXMLParts;
            selected = parts.SelectByNamespace(XmlNamespace);
            if ((int)selected.Count == 0) return null;
            if ((int)selected.Count != 1) throw new InvalidOperationException("Workbook contains ambiguous session metadata.");
            part = selected.Item(1);
            return (string)part.XML;
        }
        finally { Release(part); Release(selected); Release(parts); }
    }

    private void WriteXml(string? xml)
    {
        dynamic? parts = null; dynamic? selected = null; dynamic? part = null;
        try
        {
            parts = _workbook.CustomXMLParts;
            selected = parts.SelectByNamespace(XmlNamespace);
            if ((int)selected.Count > 1) throw new InvalidOperationException("Workbook contains ambiguous session metadata.");
            if ((int)selected.Count == 1)
            {
                part = selected.Item(1);
                if (xml == (string)part.XML) return;
                // Office LoadXML is initial-load-only. Replace this owned part;
                // the enclosing transaction restores its exact preimage if Add/readback fails.
                part.Delete();
                Release(part);
                part = null;
                if (xml is not null) part = parts.Add(xml);
            }
            else if (xml is not null) part = parts.Add(xml);
        }
        finally { Release(part); Release(selected); Release(parts); }
    }

    private void RequireWritable()
    {
        if ((bool)_workbook.ReadOnly || (bool)_workbook.ProtectStructure)
            throw new InvalidOperationException("Use a writable workbook with unprotected structure.");
    }

    private static string Serialize(OfflineDocumentState state) => new XElement(XName.Get("state", XmlNamespace),
        JsonSerializer.Serialize(state, WorkbookContract.Json)).ToString(SaveOptions.DisableFormatting);

    private static void SetFormula(dynamic sheet, string address, string formula)
    {
        dynamic cell = sheet.Range[address];
        try { cell.NumberFormat = "General"; cell.Formula = formula; }
        finally { Release(cell); }
    }

    private static void CaptureFormulaAreas(dynamic range, List<(string Address, object Formula)> result)
    {
        object? hasFormula = range.HasFormula;
        if (hasFormula is false) return;
        dynamic? formulas = null;
        dynamic? areas = null;
        try
        {
            formulas = range.SpecialCells(-4123); // xlCellTypeFormulas, actual formulas only.
            areas = formulas.Areas;
            for (var i = 1; i <= (int)areas.Count; i++)
            {
                dynamic area = areas.Item(i);
                try { result.Add(((string)area.Address, (object)area.Formula)); }
                finally { Release(area); }
            }
        }
        finally { Release(areas); Release(formulas); }
    }

    private static void FormatNewSheet(dynamic sheet, int rows, int columns, bool assumptions)
    {
        dynamic? range = null; dynamic? font = null; dynamic? header = null; dynamic? fill = null;
        try
        {
            range = SizedRange(sheet, "A1", rows, columns);
            range.NumberFormat = "@";
            font = range.Font; font.Name = "Aptos"; font.Size = 11;
            range.ColumnWidth = assumptions ? 29 : 18;
            header = sheet.Range[assumptions ? "A5:D5" : "A9:M9"];
            fill = header.Interior; fill.Color = 0x705030;
            dynamic headerFont = header.Font;
            try { headerFont.Color = 0xFFFFFF; headerFont.Bold = true; }
            finally { Release(headerFont); }
            if (assumptions)
            {
                dynamic inputs = sheet.Range[$"B6:B{rows}"];
                dynamic inputFill = inputs.Interior;
                try { inputFill.Color = 0xE9F4FF; inputs.NumberFormat = "General"; }
                finally { Release(inputFill); Release(inputs); }
            }
        }
        finally { Release(fill); Release(header); Release(font); Release(range); }
    }

    private static dynamic SizedRange(dynamic sheet, string address, int rows, int columns)
    {
        dynamic anchor = sheet.Range[address];
        try { return anchor.Resize[rows, columns]; }
        finally { Release(anchor); }
    }

    private static bool HasContent(object? value) => value is object[,] matrix
        ? matrix.Cast<object?>().Any(item => !string.IsNullOrEmpty(Text(item))) : !string.IsNullOrEmpty(Text(value));
    private static bool SameValues(object actual, object[,] expected)
    {
        if (actual is not object[,] matrix) return false;
        for (var row = 0; row < expected.GetLength(0); row++)
            for (var column = 0; column < expected.GetLength(1); column++)
                if (Text(matrix[row + matrix.GetLowerBound(0), column + matrix.GetLowerBound(1)]) != Text(expected[row, column])) return false;
        return true;
    }
    private static bool SameMatrix(object? actual, object? expected) => actual is object[,] a && expected is object[,] b
        ? a.GetLength(0) == b.GetLength(0) && a.GetLength(1) == b.GetLength(1) && a.Cast<object?>().Select(Text).SequenceEqual(b.Cast<object?>().Select(Text))
        : Text(actual) == Text(expected);
    private static bool SameStoredValues(object? actual, object? expected) => actual is object[,] a && expected is object[,] b
        ? a.GetLength(0) == b.GetLength(0) && a.GetLength(1) == b.GetLength(1) && a.Cast<object?>().SequenceEqual(b.Cast<object?>())
        : Equals(actual, expected);
    private static string Text(object? value) => Convert.ToString(value, CultureInfo.InvariantCulture) ?? "";
    internal static void Release(object? value) => ExcelWorkbookTableStore.ReleaseCom(value);
}
