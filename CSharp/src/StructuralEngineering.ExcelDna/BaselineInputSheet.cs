using System.Globalization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Host-free, rectangular workbook contract for the WP11 Design Inputs sheet.</summary>
public static class BaselineInputSheet
{
    public const string SheetName = "Design Inputs";
    public const int HeaderRow = 0;
    public const int FirstDataRow = 1;
    private static readonly string[] Headers = ["Category", "Source ID", "Field", "Value", "Unit", "Origin"];

    public static object[,] Create(AnalysisSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        var rows = new List<Row>
        {
            new("Project", "project", "project_id", "", "text", "required engineering input"),
            new("Project", "project", "revision_id", "", "text", "required engineering input"),
            new("Project", "project", "origin", "", "text", "required engineering input"),
            new("Project", "project", "evidence_reference", "", "text", "required engineering input"),
            new("Catalogue", "catalogue", "revision_id", "baseline-catalogue-v1", "text", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "longitudinal_diameters_mm", "12,16,20", "mm", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "link_diameters_mm", "8,10", "mm", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "link_spacings_mm", "250,200,150,100", "mm", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "bar_counts", "2,3,4,6", "count", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "layers", "1,2", "count", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "stock_lengths_mm", "6000,12000", "mm", "demo default — accept inputs required"),
            new("Catalogue", "catalogue", "maximum_candidates", "1000", "count", "demo default — accept inputs required")
        };
        foreach (var material in snapshot.Materials.OrderBy(x => x.MaterialId, StringComparer.Ordinal))
        {
            rows.Add(new("Material", material.MaterialId, "concrete_strength_n_per_mm2", "", "N/mm²", "required engineering input"));
            rows.Add(new("Material", material.MaterialId, "steel_yield_strength_n_per_mm2", "", "N/mm²", "required engineering input"));
            rows.Add(new("Material", material.MaterialId, "link_steel_yield_strength_n_per_mm2", "", "N/mm²", "required engineering input"));
            rows.Add(new("Material", material.MaterialId, "steel_modulus_n_per_mm2", "", "N/mm²", "required engineering input"));
            rows.Add(new("Source", material.MaterialId, "material_source_name", material.SourceName, "text", "snapshot read-only"));
        }
        foreach (var member in snapshot.Members.OrderBy(x => x.MemberId, StringComparer.Ordinal))
        {
            AddMemberRows(rows, member);
            rows.Add(new("Source", member.MemberId, "source_object_id", member.ObjectId, "text", "snapshot read-only"));
            rows.Add(new("Source", member.MemberId, "source_section_id", member.SectionId, "text", "snapshot read-only"));
        }
        var actionSelectionIds = snapshot.ActionRows.Select(x => x.SelectionId).ToHashSet(StringComparer.Ordinal);
        foreach (var selection in snapshot.ResultSelections.Where(x => actionSelectionIds.Contains(x.SelectionId)).OrderBy(x => x.SelectionId, StringComparer.Ordinal))
        {
            rows.Add(new("Role", selection.SelectionId, "role", "", "uls|sls_total|sls_sustained", "required engineering input"));
            rows.Add(new("Source", selection.SelectionId, "source_selection", selection.SourceName, "text", "snapshot read-only"));
        }
        var cells = new object[rows.Count + 1, Headers.Length];
        for (var col = 0; col < Headers.Length; col++) cells[HeaderRow, col] = Headers[col];
        for (var row = 0; row < rows.Count; row++)
        {
            var value = rows[row];
            cells[row + FirstDataRow, 0] = value.Category; cells[row + FirstDataRow, 1] = value.SourceId;
            cells[row + FirstDataRow, 2] = value.Field; cells[row + FirstDataRow, 3] = value.Value;
            cells[row + FirstDataRow, 4] = value.Unit; cells[row + FirstDataRow, 5] = value.Origin;
        }
        return cells;
    }

    public static object[,] NormalizeOrigins(AnalysisSnapshot snapshot, object[,] cells)
    {
        var template = Create(snapshot); var r0 = cells.GetLowerBound(0); var c0 = cells.GetLowerBound(1);
        var copy = new object[cells.GetLength(0), cells.GetLength(1)];
        for (var row = 0; row < cells.GetLength(0); row++) for (var col = 0; col < cells.GetLength(1); col++) copy[row, col] = cells[row + r0, col + c0];
        var defaults = new Dictionary<Key, (string Value, string Origin)>();
        for (var row = 1; row < template.GetLength(0); row++) defaults.Add(new(Text(template[row, 0]), Text(template[row, 1]), Text(template[row, 2])), (Text(template[row, 3]), Text(template[row, 5])));
        for (var r = 1; r < cells.GetLength(0); r++)
        {
            var category = Text(cells[r0 + r, c0]); var source = Text(cells[r0 + r, c0 + 1]); var field = Text(cells[r0 + r, c0 + 2]);
            var seed = defaults[new(category, source, field)];
            copy[r, 5] = category == "Source" ? "snapshot read-only" : Text(copy[r, 3]) == seed.Value ? seed.Origin : "engineer input — accepted revision";
        }
        return copy;
    }

    public static BaselineInputReadResult Read(AnalysisSnapshot snapshot, object[,] cells)
    {
        ArgumentNullException.ThrowIfNull(snapshot); ArgumentNullException.ThrowIfNull(cells);
        var issues = new List<string>();
        var data = ReadLayout(snapshot, cells, issues);
        var project = new BaselineProjectIdentity(Required(data, "Project", "project", "project_id", issues),
            Required(data, "Project", "project", "revision_id", issues), Required(data, "Project", "project", "origin", issues),
            Required(data, "Project", "project", "evidence_reference", issues), true, false);
        var catalogue = new BaselineCatalogue(Required(data, "Catalogue", "catalogue", "revision_id", issues),
            Numbers(data, "longitudinal_diameters_mm", issues), Numbers(data, "link_diameters_mm", issues), Numbers(data, "link_spacings_mm", issues),
            Integers(data, "bar_counts", issues), Integers(data, "layers", issues), Numbers(data, "stock_lengths_mm", issues), Integer(data, "maximum_candidates", issues));
        if (issues.Count > 0) throw new ArgumentException(string.Join("; ", WithCellAddresses(cells, issues)));

        var materials = new List<BaselineMaterialMapping>();
        foreach (var material in snapshot.Materials)
        {
            var values = new[] { Number(data, "Material", material.MaterialId, "concrete_strength_n_per_mm2", issues), Number(data, "Material", material.MaterialId, "steel_yield_strength_n_per_mm2", issues), Number(data, "Material", material.MaterialId, "link_steel_yield_strength_n_per_mm2", issues), Number(data, "Material", material.MaterialId, "steel_modulus_n_per_mm2", issues) };
            if (values.All(x => x.HasValue)) materials.Add(new(material.MaterialId, values[0]!.Value, values[1]!.Value, values[2]!.Value, values[3]!.Value));
            else issues.Add($"Material:{material.MaterialId}: complete strength and modulus mapping is required.");
        }
        var contexts = new List<BaselineMemberContext>(); var memberIds = new List<string>();
        foreach (var member in snapshot.Members)
        {
            if (!bool.TryParse(Value(data, "Member", member.MemberId, "selected"), out var selected))
                throw new ArgumentException(string.Join("; ", WithCellAddresses(cells, [$"Member:{member.MemberId}:selected must be true or false."])));
            if (!selected) continue;
            memberIds.Add(member.MemberId);
            var context = Context(data, member, issues);
            if (context is null) issues.Add($"Member:{member.MemberId}: required context group omitted.");
            else contexts.Add(context);
        }
        var roles = new List<BaselineSelectionBinding>();
        var actionSelectionIds = snapshot.ActionRows.Select(x => x.SelectionId).ToHashSet(StringComparer.Ordinal);
        foreach (var selection in snapshot.ResultSelections.Where(x => actionSelectionIds.Contains(x.SelectionId)))
        {
            var text = Value(data, "Role", selection.SelectionId, "role");
            if (string.IsNullOrWhiteSpace(text)) { issues.Add($"Role:{selection.SelectionId}:role is required."); continue; }
            if (!TryRole(text, out var role)) issues.Add($"Role:{selection.SelectionId}:role has invalid value '{text}'.");
            else roles.Add(new(selection.SelectionId, role));
        }
        var inputs = new BaselineProjectInputs(project, materials, catalogue, contexts, roles);
        var revision = WorkbookContract.HashJson(new
        {
            snapshot.SnapshotId,
            snapshot.SnapshotSha256,
            inputs,
            memberIds,
            fields = data.OrderBy(x => x.Key.Category).ThenBy(x => x.Key.SourceId).ThenBy(x => x.Key.Field).Select(x => new { x.Key, x.Value }).ToArray()
        });
        return new(inputs, memberIds, WithCellAddresses(cells, issues), revision);
    }

    private static void AddMemberRows(List<Row> rows, SnapshotMember member)
    {
        void Add(string field, string value, string unit = "text") => rows.Add(new("Member", member.MemberId, field, value, unit, field == "selected" ? "editable selection" : "required engineering input"));
        Add("selected", "true", "true|false"); Add("physical_span_id", ""); Add("support_condition", ""); Add("left_support_face_x_mm", "", "mm"); Add("right_support_face_x_mm", "", "mm");
        Add("left_support_centre_x_mm", "", "mm"); Add("right_support_centre_x_mm", "", "mm"); Add("effective_span_mm", "", "mm"); Add("anchorage_start_x_mm", "", "mm"); Add("anchorage_end_x_mm", "", "mm");
        Add("nominal_cover_mm", "", "mm"); Add("maximum_aggregate_size_mm", "", "mm"); Add("exposure", ""); Add("cracking_harmful", "", "true|false"); Add("ordinary_seismic", "", "true|false");
        Add("screening_permitted", "", "true|false"); Add("horizontal", "", "true|false"); Add("top_mapping_normal", "", "true|false"); Add("evidence_revision_id", "");
        Add("fire_requirement", "", "unspecified|not_required|required"); Add("fire_decision_reference", ""); Add("fire_required_minutes", "", "minutes"); Add("lateral_restraint_positions_mm", "", "mm"); Add("lateral_restraint_evidence_reference", "");
    }

    private static BaselineMemberContext? Context(Dictionary<Key, string> data, SnapshotMember member, List<string> issues)
    {
        var issueStart = issues.Count;
        string F(string field) => Required(data, "Member", member.MemberId, field, issues);
        var numbers = new[] { Number(data, "Member", member.MemberId, "left_support_face_x_mm", issues), Number(data, "Member", member.MemberId, "right_support_face_x_mm", issues), Number(data, "Member", member.MemberId, "left_support_centre_x_mm", issues), Number(data, "Member", member.MemberId, "right_support_centre_x_mm", issues), Number(data, "Member", member.MemberId, "effective_span_mm", issues), Number(data, "Member", member.MemberId, "anchorage_start_x_mm", issues), Number(data, "Member", member.MemberId, "anchorage_end_x_mm", issues), Number(data, "Member", member.MemberId, "nominal_cover_mm", issues), Number(data, "Member", member.MemberId, "maximum_aggregate_size_mm", issues) };
        if (numbers.Any(x => !x.HasValue)) return null;
        if (!TrySupport(F("support_condition"), out var support)) { issues.Add($"Member:{member.MemberId}:support_condition has an invalid value."); return null; }
        var fireText = Value(data, "Member", member.MemberId, "fire_requirement");
        if (!TryFire(fireText, out var fire)) { issues.Add($"Member:{member.MemberId}:fire_requirement has an invalid value."); return null; }
        var minutes = Number(data, "Member", member.MemberId, "fire_required_minutes", issues, optional: true);
        var positions = Numbers(data, "Member", member.MemberId, "lateral_restraint_positions_mm", issues, optional: true);
        var lateralRef = Value(data, "Member", member.MemberId, "lateral_restraint_evidence_reference");
        var crack = Bool(data, "Member", member.MemberId, "cracking_harmful", issues); var seismic = Bool(data, "Member", member.MemberId, "ordinary_seismic", issues); var screening = Bool(data, "Member", member.MemberId, "screening_permitted", issues); var horizontal = Bool(data, "Member", member.MemberId, "horizontal", issues); var top = Bool(data, "Member", member.MemberId, "top_mapping_normal", issues);
        var span = F("physical_span_id"); var exposure = F("exposure"); var evidence = F("evidence_revision_id");
        if (issues.Count > issueStart) return null;
        return new(member.MemberId, member.ObjectId, span, support, numbers[0]!.Value, numbers[1]!.Value, numbers[2]!.Value, numbers[3]!.Value, numbers[4]!.Value, numbers[5]!.Value, numbers[6]!.Value, numbers[7]!.Value, numbers[8]!.Value, exposure, crack, seismic, screening, horizontal, top, evidence, new(fire, Value(data, "Member", member.MemberId, "fire_decision_reference"), minutes), string.IsNullOrWhiteSpace(lateralRef) || positions.Count == 0 ? null : new(positions, lateralRef));
    }

    private static Dictionary<Key, string> ReadLayout(AnalysisSnapshot snapshot, object[,] cells, List<string> issues)
    {
        if (cells.GetLength(1) != Headers.Length || cells.GetLength(0) < 2) throw new ArgumentException($"{SheetName}: incompatible six-column layout.");
        var r0 = cells.GetLowerBound(0); var c0 = cells.GetLowerBound(1);
        for (var c = 0; c < Headers.Length; c++) if (!string.Equals(Text(cells[r0, c0 + c]), Headers[c], StringComparison.Ordinal)) throw new ArgumentException($"{SheetName}: header {c + 1} must be '{Headers[c]}'.");
        var expected = Create(snapshot); var expectedRows = new Dictionary<Key, (string Value, string Unit)>();
        for (var r = 1; r < expected.GetLength(0); r++) expectedRows.Add(new(Text(expected[r, 0]), Text(expected[r, 1]), Text(expected[r, 2])), (Text(expected[r, 3]), Text(expected[r, 4])));
        var result = new Dictionary<Key, string>();
        for (var r = r0 + 1; r <= cells.GetUpperBound(0); r++) { var key = new Key(Text(cells[r, c0]), Text(cells[r, c0 + 1]), Text(cells[r, c0 + 2])); if (!expectedRows.TryGetValue(key, out var expectedRow)) { issues.Add($"{SheetName}!A{r - r0 + 1}: immutable category/source ID/field layout changed."); continue; } if (Text(cells[r, c0 + 4]) != expectedRow.Unit) issues.Add($"{SheetName}!E{r - r0 + 1}: immutable unit changed."); var value = RawText(cells[r, c0 + 3]); if (value.StartsWith('=')) issues.Add($"{SheetName}!D{r - r0 + 1}: formulas are not accepted."); if (key.Category == "Source" && value != expectedRow.Value) issues.Add($"{SheetName}!D{r - r0 + 1}: snapshot source fact changed."); if (!result.TryAdd(key, value)) issues.Add($"{SheetName}!A{r - r0 + 1}: duplicate field."); }
        foreach (var key in expectedRows.Keys) if (!result.ContainsKey(key)) issues.Add($"{SheetName}: missing required layout row {key.Category}/{key.SourceId}/{key.Field}.");
        return result;
    }
    private static string Value(Dictionary<Key, string> data, string category, string id, string field) => data.GetValueOrDefault(new(category, id, field), "");
    private static string Required(Dictionary<Key, string> d, string c, string id, string f, List<string> e) { var v = Value(d, c, id, f); if (string.IsNullOrWhiteSpace(v)) e.Add($"{c}:{id}:{f} is required."); return v; }
    private static double? Number(Dictionary<Key, string> d, string c, string id, string f, List<string> e, bool optional = false) { var v = Value(d, c, id, f); if (string.IsNullOrWhiteSpace(v)) { if (!optional) e.Add($"{c}:{id}:{f} is required."); return null; } if (!double.TryParse(v, NumberStyles.Float, CultureInfo.InvariantCulture, out var n) || !double.IsFinite(n)) { e.Add($"{c}:{id}:{f} must be a finite number; formulas are not accepted."); return null; } return n; }
    private static int Integer(Dictionary<Key, string> d, string f, List<string> e) { var v = Number(d, "Catalogue", "catalogue", f, e); if (v is { } n && n == Math.Truncate(n) && n >= int.MinValue && n <= int.MaxValue) return (int)n; e.Add($"Catalogue:catalogue:{f} must be a whole number."); return 0; }
    private static IReadOnlyList<int> Integers(Dictionary<Key, string> d, string f, List<string> e) { var values = List(Value(d, "Catalogue", "catalogue", f), e, $"Catalogue:catalogue:{f}"); if (values.Any(x => x != Math.Truncate(x))) e.Add($"Catalogue:catalogue:{f} must contain whole numbers."); return values.Select(x => (int)x).ToArray(); }
    private static IReadOnlyList<double> Numbers(Dictionary<Key, string> d, string f, List<string> e) => List(Value(d, "Catalogue", "catalogue", f), e, $"Catalogue:catalogue:{f}");
    private static IReadOnlyList<double> Numbers(Dictionary<Key, string> d, string c, string id, string f, List<string> e, bool optional) { var v = Value(d, c, id, f); return string.IsNullOrWhiteSpace(v) && optional ? [] : List(v, e, $"{c}:{id}:{f}"); }
    private static IReadOnlyList<double> List(string text, List<string> e, string label) { var values = new List<double>(); foreach (var part in text.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)) if (double.TryParse(part, NumberStyles.Float, CultureInfo.InvariantCulture, out var n) && double.IsFinite(n)) values.Add(n); else e.Add($"{label} contains invalid number '{part}'."); if (values.Count == 0) e.Add($"{label} is required."); return values; }
    private static bool Bool(Dictionary<Key, string> d, string c, string id, string f, List<string> e) { var v = Value(d, c, id, f); if (bool.TryParse(v, out var b)) return b; e.Add($"{c}:{id}:{f} must be true or false; blank is not false."); return false; }
    private static bool TryRole(string value, out BaselineSelectionRole role) => (role = value.Trim().ToLowerInvariant() switch { "uls" => BaselineSelectionRole.Uls, "sls_total" => BaselineSelectionRole.SlsTotal, "sls_sustained" => BaselineSelectionRole.SlsSustained, _ => default }) switch { BaselineSelectionRole.Uls when value.Trim().ToLowerInvariant() != "uls" => false, _ => value.Trim().ToLowerInvariant() is "uls" or "sls_total" or "sls_sustained" };
    private static bool TrySupport(string v, out BaselineSupportCondition s) { s = v.Trim().ToLowerInvariant() switch { "simply_supported" => BaselineSupportCondition.SimplySupported, "continuous" => BaselineSupportCondition.Continuous, "unknown" => BaselineSupportCondition.Unknown, _ => default }; return v.Trim().ToLowerInvariant() is "simply_supported" or "continuous" or "unknown"; }
    private static bool TryFire(string v, out BaselineFireRequirement f) { f = v.Trim().ToLowerInvariant() switch { "unspecified" => BaselineFireRequirement.Unspecified, "not_required" => BaselineFireRequirement.NotRequired, "required" => BaselineFireRequirement.Required, _ => default }; return v.Trim().ToLowerInvariant() is "" or "unspecified" or "not_required" or "required"; }
    private static IReadOnlyList<string> WithCellAddresses(object[,] cells, IReadOnlyList<string> issues)
    {
        var r0 = cells.GetLowerBound(0); var c0 = cells.GetLowerBound(1);
        var locations = new Dictionary<string, string>();
        for (var r = 1; r < cells.GetLength(0); r++) locations[$"{Text(cells[r + r0, c0])}:{Text(cells[r + r0, c0 + 1])}:{Text(cells[r + r0, c0 + 2])}"] = $"{SheetName}!D{r + 1}";
        return issues.Select(issue => { var space = issue.IndexOf(' '); var field = space < 0 ? issue : issue[..space]; return locations.TryGetValue(field, out var address) ? address + ": " + issue : issue; }).ToArray();
    }
    private static string Text(object? value) => Convert.ToString(value, CultureInfo.InvariantCulture)?.Trim() ?? "";
    private static string RawText(object? value) => Text(value);
    private sealed record Row(string Category, string SourceId, string Field, string Value, string Unit, string Origin);
    private sealed record Key(string Category, string SourceId, string Field);
}

public sealed record BaselineInputReadResult(BaselineProjectInputs Inputs, IReadOnlyList<string> MemberIds, IReadOnlyList<string> Issues, string Revision);
