using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Host-free, all-or-nothing normalization of the WP10 source projection.</summary>
public static class AnalysisSnapshotNormalizer
{
    public const string Policy = "wp10-offline-horizontal-frame/v1";
    private const double Tolerance = 1e-8;
    private static readonly JsonSerializerOptions Options = CreateOptions();

    public static JsonElement SourceData<T>(T value) => JsonSerializer.SerializeToElement(value, Options);
    public static string Digest(object value) => Convert.ToHexStringLower(
        SHA256.HashData(AnalysisSnapshotCodec.CanonicalJsonBytes(value)));

    public static EtabsSnapshotResult Normalize(RawAnalysisCapture raw)
    {
        try { return NormalizeCore(raw); }
        catch (NormalizationException error) { return Failure(error.Code, error.Message); }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or
            JsonException or KeyNotFoundException or NullReferenceException or IndexOutOfRangeException)
        {
            return Failure("ETABS.MAPPING_UNRESOLVED", $"Incomplete source projection: {error.Message}");
        }
    }

    public static EtabsSnapshotResult Failure(string code, string message) => new(
        "etabs.beam_snapshot.import-result/v1", AnalysisSnapshotCodec.Operation,
        SnapshotOperationState.Fenced, ExecutionState.Completed, ApplicabilityState.Unknown,
        EngineeringState.NotEvaluated, CompletenessState.Partial, FreshnessState.Unbound,
        ApprovalState.Unreviewed, null, null,
        [new(code, "error", "raw_capture", message, "Resolve the retained evidence or explicit normalization context; no partial snapshot is accepted.")],
        Provenance([]));

    private static EtabsSnapshotResult NormalizeCore(RawAnalysisCapture raw)
    {
        Require(raw.RawCaptureSha256 == AnalysisSnapshotCodec.RawCaptureSha256(raw),
            "RAW_CAPTURE.HASH_MISMATCH", "The source projection changed after its identity was bound.");
        var metadataRecord = raw.ModelRecords.Single(item => item.RecordKind == RawModelRecordKind.ModelMetadata);
        var sourceMetadata = Read<SourceSnapshotMetadata>(metadataRecord);
        var context = sourceMetadata.Context;
        Require(context.PolicyId == Policy && !string.IsNullOrWhiteSpace(context.EvidenceReference),
            "NORMALIZATION.POLICY", "An explicit supported normalization policy and evidence reference are required.");
        ValidateCoverage(raw, sourceMetadata.Projection);
        var sourceUnits = new SnapshotSourceUnits("m", "kN", "kNm", "kN/m2", "kN*s2/m4");
        Require(raw.SourceUnits == sourceUnits, "UNITS.INVALID", "This source policy requires the proved kN_m_C basis including mass density.");
        var conversion = new SnapshotUnitConversion(1000, 1, 1, 0.001, 1000);
        var units = new SnapshotUnitBasis("mm", "kN", "kNm", "N/mm2", "kg/m3", sourceUnits, conversion);
        var points = Records<SourceSnapshotPoint>(raw, RawModelRecordKind.Point);
        var materials = Records<SourceSnapshotMaterial>(raw, RawModelRecordKind.Material);
        var sections = Records<SourceSnapshotSection>(raw, RawModelRecordKind.Section);
        var members = Records<SourceSnapshotMember>(raw, RawModelRecordKind.Member);
        var cases = Records<SourceSnapshotLoadCase>(raw, RawModelRecordKind.LoadCase);
        var combinations = Records<SourceSnapshotCombination>(raw, RawModelRecordKind.LoadCombination);
        var selections = Records<SourceSnapshotSelection>(raw, RawModelRecordKind.ResultSelection);
        var stations = Records<SourceSnapshotStation>(raw, RawModelRecordKind.Station);
        var pointById = points.ToDictionary(item => item.Data.Id, item => item.Data, StringComparer.Ordinal);
        var memberById = members.ToDictionary(item => item.Data.Id, item => item.Data, StringComparer.Ordinal);
        var casesById = cases.ToDictionary(item => item.Data.Id, item => item.Data, StringComparer.Ordinal);
        var combosById = combinations.ToDictionary(item => item.Data.Id, item => item.Data, StringComparer.Ordinal);
        var normalizedPoints = points.Select(item => new SnapshotPoint(item.Data.Id, item.Data.Name,
            item.Data.X * 1000, item.Data.Y * 1000, item.Data.Z * 1000, item.Data.Story, item.Id)).ToArray();
        var normalizedMaterials = materials.Select(item =>
        {
            Require(context.MaterialClassifications.TryGetValue(item.Data.Name, out var classification) &&
                !string.IsNullOrWhiteSpace(classification.MaterialKind) && !string.IsNullOrWhiteSpace(classification.EvidenceReference),
                "MATERIAL.CLASSIFICATION_REQUIRED", "A source material lacks an explicit evidence-bound classification.");
            return new SnapshotMaterial(item.Data.Id, item.Data.Name, classification!.MaterialKind,
                item.Data.ElasticModulus * 0.001, item.Data.PoissonRatio, item.Data.MassDensity * 1000, item.Id);
        }).ToArray();
        var normalizedSections = sections.Select(item =>
        {
            Require(item.Data.Modifiers.Count == 8 && item.Data.Modifiers.All(value => double.IsFinite(value) && value >= 0),
                "ETABS.MAPPING_UNRESOLVED", "Retain eight finite section modifiers independently of object modifiers.");
            return new SnapshotSection(item.Data.Id, item.Data.Name, SnapshotSectionShape.Rectangular,
                item.Data.MaterialId, item.Data.Area * 1e6, item.Data.Torsion * 1e12,
                item.Data.Inertia2 * 1e12, item.Data.Inertia3 * 1e12,
                item.Data.Width * 1000, item.Data.Depth * 1000, item.Id);
        }).ToArray();
        var axes = new List<SnapshotAxis>();
        var normalizedMembers = new List<SnapshotMember>();
        foreach (var item in members)
        {
            var member = item.Data;
            ValidateAssignments(member);
            var axis = Axis(member, pointById, item.Id);
            axes.Add(axis);
            normalizedMembers.Add(new(member.Id, member.ObjectId, member.Label, member.Story,
                member.PointIId, member.PointJId, member.SectionId, axis.AxisId,
                member.AutoSelectListId is null ? SectionAssignmentKind.Direct : SectionAssignmentKind.AutoSelect,
                member.AutoSelectListId, Modifiers(member.Modifiers),
                new(member.AutomaticOffsets, member.EndOffsetI * 1000, member.EndOffsetJ * 1000, member.RigidZoneFactor),
                new(Releases(member.ReleasesI), Releases(member.ReleasesJ)),
                member.Elements.Select(element => element.Id).Order(StringComparer.Ordinal).ToArray(), item.Id));
        }
        foreach (var selection in selections)
        {
            Require(selection.Data.Selected, "ETABS.SELECTION_UNPROVED", "An unselected result entered the selected scope.");
            Require(IsStatic(selection.Data.Kind, selection.Data.SourceId, new HashSet<string>(StringComparer.Ordinal)),
                "ETABS.CONCURRENCY_UNPROVED", "The selected dependency graph is not completed linear-static concurrency with zero initial conditions.");
        }
        bool IsStatic(SnapshotResultSelectionKind kind, string id, HashSet<string> visiting)
        {
            if (kind == SnapshotResultSelectionKind.LoadCase)
                return casesById.TryGetValue(id, out var loadCase) && loadCase.Kind == SnapshotLoadCaseKind.LinearStatic &&
                    loadCase.Status == SnapshotAnalysisCaseStatus.Finished && (loadCase.InitialCase is "" or "None");
            if (!visiting.Add(id)) return false;
            var valid = combosById.TryGetValue(id, out var combo) && combo.Kind == SnapshotCombinationKind.LinearAdd &&
                combo.Factors.Count > 0 && combo.Factors.All(factor => IsStatic(factor.SourceKind, factor.SourceId, visiting));
            visiting.Remove(id);
            return valid;
        }
        var normalizedSelections = selections.Select(item => new SnapshotResultSelection(item.Data.Id,
            item.Data.Kind, item.Data.SourceId, item.Data.Name, true, SnapshotActionBasis.StaticConcurrent,
            raw.ResultEpochId, item.Id)).ToArray();
        var normalizedStations = stations.Select(item =>
        {
            var station = item.Data;
            var member = memberById[station.MemberId];
            var length = Length(Subtract(pointById[member.PointJId], pointById[member.PointIId]));
            var element = member.Elements.Single(value => value.Id == station.ElementId);
            var physical = element.RelativeI * length + station.ElementStation;
            Require(station.ObjectId == member.ObjectId && double.IsFinite(physical) &&
                Math.Abs(physical - station.ObjectStation) <= Tolerance &&
                station.ElementStation >= -Tolerance && station.ElementStation <= (element.RelativeJ - element.RelativeI) * length + Tolerance &&
                physical >= member.EndOffsetI - Tolerance && physical <= length - member.EndOffsetJ + Tolerance,
                "STATION.UNRESOLVED", "Object and element stations disagree with retained element topology and end offsets.");
            return new SnapshotStation(station.Id, station.MemberId, station.ObjectId, station.ElementId,
                station.ObjectStation * 1000, station.ObjectStation * 1000, station.ElementStation * 1000,
                station.ObjectStation / length, SnapshotStationSide.Continuous, item.Id);
        }).ToArray();
        var forceEvidence = sourceMetadata.Projection.GetterEvidence.Single(item => item.Operation == "Results.FrameForce");
        var rows = new List<SnapshotActionRow>();
        foreach (var row in raw.ForceRows)
        {
            Require(row.StepType == "Single Value" && row.StepNumber is null,
                "ETABS.CONCURRENCY_UNPROVED", "Only proved static Single Value rows use the portable null-step sentinel.");
            var station = normalizedStations.Single(item => item.ObjectId == row.ObjectId && item.AnalysisElementId == row.AnalysisElementId &&
                item.ObjectStationMm == row.ObjectStation * 1000 && item.ElementStationMm == row.ElementStation * 1000);
            var selection = normalizedSelections.Single(item => item.SourceName == row.OutputCaseName);
            var action = new SnapshotActionRow("", row.SourceRowId, station.MemberId, row.ObjectId, row.AnalysisElementId,
                station.StationId, selection.SelectionId, row.OutputCaseName, row.StepType, null,
                SnapshotActionBasis.StaticConcurrent, row.P, row.V2, row.V3, row.T, row.M2, row.M3, "kN", "kNm",
                new("Results.FrameForce", forceEvidence.SignatureAuthoritySha256, forceEvidence.CallId,
                    row.SourceRowIndex, "linear-static dependency closure; original Single Value/0 retained in getter evidence", row.SourceRowId));
            rows.Add(action with { RowId = AnalysisSnapshotCodec.ActionRowId(action) });
        }
        Require(normalizedSelections.All(selection => rows.Any(row => row.SelectionId == selection.SelectionId)),
            "ETABS.ROW_ACCOUNTING", "Every selected result must have accepted same-row actions.");
        var normalizedCases = cases.Select(item => new SnapshotLoadCase(item.Data.Id, item.Data.Name, item.Data.Kind, item.Data.Status, item.Id)).ToArray();
        var normalizedCombos = combinations.Select(item => new SnapshotLoadCombination(item.Data.Id, item.Data.Name, item.Data.Kind, item.Data.Factors, item.Id)).ToArray();
        var disposition = new List<SnapshotRowDispositionRecord>();
        void Accept(string sourceId, string kind, string canonicalId) => disposition.Add(new(sourceId, kind,
            SnapshotRowDisposition.Accepted, canonicalId, null, null, []));
        Accept(metadataRecord.SourceRecordId, "model_metadata", context.ProjectId);
        foreach (var item in normalizedPoints) Accept(item.EvidenceReference, "point", item.PointId);
        foreach (var item in normalizedMaterials) Accept(item.EvidenceReference, "material", item.MaterialId);
        foreach (var item in normalizedSections) Accept(item.EvidenceReference, "section", item.SectionId);
        foreach (var item in normalizedMembers) Accept(item.EvidenceReference, "member", item.MemberId);
        foreach (var item in normalizedCases) Accept(item.EvidenceReference, "load_case", item.CaseId);
        foreach (var item in normalizedCombos) Accept(item.EvidenceReference, "load_combination", item.CombinationId);
        foreach (var item in normalizedSelections) Accept(item.EvidenceReference, "result_selection", item.SelectionId);
        foreach (var item in normalizedStations) Accept(item.EvidenceReference, "station", item.StationId);
        foreach (var item in rows) Accept(item.SourceRowId, "force_row", item.RowId);
        Require(disposition.Count == raw.ModelRecords.Count + raw.ForceRows.Count,
            "ETABS.ROW_ACCOUNTING", "Normalization did not conserve the complete source projection.");
        var source = new SnapshotSourceIdentity("etabs", context.SourceVersion, AnalysisSnapshotCodec.Operation,
            context.AdapterBuildId, raw.AcquisitionId, raw.RawCaptureId, raw.RawCaptureSha256, raw.ModelRevisionId,
            raw.AnalysisRevisionId, raw.ResultEpochId, context.RuntimeFingerprint, context.ProcessIdentity, context.ModelFileSha256);
        var snapshot = new AnalysisSnapshot(AnalysisSnapshotCodec.SnapshotSchemaVersion, AnalysisSnapshotCodec.Operation,
            "", "", context.CreatedAtUtc, source,
            new(context.ProjectId, context.ModelName, new(OptionalEvidenceState.Unavailable, null, "NOT_CAPTURED_BY_GETTER_MATRIX"),
                sourceMetadata.ModelLocked, sourceMetadata.AnalysisStatus, metadataRecord.SourceRecordId), units,
            axes.OrderBy(item => item.AxisId, StringComparer.Ordinal).ToArray(),
            normalizedPoints.OrderBy(item => item.PointId, StringComparer.Ordinal).ToArray(),
            normalizedMaterials.OrderBy(item => item.MaterialId, StringComparer.Ordinal).ToArray(),
            normalizedSections.OrderBy(item => item.SectionId, StringComparer.Ordinal).ToArray(),
            normalizedMembers.OrderBy(item => item.MemberId, StringComparer.Ordinal).ToArray(),
            normalizedCases.OrderBy(item => item.CaseId, StringComparer.Ordinal).ToArray(),
            normalizedCombos.OrderBy(item => item.CombinationId, StringComparer.Ordinal).ToArray(),
            normalizedSelections.OrderBy(item => item.SelectionId, StringComparer.Ordinal).ToArray(),
            normalizedStations.OrderBy(item => item.StationId, StringComparer.Ordinal).ToArray(),
            rows.OrderBy(item => item.RowId, StringComparer.Ordinal).ToArray(),
            new(disposition.Count, disposition.Count, 0, 0, disposition.OrderBy(item => item.SourceRecordId, StringComparer.Ordinal).ToArray()),
            new("structural.analysis_snapshot.normalize/v1", true, Digest(sourceUnits)),
            new(FreshnessState.Current, raw.ModelRevisionId, raw.AnalysisRevisionId, raw.ResultEpochId,
                normalizedSelections.Select(item => item.SelectionId).Order(StringComparer.Ordinal).ToArray()),
            [], Provenance([context.EvidenceReference, $"artifact:{sourceMetadata.Projection.ArtifactSha256}"]),
            Digest(sourceMetadata), raw);
        var sha = AnalysisSnapshotCodec.SnapshotSha256(snapshot);
        snapshot = snapshot with { SnapshotSha256 = sha, SnapshotId = $"analysis_snapshot_id:{AnalysisSnapshotCodec.CanonicalizationVersion}:{sha}" };
        return AnalysisSnapshotCodec.Validate(snapshot);
    }

    private static void ValidateCoverage(RawAnalysisCapture raw, SnapshotProjectionManifest manifest)
    {
        Require(manifest.ModelRecords.Count == raw.ModelRecords.Count &&
            manifest.ModelRecords.SequenceEqual(raw.ModelRecords.Select(item => new SnapshotProjectionRecord(item.SourceRecordId, item.RecordKind))) &&
            manifest.ForceRowIds.SequenceEqual(raw.ForceRows.Select(item => item.SourceRowId)) &&
            raw.ForceRows.Select(item => item.SourceRowIndex).SequenceEqual(Enumerable.Range(0, raw.ForceRows.Count)) &&
            raw.ModelRecords.Select(item => item.SourceRecordId).Distinct(StringComparer.Ordinal).Count() == raw.ModelRecords.Count,
            "ETABS.ROW_ACCOUNTING", "The frozen source inventory and portable projection disagree.");
        var returned = raw.CallLedger.Records.Where(item => item.Stage == SnapshotCallStage.Returned).ToArray();
        var ids = raw.ModelRecords.Select(item => item.SourceRecordId).ToHashSet(StringComparer.Ordinal);
        Require(manifest.GetterEvidence.Count == returned.Length && manifest.GetterEvidence.Select(item => item.Ordinal).SequenceEqual(Enumerable.Range(1, returned.Length)),
            "ETABS.COVERAGE_INCOMPLETE", "Every getter requires one ordered projection evidence record.");
        for (var index = 0; index < returned.Length; index++)
        {
            var evidence = manifest.GetterEvidence[index];
            var call = returned[index];
            Require(evidence.CallId == call.CallId && evidence.Operation == call.Method &&
                evidence.SignatureAuthoritySha256 == call.SignatureAuthoritySha256 &&
                Digest(evidence.Inputs) == call.ArgumentsSha256 && ids.Contains(evidence.TargetSourceRecordId),
                "ETABS.COVERAGE_INCOMPLETE", "Getter facts are not bound to their exact ledger entry and retained model record.");
        }
        var force = manifest.GetterEvidence.Single(item => item.Operation == "Results.FrameForce").Outputs;
        Require(force[0].GetInt32() == raw.ForceRows.Count, "ETABS.ROW_ACCOUNTING", "The force getter count and raw row count disagree.");
        foreach (var row in raw.ForceRows)
        {
            var index = row.SourceRowIndex;
            Require(index >= 0 && index < raw.ForceRows.Count && force[1][index].GetString() == row.ObjectId &&
                force[2][index].GetDouble() == row.ObjectStation && force[3][index].GetString() == row.AnalysisElementId &&
                force[4][index].GetDouble() == row.ElementStation && force[5][index].GetString() == row.OutputCaseName &&
                force[6][index].GetString() == "Single Value" && force[7][index].GetDouble() == 0 && row.StepNumber is null &&
                new[] { row.P, row.V2, row.V3, row.T, row.M2, row.M3 }.Select((value, component) =>
                    value == force[8 + component][index].GetDouble()).All(value => value),
                "ETABS.ROW_ACCOUNTING", "A portable force row differs from its complete original getter row.");
        }
    }

    private static SnapshotAxis Axis(SourceSnapshotMember member, Dictionary<string, SourceSnapshotPoint> points, string evidence)
    {
        var delta = Subtract(points[member.PointJId], points[member.PointIId]);
        var length = Length(delta);
        Require(double.IsFinite(length) && length > 0 && Math.Abs(delta.Z) <= Tolerance,
            "AXIS.UNRESOLVED", "The bounded physical-face convention requires a nonzero horizontal member.");
        var direction = Scale(delta, 1 / length);
        var elements = member.Elements.OrderBy(item => item.RelativeI).ToArray();
        Require(elements.Length > 0, "ETABS.MAPPING_UNRESOLVED", "The member has no retained analysis element.");
        var first = elements[0].LocalToGlobal;
        Require(first.Count == 9, "AXIS.UNRESOLVED", "A nine-value transformation matrix is required.");
        var e1 = new SnapshotVector3(first[0], first[3], first[6]);
        var e2 = new SnapshotVector3(first[1], first[4], first[7]);
        var e3 = new SnapshotVector3(first[2], first[5], first[8]);
        var up = new SnapshotVector3(0, 0, 1);
        var left = Cross(up, direction);
        Require(Near(e1, direction) && Math.Abs(Math.Abs(Dot(e2, up)) - 1) <= Tolerance &&
            Math.Abs(Math.Abs(Dot(e3, left)) - 1) <= Tolerance && Near(Cross(e1, e2), e3) &&
            Math.Abs(Length(e2) - 1) <= Tolerance && Math.Abs(Length(e3) - 1) <= Tolerance,
            "AXIS.UNRESOLVED", "The declared matrix columns must prove I-to-J, global top, viewing-left and handedness.");
        double expectedI = 0;
        foreach (var element in elements)
        {
            Require(element.ObjectId == member.ObjectId && element.RelativeI >= 0 && element.RelativeJ <= 1 &&
                element.RelativeJ > element.RelativeI && Math.Abs(element.RelativeI - expectedI) <= Tolerance &&
                element.LocalToGlobal.Count == 9 && element.LocalToGlobal.Zip(first).All(pair => Math.Abs(pair.First - pair.Second) <= Tolerance),
                "ETABS.MAPPING_UNRESOLVED", "Analysis elements must cover the member without gaps, overlaps or changed local axes.");
            Require(Near(Subtract(points[element.PointIId], points[member.PointIId]), Scale(delta, element.RelativeI)) &&
                Near(Subtract(points[element.PointJId], points[member.PointIId]), Scale(delta, element.RelativeJ)),
                "STATION.UNRESOLVED", "Element endpoints do not prove the retained relative physical positions.");
            expectedI = element.RelativeJ;
        }
        Require(Math.Abs(expectedI - 1) <= Tolerance && member.EndOffsetI + member.EndOffsetJ < length,
            "STATION.UNRESOLVED", "Element coverage or the member's clear interval is incomplete.");
        return new($"axis:{member.Id}", e1, e2, e3,
            new([first[0], first[1], first[2]], [first[3], first[4], first[5]], [first[6], first[7], first[8]]),
            Dot(e2, up) > 0 ? SnapshotLocal2Face.PositiveLocal2 : SnapshotLocal2Face.NegativeLocal2,
            Dot(e3, left) > 0 ? SnapshotLocal3Face.PositiveLocal3 : SnapshotLocal3Face.NegativeLocal3, evidence);
    }

    private static void ValidateAssignments(SourceSnapshotMember member)
    {
        var insertion = member.Insertion;
        Require(insertion.CardinalPoint is >= 1 and <= 11 && !insertion.Mirror2 && !insertion.Mirror3 && !insertion.StiffnessTransformed &&
            insertion.OffsetI.Count == 3 && insertion.OffsetJ.Count == 3 && insertion.OffsetI.Concat(insertion.OffsetJ).All(value => value == 0) &&
            member.SpringsI.Count == 6 && member.SpringsJ.Count == 6 && member.SpringsI.Concat(member.SpringsJ).All(value => value == 0),
            "ASSIGNMENT.UNSUPPORTED", "Mirroring, transformed stiffness, joint offsets or release springs require a separate normalization basis.");
        Require(member.Modifiers.Count == 8 && member.ReleasesI.Count == 6 && member.ReleasesJ.Count == 6,
            "ASSIGNMENT.UNRESOLVED", "Object modifiers and end release arrays must be complete.");
    }

    private static SnapshotModifiers Modifiers(IReadOnlyList<double> values) => new(values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7]);
    private static SnapshotEndReleases Releases(IReadOnlyList<bool> values) => new(values[0], values[1], values[2], values[3], values[4], values[5]);
    private static T Read<T>(RawSnapshotModelRecord item) => item.Fields["data"].Deserialize<T>(Options) ?? throw new JsonException("Missing typed source data.");
    private static (string Id, T Data)[] Records<T>(RawAnalysisCapture raw, RawModelRecordKind kind) =>
        raw.ModelRecords.Where(item => item.RecordKind == kind).Select(item => (item.SourceRecordId, Read<T>(item))).ToArray();
    private static SnapshotVector3 Subtract(SourceSnapshotPoint a, SourceSnapshotPoint b) => new(a.X - b.X, a.Y - b.Y, a.Z - b.Z);
    private static SnapshotVector3 Scale(SnapshotVector3 a, double factor) => new(a.X * factor, a.Y * factor, a.Z * factor);
    private static double Dot(SnapshotVector3 a, SnapshotVector3 b) => a.X * b.X + a.Y * b.Y + a.Z * b.Z;
    private static double Length(SnapshotVector3 a) => Math.Sqrt(Dot(a, a));
    private static SnapshotVector3 Cross(SnapshotVector3 a, SnapshotVector3 b) => new(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X);
    private static bool Near(SnapshotVector3 a, SnapshotVector3 b) => Math.Abs(a.X - b.X) <= Tolerance && Math.Abs(a.Y - b.Y) <= Tolerance && Math.Abs(a.Z - b.Z) <= Tolerance;
    private static void Require(bool condition, string code, string message) { if (!condition) throw new NormalizationException(code, message); }
    private sealed class NormalizationException(string code, string message) : InvalidOperationException(message) { public string Code { get; } = code; }
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
    private static SnapshotProvenance Provenance(IReadOnlyList<string> references) => new("wp10-analysis-snapshot-contract-v1",
        ["PF11 / AO16 / WP10-04", .. references],
        ["Offline capture consistency only; current does not assert today's live model state.",
         "Analysis revision and epoch are evidence-derived, not native ETABS revision identifiers.",
         "Material kind is explicitly supplied; no concrete or reinforcement strength is inferred.",
         "Points and stations follow the object reference line. Raw member data retains cardinal insertion; no centroid relocation is performed.",
         "Section modifiers remain separately retained in raw section data; canonical member modifiers are object modifiers.",
         "No COM, Excel import, structural design, installed qualification or engineering approval is implied."]);
}
