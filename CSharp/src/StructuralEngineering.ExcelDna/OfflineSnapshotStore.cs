using System.Security.Cryptography;
using System.Text;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>
/// A compact, workbook-storable pointer to an immutable portable analysis snapshot.
/// The referenced bytes remain outside the workbook and are addressed by their SHA-256.
/// </summary>
public sealed record OfflineSnapshotReference(
    string ProjectId,
    string FileSha256,
    string SnapshotId,
    string SnapshotSha256,
    int ByteCount);

/// <summary>
/// Host-free, content-addressed storage for complete portable analysis snapshots.
/// </summary>
public sealed class OfflineSnapshotStore
{
    public const int MaximumInputBytes = 16 * 1024 * 1024;
    public const int MaximumActionRows = 10_000;
    public const int MaximumMembers = 1_000;

    private static readonly UTF8Encoding StrictUtf8 = new(false, true);

    public OfflineSnapshotStore(string rootDirectory)
    {
        if (string.IsNullOrWhiteSpace(rootDirectory))
            throw new ArgumentException("An offline snapshot root directory is required.", nameof(rootDirectory));
        RootDirectory = Path.GetFullPath(rootDirectory);
    }

    public string RootDirectory { get; }

    /// <summary>Validates all source bytes before atomically admitting one immutable artifact.</summary>
    public OfflineSnapshotReference Import(string sourcePath, string? expectedSha256 = null)
    {
        var bytes = ReadBoundedFile(sourcePath);
        var fileSha256 = Sha256(bytes);
        if (expectedSha256 is not null)
        {
            ValidateSha256(expectedSha256, nameof(expectedSha256));
            if (!string.Equals(fileSha256, expectedSha256, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("The supplied snapshot file digest does not match its exact bytes.");
        }

        var snapshot = ParseAccepted(bytes);
        EnforceAdmissionLimits(snapshot);
        var reference = new OfflineSnapshotReference(
            snapshot.Metadata.ProjectId,
            fileSha256,
            snapshot.SnapshotId,
            snapshot.SnapshotSha256,
            bytes.Length);
        ValidateReference(reference);

        var target = GetArtifactPath(reference);
        if (File.Exists(target))
        {
            VerifyExisting(target, reference, bytes);
            return reference;
        }

        Directory.CreateDirectory(Path.GetDirectoryName(target)!);
        var temporary = Path.Combine(Path.GetDirectoryName(target)!, $".{fileSha256}.{Guid.NewGuid():N}.tmp");
        try
        {
            using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                stream.Write(bytes);
                stream.Flush(flushToDisk: true);
            }

            try
            {
                File.Move(temporary, target, overwrite: false);
            }
            catch (IOException) when (File.Exists(target))
            {
                // A concurrent importer won the create-new race. It must be the same valid artifact.
            }

            VerifyExisting(target, reference, bytes);
            return reference;
        }
        finally
        {
            if (File.Exists(temporary)) File.Delete(temporary);
        }
    }

    /// <summary>Reopens the exact referenced bytes and revalidates their snapshot contract.</summary>
    public AnalysisSnapshot Read(OfflineSnapshotReference reference)
    {
        ValidateReference(reference);
        var bytes = ReadStoredBytes(GetArtifactPath(reference), reference);
        return ParseVerified(reference, bytes);
    }

    public string GetArtifactPath(OfflineSnapshotReference reference)
    {
        ValidateReference(reference);
        return Path.Combine(RootDirectory, Sha256(StrictUtf8.GetBytes(reference.ProjectId)), $"{reference.FileSha256}.json");
    }

    private static byte[] ReadBoundedFile(string sourcePath)
    {
        if (string.IsNullOrWhiteSpace(sourcePath))
            throw new ArgumentException("A snapshot source path is required.", nameof(sourcePath));
        var fullPath = Path.GetFullPath(sourcePath);
        using var stream = new FileStream(fullPath, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length > MaximumInputBytes)
            throw new InvalidDataException($"Offline snapshots may not exceed {MaximumInputBytes} bytes.");

        var bytes = new byte[checked((int)stream.Length)];
        var offset = 0;
        while (offset < bytes.Length)
        {
            var read = stream.Read(bytes, offset, bytes.Length - offset);
            if (read == 0) throw new InvalidDataException("The snapshot source changed while it was being read.");
            offset += read;
        }
        return bytes;
    }

    private static byte[] ReadStoredBytes(string path, OfflineSnapshotReference reference)
    {
        var bytes = ReadBoundedFile(path);
        if (bytes.Length != reference.ByteCount || !string.Equals(Sha256(bytes), reference.FileSha256, StringComparison.Ordinal))
            throw new InvalidDataException("The stored offline snapshot no longer matches its workbook reference.");
        return bytes;
    }

    private static void VerifyExisting(string path, OfflineSnapshotReference reference, byte[] expectedBytes)
    {
        var bytes = ReadStoredBytes(path, reference);
        if (!bytes.AsSpan().SequenceEqual(expectedBytes))
            throw new InvalidDataException("A different artifact already occupies the requested content-addressed path.");
        _ = ParseVerified(reference, bytes);
    }

    private static AnalysisSnapshot ParseVerified(OfflineSnapshotReference reference, byte[] bytes)
    {
        var snapshot = ParseAccepted(bytes);
        EnforceAdmissionLimits(snapshot);
        if (!string.Equals(snapshot.Metadata.ProjectId, reference.ProjectId, StringComparison.Ordinal) ||
            !string.Equals(snapshot.SnapshotId, reference.SnapshotId, StringComparison.Ordinal) ||
            !string.Equals(snapshot.SnapshotSha256, reference.SnapshotSha256, StringComparison.Ordinal))
            throw new InvalidDataException("The offline snapshot content does not match its project or snapshot reference.");
        return snapshot;
    }

    private static AnalysisSnapshot ParseAccepted(byte[] bytes)
    {
        string json;
        try { json = StrictUtf8.GetString(bytes); }
        catch (DecoderFallbackException exception)
        {
            throw new InvalidDataException("Offline snapshot bytes must be strict UTF-8.", exception);
        }

        var result = AnalysisSnapshotCodec.ParseAndValidate(json);
        if (result.Snapshot is not AnalysisSnapshot snapshot)
        {
            var detail = string.Join(" | ", result.Diagnostics.Select(item => $"{item.Code}: {item.Message}"));
            throw new InvalidDataException($"The offline snapshot is not accepted by the portable snapshot contract. {detail}");
        }
        return snapshot;
    }

    private static void EnforceAdmissionLimits(AnalysisSnapshot snapshot)
    {
        if (snapshot.ActionRows.Count > MaximumActionRows)
            throw new InvalidDataException($"Offline snapshots may not contain more than {MaximumActionRows} action rows.");
        if (snapshot.Members.Count > MaximumMembers)
            throw new InvalidDataException($"Offline snapshots may not contain more than {MaximumMembers} members.");
    }

    internal static void ValidateReference(OfflineSnapshotReference reference)
    {
        ArgumentNullException.ThrowIfNull(reference);
        if (string.IsNullOrWhiteSpace(reference.ProjectId) || string.IsNullOrWhiteSpace(reference.SnapshotId) ||
            reference.ByteCount < 1)
            throw new ArgumentException("An offline snapshot reference requires project, snapshot, and positive byte-count identities.", nameof(reference));
        ValidateSha256(reference.FileSha256, nameof(reference.FileSha256));
        ValidateSha256(reference.SnapshotSha256, nameof(reference.SnapshotSha256));
    }

    private static void ValidateSha256(string value, string parameterName)
    {
        if (value.Length != 64 || value.Any(character => !Uri.IsHexDigit(character)))
            throw new ArgumentException("A SHA-256 identity must be 64 hexadecimal characters.", parameterName);
    }

    private static string Sha256(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
}
