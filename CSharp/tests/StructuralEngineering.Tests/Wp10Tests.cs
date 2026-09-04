using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class Wp10Tests
{
    private static readonly JsonObject Fixture = LoadFixture();

    [Fact]
    public void ImportRequestRetainsExplicitScopeAndOptionalEvidence()
    {
        var request = AnalysisSnapshotCodec.ParseImportRequest(
            Fixture["valid_request"]!.ToJsonString());

        Assert.Equal("etabs.beam_snapshot.import/v1", request.OperationSemanticId);
        Assert.Equal(["member-b1"], request.Scope.Members.MemberIds);
        Assert.Equal(["selection-uls"], request.Scope.ResultSelectionIds);
        Assert.Equal(OptionalEvidenceState.Supplied, request.SourceExpectation.ProcessIdentity.State);
        Assert.NotNull(request.SourceExpectation.ModelFileSha256.Value);
    }

    [Fact]
    public void ImportRequestRejectsInvalidShaAndEmptyExplicitScope()
    {
        var invalidSha = Fixture["valid_request"]!.DeepClone().AsObject();
        invalidSha["source_expectation"]!["model_file_sha256"]!["value"] = "bad";
        var emptyExplicit = Fixture["valid_request"]!.DeepClone().AsObject();
        emptyExplicit["scope"]!["members"]!["member_ids"] = new JsonArray();

        Assert.Throws<ArgumentException>(() =>
            AnalysisSnapshotCodec.ParseImportRequest(invalidSha.ToJsonString()));
        Assert.Throws<ArgumentException>(() =>
            AnalysisSnapshotCodec.ParseImportRequest(emptyExplicit.ToJsonString()));
    }

    [Fact]
    public void ValidSnapshotMatchesPythonCanonicalIdentityAndBytes()
    {
        var expected = Fixture["expected"]!.AsObject();
        var result = AnalysisSnapshotCodec.ParseAndValidate(
            Fixture["valid_snapshot"]!.ToJsonString());

        Assert.True(
            result.OperationState == SnapshotOperationState.Completed,
            string.Join(" | ", result.Diagnostics.Select(item => item.Message)));
        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(ApplicabilityState.Applicable, result.Applicability);
        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(CompletenessState.CompleteForScope, result.Completeness);
        Assert.Equal(FreshnessState.Current, result.Freshness);
        Assert.Equal(ApprovalState.Unreviewed, result.Approval);
        var snapshot = Assert.IsType<AnalysisSnapshot>(result.Snapshot);
        Assert.Equal(expected["snapshot_id"]!.GetValue<string>(), snapshot.SnapshotId);
        Assert.Equal(expected["raw_capture_id"]!.GetValue<string>(), snapshot.RawCapture.RawCaptureId);

        var canonical = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
        Assert.Equal(expected["canonical_json_byte_count"]!.GetValue<int>(), canonical.Length);
        Assert.Equal(
            expected["canonical_json_sha256"]!.GetValue<string>(),
            Convert.ToHexStringLower(SHA256.HashData(canonical)));
        var replay = Assert.IsType<AnalysisSnapshot>(
            AnalysisSnapshotCodec.ParseAndValidate(
                AnalysisSnapshotCodec.CanonicalJson(snapshot)).Snapshot);
        Assert.Equal(
            AnalysisSnapshotCodec.CanonicalJson(snapshot),
            AnalysisSnapshotCodec.CanonicalJson(replay));
    }

    [Fact]
    public void DuplicateKeysAndNonFiniteNumbersAreRejected()
    {
        var payload = Fixture["valid_snapshot"]!.ToJsonString();
        var invalidPayloads = new[]
        {
            "{\"schema_version\":\"duplicate\"," + payload[1..],
            payload.Replace("\"p\":-12000", "\"p\":NaN", StringComparison.Ordinal)
        };

        foreach (var invalid in invalidPayloads)
        {
            var result = AnalysisSnapshotCodec.ParseAndValidate(invalid);
            Assert.Equal(SnapshotOperationState.PreflightRejected, result.OperationState);
            Assert.Equal(ExecutionState.RejectedInput, result.Execution);
            Assert.Equal("INPUT.SCHEMA", Assert.Single(result.Diagnostics).Code);
        }
    }

    public static TheoryData<string, string, string, string> InvalidVectors()
    {
        var data = new TheoryData<string, string, string, string>();
        foreach (var item in Fixture["invalid_vectors"]!.AsArray())
        {
            var vector = item!.AsObject();
            var expected = vector["expected"]!.AsObject();
            data.Add(
                vector.ToJsonString(),
                expected["operation_state"]!.GetValue<string>(),
                expected["execution"]!.GetValue<string>(),
                expected["diagnostic"]!.GetValue<string>());
        }
        return data;
    }

    [Theory]
    [MemberData(nameof(InvalidVectors))]
    public void InvalidSnapshotVectorsFailClosed(
        string vectorJson,
        string expectedOperationState,
        string expectedExecution,
        string expectedDiagnostic)
    {
        var snapshot = Fixture["valid_snapshot"]!.DeepClone().AsObject();
        var vector = JsonNode.Parse(vectorJson)!.AsObject();
        foreach (var mutation in vector["mutations"]!.AsArray())
            Mutate(snapshot, mutation!.AsObject());

        var result = AnalysisSnapshotCodec.ParseAndValidate(snapshot.ToJsonString());

        Assert.Null(result.Snapshot);
        Assert.Equal(expectedOperationState, Snake(result.OperationState));
        Assert.Equal(expectedExecution, Snake(result.Execution));
        Assert.Equal(expectedDiagnostic, Assert.Single(result.Diagnostics).Code);
    }

    [Fact]
    public void PortableAssembliesDoNotReferenceEtabsOrOfficeHosts()
    {
        var references = typeof(AnalysisSnapshotCodec).Assembly
            .GetReferencedAssemblies()
            .Select(item => item.Name ?? string.Empty)
            .ToArray();

        Assert.DoesNotContain(references, name =>
            name.Contains("ETABS", StringComparison.OrdinalIgnoreCase) ||
            name.Contains("SAP2000", StringComparison.OrdinalIgnoreCase) ||
            name.Contains("Office", StringComparison.OrdinalIgnoreCase) ||
            name.Contains("Excel", StringComparison.OrdinalIgnoreCase));
    }

    private static void Mutate(JsonObject root, JsonObject mutation)
    {
        var parts = mutation["path"]!.GetValue<string>()
            .TrimStart('/')
            .Split('/');
        JsonNode target = root;
        foreach (var part in parts[..^1])
            target = target is JsonArray array
                ? array[int.Parse(part)]!
                : target[part]!;
        var leaf = parts[^1];
        if (mutation["operation"]!.GetValue<string>() == "remove")
        {
            if (target is JsonArray array) array.RemoveAt(int.Parse(leaf));
            else target.AsObject().Remove(leaf);
            return;
        }

        var replacement = mutation["value"]?.DeepClone();
        if (target is JsonArray targetArray) targetArray[int.Parse(leaf)] = replacement;
        else target.AsObject()[leaf] = replacement;
    }

    private static string Snake<T>(T value) where T : struct, Enum =>
        JsonSerializer.Serialize(value, new JsonSerializerOptions
        {
            Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower) }
        }).Trim('"');

    private static JsonObject LoadFixture()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(
                directory.FullName,
                "contracts",
                "structural-engineering",
                "conformance",
                "wp10-vectors.json");
            if (File.Exists(path))
                return JsonNode.Parse(File.ReadAllText(path))!.AsObject();
            directory = directory.Parent;
        }
        throw new FileNotFoundException("WP10 conformance fixture was not found.");
    }
}
