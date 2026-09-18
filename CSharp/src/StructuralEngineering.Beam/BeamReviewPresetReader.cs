using System.Text.Json;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

/// <summary>Pure parsing; the host supplies the canonical preset text.</summary>
public static class BeamReviewPresetReader
{
    public static IReadOnlyDictionary<string, string> LegacyKeys { get; } = new Dictionary<string, string>
    {
        ["design_basis.code"] = "design.code",
        ["design_basis.seismic_basis"] = "design.seismic",
        ["design_basis.concrete_strength_n_per_mm2"] = "design.fck",
        ["design_basis.longitudinal_steel_yield_n_per_mm2"] = "design.fy",
        ["design_basis.link_steel_yield_n_per_mm2"] = "design.link_fy",
        ["design_basis.nominal_cover_to_outermost_reinforcement_mm"] = "design.cover",
        ["design_basis.exposure"] = "design.exposure",
        ["design_basis.fire_resistance_minutes"] = "design.fire_minutes",
        ["design_basis.nominal_max_aggregate_mm"] = "design.aggregate",
        ["detailing_preferences.longitudinal_bar_diameters_mm"] = "detailing.bars",
        ["detailing_preferences.link_diameters_mm"] = "detailing.links",
        ["detailing_preferences.preferred_longitudinal_layers"] = "detailing.preferred_layers",
        ["detailing_preferences.stock_length_mm"] = "detailing.stock",
        ["detailing_preferences.uniform_section_scope"] = "detailing.uniform_scope",
        ["detailing_preferences.section_widths_mm"] = "detailing.widths",
        ["detailing_preferences.section_depths_mm"] = "detailing.depths",
        ["illustrative_rates.currency"] = "rates.currency",
        ["illustrative_rates.concrete_per_m3"] = "rates.concrete",
        ["illustrative_rates.reinforcement_per_kg"] = "rates.steel",
        ["illustrative_rates.formwork_per_m2"] = "rates.formwork"
    };

    public static BeamReviewPreset Parse(string json)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var (path, key) in LegacyKeys)
        {
            var parts = path.Split('.');
            values.Add(key, Text(root.GetProperty(parts[0]).GetProperty(parts[1])));
        }
        foreach (var item in root.GetProperty("review_defaults").EnumerateObject()) values.Add(item.Name, Text(item.Value));
        foreach (var key in values.Keys)
        {
            if (!BeamReviewFields.TryNormalize(key, values[key], out var normalized)) throw new ArgumentException("Invalid preset field: " + key);
            values[key] = normalized;
        }
        return new(root.GetProperty("preset_id").GetString()!, ResultFactory.SemanticId("review_preset", values), values);
    }

    private static string Text(JsonElement value) => value.ValueKind == JsonValueKind.Array
        ? string.Join(',', value.EnumerateArray().Select(x => x.ToString())) : value.ToString();
}
