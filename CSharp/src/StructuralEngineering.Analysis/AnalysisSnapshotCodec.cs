using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Analysis;

/// <summary>Strict host-free parsing, validation, identity, and replay for WP10 snapshots.</summary>
public static class AnalysisSnapshotCodec
{
    public const string Operation = "etabs.beam_snapshot.import/v1";
    public const string SnapshotSchemaVersion = "structural.analysis_snapshot/v1";
    public const string CanonicalizationVersion = "pf4-canonical-json-v1";
    public const int MaximumSnapshotBytes = 25_000_000;

    private static readonly JsonSerializerOptions JsonOptions = CreateOptions();
    private static readonly SnapshotProvenance DefaultProvenance = new(
        "wp10-analysis-snapshot-contract-v1",
        [
            "PF4 engineering semantic model",
            "PF8 portable analysis snapshot contract",
            "WP10-01 shared conformance fixture"
        ],
        [
            "Offline validation proves portable evidence integrity, not live ETABS compatibility.",
            "Snapshot acceptance is not structural analysis validation or engineering approval."
        ]);

    public static EtabsImportRequest ParseImportRequest(string json)
    {
        EnsureText(json);
        using var document = JsonDocument.Parse(json);
        EnsureNoDuplicateProperties(document.RootElement);
        var request = JsonSerializer.Deserialize<EtabsImportRequest>(json, JsonOptions)
            ?? throw new JsonException("AO16 request cannot be null.");
        ValidateRequest(request);
        return request;
    }

    public static EtabsSnapshotResult ParseAndValidate(string json)
    {
        try
        {
            EnsureText(json);
            using var document = JsonDocument.Parse(json);
            EnsureNoDuplicateProperties(document.RootElement);
            var snapshot = JsonSerializer.Deserialize<AnalysisSnapshot>(json, JsonOptions)
                ?? throw new JsonException("Snapshot cannot be null.");
            return Validate(snapshot);
        }
        catch (Exception exception) when (exception is JsonException or ArgumentException or InvalidOperationException or NullReferenceException)
        {
            return Rejected(
                "INPUT.SCHEMA",
                "$",
                $"The portable snapshot does not match the strict version-1 schema: {exception.Message}",
                "Correct the required fields, enum tokens, value types, and unknown fields.");
        }
    }

    public static EtabsSnapshotResult Validate(AnalysisSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        var required = ValidateRequiredStructure(snapshot);
        if (required is not null) return required;
        var values = ValidateDomainValues(snapshot);
        if (values is not null) return values;
        var ledger = ValidateLedger(snapshot);
        if (ledger is not null) return ledger;
        var source = ValidateSource(snapshot);
        if (source is not null) return source;
        var rowLedger = ValidateRowLedger(snapshot);
        if (rowLedger is not null) return rowLedger;
        var unitsAxes = ValidateUnitsAndAxes(snapshot);
        if (unitsAxes is not null) return unitsAxes;
        var mapping = ValidateMapping(snapshot);
        if (mapping is not null) return mapping;

        var rawSha = RawCaptureSha256(snapshot.RawCapture);
        var expectedRawId = $"raw_capture_id:{CanonicalizationVersion}:{rawSha}";
        if (snapshot.RawCapture.RawCaptureSha256 != rawSha || snapshot.RawCapture.RawCaptureId != expectedRawId)
        {
            return Rejected(
                "RAW_CAPTURE.HASH_MISMATCH",
                "raw_capture",
                "The raw-capture identity or digest does not match its canonical bytes.",
                "Reject the artifact and recapture or restore the exact bytes.");
        }

        var snapshotSha = SnapshotSha256(snapshot);
        var expectedSnapshotId = $"analysis_snapshot_id:{CanonicalizationVersion}:{snapshotSha}";
        if (snapshot.SnapshotSha256 != snapshotSha || snapshot.SnapshotId != expectedSnapshotId)
        {
            return Rejected(
                "SNAPSHOT.HASH_MISMATCH",
                "snapshot_sha256",
                "The snapshot identity or digest does not match its canonical hash basis.",
                "Reject the payload and replay from the intact raw capture.");
        }

        if (snapshot.Diagnostics.Count != 0)
        {
            return Blocked(
                "SNAPSHOT.DIAGNOSTIC_BLOCK",
                "diagnostics",
                "An accepted snapshot cannot retain unresolved diagnostics.",
                "Resolve every diagnostic before accepting the snapshot.");
        }

        return new(
            "etabs.beam_snapshot.import-result/v1",
            Operation,
            SnapshotOperationState.Completed,
            ExecutionState.Completed,
            ApplicabilityState.Applicable,
            EngineeringState.NotEvaluated,
            CompletenessState.CompleteForScope,
            FreshnessState.Current,
            ApprovalState.Unreviewed,
            null,
            snapshot,
            [],
            snapshot.Provenance);
    }

    public static string CanonicalJson(AnalysisSnapshot snapshot) =>
        Encoding.UTF8.GetString(CanonicalJsonBytes(snapshot));

    public static byte[] CanonicalJsonBytes(object value)
    {
        var node = JsonSerializer.SerializeToNode(value, JsonOptions)
            ?? throw new ArgumentException("Canonical value cannot be null.", nameof(value));
        return Encoding.UTF8.GetBytes(Canonical(node));
    }

    public static string SnapshotSha256(AnalysisSnapshot snapshot) =>
        Sha256(HashBasis(snapshot, "snapshot_id", "snapshot_sha256"));

    public static string RawCaptureSha256(RawAnalysisCapture capture) =>
        Sha256(HashBasis(capture, "raw_capture_id", "raw_capture_sha256"));

    public static string CallRecordSha256(SnapshotCallRecord record) =>
        Sha256(HashBasis(record, "record_sha256"));

    public static string CallLedgerSha256(SnapshotCallLedger ledger) =>
        Sha256(HashBasis(ledger, "ledger_sha256"));

    public static string ActionRowId(SnapshotActionRow row) =>
        $"analysis_action_row_id:{CanonicalizationVersion}:{Sha256(HashBasis(row, "row_id"))}";

    private static JsonObject HashBasis(object value, params string[] excluded)
    {
        var node = JsonSerializer.SerializeToNode(value, JsonOptions) as JsonObject
            ?? throw new ArgumentException("Identity values must serialize as objects.", nameof(value));
        foreach (var key in excluded) node.Remove(key);
        return node;
    }

    private static string Sha256(object value) =>
        Convert.ToHexStringLower(SHA256.HashData(CanonicalJsonBytes(value)));

    private static EtabsSnapshotResult? ValidateRequiredStructure(AnalysisSnapshot snapshot)
    {
        if (snapshot.SchemaVersion != SnapshotSchemaVersion || snapshot.OperationSemanticId != Operation ||
            !Text(snapshot.SnapshotId) || !Sha(snapshot.SnapshotSha256) || !Utc(snapshot.CreatedAtUtc) ||
            snapshot.SourceIdentity is null || snapshot.Metadata is null || snapshot.Units is null ||
            snapshot.RawCapture is null || snapshot.RowLedger is null || snapshot.Normalization is null ||
            snapshot.Freshness is null || snapshot.Provenance is null || !Sha(snapshot.EvidenceManifestSha256) ||
            snapshot.Axes is null || snapshot.Axes.Count == 0 || snapshot.Points is null || snapshot.Points.Count < 2 ||
            snapshot.Materials is null || snapshot.Materials.Count == 0 || snapshot.Sections is null || snapshot.Sections.Count == 0 ||
            snapshot.Members is null || snapshot.Members.Count == 0 || snapshot.LoadCases is null || snapshot.LoadCases.Count == 0 ||
            snapshot.LoadCombinations is null || snapshot.ResultSelections is null || snapshot.ResultSelections.Count == 0 ||
            snapshot.Stations is null || snapshot.Stations.Count == 0 || snapshot.ActionRows is null || snapshot.ActionRows.Count == 0 ||
            snapshot.Diagnostics is null)
        {
            return Rejected("INPUT.SCHEMA", "$", "The snapshot omits a required version-1 field or collection.", "Supply the complete strict version-1 payload.");
        }
        return null;
    }

    private static EtabsSnapshotResult? ValidateDomainValues(AnalysisSnapshot snapshot)
    {
        var source = snapshot.SourceIdentity;
        var metadata = snapshot.Metadata;
        var raw = snapshot.RawCapture;
        if (!Text(source.SourceVersion) || !Text(source.AdapterBuildId) || !Text(source.AcquisitionId) ||
            !Text(source.ModelRevisionId) || !Text(source.AnalysisRevisionId) || !Text(source.ResultEpochId) ||
            !Text(source.RuntimeFingerprint) || !Text(metadata.ProjectId) || !Text(metadata.ModelName) || !Text(metadata.EvidenceReference) ||
            raw.SchemaVersion != "structural.analysis_raw_capture/v1" || !Text(raw.RawCaptureId) || !Sha(raw.RawCaptureSha256) ||
            !Text(raw.AcquisitionId) || !Text(raw.ModelRevisionId) || !Text(raw.AnalysisRevisionId) || !Text(raw.ResultEpochId) ||
            raw.SourceUnits is null || raw.CallLedger is null || raw.CallLedger.Records is null || raw.ModelRecords is null || raw.ModelRecords.Count == 0 || raw.ForceRows is null || raw.ForceRows.Count == 0 ||
            !Text(raw.SourceUnits.Length) || !Text(raw.SourceUnits.Force) || !Text(raw.SourceUnits.Moment) || !Text(raw.SourceUnits.Stress) || !Text(raw.SourceUnits.MassDensity) ||
            raw.CallLedger.SchemaVersion != "structural.analysis_call_ledger/v1" || !Text(raw.CallLedger.OperationId) || !Sha(raw.CallLedger.LedgerSha256) ||
            snapshot.Normalization.RuleId != "structural.analysis_snapshot.normalize/v1" || !Sha(snapshot.Normalization.SourceUnitsSha256) ||
            snapshot.Provenance.ContractRevisionId != "wp10-analysis-snapshot-contract-v1" || snapshot.Provenance.SourceReferences is null || snapshot.Provenance.SourceReferences.Count == 0 || snapshot.Provenance.Limitations is null)
            return Rejected("INPUT.SCHEMA", "$", "The snapshot contains an invalid required identity, version, unit, or provenance value.", "Supply the strict version-1 values and non-empty evidence identities.");

        if (raw.CallLedger.Records.Any(record => record is null || record.SchemaVersion != "structural.analysis_call_record/v1" ||
                !Text(record.OperationId) || !Text(record.CallId) || record.Sequence < 1 || !Text(record.Method) ||
                !Sha(record.SignatureAuthoritySha256) || !Sha(record.ArgumentsSha256) || !Sha(record.RecordSha256) || !Utc(record.RecordedAtUtc)) ||
            raw.ModelRecords.Any(record => record is null || !Text(record.SourceRecordId) || record.Fields is null) ||
            raw.ForceRows.Any(row => row is null || !Text(row.SourceRowId) || row.SourceRowIndex < 0 || !Text(row.ObjectId) ||
                !Text(row.AnalysisElementId) || !Text(row.OutputCaseName) || !Text(row.StepType) ||
                !FiniteNonnegative(row.ObjectStation) || !FiniteNonnegative(row.ElementStation) ||
                !Finite(row.StepNumber) || !Finite(row.P) || !Finite(row.V2) || !Finite(row.V3) || !Finite(row.T) || !Finite(row.M2) || !Finite(row.M3)))
            return Rejected("INPUT.SCHEMA", "raw_capture", "The raw capture contains an invalid call, model, or force record.", "Retain finite values and complete source/call identities for every raw record.");

        if (snapshot.Axes.Any(axis => axis is null || !Text(axis.AxisId) || axis.E1 is null || axis.E2 is null || axis.E3 is null || axis.SourceToCommon is null || !Text(axis.EvidenceReference)) ||
            snapshot.Points.Any(point => point is null || !Text(point.PointId) || !Text(point.SourceName) || !Text(point.StoryId) || !Text(point.EvidenceReference) || !Finite(point.XMm) || !Finite(point.YMm) || !Finite(point.ZMm)) ||
            snapshot.Materials.Any(material => material is null || !Text(material.MaterialId) || !Text(material.SourceName) || !Text(material.MaterialKind) || !Text(material.EvidenceReference) || !FinitePositive(material.ElasticModulusNPerMm2) || !double.IsFinite(material.PoissonRatio) || material.PoissonRatio is <= -1 or >= 0.5 || !FiniteNonnegative(material.MassDensityKgPerM3)) ||
            snapshot.Sections.Any(section => section is null || !Text(section.SectionId) || !Text(section.SourceName) || !Text(section.MaterialId) || !Text(section.EvidenceReference) || !FinitePositive(section.AreaMm2) || !FinitePositive(section.TorsionalConstantMm4) || !FinitePositive(section.Inertia2Mm4) || !FinitePositive(section.Inertia3Mm4) || !FiniteOptionalPositive(section.WidthMm) || !FiniteOptionalPositive(section.DepthMm)))
            return Rejected("INPUT.SCHEMA", "model_facts", "A normalized geometry, material, section, or axis record contains an invalid value.", "Supply finite physical values and complete source/evidence identities.");

        if (snapshot.Members.Any(member => member is null || !Text(member.MemberId) || !Text(member.ObjectId) || !Text(member.SourceLabel) || !Text(member.StoryId) ||
                !Text(member.PointIId) || !Text(member.PointJId) || !Text(member.SectionId) || !Text(member.AxisId) || !Text(member.EvidenceReference) ||
                member.Modifiers is null || member.Offsets is null || member.Releases is null || member.AnalysisElementIds is null ||
                !new[] { member.Modifiers.AxialArea, member.Modifiers.ShearArea2, member.Modifiers.ShearArea3, member.Modifiers.Torsion, member.Modifiers.Inertia2, member.Modifiers.Inertia3, member.Modifiers.Mass, member.Modifiers.Weight }.All(FiniteNonnegative) ||
                !FiniteNonnegative(member.Offsets.EndIMm) || !FiniteNonnegative(member.Offsets.EndJMm) || !double.IsFinite(member.Offsets.RigidZoneFactor) || member.Offsets.RigidZoneFactor is < 0 or > 1) ||
            snapshot.LoadCases.Any(item => item is null || !Text(item.CaseId) || !Text(item.SourceName) || !Text(item.EvidenceReference)) ||
            snapshot.LoadCombinations.Any(item => item is null || !Text(item.CombinationId) || !Text(item.SourceName) || !Text(item.EvidenceReference) || item.Factors is null || item.Factors.Count == 0 || item.Factors.Any(factor => factor is null || !Text(factor.SourceId) || !double.IsFinite(factor.ScaleFactor))) ||
            snapshot.ResultSelections.Any(item => item is null || !Text(item.SelectionId) || !Text(item.SourceId) || !Text(item.SourceName) || !Text(item.ResultEpochId) || !Text(item.EvidenceReference)) ||
            snapshot.Stations.Any(item => item is null || !Text(item.StationId) || !Text(item.MemberId) || !Text(item.ObjectId) || !Text(item.AnalysisElementId) || !Text(item.EvidenceReference)) ||
            snapshot.ActionRows.Any(item => item is null || !Text(item.RowId) || !Text(item.SourceRowId) || !Text(item.MemberId) || !Text(item.ObjectId) || !Text(item.AnalysisElementId) || !Text(item.StationId) || !Text(item.SelectionId) || !Text(item.OutputCaseName) || !Text(item.StepType) || item.Provenance is null || !Text(item.Provenance.GetterMethod) || !Sha(item.Provenance.SignatureAuthoritySha256) || !Text(item.Provenance.CallId) || item.Provenance.SourceRowIndex < 0 || !Text(item.Provenance.ConcurrencyBasis) || !Text(item.Provenance.EvidenceReference) || !Finite(item.StepNumber) || !Finite(item.PKn) || !Finite(item.V2Kn) || !Finite(item.V3Kn) || !Finite(item.TKnm) || !Finite(item.M2Knm) || !Finite(item.M3Knm)))
            return Rejected("INPUT.SCHEMA", "normalized_records", "A normalized member, loading, selection, station, or action record contains an invalid value.", "Supply finite values and complete portable identities for every normalized record.");
        return null;
    }

    private static EtabsSnapshotResult? ValidateLedger(AnalysisSnapshot snapshot)
    {
        var ledger = snapshot.RawCapture.CallLedger;
        if (ledger is null || ledger.Records is null || ledger.OperationId != snapshot.SourceIdentity.AcquisitionId || ledger.OperationId != snapshot.RawCapture.AcquisitionId)
            return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger.operation_id", "The call ledger is not bound to the acquisition.", "Retain the exact acquisition identity in every call record and ledger.");
        if (ledger.RecordCount != ledger.Records.Count || !ledger.Records.Select(record => record.Sequence).SequenceEqual(Enumerable.Range(1, ledger.Records.Count)))
            return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger.records", "The call ledger is truncated or has a sequence gap.", "Retain every started and returned record in sequence.");

        string? previous = null;
        string? pending = null;
        foreach (var record in ledger.Records)
        {
            if (record is null || record.OperationId != ledger.OperationId || record.Effect != SnapshotCallEffect.Getter ||
                record.PreviousRecordSha256 != previous)
                return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger.records", "The call ledger contains an unbound, non-getter, or discontinuous call.", "Capture getter-only calls under one continuous operation identity.");
            if (record.Stage == SnapshotCallStage.Started)
            {
                if (pending is not null || record.ReturnCode is not null || record.RawShape is not null)
                    return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger.records", "A started getter has invalid pairing or returned fields.", "Close each getter before starting another call.");
                pending = record.CallId;
            }
            else if (pending != record.CallId || record.ReturnCode != 0 || !Text(record.RawShape))
                return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger.records", "A getter did not return successfully against its started call.", "Retain the exact paired successful getter result.");
            else
                pending = null;
            previous = record.RecordSha256;
        }
        if (pending is not null || ledger.HeadRecordSha256 != previous)
            return Uncertain("ETABS.LEDGER_UNFINALIZED", "raw_capture.call_ledger", "The call ledger has an unmatched start or incorrect head.", "Finalize the durable getter ledger before normalization.");
        if (ledger.Records.Any(record => CallRecordSha256(record) != record.RecordSha256) || CallLedgerSha256(ledger) != ledger.LedgerSha256)
            return Uncertain("ETABS.LEDGER_INVALID", "raw_capture.call_ledger", "A call-ledger digest does not match its canonical payload.", "Reject or recapture the tampered call ledger.");
        return null;
    }

    private static EtabsSnapshotResult? ValidateSource(AnalysisSnapshot snapshot)
    {
        var source = snapshot.SourceIdentity;
        var raw = snapshot.RawCapture;
        if (source.SourceSystem != "etabs" || source.AdapterSemanticId != Operation ||
            source.AcquisitionId != raw.AcquisitionId || source.ModelRevisionId != raw.ModelRevisionId ||
            source.AnalysisRevisionId != raw.AnalysisRevisionId || source.ResultEpochId != raw.ResultEpochId ||
            source.RawCaptureId != raw.RawCaptureId || source.RawCaptureSha256 != raw.RawCaptureSha256)
            return Blocked("ETABS.IDENTITY_DRIFT", "source_identity", "Source and raw-capture identities disagree.", "Reacquire one internally consistent source artifact.");
        if (!ValidOptional(source.ProcessIdentity, false) || !ValidOptional(source.ModelFileSha256, true) || !ValidOptional(snapshot.Metadata.ModelGuid, false))
            return Rejected("INPUT.SCHEMA", "source_identity", "An optional evidence record has conflicting state, value, or reason.", "Use supplied with one value, or a non-supplied state with one reason.");
        var fresh = snapshot.Freshness;
        if (fresh.State != FreshnessState.Current || fresh.ModelRevisionId != source.ModelRevisionId || fresh.AnalysisRevisionId != source.AnalysisRevisionId || fresh.ResultEpochId != source.ResultEpochId)
            return Blocked("ETABS.RESULT_EPOCH_INVALID", "freshness", "The normalized snapshot is stale or bound to another analysis/result epoch.", "Acquire current completed results and rebuild the snapshot.");
        if (snapshot.Metadata.AnalysisStatus != SnapshotAnalysisCaseStatus.Finished)
            return Blocked("ETABS.RESULT_EPOCH_INVALID", "metadata.analysis_status", "The source analysis is not recorded as finished.", "Select a completed result epoch before acquisition.");
        var selectionIds = snapshot.ResultSelections.Select(item => item.SelectionId).ToArray();
        if (!fresh.SelectionIds.SequenceEqual(selectionIds, StringComparer.Ordinal) || snapshot.ResultSelections.Any(item => !item.SelectedForOutput))
            return Blocked("ETABS.SELECTION_UNPROVED", "result_selections", "The complete selected-result set is not proved.", "Stop before force acquisition when selection is absent.");
        if (snapshot.ResultSelections.Any(item => item.ResultEpochId != source.ResultEpochId))
            return Blocked("ETABS.RESULT_EPOCH_INVALID", "result_selections", "A selected result belongs to another result epoch.", "Reacquire selections and results under one epoch.");
        return null;
    }

    private static EtabsSnapshotResult? ValidateRowLedger(AnalysisSnapshot snapshot)
    {
        var ledger = snapshot.RowLedger;
        if (ledger.Rows is null || ledger.SourceRowCount != ledger.Rows.Count ||
            ledger.SourceRowCount != ledger.AcceptedCount + ledger.ApprovedExclusionCount + ledger.BlockedCount ||
            ledger.AcceptedCount != ledger.Rows.Count(row => row.Disposition == SnapshotRowDisposition.Accepted) ||
            ledger.ApprovedExclusionCount != ledger.Rows.Count(row => row.Disposition == SnapshotRowDisposition.ApprovedExclusion) ||
            ledger.BlockedCount != ledger.Rows.Count(row => row.Disposition == SnapshotRowDisposition.Blocked))
            return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger", "The row-ledger totals do not conserve every source row.", "Reconcile the disposition counts and records.");
        if (ledger.BlockedCount != 0)
            return Blocked("ETABS.ROW_BLOCKED", "row_ledger", "At least one required source row is blocked.", "Resolve or explicitly approve the row before creating a complete snapshot.");
        foreach (var row in ledger.Rows)
        {
            var accepted = row.Disposition == SnapshotRowDisposition.Accepted;
            var excluded = row.Disposition == SnapshotRowDisposition.ApprovedExclusion;
            if (accepted && (!Text(row.CanonicalId) || row.ReasonCode is not null || row.ApprovalReference is not null || row.DiagnosticCodes.Count != 0) ||
                excluded && (row.CanonicalId is not null || !Text(row.ReasonCode) || !Text(row.ApprovalReference) || row.DiagnosticCodes.Count != 0))
                return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "A row disposition has conflicting accepted/exclusion evidence.", "Use the exact fields required by its disposition.");
        }
        var sourceIds = snapshot.RawCapture.ModelRecords.Select(item => item.SourceRecordId)
            .Concat(snapshot.RawCapture.ForceRows.Select(item => item.SourceRowId)).ToHashSet(StringComparer.Ordinal);
        var ledgerIds = ledger.Rows.Select(item => item.SourceRecordId).ToArray();
        if (ledgerIds.Length != ledgerIds.Distinct(StringComparer.Ordinal).Count() || !sourceIds.SetEquals(ledgerIds))
            return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "The row ledger does not account for every raw record exactly once.", "Reconcile raw and disposition identities without omission or duplication.");
        if (snapshot.ActionRows.Select(item => item.SourceRowId).Distinct(StringComparer.Ordinal).Count() != snapshot.ActionRows.Count)
            return Blocked("ETABS.ROW_ACCOUNTING", "action_rows.source_row_id", "More than one canonical action row is bound to the same raw force row.", "Bind every raw force row to at most one canonical action row.");
        var actionBySource = snapshot.ActionRows.ToDictionary(item => item.SourceRowId, item => item.RowId, StringComparer.Ordinal);
        var expectedModelRows = new Dictionary<string, (string RecordKind, string CanonicalId)>(StringComparer.Ordinal);
        foreach (var raw in snapshot.RawCapture.ModelRecords)
        {
            IEnumerable<(string EvidenceReference, string CanonicalId)> candidates = raw.RecordKind switch
            {
                RawModelRecordKind.ModelMetadata => [(snapshot.Metadata.EvidenceReference, snapshot.Metadata.ProjectId)],
                RawModelRecordKind.Point => snapshot.Points.Select(item => (item.EvidenceReference, item.PointId)),
                RawModelRecordKind.Material => snapshot.Materials.Select(item => (item.EvidenceReference, item.MaterialId)),
                RawModelRecordKind.Section => snapshot.Sections.Select(item => (item.EvidenceReference, item.SectionId)),
                RawModelRecordKind.Member => snapshot.Members.Select(item => (item.EvidenceReference, item.MemberId)),
                RawModelRecordKind.LoadCase => snapshot.LoadCases.Select(item => (item.EvidenceReference, item.CaseId)),
                RawModelRecordKind.LoadCombination => snapshot.LoadCombinations.Select(item => (item.EvidenceReference, item.CombinationId)),
                RawModelRecordKind.ResultSelection => snapshot.ResultSelections.Select(item => (item.EvidenceReference, item.SelectionId)),
                RawModelRecordKind.Station => snapshot.Stations.Select(item => (item.EvidenceReference, item.StationId)),
                _ => []
            };
            var matches = candidates.Where(item => item.EvidenceReference == raw.SourceRecordId).ToArray();
            if (matches.Length != 1)
                return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "A raw model row is not bound to exactly one canonical model fact.", "Bind each raw model row to one fact of the matching record kind.");
            expectedModelRows[raw.SourceRecordId] = (RawRecordKindToken(raw.RecordKind), matches[0].CanonicalId);
        }
        foreach (var item in ledger.Rows)
        {
            if (expectedModelRows.TryGetValue(item.SourceRecordId, out var expectedModel))
            {
                if (item.RecordKind != expectedModel.RecordKind || item.Disposition != SnapshotRowDisposition.Accepted || item.CanonicalId != expectedModel.CanonicalId)
                    return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "An accepted model row is not bound to its canonical kind and identity.", "Bind each accepted raw model row to its matching canonical model fact.");
            }
            else if (actionBySource.TryGetValue(item.SourceRecordId, out var actionId))
            {
                if (item.RecordKind != "force_row" || item.Disposition != SnapshotRowDisposition.Accepted || item.CanonicalId != actionId)
                    return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "An accepted action row is not bound to its canonical identity.", "Bind each accepted raw force row to its action-row identity.");
            }
            else if (item.RecordKind == "force_row" && item.Disposition == SnapshotRowDisposition.Accepted)
                return Blocked("ETABS.ROW_ACCOUNTING", "row_ledger.rows", "An accepted raw force row has no canonical action row.", "Normalize or explicitly exclude every force row.");
        }
        return null;
    }

    private static string RawRecordKindToken(RawModelRecordKind recordKind) => recordKind switch
    {
        RawModelRecordKind.ModelMetadata => "model_metadata",
        RawModelRecordKind.Point => "point",
        RawModelRecordKind.Material => "material",
        RawModelRecordKind.Section => "section",
        RawModelRecordKind.Member => "member",
        RawModelRecordKind.LoadCase => "load_case",
        RawModelRecordKind.LoadCombination => "load_combination",
        RawModelRecordKind.ResultSelection => "result_selection",
        RawModelRecordKind.Station => "station",
        _ => throw new ArgumentOutOfRangeException(nameof(recordKind), recordKind, null)
    };

    private static EtabsSnapshotResult? ValidateUnitsAndAxes(AnalysisSnapshot snapshot)
    {
        var units = snapshot.Units;
        var conversion = units.ConversionToCanonical;
        if (units.Length != "mm" || units.Force != "kN" || units.Moment != "kNm" || units.Stress != "N/mm2" || units.MassDensity != "kg/m3" ||
            units.OriginalSourceUnits != snapshot.RawCapture.SourceUnits ||
            !(FinitePositive(conversion.LengthToMm) && FinitePositive(conversion.ForceToKn) && FinitePositive(conversion.MomentToKnm) && FinitePositive(conversion.StressToNPerMm2) && FinitePositive(conversion.MassDensityToKgPerM3)) ||
            Sha256(units.OriginalSourceUnits) != snapshot.Normalization.SourceUnitsSha256 || !snapshot.Normalization.ConversionPerformedOnce)
            return Blocked("UNITS.INVALID", "units", "Source units, conversion factors, or one-time normalization evidence are inconsistent.", "Record source units once and apply a positive declared conversion once.");
        if (snapshot.Axes.Any(axis => !ValidAxes(axis)))
            return Blocked("AXIS.UNRESOLVED", "axes", "An axis or source-to-common transform is not orthonormal and right-handed.", "Resolve axes and physical faces from retained geometry evidence.");
        return null;
    }

    private static EtabsSnapshotResult? ValidateMapping(AnalysisSnapshot snapshot)
    {
        if (!UniqueOrdered(snapshot.Axes, item => item.AxisId) || !UniqueOrdered(snapshot.Points, item => item.PointId) ||
            !UniqueOrdered(snapshot.Materials, item => item.MaterialId) || !UniqueOrdered(snapshot.Sections, item => item.SectionId) ||
            !UniqueOrdered(snapshot.Members, item => item.MemberId) || !UniqueOrdered(snapshot.LoadCases, item => item.CaseId) ||
            !UniqueOrdered(snapshot.LoadCombinations, item => item.CombinationId) || !UniqueOrdered(snapshot.ResultSelections, item => item.SelectionId) ||
            !UniqueOrdered(snapshot.Stations, item => item.StationId) || !UniqueOrdered(snapshot.ActionRows, item => item.RowId))
            return Blocked("SNAPSHOT.ORDER_INVALID", "$", "Portable arrays must have unique identities in deterministic order.", "Sort each identity-bearing collection before serialization.");
        if (!snapshot.RawCapture.ModelRecords.Select(item => item.SourceRecordId).SequenceEqual(snapshot.RawCapture.ModelRecords.Select(item => item.SourceRecordId).Order(StringComparer.Ordinal), StringComparer.Ordinal) ||
            !snapshot.RawCapture.ForceRows.Select(item => (item.SourceRowIndex, item.SourceRowId)).SequenceEqual(snapshot.RawCapture.ForceRows.Select(item => (item.SourceRowIndex, item.SourceRowId)).Order()))
            return Blocked("SNAPSHOT.ORDER_INVALID", "raw_capture", "Raw records are not in deterministic source order.", "Sort model identities and preserve force-row ordinal order.");
        var requiredKinds = Enum.GetValues<RawModelRecordKind>().ToHashSet();
        if (!requiredKinds.SetEquals(snapshot.RawCapture.ModelRecords.Select(item => item.RecordKind)))
            return Blocked("ETABS.MAPPING_UNRESOLVED", "raw_capture.model_records", "The raw capture omits a required model-fact record kind.", "Capture metadata, geometry, assignments, cases, combinations, selections, and stations.");

        var rawIds = snapshot.RawCapture.ModelRecords.Select(item => item.SourceRecordId).ToHashSet(StringComparer.Ordinal);
        var evidence = new List<string> { snapshot.Metadata.EvidenceReference };
        evidence.AddRange(snapshot.Axes.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.Points.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.Materials.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.Sections.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.Members.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.LoadCases.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.LoadCombinations.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.ResultSelections.Select(item => item.EvidenceReference));
        evidence.AddRange(snapshot.Stations.Select(item => item.EvidenceReference));
        if (evidence.Any(item => !rawIds.Contains(item)))
            return Blocked("ETABS.MAPPING_UNRESOLVED", "$", "A normalized model fact lacks a retained raw-record reference.", "Bind every normalized fact to one raw model record.");

        var axes = snapshot.Axes.ToDictionary(item => item.AxisId, StringComparer.Ordinal);
        var points = snapshot.Points.ToDictionary(item => item.PointId, StringComparer.Ordinal);
        var materials = snapshot.Materials.ToDictionary(item => item.MaterialId, StringComparer.Ordinal);
        var sections = snapshot.Sections.ToDictionary(item => item.SectionId, StringComparer.Ordinal);
        var members = snapshot.Members.ToDictionary(item => item.MemberId, StringComparer.Ordinal);
        var cases = snapshot.LoadCases.ToDictionary(item => item.CaseId, StringComparer.Ordinal);
        var combinations = snapshot.LoadCombinations.ToDictionary(item => item.CombinationId, StringComparer.Ordinal);
        var selections = snapshot.ResultSelections.ToDictionary(item => item.SelectionId, StringComparer.Ordinal);
        var stations = snapshot.Stations.ToDictionary(item => item.StationId, StringComparer.Ordinal);
        if (snapshot.Sections.Any(section => !materials.ContainsKey(section.MaterialId) ||
                (section.Shape == SnapshotSectionShape.Rectangular) != (section.WidthMm is > 0 && section.DepthMm is > 0)) ||
            snapshot.Members.Any(member => !points.ContainsKey(member.PointIId) || !points.ContainsKey(member.PointJId) || member.PointIId == member.PointJId || !sections.ContainsKey(member.SectionId) || !axes.ContainsKey(member.AxisId) ||
                member.AnalysisElementIds.Count == 0 || member.AnalysisElementIds.Distinct(StringComparer.Ordinal).Count() != member.AnalysisElementIds.Count ||
                (member.AssignmentKind == SectionAssignmentKind.AutoSelect) != Text(member.AutoSelectListId)))
            return Blocked("ETABS.MAPPING_UNRESOLVED", "members", "A geometry, section, material, axis, or assignment reference is unresolved.", "Retain complete connectivity and assignments.");
        foreach (var combination in snapshot.LoadCombinations)
        {
            if (!combination.Factors.Select(item => item.Ordinal).SequenceEqual(Enumerable.Range(0, combination.Factors.Count)) ||
                combination.Factors.Any(factor => factor.SourceKind == SnapshotResultSelectionKind.LoadCase ? !cases.ContainsKey(factor.SourceId) : !combinations.ContainsKey(factor.SourceId)))
                return Blocked("ETABS.MAPPING_UNRESOLVED", "load_combinations.factors", "A combination factor source or ordinal is unresolved.", "Retain ordered referenced cases or combinations.");
        }
        if (snapshot.ResultSelections.Any(selection => selection.Kind == SnapshotResultSelectionKind.LoadCase ? !cases.ContainsKey(selection.SourceId) : !combinations.ContainsKey(selection.SourceId)))
            return Blocked("ETABS.SELECTION_UNPROVED", "result_selections.source_id", "A selected case/combination definition is missing.", "Retain the selected result definition.");
        foreach (var station in snapshot.Stations)
        {
            if (!members.TryGetValue(station.MemberId, out var member) || station.ObjectId != member.ObjectId || !member.AnalysisElementIds.Contains(station.AnalysisElementId, StringComparer.Ordinal) ||
                !FiniteNonnegative(station.PhysicalStationMm) || !FiniteNonnegative(station.ObjectStationMm) || !FiniteNonnegative(station.ElementStationMm) || !double.IsFinite(station.NormalizedRatio) || station.NormalizedRatio is < 0 or > 1)
                return Blocked("ETABS.MAPPING_UNRESOLVED", "stations", "A station's physical/object/element mapping is unresolved.", "Resolve all three station identities from retained topology evidence.");
        }

        var returned = snapshot.RawCapture.CallLedger.Records.Where(item => item.Stage == SnapshotCallStage.Returned).ToDictionary(item => item.CallId, StringComparer.Ordinal);
        var rawRows = snapshot.RawCapture.ForceRows.ToDictionary(item => item.SourceRowId, StringComparer.Ordinal);
        var conversion = snapshot.Units.ConversionToCanonical;
        foreach (var row in snapshot.ActionRows)
        {
            var requiresStep = row.ActionBasis is SnapshotActionBasis.StagedStep or SnapshotActionBasis.ResponseResult;
            if (!stations.TryGetValue(row.StationId, out var station) || !selections.TryGetValue(row.SelectionId, out var selection) || !rawRows.TryGetValue(row.SourceRowId, out var raw) || !returned.TryGetValue(row.Provenance.CallId, out var call) ||
                (row.MemberId, row.ObjectId, row.AnalysisElementId) != (station.MemberId, station.ObjectId, station.AnalysisElementId) || row.ActionBasis != selection.ActionBasis ||
                (row.ObjectId, row.AnalysisElementId, row.OutputCaseName, row.StepType, row.StepNumber) != (raw.ObjectId, raw.AnalysisElementId, raw.OutputCaseName, raw.StepType, raw.StepNumber) ||
                row.OutputCaseName != selection.SourceName || requiresStep != row.StepNumber.HasValue ||
                row.Provenance.SignatureAuthoritySha256 != call.SignatureAuthoritySha256 || row.Provenance.SourceRowIndex != raw.SourceRowIndex ||
                row.Provenance.GetterMethod != call.Method || row.Provenance.EvidenceReference != raw.SourceRowId ||
                Math.Abs(station.ObjectStationMm - raw.ObjectStation * conversion.LengthToMm) > 1e-12 ||
                Math.Abs(station.ElementStationMm - raw.ElementStation * conversion.LengthToMm) > 1e-12)
                return Blocked("ETABS.MAPPING_UNRESOLVED", "action_rows", "An action row lacks consistent station, selection, raw-row, or getter evidence.", "Retain the complete provenance chain for each force row.");
            var expected = new[] { raw.P * conversion.ForceToKn, raw.V2 * conversion.ForceToKn, raw.V3 * conversion.ForceToKn, raw.T * conversion.MomentToKnm, raw.M2 * conversion.MomentToKnm, raw.M3 * conversion.MomentToKnm };
            var actual = new[] { row.PKn, row.V2Kn, row.V3Kn, row.TKnm, row.M2Knm, row.M3Knm };
            if (expected.Zip(actual).Any(pair => Math.Abs(pair.First - pair.Second) > 1e-12) || row.ForceUnit != "kN" || row.MomentUnit != "kNm")
                return Blocked("UNITS.INVALID", "action_rows", "A normalized force component does not match the one-time source conversion.", "Normalize all six signed components from the same raw row.");
            if (ActionRowId(row) != row.RowId)
                return Blocked("SNAPSHOT.HASH_MISMATCH", "action_rows.row_id", "An action-row identity does not match its canonical payload.", "Regenerate the row identity from the complete same-row payload.");
        }
        return null;
    }

    private static void ValidateRequest(EtabsImportRequest request)
    {
        if (request.SchemaVersion != "etabs.beam_snapshot.import-request/v1" || request.OperationSemanticId != Operation || !Text(request.RequestId) ||
            request.SourceExpectation is null || request.Scope is null || !Utc(request.DeadlineUtc) || request.RequiredProvenance is null || request.RequiredProvenance.Count == 0 ||
            request.RequiredProvenance.Any(item => !Text(item)) || request.RequiredProvenance.Distinct(StringComparer.Ordinal).Count() != request.RequiredProvenance.Count ||
            request.SourceExpectation.SourceSystem != "etabs" || !Text(request.SourceExpectation.SourceVersion) || !Text(request.SourceExpectation.ModelRevisionId) ||
            !ValidOptional(request.SourceExpectation.ProcessIdentity, false) || !ValidOptional(request.SourceExpectation.ModelFileSha256, true) || !Text(request.Scope.ProjectId) ||
            request.Scope.ResultSelectionIds is null || request.Scope.ResultSelectionIds.Count == 0 || request.Scope.ResultSelectionIds.Distinct(StringComparer.Ordinal).Count() != request.Scope.ResultSelectionIds.Count ||
            request.Scope.ResultKinds is null || request.Scope.ResultKinds.Count == 0 || request.Scope.ResultKinds.Distinct().Count() != request.Scope.ResultKinds.Count ||
            request.Scope.Members is null || request.Scope.Stations is null || request.Scope.Members.MemberIds is null || request.Scope.Stations.StationIds is null ||
            request.Scope.Members.MemberIds.Any(item => !Text(item)) || request.Scope.Members.MemberIds.Distinct(StringComparer.Ordinal).Count() != request.Scope.Members.MemberIds.Count ||
            request.Scope.Stations.StationIds.Any(item => !Text(item)) || request.Scope.Stations.StationIds.Distinct(StringComparer.Ordinal).Count() != request.Scope.Stations.StationIds.Count ||
            (request.Scope.Members.Mode == MemberSelectionMode.Explicit) != (request.Scope.Members.MemberIds.Count > 0) ||
            (request.Scope.Stations.Mode == StationSelectionMode.Explicit) != (request.Scope.Stations.StationIds.Count > 0))
            throw new ArgumentException("AO16 request fields or conditional selections are invalid.", nameof(request));
    }

    private static bool ValidOptional(PortableOptionalText value, bool sha)
    {
        if (value is null) return false;
        if (value.State == OptionalEvidenceState.Supplied)
            return Text(value.Value) && value.ReasonCode is null && (!sha || Sha(value.Value!));
        return value.Value is null && Text(value.ReasonCode);
    }

    private static bool UniqueOrdered<T>(IReadOnlyList<T> values, Func<T, string> selector)
    {
        var ids = values.Select(selector).ToArray();
        return ids.Length == ids.Distinct(StringComparer.Ordinal).Count() && ids.SequenceEqual(ids.Order(StringComparer.Ordinal), StringComparer.Ordinal);
    }

    private static bool ValidAxes(SnapshotAxis axis)
    {
        var vectors = new[] { Vector(axis.E1), Vector(axis.E2), Vector(axis.E3) };
        var rows = new[] { axis.SourceToCommon.Row1.ToArray(), axis.SourceToCommon.Row2.ToArray(), axis.SourceToCommon.Row3.ToArray() };
        return OrthonormalRightHanded(vectors) && rows.All(item => item.Length == 3) && OrthonormalRightHanded(rows);
    }

    private static double[] Vector(SnapshotVector3 value) => [value.X, value.Y, value.Z];
    private static double Dot(double[] a, double[] b) => a.Zip(b).Sum(pair => pair.First * pair.Second);
    private static double[] Cross(double[] a, double[] b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    private static bool OrthonormalRightHanded(double[][] values)
    {
        const double tolerance = 1e-9;
        return values.All(value => value.Length == 3 && Math.Abs(Dot(value, value) - 1) <= tolerance) &&
            Math.Abs(Dot(values[0], values[1])) <= tolerance && Math.Abs(Dot(values[0], values[2])) <= tolerance && Math.Abs(Dot(values[1], values[2])) <= tolerance &&
            Cross(values[0], values[1]).Zip(values[2]).All(pair => Math.Abs(pair.First - pair.Second) <= tolerance);
    }

    private static EtabsSnapshotResult Rejected(string code, string path, string message, string remediation) =>
        Result(SnapshotOperationState.PreflightRejected, ExecutionState.RejectedInput, CompletenessState.Partial, FreshnessState.Unbound, code, path, message, remediation);
    private static EtabsSnapshotResult Blocked(string code, string path, string message, string remediation) =>
        Result(SnapshotOperationState.Fenced, ExecutionState.Completed, CompletenessState.Partial, FreshnessState.Current, code, path, message, remediation);
    private static EtabsSnapshotResult Uncertain(string code, string path, string message, string remediation) =>
        Result(SnapshotOperationState.TransactionUncertain, ExecutionState.NotRun, CompletenessState.Partial, FreshnessState.Unbound, code, path, message, remediation);

    private static EtabsSnapshotResult Result(SnapshotOperationState state, ExecutionState execution, CompletenessState completeness, FreshnessState freshness, string code, string path, string message, string remediation) =>
        new(
            "etabs.beam_snapshot.import-result/v1", Operation, state, execution,
            ApplicabilityState.Unknown, EngineeringState.NotEvaluated, completeness,
            freshness, ApprovalState.Unreviewed, null, null,
            [new(code, "error", path, message, remediation)], DefaultProvenance);

    private static void EnsureText(string json)
    {
        ArgumentNullException.ThrowIfNull(json);
        if (Encoding.UTF8.GetByteCount(json) > MaximumSnapshotBytes)
            throw new ArgumentException("Snapshot JSON exceeds the portable size limit.", nameof(json));
    }

    private static void EnsureNoDuplicateProperties(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in element.EnumerateObject())
            {
                if (!names.Add(property.Name)) throw new JsonException($"Duplicate JSON key: {property.Name}");
                EnsureNoDuplicateProperties(property.Value);
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
            foreach (var item in element.EnumerateArray()) EnsureNoDuplicateProperties(item);
    }

    private static string Canonical(JsonNode? node) => node switch
    {
        JsonObject obj => "{" + string.Join(",", obj.OrderBy(pair => pair.Key, StringComparer.Ordinal).Select(pair => CanonicalString(pair.Key) + ":" + Canonical(pair.Value))) + "}",
        JsonArray array => "[" + string.Join(",", array.Select(Canonical)) + "]",
        JsonValue value => CanonicalValue(value),
        _ => node?.ToJsonString(JsonOptions) ?? "null"
    };

    private static string CanonicalValue(JsonValue value)
    {
        if (value.TryGetValue<string>(out var text))
            return CanonicalString(text);
        if (value.TryGetValue<double>(out var number))
        {
            if (!double.IsFinite(number))
                throw new ArgumentException("Canonical snapshot numbers must be finite.", nameof(value));
            if (number == 0) return "0";
            if (Math.Truncate(number) == number && Math.Abs(number) <= 9_007_199_254_740_991)
                return number.ToString("0", CultureInfo.InvariantCulture);
            var token = number.ToString("R", CultureInfo.InvariantCulture).ToLowerInvariant();
            // Match the frozen Python/PF4 shortest-roundtrip representation.
            if (!token.Contains('e') && Math.Abs(number) >= 1e16)
            {
                var sign = token.StartsWith('-') ? "-" : "";
                var digits = token.TrimStart('-');
                var exponent = digits.Length - 1;
                var significant = digits.TrimEnd('0');
                token = sign + significant[0] + (significant.Length == 1 ? "" : "." + significant[1..]) + $"e+{exponent:D2}";
            }
            return token;
        }
        return value.ToJsonString(JsonOptions);
    }

    private static string CanonicalString(string value)
    {
        var builder = new StringBuilder(value.Length + 2).Append('"');
        for (var index = 0; index < value.Length; index++)
        {
            var character = value[index];
            switch (character)
            {
                case '"': builder.Append("\\\""); break;
                case '\\': builder.Append("\\\\"); break;
                case '\b': builder.Append("\\b"); break;
                case '\f': builder.Append("\\f"); break;
                case '\n': builder.Append("\\n"); break;
                case '\r': builder.Append("\\r"); break;
                case '\t': builder.Append("\\t"); break;
                default:
                    if (character < ' ')
                    {
                        builder.Append("\\u").Append(((int)character).ToString("x4", CultureInfo.InvariantCulture));
                    }
                    else if (char.IsHighSurrogate(character))
                    {
                        if (++index >= value.Length || !char.IsLowSurrogate(value[index]))
                            throw new ArgumentException("Canonical snapshot strings must contain valid Unicode scalar values.", nameof(value));
                        builder.Append(character).Append(value[index]);
                    }
                    else if (char.IsLowSurrogate(character))
                    {
                        throw new ArgumentException("Canonical snapshot strings must contain valid Unicode scalar values.", nameof(value));
                    }
                    else
                    {
                        builder.Append(character);
                    }
                    break;
            }
        }
        return builder.Append('"').ToString();
    }

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = false,
            WriteIndented = false,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
            RespectRequiredConstructorParameters = true
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower, allowIntegerValues: false));
        return options;
    }

    private static bool Text(string? value) => !string.IsNullOrWhiteSpace(value);
    private static bool Sha(string value) => value.Length == 64 && value.All(character => character is >= '0' and <= '9' or >= 'a' and <= 'f');
    private static bool Utc(string value) => value.EndsWith('Z') && DateTimeOffset.TryParse(value, out _);
    private static bool FinitePositive(double value) => double.IsFinite(value) && value > 0;
    private static bool FiniteNonnegative(double value) => double.IsFinite(value) && value >= 0;
    private static bool Finite(double value) => double.IsFinite(value);
    private static bool Finite(double? value) => !value.HasValue || double.IsFinite(value.Value);
    private static bool FiniteOptionalPositive(double? value) => !value.HasValue || FinitePositive(value.Value);
}
