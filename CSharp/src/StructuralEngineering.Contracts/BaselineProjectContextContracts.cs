namespace StructuralEngineering.Contracts;

public enum BaselineFireRequirement { Unspecified, NotRequired, Required }
public sealed record BaselineFireBasis(BaselineFireRequirement Requirement, string DecisionReference, double? RequiredMinutes = null);
public sealed record BaselineLateralRestraintBasis(IReadOnlyList<double> RestraintStationsMm, string EvidenceReference);
