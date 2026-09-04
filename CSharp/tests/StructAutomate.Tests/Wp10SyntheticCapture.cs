using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

namespace StructAutomate.Tests;

// Entirely invented model and deterministic getter transcript; no installed host or private capture.
internal static class Wp10SyntheticCapture
{
    internal static EtabsNormalizationOptions Options => new("synthetic-project", "wp10-normalizer/v1",
        "synthetic-normalization-example/v1", new Dictionary<string, SnapshotMaterialClassification>
        { ["material"] = new("concrete", "synthetic-explicit-material-kind") });

    internal static EtabsDurableRawArtifact Create()
    {
        var start = DateTimeOffset.Parse("2026-09-01T00:00:00Z");
        var host = new EtabsHostIdentity(101, start.AddHours(-1), "synthetic.exe", "23.3.1.4563", 1, new('a', 64),
            "synthetic-api.dll", "synthetic", "2.16.0.0", new('b', 64), "synthetic.tlb", 1, new('c', 64),
            "synthetic.edb", 1, start.AddHours(-1), new('d', 64), "23.3.1", true, 6);
        var calls = new List<EtabsRawGetterCall>();
        void Add(string operation, object?[] inputs, object?[] outputs, object? direct = null)
        {
            var time = start.AddSeconds(calls.Count + 1);
            calls.Add(new(operation, inputs, direct, outputs,
                EtabsGetterMatrix.Allowed[operation].ReturnSemantics == EtabsReturnSemantics.DirectValue ? null : 0,
                time, time.AddMilliseconds(10), EtabsGetterMatrix.Sha256, host));
        }
        Add("SapModel.GetModelFilename", [true], [], host.ModelPath);
        Add("SapModel.GetModelIsLocked", [], [], true);
        Add("SapModel.GetPresentUnits", [], [], 6);
        Add("SapModel.GetDatabaseUnits", [], [], 6);
        Add("SapModel.GetPresentUnits_2", [], [4, 6, 2]);
        Add("SapModel.GetDatabaseUnits_2", [], [4, 6, 2]);
        Add("SapModel.GetVersion", [], ["23.3.1", 23.3]);
        Add("Story.GetStories_2", [], [0d, 1, new[] { "story" }, new[] { 3d }, new[] { 3d }, new[] { true }, new string?[] { null }, new[] { false }, new[] { 0d }, new[] { 0 }]);
        Add("FrameObj.GetNameList", [], [2, new[] { "beam", "catalog-only-frame" }]);
        Add("FrameObj.GetLabelFromName", ["beam"], ["B", "story"]);
        Add("FrameObj.GetPoints", ["beam"], ["pI", "pJ"]);
        Add("FrameObj.GetSection", ["beam"], ["section", ""]);
        Add("FrameObj.GetModifiers", ["beam"], [new[] { 1d, 1d, 1d, 1d, 0.8, 0.9, 1d, 1d }]);
        Add("FrameObj.GetEndLengthOffset", ["beam"], [true, 0.2, 0.3, 0d]);
        Add("FrameObj.GetInsertionPoint_1", ["beam"], [8, false, false, false, new double[3], new double[3], "Local"]);
        Add("FrameObj.GetReleases", ["beam"], [new bool[6], new[] { false, false, false, false, true, false }, new double[6], new double[6]]);
        Add("FrameObj.GetLocalAxes", ["beam"], [0d, false]);
        foreach (var name in new[] { "pI", "pJ" })
        {
            Add("PointObj.GetCoordCartesian", [name, "Global"], [1d, name == "pI" ? 2d : 6d, 3d]);
            Add("PointObj.GetLabelFromName", [name], [name, "story"]);
            Add("PointObj.GetRestraint", [name], [new[] { true, true, true, false, false, false }]);
            Add("PointObj.GetLocalAxes", [name], [0d, 0d, 0d, false]);
            Add("PointObj.GetTransformationMatrix", [name, true], [new[] { 1d, 0d, 0d, 0d, 1d, 0d, 0d, 0d, 1d }]);
        }
        Add("LineElm.GetObj", ["element"], ["beam", 0, 0d, 1d]);
        Add("LineElm.GetPoints", ["element"], ["pI", "pJ"]);
        Add("LineElm.GetLocalAxes", ["element"], [0d]);
        Add("LineElm.GetTransformationMatrix", ["element"], [new[] { 0d, 0d, 1d, 1d, 0d, 0d, 0d, 1d, 0d }]);
        Add("PropFrame.GetMaterial", ["section"], ["material"]);
        Add("PropFrame.GetRectangle", ["section"], ["", "material", 0.4, 0.2, 0, "synthetic section", "synthetic-section-guid"]);
        Add("PropFrame.GetSectProps", ["section"], [0.08, 0.066, 0.066, 0.00073, 0.0002666666666666667, 0.0010666666666666667, 0.0026, 0.0053, 0.004, 0.008, 0.057, 0.115]);
        Add("PropFrame.GetModifiers", ["section"], [new[] { 1d, 1d, 1d, 1d, 0.7, 0.6, 1d, 1d }]);
        Add("PropMaterial.GetMPIsotropic", ["material", 0d], [30000000d, 0.2, 0.00001, 12500000d]);
        Add("PropMaterial.GetWeightAndMass", ["material", 0d], [23.5, 2.4]);
        Add("LoadPatterns.GetNameList", [], [1, new[] { "pattern" }]);
        Add("LoadPatterns.GetLoadType", ["pattern"], [1]);
        Add("LoadPatterns.GetSelfWTMultiplier", ["pattern"], [1d]);
        Add("LoadCases.GetNameList", [0], [1, new[] { "case" }]);
        Add("LoadCases.GetTypeOAPI", ["case"], [1, 0]);
        Add("LoadCases.GetTypeOAPI_1", ["case"], [1, 0, 1, 0, 0]);
        Add("LoadCases.StaticLinear.GetInitialCase", ["case"], ["None"]);
        Add("LoadCases.StaticLinear.GetLoads", ["case"], [1, new[] { "Load" }, new[] { "pattern" }, new[] { 1d }]);
        Add("RespCombo.GetNameList", [], [1, new[] { "combo" }]);
        Add("RespCombo.GetTypeOAPI", ["combo"], [0]);
        Add("RespCombo.GetCaseList", ["combo"], [1, new[] { 0 }, new[] { "case" }, new[] { 1.5 }]);
        Add("Analyze.GetCaseStatus", [], [1, new[] { "case" }, new[] { 4 }]);
        Add("Analyze.GetRunCaseFlag", [], [1, new[] { "case" }, new[] { true }]);
        Add("Results.Setup.GetCaseSelectedForOutput", ["case"], [false]);
        Add("Results.Setup.GetComboSelectedForOutput", ["combo"], [true]);
        Add("Results.FrameForce", ["beam", 0], [3, new[] { "beam", "beam", "beam" }, new[] { 0.2, 2d, 3.7 },
            new[] { "element", "element", "element" }, new[] { 0.2, 2d, 3.7 }, new[] { "combo", "combo", "combo" },
            new[] { "Single Value", "Single Value", "Single Value" }, new double[3],
            new[] { -20d, -30d, -40d }, new[] { 10d, 2d, -11d }, new[] { -3d, 4d, -5d },
            new[] { 0.3, -0.4, 0.5 }, new[] { -1.5, 2.5, -3.5 }, new[] { 7d, -9d, 11d }]);
        var finish = start.AddSeconds(calls.Count + 3);
        var state = new EtabsProtectedState(new('e', 64), host.ModelPath, host.ModelBytes, host.ModelModifiedUtc, host.ModelSha256,
            true, 6, 6, host.EtabsApiVersion, ["case"], [4], [true], new Dictionary<string, bool> { ["case"] = false }, new Dictionary<string, bool> { ["combo"] = true });
        var capture = new EtabsLiveGetterProbeCapture("LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM", start, finish,
            EtabsGetterMatrix.Sha256, host, new("beam", "B", "story", [], ["combo"], 4, 0, finish.AddMinutes(1)),
            state, state, ["pI", "pJ"], ["element"], "section", "material", 3, calls);
        return Rebind(new("synthetic-acquisition", "etabs-process:101", start.AddSeconds(-1), finish.AddSeconds(1),
            EtabsGetterMatrix.Sha256, host, host, null!, capture, new(true, true, "win32-peekmessage/v1", "STA")));
    }

    internal static EtabsDurableRawArtifact Rebind(EtabsRawAcquisitionContent content)
    {
        var records = new List<SnapshotCallRecord>();
        string? previous = null;
        foreach (var call in content.Capture.Calls)
        {
            var id = $"{content.OperationId}:call:{records.Count / 2 + 1:D6}";
            foreach (var stage in new[] { SnapshotCallStage.Started, SnapshotCallStage.Returned })
            {
                var record = new SnapshotCallRecord("structural.analysis_call_record/v1", content.OperationId, id,
                    records.Count + 1, previous, stage, call.Operation, EtabsGetterMatrix.Sha256, SnapshotCallEffect.Getter,
                    AnalysisSnapshotNormalizer.Digest(call.Inputs), stage == SnapshotCallStage.Returned ? 0 : null,
                    stage == SnapshotCallStage.Returned ? "synthetic managed getter shape" : null, call.StartedUtc.ToString("O"), "");
                record = record with { RecordSha256 = AnalysisSnapshotCodec.CallRecordSha256(record) };
                previous = record.RecordSha256;
                records.Add(record);
            }
        }
        var ledger = new SnapshotCallLedger("structural.analysis_call_ledger/v1", content.OperationId, records.Count, previous, "", records);
        return EtabsAcquisitionArtifactCodec.Create(content with { CallLedger = ledger with { LedgerSha256 = AnalysisSnapshotCodec.CallLedgerSha256(ledger) } });
    }
}
