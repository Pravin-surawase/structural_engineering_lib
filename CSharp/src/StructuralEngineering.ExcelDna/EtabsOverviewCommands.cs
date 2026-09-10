using ExcelDna.Integration;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public static partial class OfflineCommands
{
    [ExcelCommand(Name = "STR_XL_INSPECT_ETABS", Description = "Read model counts and analysis/design availability without geometry or forces.")]
    public static string InspectEtabs() => InspectEtabsProcess(0);

    [ExcelCommand(Name = "STR_XL_INSPECT_ETABS_PROCESS", Description = "Read a lightweight overview from the selected ETABS process.")]
    public static string InspectEtabsProcess(double processId) => StartConnection(processId, overview: true);

    [ExcelCommand(Name = "STR_XL_LOAD_ETABS_DETAILS", Description = "Load geometry for the current overview after checking its source identity.")]
    public static string LoadEtabsDetails() => StartConnection(0, overview: false, fromOverview: true);

    [ExcelCommand(Name = "STR_XL_TEST_OVERVIEW_SESSION_COUNT", Description = "Installed acceptance: count resident model overviews.")]
    public static double OverviewSessionCount() => Entries.Values.Count(entry => entry.Overview?.Artifact is not null);

    private static void CompleteOverview(long key, Entry expectedEntry, string requestId, EtabsOverviewResult? result, Exception? failure)
    {
        if (!Entries.TryGetValue(key, out var current) || !ReferenceEquals(current, expectedEntry) || current.ConnectionRequestId != requestId) return;
        Run((app, workbook, store, entry) =>
        {
            if (!ReferenceEquals(entry, expectedEntry) || entry.ConnectionRequestId != requestId)
                throw new InvalidOperationException("The initiating overview is no longer current.");
            entry.ConnectionRequestId = null;
            entry.ConnectionCancellation?.Dispose(); entry.ConnectionCancellation = null;
            entry.Window?.EndPendingConnection();
            if (failure is not null) return Result("rejected", "ETABS overview failed: " + failure.Message);
            if (result?.Artifact is null || result.Response.State != EtabsContextWorkerState.Completed)
                return Result("rejected", result?.Response.Message ?? "No completed model overview was returned.", result?.Response);
            entry.Overview = result; entry.Context = null; entry.ForceContextArtifactSha256 = null;
            entry.Window ??= new OfflineReviewWindow();
            entry.Window.SetOverview(result.Artifact, () => ExcelAsyncUtil.QueueAsMacro(() =>
            {
                if (Entries.TryGetValue(key, out var owner) && ReferenceEquals(owner, entry))
                    StartConnection(0, overview: false, fromOverview: true, workbookKey: key);
            }));
            return OverviewSummary(result);
        }, key);
    }

    private static string OverviewSummary(EtabsOverviewResult result) => Result("completed",
        "Model overview captured. Load model details to review frames or request forces. Engineering checks have not run.",
        new
        {
            overview_id = result.Artifact!.ArtifactSha256,
            overview = result.Artifact.Overview,
            operation_directory = result.OperationDirectory,
            geometry_loaded = false,
            forces_loaded = false,
            engineering = "not_evaluated"
        });
}
