using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsSourceArtifact(string SchemaVersion, string GetterMatrixSha256,
    EtabsHostIdentity Source, EtabsSourceCapture Capture, SnapshotCallLedger Ledger, EtabsCleanupEvidence Cleanup);

public static class EtabsSourceBroker
{
    public const string ArtifactSchema = "structural.etabs_source_qualification/v1";

    public static EtabsInspectionHandle Start(EtabsBrokerRequest request, EtabsSourceScope scope,
        Func<IEtabsGetterHost> hostFactory, CancellationToken cancellationToken = default)
    {
        EtabsSourceQualification.ValidateScope(scope);
        return EtabsInspectionBroker.StartCore(request, hostFactory, EtabsSourceGetterMatrix.Sha256,
            (host, token) => EtabsSourceReader.Read(host, scope, request.DeadlineUtc, token),
            (capture, source, ledger, cleanup) => new EtabsSourceArtifact(ArtifactSchema,
                EtabsSourceGetterMatrix.Sha256, source, capture, ledger, cleanup), cancellationToken);
    }
}
