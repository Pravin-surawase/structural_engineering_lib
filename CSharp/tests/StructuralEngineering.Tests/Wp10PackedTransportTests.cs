using System.IO.Compression;
using System.Text;
using System.Text.Json.Nodes;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class Wp10PackedTransportTests
{
    [Fact]
    public void CompactRowsTransportPreservesCanonicalIdentityAndIsSmaller()
    {
        var snapshot = Accepted(AnalysisSnapshotCodec.ParseAndValidate(LoadSnapshot()));
        using var legacy = new MemoryStream(); AnalysisSnapshotTransport.Write(legacy, snapshot);
        using var compact = new MemoryStream(); AnalysisSnapshotTransport.WriteCompact(compact, snapshot);
        Assert.True(compact.ToArray().AsSpan().StartsWith("STRUCTSNAP-ROWS-1\n"u8));
        Assert.True(compact.Length < legacy.Length);
        compact.Position = 0;
        var replay = Accepted(AnalysisSnapshotTransport.Read(compact));
        Assert.Equal(AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot), AnalysisSnapshotCodec.CanonicalJsonBytes(replay));
    }

    [Fact]
    public void CompactRowsTransportRejectsTruncatedFooterExtraColumnAndWrongType()
    {
        var snapshot = Accepted(AnalysisSnapshotCodec.ParseAndValidate(LoadSnapshot()));
        using var compact = new MemoryStream(); AnalysisSnapshotTransport.WriteCompact(compact, snapshot);
        var bytes = compact.ToArray();
        Assert.Null(AnalysisSnapshotTransport.Read(new MemoryStream(bytes[..^4])).Snapshot);

        var root = JsonNode.Parse(Expand(bytes))!.AsObject();
        root["action_rows"]!.AsArray()[0]!.AsArray().Add("extra");
        Assert.Null(AnalysisSnapshotTransport.Read(Encode(root.ToJsonString())).Snapshot);

        root = JsonNode.Parse(Expand(bytes))!.AsObject();
        root["action_rows"]!.AsArray()[0]!.AsArray()[9] = "not-a-number"; // p_kn
        Assert.Null(AnalysisSnapshotTransport.Read(Encode(root.ToJsonString())).Snapshot);
    }

    private static string Expand(byte[] encoded)
    {
        using var input = new MemoryStream(encoded, "STRUCTSNAP-ROWS-1\n"u8.Length, encoded.Length - "STRUCTSNAP-ROWS-1\n"u8.Length);
        using var gzip = new GZipStream(input, CompressionMode.Decompress);
        using var reader = new StreamReader(gzip, Encoding.UTF8);
        return reader.ReadToEnd();
    }

    private static MemoryStream Encode(string json)
    {
        var output = new MemoryStream(); output.Write("STRUCTSNAP-ROWS-1\n"u8);
        using (var gzip = new GZipStream(output, CompressionLevel.Fastest, leaveOpen: true))
            gzip.Write(Encoding.UTF8.GetBytes(json));
        output.Position = 0; return output;
    }

    private static AnalysisSnapshot Accepted(EtabsSnapshotResult result) =>
        Assert.IsType<AnalysisSnapshot>(result.Snapshot);

    private static string LoadSnapshot()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null)
        {
            var path = Path.Combine(root.FullName, "contracts", "structural-engineering", "conformance", "wp10-vectors.json");
            if (File.Exists(path)) return JsonNode.Parse(File.ReadAllText(path))!["valid_snapshot"]!.ToJsonString();
            root = root.Parent;
        }
        throw new FileNotFoundException("WP10 conformance fixture was not found.");
    }
}
