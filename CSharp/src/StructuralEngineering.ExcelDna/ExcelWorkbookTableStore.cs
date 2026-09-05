using System.Globalization;
using System.Runtime.InteropServices;

namespace StructuralEngineering.ExcelDna;

/// <summary>Bulk, values-only adapter for the named tables controlled by the add-in.</summary>
public sealed class ExcelWorkbookTableStore : IWorkbookTableStore
{
    private const int ExcelCellCharacterLimit = 32767;
    private readonly dynamic _workbook;
    private readonly HashSet<string> _createdSheets = new(StringComparer.Ordinal);
    private readonly int? _failAfterWrites;
    private int _writes;
    private bool _failureConsumed;

    private static readonly IReadOnlyDictionary<string, string> SheetNames =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [WorkbookContract.ProjectTable] = "SA_Project",
            [WorkbookContract.MembersTable] = "SA_Members",
            [WorkbookContract.OperationsTable] = "SA_Operations",
            [WorkbookContract.ResultsTable] = "SA_Results",
            [WorkbookContract.FreshnessTable] = "SA_Freshness",
            [WorkbookContract.ReceiptTable] = "SA_Receipts",
            [WorkbookContract.BenchmarkTable] = "SA_Benchmark",
            [WorkbookContract.HostEffectsTable] = "SA_HostEffects"
        };

    public ExcelWorkbookTableStore(object workbook, int? failAfterWrites = null)
    {
        ArgumentNullException.ThrowIfNull(workbook);
        if (failAfterWrites is < 1)
            throw new ArgumentOutOfRangeException(nameof(failAfterWrites));
        _workbook = workbook;
        _failAfterWrites = failAfterWrites;
    }

    public bool TryRead(string tableId, out WorkbookTable table)
    {
        HostEffectLedger.Record("excel.workbook.table.read");
        dynamic? worksheet = null;
        dynamic? listObject = FindListObject(tableId, out worksheet);
        dynamic? range = null;
        dynamic? rangeRows = null;
        dynamic? rangeColumns = null;
        try
        {
            if (listObject is null)
            {
                table = null!;
                return false;
            }
            range = listObject.Range;
            rangeRows = range.Rows;
            rangeColumns = range.Columns;
            var rowCount = (int)rangeRows.Count;
            var columnCount = (int)rangeColumns.Count;
            object? values = range.Value2;
            var rows = new List<IReadOnlyList<WorkbookCell>>(rowCount);
            for (var row = 1; row <= rowCount; row++)
            {
                var cells = new WorkbookCell[columnCount];
                for (var column = 1; column <= columnCount; column++)
                {
                    var value = rowCount == 1 && columnCount == 1
                        ? values
                        : ((object[,])values!)[row, column];
                    cells[column - 1] = new WorkbookCell(ToInvariantText(value));
                }
                rows.Add(cells);
            }
            table = new(tableId, rows);
            return true;
        }
        finally
        {
            ReleaseCom(rangeColumns);
            ReleaseCom(rangeRows);
            ReleaseCom(range);
            ReleaseCom(listObject);
            ReleaseCom(worksheet);
        }
    }

    public void BulkWrite(IReadOnlyList<WorkbookTable> tables)
    {
        ArgumentNullException.ThrowIfNull(tables);
        if (tables.Select(table => table.TableId).Distinct(StringComparer.Ordinal).Count() != tables.Count)
            throw new ArgumentException("A bulk write cannot name a controlled table more than once.", nameof(tables));
        foreach (var table in tables)
        {
            try { Write(table); }
            catch (Exception error)
            {
                throw new InvalidOperationException(
                    $"EXCEL.TABLE_WRITE_FAILED {table.TableId}: {error.Message}", error);
            }
            _writes++;
            if (!_failureConsumed && _failAfterWrites is { } limit && _writes >= limit)
            {
                _failureConsumed = true;
                throw new InvalidOperationException("EXCEL.INJECTED_MID_WRITE_FAILURE");
            }
        }
    }

    public void Remove(string tableId)
    {
        HostEffectLedger.Record("excel.workbook.table.remove");
        dynamic? worksheet = null;
        dynamic? listObject = FindListObject(tableId, out worksheet);
        dynamic? application = null;
        try
        {
            if (listObject is not null) listObject.Delete();
            if (!_createdSheets.Remove(tableId)) return;
            if (worksheet is null) worksheet = FindControlledSheet(tableId);
            if (worksheet is null) return;
            application = _workbook.Application;
            var priorAlerts = (bool)application.DisplayAlerts;
            try
            {
                application.DisplayAlerts = false;
                worksheet.Delete();
            }
            finally { application.DisplayAlerts = priorAlerts; }
        }
        finally
        {
            ReleaseCom(application);
            ReleaseCom(listObject);
            ReleaseCom(worksheet);
        }
    }

    private void Write(WorkbookTable table)
    {
        Validate(table);
        HostEffectLedger.Record("excel.workbook.table.write");
        var stage = "find_table";
        dynamic? worksheet = null;
        dynamic? listObject = FindListObject(table.TableId, out worksheet);
        dynamic? anchor = null;
        dynamic? target = null;
        dynamic? listObjects = null;
        dynamic? listColumns = null;
        dynamic? headerRange = null;
        dynamic? oldDataRange = null;
        dynamic? newDataRange = null;
        dynamic? replacement = null;
        try
        {
            if (listObject is null)
            {
                stage = "get_or_create_sheet";
                worksheet = GetOrCreateControlledSheet(table.TableId);
                stage = "create_anchor";
                anchor = worksheet.Range["A1"];
                stage = "create_target";
                target = anchor.Resize[table.Rows.Count, table.Rows[0].Count];
                stage = "create_write";
                target.NumberFormat = "@";
                target.Value2 = Values(table);
                stage = "create_table";
                listObjects = worksheet.ListObjects;
                listObject = listObjects.Add(1, target, Type.Missing, 1);
                listObject.Name = table.TableId;
                listObject.TableStyle = "TableStyleMedium2";
                return;
            }

            if (worksheet is null)
                throw new InvalidOperationException($"The worksheet for table {table.TableId} was not found.");
            stage = "existing_schema";
            listColumns = listObject.ListColumns;
            if ((int)listColumns.Count != table.Rows[0].Count)
                throw new InvalidOperationException(
                    $"Existing table {table.TableId} has a different column count.");
            stage = "existing_headers";
            headerRange = listObject.HeaderRowRange;
            if (!HeaderMatches(headerRange.Value2, table.Rows[0]))
                throw new InvalidOperationException(
                    $"Existing table {table.TableId} has different headers.");
            stage = "existing_clear_data";
            oldDataRange = listObject.DataBodyRange;
            if (oldDataRange is not null) oldDataRange.ClearContents();
            stage = "existing_anchor";
            anchor = worksheet.Range["A1"];
            stage = "existing_replacement";
            replacement = anchor.Resize[table.Rows.Count, table.Rows[0].Count];
            stage = "existing_resize";
            listObject.Resize(replacement);
            if (table.Rows.Count > 1)
            {
                stage = "existing_data_range";
                // A cleared table resized to one empty data row has a null DataBodyRange
                // until that row is populated. Write the declared body rectangle directly.
                dynamic dataAnchor = worksheet.Range["A2"];
                try { newDataRange = dataAnchor.Resize[table.Rows.Count - 1, table.Rows[0].Count]; }
                finally { ReleaseCom(dataAnchor); }
                stage = "existing_write_data";
                newDataRange.NumberFormat = "@";
                newDataRange.Value2 = DataValues(table);
            }
        }
        catch (Exception error)
        {
            throw new InvalidOperationException($"{stage}: {error.Message}", error);
        }
        finally
        {
            ReleaseCom(newDataRange);
            ReleaseCom(oldDataRange);
            ReleaseCom(headerRange);
            ReleaseCom(replacement);
            ReleaseCom(listColumns);
            ReleaseCom(listObject);
            ReleaseCom(listObjects);
            ReleaseCom(target);
            ReleaseCom(anchor);
            ReleaseCom(worksheet);
        }
    }

    private dynamic GetOrCreateControlledSheet(string tableId)
    {
        if (!SheetNames.TryGetValue(tableId, out var sheetName))
            throw new InvalidOperationException($"Table {tableId} is outside the controlled workbook schema.");
        dynamic worksheets = _workbook.Worksheets;
        try
        {
            for (var index = 1; index <= (int)worksheets.Count; index++)
            {
                dynamic? sheet = null;
                dynamic? used = null;
                try
                {
                    sheet = worksheets.Item(index);
                    if (!string.Equals((string)sheet.Name, sheetName, StringComparison.Ordinal)) continue;
                    used = sheet.UsedRange;
                    if (HasCellContent(used.Value2) || HasCellContent(used.Formula))
                        throw new InvalidOperationException($"Controlled sheet name {sheetName} already contains unrelated content.");
                    var matched = sheet;
                    sheet = null;
                    return matched;
                }
                finally
                {
                    ReleaseCom(used);
                    ReleaseCom(sheet);
                }
            }
            dynamic created = worksheets.Add();
            created.Name = sheetName;
            _createdSheets.Add(tableId);
            return created;
        }
        finally { ReleaseCom(worksheets); }
    }

    private dynamic? FindListObject(string tableId, out dynamic? worksheet)
    {
        worksheet = null;
        dynamic worksheets = _workbook.Worksheets;
        try
        {
            for (var sheetIndex = 1; sheetIndex <= (int)worksheets.Count; sheetIndex++)
            {
                dynamic? sheet = null;
                dynamic? tables = null;
                try
                {
                    sheet = worksheets.Item(sheetIndex);
                    tables = sheet.ListObjects;
                    for (var tableIndex = 1; tableIndex <= (int)tables.Count; tableIndex++)
                    {
                        dynamic? candidate = null;
                        try
                        {
                            candidate = tables.Item(tableIndex);
                            if (!string.Equals((string)candidate.Name, tableId, StringComparison.Ordinal)) continue;
                            worksheet = sheet;
                            sheet = null;
                            var matched = candidate;
                            candidate = null;
                            return matched;
                        }
                        finally { ReleaseCom(candidate); }
                    }
                }
                finally
                {
                    ReleaseCom(tables);
                    ReleaseCom(sheet);
                }
            }
            return null;
        }
        finally { ReleaseCom(worksheets); }
    }

    private dynamic? FindControlledSheet(string tableId)
    {
        if (!SheetNames.TryGetValue(tableId, out var sheetName)) return null;
        dynamic worksheets = _workbook.Worksheets;
        try
        {
            for (var index = 1; index <= (int)worksheets.Count; index++)
            {
                dynamic? sheet = null;
                try
                {
                    sheet = worksheets.Item(index);
                    if (!string.Equals((string)sheet.Name, sheetName, StringComparison.Ordinal)) continue;
                    var matched = sheet;
                    sheet = null;
                    return matched;
                }
                finally { ReleaseCom(sheet); }
            }
            return null;
        }
        finally { ReleaseCom(worksheets); }
    }

    private static object[,] Values(WorkbookTable table)
    {
        var values = new object[table.Rows.Count, table.Rows[0].Count];
        for (var row = 0; row < table.Rows.Count; row++)
            for (var column = 0; column < table.Rows[row].Count; column++)
                values[row, column] = table.Rows[row][column].Value ?? string.Empty;
        return values;
    }

    private static object[,] DataValues(WorkbookTable table)
    {
        var values = new object[table.Rows.Count - 1, table.Rows[0].Count];
        for (var row = 1; row < table.Rows.Count; row++)
            for (var column = 0; column < table.Rows[row].Count; column++)
                values[row - 1, column] = table.Rows[row][column].Value ?? string.Empty;
        return values;
    }

    private static bool HeaderMatches(object? values, IReadOnlyList<WorkbookCell> expected)
    {
        if (expected.Count == 1) return ToInvariantText(values) == expected[0].Value;
        if (values is not object[,] cells || cells.GetLength(1) != expected.Count) return false;
        var row = cells.GetLowerBound(0);
        var firstColumn = cells.GetLowerBound(1);
        return Enumerable.Range(0, expected.Count)
            .All(index => ToInvariantText(cells[row, firstColumn + index]) == expected[index].Value);
    }

    private static bool HasCellContent(object? values)
    {
        if (values is not Array cells)
            return !string.IsNullOrWhiteSpace(ToInvariantText(values));

        foreach (var cell in cells)
            if (!string.IsNullOrWhiteSpace(ToInvariantText(cell))) return true;
        return false;
    }

    private static void Validate(WorkbookTable table)
    {
        if (!SheetNames.ContainsKey(table.TableId))
            throw new ArgumentException($"Table {table.TableId} is outside the controlled workbook schema.");
        if (table.Rows.Count == 0 || table.Rows[0].Count == 0 ||
            table.Rows.Any(row => row.Count != table.Rows[0].Count))
            throw new ArgumentException($"Table {table.TableId} must be a nonempty rectangle.");
        if (table.Rows[0].Any(cell => string.IsNullOrWhiteSpace(cell.Value)) ||
            table.Rows[0].Select(cell => cell.Value).Distinct(StringComparer.Ordinal).Count() != table.Rows[0].Count)
            throw new ArgumentException($"Table {table.TableId} requires unique nonblank headers.");
        if (table.Rows.SelectMany(row => row).Any(cell => cell.Value is { Length: > ExcelCellCharacterLimit }))
            throw new ArgumentException($"Table {table.TableId} contains a cell longer than {ExcelCellCharacterLimit} characters.");
    }

    private static string? ToInvariantText(object? value) => value switch
    {
        null => null,
        string text => text.Length == 0 ? null : text,
        double number => number.ToString("R", CultureInfo.InvariantCulture),
        float number => number.ToString("R", CultureInfo.InvariantCulture),
        decimal number => number.ToString(CultureInfo.InvariantCulture),
        bool boolean => boolean.ToString(),
        DateTime date => date.ToString("O", CultureInfo.InvariantCulture),
        _ => Convert.ToString(value, CultureInfo.InvariantCulture)
    };

    internal static void ReleaseCom(object? value)
    {
        if (value is not null && Marshal.IsComObject(value))
            _ = Marshal.ReleaseComObject(value);
    }
}
