using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public static class EtabsOverviewProjector
{
    public static EtabsOverviewArtifact Project(byte[] inspectionBytes, string inspectionFileName, byte[] journalBytes,
        string journalFileName, string requestId, string requestSha, EtabsProcessTarget target)
    {
        var raw = JsonSerializer.Deserialize<EtabsInspectionArtifact>(inspectionBytes) ?? throw new InvalidDataException("Inspection is empty.");
        var capture = raw.Capture; var ledger = raw.Ledger;
        if (raw.SchemaVersion != "structural.etabs_inspection/v1" || raw.GetterMatrixSha256 != EtabsInspectionGetterMatrix.Sha256 ||
            capture.Scope != EtabsInspectionReader.OverviewScope || capture.SampleFrames.Count != 0 ||
            !raw.Cleanup.HostDisposed || !raw.Cleanup.LeaseReleased || raw.Cleanup.ApartmentState != "STA" ||
            ledger.OperationId != requestId || ledger.RecordCount != ledger.Records.Count || ledger.RecordCount == 0 || ledger.RecordCount % 2 != 0 ||
            ledger.LedgerSha256 != AnalysisSnapshotCodec.CallLedgerSha256(ledger) ||
            capture.Calls.Any(call => !Allowed.Contains(call.Operation) || call.GetterMatrixSha256 != raw.GetterMatrixSha256))
            throw new InvalidDataException("The source evidence is not a completed model overview.");
        var expectedJournal = System.Text.Encoding.UTF8.GetBytes(string.Concat(ledger.Records.Select(record =>
            System.Text.Encoding.UTF8.GetString(AnalysisSnapshotCodec.CanonicalJsonBytes(record)) + "\n")));
        if (!journalBytes.AsSpan().SequenceEqual(expectedJournal) || ledger.Records.Any(record => record.Effect != SnapshotCallEffect.Getter ||
            record.SignatureAuthoritySha256 != raw.GetterMatrixSha256 || record.RecordSha256 != AnalysisSnapshotCodec.CallRecordSha256(record)))
            throw new InvalidDataException("The overview journal differs from its retained evidence.");
        var source = raw.Source;
        var cases = Names("LoadCases.GetNameList", 1); var statuses = Output("Analyze.GetCaseStatus");
        var statusNames = Elements(statuses[1], statuses[0].GetInt32()).Select(value => value.GetString()!).ToArray();
        var statusValues = Elements(statuses[2], statuses[0].GetInt32()).Select(value => value.GetInt32()).ToArray();
        if (cases.Distinct(StringComparer.Ordinal).Count() != cases.Length || statusNames.Length != cases.Length ||
            statusNames.Distinct(StringComparer.Ordinal).Count() != statusNames.Length || !cases.ToHashSet(StringComparer.Ordinal).SetEquals(statusNames) ||
            statusValues.Length != statusNames.Length || statusValues.Any(value => value is < 1 or > 4))
            throw new InvalidDataException("Analysis case names and statuses disagree.");
        var designCode = Optional("DesignConcrete.GetCode"); var designAvailable = Optional("DesignConcrete.GetResultsAvailable");
        var identity = new EtabsContextSourceIdentity(source.ProcessId, source.ProcessStartedUtc, source.ExecutablePath, source.ExecutableSha256,
            source.ModelPath, source.ModelBytes, source.ModelModifiedUtc, source.ModelSha256, source.EtabsApiVersion,
            Direct("SapModel.GetModelIsLocked").GetBoolean(), Direct("SapModel.GetPresentUnits").GetInt32(), Direct("SapModel.GetDatabaseUnits").GetInt32());
        var overview = new EtabsModelOverview(requestSha, DateTimeOffset.UtcNow, identity,
            capture.FrameCount, capture.PointCount, capture.AreaCount, Output("Story.GetStories_2")[1].GetInt32(),
            cases.Length, statusValues.Count(value => value == 4), Names("RespCombo.GetNameList", 1).Length,
            designCode is null ? null : JsonSerializer.SerializeToElement(designCode.Outputs)[0].GetString(),
            designAvailable is null ? null : JsonSerializer.SerializeToElement(designAvailable.DirectValue).GetBoolean(),
            capture.Gaps.Select(gap => $"{gap.Operation}: {gap.Code}: {gap.Reason}").ToArray(),
            new(raw.GetterMatrixSha256, inspectionFileName, Sha(inspectionBytes), journalFileName, Sha(journalBytes), ledger.RecordCount / 2));
        var artifact = EtabsOverviewWorkerCodec.CreateArtifact(overview);
        return EtabsOverviewWorkerCodec.ParseAndValidateArtifact(EtabsOverviewWorkerCodec.CanonicalArtifactJsonBytes(artifact), target, requestSha);

        EtabsRawGetterCall? Optional(string name) => capture.Calls.FirstOrDefault(call => call.Operation == name);
        EtabsRawGetterCall Required(string name) => Optional(name) ?? throw new InvalidDataException($"Missing overview getter: {name}.");
        JsonElement Output(string name) => JsonSerializer.SerializeToElement(Required(name).Outputs);
        JsonElement Direct(string name) => JsonSerializer.SerializeToElement(Required(name).DirectValue);
        string[] Names(string name, int index)
        {
            var output = Output(name);
            return Elements(output[index], output[0].GetInt32()).Select(value => value.GetString()!).ToArray();
        }
    }

    private static IEnumerable<JsonElement> Elements(JsonElement value, int count) => count == 0 && value.ValueKind == JsonValueKind.Null
        ? [] : value.EnumerateArray();
    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private static readonly HashSet<string> Allowed = new(StringComparer.Ordinal)
    {
        "SapModel.GetModelFilename", "SapModel.GetModelIsLocked", "SapModel.GetPresentUnits", "SapModel.GetDatabaseUnits", "SapModel.GetVersion",
        "FrameObj.Count", "PointObj.Count", "AreaObj.Count", "Story.GetStories_2", "LoadPatterns.GetNameList", "LoadCases.GetNameList",
        "RespCombo.GetNameList", "Analyze.GetCaseStatus", "Analyze.GetRunCaseFlag", "DesignConcrete.GetCode", "DesignConcrete.GetResultsAvailable"
    };
}
