using System.Globalization;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Excel layout/migration only. All effective-value choices belong to the native resolver.</summary>
public static class BeamReviewInputProjection
{
    public const string SheetName = "Review Inputs";
    public const string SummarySheet = "Provisional Review";
    public const string DetailSheet = "Review Evidence";

    public static BeamReviewPreset Preset()
    {
        using var stream = typeof(OfflineAssumptions).Assembly.GetManifestResourceStream("StructAutomate.DemoPreset.json")!;
        using var reader = new StreamReader(stream);
        return BeamReviewPresetReader.Parse(reader.ReadToEnd());
    }

    public static object[,] Inputs(BeamInputLedger ledger)
    {
        var rows = new object[ledger.Fields.Count + 4, 8];
        rows[0, 0] = "PERSISTENT BEAM INPUTS — provisional scenario";
        rows[1, 0] = "Edit column C for a member/selection override. Assumptions column B supplies project preferences. Blank or invalid text retains a valid fallback.";
        rows[2, 0] = "Original source facts remain separate. Required fire and unavailable service evidence are not waived.";
        var headers = new[] { "Member / selection", "Field", "Entered override", "Effective value", "Unit", "Origin", "Reason / rule", "Captured source value" };
        for (var c = 0; c < headers.Length; c++) rows[3, c] = headers[c];
        for (var i = 0; i < ledger.Fields.Count; i++)
        {
            var field = ledger.Fields[i]; var row = i + 4;
            rows[row, 0] = field.SubjectId; rows[row, 1] = field.Key;
            // Inherited entries are disclosed in Reason; C represents only a local override.
            var local = ledger.Edits.Where(x => field.EditIds.Contains(x.Id) && x.Scope is BeamInputScope.Member or BeamInputScope.Selection).ToArray();
            rows[row, 2] = local.Length == 0 ? "" : string.Join(" | ", local.Select(x => x.EnteredText));
            rows[row, 3] = field.Value; rows[row, 4] = field.Unit; rows[row, 5] = field.Origin.ToString();
            rows[row, 6] = Display(field.Reason + (field.EnteredText is null ? "" : " | selected entry: " + field.EnteredText));
            rows[row, 7] = field.SourceText ?? "Missing / not captured";
        }
        return rows;
    }

    public static object[,] Summary(BeamReviewResult result)
    {
        var rows = new object[result.Members.Count + 4, 9];
        rows[0, 0] = "PROVISIONAL BEAM REVIEW — workflow complete; full design is separate";
        rows[1, 0] = result.LiveAcquisitionStatus;
        rows[2, 0] = "Inputs: " + result.Ledger.Revision;
        var headers = new[] { "Member", "Source", "Scenario", "Core", "Full design", "Workflow", "Fire", "Serviceability", "Example basis" };
        for (var c = 0; c < headers.Length; c++) rows[3, c] = headers[c];
        for (var i = 0; i < result.Members.Count; i++)
        {
            var member = result.Members[i]; var row = i + 4;
            rows[row, 0] = member.MemberId; rows[row, 1] = member.SourceStatus; rows[row, 2] = member.ScenarioStatus;
            rows[row, 3] = member.CoreStatus; rows[row, 4] = member.FullDesignStatus; rows[row, 5] = "Complete accounting";
            rows[row, 6] = member.Stages.Single(x => x.StageId == "fire").Status;
            rows[row, 7] = member.Stages.Single(x => x.StageId == "serviceability").Status;
            rows[row, 8] = member.ExampleCore is null ? "Not used" : result.ExampleBasisId;
        }
        return rows;
    }

    public static object[,] SharedDesignInputs(AnalysisSnapshot snapshot, BeamResolvedReview resolved, object[,] current)
    {
        var rows = (object[,])current.Clone();
        var materialMembers = snapshot.Members.ToDictionary(x => x.MemberId,
            x => snapshot.Sections.Single(s => s.SectionId == x.SectionId).MaterialId, StringComparer.Ordinal);
        for (var r = 1; r < rows.GetLength(0); r++)
        {
            var category = Text(rows[r, 0]); var source = Text(rows[r, 1]); var field = Text(rows[r, 2]);
            var key = LegacyField(category, field); if (key is null) continue;
            var matches = resolved.Ledger.Fields.Where(x => x.Key == key && (category switch
            {
                "Member" => x.SubjectId == source,
                "Material" => materialMembers.GetValueOrDefault(x.SubjectId) == source,
                "Role" => x.SubjectId.EndsWith("/" + source, StringComparison.Ordinal),
                _ => true
            })).ToArray();
            if (matches.Length == 0) continue;
            var values = matches.Select(x => x.EnteredText is { } entered && !BeamReviewFields.TryNormalize(key, entered, out _) ? entered : x.Value).Distinct(StringComparer.Ordinal).ToArray();
            var value = values.Length == 1 ? values[0] : "Member-specific values — see Review Inputs";
            value = value switch { "SimplySupported" => "simply_supported", "NotRequired" => "not_required", "SlsTotal" => "sls_total", "SlsSustained" => "sls_sustained", "Uls" => "uls", _ => value };
            if (key == "design.seismic") value = value == "non_seismic_demo_only" ? "true" : "false";
            if (key == "design.fire_minutes" && resolved.Members.SingleOrDefault(x => x.MemberId == source)?.Inputs.MemberContexts[0].FireBasis?.Requirement == BaselineFireRequirement.NotRequired) value = "";
            rows[r, 3] = value;
            rows[r, 5] = values.Length == 1 ? $"Shared ledger: {matches[0].Origin}; effective {matches[0].Value} {matches[0].Unit}" : "Full baseline requires consistent material/catalogue mapping; provisional member inputs are retained";
        }
        return rows;
    }

    public static object[,] Details(BeamReviewResult result, string? artifactPath = null)
    {
        var entries = new List<object[]> { new object[] { "REVIEW EVIDENCE — captured / assumed / example / unavailable remain distinct", "Complete evidence artifact", artifactPath ?? result.RequestId },
            new object[] { "Member", "Stage / check", "Availability / engineering", "Basis / result", "Quantity / value", "Units / scope", "Detail" } };
        foreach (var member in result.Members)
        {
            foreach (var stage in member.Stages) entries.Add([member.MemberId, stage.StageId, stage.Availability.ToString(), stage.Basis, stage.Status, "", string.Join(";", stage.EvidenceIds)]);
            foreach (var check in (member.Core?.Design?.Checks ?? []).Concat(member.ServiceChecks ?? []))
                entries.Add([member.MemberId, check.RuleId, check.Result.Engineering.ToString(), check.Result.ResultId,
                    check.Result.Outputs.ToString(), check.ScopeId, string.Join(";", check.Result.Diagnostics.Select(x => x.Code))]);
            if (member.Core?.Design is { } core)
            {
                entries.Add([member.MemberId, "actual bottom effective depth", "Provisional", core.Arrangement.RevisionId, core.Arrangement.BottomEffectiveDepthMm, "mm", "From actual bar coordinates"]);
                entries.Add([member.MemberId, "actual top effective depth", "Provisional", core.Arrangement.RevisionId, core.Arrangement.TopEffectiveDepthMm, "mm", "From actual bar coordinates"]);
            }
        }
        var rows = new object[entries.Count, 7];
        for (var r = 0; r < entries.Count; r++) for (var c = 0; c < entries[r].Length; c++) rows[r, c] = entries[r][c] is string text ? Display(text) : entries[r][c];
        return rows;
    }

    private static string Display(string text) => text.Length <= 4000 ? text : text[..3900] + " … [complete value in the hashed review artifact]";

    public static string? LegacyField(string category, string field) => (category, field) switch
    {
        ("Material", "concrete_strength_n_per_mm2") => "design.fck",
        ("Material", "steel_yield_strength_n_per_mm2") => "design.fy",
        ("Material", "link_steel_yield_strength_n_per_mm2") => "design.link_fy",
        ("Material", "steel_modulus_n_per_mm2") => "design.steel_modulus",
        ("Catalogue", "longitudinal_diameters_mm") => "detailing.bars",
        ("Catalogue", "link_diameters_mm") => "detailing.links",
        ("Catalogue", "link_spacings_mm") => "detailing.link_spacings",
        ("Catalogue", "bar_counts") => "detailing.bar_counts",
        ("Catalogue", "layers") => "detailing.layers",
        ("Catalogue", "stock_lengths_mm") => "detailing.stock",
        ("Catalogue", "maximum_candidates") => "catalogue.maximum_candidates",
        ("Member", "physical_span_id") => "member.physical_span",
        ("Member", "support_condition") => "member.support",
        ("Member", "left_support_face_x_mm") => "member.left_face",
        ("Member", "right_support_face_x_mm") => "member.right_face",
        ("Member", "left_support_centre_x_mm") => "member.left_centre",
        ("Member", "right_support_centre_x_mm") => "member.right_centre",
        ("Member", "effective_span_mm") => "member.effective_span",
        ("Member", "anchorage_start_x_mm") => "member.anchor_start",
        ("Member", "anchorage_end_x_mm") => "member.anchor_end",
        ("Member", "nominal_cover_mm") => "design.cover",
        ("Member", "maximum_aggregate_size_mm") => "design.aggregate",
        ("Member", "exposure") => "design.exposure",
        ("Member", "cracking_harmful") => "design.cracking_harmful",
        ("Member", "screening_permitted") => "design.screening_permitted",
        ("Member", "fire_required_minutes") => "design.fire_minutes",
        ("Member", "lateral_restraint_positions_mm") => "member.restraints",
        ("Member", "fire_requirement") => "design.fire_requirement",
        ("Member", "fire_decision_reference") => "member.fire_decision",
        ("Member", "evidence_revision_id") => "member.evidence_reference",
        ("Member", "lateral_restraint_evidence_reference") => "member.restraint_reference",
        ("Member", "horizontal") => "member.horizontal",
        ("Member", "top_mapping_normal") => "member.top_mapping_normal",
        ("Member", "ordinary_seismic") => "design.seismic",
        ("Role", "role") => "selection.role",
        _ => null
    };

    internal static string Text(object? value) => Convert.ToString(value, CultureInfo.InvariantCulture) ?? "";
}
