namespace StructuralEngineering.Contracts;

/// <summary>Existing accepted project inputs bound to the exact review ledger. This does not grant approval.</summary>
public sealed record BeamReadinessAcceptance(string LedgerRevision, BaselineProjectInputs Inputs);

public sealed record BeamReadinessRequest(string CohortId, IReadOnlyList<string> MemberIds,
    AnalysisSnapshot? Snapshot, BeamReviewPreset Preset, BeamInputLedger? SavedLedger,
    IReadOnlyList<BeamInputEdit> Edits, BeamReadinessAcceptance? Acceptance);

/// <summary>Complete means ready for the selected input profile, never a completed design.</summary>
public sealed record BeamMemberReadiness(string MemberId, BaselineRunState State,
    bool ReadyForSelectedProfile, string? EffectiveInputId, IReadOnlyList<Diagnostic> Diagnostics);

public sealed record BeamReadinessDocument(string SchemaVersion, string ProfileId,
    string PolicyRevision, string EngineIdentity, string RequestId, string DocumentId,
    BeamReadinessRequest Request, BeamInputLedger? Ledger,
    IReadOnlyList<BeamMemberReadiness> Members, EngineeringState Engineering,
    ApprovalState Approval, string SourceQualification);
