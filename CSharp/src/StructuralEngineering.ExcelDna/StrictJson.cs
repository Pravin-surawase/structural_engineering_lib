using System.Text.Json;
using System.Text.Json.Serialization;

namespace StructuralEngineering.ExcelDna;

internal sealed class WorksheetInputException(string code, string message) : ArgumentException(message)
{
    public string Code { get; } = code;
}

internal static class StrictJson
{
    public static T Deserialize<T>(object requestJson)
    {
        if (requestJson is not string json || string.IsNullOrWhiteSpace(json))
            throw new WorksheetInputException("INPUT.REQUIRED", "Supply a non-blank JSON request.");

        try
        {
            return JsonSerializer.Deserialize<T>(json, Options())
                ?? throw new WorksheetInputException("INPUT.REQUIRED", "The JSON request must not be null.");
        }
        catch (JsonException exception)
        {
            throw new WorksheetInputException("INPUT.JSON_INVALID", exception.Message);
        }
    }

    public static double Number(object value, string field)
    {
        if (value is not double number || !double.IsFinite(number))
            throw new WorksheetInputException("INPUT.REQUIRED", $"{field} must be a finite number; blank cells are not zero.");
        return number;
    }

    public static JsonSerializerOptions Options()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
            PropertyNameCaseInsensitive = false,
            WriteIndented = false
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        return options;
    }
}
