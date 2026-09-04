using System.Text.Json;

namespace StructuralEngineering.ExcelDna;

internal static class ResultSpill
{
    private const int ExcelCellCharacterLimit = 32767;

    public static object[,] From(object result)
    {
        using var document = JsonDocument.Parse(JsonSerializer.Serialize(result, StrictJson.Options()));
        var rows = document.RootElement.EnumerateObject()
            .SelectMany(Rows)
            .ToArray();
        if (rows.Any(row => row.Value is string text && text.Length > ExcelCellCharacterLimit))
            return Diagnostic("EXCEL.RESULT_TOO_LARGE", "The structured result exceeds Excel's per-cell character limit.");

        var spill = new object[rows.Length, 2];
        for (var index = 0; index < rows.Length; index++)
        {
            spill[index, 0] = rows[index].Key;
            spill[index, 1] = rows[index].Value;
        }
        return spill;
    }

    public static object[,] Diagnostic(string code, string message) => new object[,]
    {
        { "execution", "rejected_input" },
        { "diagnostic_code", code },
        { "message", message }
    };

    private static IEnumerable<(string Key, object Value)> Rows(JsonProperty property)
    {
        if (property.NameEquals("outputs") && property.Value.ValueKind == JsonValueKind.Object)
        {
            foreach (var output in property.Value.EnumerateObject())
                yield return ($"outputs.{output.Name}", Value(output.Value));
            yield break;
        }
        yield return (property.Name, Value(property.Value));
    }

    private static object Value(JsonElement value) => value.ValueKind switch
    {
        JsonValueKind.String => value.GetString() ?? string.Empty,
        JsonValueKind.Number when value.TryGetInt64(out var integer) => integer,
        JsonValueKind.Number => value.GetDouble(),
        JsonValueKind.True => true,
        JsonValueKind.False => false,
        JsonValueKind.Null => "null",
        _ => value.GetRawText()
    };
}
