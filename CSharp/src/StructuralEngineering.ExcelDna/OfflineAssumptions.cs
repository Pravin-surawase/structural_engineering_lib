using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace StructuralEngineering.ExcelDna;

public sealed record AssumptionDefinition(string Key, string Label, string DefaultValue, string Unit, string Kind);
public sealed record AssumptionValue(string Key, string Value, string Unit, string Origin);
public sealed record OfflineAssumptionInput(string PresetId, bool ProductionIssuanceAllowed, IReadOnlyList<AssumptionValue> Values)
{
    [JsonIgnore]
    public string Revision => WorkbookContract.HashJson(this);
}

/// <summary>Application inputs only. These values never replace imported model facts.</summary>
public static class OfflineAssumptions
{
    public const string SheetName = "Assumptions";
    public const int FirstValueRow = 6;
    public static IReadOnlyList<AssumptionDefinition> Definitions { get; } = LoadDefinitions();

    public static OfflineAssumptionInput Read(IReadOnlyList<string?> values)
    {
        if (values.Count != Definitions.Count) throw new ArgumentException("The Assumptions sheet has an incompatible layout.");
        var result = new List<AssumptionValue>();
        for (var index = 0; index < Definitions.Count; index++)
        {
            var definition = Definitions[index];
            var value = values[index]?.Trim();
            if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException($"Assumptions!B{index + FirstValueRow}: {definition.Label} is required; blank is not zero.");
            try { value = Normalize(definition, value); }
            catch (ArgumentException error) { throw new ArgumentException($"Assumptions!B{index + FirstValueRow}: {definition.Label}: {error.Message}"); }
            result.Add(new(definition.Key, value, definition.Unit,
                value == Normalize(definition, definition.DefaultValue) ? "demo_default" : "engineer_edit_demo_basis"));
        }
        return new("demo-rc-beam-v1", false, result.AsReadOnly());
    }

    public static object[,] CreateSheet()
    {
        var rows = new object[Definitions.Count + 5, 4];
        rows[0, 0] = "BEAM ASSUMPTIONS";
        rows[1, 0] = "DEMO — editable development values; not project approval";
        rows[2, 0] = "Edit the Value column. Imported materials and forces remain separate source facts.";
        rows[3, 0] = "Cover is measured to outermost reinforcement. Rates are illustrative, not market quotes.";
        rows[4, 0] = "Parameter"; rows[4, 1] = "Value"; rows[4, 2] = "Unit / basis"; rows[4, 3] = "Origin";
        for (var i = 0; i < Definitions.Count; i++)
        {
            var d = Definitions[i];
            rows[i + 5, 0] = d.Label; rows[i + 5, 1] = d.DefaultValue; rows[i + 5, 2] = d.Unit;
            rows[i + 5, 3] = "Demo default";
        }
        return rows;
    }

    public static string OriginFormula(int index) =>
        $"=IF(B{index + FirstValueRow}&\"\"=\"{Definitions[index].DefaultValue.Replace("\"", "\"\"")}\",\"Demo default\",\"Engineer edit (demo basis)\")";

    public static string ReportFreshnessFormula(OfflineAssumptionInput input)
    {
        var tests = input.Values.Select((value, index) =>
            $"'{SheetName}'!B{index + FirstValueRow}&\"\"=\"{value.Value.Replace("\"", "\"\"")}\"");
        return $"=IFERROR(IF(AND({string.Join(",", tests)}),\"Offline review — assumptions unchanged; engineering not evaluated\",\"Historical review — assumptions changed; review again\"),\"Historical review — assumptions unavailable\")";
    }

    private static string Normalize(AssumptionDefinition definition, string value)
    {
        if (definition.Kind == "choice")
        {
            if (value != definition.DefaultValue) throw new ArgumentException("This demo profile supports only " + definition.DefaultValue + ".");
            return value;
        }
        if (definition.Kind == "list")
        {
            var numbers = value.Split(',').Select(item => PositiveNumber(item.Trim(), false)).ToArray();
            if (numbers.Length == 0 || numbers.Distinct().Count() != numbers.Length) throw new ArgumentException("Use a comma-separated list of distinct positive numbers.");
            return string.Join(", ", numbers.Select(item => item.ToString("G17", CultureInfo.InvariantCulture)));
        }
        var number = PositiveNumber(value, definition.Kind == "rate");
        if (definition.Kind == "integer" && number != Math.Truncate(number)) throw new ArgumentException("A positive whole number is required.");
        return number.ToString("G17", CultureInfo.InvariantCulture);
    }

    private static double PositiveNumber(string value, bool zeroAllowed)
    {
        if (!double.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out var number) ||
            !double.IsFinite(number) || (zeroAllowed ? number < 0 : number <= 0))
            throw new ArgumentException(zeroAllowed ? "Use a finite nonnegative number; zero must be explicit." : "Use a finite positive number.");
        return number;
    }

    private static IReadOnlyList<AssumptionDefinition> LoadDefinitions()
    {
        using var stream = typeof(OfflineAssumptions).Assembly.GetManifestResourceStream("StructAutomate.DemoPreset.json")
            ?? throw new InvalidOperationException("The canonical demo preset is missing.");
        using var json = JsonDocument.Parse(stream);
        var result = new List<AssumptionDefinition>();
        void Add(string group, string key, string label, string unit, string kind = "number")
        {
            var element = json.RootElement.GetProperty(group).GetProperty(key);
            var value = element.ValueKind == JsonValueKind.Array
                ? string.Join(", ", element.EnumerateArray().Select(item => item.ToString())) : element.ToString();
            result.Add(new(group + "." + key, label, value, unit, kind));
        }
        const string basis = "design_basis";
        Add(basis, "code", "Design code", "demo", "choice");
        Add(basis, "seismic_basis", "Seismic basis", "demo scope", "choice");
        Add(basis, "concrete_strength_n_per_mm2", "Concrete strength fck", "N/mm²");
        Add(basis, "longitudinal_steel_yield_n_per_mm2", "Longitudinal steel fy", "N/mm²");
        Add(basis, "link_steel_yield_n_per_mm2", "Link steel fy", "N/mm²");
        Add(basis, "nominal_cover_to_outermost_reinforcement_mm", "Nominal cover", "mm, outermost reinforcement");
        Add(basis, "exposure", "Exposure", "demo scope", "choice");
        Add(basis, "fire_resistance_minutes", "Fire resistance", "minutes");
        Add(basis, "nominal_max_aggregate_mm", "Maximum aggregate", "mm");
        const string detailing = "detailing_preferences";
        Add(detailing, "longitudinal_bar_diameters_mm", "Longitudinal bar choices", "mm", "list");
        Add(detailing, "link_diameters_mm", "Link diameter choices", "mm", "list");
        Add(detailing, "preferred_longitudinal_layers", "Preferred layers", "count", "integer");
        Add(detailing, "stock_length_mm", "Stock bar length", "mm");
        Add(detailing, "uniform_section_scope", "Uniform section preference", "construction preference", "choice");
        Add(detailing, "section_widths_mm", "Section width choices", "mm", "list");
        Add(detailing, "section_depths_mm", "Section depth choices", "mm", "list");
        Add("illustrative_rates", "currency", "Currency", "illustrative", "choice");
        Add("illustrative_rates", "concrete_per_m3", "Concrete rate", "INR/m³", "rate");
        Add("illustrative_rates", "reinforcement_per_kg", "Steel rate", "INR/kg", "rate");
        Add("illustrative_rates", "formwork_per_m2", "Formwork rate", "INR/m²", "rate");
        return result.AsReadOnly();
    }
}
