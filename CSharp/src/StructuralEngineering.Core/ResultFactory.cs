using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Core;

public static class ResultFactory
{
    public const string SchemaVersion = "structural-operation-result/v1";
    public const string CanonicalizationVersion = "pf4-canonical-json-v1";

    private static readonly JsonSerializerOptions CanonicalOptions = CreateOptions();

    public static IReadOnlyDictionary<string, EffectiveValue> Effective(
        params (string Key, object? Value)[] values) =>
        values.ToDictionary(item => item.Key,
            item => new EffectiveValue(item.Value, Dependencies: []), StringComparer.Ordinal);

    public static ResultEnvelope<TOutput> Completed<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        TOutput output,
        Provenance provenance,
        EngineeringState engineering = EngineeringState.Pass,
        params Diagnostic[] diagnostics) =>
        Build(operation, inputs, output, provenance, ExecutionState.Completed,
            ApplicabilityState.Applicable, engineering, CompletenessState.CompleteForScope,
            FreshnessState.Current, diagnostics);

    public static ResultEnvelope<TOutput> Rejected<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance,
        params Diagnostic[] diagnostics) =>
        Build<TOutput>(operation, inputs, default, provenance, ExecutionState.RejectedInput,
            ApplicabilityState.Unknown, EngineeringState.NotEvaluated, CompletenessState.Partial,
            FreshnessState.Unbound, diagnostics);

    public static ResultEnvelope<TOutput> NotApplicable<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance,
        params Diagnostic[] diagnostics) =>
        Build<TOutput>(operation, inputs, default, provenance, ExecutionState.Completed,
            ApplicabilityState.NotApplicable, EngineeringState.NotEvaluated,
            CompletenessState.CompleteForScope, FreshnessState.Current, diagnostics);

    public static ResultEnvelope<TOutput> NotEvaluated<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        Provenance provenance,
        params Diagnostic[] diagnostics) =>
        Build<TOutput>(operation, inputs, default, provenance, ExecutionState.Completed,
            ApplicabilityState.Unknown, EngineeringState.NotEvaluated,
            CompletenessState.Partial, FreshnessState.Current, diagnostics);

    public static ResultEnvelope<TOutput> Partial<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        TOutput output,
        Provenance provenance,
        FreshnessState freshness = FreshnessState.Current,
        params Diagnostic[] diagnostics) =>
        Build(operation, inputs, output, provenance, ExecutionState.Completed,
            ApplicabilityState.Applicable, EngineeringState.NotEvaluated,
            CompletenessState.Partial, freshness, diagnostics);

    public static string NormalizedInputId(object inputs) => Hash("normalized_input_id", inputs);

    public static string SemanticId(string kind, object value) => Hash(kind, value);

    public static string CalculationId(string operation, Provenance provenance, string normalizedInputId) =>
        Hash("calculation_id", new Dictionary<string, object?>
        {
            ["code_data_revision_id"] = provenance.CodeDataRevisionId,
            ["engine_build"] = provenance.MethodRevisionId,
            ["normalized_input_id"] = normalizedInputId,
            ["operation_semantic_id"] = operation
        });

    public static byte[] CanonicalJsonBytes(object value) =>
        Encoding.UTF8.GetBytes(Canonical(JsonSerializer.SerializeToNode(value, CanonicalOptions)!));

    private static ResultEnvelope<TOutput> Build<TOutput>(
        string operation,
        IReadOnlyDictionary<string, EffectiveValue> inputs,
        TOutput? output,
        Provenance provenance,
        ExecutionState execution,
        ApplicabilityState applicability,
        EngineeringState engineering,
        CompletenessState completeness,
        FreshnessState freshness,
        IReadOnlyList<Diagnostic> diagnostics)
    {
        var normalized = NormalizedInputId(inputs);
        var calculation = execution == ExecutionState.Completed
            ? CalculationId(operation, provenance, normalized)
            : string.Empty;
        var outcome = new Dictionary<string, object?>
        {
            ["applicability"] = applicability,
            ["calculation_id"] = calculation,
            ["completeness"] = completeness,
            ["diagnostics"] = diagnostics,
            ["engineering"] = engineering,
            ["execution"] = execution,
            ["freshness"] = freshness,
            ["outputs"] = output
        };
        return new ResultEnvelope<TOutput>(SchemaVersion, operation, execution, applicability,
            engineering, completeness, freshness, ApprovalState.Unreviewed, inputs, output,
            diagnostics, provenance, normalized, calculation, Hash("result_id", outcome));
    }

    private static string Hash(string kind, object value) =>
        kind + ":" + CanonicalizationVersion + ":" +
        Convert.ToHexStringLower(SHA256.HashData(CanonicalJsonBytes(value)));

    private static string Canonical(JsonNode? node) => node switch
    {
        JsonObject obj => "{" + string.Join(",", obj.OrderBy(pair => pair.Key, StringComparer.Ordinal)
            .Select(pair => JsonSerializer.Serialize(pair.Key) + ":" + Canonical(pair.Value))) + "}",
        JsonArray array => "[" + string.Join(",", array.Select(Canonical)) + "]",
        _ => node?.ToJsonString(CanonicalOptions) ?? "null"
    };

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            WriteIndented = false
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        return options;
    }
}

public static class Validation
{
    public static bool Positive(double value) => double.IsFinite(value) && value > 0;
    public static bool Nonnegative(double value) => double.IsFinite(value) && value >= 0;
}
