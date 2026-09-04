using System.Collections.Concurrent;

namespace StructuralEngineering.ExcelDna;

/// <summary>
/// Runtime proof boundary for PF8 E5-01. Host adapters record here; pure worksheet
/// functions do not reference this type or any Excel object-model API.
/// </summary>
public static class HostEffectLedger
{
    private static readonly ConcurrentDictionary<string, int> Counts = new(StringComparer.Ordinal);
    private static int _capturing;

    public static void ResetAndStart()
    {
        Counts.Clear();
        Volatile.Write(ref _capturing, 1);
    }

    public static HostEffectSnapshot StopAndCapture()
    {
        Volatile.Write(ref _capturing, 0);
        var counts = Counts.OrderBy(pair => pair.Key, StringComparer.Ordinal)
            .ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
        return new(counts.Values.Sum(), counts);
    }

    internal static void Record(string effect)
    {
        if (Volatile.Read(ref _capturing) == 1)
            Counts.AddOrUpdate(effect, 1, (_, count) => checked(count + 1));
    }
}

public sealed record HostEffectSnapshot(
    int TotalCalls,
    IReadOnlyDictionary<string, int> Calls);
