using System.Text.Json;

namespace StructuralEngineering.Contracts;

public enum BaselineRunState { Complete, NeedsInput, Unsupported, Failed, Stale, Incomplete, NoFeasibleArrangement, Cancelled }
public sealed record BaselineArrangement(string RevisionId, IReadOnlyList<BarCoordinate> Bars,
    IReadOnlyList<LongitudinalBarPath> Paths, TransverseLink Link, double BottomEffectiveDepthMm,
    double TopEffectiveDepthMm, double TotalLongitudinalAreaMm2, int BottomCount, int TopCount,
    double BottomDiameterMm, double TopDiameterMm, int BottomLayers, int TopLayers);
public sealed record BaselineCheckEvidence(string RuleId, CheckScope Scope, string ScopeId,
    IReadOnlyList<string> ActionRowIds, ResultEnvelope<JsonElement> Result);
public sealed record BaselineCandidateEvaluation(BaselineArrangement Arrangement,
    IReadOnlyList<BaselineCheckEvidence> Checks, IReadOnlyList<ResultEnvelope<JsonElement>> Derivations,
    ResultEnvelope<MemberDesignOutput>? MemberResult, bool Qualified);
public sealed record BaselineDesignOptions(int MaximumCandidates = 1000);
public sealed record BaselineMemberDesignResult(string MemberId, string EffectiveInputId,
    string EngineRevisionId, BaselineRunState State, int EvaluatedCandidates, int EnumeratedCandidates,
    BaselineCandidateEvaluation? Design, IReadOnlyList<Diagnostic> Diagnostics);
public sealed record BaselineBatchDesignResult(string RequestId, string SnapshotId,
    BaselineProjectInputs AcceptedInputs, BaselineDesignOptions Options,
    IReadOnlyList<BaselineMemberDesignResult> Members);
