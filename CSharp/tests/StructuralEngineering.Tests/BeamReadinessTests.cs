using System.Globalization;
using System.IO.Compression;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BeamReadinessTests
{
    [Fact]
    public void RetainedCohortIsReadyWithoutChangingSourceOrQualifyingEngineering()
    {
        var request = ReadyRequest();
        var before = AnalysisSnapshotCodec.CanonicalJsonBytes(request.Snapshot!);
        var result = BeamReadinessOperations.Assess(request);
        Assert.Equal(3, result.Members.Count);
        Assert.All(result.Members, x => Assert.True(x.ReadyForSelectedProfile,
            string.Join(';', x.Diagnostics.Select(d => d.Code + ":" + d.Message))));
        Assert.All(result.Members, x => Assert.Equal(BaselineRunState.Complete, x.State));
        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(ApprovalState.Unreviewed, result.Approval);
        Assert.Contains("HOLD", result.SourceQualification);
        Assert.Equal(before, AnalysisSnapshotCodec.CanonicalJsonBytes(request.Snapshot!));
        var bytes = BeamReadinessOperations.Serialize(result);
        Assert.Equal(bytes, BeamReadinessOperations.Serialize(BeamReadinessOperations.Parse(bytes)));
        var fixture = Environment.GetEnvironmentVariable("LIB2_READINESS_CONFORMANCE_PATH");
        if (!string.IsNullOrWhiteSpace(fixture))
        {
            using var output = File.Create(fixture);
            using var gzip = new GZipStream(output, CompressionLevel.SmallestSize);
            gzip.Write(bytes);
            gzip.WriteByte((byte)'\n');
        }
        var altered = JsonNode.Parse(bytes)!;
        altered["ledger"]!["fields"]![0]!["state"] = "supplied";
        Assert.Throws<JsonException>(() => BeamReadinessOperations.Parse(Encoding.UTF8.GetBytes(altered.ToJsonString())));
        var imported = BeamReadinessOperations.ImportRequest(bytes);
        Assert.Equal(request.MemberIds, imported.MemberIds);
    }

    [Fact]
    public void ProvisionalMissingUnsupportedAndFailedRemainDistinctAndAccounted()
    {
        var request = ReadyRequest();
        var provisional = BeamReadinessOperations.Assess(request with { Acceptance = null });
        Assert.All(provisional.Members, x => Assert.Equal(BaselineRunState.Incomplete, x.State));
        var missing = BeamReadinessOperations.Assess(request with { Snapshot = null });
        Assert.Equal(request.MemberIds, missing.Members.Select(x => x.MemberId));
        Assert.All(missing.Members, x => Assert.Equal(BaselineRunState.NeedsInput, x.State));
        var failed = BeamReadinessOperations.Assess(request with { Snapshot = request.Snapshot! with { SnapshotSha256 = new string('0', 64) } });
        Assert.All(failed.Members, x => Assert.Equal(BaselineRunState.Failed, x.State));
        var changed = Change(request, "member.intent", "Other");
        var unsupported = BeamReadinessOperations.Assess(changed);
        Assert.Equal(BaselineRunState.Unsupported, unsupported.Members[0].State);
        Assert.Equal(3, unsupported.Members.Count);
        var absent = BeamReadinessOperations.Assess(request with { MemberIds = [.. request.MemberIds, "member:absent"], Acceptance = null });
        Assert.Equal(4, absent.Members.Count);
        Assert.Equal("MEMBER.MISSING", absent.Members[^1].Diagnostics[0].Code);
        var casePath = Environment.GetEnvironmentVariable("LIB2_READINESS_CASES_PATH");
        if (!string.IsNullOrWhiteSpace(casePath))
        {
            var baseline = JsonNode.Parse(BeamReadinessOperations.Serialize(BeamReadinessOperations.Assess(request)))!;
            var cases = new[] { ("provisional", provisional), ("missing", missing), ("unsupported", unsupported), ("failed", failed) }
                .Select(item => new
                {
                    name = item.Item1,
                    expected_states = item.Item2.Members.Select(x => x.State).ToArray(),
                    changes = Differences(baseline, JsonNode.Parse(BeamReadinessOperations.Serialize(item.Item2)), []).ToArray()
                }).ToArray();
            File.WriteAllText(casePath, Encoding.UTF8.GetString(AnalysisSnapshotCodec.CanonicalJsonBytes(cases)) + "\n", new UTF8Encoding(false));
        }
    }

    [Fact]
    public void ChangedSupportRoleEpochOrProvenanceInvalidatesRealRequestAndReuse()
    {
        var request = ReadyRequest();
        var original = BeamReadinessOperations.Assess(request);
        foreach (var changed in new[] { Change(request, "member.support", "Continuous"),
            Change(request, "selection.role", "SlsTotal", BeamInputScope.Selection, "selection-case:WP11_ULS"),
            Change(request, "member.evidence_reference", "updated source of the supplied decision") })
        {
            var result = BeamReadinessOperations.Assess(changed);
            Assert.NotEqual(original.RequestId, result.RequestId);
            Assert.NotEqual(original.Ledger!.Revision, result.Ledger!.Revision);
            Assert.False(BeamReadinessOperations.IsCurrent(original, changed));
            Assert.False(result.Members[0].ReadyForSelectedProfile);
        }
        // A changed epoch without re-bound capture evidence is invalid, never a current replay.
        var epoch = request.Snapshot! with { SourceIdentity = request.Snapshot!.SourceIdentity with { ResultEpochId = "changed-epoch" } };
        Assert.False(BeamReadinessOperations.IsCurrent(original, request with { Snapshot = epoch }));
        Assert.NotEqual(original.RequestId, BeamReadinessOperations.Assess(request with { Snapshot = epoch }).RequestId);
        var cover = Change(request, "design.cover", "40");
        var resolved = BeamReviewResolver.Resolve(cover.Snapshot!, cover.MemberIds, cover.Preset, edits: cover.Edits);
        var reboundWithoutReconciliation = cover with { Acceptance = cover.Acceptance! with { LedgerRevision = resolved.Ledger.Revision } };
        var mismatch = BeamReadinessOperations.Assess(reboundWithoutReconciliation);
        Assert.Equal("INPUT.LEDGER_MISMATCH", mismatch.Members[0].Diagnostics[0].Code);
        var newProjectRevision = request with
        {
            Acceptance = request.Acceptance! with
            { Inputs = request.Acceptance.Inputs with { Project = request.Acceptance.Inputs.Project with { RevisionId = "new-decision-revision" } } }
        };
        Assert.False(BeamReadinessOperations.IsCurrent(original, newProjectRevision));
        Assert.Equal(original.Ledger!.Revision, BeamReadinessOperations.Assess(newProjectRevision).Ledger!.Revision);
    }

    [Fact]
    public void EvidenceStatesRetainZeroAbsentDerivedAssumedAndConflictingInput()
    {
        var request = ReadyRequest();
        var result = BeamReadinessOperations.Assess(request);
        var zero = result.Ledger!.Fields.First(x => x.Key == "member.left_centre");
        Assert.Equal("zero", zero.State);
        Assert.Equal("absent", zero.SourceState);
        Assert.Equal("zero", zero.EnteredState);
        var defaults = BeamReviewResolver.Resolve(request.Snapshot!, request.MemberIds, request.Preset);
        Assert.Equal("Unknown", defaults.Ledger.Fields.First(x => x.Key == "member.intent").Value);
        Assert.Equal("derived", defaults.Ledger.Fields.First(x => x.Key == "member.horizontal").State);
        Assert.Equal("defaulted", defaults.Ledger.Fields.First(x => x.Key == "member.support").State);
        Assert.Equal(BeamValueOrigin.Source, defaults.Ledger.Fields.First(x => x.Key == "member.width").Origin);
        var id = request.MemberIds[0];
        var duplicate = BeamReviewResolver.Edit("member.support", BeamInputScope.Member, id,
            BeamReviewResolver.ModelBinding(request.Snapshot!), "Continuous", 999);
        var conflict = BeamReadinessOperations.Assess(request with { Edits = [.. request.Edits, duplicate] });
        Assert.Equal("conflicting", conflict.Ledger!.Fields.First(x => x.SubjectId == id && x.Key == "member.support").State);
        Assert.Equal(BaselineRunState.NeedsInput, conflict.Members[0].State);
    }

    [Fact]
    public void UnknownSupportAndConflictingRetainedSupportRemainMissingInput()
    {
        var request = ReadyRequest();
        var unknown = BeamReadinessOperations.Assess(Change(request, "member.support", "Unknown"));
        Assert.Equal(BaselineRunState.NeedsInput, unknown.Members[0].State);
        Assert.Equal("INPUT.SUPPORT_REQUIRED", unknown.Members[0].Diagnostics[0].Code);
        Assert.Equal("member.support", unknown.Members[0].Diagnostics[0].FieldOrLocation);
        var continuous = Change(request, "member.support", "Continuous");
        var saved = BeamReviewResolver.Resolve(continuous.Snapshot!, continuous.MemberIds, continuous.Preset, edits: continuous.Edits).Ledger;
        var invalid = Change(continuous, "member.support", "=invalid") with { SavedLedger = saved };
        var conflicting = continuous with
        {
            SavedLedger = saved,
            Edits = [.. continuous.Edits,
            BeamReviewResolver.Edit("member.support", BeamInputScope.Member, request.MemberIds[0],
                BeamReviewResolver.ModelBinding(request.Snapshot!), "SimplySupported", 1001)]
        };
        foreach (var changed in new[] { invalid, conflicting })
        {
            var result = BeamReadinessOperations.Assess(changed);
            Assert.Equal("Continuous", result.Ledger!.Fields.Single(x => x.SubjectId == request.MemberIds[0] && x.Key == "member.support").Value);
            Assert.Equal(BaselineRunState.NeedsInput, result.Members[0].State);
            Assert.Equal("INPUT.CONFLICT_OR_INVALID", result.Members[0].Diagnostics[0].Code);
        }
    }

    private static BeamReadinessRequest Change(BeamReadinessRequest request, string key, string value,
        BeamInputScope scope = BeamInputScope.Member, string? scopeId = null) => request with
        {
            Edits = BeamReviewResolver.ApplyEdit(request.Edits, BeamReviewResolver.Edit(key, scope,
                scopeId ?? request.MemberIds[0], BeamReviewResolver.ModelBinding(request.Snapshot!), value, 1000))
        };

    private sealed record JsonChange(IReadOnlyList<string> Path, JsonNode? Value);
    private static IEnumerable<JsonChange> Differences(JsonNode? before, JsonNode? after, string[] path)
    {
        if (JsonNode.DeepEquals(before, after)) yield break;
        if (before is JsonObject first && after is JsonObject second && first.Select(x => x.Key).SequenceEqual(second.Select(x => x.Key)))
        {
            foreach (var (key, value) in second)
                foreach (var change in Differences(first[key], value, [.. path, key])) yield return change;
        }
        else if (before is JsonArray a && after is JsonArray b && a.Count == b.Count)
        {
            for (var i = 0; i < a.Count; i++)
                foreach (var change in Differences(a[i], b[i], [.. path, i.ToString(CultureInfo.InvariantCulture)])) yield return change;
        }
        else yield return new(path, after?.DeepClone());
    }

    internal static BeamReadinessRequest ReadyRequest()
    {
        var snapshot = BaselineDesignTests.LoadOwnedSnapshot();
        var inputs = BeamReviewExamples.Owned(snapshot).Inputs;
        using var stream = typeof(BeamReadinessTests).Assembly.GetManifestResourceStream("DemoPreset.json")!;
        using var reader = new StreamReader(stream);
        var preset = BeamReviewPresetReader.Parse(reader.ReadToEnd());
        var edits = new List<BeamInputEdit>();
        var binding = BeamReviewResolver.ModelBinding(snapshot);
        var ids = snapshot.Members.Select(x => x.MemberId).ToArray();
        void Add(string key, object value, BeamInputScope scope = BeamInputScope.Project, string id = "project") =>
            edits.Add(BeamReviewResolver.Edit(key, scope, id, scope == BeamInputScope.Project ? null : binding,
                Convert.ToString(value, CultureInfo.InvariantCulture)!, edits.Count + 1));
        Add("design.cover", 35); Add("design.link_fy", 415); Add("design.fire_requirement", "NotRequired");
        Add("detailing.bars", "12,16,20"); Add("detailing.links", "8,10"); Add("detailing.link_spacings", "250,200,150,100");
        Add("detailing.bar_counts", "2,3,4,6"); Add("detailing.layers", "1,2"); Add("detailing.preferred_layers", 1);
        Add("detailing.stock", "6000,12000"); Add("catalogue.maximum_candidates", 1000);
        foreach (var c in inputs.MemberContexts)
        {
            Add("member.intent", "OrdinaryBeam", BeamInputScope.Member, c.MemberId);
            Add("member.support", c.SupportCondition, BeamInputScope.Member, c.MemberId);
            Add("member.physical_span", c.PhysicalSpanId, BeamInputScope.Member, c.MemberId);
            Add("member.left_centre", c.LeftSupportCentreXMm, BeamInputScope.Member, c.MemberId);
            Add("member.anchor_start", c.AnchorageStartXMm, BeamInputScope.Member, c.MemberId);
            Add("member.anchor_end", c.AnchorageEndXMm, BeamInputScope.Member, c.MemberId);
        }
        foreach (var role in inputs.SelectionRoles) Add("selection.role", role.Role, BeamInputScope.Selection, role.SelectionId);
        var resolved = BeamReviewResolver.Resolve(snapshot, ids, preset, edits: edits);
        return new("lnv01-wp11-owned-rectangular-v1", ids, snapshot, preset, null, edits,
            new(resolved.Ledger.Revision, inputs));
    }
}
