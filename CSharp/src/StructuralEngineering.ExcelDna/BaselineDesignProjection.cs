using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Bounded worksheet projection of native WP11 evidence; it performs no engineering calculation.</summary>
public static class BaselineDesignProjection
{
    private const int Columns = 12;
    public static object[,] Summary(BaselineBatchDesignResult result, string status)
    {
        ArgumentNullException.ThrowIfNull(result);
        var rows = new List<object[]> { Row("BASELINE BEAM DESIGNS"), Row(status), Row("Request ID", result.RequestId), Row("Snapshot ID", result.SnapshotId), Row("Project", result.AcceptedInputs.Project.ProjectId), Row("Input revision", result.AcceptedInputs.Project.RevisionId), Row("Candidate limit", result.Options.MaximumCandidates), Row("Members", result.Members.Count), Header("Member ID", "State", "Top bars", "Bottom bars", "Link", "Depths mm", "Checks", "Diagnostics", "Effective input ID", "Evaluated", "Enumerated", "Status") };
        foreach (var member in result.Members)
        {
            var a = member.Design?.Arrangement;
            rows.Add(Row(member.MemberId, member.State, a is null ? "" : $"{a.TopCount}x{a.TopDiameterMm:g}/L{a.TopLayers}", a is null ? "" : $"{a.BottomCount}x{a.BottomDiameterMm:g}/L{a.BottomLayers}", a is null ? "" : $"{a.Link.DiameterMm:g}@{a.Link.SpacingMm:g}", a is null ? "" : $"top {a.TopEffectiveDepthMm:g}; bottom {a.BottomEffectiveDepthMm:g}", member.Design?.Checks.Count ?? 0, string.Join("; ", member.Diagnostics.Select(x => x.Code)), member.EffectiveInputId, member.EvaluatedCandidates, member.EnumeratedCandidates, status));
        }
        return Matrix(rows);
    }

    public static object[,] Details(BaselineMemberDesignResult member, AnalysisSnapshot snapshot, string status, string externalResultPath)
    {
        ArgumentNullException.ThrowIfNull(member); ArgumentNullException.ThrowIfNull(snapshot);
        var rows = new List<object[]> { Row("BASELINE DESIGN DETAILS"), Row(status), Row("Member", member.MemberId), Row("Snapshot", snapshot.SnapshotId), Row("External result", externalResultPath), Row("Effective input", member.EffectiveInputId), Row("Engine", member.EngineRevisionId), Row("State", member.State), Header("Group / item", "Scope", "Status", "Count", "Maximum utilization", "Governing source", "Geometry / provenance", "Action rows", "Diagnostics", "Result ID", "Input ID", "Notes") };
        if (member.Design is null)
        {
            rows.Add(Row("No design", "member", member.State, 0, "", "", "", "", string.Join("; ", member.Diagnostics.Select(x => x.FieldOrLocation + ": " + x.Message)), "", member.EffectiveInputId, "No arrangement/result is available."));
            return Matrix(rows);
        }
        foreach (var group in member.Design.Checks.GroupBy(c => new { c.RuleId, c.Scope, c.Result.Execution, c.Result.Applicability, c.Result.Engineering, c.Result.Completeness, c.Result.Freshness }))
        {
            var checks = group.ToArray(); var governing = checks.OrderByDescending(c => Utilization(c.Result.Outputs)).First(); var action = governing.ActionRowIds.FirstOrDefault();
            var utilization = Utilization(governing.Result.Outputs);
            var source = (utilization is null ? "Example: " : "Governing: ") + Source(snapshot, action);
            rows.Add(Row(group.Key.RuleId, group.Key.Scope, $"{group.Key.Execution}/{group.Key.Applicability}/{group.Key.Engineering}/{group.Key.Completeness}/{group.Key.Freshness}", checks.Length, utilization is { } u ? u : "unavailable", source, string.Join("; ", governing.Result.Provenance.SourceReferences), action ?? "member scope", string.Join("; ", checks.SelectMany(c => c.Result.Diagnostics).Select(d => d.FieldOrLocation + ": " + d.Message).Distinct()), governing.Result.ResultId, governing.Result.NormalizedInputId, checks.Length == 1 ? "required scope accounted" : "grouped required scopes accounted"));
        }
        var a = member.Design.Arrangement;
        foreach (var bar in a.Bars) rows.Add(Row("Bar " + bar.BarId, bar.Face, "actual", 1, "", "", $"phi {bar.DiameterMm:g}; x {bar.XFromLeftMm:g}; y {bar.YFromTopMm:g}; layer {bar.Layer}", "", "", a.RevisionId, member.EffectiveInputId, "selected reinforcement"));
        foreach (var path in a.Paths) rows.Add(Row("Path " + path.BarId, "bar path", "actual", 1, "", "", $"start {path.StartStationMm:g}; end {path.EndStationMm:g}; length {path.EndStationMm - path.StartStationMm:g}", "", "", a.RevisionId, member.EffectiveInputId, "full selected path"));
        rows.Add(Row("Link " + a.Link.LinkId, "link", "actual", 1, "", "", $"phi {a.Link.DiameterMm:g}; spacing {a.Link.SpacingMm:g}; legs V2={a.Link.LegsV2}, V3={a.Link.LegsV3}", "", "", a.RevisionId, member.EffectiveInputId, "selected closed link"));
        foreach (var diagnostic in member.Diagnostics) rows.Add(Row("Diagnostic", "member", diagnostic.Severity, 1, "", "", "", "", diagnostic.Code, "", member.EffectiveInputId, diagnostic.Message));
        return Matrix(rows);
    }
    private static double? Utilization(JsonElement? output)
    {
        if (output is not { ValueKind: JsonValueKind.Object } value) return null;
        foreach (var name in new[] { "utilization", "governing_utilization" }) if (value.TryGetProperty(name, out var property) && property.TryGetDouble(out var number)) return number;
        return null;
    }
    private static string Source(AnalysisSnapshot snapshot, string? rowId)
    { var row = snapshot.ActionRows.FirstOrDefault(x => x.RowId == rowId); return row is null ? "no action row" : $"{row.OutputCaseName}; x={snapshot.Stations.FirstOrDefault(x => x.StationId == row.StationId)?.PhysicalStationMm:g} mm; {row.RowId}"; }
    private static object[] Header(params object[] values) => Row(values);
    private static object[] Row(params object[] values) { var row = new object[Columns]; for (var i = 0; i < Math.Min(values.Length, Columns); i++) row[i] = values[i] is Enum e ? e.ToString() : values[i]; return row; }
    private static object[,] Matrix(IReadOnlyList<object[]> rows) { var matrix = new object[rows.Count, Columns]; for (var r = 0; r < rows.Count; r++) for (var c = 0; c < Columns; c++) matrix[r, c] = rows[r][c] ?? ""; return matrix; }
}
