using StructuralEngineering.ExcelDna;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructAutomate.Tests;

public class WorkbookInputReaderTests
{
    [Fact]
    public void TypicalSampleHasVersionedTablesAndReadsTwentyGroupedSnapshots()
    {
        var tables = SampleWorkbookData.CreateTypicalTables();

        Assert.Equal(2, Table(tables, WorkbookContract.ProjectTable).Rows.Count);
        Assert.Equal(21, Table(tables, WorkbookContract.MembersTable).Rows.Count);
        Assert.Equal(201, Table(tables, WorkbookContract.OperationsTable).Rows.Count);
        Assert.All(tables.SelectMany(table => table.Rows).SelectMany(row => row), cell => Assert.True(cell.Value is null || cell.Value.Length <= 32767));

        var parsed = WorkbookInputReader.Read(tables);

        Assert.True(parsed.Succeeded);
        Assert.Equal(20, parsed.Snapshots.Count);
        Assert.All(parsed.Snapshots, snapshot =>
        {
            Assert.Equal(WorkbookContract.TemplateId, snapshot.TemplateId);
            Assert.Equal("SAMPLE-PROJECT", snapshot.ProjectId);
            Assert.Contains(snapshot.MemberId, snapshot.RequestId, StringComparison.Ordinal);
            Assert.Single(snapshot.TopologyRows);
            Assert.Equal(9, snapshot.LeafOperationRows.Count);
        });
        var expandedPaths = WorkbookOperationDispatcher.Deserialize<BarPathRequest>(parsed.Snapshots[0].BarPathRequestJson!);
        Assert.Equal(41, expandedPaths.Paths.Count(path => path.Role == BarPathRole.TransverseLink));
    }

    [Fact]
    public void HeaderDuplicateAndOrphanRowsFailClosed()
    {
        var source = SampleWorkbookData.CreateTypicalTables();
        var malformedHeader = Replace(source, WorkbookContract.MembersTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 0 ? ReplaceCell(row, 0, "member") : row)] });
        var duplicate = Replace(source, WorkbookContract.OperationsTable, table =>
            table with { Rows = [.. table.Rows, table.Rows[1]] });
        var orphan = Replace(source, WorkbookContract.OperationsTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 1 ? ReplaceCell(row, 0, "ORPHAN") : row)] });
        var unsupportedTemplate = Replace(source, WorkbookContract.ProjectTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 1 ? ReplaceCell(row, 0, "unknown-template/v1") : row)] });
        var memberIdentityMismatch = Replace(source, WorkbookContract.MembersTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 1 ? ReplaceCell(row, 0, "B999") : row)] });

        Assert.False(WorkbookInputReader.Read(malformedHeader).Succeeded);
        Assert.Contains(WorkbookInputReader.Read(duplicate).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.OPERATION_DUPLICATE");
        Assert.Contains(WorkbookInputReader.Read(orphan).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.OPERATION_ORPHAN");
        Assert.Contains(WorkbookInputReader.Read(unsupportedTemplate).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.TEMPLATE_UNSUPPORTED");
        Assert.Contains(WorkbookInputReader.Read(memberIdentityMismatch).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.MEMBER_IDENTITY_MISMATCH");
    }

    [Fact]
    public void UnknownEnumAndMalformedRequestFailWithRowFieldDiagnostic()
    {
        var source = SampleWorkbookData.CreateTypicalTables();
        var unknownEnum = Replace(source, WorkbookContract.OperationsTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 2 ? ReplaceCell(row, 8, "unknown_scope") : row)] });
        var malformedJson = Replace(source, WorkbookContract.OperationsTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 2 ? ReplaceCell(row, 5, "{") : row)] });
        var unknownOperation = Replace(source, WorkbookContract.OperationsTable, table =>
            table with { Rows = [.. table.Rows.Select((row, index) => index == 2 ? ReplaceCell(row, 4, "unknown.operation/v1") : row)] });

        Assert.Contains(WorkbookInputReader.Read(unknownEnum).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.ENUM_INVALID" && diagnostic.Field!.Contains("check_scope", StringComparison.Ordinal));
        Assert.Contains(WorkbookInputReader.Read(malformedJson).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.JSON_INVALID" && diagnostic.Field!.Contains("request_json", StringComparison.Ordinal));
        Assert.Contains(WorkbookInputReader.Read(unknownOperation).Diagnostics, diagnostic => diagnostic.Code == "EXCEL.OPERATION_UNKNOWN" && diagnostic.Field!.Contains("operation_semantic_id", StringComparison.Ordinal));
    }

    [Fact]
    public void PublicStoreReaderAndBatchCalculationKeepCellsWithinExcelLimit()
    {
        var store = new Store(SampleWorkbookData.CreateTypicalTables());
        var snapshots = WorkbookInputReader.Read(store);
        var result = new WorkbookCommandEngine().ExecuteBatch(WorkbookCommandKind.Calculate, snapshots, store, "2026-09-04T00:00:00Z");

        Assert.True(result.Receipt.State == WorkbookReceiptState.Completed,
            string.Join("; ", result.Results.SelectMany(item => item.Diagnostics)
                .Select(diagnostic => $"{diagnostic.Code}: {diagnostic.Message}")));
        Assert.True(result.Freshness.IsCurrent);
        Assert.All(result.OutputTables.SelectMany(table => table.Rows).SelectMany(row => row), cell => Assert.True(cell.Value is null || cell.Value.Length <= 32767));
    }

    private static WorkbookTable Table(IReadOnlyList<WorkbookTable> tables, string id) => tables.Single(table => table.TableId == id);

    private static IReadOnlyList<WorkbookTable> Replace(IReadOnlyList<WorkbookTable> tables, string id, Func<WorkbookTable, WorkbookTable> edit) =>
        tables.Select(table => table.TableId == id ? edit(table) : table).ToArray();

    private static IReadOnlyList<WorkbookCell> ReplaceCell(IReadOnlyList<WorkbookCell> row, int index, string? value) =>
        row.Select((cell, position) => position == index ? new WorkbookCell(value) : cell).ToArray();

    private sealed class Store : IWorkbookTableStore
    {
        private readonly Dictionary<string, WorkbookTable> _tables;
        public Store(IReadOnlyList<WorkbookTable> tables) => _tables = tables.ToDictionary(table => table.TableId, StringComparer.Ordinal);
        public bool TryRead(string tableId, out WorkbookTable table) => _tables.TryGetValue(tableId, out table!);
        public void BulkWrite(IReadOnlyList<WorkbookTable> tables)
        {
            foreach (var table in tables) _tables[table.TableId] = table;
        }
        public void Remove(string tableId) => _tables.Remove(tableId);
    }
}
