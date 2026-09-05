using System.Security.Cryptography;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

if (args.Length != 4 || args[0] != "--request" || args[2] != "--response")
    return 2;

var requestPath = Path.GetFullPath(args[1]);
var responsePath = Path.GetFullPath(args[3]);
if (File.Exists(responsePath))
    return 3;

EtabsContextWorkerRequest request;
string requestSha;
try
{
    var requestBytes = await File.ReadAllBytesAsync(requestPath);
    request = EtabsContextWorkerCodec.ParseRequest(requestBytes);
    requestSha = EtabsContextWorkerCodec.RequestSha256(request);
}
catch (Exception exception)
{
    await WriteResponse(responsePath, new("unknown", string.Empty, EtabsContextWorkerState.Rejected, "ETABS.REQUEST_INVALID", $"{exception.GetType().Name}: {exception.Message}", null, null, true, true));
    return 1;
}

using var cancellation = new CancellationTokenSource();
var sentinel = requestPath + ".cancel";
using var watcher = new Timer(_ => { if (File.Exists(sentinel)) cancellation.Cancel(); }, null, TimeSpan.Zero, TimeSpan.FromMilliseconds(100));
EtabsContextBrokerResult result;
try
{
    var brokerRequest = new EtabsBrokerRequest(request.RequestId, request.Target.ProcessId, request.DeadlineUtc, request.EvidencePath);
    var handle = new EtabsContextOperationBroker().Start(brokerRequest,
        () => EtabsReflectionGetterHost.AttachContext(EtabsHostDiscovery.Discover(request.Target)),
        (host, token) => EtabsContextCapture.Run(host, new EtabsContextCaptureRequest(requestSha, request.DeadlineUtc), token), cancellation.Token);
    result = await handle.Completion;
    if (result.State != EtabsContextWorkerState.Completed)
        await WriteResponse(responsePath + ".terminal", new EtabsContextWorkerResponse(request.RequestId, requestSha, result.State,
            result.DiagnosticCode, result.Message, null, null, result.CleanupCompleted, false));
    await handle.Quiescence;
}
catch (Exception exception)
{
    result = new(EtabsContextWorkerState.Fenced, "ETABS.WORKER_FAILED", $"{exception.GetType().Name}: {exception.Message}", request.EvidencePath, true, null);
}

var response = result.State == EtabsContextWorkerState.Completed && result.Artifact is not null
    ? new EtabsContextWorkerResponse(request.RequestId, requestSha, result.State, null, null, result.EvidencePath, result.Artifact.ArtifactSha256, result.CleanupCompleted, true)
    : new EtabsContextWorkerResponse(request.RequestId, requestSha, result.State, result.DiagnosticCode, result.Message, null, null, result.CleanupCompleted, true);
await WriteResponse(responsePath, response);
return result.State == EtabsContextWorkerState.Completed ? 0 : 1;

static async Task WriteResponse(string path, EtabsContextWorkerResponse response)
{
    Directory.CreateDirectory(Path.GetDirectoryName(path) ?? throw new InvalidOperationException("The response path has no parent directory."));
    var bytes = EtabsContextWorkerCodec.CanonicalResponseJsonBytes(response);
    var temporary = path + $".{Guid.NewGuid():N}.tmp";
    try
    {
        await using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
        {
            await stream.WriteAsync(bytes);
            await stream.FlushAsync();
        }
        File.Move(temporary, path);
    }
    finally
    {
        if (File.Exists(temporary)) File.Delete(temporary);
    }
}
