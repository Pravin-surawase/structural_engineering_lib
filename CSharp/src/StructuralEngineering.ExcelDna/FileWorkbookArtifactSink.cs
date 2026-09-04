namespace StructuralEngineering.ExcelDna;

/// <summary>Stages beside the destination, commits atomically, and restores any preimage.</summary>
public sealed class FileWorkbookArtifactSink : IWorkbookArtifactSink
{
    private readonly string _directory;
    private readonly Dictionary<string, StagedArtifact> _staged = new(StringComparer.Ordinal);

    public string? LastCommittedPath { get; private set; }

    public FileWorkbookArtifactSink(string directory)
    {
        if (string.IsNullOrWhiteSpace(directory))
            throw new ArgumentException("An export directory is required.", nameof(directory));
        _directory = Path.GetFullPath(directory);
        Directory.CreateDirectory(_directory);
    }

    public void Stage(string artifactName, byte[] bytes)
    {
        ValidateName(artifactName);
        ArgumentNullException.ThrowIfNull(bytes);
        if (_staged.ContainsKey(artifactName))
            throw new InvalidOperationException($"Artifact {artifactName} is already staged.");
        HostEffectLedger.Record("file.artifact.stage");
        var target = Path.Combine(_directory, artifactName);
        var temporary = Path.Combine(_directory, $".{artifactName}.{Guid.NewGuid():N}.tmp");
        var backup = File.Exists(target) ? File.ReadAllBytes(target) : null;
        try
        {
            File.WriteAllBytes(temporary, bytes);
            _staged.Add(artifactName, new(target, temporary, backup));
        }
        catch
        {
            if (File.Exists(temporary)) File.Delete(temporary);
            throw;
        }
    }

    public void Commit(string artifactName)
    {
        var staged = Required(artifactName);
        HostEffectLedger.Record("file.artifact.commit");
        File.Move(staged.TemporaryPath, staged.TargetPath, true);
        _staged[artifactName] = staged with { Committed = true };
        LastCommittedPath = staged.TargetPath;
    }

    public void Rollback(string artifactName)
    {
        if (!_staged.Remove(artifactName, out var staged)) return;
        HostEffectLedger.Record("file.artifact.rollback");
        if (File.Exists(staged.TemporaryPath)) File.Delete(staged.TemporaryPath);
        if (!staged.Committed) return;
        if (staged.Preimage is null)
        {
            if (File.Exists(staged.TargetPath)) File.Delete(staged.TargetPath);
        }
        else File.WriteAllBytes(staged.TargetPath, staged.Preimage);
    }

    private StagedArtifact Required(string name) => _staged.TryGetValue(name, out var staged)
        ? staged
        : throw new InvalidOperationException($"Artifact {name} is not staged.");

    private static void ValidateName(string name)
    {
        if (string.IsNullOrWhiteSpace(name) || name != Path.GetFileName(name) ||
            name.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)
            throw new ArgumentException("Artifact name must be one safe file name.", nameof(name));
    }

    private sealed record StagedArtifact(
        string TargetPath,
        string TemporaryPath,
        byte[]? Preimage,
        bool Committed = false);
}
