using System.Collections.Concurrent;

namespace StructuralEngineering.Etabs;

/// <summary>Exclusive read-operation lease shared by in-process brokers and separately launched workers.</summary>
internal static class EtabsProcessLease
{
    private static readonly ConcurrentDictionary<int, SemaphoreSlim> InProcess = new();

    public static bool TryAcquire(int processId, out IDisposable? lease)
    {
        lease = null;
        var local = InProcess.GetOrAdd(processId, static _ => new SemaphoreSlim(1, 1));
        if (!local.Wait(0))
            return false;

        FileStream? crossProcess = null;
        try
        {
            var path = Path.Combine(Path.GetTempPath(), $"StructAutomate.Etabs.Process.{processId}.lease");
            crossProcess = new FileStream(path, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None, 1, FileOptions.WriteThrough);
            lease = new Lease(local, crossProcess);
            return true;
        }
        catch (IOException)
        {
            crossProcess?.Dispose();
            local.Release();
            return false;
        }
        catch
        {
            crossProcess?.Dispose();
            local.Release();
            throw;
        }
    }

    private sealed class Lease(SemaphoreSlim local, FileStream crossProcess) : IDisposable
    {
        private int _disposed;

        public void Dispose()
        {
            if (Interlocked.Exchange(ref _disposed, 1) != 0)
                return;
            try { crossProcess.Dispose(); }
            finally { local.Release(); }
        }
    }
}
