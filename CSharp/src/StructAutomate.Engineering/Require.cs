using StructAutomate.Contracts;

namespace StructAutomate.Engineering;

public static class Require
{
    public static void That(bool condition, string path, string message, string code = "invalid_input")
    {
        if (!condition) throw new InputValidationException(new InputProblem(code, path, message));
    }
    public static void Finite(double value, string path) => That(double.IsFinite(value), path, "Enter a finite number.");
    public static void Positive(double value, string path)
    {
        Finite(value, path);
        That(value > 0, path, "Enter a value greater than zero.");
    }
    public static void Nonnegative(double value, string path)
    {
        Finite(value, path);
        That(value >= 0, path, "Enter zero or a positive value.");
    }
    public static void Text(string? value, string path) => That(!string.IsNullOrWhiteSpace(value), path, "Enter a value.");
    public static void Version(string version) => That(version == ContractJson.SchemaVersion, "schemaVersion", "Use schema version 1.0.0.");
    public static void Unique(IEnumerable<string> ids, string path)
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var id in ids)
        {
            Text(id, path);
            That(seen.Add(id), path, $"Duplicate identifier: {id}.");
        }
    }
}
