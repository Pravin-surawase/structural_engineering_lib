using System.Security.Cryptography;
using System.Text.Json;

namespace StructuralEngineering.Etabs;

/// <summary>Host-free strict replay of an accepted WP10-02 getter capture.</summary>
public sealed class EtabsRecordedGetterHost : IEtabsGetterHost, IEtabsGetterHostCompletionVerifier
{
    private readonly IReadOnlyList<RecordedCall> _calls;
    private int _nextCall;
    private bool _disposed;

    private EtabsRecordedGetterHost(
        EtabsHostIdentity identity,
        EtabsLiveGetterProbeRequest recordedRequest,
        string recordedPreflightSha256,
        IReadOnlyList<RecordedCall> calls)
    {
        Identity = identity;
        RecordedRequest = recordedRequest;
        RecordedPreflightSha256 = recordedPreflightSha256;
        _calls = calls;
    }

    public EtabsHostIdentity Identity { get; }
    public EtabsLiveGetterProbeRequest RecordedRequest { get; }
    public string RecordedPreflightSha256 { get; }
    public int RemainingCallCount => _calls.Count - _nextCall;

    public static EtabsRecordedGetterHost Load(string path, string expectedSha256)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        ArgumentException.ThrowIfNullOrWhiteSpace(expectedSha256);
        var fullPath = Path.GetFullPath(path);
        using (var stream = File.OpenRead(fullPath))
        {
            var actualSha = Convert.ToHexStringLower(SHA256.HashData(stream));
            if (!string.Equals(actualSha, expectedSha256, StringComparison.Ordinal))
                throw new InvalidDataException("The recorded getter-capture SHA-256 does not match its expectation.");
        }

        using var document = JsonDocument.Parse(File.ReadAllText(fullPath));
        var root = document.RootElement;
        RequireString(root, "Verdict", "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM");
        RequireString(root, "GetterMatrixSha256", EtabsGetterMatrix.Sha256);
        var identity = JsonSerializer.Deserialize<EtabsHostIdentity>(
            root.GetProperty("HostIdentity").GetRawText())
            ?? throw new InvalidDataException("The recorded capture has no host identity.");
        var recordedRequest = JsonSerializer.Deserialize<EtabsLiveGetterProbeRequest>(
            root.GetProperty("Request").GetRawText())
            ?? throw new InvalidDataException("The recorded capture has no request.");
        var recordedPreflightSha256 = root.GetProperty("Preflight").GetProperty("Sha256").GetString()
            ?? throw new InvalidDataException("The recorded capture has no preflight identity.");
        var calls = root.GetProperty("Calls")
            .EnumerateArray()
            .Select(ParseCall)
            .ToArray();
        if (calls.Length == 0)
            throw new InvalidDataException("The recorded capture contains no getter calls.");
        return new(identity, recordedRequest, recordedPreflightSha256, calls);

        RecordedCall ParseCall(JsonElement value)
        {
            var operation = value.GetProperty("Operation").GetString()
                ?? throw new InvalidDataException("A recorded getter operation is blank.");
            if (!EtabsGetterMatrix.Allowed.TryGetValue(operation, out var definition))
                throw new InvalidDataException($"Recorded operation {operation} is outside the frozen getter matrix.");
            RequireString(value, "GetterMatrixSha256", EtabsGetterMatrix.Sha256);
            var callIdentity = JsonSerializer.Deserialize<EtabsHostIdentity>(
                value.GetProperty("HostIdentity").GetRawText())
                ?? throw new InvalidDataException("A recorded getter call has no host identity.");
            if (callIdentity != identity)
                throw new InvalidDataException("A recorded getter call has a different host identity.");
            var outputs = value.GetProperty("Outputs");
            if (outputs.ValueKind != JsonValueKind.Array || outputs.GetArrayLength() != definition.OutputKinds.Length)
                throw new InvalidDataException($"Recorded operation {operation} has the wrong output count.");
            return new(
                operation,
                value.GetProperty("Inputs").Clone(),
                value.GetProperty("DirectValue").Clone(),
                outputs.Clone(),
                value.GetProperty("CsiReturnCode").ValueKind == JsonValueKind.Null
                    ? null
                    : value.GetProperty("CsiReturnCode").GetInt32());
        }
    }

    public EtabsInvocation Invoke(
        EtabsGetterDefinition definition,
        IReadOnlyList<object?> inputs,
        CancellationToken cancellationToken)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        cancellationToken.ThrowIfCancellationRequested();
        if (_nextCall >= _calls.Count)
            throw new InvalidOperationException("The recorded getter capture is exhausted.");
        var recorded = _calls[_nextCall];
        if (recorded.Operation != definition.Operation)
            throw new InvalidOperationException(
                $"Recorded getter order mismatch: expected {recorded.Operation}; received {definition.Operation}.");
        var actualInputs = JsonSerializer.SerializeToElement(inputs);
        if (!Equivalent(recorded.Inputs, actualInputs))
            throw new InvalidOperationException($"Recorded getter inputs differ for {definition.Operation}.");

        _nextCall++;
        var outputs = recorded.Outputs
            .EnumerateArray()
            .Select((value, index) => ConvertValue(value, definition.OutputKinds[index]))
            .ToArray();
        object? returnValue = definition.ReturnSemantics == EtabsReturnSemantics.FinalCsiReturnCode
            ? recorded.CsiReturnCode ?? throw new InvalidDataException(
                $"Recorded status getter {definition.Operation} has no CSI return code.")
            : ConvertValue(recorded.DirectValue, definition.DirectValueKind);
        return new(returnValue, outputs);
    }

    public void AssertComplete()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (RemainingCallCount != 0)
            throw new InvalidOperationException(
                $"The recorded getter replay has {RemainingCallCount} unconsumed calls.");
    }

    public void Dispose() => _disposed = true;

    private static object? ConvertValue(JsonElement value, EtabsRawValueKind kind)
    {
        if (value.ValueKind == JsonValueKind.Null)
            return kind is EtabsRawValueKind.StringArray or EtabsRawValueKind.BooleanArray or
                EtabsRawValueKind.Int32Array or EtabsRawValueKind.DoubleArray
                ? null
                : throw new InvalidDataException($"A recorded {kind} value is null.");
        return kind switch
        {
            EtabsRawValueKind.String => value.GetString(),
            EtabsRawValueKind.Boolean => value.GetBoolean(),
            EtabsRawValueKind.Int32 => value.GetInt32(),
            EtabsRawValueKind.Double => value.GetDouble(),
            EtabsRawValueKind.StringArray => value.EnumerateArray()
                .Select(item => item.ValueKind == JsonValueKind.Null ? null : item.GetString()).Cast<object?>().ToArray(),
            EtabsRawValueKind.BooleanArray => value.EnumerateArray()
                .Select(item => (object?)item.GetBoolean()).ToArray(),
            EtabsRawValueKind.Int32Array => value.EnumerateArray()
                .Select(item => (object?)item.GetInt32()).ToArray(),
            EtabsRawValueKind.DoubleArray => value.EnumerateArray()
                .Select(item => (object?)item.GetDouble()).ToArray(),
            _ => throw new InvalidDataException($"Recorded value kind {kind} is unsupported.")
        };
    }

    private static bool Equivalent(JsonElement expected, JsonElement actual)
    {
        if (expected.ValueKind == JsonValueKind.Number && actual.ValueKind == JsonValueKind.Number)
            return expected.GetDouble().Equals(actual.GetDouble());
        if (expected.ValueKind != actual.ValueKind)
            return false;
        return expected.ValueKind switch
        {
            JsonValueKind.Array => expected.GetArrayLength() == actual.GetArrayLength() &&
                expected.EnumerateArray().Zip(actual.EnumerateArray()).All(pair => Equivalent(pair.First, pair.Second)),
            JsonValueKind.String => expected.GetString() == actual.GetString(),
            JsonValueKind.True or JsonValueKind.False => expected.GetBoolean() == actual.GetBoolean(),
            JsonValueKind.Null => true,
            _ => expected.GetRawText() == actual.GetRawText()
        };
    }

    private static void RequireString(JsonElement value, string property, string expected)
    {
        if (value.GetProperty(property).GetString() != expected)
            throw new InvalidDataException($"Recorded {property} differs from its frozen expectation.");
    }

    private sealed record RecordedCall(
        string Operation,
        JsonElement Inputs,
        JsonElement DirectValue,
        JsonElement Outputs,
        int? CsiReturnCode);
}
