using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed record EtabsOverviewResult(EtabsContextWorkerResponse Response, EtabsOverviewArtifact? Artifact, string OperationDirectory);

public static partial class EtabsConnectionClient
{
    public static async Task<EtabsOverviewResult> InspectAsync(string packageDirectory, string operationsRoot,
        EtabsProcessChoice choice, string requestId, CancellationToken cancellationToken)
    {
        var result = await ReadAsync(packageDirectory, operationsRoot, choice, requestId, cancellationToken,
            new ReaderProfile<EtabsOverviewArtifact>("--overview-request", "overview.json", EtabsOverviewWorkerCodec.CanonicalRequestJsonBytes,
                EtabsOverviewWorkerCodec.RequestSha256, (bytes, id, sha) => EtabsOverviewWorkerCodec.ParseAndValidateResponse(bytes, id, sha),
                (bytes, target, sha) => EtabsOverviewWorkerCodec.ParseAndValidateArtifact(bytes, target, sha),
                artifact => artifact.ArtifactSha256, ValidateOverviewEvidence)).ConfigureAwait(false);
        return new(result.Response, result.Artifact, result.OperationDirectory);
    }

    public static void ValidateOverviewEvidence(EtabsOverviewArtifact artifact, string directory)
    {
        var proof = artifact.Overview.Provenance;
        foreach (var (name, hash) in new[] { (proof.InspectionFileName, proof.InspectionSha256), (proof.JournalFileName, proof.JournalSha256) })
        {
            var path = Path.Combine(directory, name);
            if (!File.Exists(path) || new FileInfo(path).Length > 16L * 1024 * 1024 || Sha256File(path) != hash)
                throw new InvalidDataException("The retained overview evidence is missing or has changed.");
        }
    }
}
