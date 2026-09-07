using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public static partial class EtabsLiveGetterProbe
{
    /// <summary>Shared full-precision assignment export, exact source geometry and one real force getter per beam.</summary>
    public static EtabsBatchCapture RunBulk(IEtabsGetterHost host, EtabsBatchCaptureRequest request,
        CancellationToken cancellationToken = default, Action<int, int>? progress = null)
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
        var adapter = new EtabsGetterAdapter(host, EtabsBulkGetterMatrix.Allowed);
        var calls = new List<EtabsRawGetterCall>();
        var seed = new EtabsLiveGetterProbeRequest(request.MemberObjectNames[0], "", "", [], [], 4, 0, request.DeadlineUtc);
        var preflight = CaptureProtectedState(adapter, host, seed, calls, cancellationToken);
        seed = seed with { SelectedCases = preflight.CaseSelections.Where(item => item.Value).Select(item => item.Key).ToArray(),
            SelectedCombinations = preflight.CombinationSelections.Where(item => item.Value).Select(item => item.Key).ToArray() };
        ValidateReadiness(preflight, seed);
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
            var forces = Read("Results.FrameForce", [name, 0]);
            var count = Scalar<int>(forces, 0);
            if (count <= 0 || Strings(forces, 1).Any(owner => owner != name) ||
                !Strings(forces, 5).ToHashSet(StringComparer.Ordinal).SetEquals(seed.SelectedCases.Concat(seed.SelectedCombinations)))
                throw new EtabsLiveGetterProbeException("ETABS.ROW_ACCOUNTING: incomplete or mismatched same-object result scope.");
            totalRows = checked(totalRows + count);
            if (totalRows > 100_000) throw new EtabsLiveGetterProbeException("ETABS.SCOPE_LIMIT: complete results exceed 100,000 rows.");
            members.Add(new(name, beam.Required("BeamBay"), frame.SourceStoryId, [frame.SourcePoint1Id, frame.SourcePoint2Id],
                Strings(forces, 3).Distinct(StringComparer.Ordinal).ToArray(), section, materials[section], count));
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
        return new(EtabsBulkGetterMatrix.ProfileId, request.RequestSha256, EtabsBulkGetterMatrix.Sha256, started, DateTimeOffset.UtcNow,
            identity, request.Context, preflight, postflight, members, calls);

        EtabsRawGetterCall Read(string operation, object?[] inputs) => Call(adapter, seed, calls, operation, inputs, cancellationToken);
        EtabsRawGetterCall ReadTable(EtabsBulkTableSpec spec, EtabsRawGetterCall metadata) => spec.Editing
            ? Read("DatabaseTables.GetTableForEditingArray", [spec.Key, "All"])
            : Read("DatabaseTables.GetTableForDisplayArray", [spec.Key, Strings(metadata, 2), "All"]);
    }
}
