using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

/// <summary>Host-free input admission. Resolution and engineering guards remain with their existing owners.</summary>
public static class BeamReadinessOperations
{
    public const string SchemaVersion = "beam-readiness/v1";
    public const string PolicyRevision = "beam-readiness-lnv01-v1";
    public const string Operation = "is456.beam.readiness/v1";
    public const string SourceQualification = "offline_replay_only;physical_material_and_current_installed_qualification=HOLD;engineering_acceptance=not_granted";
    private static readonly JsonSerializerOptions Options = CreateOptions();

    public static BeamReadinessDocument Assess(BeamReadinessRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.CohortId) || request.MemberIds.Count == 0 ||
            request.MemberIds.Any(string.IsNullOrWhiteSpace) || request.MemberIds.Distinct(StringComparer.Ordinal).Count() != request.MemberIds.Count)
            throw new ArgumentException("A named cohort and distinct, nonblank requested member IDs are required.", nameof(request));
        var id = Identity("beam_readiness_request", new
        { request, policy_revision = PolicyRevision, engine_identity = BaselineDesignOperations.EngineIdentity });
        BeamInputLedger? ledger = null;
        var members = new List<BeamMemberReadiness>();
        if (request.Snapshot is null)
            return Finish(All(BaselineRunState.NeedsInput, "REPLAY.SNAPSHOT_REQUIRED", "The exact retained snapshot is required.", "snapshot", "BaselineReplay.Run"));
        if (AnalysisSnapshotCodec.Validate(request.Snapshot).Snapshot is null)
            return Finish(All(BaselineRunState.Failed, "SNAPSHOT.INVALID", "Retained snapshot failed its identity or evidence validation.", "snapshot", "AnalysisSnapshotCodec.Validate"));
        var resolved = BeamReviewResolver.Resolve(request.Snapshot, request.MemberIds, request.Preset, request.SavedLedger, request.Edits);
        ledger = resolved.Ledger;
        foreach (var member in resolved.Members)
        {
            try { members.Add(AssessMember(member)); }
            catch (Exception error) when (error is ArgumentException or InvalidOperationException or NullReferenceException)
            {
                members.Add(Outcome(member.MemberId, BaselineRunState.Failed, "READINESS.MEMBER_FAILED", error.Message,
                    "member_context", "BaselineInputMapper.Map"));
            }
        }
        return Finish(members);

        BeamMemberReadiness AssessMember(BeamResolvedMember member)
        {
            var fields = resolved.Ledger.Fields.Where(x => x.SubjectId == member.MemberId || x.SubjectId.StartsWith(member.MemberId + "/", StringComparison.Ordinal)).ToArray();
            var intent = fields.Single(x => x.Key == "member.intent");
            if (!request.Snapshot.Members.Any(x => x.MemberId == member.MemberId))
                return Outcome(member.MemberId, BaselineRunState.NeedsInput, "MEMBER.MISSING", "Requested member is absent from the retained snapshot.", "member_id", "BaselineInputMapper.Map");
            // The mapper establishes unsupported source actions before supplemental inputs.
            // Other profile exclusions may depend on unresolved or conflicting ledger values.
            var core = BaselineInputMapper.MapCore(new BaselineSnapshotIndex(request.Snapshot), member.Inputs, member.MemberId);
            if (core.State == BaselineDesignState.Stale || core.Diagnostics.Any(x => x.Code is
                "ACTION.UNSUPPORTED_COMPONENT" or "ACTION.BASIS_UNSUPPORTED" or "SECTION.PROFILE_UNSUPPORTED"))
                return new(member.MemberId, core.State == BaselineDesignState.Unsupported ? BaselineRunState.Unsupported : BaselineRunState.Stale, false, null, core.Diagnostics);
            if (fields.Any(x => x.Origin is BeamValueOrigin.ConflictFallback or BeamValueOrigin.LastValid ||
                x.EditIds.Count > 0 && x.Origin != BeamValueOrigin.Override))
                return Outcome(member.MemberId, BaselineRunState.NeedsInput, "INPUT.CONFLICT_OR_INVALID", "Correct retained invalid or conflicting entries before profile admission.",
                    string.Join(',', fields.Where(x => x.EditIds.Count > 0 && x.Origin != BeamValueOrigin.Override).Select(x => x.Key)), "BeamReviewResolver.Resolve");
            if (fields.Single(x => x.Key == "member.support").Value == "Unknown")
                return Outcome(member.MemberId, BaselineRunState.NeedsInput, "INPUT.SUPPORT_REQUIRED", "Physical support intent is unknown; supply the member.support decision.", "member.support", "BeamReviewFields");
            if (core.State == BaselineDesignState.Unsupported)
                return new(member.MemberId, BaselineRunState.Unsupported, false, null, core.Diagnostics);
            if (intent.Value == "Other")
                return Outcome(member.MemberId, BaselineRunState.Unsupported, "PROFILE.MEMBER_INTENT", "Physical purpose is outside the ordinary beam profile.", "member.intent", "BeamReviewFields");
            if (request.Acceptance is null)
                return Outcome(member.MemberId, BaselineRunState.Incomplete, "INPUT.PROVISIONAL", "The ledger remains a provisional review scenario; revision-bound accepted project inputs are required for readiness.", "project.values_accepted", "BeamReviewResolver.Resolve");
            if (request.Acceptance.LedgerRevision != resolved.Ledger.Revision)
                return Outcome(member.MemberId, BaselineRunState.NeedsInput, "INPUT.LEDGER_CHANGED", "Accepted inputs bind a different ledger revision; reconcile the edited values and rebind explicitly.", "acceptance.ledger_revision", "BeamReviewResolver.Resolve");
            if (intent.Value != "OrdinaryBeam" || intent.Origin != BeamValueOrigin.Override ||
                fields.Where(x => x.Key is "member.support" or "selection.role").Any(x => x.Origin != BeamValueOrigin.Override))
                return Outcome(member.MemberId, BaselineRunState.Incomplete, "INPUT.INTENT_PROVISIONAL", "Supply explicit member.intent, member.support and selection.role decisions; fallback assumptions retain their meaning.", "member.intent,member.support,selection.role", "BeamReviewFields");
            if (fields.Single(x => x.Key == "design.code").Value != "IS 456:2000")
                return Outcome(member.MemberId, BaselineRunState.Unsupported, "PROFILE.CODE", "The selected code has no admitted baseline profile.", "design.code", "BeamReviewFields");
            if (!Matches(member, request.Acceptance.Inputs))
                return Outcome(member.MemberId, BaselineRunState.NeedsInput, "INPUT.LEDGER_MISMATCH", "Accepted engineering values differ from the effective ledger; reconcile material, context, catalogue, section and roles.", "member_context,materials,catalogue,selection_roles", "BeamReviewResolver.Resolve");
            var mapped = BaselineInputMapper.Map(request.Snapshot, request.Acceptance.Inputs, member.MemberId);
            return new(member.MemberId, mapped.State switch
            {
                BaselineDesignState.Supported => BaselineRunState.Complete,
                BaselineDesignState.Unsupported => BaselineRunState.Unsupported,
                BaselineDesignState.Stale => BaselineRunState.Stale,
                _ => BaselineRunState.NeedsInput
            }, mapped.State == BaselineDesignState.Supported, mapped.Beam?.EffectiveInputId, mapped.Diagnostics);
        }

        IEnumerable<BeamMemberReadiness> All(BaselineRunState state, string code, string message, string field, string owner) =>
            request.MemberIds.Select(member => Outcome(member, state, code, message, field, owner));
        BeamReadinessDocument Finish(IEnumerable<BeamMemberReadiness> results)
        {
            var document = new BeamReadinessDocument(SchemaVersion,
                BaselineDesignOperations.ProfileId, PolicyRevision, BaselineDesignOperations.EngineIdentity, id, "",
                request, ledger, results.ToArray(), EngineeringState.NotEvaluated, ApprovalState.Unreviewed, SourceQualification);
            return document with { DocumentId = Identity("beam_readiness_document", document) };
        }
    }

    public static bool IsCurrent(BeamReadinessDocument document, BeamReadinessRequest currentRequest)
    {
        var current = Assess(currentRequest);
        return current.Request.Snapshot is not null && current.Ledger is not null &&
            current.RequestId == document.RequestId && current.Ledger.Revision == document.Ledger?.Revision &&
            Serialize(Assess(document.Request)).AsSpan().SequenceEqual(Serialize(document));
    }

    public static byte[] Serialize(BeamReadinessDocument document) => AnalysisSnapshotCodec.CanonicalJsonBytes(document);

    /// <summary>Parse and replay through the native owners; reject altered claims instead of trusting stored status.</summary>
    public static BeamReadinessDocument Parse(ReadOnlySpan<byte> payload)
    {
        var document = Decode(payload);
        var replay = Assess(document.Request);
        if (!Serialize(replay).AsSpan().SequenceEqual(Serialize(document))) throw new JsonException("Readiness document does not match native replay.");
        return replay;
    }

    /// <summary>Import evidence-bound inputs from another native build; no stored readiness claim is accepted.</summary>
    public static BeamReadinessRequest ImportRequest(ReadOnlySpan<byte> payload) => Decode(payload).Request;

    private static BeamReadinessDocument Decode(ReadOnlySpan<byte> payload)
    {
        using var tree = JsonDocument.Parse(payload.ToArray());
        CheckKeys(tree.RootElement);
        var document = JsonSerializer.Deserialize<BeamReadinessDocument>(payload, Options) ?? throw new JsonException("A readiness document is required.");
        if (!AnalysisSnapshotCodec.CanonicalJsonBytes(tree.RootElement).AsSpan().SequenceEqual(Serialize(document)))
            throw new JsonException("Readiness projection would lose or alter evidence.");
        if (document.SchemaVersion != SchemaVersion || document.ProfileId != BaselineDesignOperations.ProfileId ||
            document.PolicyRevision != PolicyRevision || document.Engineering != EngineeringState.NotEvaluated ||
            document.Approval != ApprovalState.Unreviewed || document.SourceQualification != SourceQualification ||
            document.DocumentId != Identity("beam_readiness_document", document with { DocumentId = "" }) ||
            document.RequestId != Identity("beam_readiness_request", new
            {
                request = document.Request,
                policy_revision = document.PolicyRevision,
                engine_identity = document.EngineIdentity
            }))
            throw new JsonException("Readiness document contract or identity is invalid.");
        return document;
    }

    private static void CheckKeys(JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in value.EnumerateObject())
            {
                if (!names.Add(property.Name)) throw new JsonException("Duplicate readiness JSON field: " + property.Name);
                CheckKeys(property.Value);
            }
        }
        else if (value.ValueKind == JsonValueKind.Array)
            foreach (var item in value.EnumerateArray()) CheckKeys(item);
    }

    private static bool Matches(BeamResolvedMember member, BaselineProjectInputs supplied)
    {
        var expected = member.Inputs;
        var context = supplied.MemberContexts.SingleOrDefault(x => x.MemberId == member.MemberId);
        if (context is null || member.AnalysisAlternative) return false;
        var target = expected.MemberContexts[0];
        context = context with
        {
            EvidenceRevisionId = target.EvidenceRevisionId,
            FireBasis = context.FireBasis is null ? null : context.FireBasis with { DecisionReference = target.FireBasis!.DecisionReference },
            LateralRestraints = context.LateralRestraints is null ? null : context.LateralRestraints with { EvidenceReference = target.LateralRestraints!.EvidenceReference }
        };
        var material = supplied.Materials.SingleOrDefault(x => x.MaterialId == expected.Materials[0].MaterialId);
        var roles = expected.SelectionRoles.Select(x => supplied.SelectionRoles.SingleOrDefault(y => y.SelectionId == x.SelectionId)).ToArray();
        return Equal(context, target) && Equal(material, expected.Materials[0]) &&
            Equal(supplied.Catalogue with { RevisionId = expected.Catalogue.RevisionId }, expected.Catalogue) && Equal(roles, expected.SelectionRoles);
    }

    private static bool Equal(object? left, object? right) => ResultFactory.CanonicalJsonBytes(left!).AsSpan().SequenceEqual(ResultFactory.CanonicalJsonBytes(right!));
    private static string Identity(string kind, object value) => kind + ":" + AnalysisSnapshotCodec.CanonicalizationVersion + ":" + AnalysisSnapshotCodec.CanonicalDigest(value);
    private static BeamMemberReadiness Outcome(string member, BaselineRunState state, string code, string message, string field, string owner) =>
        new(member, state, false, null, [new(code, "error", message, Operation, field, owner, "Update the named input owner and replay the exact ledger and snapshot.")]);

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
            RespectRequiredConstructorParameters = true
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower, allowIntegerValues: false));
        return options;
    }
}
