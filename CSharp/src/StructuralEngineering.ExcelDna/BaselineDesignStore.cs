using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.ExcelDna;

public sealed record BaselineRequestReference(string FileName, string FileSha256, string RequestId, string SnapshotId, string SnapshotSha256, string EngineRevisionId);
public sealed record BaselineResultReference(string FileName, string FileSha256, string RequestId, string SnapshotId, string RequestFileSha256);
public sealed class BaselineDesignStore(string directory)
{
    private readonly string _root = Path.GetFullPath(directory);
    public BaselineRequestReference SaveRequest(BaselineReplayRequest request)
    {
        var bytes = BaselineReplay.Serialize(request); var hash = Hash(bytes); var id = ResultFactory.SemanticId("baseline_request", new { request.SnapshotSha256, inputs = request.AcceptedInputs, memberIds = request.MemberIds, options = request.Options, EngineIdentity = request.EngineRevisionId }); var file = Write("request-" + hash + ".json", bytes);
        return new(file, hash, id, request.SnapshotId, request.SnapshotSha256, request.EngineRevisionId);
    }
    public BaselineReplayRequest ReadRequest(BaselineRequestReference reference)
    { var bytes = Read(reference.FileName, reference.FileSha256); var request = BaselineReplay.Parse(bytes); if (RequestId(request) != reference.RequestId || request.SnapshotId != reference.SnapshotId || request.SnapshotSha256 != reference.SnapshotSha256 || request.EngineRevisionId != reference.EngineRevisionId) throw new InvalidDataException("Request reference binding mismatch."); return request; }
    public BaselineResultReference SaveResult(BaselineBatchDesignResult result, BaselineRequestReference request)
    { var persisted = ReadRequest(request); ValidateResult(result, persisted, request); var bytes = JsonSerializer.SerializeToUtf8Bytes(result, WorkbookContract.Json); var hash = Hash(bytes); return new(Write("result-" + hash + ".json", bytes), hash, result.RequestId, result.SnapshotId, request.FileSha256); }
    public BaselineBatchDesignResult ReadResult(BaselineResultReference reference)
    { var result = JsonSerializer.Deserialize<BaselineBatchDesignResult>(Read(reference.FileName, reference.FileSha256), WorkbookContract.Json) ?? throw new InvalidDataException("Result missing."); var file = "request-" + reference.RequestFileSha256 + ".json"; var request = BaselineReplay.Parse(Read(file, reference.RequestFileSha256)); var requestReference = new BaselineRequestReference(file, reference.RequestFileSha256, RequestId(request), request.SnapshotId, request.SnapshotSha256, request.EngineRevisionId); if (result.RequestId != reference.RequestId || result.SnapshotId != reference.SnapshotId) throw new InvalidDataException("Result reference binding mismatch."); ValidateResult(result, request, requestReference); return result; }
    private static string RequestId(BaselineReplayRequest request) => ResultFactory.SemanticId("baseline_request", new { request.SnapshotSha256, inputs = request.AcceptedInputs, memberIds = request.MemberIds, options = request.Options, EngineIdentity = request.EngineRevisionId });
    private static void ValidateResult(BaselineBatchDesignResult result, BaselineReplayRequest request, BaselineRequestReference reference)
    { if (result.RequestId != reference.RequestId || result.SnapshotId != request.SnapshotId || !Same(result.AcceptedInputs, request.AcceptedInputs) || !Same(result.Options, request.Options) || result.Members.Count != request.MemberIds.Count || !result.Members.Select(x => x.MemberId).SequenceEqual(request.MemberIds, StringComparer.Ordinal) || result.Members.Any(x => x.EngineRevisionId != request.EngineRevisionId)) throw new InvalidDataException("Result does not bind exactly to persisted request."); }
    private static bool Same<T>(T a, T b) where T : notnull => ResultFactory.CanonicalJsonBytes(a).AsSpan().SequenceEqual(ResultFactory.CanonicalJsonBytes(b));
    private string Write(string file, byte[] bytes) { Directory.CreateDirectory(_root); var path = Path.Combine(_root, file); if (File.Exists(path)) { if (!File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes)) throw new InvalidDataException("Content-addressed collision."); return file; } var tmp = path + "." + Guid.NewGuid().ToString("N") + ".tmp"; try { using (var s = new FileStream(tmp, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { s.Write(bytes); s.Flush(true); } try { File.Move(tmp, path, false); } catch (IOException) when (File.Exists(path)) { } if (!File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes)) throw new InvalidDataException("Stored artifact differs."); return file; } finally { if (File.Exists(tmp)) File.Delete(tmp); } }
    private byte[] Read(string file, string hash) { if (Path.GetFileName(file) != file) throw new ArgumentException("Artifact filename is invalid."); var p = Path.Combine(_root, file); if (!File.Exists(p)) throw new FileNotFoundException("Artifact missing.", p); var b = File.ReadAllBytes(p); if (Hash(b) != hash) throw new InvalidDataException("Artifact hash mismatch."); return b; }
    private static string Hash(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
}
