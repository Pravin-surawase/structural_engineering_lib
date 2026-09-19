using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsTopologyArtifact(string SchemaVersion, string GetterMatrixSha256,
    EtabsHostIdentity Source, EtabsTopologyCapture Capture, SnapshotCallLedger Ledger, EtabsCleanupEvidence Cleanup);

public static class EtabsTopologyBroker
{
    public static EtabsInspectionHandle Start(EtabsBrokerRequest request, EtabsSourceScope scope,
        Func<IEtabsGetterHost> hostFactory, CancellationToken cancellationToken = default)
    {
        EtabsSourceQualification.ValidateScope(scope);
        return EtabsInspectionBroker.StartCore(request, hostFactory, EtabsTopologyGetterMatrix.Sha256,
            (host, token) => EtabsTopologyReader.Read(host, scope, request.DeadlineUtc, token),
            (capture, source, ledger, cleanup) => new EtabsTopologyArtifact("structural.etabs_topology/v1",
                EtabsTopologyGetterMatrix.Sha256, source, capture, ledger, cleanup), cancellationToken);
    }
}
