using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

internal static class SourceWorker
{
    private sealed record Request(string SchemaVersion, string RequestId, EtabsProcessTarget Target,
        string ExpectedModelSha256, DateTimeOffset DeadlineUtc, string EvidencePath, EtabsSourceScope Scope);

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
                ?? throw new InvalidDataException("Source request is empty.");
            if (request.SchemaVersion != "structural.etabs_source_request/v1" || request.Target is null ||
                request.ExpectedModelSha256 is null || request.ExpectedModelSha256.Length != 64 ||
                request.ExpectedModelSha256.Any(c => !char.IsAsciiHexDigit(c)))
                throw new InvalidDataException("Source request schema or target is invalid.");
            using var cancellation = new CancellationTokenSource();
            using var watcher = new Timer(_ => { if (File.Exists(requestPath + ".cancel")) cancellation.Cancel(); }, null, TimeSpan.Zero, TimeSpan.FromMilliseconds(100));
            var handle = EtabsSourceBroker.Start(new(request.RequestId, request.Target.ProcessId, request.DeadlineUtc, request.EvidencePath), request.Scope,
                () =>
                {
                    var expected = EtabsHostDiscovery.Discover(request.Target);
                    if (!string.Equals(expected.ModelSha256, request.ExpectedModelSha256, StringComparison.OrdinalIgnoreCase))
                        throw new InvalidDataException("The selected saved model differs from the request's exact source hash.");
                    return EtabsReflectionGetterHost.AttachSource(expected);
                }, cancellation.Token);
            var result = await handle.Completion;
            if (!handle.Quiescence.IsCompleted) await Write(responsePath + ".terminal", new { result, quiescent = false });
            await handle.Quiescence;
            await Write(responsePath, new { result, quiescent = true });
            Console.WriteLine($"Source qualification {result.State}; quiescent=true; evidence={result.FileSha256 ?? "none"}");
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
