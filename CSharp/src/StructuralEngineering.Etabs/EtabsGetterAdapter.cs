namespace StructuralEngineering.Etabs;

public sealed record EtabsHostIdentity(
    int ProcessId,
    DateTimeOffset ProcessStartedUtc,
    string ExecutablePath,
    string ExecutableFileVersion,
    long ExecutableBytes,
    string ExecutableSha256,
    string ApiAssemblyPath,
    string ApiAssemblyIdentity,
    string ApiFileVersion,
    string ApiSha256,
    string TypeLibraryPath,
    long TypeLibraryBytes,
    string TypeLibrarySha256,
    string ModelPath,
    long ModelBytes,
    DateTimeOffset ModelModifiedUtc,
    string ModelSha256,
    string EtabsApiVersion,
    bool ModelLocked,
    int PresentUnits);

public sealed record EtabsInvocation(
    object? ReturnValue,
    IReadOnlyList<object?> Outputs);

public interface IEtabsGetterHost : IDisposable
{
    EtabsHostIdentity Identity { get; }

    EtabsInvocation Invoke(
        EtabsGetterDefinition definition,
        IReadOnlyList<object?> inputs,
        CancellationToken cancellationToken);
}

public enum EtabsGetterState
{
    Completed,
    Rejected
}

public sealed record EtabsRawGetterCall(
    string Operation,
    IReadOnlyList<object?> Inputs,
    object? DirectValue,
    IReadOnlyList<object?> Outputs,
    int? CsiReturnCode,
    DateTimeOffset StartedUtc,
    DateTimeOffset CompletedUtc,
    string GetterMatrixSha256,
    EtabsHostIdentity HostIdentity);

public sealed record EtabsGetterResult(
    EtabsGetterState State,
    string? DiagnosticCode,
    string? Message,
    EtabsRawGetterCall? RawCall)
{
    public static EtabsGetterResult Rejected(string code, string message) =>
        new(EtabsGetterState.Rejected, code, message, null);
}

public sealed class EtabsGetterAdapter(IEtabsGetterHost host)
{
    public EtabsGetterResult Read(
        string operation,
        IReadOnlyList<object?> inputs,
        DateTimeOffset deadlineUtc,
        CancellationToken cancellationToken = default)
    {
        if (!EtabsGetterMatrix.Allowed.TryGetValue(operation, out var definition))
            return EtabsGetterResult.Rejected(
                "ETABS.CALL_NOT_ALLOWED",
                $"Operation '{operation}' is outside the frozen getter whitelist.");

        var started = DateTimeOffset.UtcNow;
        if (started >= deadlineUtc || cancellationToken.IsCancellationRequested)
            return EtabsGetterResult.Rejected(
                "ETABS.CALL_TIMEOUT",
                "The getter deadline elapsed before dispatch; no call was issued.");

        var before = host.Identity;
        EtabsInvocation invocation;
        try
        {
            invocation = host.Invoke(definition, inputs, cancellationToken);
        }
        catch (TimeoutException exception)
        {
            return EtabsGetterResult.Rejected("ETABS.CALL_TIMEOUT", exception.Message);
        }
        catch (OperationCanceledException exception)
        {
            return EtabsGetterResult.Rejected("ETABS.CALL_TIMEOUT", exception.Message);
        }
        catch (Exception exception)
        {
            return EtabsGetterResult.Rejected(
                "ETABS.CALL_FAILED",
                $"{exception.GetType().Name}: {exception.Message}");
        }

        var completed = DateTimeOffset.UtcNow;
        if (completed >= deadlineUtc)
            return EtabsGetterResult.Rejected(
                "ETABS.CALL_TIMEOUT",
                "The getter returned after its deadline; its outputs are not accepted.");
        if (before != host.Identity)
            return EtabsGetterResult.Rejected(
                "ETABS.IDENTITY_DRIFT",
                "The attached process, runtime, or model identity changed during the getter.");

        int? csiCode = null;
        object? directValue = null;
        if (definition.ReturnSemantics is EtabsReturnSemantics.FinalCsiReturnCode)
        {
            if (invocation.ReturnValue is not int exactCode)
                return EtabsGetterResult.Rejected(
                    "ETABS.RETURN_SHAPE_INVALID",
                    $"{operation} did not return an exact Int32 CSI status.");
            csiCode = exactCode;
            if (exactCode != 0)
                return EtabsGetterResult.Rejected(
                    "ETABS.CSI_RETURN_CODE",
                    $"{operation} returned CSI status {exactCode}.");
        }
        else
        {
            directValue = invocation.ReturnValue;
            if (!HasExactKind(
                    directValue,
                    definition.DirectValueKind,
                    allowNullArray: false,
                    allowNullStringElements: false))
                return EtabsGetterResult.Rejected(
                    "ETABS.RETURN_TYPE_INVALID",
                    $"{operation} direct value does not match its frozen managed type.");
        }

        if (invocation.Outputs.Count != definition.OutputNames.Count)
            return EtabsGetterResult.Rejected(
                "ETABS.RETURN_SHAPE_INVALID",
                $"{operation} returned {invocation.Outputs.Count} outputs; {definition.OutputNames.Count} are required.");

        var countedZero = definition.CountOutputIndex is int countPosition &&
            invocation.Outputs[countPosition] is int exactCount && exactCount == 0;
        for (var index = 0; index < invocation.Outputs.Count; index++)
        {
            var allowNullArray = countedZero && definition.ParallelArrays.Contains(index);
            var allowNullStringElements = definition.NullableStringArrays.Contains(index);
            if (!HasExactKind(
                    invocation.Outputs[index],
                    definition.OutputKinds[index],
                    allowNullArray,
                    allowNullStringElements))
                return EtabsGetterResult.Rejected(
                    "ETABS.RETURN_TYPE_INVALID",
                    $"{operation} output {definition.OutputNames[index]} does not match its frozen managed type.");
        }

        var shapeError = ValidateArrays(definition, invocation.Outputs);
        if (shapeError is not null)
            return EtabsGetterResult.Rejected(shapeError.Value.Code, shapeError.Value.Message);

        return new EtabsGetterResult(
            EtabsGetterState.Completed,
            null,
            null,
            new EtabsRawGetterCall(
                operation,
                inputs.ToArray(),
                directValue,
                invocation.Outputs.ToArray(),
                csiCode,
                started,
                completed,
                EtabsGetterMatrix.Sha256,
                before));
    }

    private static (string Code, string Message)? ValidateArrays(
        EtabsGetterDefinition definition,
        IReadOnlyList<object?> outputs)
    {
        if (definition.CountOutputIndex is int countIndex)
        {
            if (countIndex >= outputs.Count || outputs[countIndex] is not int count || count < 0)
                return ("ETABS.RETURN_SHAPE_INVALID",
                    $"{definition.Operation} did not return a non-negative exact Int32 count.");
            foreach (var index in definition.ParallelArrays)
            {
                var length = ArrayLength(outputs[index], count);
                if (length != count)
                    return ("ETABS.ARRAY_LENGTH_MISMATCH",
                        $"{definition.Operation} output {definition.OutputNames[index]} has length {length}; expected {count}.");
            }
        }

        foreach (var (index, expected) in definition.FixedArrays)
        {
            var length = ArrayLength(outputs[index], expected);
            if (length != expected)
                return ("ETABS.ARRAY_LENGTH_MISMATCH",
                    $"{definition.Operation} output {definition.OutputNames[index]} has length {length}; expected {expected}.");
        }
        return null;
    }

    private static int ArrayLength(object? value, int expectedWhenNull)
    {
        if (value is null)
            return expectedWhenNull == 0 ? 0 : -1;
        if (value is Array array)
            return array.Length;
        if (value is System.Collections.ICollection collection)
            return collection.Count;
        return -1;
    }

    private static bool HasExactKind(
        object? value,
        EtabsRawValueKind kind,
        bool allowNullArray,
        bool allowNullStringElements)
    {
        if (value is null)
            return allowNullArray && IsArrayKind(kind);
        return kind switch
        {
            EtabsRawValueKind.String => value.GetType() == typeof(string),
            EtabsRawValueKind.Boolean => value.GetType() == typeof(bool),
            EtabsRawValueKind.Int32 => value.GetType() == typeof(int),
            EtabsRawValueKind.Double => value.GetType() == typeof(double),
            EtabsRawValueKind.StringArray => HasExactArray<string>(value, allowNullStringElements),
            EtabsRawValueKind.BooleanArray => HasExactArray<bool>(value),
            EtabsRawValueKind.Int32Array => HasExactArray<int>(value),
            EtabsRawValueKind.DoubleArray => HasExactArray<double>(value),
            _ => false
        };
    }

    private static bool HasExactArray<T>(object value, bool allowNullElements = false)
    {
        if (value is not Array array)
            return false;
        return array.Cast<object?>().All(item =>
            item?.GetType() == typeof(T) || (allowNullElements && item is null));
    }

    private static bool IsArrayKind(EtabsRawValueKind kind) => kind is
        EtabsRawValueKind.StringArray or
        EtabsRawValueKind.BooleanArray or
        EtabsRawValueKind.Int32Array or
        EtabsRawValueKind.DoubleArray;
}
