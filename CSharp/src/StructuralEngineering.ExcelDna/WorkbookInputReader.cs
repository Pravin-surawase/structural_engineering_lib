using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Fail-closed parser for the three immutable, versioned input tables.</summary>
public static class WorkbookInputReader
{
    private static readonly string[] ProjectHeaders =
        ["template_id", "workbook_id", "project_id", "project_request_json"];
    private static readonly string[] MemberHeaders =
        ["member_id", "request_id", "member_design_seed_json", "bar_path_request_json",
         "bbs_seed_json", "quantity_seed_json", "cost_seed_json", "package_seed_json",
         "optimization_seed_json"];
    private static readonly string[] OperationHeaders =
        ["member_id", "request_id", "row_id", "phase", "operation_semantic_id",
         "request_json", "rule_id", "scope_id", "check_scope", "expected_applicability",
         "code_data_binding_id"];

    /// <summary>Host entry point: only the three declared input tables are read.</summary>
    public static IReadOnlyList<WorkbookInputSnapshot> Read(IWorkbookTableStore store)
    {
        var tables = new List<WorkbookTable>();
        foreach (var tableId in new[] { WorkbookContract.ProjectTable, WorkbookContract.MembersTable, WorkbookContract.OperationsTable })
            if (store.TryRead(tableId, out var table)) tables.Add(table);
        var result = Read(tables);
        if (!result.Succeeded)
            throw new ArgumentException(string.Join("; ", result.Diagnostics.Select(diagnostic =>
                $"{diagnostic.Code} [{diagnostic.RowId ?? "workbook"}/{diagnostic.Field ?? "input"}]: {diagnostic.Message}")));
        return result.Snapshots;
    }

    public static WorkbookInputReadResult Read(IReadOnlyList<WorkbookTable> tables)
    {
        var diagnostics = new List<WorkbookDiagnostic>();
        var byId = tables.GroupBy(table => table.TableId, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        var allowedTables = new HashSet<string>(StringComparer.Ordinal)
        {
            WorkbookContract.ProjectTable,
            WorkbookContract.MembersTable,
            WorkbookContract.OperationsTable
        };
        foreach (var table in tables.Where(table => !allowedTables.Contains(table.TableId)))
            diagnostics.Add(new("EXCEL.TABLE_UNKNOWN", "error", "The workbook input contains an undeclared table.", table.TableId));
        var project = RequiredTable(byId, WorkbookContract.ProjectTable, ProjectHeaders, diagnostics);
        var members = RequiredTable(byId, WorkbookContract.MembersTable, MemberHeaders, diagnostics);
        var operations = RequiredTable(byId, WorkbookContract.OperationsTable, OperationHeaders, diagnostics);
        if (diagnostics.Count > 0) return new([], diagnostics);

        var projectRows = DataRows(project!, WorkbookContract.ProjectTable, ProjectHeaders.Length, diagnostics).ToArray();
        var memberRows = DataRows(members!, WorkbookContract.MembersTable, MemberHeaders.Length, diagnostics).ToArray();
        var operationRows = DataRows(operations!, WorkbookContract.OperationsTable, OperationHeaders.Length, diagnostics).ToArray();
        if (projectRows.Length != 1)
            diagnostics.Add(new("EXCEL.PROJECT_ROW_COUNT", "error", "StructuralProject must contain exactly one data row.", WorkbookContract.ProjectTable));
        if (memberRows.Length == 0)
            diagnostics.Add(new("EXCEL.MEMBER_ROW_REQUIRED", "error", "StructuralMembers must contain at least one member.", WorkbookContract.MembersTable));
        if (diagnostics.Count > 0) return new([], diagnostics);

        var projectRow = projectRows[0];
        var template = Value(projectRow, 0, WorkbookContract.ProjectTable, diagnostics, "template_id");
        var workbookId = Value(projectRow, 1, WorkbookContract.ProjectTable, diagnostics, "workbook_id");
        var projectId = Value(projectRow, 2, WorkbookContract.ProjectTable, diagnostics, "project_id");
        var projectJson = Value(projectRow, 3, WorkbookContract.ProjectTable, diagnostics, "project_request_json");
        BeamProjectRequest? projectRequest = Deserialize<BeamProjectRequest>(projectJson, WorkbookContract.ProjectTable, projectRow.RowNumber, "project_request_json", diagnostics);
        if (template != WorkbookContract.TemplateId)
            diagnostics.Add(new("EXCEL.TEMPLATE_UNSUPPORTED", "error", $"Expected {WorkbookContract.TemplateId}.", WorkbookContract.ProjectTable, "template_id"));
        if (projectRequest is not null && projectRequest.Project.ProjectId != projectId)
            diagnostics.Add(new("EXCEL.PROJECT_IDENTITY_MISMATCH", "error", "project_id must equal project_request_json.project_id.", WorkbookContract.ProjectTable, "project_id"));

        var memberInputs = new Dictionary<string, MemberInput>(StringComparer.Ordinal);
        var requestIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in memberRows)
        {
            var memberId = Value(row, 0, WorkbookContract.MembersTable, diagnostics, "member_id");
            var requestId = Value(row, 1, WorkbookContract.MembersTable, diagnostics, "request_id");
            var seedJson = Value(row, 2, WorkbookContract.MembersTable, diagnostics, "member_design_seed_json");
            var pathsJson = ReadPaths(Optional(row, 3), memberId, row.RowNumber, diagnostics);
            if (!memberInputs.TryAdd(memberId, new(row, memberId, requestId, seedJson,
                pathsJson, Optional(row, 4), Optional(row, 5), Optional(row, 6), Optional(row, 7), Optional(row, 8))))
                diagnostics.Add(new("EXCEL.MEMBER_DUPLICATE", "error", "member_id must be unique.", WorkbookContract.MembersTable, "member_id"));
            if (!requestIds.Add(requestId))
                diagnostics.Add(new("EXCEL.REQUEST_DUPLICATE", "error", "request_id must be unique per member snapshot.", WorkbookContract.MembersTable, "request_id"));
            var seed = Deserialize<WorkbookMemberDesignSeed>(seedJson, WorkbookContract.MembersTable, row.RowNumber, "member_design_seed_json", diagnostics);
            if (seed is not null && seed.MemberId != memberId)
                diagnostics.Add(new("EXCEL.MEMBER_IDENTITY_MISMATCH", "error", "member_id must equal member_design_seed_json.member_id.", WorkbookContract.MembersTable, "member_id"));
            ValidateOptional<WorkbookBbsSeed>(Optional(row, 4), WorkbookContract.MembersTable, row.RowNumber, "bbs_seed_json", diagnostics, value => value.MemberId == memberId);
            ValidateOptional<WorkbookQuantitySeed>(Optional(row, 5), WorkbookContract.MembersTable, row.RowNumber, "quantity_seed_json", diagnostics, value => value.MemberId == memberId);
            ValidateOptional<WorkbookCostSeed>(Optional(row, 6), WorkbookContract.MembersTable, row.RowNumber, "cost_seed_json", diagnostics, value => value.MemberId == memberId);
            ValidateOptional<WorkbookCalculationPackageSeed>(Optional(row, 7), WorkbookContract.MembersTable, row.RowNumber, "package_seed_json", diagnostics, value => value.Metadata.MemberId == memberId);
            var optimization = DeserializeOptional<WorkbookOptimizationSeed>(Optional(row, 8), WorkbookContract.MembersTable, row.RowNumber, "optimization_seed_json", diagnostics);
            if (optimization is not null && optimization.Domain.MemberId != memberId)
                diagnostics.Add(new("EXCEL.OPTIMIZATION_IDENTITY_MISMATCH", "error", "optimization_seed_json.domain.member_id must match member_id.", WorkbookContract.MembersTable, $"row:{row.RowNumber}.optimization_seed_json"));
        }

        var grouped = new Dictionary<string, List<WorkbookOperationRow>>(StringComparer.Ordinal);
        var operationIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in operationRows)
        {
            var memberId = Value(row, 0, WorkbookContract.OperationsTable, diagnostics, "member_id");
            var requestId = Value(row, 1, WorkbookContract.OperationsTable, diagnostics, "request_id");
            var rowId = Value(row, 2, WorkbookContract.OperationsTable, diagnostics, "row_id");
            var phase = Value(row, 3, WorkbookContract.OperationsTable, diagnostics, "phase");
            var operation = Value(row, 4, WorkbookContract.OperationsTable, diagnostics, "operation_semantic_id");
            var requestJson = Value(row, 5, WorkbookContract.OperationsTable, diagnostics, "request_json");
            if (!memberInputs.TryGetValue(memberId, out var member))
            {
                diagnostics.Add(new("EXCEL.OPERATION_ORPHAN", "error", "Operation member_id has no StructuralMembers row.", WorkbookContract.OperationsTable, "member_id"));
                continue;
            }
            if (member.RequestId != requestId)
                diagnostics.Add(new("EXCEL.OPERATION_REQUEST_MISMATCH", "error", "Operation request_id must match its member row.", WorkbookContract.OperationsTable, "request_id"));
            if (!operationIds.Add(memberId + "\u001f" + rowId))
                diagnostics.Add(new("EXCEL.OPERATION_DUPLICATE", "error", "row_id must be unique within a member.", WorkbookContract.OperationsTable, "row_id"));
            if (phase is not ("topology" or "leaf"))
            {
                diagnostics.Add(new("EXCEL.OPERATION_PHASE_INVALID", "error", "phase must be topology or leaf.", WorkbookContract.OperationsTable, "phase"));
                continue;
            }
            WorkbookOperationRow? operationRow = phase == "topology"
                ? Topology(rowId, operation, requestJson, row, diagnostics)
                : Leaf(rowId, operation, requestJson, row, diagnostics);
            if (operationRow is not null)
            {
                if (!grouped.TryGetValue(memberId, out var memberOperationRows))
                {
                    memberOperationRows = [];
                    grouped.Add(memberId, memberOperationRows);
                }
                memberOperationRows.Add(operationRow);
            }
        }

        var snapshots = new List<WorkbookInputSnapshot>();
        foreach (var member in memberInputs.Values.OrderBy(item => item.MemberId, StringComparer.Ordinal))
        {
            var rows = grouped.GetValueOrDefault(member.MemberId, []);
            var topology = rows.Where(row => row.TableId == "topology").ToArray();
            var leaves = rows.Where(row => row.TableId == "leaf").ToArray();
            if (topology.Length != 1)
                diagnostics.Add(new("EXCEL.TOPOLOGY_COUNT", "error", "Each member requires exactly one topology operation row.", WorkbookContract.OperationsTable, member.MemberId));
            if (leaves.Length == 0)
                diagnostics.Add(new("EXCEL.LEAF_REQUIRED", "error", "Each member requires at least one leaf operation row.", WorkbookContract.OperationsTable, member.MemberId));
            snapshots.Add(new(template, workbookId, projectId, member.MemberId, member.RequestId,
                projectJson, topology, leaves, member.MemberSeedJson, member.PathsJson,
                member.BbsJson, member.QuantityJson, member.CostJson, member.PackageJson,
                member.OptimizationJson));
        }
        return diagnostics.Count == 0 ? new(snapshots, diagnostics) : new([], diagnostics);
    }

    private static WorkbookOperationRow? Topology(string rowId, string operation, string requestJson, DataRow row, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (operation != "structural.beam_topology.define/v1")
        {
            diagnostics.Add(new("EXCEL.TOPOLOGY_OPERATION_INVALID", "error", "Topology phase must call structural.beam_topology.define/v1.", WorkbookContract.OperationsTable, "operation_semantic_id"));
            return null;
        }
        _ = Deserialize<BeamTopologyDefinitionRequest>(requestJson, WorkbookContract.OperationsTable, row.RowNumber, "request_json", diagnostics);
        if (Optional(row, 6) is not null || Optional(row, 7) is not null || Optional(row, 8) is not null || Optional(row, 9) is not null || Optional(row, 10) is not null)
            diagnostics.Add(new("EXCEL.TOPOLOGY_METADATA_FORBIDDEN", "error", "Topology rows cannot carry leaf metadata.", WorkbookContract.OperationsTable, "rule_id"));
        return new(rowId, operation, requestJson, "topology");
    }

    private static string? ReadPaths(string? json, string memberId, int rowNumber, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (json is null) return null;
        try
        {
            using var document = JsonDocument.Parse(json);
            if (!document.RootElement.TryGetProperty("longitudinal_paths", out _))
            {
                var request = Deserialize<BarPathRequest>(json, WorkbookContract.MembersTable, rowNumber, "bar_path_request_json", diagnostics);
                if (request is not null && request.MemberId != memberId)
                    diagnostics.Add(new("EXCEL.MEMBER_IDENTITY_MISMATCH", "error", "Seed identity must match member_id.", WorkbookContract.MembersTable, $"row:{rowNumber}.bar_path_request_json"));
                return json;
            }
        }
        catch (JsonException error)
        {
            diagnostics.Add(new("EXCEL.JSON_INVALID", "error", error.Message, WorkbookContract.MembersTable, $"row:{rowNumber}.bar_path_request_json"));
            return null;
        }

        var seed = Deserialize<WorkbookBarPathSeed>(json, WorkbookContract.MembersTable, rowNumber, "bar_path_request_json", diagnostics);
        if (seed is null) return null;
        if (seed.MemberId != memberId)
        {
            diagnostics.Add(new("EXCEL.MEMBER_IDENTITY_MISMATCH", "error", "Seed identity must match member_id.", WorkbookContract.MembersTable, $"row:{rowNumber}.bar_path_request_json"));
            return null;
        }
        var paths = seed.LongitudinalPaths.ToList();
        var links = seed.TransverseLinks;
        if (links is not null)
        {
            var delta = links.EndStationXMm - links.StartStationXMm;
            var steps = links.SpacingMm == 0 ? double.NaN : delta / links.SpacingMm;
            if (!double.IsFinite(delta) || !double.IsFinite(links.SpacingMm) || links.SpacingMm <= 0 ||
                delta < 0 || Math.Abs(steps - Math.Round(steps, MidpointRounding.ToEven)) > seed.GeometryToleranceMm)
            {
                diagnostics.Add(new("EXCEL.LINK_PATTERN_INVALID", "error", "Transverse link pattern requires finite aligned bounds and positive spacing.", WorkbookContract.MembersTable, $"row:{rowNumber}.bar_path_request_json"));
                return null;
            }
            for (var index = 0; index <= (int)Math.Round(steps, MidpointRounding.ToEven); index++)
            {
                var station = links.StartStationXMm + index * links.SpacingMm;
                var id = $"{seed.MemberId}-L{station:0000}";
                paths.Add(new(id, links.BarMark, BarPathRole.TransverseLink, links.Layer,
                    links.DiameterMm, links.SteelGradeNPerMm2,
                    [new($"{id}-1", new(station, links.LeftXFromLeftMm, links.TopYFromTopMm), links.BendRadiusMm, links.BendKind),
                     new($"{id}-2", new(station, links.RightXFromLeftMm, links.TopYFromTopMm), links.BendRadiusMm, links.BendKind),
                     new($"{id}-3", new(station, links.RightXFromLeftMm, links.BottomYFromTopMm), links.BendRadiusMm, links.BendKind),
                     new($"{id}-4", new(station, links.LeftXFromLeftMm, links.BottomYFromTopMm), links.BendRadiusMm, links.BendKind)], Closed: true));
            }
        }
        if (paths.Select(path => path.BarId).Distinct(StringComparer.Ordinal).Count() != paths.Count)
        {
            diagnostics.Add(new("EXCEL.BAR_PATH_DUPLICATE", "error", "Expanded bar path identifiers must be unique.", WorkbookContract.MembersTable, $"row:{rowNumber}.bar_path_request_json"));
            return null;
        }
        return JsonSerializer.Serialize(new BarPathRequest(seed.ProfileId, seed.ProjectBasisId,
            seed.CriteriaRevisionId, seed.MemberId, seed.PhysicalSpanId, seed.TopologyRevisionId,
            seed.DetailRevisionId, seed.CoordinateSystem, seed.MemberStartXMm, seed.MemberEndXMm,
            seed.SectionWidthMm, seed.SectionDepthMm, paths, seed.StockLengthsMm,
            seed.GeometryToleranceMm), WorkbookContract.Json);
    }

    private static WorkbookOperationRow? Leaf(string rowId, string operation, string requestJson, DataRow row, ICollection<WorkbookDiagnostic> diagnostics)
    {
        var rule = Value(row, 6, WorkbookContract.OperationsTable, diagnostics, "rule_id");
        var scopeId = Value(row, 7, WorkbookContract.OperationsTable, diagnostics, "scope_id");
        var scope = EnumValue<CheckScope>(Value(row, 8, WorkbookContract.OperationsTable, diagnostics, "check_scope"), row, "check_scope", diagnostics);
        var applicability = EnumValue<ApplicabilityState>(Value(row, 9, WorkbookContract.OperationsTable, diagnostics, "expected_applicability"), row, "expected_applicability", diagnostics);
        var binding = Value(row, 10, WorkbookContract.OperationsTable, diagnostics, "code_data_binding_id");
        ValidateLeafRequest(operation, requestJson, row, diagnostics);
        if (scope is null || applicability is null || applicability == ApplicabilityState.Unknown) return null;
        return new(rowId, operation, requestJson, "leaf", rule, scopeId, scope, applicability, binding);
    }

    private static void ValidateLeafRequest(string operation, string requestJson, DataRow row, ICollection<WorkbookDiagnostic> diagnostics)
    {
        switch (operation)
        {
            case "structural.action_snapshot.normalize/v1": ValidateRequest<RawActionSnapshot>(requestJson, row, diagnostics); break;
            case "structural.beam_line.solve/v1": ValidateRequest<BeamLineRequest>(requestJson, row, diagnostics); break;
            case "structural.reinforcement.bar_area/v1": ValidateRequest<BarAreaRequest>(requestJson, row, diagnostics); break;
            case "structural.reinforcement.mass_per_length/v1": ValidateRequest<MassPerLengthRequest>(requestJson, row, diagnostics); break;
            case "structural.reinforcement.effective_depth/v1": ValidateRequest<WorkbookEffectiveDepthRequest>(requestJson, row, diagnostics); break;
            case "structural.reinforcement_geometry.evaluate/v1": ValidateRequest<GeometryRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.flexural_capacity/v1": ValidateRequest<FlexuralCapacityRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.flexure.check/v1": ValidateRequest<FlexureCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.shear_capacity/v1": ValidateRequest<ShearCapacityRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.shear.check/v1": ValidateRequest<ShearCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.torsion.check/v1": ValidateRequest<TorsionCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.deflection_limit/v1": ValidateRequest<DeflectionLimitRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.crack_width_limit/v1": ValidateRequest<CrackWidthLimitRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.deflection.check/v1": ValidateRequest<DeflectionCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.crack_width.check/v1": ValidateRequest<CrackWidthCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.reinforcement.development_length/v1": ValidateRequest<DevelopmentLengthRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.anchorage.check/v1": ValidateRequest<AnchorageCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.lap_curtailment.check/v1": ValidateRequest<LapCurtailmentCheckRequest>(requestJson, row, diagnostics); break;
            case "is456.beam.seismic_detailing.check/v1": ValidateRequest<SeismicDetailingCheckRequest>(requestJson, row, diagnostics); break;
            case "structural.reinforcement_arrangement.check/v1": ValidateRequest<ReinforcementArrangementCheckRequest>(requestJson, row, diagnostics); break;
            default:
                diagnostics.Add(new("EXCEL.OPERATION_UNKNOWN", "error", "operation_semantic_id is not a declared native WP01-WP08 operation.", WorkbookContract.OperationsTable, $"row:{row.RowNumber}.operation_semantic_id"));
                break;
        }
    }

    private static void ValidateRequest<T>(string json, DataRow row, ICollection<WorkbookDiagnostic> diagnostics) where T : class =>
        _ = Deserialize<T>(json, WorkbookContract.OperationsTable, row.RowNumber, "request_json", diagnostics);

    private static WorkbookTable? RequiredTable(IReadOnlyDictionary<string, WorkbookTable[]> tables, string id, IReadOnlyList<string> headers, ICollection<WorkbookDiagnostic> diagnostics)
    {
        if (!tables.TryGetValue(id, out var matches) || matches.Length != 1)
        {
            diagnostics.Add(new("EXCEL.TABLE_REQUIRED", "error", $"Exactly one {id} table is required.", id));
            return null;
        }
        var table = matches[0];
        if (table.Rows.Count == 0 || table.Rows[0].Count != headers.Count || headers.Where((header, index) => table.Rows[0][index].Value != header).Any())
            diagnostics.Add(new("EXCEL.TABLE_HEADER_INVALID", "error", "Table headers must exactly match the versioned contract and order.", id, "header"));
        return table;
    }

    private static IEnumerable<DataRow> DataRows(WorkbookTable table, string tableId, int columns, ICollection<WorkbookDiagnostic> diagnostics)
    {
        for (var index = 1; index < table.Rows.Count; index++)
        {
            var row = table.Rows[index];
            if (row.Count != columns)
            {
                diagnostics.Add(new("EXCEL.TABLE_WIDTH_INVALID", "error", $"Expected {columns} columns.", tableId, $"row:{index + 1}"));
                continue;
            }
            if (row.Any(cell => cell.Value is { Length: > 32767 }))
                diagnostics.Add(new("EXCEL.CELL_TOO_LARGE", "error", "Workbook cells cannot exceed 32767 characters.", tableId, $"row:{index + 1}"));
            yield return new(index + 1, row);
        }
    }

    private static string Value(DataRow row, int index, string table, ICollection<WorkbookDiagnostic> diagnostics, string field)
    {
        var value = row.Cells[index].Value;
        if (string.IsNullOrWhiteSpace(value))
        {
            diagnostics.Add(new("EXCEL.INPUT_REQUIRED", "error", "A nonblank value is required.", table, $"row:{row.RowNumber}.{field}"));
            return string.Empty;
        }
        return value;
    }

    private static string? Optional(DataRow row, int index) => string.IsNullOrWhiteSpace(row.Cells[index].Value) ? null : row.Cells[index].Value;

    private static T? Deserialize<T>(string json, string table, int row, string field, ICollection<WorkbookDiagnostic> diagnostics) where T : class
    {
        try { return JsonSerializer.Deserialize<T>(json, WorkbookContract.Json) ?? throw new JsonException("JSON cannot be null."); }
        catch (JsonException error)
        {
            diagnostics.Add(new("EXCEL.JSON_INVALID", "error", error.Message, table, $"row:{row}.{field}"));
            return null;
        }
    }

    private static T? DeserializeOptional<T>(string? json, string table, int row, string field, ICollection<WorkbookDiagnostic> diagnostics) where T : class =>
        json is null ? null : Deserialize<T>(json, table, row, field, diagnostics);

    private static void ValidateOptional<T>(string? json, string table, int row, string field, ICollection<WorkbookDiagnostic> diagnostics, Func<T, bool> identity) where T : class
    {
        var value = DeserializeOptional<T>(json, table, row, field, diagnostics);
        if (value is not null && !identity(value)) diagnostics.Add(new("EXCEL.MEMBER_IDENTITY_MISMATCH", "error", "Seed identity must match member_id.", table, $"row:{row}.{field}"));
    }

    private static TEnum? EnumValue<TEnum>(string value, DataRow row, string field, ICollection<WorkbookDiagnostic> diagnostics) where TEnum : struct, Enum
    {
        try { return JsonSerializer.Deserialize<TEnum>($"\"{value}\"", WorkbookContract.Json); }
        catch (JsonException)
        {
            diagnostics.Add(new("EXCEL.ENUM_INVALID", "error", "Use the declared snake_case enum value.", WorkbookContract.OperationsTable, $"row:{row.RowNumber}.{field}"));
            return null;
        }
    }

    private sealed record DataRow(int RowNumber, IReadOnlyList<WorkbookCell> Cells);
    private sealed record MemberInput(DataRow Row, string MemberId, string RequestId,
        string MemberSeedJson, string? PathsJson, string? BbsJson, string? QuantityJson,
        string? CostJson, string? PackageJson, string? OptimizationJson);
}

public sealed record WorkbookInputReadResult(
    IReadOnlyList<WorkbookInputSnapshot> Snapshots,
    IReadOnlyList<WorkbookDiagnostic> Diagnostics)
{
    public bool Succeeded => Diagnostics.Count == 0;
}
