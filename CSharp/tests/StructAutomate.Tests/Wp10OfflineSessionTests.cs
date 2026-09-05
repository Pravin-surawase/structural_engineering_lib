using System.Security.Cryptography;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using StructuralEngineering.ExcelDna;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10OfflineSessionTests
{
    [Fact]
    public void ImportReopensExactPortableIdentityAndRawProvenance()
    {
        using var files = new TemporaryFiles();
        var snapshot = SyntheticSnapshot();
        var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
        var source = files.Write("input/snapshot.json", bytes);
        var store = new OfflineSnapshotStore(files.Path("store"));

        var reference = store.Import(source, Sha(bytes));
        var reopened = new OfflineSnapshotStore(store.RootDirectory).Read(reference);

        Assert.Equal("synthetic-project", reference.ProjectId);
        Assert.Equal(Sha(bytes), reference.FileSha256);
        Assert.Equal(bytes.Length, reference.ByteCount);
        Assert.Equal(snapshot.SnapshotId, reference.SnapshotId);
        Assert.Equal(snapshot.SnapshotSha256, reference.SnapshotSha256);
        Assert.Equal(bytes, File.ReadAllBytes(store.GetArtifactPath(reference)));
        Assert.Equal(AnalysisSnapshotCodec.CanonicalJson(snapshot), AnalysisSnapshotCodec.CanonicalJson(reopened));
        Assert.Equal(snapshot.RawCapture.RawCaptureId, reopened.RawCapture.RawCaptureId);
        Assert.Equal(snapshot.RawCapture.RawCaptureSha256, reopened.RawCapture.RawCaptureSha256);
    }

    [Fact]
    public void ImportRejectsBadHashAndIncompletePayloadBeforeStorage()
    {
        using var files = new TemporaryFiles();
        var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(SyntheticSnapshot());
        var source = files.Write("input/snapshot.json", bytes);
        var storeRoot = files.Path("store");
        var store = new OfflineSnapshotStore(storeRoot);

        Assert.Throws<InvalidDataException>(() => store.Import(source, new string('0', 64)));
        Assert.False(Directory.Exists(storeRoot));

        var incomplete = files.Write("input/incomplete.json", "{}"u8.ToArray());
        Assert.Throws<InvalidDataException>(() => store.Import(incomplete));
        Assert.False(Directory.Exists(storeRoot));
    }

    [Fact]
    public void ReadRejectsWrongProjectAndCorruptedStoredArtifact()
    {
        using var files = new TemporaryFiles();
        var snapshot = SyntheticSnapshot();
        var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
        var source = files.Write("input/snapshot.json", bytes);
        var store = new OfflineSnapshotStore(files.Path("store"));
        var reference = store.Import(source);

        var wrongProject = reference with { ProjectId = "another-project" };
        var wrongProjectPath = store.GetArtifactPath(wrongProject);
        Directory.CreateDirectory(Path.GetDirectoryName(wrongProjectPath)!);
        File.WriteAllBytes(wrongProjectPath, bytes);
        Assert.Throws<InvalidDataException>(() => store.Read(wrongProject));

        File.WriteAllBytes(store.GetArtifactPath(reference), "corrupt"u8.ToArray());
        Assert.Throws<InvalidDataException>(() => store.Read(reference));
    }

    [Fact]
    public void ImportDeduplicatesExactBytesAndNeverOverwritesExistingArtifact()
    {
        using var files = new TemporaryFiles();
        var snapshot = SyntheticSnapshot();
        var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
        var source = files.Write("input/snapshot.json", bytes);
        var store = new OfflineSnapshotStore(files.Path("store"));

        var first = store.Import(source);
        var second = store.Import(source);
        Assert.Equal(first, second);
        Assert.Equal(bytes, File.ReadAllBytes(store.GetArtifactPath(first)));

        var occupied = new OfflineSnapshotStore(files.Path("occupied"));
        var expected = new OfflineSnapshotReference(snapshot.Metadata.ProjectId, Sha(bytes), snapshot.SnapshotId,
            snapshot.SnapshotSha256, bytes.Length);
        var occupiedPath = occupied.GetArtifactPath(expected);
        Directory.CreateDirectory(Path.GetDirectoryName(occupiedPath)!);
        File.WriteAllBytes(occupiedPath, "preexisting-corruption"u8.ToArray());

        Assert.Throws<InvalidDataException>(() => occupied.Import(source));
        Assert.Equal("preexisting-corruption"u8.ToArray(), File.ReadAllBytes(occupiedPath));
    }

    [Fact]
    public void SessionIndexesKnownMembersOnceWithoutStorageIo()
    {
        using var files = new TemporaryFiles();
        var snapshot = SyntheticSnapshot();
        var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
        var source = files.Write("input/snapshot.json", bytes);
        var store = new OfflineSnapshotStore(files.Path("store"));
        var reference = store.Import(source);
        var session = new OfflineSnapshotSession(reference, store.Read(reference));
        var member = Assert.Single(session.Snapshot.Members);

        Directory.Delete(store.RootDirectory, recursive: true);

        var rows = session.ActionsForMember(member.MemberId);
        Assert.Equal(session.Snapshot.ActionRows, rows);
        Assert.Same(rows, session.ActionsForMember(member.MemberId));
        Assert.Throws<KeyNotFoundException>(() => session.ActionsForMember("unknown-member"));
    }

    private static AnalysisSnapshot SyntheticSnapshot()
    {
        var raw = Wp10SyntheticCapture.Create();
        var rawBytes = EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(raw);
        var result = EtabsCaptureProjector.Normalize(rawBytes, Sha(rawBytes), Wp10SyntheticCapture.Options);
        Assert.True(result.OperationState == SnapshotOperationState.Completed,
            string.Join(" | ", result.Diagnostics.Select(item => $"{item.Code}: {item.Message}")));
        return Assert.IsType<AnalysisSnapshot>(result.Snapshot);
    }

    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));

    private sealed class TemporaryFiles : IDisposable
    {
        private readonly string _root = System.IO.Path.Combine(System.IO.Path.GetTempPath(), $"structautomate-wp10-{Guid.NewGuid():N}");

        public string Path(string relative) => System.IO.Path.Combine(_root, relative);

        public string Write(string relative, byte[] bytes)
        {
            var path = Path(relative);
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, bytes);
            return path;
        }

        public void Dispose()
        {
            if (Directory.Exists(_root)) Directory.Delete(_root, recursive: true);
        }
    }
}
