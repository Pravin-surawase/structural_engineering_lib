using System.Globalization;
using System.Text.Json;

namespace StructuralEngineering.Etabs;

internal sealed record EtabsBulkTableSpec(string Key, bool Editing, int Version, string IdentityField, string? ScopeField = null, string? ScopeValue = null);

/// <summary>Versioned source-table decoding. Display numbers are never used as exact geometry or assignments.</summary>
internal sealed class EtabsBulkTable
{
    internal static readonly EtabsBulkTableSpec[] Specifications =
    [
        new("Beam Object Connectivity", false, 2, "UniqueName"),
        new("Point Object Connectivity", false, 1, "UniqueName"),
        new("Objects and Elements - Frames", false, 1, "ElmName", "ObjType", "Frame"),
        new("Frame Assignments - Property Modifiers", true, 1, "UniqueName"),
        new("Frame Assignments - Releases and Partial Fixity", true, 1, "UniqueName"),
        new("Frame Assignments - Insertion Point", true, 1, "UniqueName"),
        new("Frame Assignments - End Length Offsets", true, 1, "UniqueName"),
        new("Frame Assignments - Section Properties", true, 1, "UniqueName"),
        new("Joint Assignments - Restraints", true, 1, "UniqueName")
    ];

    internal IReadOnlyDictionary<string, Row> Rows { get; }
    internal string Key { get; }
    internal int SourceRowCount { get; }
    internal int ContextOnlyRowCount { get; }
    internal EtabsBulkTable(EtabsBulkTableSpec specification, JsonElement metadata, JsonElement data)
    {
        Key = specification.Key;
        var shift = specification.Editing ? 0 : 1;
        Need(metadata[0].GetInt32() == specification.Version && data[shift].GetInt32() == specification.Version,
            "The table version is outside the qualified source profile.");
        var fieldNames = metadata[2].EnumerateArray().Select(item => item.GetString()!).ToArray();
        var units = metadata[5].EnumerateArray().Select(item => item.GetString()!).ToArray();
        Need(fieldNames.Length == metadata[1].GetInt32() && units.Length == fieldNames.Length && fieldNames.Distinct(StringComparer.Ordinal).Count() == fieldNames.Length,
            "Table field metadata is incomplete or duplicated.");
        var included = data[shift + 1].EnumerateArray().Select(item => item.GetString()!).ToArray();
        Need(included.Length > 0 && included.Distinct(StringComparer.Ordinal).Count() == included.Length && included.All(fieldNames.Contains) && included.Contains(specification.IdentityField),
            "The included source fields are unresolved.");
        var count = data[shift + 2].GetInt32();
        SourceRowCount = count;
        var cells = data[shift + 3].ValueKind == JsonValueKind.Null ? [] : data[shift + 3].EnumerateArray().Select(item => item.GetString()).ToArray();
        Need(count >= 0 && cells.LongLength == (long)count * included.Length, "The table is truncated.");
        var fieldUnits = fieldNames.Select((name, index) => (name, units[index])).ToDictionary(item => item.name, item => item.Item2, StringComparer.Ordinal);
        if (specification.Editing)
        {
            var importable = metadata[6].EnumerateArray().Select(item => item.GetBoolean()).ToArray();
            Need(importable.Length == fieldNames.Length && included.SequenceEqual(fieldNames.Where((_, index) => importable[index])),
                "An editing export must retain the complete importable source field sequence, including blank defaults.");
        }
        if (Key == "Frame Assignments - Property Modifiers")
            foreach (var field in new[] { "AMod", "A2Mod", "A3Mod", "JMod", "I2Mod", "I3Mod", "MMod", "WMod" })
                Need(fieldUnits.TryGetValue(field, out var unit) && unit == "" && included.Contains(field), "Modifier-default evidence has incomplete fields or units.");
        if (Key == "Frame Assignments - Releases and Partial Fixity")
            foreach (var dof in new[] { "P", "V2", "V3", "T", "M2", "M3" })
                foreach (var end in new[] { "I", "J" })
                {
                    Need(included.Contains(dof + end) && included.Contains(dof + end + "Spring"), "Release-default evidence has incomplete fields.");
                    Need(fieldUnits[dof + end] == "" && fieldUnits[dof + end + "Spring"] == (dof is "P" or "V2" or "V3" ? "kN/m" : "kN-m/rad"),
                        "Release-default evidence has unqualified units.");
                }
        var rows = new Dictionary<string, Row>(StringComparer.Ordinal);
        for (var index = 0; index < count; index++)
        {
            var row = new Row(included.Select((name, column) => (name, cells[index * included.Length + column]))
                .ToDictionary(item => item.name, item => item.Item2, StringComparer.Ordinal), fieldUnits);
            // Shell-generated line records share names and can repeat connectivity. They stay
            // in the full getter payload as context; only source Frame rows define beam meshes.
            if (specification.ScopeField is { } scope && row.Required(scope) != specification.ScopeValue)
            {
                ContextOnlyRowCount++;
                continue;
            }
            Need(rows.TryAdd(row.Required(specification.IdentityField), row), "A table has duplicate source identities.");
        }
        Rows = rows;
    }

    internal Row Required(string id) => Rows.TryGetValue(id, out var row) ? row : throw new InvalidDataException($"{Key}: source row {id} is absent.");
    private void Need(bool valid, string message) { if (!valid) throw new InvalidDataException($"{Key}: {message}"); }

    internal sealed class Row(IReadOnlyDictionary<string, string?> values, IReadOnlyDictionary<string, string> units)
    {
        internal string? Optional(string key)
        {
            if (!units.ContainsKey(key)) throw new InvalidDataException($"Required source field {key} is unknown in the table metadata.");
            return values.TryGetValue(key, out var value) && !string.IsNullOrEmpty(value) ? value : null;
        }
        internal string Required(string key) => Optional(key) ?? throw new InvalidDataException($"Required source field {key} is absent.");
        internal bool Boolean(string key) => Required(key) switch { "Yes" => true, "No" => false, _ => throw new InvalidDataException($"Unknown source boolean in {key}.") };
        internal double Number(string key, string unit = "", double? blankDefault = null)
        {
            if (!units.TryGetValue(key, out var sourceUnit) || sourceUnit != unit) throw new InvalidDataException($"Source field {key} has an unqualified unit.");
            var text = Optional(key);
            if (text is null && blankDefault is { } value) return value;
            if (!double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var number) || !double.IsFinite(number))
                throw new InvalidDataException($"Source field {key} is not a complete finite numeric value.");
            return number;
        }
    }
}
