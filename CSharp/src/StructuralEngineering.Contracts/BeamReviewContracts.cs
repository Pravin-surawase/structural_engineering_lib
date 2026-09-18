namespace StructuralEngineering.Contracts;

public enum BeamInputScope { Project, Material, Story, PhysicalSpan, Member, Selection }
public enum BeamValueOrigin { Source, Preset, Rule, Override, LastValid, ConflictFallback }
public enum BeamReviewAvailability { Available, Example, Unavailable, Cancelled }

/// <summary>Entered text is evidence, never an expression to execute. A scope is model-bound except Project.</summary>
public sealed record BeamInputEdit(string Id, string Key, BeamInputScope Scope, string ScopeId,
    string? ModelBinding, string EnteredText, long Sequence);

public sealed record BeamFieldDefinition(string Key, string Unit, string Kind, string Consumer,
    string DataGroup, string FallbackRule, bool AffectsStructure = true);

public sealed record BeamEffectiveField(string SubjectId, string Key, string Unit, string? SourceText,
    string? EnteredText, string Value, BeamValueOrigin Origin, string Reason, string RuleRevision,
    string PresetRevision, IReadOnlyList<string> EditIds, string? LastValidOverride);

public sealed record BeamReviewPreset(string Id, string Revision,
    IReadOnlyDictionary<string, string> Values);

public sealed record BeamInputLedger(string SchemaVersion, string ModelBinding, string SnapshotSha256,
    string PresetRevision, IReadOnlyList<string> MemberIds, IReadOnlyList<BeamInputEdit> Edits,
    IReadOnlyList<BeamEffectiveField> Fields, string Revision);

/// <summary>One member per input bundle permits a material override without changing another member.</summary>
public sealed record BeamResolvedMember(string MemberId, BaselineProjectInputs Inputs,
    double WidthMm, double DepthMm, bool AnalysisAlternative, string StructuralRevision);

public sealed record BeamResolvedReview(BeamInputLedger Ledger, IReadOnlyList<BeamResolvedMember> Members);

public sealed record BeamReviewStage(string StageId, BeamReviewAvailability Availability, string Status,
    string Basis, IReadOnlyList<string> EvidenceIds);

/// <summary>Completion covers independent core checks only. It cannot be stored as a BaselineMemberDesignResult.</summary>
public sealed record BeamCorePreviewResult(string MemberId, string EffectiveInputId, string EngineRevisionId,
    BaselineRunState State, int EvaluatedCandidates, int EnumeratedCandidates, BaselineCandidateEvaluation? Design,
    IReadOnlyList<Diagnostic> Diagnostics);

/// <summary>Core evidence is provisional. FullDesign is produced only by the unchanged strict baseline operation.</summary>
public sealed record BeamMemberReview(string MemberId, string SourceStatus, string ScenarioStatus,
    string CoreStatus, string FullDesignStatus, bool WorkflowComplete, string StructuralRevision,
    BeamCorePreviewResult? Core, BaselineMemberDesignResult? FullDesign,
    IReadOnlyList<BeamReviewStage> Stages, IReadOnlyList<Diagnostic> Diagnostics,
    BaselineMemberDesignResult? ExampleCore = null, IReadOnlyList<BaselineCheckEvidence>? ServiceChecks = null,
    BeamReviewCostEvidence? Cost = null);

public sealed record BeamReviewQuantityEvidence(string StructuralRevision,
    ResultEnvelope<ConstructionQuantityOutput> Result);
public sealed record BeamReviewCostEvidence(string BasisId, BeamReviewAvailability Availability,
    ConstructionQuantityOutput Quantities, ResultEnvelope<ConstructionCostOutput> Result);

public sealed record BeamReviewResult(string RequestId, string EngineIdentity, string SnapshotSha256,
    BeamInputLedger Ledger, IReadOnlyList<BeamMemberReview> Members, bool WorkflowComplete,
    string ExampleBasisId, string LiveAcquisitionStatus);

public sealed record BeamReviewExample(string Id, AnalysisSnapshot Snapshot, BaselineProjectInputs Inputs,
    string MemberId);
