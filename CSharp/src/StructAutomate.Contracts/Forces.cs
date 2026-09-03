namespace StructAutomate.Contracts;

public enum ForceUnit { Newton, Kilonewton, PoundForce }
public enum LengthUnit { Millimetre, Metre, Inch }
public enum MomentUnit { NewtonMillimetre, NewtonMetre, KilonewtonMillimetre, KilonewtonMetre, PoundForceInch, PoundForceFoot }
public enum SelectionKind { Case, Combination }
public sealed record Vector3(double X, double Y, double Z);
public sealed record LocalAxes(Vector3 Local1, Vector3 Local2, Vector3 Local3);
public sealed record AnalysisSource(
    string ModelId, string ModelRevision, string AnalysisRevision, string ExportSha256,
    string EtabsVersion, DateTimeOffset AcquiredAtUtc);
public sealed record ResultSelection(string Id, SelectionKind Kind, string Name);

// These six components always belong to the same source row. No component envelope is substituted.
public sealed record RawFrameForceRow(
    int RowIndex, string MemberId, string ObjectId, double ObjectStation,
    string ElementId, double ElementStation, ResultSelection Selection,
    string OutputCaseName, string StepType, double StepNumber,
    double P, double V2, double V3, double T, double M2, double M3);

public sealed record EtabsForceBatch(
    string SchemaVersion, AnalysisSource Source, bool IsAnalysisCurrent,
    ForceUnit ForceUnit, LengthUnit LengthUnit, MomentUnit MomentUnit,
    IReadOnlyDictionary<string, LocalAxes> ObjectAxes, IReadOnlyList<RawFrameForceRow> Rows);

public sealed record BeamActionRow(
    string RowId, AnalysisSource Source, int SourceRowIndex, string MemberId,
    string ObjectId, double ObjectStationMm, string ElementId, double ElementStationMm,
    ResultSelection Selection, string OutputCaseName, string StepType, double StepNumber,
    double PKn, double V2Kn, double V3Kn, double TKnM, double M2KnM, double M3KnM,
    LocalAxes LocalAxes);
