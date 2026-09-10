using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

internal static class InspectionWorker
{
    private sealed record Request(string SchemaVersion, string RequestId, EtabsProcessTarget Target,
        DateTimeOffset DeadlineUtc, string EvidencePath, bool IncludeSample);

    public static async Task<int> Run(string requestPath, string responsePath)
    {
        if (File.Exists(responsePath) || File.Exists(responsePath + ".terminal")) return 3;
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
        };
        try
        {
            var request = JsonSerializer.Deserialize<Request>(await File.ReadAllBytesAsync(requestPath), options)
                ?? throw new InvalidDataException("Inspection request is empty.");
            if (request.SchemaVersion != "structural.etabs_inspection_request/v1" || request.Target is null)
                throw new InvalidDataException("Inspection request schema or target is invalid.");
            using var cancellation = new CancellationTokenSource();
            using var watcher = new Timer(_ => { if (File.Exists(requestPath + ".cancel")) cancellation.Cancel(); }, null, TimeSpan.Zero, TimeSpan.FromMilliseconds(100));
            var handle = EtabsInspectionBroker.Start(new(request.RequestId, request.Target.ProcessId, request.DeadlineUtc, request.EvidencePath),
                () => EtabsReflectionGetterHost.AttachInspection(EtabsHostDiscovery.Discover(request.Target)), request.IncludeSample, cancellation.Token);
            var result = await handle.Completion;
            if (!handle.Quiescence.IsCompleted) await Write(responsePath + ".terminal", new { result, quiescent = false });
            await handle.Quiescence;
            await Write(responsePath, new { result, quiescent = true });
            Console.WriteLine($"Inspection {result.State}; quiescent=true; evidence={result.FileSha256 ?? "none"}");
            return result.State == "completed" ? 0 : 1;
        }
        catch (Exception exception)
        {
            await Write(responsePath, new { state = "rejected", diagnostic = exception.ToString() });
            return 1;
        }
    }

    private static async Task Write(string path, object value)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        await using var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
        await JsonSerializer.SerializeAsync(stream, value);
    }
}
