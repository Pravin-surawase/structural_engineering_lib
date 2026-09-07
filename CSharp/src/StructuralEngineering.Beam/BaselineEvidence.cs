using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Beam;

public static class BaselineEvidence
{
    private static readonly JsonSerializerOptions Options = CreateOptions();
    public static ResultEnvelope<JsonElement> Pack<T>(ResultEnvelope<T> result) => new(
        result.SchemaVersion, result.OperationSemanticId, result.Execution, result.Applicability,
        result.Engineering, result.Completeness, result.Freshness, result.Approval,
        result.EffectiveInputs, JsonSerializer.SerializeToElement(result.Outputs, Options), result.Diagnostics,
        result.Provenance, result.NormalizedInputId, result.CalculationId, result.ResultId);
    public static bool Qualified<T>(ResultEnvelope<T> result) => result.Execution == ExecutionState.Completed &&
        result.Completeness == CompletenessState.CompleteForScope && result.Freshness == FreshnessState.Current &&
        (result.Applicability == ApplicabilityState.Applicable && result.Engineering == EngineeringState.Pass ||
        result.Applicability == ApplicabilityState.NotApplicable && result.Engineering == EngineeringState.NotEvaluated);

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        return options;
    }
}
