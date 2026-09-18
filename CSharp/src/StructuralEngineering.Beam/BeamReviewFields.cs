using System.Globalization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Beam;

/// <summary>Executable field/consumer/fallback map shared by every review host.</summary>
public static class BeamReviewFields
{
    public const string RuleRevision = "beam-review-resolution-v1";
    public static IReadOnlyList<BeamFieldDefinition> All { get; } =
    [
        F("design.code", "code", "text", "profile", "DATA-01", "preset"),
        F("design.seismic", "basis", "text", "ordinary_seismic", "DATA-01", "preset"),
        F("design.fck", "N/mm2", "positive", "material.ConcreteStrengthNPerMm2", "DATA-04", "preset; never infer strength from a label"),
        F("design.fy", "N/mm2", "positive", "material.SteelYieldStrengthNPerMm2", "DATA-04", "preset"),
        F("design.link_fy", "N/mm2", "positive", "material.LinkSteelYieldStrengthNPerMm2", "DATA-04", "preset"),
        F("design.steel_modulus", "N/mm2", "positive", "material.SteelModulusNPerMm2", "DATA-04", "preset"),
        F("design.cover", "mm", "positive", "context.NominalCoverMm", "DATA-07", "preset"),
        F("design.exposure", "class", "exposure", "context.Exposure", "DATA-07", "preset"),
        F("design.fire_minutes", "min", "nonnegative", "context.FireBasis", "DATA-07", "retain required rating; unavailable fire check"),
        F("design.fire_requirement", "requirement", "fire", "context.FireBasis.Requirement", "DATA-07", "required preset fire; preserve explicit decisions"),
        F("design.aggregate", "mm", "positive", "context.MaximumAggregateSizeMm", "DATA-07", "preset"),
        F("design.cracking_harmful", "bool", "bool", "context.CrackingHarmful", "DATA-08", "preset"),
        F("design.screening_permitted", "bool", "bool", "context.ScreeningPermitted", "DATA-08", "scenario screening; never project approval"),
        F("detailing.bars", "mm", "positive-list", "catalogue.LongitudinalDiametersMm", "DATA-09", "preset"),
        F("detailing.links", "mm", "positive-list", "catalogue.LinkDiametersMm", "DATA-09", "preset"),
        F("detailing.link_spacings", "mm", "positive-list", "catalogue.LinkSpacingsMm", "DATA-09", "preset"),
        F("detailing.bar_counts", "count", "counts", "catalogue.BarCounts", "DATA-09", "preset"),
        F("detailing.layers", "count", "layers", "catalogue.Layers", "DATA-09", "preset"),
        F("detailing.preferred_layers", "count", "layer", "catalogue.Layers ordering", "DATA-09", "preset"),
        F("detailing.stock", "mm", "positive-list", "catalogue.StockLengthsMm", "DATA-10", "preset"),
        F("detailing.uniform_scope", "scope", "text", "future optimization scope", "DATA-12", "retain preference; optimization unavailable", false),
        F("detailing.widths", "mm", "positive-list", "future section catalogue", "DATA-12", "retain preference; alternatives unverified", false),
        F("detailing.depths", "mm", "positive-list", "future section catalogue", "DATA-12", "retain preference; alternatives unverified", false),
        F("catalogue.maximum_candidates", "count", "budget", "search budget", "DATA-15", "preset bounded to 10000"),
        F("member.physical_span", "id", "text", "context.PhysicalSpanId", "DATA-03", "one captured member per assumed physical span"),
        F("member.support", "basis", "support", "context.SupportCondition", "DATA-03", "assumed simply supported scenario"),
        F("member.left_face", "mm", "number", "context.LeftSupportFaceXMm", "DATA-03", "assumed 500 mm from captured end, limited to span/4"),
        F("member.right_face", "mm", "number", "context.RightSupportFaceXMm", "DATA-03", "captured length minus assumed end face"),
        F("member.left_centre", "mm", "number", "context.LeftSupportCentreXMm", "DATA-03", "captured start"),
        F("member.right_centre", "mm", "positive", "context.RightSupportCentreXMm", "DATA-03", "captured length"),
        F("member.effective_span", "mm", "positive", "context.EffectiveSpanMm", "DATA-03", "conservative captured centre-to-centre span"),
        F("member.anchor_start", "mm", "number", "context.AnchorageStartXMm", "DATA-10", "assumed 1000 mm beyond end; verify support space"),
        F("member.anchor_end", "mm", "number", "context.AnchorageEndXMm", "DATA-10", "assumed 1000 mm beyond end; verify support space"),
        F("member.restraints", "mm", "stations", "context.LateralRestraints", "DATA-03", "assumed end restraints"),
        F("member.horizontal", "bool", "bool", "context.Horizontal", "DATA-03", "captured point elevations"),
        F("member.top_mapping_normal", "bool", "bool", "context.TopMappingNormal", "DATA-03", "captured local axis; mapper verifies independently"),
        F("member.evidence_reference", "reference", "text", "context.EvidenceRevisionId", "DATA-03", "provisional rule identity"),
        F("member.fire_decision", "reference", "text", "context.FireBasis.DecisionReference", "DATA-07", "provisional requirement; no project approval"),
        F("member.restraint_reference", "reference", "text", "context.LateralRestraints.EvidenceReference", "DATA-03", "provisional assumed end restraints"),
        F("member.width", "mm", "positive", "scenario section.WidthMm", "DATA-03", "captured rectangular width, otherwise named example"),
        F("member.depth", "mm", "positive", "scenario section.DepthMm", "DATA-03", "captured rectangular depth, otherwise named example"),
        F("selection.role", "role", "role", "selection_roles", "DATA-05/06", "unclassified captured rows assumed ULS; never manufacture SLS"),
        F("rates.currency", "currency", "text", "cost currency", "DATA-12", "synthetic preset", false),
        F("rates.concrete", "currency/m3", "nonnegative", "compatible concrete cost", "DATA-12", "synthetic preset", false),
        F("rates.steel", "currency/kg", "nonnegative", "compatible steel cost", "DATA-12", "synthetic preset", false),
        F("rates.formwork", "currency/m2", "nonnegative", "compatible formwork cost", "DATA-12", "synthetic preset", false)
    ];

    private static BeamFieldDefinition F(string key, string unit, string kind, string consumer, string group,
        string rule, bool structural = true) => new(key, unit, kind, consumer, group, rule, structural);

    public static bool TryNormalize(string key, string? text, out string value)
    {
        value = text?.Trim() ?? "";
        var field = All.SingleOrDefault(x => x.Key == key);
        if (field is null || value.Length == 0 || value.StartsWith('=') || value.Length > 4096) return false;
        if (field.Kind == "text") return true;
        if (field.Kind == "bool") { if (!bool.TryParse(value, out var b)) return false; value = b ? "true" : "false"; return true; }
        if (field.Kind is "role" or "support" or "exposure" or "fire")
        {
            var options = field.Kind switch
            {
                "role" => new[] { "Uls", "SlsTotal", "SlsSustained" },
                "support" => ["SimplySupported", "Continuous", "Unknown"],
                "fire" => ["Unspecified", "Required", "NotRequired"],
                _ => ["Mild", "Moderate", "Severe", "VerySevere", "Extreme"]
            };
            if (key == "design.exposure" && value == "mild_demo_assumption") value = "Mild";
            if (key == "selection.role") value = value.Replace("_", "", StringComparison.Ordinal);
            if (key == "member.support" || key == "design.fire_requirement") value = value.Replace("_", "", StringComparison.Ordinal);
            var normalized = value;
            var match = options.FirstOrDefault(x => x.Equals(normalized, StringComparison.OrdinalIgnoreCase));
            if (match is null) return false;
            value = match; return true;
        }
        var parts = value.Split(',', StringSplitOptions.TrimEntries);
        var list = field.Kind is "positive-list" or "stations" or "counts" or "layers";
        if ((!list && parts.Length != 1) || parts.Length > (field.Kind == "stations" ? 1000 : 16)) return false;
        var numbers = new List<double>();
        foreach (var part in parts)
        {
            if (!double.TryParse(part, NumberStyles.Float, CultureInfo.InvariantCulture, out var number) || !double.IsFinite(number)) return false;
            if ((field.Kind is "positive" or "positive-list") && number <= 0 || field.Kind == "nonnegative" && number < 0) return false;
            if ((field.Kind is "budget" or "counts" or "layers" or "layer") && (number != Math.Truncate(number) || number < (field.Kind == "counts" ? 2 : 1) || number > (field.Kind == "budget" ? 10000 : field.Kind == "counts" ? 20 : 3))) return false;
            numbers.Add(number);
        }
        if (list && numbers.Distinct().Count() != numbers.Count) return false;
        if (field.Kind == "stations" && (numbers.Count < 2 || !numbers.SequenceEqual(numbers.Order()))) return false;
        value = string.Join(",", numbers.Select(x => x.ToString("G17", CultureInfo.InvariantCulture)));
        return true;
    }
}
