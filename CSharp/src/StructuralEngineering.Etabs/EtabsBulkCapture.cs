using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public static partial class EtabsLiveGetterProbe
{
    /// <summary>Shared full-precision assignment export, exact source geometry and one real force getter per beam.</summary>
    public static EtabsBatchCapture RunBulk(IEtabsGetterHost host, EtabsBatchCaptureRequest request,
        CancellationToken cancellationToken = default, Action<int, int>? progress = null)
        => RunBulkCore(host, request, false, cancellationToken, progress);

    public static EtabsBatchCapture RunGroup(IEtabsGetterHost host, EtabsBatchCaptureRequest request,
        CancellationToken cancellationToken = default, Action<int, int>? progress = null)
        => RunBulkCore(host, request, true, cancellationToken, progress);

    private static EtabsBatchCapture RunBulkCore(IEtabsGetterHost host, EtabsBatchCaptureRequest request, bool group,
        CancellationToken cancellationToken, Action<int, int>? progress)
    {
        if (request.MemberObjectNames.Count is < 1 or > 1000 || request.MemberObjectNames.Distinct(StringComparer.Ordinal).Count() != request.MemberObjectNames.Count ||
            string.IsNullOrWhiteSpace(request.RequestSha256)) throw new ArgumentException("A bulk capture requires 1-1000 unique bound beam identities.");
        var identity = host.InspectIdentity();
        var source = request.Context.Source;
        if (source.ProcessId != identity.ProcessId || source.ProcessStartedUtc != identity.ProcessStartedUtc || source.ExecutableSha256 != identity.ExecutableSha256 ||
            source.ModelPath != identity.ModelPath || source.ModelSha256 != identity.ModelSha256 || source.ModelBytes != identity.ModelBytes ||
            source.ModelModifiedUtc != identity.ModelModifiedUtc || source.EtabsApiVersion != identity.EtabsApiVersion || source.PresentUnits != identity.PresentUnits)
            throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: reconnect before reading forces.");
        var started = DateTimeOffset.UtcNow;
        var adapter = new EtabsGetterAdapter(host, group ? EtabsGroupGetterMatrix.Allowed : EtabsBulkGetterMatrix.Allowed);
        var calls = new List<EtabsRawGetterCall>();
        var seed = new EtabsLiveGetterProbeRequest(request.MemberObjectNames[0], "", "", [], [], 4, 0, request.DeadlineUtc);
        var preflight = CaptureProtectedState(adapter, host, seed, calls, cancellationToken);
        seed = seed with { SelectedCases = preflight.CaseSelections.Where(item => item.Value).Select(item => item.Key).ToArray(),
            SelectedCombinations = preflight.CombinationSelections.Where(item => item.Value).Select(item => item.Key).ToArray() };
        ValidateReadiness(preflight, seed, allowMetricDatabase: true);
        if (seed.SelectedCases.Count + seed.SelectedCombinations.Count == 0) throw new EtabsLiveGetterProbeException("ETABS.SELECTION_EMPTY: select required static output sources in ETABS.");
        var frames = Read("FrameObj.GetAllFrames", ["Global"]);
        var points = Read("PointObj.GetAllPoints", ["Global"]);
        ValidateContext(request.Context, frames, points);
        Read("Story.GetStories_2", []);
        Read("FrameObj.GetNameList", []);
        ReadCatalogue(adapter, seed, calls, preflight, cancellationToken);
        ValidateSelectedStaticSources(seed, calls);
        var tables = new Dictionary<string, EtabsBulkTable>(StringComparer.Ordinal);
        var retainedTables = new List<(EtabsRawGetterCall Metadata, EtabsRawGetterCall Data)>();
        foreach (var spec in EtabsBulkTable.Specifications)
        {
            var metadata = Read("DatabaseTables.GetAllFieldsInTable", [spec.Key]);
            var data = ReadTable(spec, metadata);
            tables.Add(spec.Key, new(spec, JsonSerializer.SerializeToElement(metadata.Outputs), JsonSerializer.SerializeToElement(data.Outputs)));
            retainedTables.Add((metadata, data));
        }
        var sourceBeams = request.Context.Frames.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam).ToDictionary(frame => frame.SourceFrameId, StringComparer.Ordinal);
        if (!tables["Beam Object Connectivity"].Rows.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(sourceBeams.Keys))
            throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: source beam classification changed.");
        var materials = new Dictionary<string, string>(StringComparer.Ordinal);
        var seenMaterials = new HashSet<string>(StringComparer.Ordinal);
        var members = new List<EtabsMemberCaptureSummary>(); var totalRows = 0;
        EtabsRawGetterCall? groupForces = null;
        Dictionary<string, int[]>? groupRows = null;
        if (group)
        {
            if (!Strings(Read("GroupDef.GetNameList", []), 1).Contains("All", StringComparer.Ordinal))
                throw new EtabsLiveGetterProbeException("ETABS.GROUP_UNRESOLVED: the source All group is absent.");
            var assignments = Read("GroupDef.GetAssignments", ["All"]);
            var types = Integers(assignments, 1); var names = Strings(assignments, 2);
            var frameNames = names.Where((_, index) => types[index] == 2).ToArray();
            var contextFrameNames = request.Context.Frames.Select(frame => frame.SourceFrameId).ToHashSet(StringComparer.Ordinal);
            // ETABS 23's built-in All group has no explicit assignment rows. Its
            // implicit whole-source scope is qualified against the complete frame inventory.
            if (Scalar<int>(assignments, 0) != 0 && (frameNames.Distinct(StringComparer.Ordinal).Count() != frameNames.Length ||
                !frameNames.ToHashSet(StringComparer.Ordinal).SetEquals(contextFrameNames)))
                throw new EtabsLiveGetterProbeException("ETABS.GROUP_UNRESOLVED: source group frame assignments differ from the complete context.");
            groupForces = Read("Results.FrameForce", ["All", 2]);
            var owners = Strings(groupForces, 1);
            var knownFrames = contextFrameNames;
            if (Scalar<int>(groupForces, 0) is < 1 or > 100_000 || owners.Any(name => !knownFrames.Contains(name)))
                throw new EtabsLiveGetterProbeException("ETABS.SCOPE_LIMIT: the complete group result exceeds 100,000 rows or has an unknown source frame.");
            groupRows = owners.Select((name, index) => (name, index)).GroupBy(item => item.name, StringComparer.Ordinal)
                .ToDictionary(items => items.Key, items => items.Select(item => item.index).ToArray(), StringComparer.Ordinal);
        }
        foreach (var name in request.MemberObjectNames.Order(StringComparer.Ordinal))
        {
            if (!sourceBeams.TryGetValue(name, out var frame)) throw new EtabsLiveGetterProbeException("ETABS.SCOPE_UNSUPPORTED: requested object is not a captured beam.");
            var beam = tables["Beam Object Connectivity"].Required(name);
            if (beam.Optional("CurveType") is not null) throw new EtabsLiveGetterProbeException("ETABS.CURVED_MEMBER_UNSUPPORTED: curved members require a separately qualified basis.");
            if (beam.Required("Story") != frame.SourceStoryId || beam.Required("UniquePtI") != frame.SourcePoint1Id || beam.Required("UniquePtJ") != frame.SourcePoint2Id)
                throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: beam connectivity changed.");
            var section = tables["Frame Assignments - Section Properties"].Required(name).Required("SectProp");
            if (section != frame.SourceSectionId) throw new EtabsLiveGetterProbeException("ETABS.CONTEXT_STALE: section assignment changed.");
            if (!materials.ContainsKey(section))
            {
                var material = Scalar<string>(Read("PropFrame.GetMaterial", [section]), 0);
                var rectangle = Read("PropFrame.GetRectangle", [section]);
                RequireEqual("section material", material, Scalar<string>(rectangle, 1));
                Read("PropFrame.GetSectProps", [section]); Read("PropFrame.GetModifiers", [section]);
                if (seenMaterials.Add(material))
                {
                    Read("PropMaterial.GetMPIsotropic", [material, 0d]); Read("PropMaterial.GetWeightAndMass", [material, 0d]);
                    Read("PropMaterial.GetTypeOAPI", [material]);
                }
                materials.Add(section, material);
            }
            Read("FrameObj.GetTransformationMatrix", [name, true]);
            var forces = groupForces ?? Read("Results.FrameForce", [name, 0]);
            var indices = groupRows is null ? Enumerable.Range(0, Scalar<int>(forces, 0)).ToArray()
                : groupRows.TryGetValue(name, out var found) ? found : [];
            var count = indices.Length;
            var resultOwners = (object?[])forces.Outputs[1]!; var resultCases = (object?[])forces.Outputs[5]!;
            if (count <= 0 || indices.Any(index => (string)resultOwners[index]! != name) ||
                !indices.Select(index => (string)resultCases[index]!).ToHashSet(StringComparer.Ordinal).SetEquals(seed.SelectedCases.Concat(seed.SelectedCombinations)))
                throw new EtabsLiveGetterProbeException("ETABS.ROW_ACCOUNTING: incomplete or mismatched same-object result scope.");
            totalRows = checked(totalRows + count);
            if (totalRows > 100_000) throw new EtabsLiveGetterProbeException("ETABS.SCOPE_LIMIT: complete results exceed 100,000 rows.");
            members.Add(new(name, beam.Required("BeamBay"), frame.SourceStoryId, [frame.SourcePoint1Id, frame.SourcePoint2Id],
                indices.Select(index => (string)((object?[])forces.Outputs[3]!)[index]!).Distinct(StringComparer.Ordinal).ToArray(), section, materials[section], count));
            progress?.Invoke(members.Count, request.MemberObjectNames.Count);
        }
        // Tables may be affected by source assignments without changing the saved file hash.
        foreach (var pair in retainedTables)
        {
            var spec = EtabsBulkTable.Specifications.Single(item => item.Key == (string)pair.Metadata.Inputs[0]!);
            var after = ReadTable(spec, pair.Metadata);
            RequireEqual("bulk source table", AnalysisSnapshotNormalizer.Digest(pair.Data.Outputs), AnalysisSnapshotNormalizer.Digest(after.Outputs));
        }
        RequireEqual("source geometry", AnalysisSnapshotNormalizer.Digest(frames.Outputs), AnalysisSnapshotNormalizer.Digest(Read("FrameObj.GetAllFrames", ["Global"]).Outputs));
        RequireEqual("source points", AnalysisSnapshotNormalizer.Digest(points.Outputs), AnalysisSnapshotNormalizer.Digest(Read("PointObj.GetAllPoints", ["Global"]).Outputs));
        var postflight = CaptureProtectedState(adapter, host, seed, calls, cancellationToken);
        RequireEqual("protected state", preflight.Sha256, postflight.Sha256);
        RequireEqual("source identity", identity, host.InspectIdentity());
        return new(group ? EtabsGroupGetterMatrix.ProfileId : EtabsBulkGetterMatrix.ProfileId, request.RequestSha256,
            group ? EtabsGroupGetterMatrix.Sha256 : EtabsBulkGetterMatrix.Sha256, started, DateTimeOffset.UtcNow,
            identity, request.Context, preflight, postflight, members, calls);

        EtabsRawGetterCall Read(string operation, object?[] inputs) => Call(adapter, seed, calls, operation, inputs, cancellationToken);
        EtabsRawGetterCall ReadTable(EtabsBulkTableSpec spec, EtabsRawGetterCall metadata) => spec.Editing
            ? Read("DatabaseTables.GetTableForEditingArray", [spec.Key, "All"])
            : Read("DatabaseTables.GetTableForDisplayArray", [spec.Key, Strings(metadata, 2), "All"]);
    }
}
