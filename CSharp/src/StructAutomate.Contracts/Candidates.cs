namespace StructAutomate.Contracts;

public sealed record EvaluatedCandidate(
    string Id, string DefinitionSha256, string AnalysisRevision, double ObjectiveValue,
    IReadOnlyList<CheckResult> Checks);
public sealed record CandidateRankingRequest(
    string SchemaVersion, string AnalysisRevision, IReadOnlyList<string> RequiredCheckIds,
    IReadOnlyList<string> DomainCandidateIds, IReadOnlyList<EvaluatedCandidate> Candidates);
public sealed record RankedCandidate(string Id, double ObjectiveValue, string DefinitionSha256);
public sealed record CandidateRankingResult(
    IReadOnlyList<RankedCandidate> FeasibleCandidates, IReadOnlyList<string> InfeasibleCandidateIds,
    IReadOnlyList<string> UnevaluatedCandidateIds, bool IsCompleteEnumeration,
    string? BestFeasibleCandidateId);
