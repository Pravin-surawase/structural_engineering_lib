using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

namespace StructAutomate.Contracts;

public static class ContractJson
{
    public const string SchemaVersion = "1.0.0";

    public static JsonSerializerOptions CreateOptions() => new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
        RespectRequiredConstructorParameters = true,
        RespectNullableAnnotations = true,
        TypeInfoResolver = new DefaultJsonTypeInfoResolver(),
        WriteIndented = true,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.CamelCase, allowIntegerValues: false) }
    };
}

public sealed record InputProblem(string Code, string Path, string Message);

public sealed class InputValidationException : ArgumentException
{
    public IReadOnlyList<InputProblem> Problems { get; }
    public InputValidationException(params InputProblem[] problems)
        : base(string.Join("; ", problems.Select(p => $"{p.Path}: {p.Message}"))) => Problems = problems;
}

public enum CheckOutcome { Pass, Fail, NotApplicable, NotEvaluated }

public sealed record CheckResult(
    string CheckId, CheckOutcome Outcome, string Basis, string? GoverningActionRowId,
    double? Demand, double? Capacity, string? Unit, double? Utilization,
    IReadOnlyList<string> SourceReferences);
