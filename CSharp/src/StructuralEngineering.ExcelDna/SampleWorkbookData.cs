using System.Text.Json;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.ExcelDna;

/// <summary>Deterministic ordinary-beam workbook used by the shipped sample and PERF-WORKBOOK.</summary>
public static class SampleWorkbookData
{
    public const int TypicalMemberCount = 20;
    public const int TypicalOperationRowCount = 200;

    public static IReadOnlyList<WorkbookTable> CreateTypicalTables(
        int memberCount = TypicalMemberCount,
        string workbookId = "standalone-beam-sample-r1")
    {
        if (memberCount is < 1 or > 1000)
            throw new ArgumentOutOfRangeException(nameof(memberCount));

        var projectRequest = ProjectRequest();
        var project = BeamProjectOperations.Create(projectRequest);
        if (project.Outputs is null)
            throw new InvalidOperationException("The embedded workbook project fixture is invalid.");

        var projectRows = new List<IReadOnlyList<WorkbookCell>>
        {
            Cells("template_id", "workbook_id", "project_id", "project_request_json"),
            Cells(WorkbookContract.TemplateId, workbookId, projectRequest.Project.ProjectId, Json(projectRequest))
        };
        var memberRows = new List<IReadOnlyList<WorkbookCell>>
        {
            Cells("member_id", "request_id", "member_design_seed_json", "bar_path_request_json",
                "bbs_seed_json", "quantity_seed_json", "cost_seed_json", "package_seed_json",
                "optimization_seed_json")
        };
        var operationRows = new List<IReadOnlyList<WorkbookCell>>
        {
            Cells("member_id", "request_id", "row_id", "phase", "operation_semantic_id",
                "request_json", "rule_id", "scope_id", "check_scope",
                "expected_applicability", "code_data_binding_id")
        };

        for (var index = 1; index <= memberCount; index++)
        {
            var memberId = $"B{index:000}";
            var requestId = $"{workbookId}:{memberId}:r1";
            var data = Member(project.Outputs, memberId);
            memberRows.Add(Cells(memberId, requestId, Json(data.MemberSeed), Json(data.Paths),
                Json(data.Bbs), Json(data.Quantities), Json(data.Cost), Json(data.Package),
                Json(data.Optimization)));
            foreach (var row in data.Rows)
                operationRows.Add(Cells(memberId, requestId, row.RowId,
                    row.TableId == "topology" ? "topology" : "leaf", row.OperationSemanticId,
                    row.RequestJson, row.RuleId, row.ScopeId,
                    row.Scope is null ? null : Snake(row.Scope.Value),
                    row.ExpectedApplicability is null ? null : Snake(row.ExpectedApplicability.Value),
                    row.CodeDataBindingId));
        }

        return
        [
            new WorkbookTable(WorkbookContract.ProjectTable, projectRows),
            new WorkbookTable(WorkbookContract.MembersTable, memberRows),
            new WorkbookTable(WorkbookContract.OperationsTable, operationRows)
        ];
    }

    private static BeamProjectRequest ProjectRequest()
    {
        var rules = new[]
        {
            Rule("flexure", "is456.beam.flexure.check/v1", CheckScope.Member, ApplicabilityState.Applicable, "is456-flexure"),
            Rule("shear", "is456.beam.shear.check/v1", CheckScope.Station, ApplicabilityState.Applicable, "is456-shear"),
            Rule("torsion", "is456.beam.torsion.check/v1", CheckScope.Station, ApplicabilityState.Applicable, "is456-shear"),
            Rule("deflection", "is456.beam.deflection.check/v1", CheckScope.Span, ApplicabilityState.Applicable, "is456-sls"),
            Rule("crack", "is456.beam.crack_width.check/v1", CheckScope.Station, ApplicabilityState.Applicable, "is456-sls"),
            Rule("anchorage", "is456.beam.anchorage.check/v1", CheckScope.BarEnd, ApplicabilityState.Applicable, "is456-detailing"),
            Rule("lap", "is456.beam.lap_curtailment.check/v1", CheckScope.Span, ApplicabilityState.Applicable, "is456-detailing"),
            Rule("seismic", "is456.beam.seismic_detailing.check/v1", CheckScope.Member, ApplicabilityState.NotApplicable, "is13920-detailing"),
            Rule("arrangement", "structural.reinforcement_arrangement.check/v1", CheckScope.Arrangement, ApplicabilityState.Applicable, "is456-detailing")
        };
        return new(
            new("SAMPLE-PROJECT", "Standalone ordinary RC beam design", "sample-project-r1"),
            new("mm", "N", "Nmm", "N/mm2"),
            [
                new("is456-flexure", "is456-wp01-v1", "IS 456 flexure data"),
                new("is456-shear", "is456-wp02-v1", "IS 456 shear and torsion data"),
                new("is456-sls", "is456-wp04-v1", "IS 456 serviceability data"),
                new("is456-detailing", "is456-amd6-wp05-v1", "IS 456 detailing data"),
                new("is13920-detailing", "is13920-2016-amd2-wp05-v1", "IS 13920 detailing data")
            ],
            new("ORDINARY-BEAM", "ordinary-beam-profile-r1", "IS 456:2000 with Amendment 6",
                SeismicDesignProfile.OrdinaryIs456, rules,
                [
                    new("nominal-cover", 25, "mm", "sample project durability basis"),
                    new("maximum-aggregate-size", 20, "mm", "sample project material basis")
                ]),
            [new("rebar", "sample-rebar-catalogue-r1", "Fe415 bars and 6/9/12 m stock")]);
    }

    private static DesignCheckRule Rule(string id, string operation, CheckScope scope,
        ApplicabilityState applicability, string binding) =>
        new(id, operation, scope, applicability, $"Sample {id} scope", binding);

    private static MemberData Member(BeamProject project, string memberId)
    {
        const string spanId = "SPAN-1";
        const string stationId = "S1";
        const string barEndId = "RIGHT";
        const string arrangementId = "MID";
        var topologyRevision = $"{memberId}-topology-r1";
        var actionRevision = $"{memberId}-actions-r1";
        var reinforcementRevision = $"{memberId}-reinforcement-r1";
        var scopeRevision = $"{memberId}-scope-r1";
        var detailRevision = $"{memberId}-detail-r1";
        var bars = Bars(memberId);
        var capacity = new FlexuralCapacityRequest("IS456-WP01", SectionKind.Rectangular,
            300, 500, 25, 415, bars, Face.Bottom);
        var link = new TransverseLink($"{memberId}-L8", 8, 2, 2, 150, 415, true, 242, 442);
        var longPaths = LongitudinalPaths(memberId);

        var topology = new BeamTopologyDefinitionRequest(memberId,
            new($"{memberId}-local", new(1, 0, 0), new(0, 1, 0), new(0, 0, 1)),
            [new("A", 0, -150, 150), new("B", 6000, 5850, 6150)],
            [new(spanId, "A", "B", 440, [new("REGION-1", "R300X500", 0, 6000)])],
            [new("E1", spanId, 0, 6000)]);
        var flexure = new FlexureCheckRequest(capacity, 80, -40);
        var shear = new ShearCheckRequest(
            [new("IS456-WP02", ShearAxis.V2, 300, 440, 25, 3 * Math.PI * 100, link)],
            [new(stationId, ShearAxis.V2, 80)]);
        var torsion = new TorsionCheckRequest("IS456-WP02",
            new($"{memberId}-ULS-S1", stationId, ActionBasis.StaticConcurrent,
                50, 0, 3, 0, 50, $"{actionRevision}:ULS"),
            capacity, link, [$"{memberId}-T1", $"{memberId}-T2", $"{memberId}-B1", $"{memberId}-B3"]);
        var deflection = new DeflectionCheckRequest("IS456-WP04",
            DeflectionMethod.CalculatedComponents,
            Calculated: new($"{memberId}-SLS-snapshot", [$"{memberId}-SLS-total"],
                [$"{memberId}-SLS-sustained"], $"{memberId}-analysis-SLS", reinforcementRevision,
                6000, 8, 5, 1.2, 1, 90, 4, 28, 1853, 1825, 60, 150,
                "effective-inertia:reviewed", "cracked-section:reviewed",
                "creep-factor:reviewed", "shrinkage-curvature:reviewed"),
            TotalLimit: new("IS456-WP04", 6000, DeflectionCriterion.TotalFinal),
            AfterFinishesLimit: new("IS456-WP04", 6000, DeflectionCriterion.AfterFinishes));
        var crack = new CrackWidthCheckRequest("IS456-WP04", memberId, stationId,
            $"{memberId}-SLS-service", reinforcementRevision, 300, 500, 200, Face.Bottom,
            bars.Where(bar => bar.Face == Face.Bottom).ToArray(), 150, 200, 415, 200_000,
            .0006, new("IS456-WP04", ExposureClass.Mild, false));
        var development = new DevelopmentLengthRequest("IS456-WP05", 20, .87 * 415,
            415, 25, BarSurface.Deformed, StressState.Tension);
        var anchorage = new AnchorageCheckRequest("IS456-WP05", memberId,
            reinforcementRevision,
            [new($"{memberId}-B1", "right-face", AnchorageLocation.SimpleSupport,
                AnchorageDirection.IncreasingX, 0, 6000, 5800, "B", 5800, 5900,
                [], null, development, new(85_000_000, 100_000, [$"{memberId}-ULS-right"]))]);
        var lap = new LapCurtailmentCheckRequest("IS456-WP05", memberId, spanId,
            actionRevision, reinforcementRevision, 0, 6000, 440, 25, 415,
            BarSurface.Deformed, longPaths,
            [new(stationId, 3000, ReinforcementRole.BottomLongitudinal, 600, 80_000, 120_000, $"{memberId}-ULS-S1")],
            [new("SP-1", SpliceKind.Lap, [$"{memberId}-B1", $"{memberId}-B2"],
                2500, 3500, StressState.Tension, false, 50, "STAGGER-A")], []);
        var seismic = new SeismicDetailingCheckRequest("IS456-WP05",
            SeismicApplicability.OrdinaryIs456);
        var arrangement = new ReinforcementArrangementCheckRequest("IS456-WP05",
            memberId, arrangementId, reinforcementRevision, 300, 500, 25, 20,
            longPaths, [new($"{memberId}-L8", 8, 29, 271, 29, 471, 16, true)],
            [ReinforcementRole.TopLongitudinal, ReinforcementRole.BottomLongitudinal],
            10, PlacementOpening: new("PO-1", 260, 460, $"{memberId}-placement-r1"),
            RequirePlacementPlan: true);

        var rows = new[]
        {
            new WorkbookOperationRow("topology", "structural.beam_topology.define/v1", Json(topology), "topology"),
            Leaf("flexure", flexure, "is456.beam.flexure.check/v1", memberId, CheckScope.Member, ApplicabilityState.Applicable, "is456-flexure"),
            Leaf("shear", shear, "is456.beam.shear.check/v1", stationId, CheckScope.Station, ApplicabilityState.Applicable, "is456-shear"),
            Leaf("torsion", torsion, "is456.beam.torsion.check/v1", stationId, CheckScope.Station, ApplicabilityState.Applicable, "is456-shear"),
            Leaf("deflection", deflection, "is456.beam.deflection.check/v1", spanId, CheckScope.Span, ApplicabilityState.Applicable, "is456-sls"),
            Leaf("crack", crack, "is456.beam.crack_width.check/v1", stationId, CheckScope.Station, ApplicabilityState.Applicable, "is456-sls"),
            Leaf("anchorage", anchorage, "is456.beam.anchorage.check/v1", barEndId, CheckScope.BarEnd, ApplicabilityState.Applicable, "is456-detailing"),
            Leaf("lap", lap, "is456.beam.lap_curtailment.check/v1", spanId, CheckScope.Span, ApplicabilityState.Applicable, "is456-detailing"),
            Leaf("seismic", seismic, "is456.beam.seismic_detailing.check/v1", memberId, CheckScope.Member, ApplicabilityState.NotApplicable, "is13920-detailing"),
            Leaf("arrangement", arrangement, "structural.reinforcement_arrangement.check/v1", arrangementId, CheckScope.Arrangement, ApplicabilityState.Applicable, "is456-detailing")
        };

        var memberSeed = new WorkbookMemberDesignSeed(memberId, topologyRevision,
            actionRevision, reinforcementRevision, scopeRevision,
            [new(stationId, CheckScope.Station, scopeRevision),
             new(spanId, CheckScope.Span, scopeRevision),
             new(barEndId, CheckScope.BarEnd, scopeRevision),
             new(arrangementId, CheckScope.Arrangement, scopeRevision)],
            [new(1, reinforcementRevision, 440, true)]);
        var paths = new WorkbookBarPathSeed("ORDINARY-BEAM", project.ProjectBasisId,
            "sample-detail-criteria-r1", memberId, spanId, topologyRevision,
            detailRevision, new($"{memberId}-local", "member_station_x",
                "section_x_from_left", "section_y_from_top"), 0, 6000, 300, 500,
            PathSeeds(memberId).Where(path => path.Role != BarPathRole.TransverseLink).ToArray(),
            new("L8", 1, 8, 415, 0, 6000, 150, 29, 271, 29, 471, 16),
            [6000, 9000, 12000]);
        var bbs = new WorkbookBbsSeed("ORDINARY-BEAM", project.ProjectBasisId,
            memberId, detailRevision, new("IS2502", "sample-shape-r1"),
            new("SAMPLE-STOCK", "sample-stock-r1", [6000, 9000, 12000], 3, 500),
            7850, [new("SP-1", BbsSpliceKind.Lap, 3000, "is456.beam.lap_curtailment.check/v1")],
            [new("LINK-ZONE-1", "L8", 0, 6000, 150, true, true)]);
        var quantities = new WorkbookQuantitySeed("ORDINARY-BEAM", project.ProjectBasisId,
            memberId, detailRevision, "beam-net-prism-v1", "contact-face-v1",
            [new("CONCRETE-1", memberId, "M25", $"{memberId}-concrete", 150_000, 6000, false)],
            [new("SOFFIT", memberId, FormworkFaceCategory.Soffit, $"{memberId}-soffit", 1_800_000, FormworkMeasurementState.Included),
             new("SIDE-L", memberId, FormworkFaceCategory.SideLeft, $"{memberId}-side-left", 3_000_000, FormworkMeasurementState.Included),
             new("SIDE-R", memberId, FormworkFaceCategory.SideRight, $"{memberId}-side-right", 3_000_000, FormworkMeasurementState.Included)]);
        var cost = new WorkbookCostSeed("ORDINARY-BEAM", project.ProjectBasisId,
            memberId, detailRevision, RateProfile());
        var leafIds = rows.Where(row => row.TableId == "leaf")
            .Select(row => $"{row.RuleId}@{row.ScopeId}").ToArray();
        var package = new WorkbookCalculationPackageSeed(
            new("SAMPLE-PROJECT", "Standalone ordinary RC beam design", "sample-project-r1",
                memberId, $"{memberId}-package-r1", "StructuralEngineering.ExcelDna/0.1.0",
                ["is456-wp01-v1", "is456-wp02-v1", "is456-wp04-v1",
                 "is456-amd6-wp05-v1", "is13920-2016-amd2-wp05-v1"],
                "2026-09-04T00:00:00Z"),
            new("SAMPLE-CALC-PACKAGE", "sample-package-profile-r1",
                "beam-calculation-package-r1", leafIds,
                ["inputs", "calculations", "reinforcement", "quantities", "cost", "drawings", "signatures"]),
            ["Actions are explicit sample design values in the stated local axes.",
             "Costs are illustrative dated rates and are not a quotation."],
            leafIds.Select((leafId, traceIndex) => new WorkbookCalculationTraceSeed(
                $"TRACE-{traceIndex + 1:00}", leafId, leafId.Split('@')[0],
                "native-operation-result/v1", "See the immutable operation request and result identity.")).ToArray(),
            [new($"{memberId}-ELEV", "beam_elevation", detailRevision,
                [new($"{memberId}-D1", memberId, "span", "6000", "mm"),
                 new($"{memberId}-D2", $"{memberId}-B1", "bottom bar mark", "B20")])],
            ["Ordinary rectangular single-span beam example; independent project review remains required."]);
        var domain = new DiscreteCandidateDomain($"{memberId}-domain", "sample-domain-r1",
            project.ProjectBasisId, project.Profile.RevisionId, memberId, topologyRevision,
            actionRevision, scopeRevision, $"{memberId}-analysis-r1", "R300X500",
            [new("R300X500", 300, 500, 25)],
            [new("L2T3B", 2, 16, 1, 3, 20, 1, 415)],
            [new("L8-150", 8, 415, 2, 150)], 1,
            ["Current sample beam detail"], ["Fixed action evaluation only."]);
        var optimization = new WorkbookOptimizationSeed($"{memberId}-search-r1", domain,
            new("COST-THEN-MASS", "sample-objective-r1",
                [CandidateObjectiveKind.Cost, CandidateObjectiveKind.SteelMass],
                [CandidateTieBreaker.LowerUtilization, CandidateTieBreaker.FewerBarMarks,
                 CandidateTieBreaker.LowerSectionDepth, CandidateTieBreaker.CandidateId]), 1);
        return new(memberSeed, paths, bbs, quantities, cost, package, optimization, rows);
    }

    private static WorkbookOperationRow Leaf<T>(string ruleId, T request, string operation,
        string scopeId, CheckScope scope, ApplicabilityState applicability, string binding) =>
        new(ruleId, operation, Json(request), "leaf", ruleId, scopeId, scope, applicability, binding);

    private static BarCoordinate[] Bars(string memberId) =>
    [
        new($"{memberId}-T1", 16, 60, 60, Face.Top),
        new($"{memberId}-T2", 16, 240, 60, Face.Top),
        new($"{memberId}-B1", 20, 60, 440, Face.Bottom),
        new($"{memberId}-B2", 20, 150, 440, Face.Bottom),
        new($"{memberId}-B3", 20, 240, 440, Face.Bottom)
    ];

    private static LongitudinalBarPath[] LongitudinalPaths(string memberId) =>
    [
        LongPath(memberId, "T1", "T16", ReinforcementRole.TopLongitudinal, 16, 60, 60),
        LongPath(memberId, "T2", "T16", ReinforcementRole.TopLongitudinal, 16, 240, 60),
        LongPath(memberId, "B1", "B20", ReinforcementRole.BottomLongitudinal, 20, 60, 440),
        LongPath(memberId, "B2", "B20", ReinforcementRole.BottomLongitudinal, 20, 150, 440),
        LongPath(memberId, "B3", "B20", ReinforcementRole.BottomLongitudinal, 20, 240, 440)
    ];

    private static LongitudinalBarPath LongPath(string memberId, string suffix, string mark,
        ReinforcementRole role, double diameter, double x, double y) =>
        new($"{memberId}-{suffix}", mark, role, diameter, 1, x, y, 0, 6000, .87 * 415);

    private static IReadOnlyList<BarPathSeed> PathSeeds(string memberId)
    {
        var seeds = LongitudinalPaths(memberId).Select(path => new BarPathSeed(path.BarId,
            path.BarMark, path.Role == ReinforcementRole.TopLongitudinal
                ? BarPathRole.TopLongitudinal : BarPathRole.BottomLongitudinal,
            path.Layer, path.DiameterMm, 415,
            [new($"{path.BarId}-1", new(0, path.XFromLeftMm, path.YFromTopMm)),
             new($"{path.BarId}-2", new(6000, path.XFromLeftMm, path.YFromTopMm))],
            SpliceIds: path.BarId.EndsWith("-B1", StringComparison.Ordinal) ||
                       path.BarId.EndsWith("-B2", StringComparison.Ordinal) ? ["SP-1"] : [])).ToList();
        for (var station = 0; station <= 6000; station += 150)
        {
            var id = $"{memberId}-L{station:0000}";
            seeds.Add(new(id, "L8", BarPathRole.TransverseLink, 1, 8, 415,
                [new($"{id}-1", new(station, 29, 29), 16, BendKind.StandardBend),
                 new($"{id}-2", new(station, 271, 29), 16, BendKind.StandardBend),
                 new($"{id}-3", new(station, 271, 471), 16, BendKind.StandardBend),
                 new($"{id}-4", new(station, 29, 471), 16, BendKind.StandardBend)], Closed: true));
        }
        return seeds;
    }

    private static MeasuredRateProfile RateProfile() => new("SAMPLE-RATES", "sample-rates-r1",
        "INR", "2026-09-04", "Asia/Calcutta", "Pune, Maharashtra",
        "Illustrative sample rates",
        new([CostCategory.Material, CostCategory.Formwork],
            [CostCategory.Coupler, CostCategory.Labour, CostCategory.Plant]),
        [new("steel", CostCategory.Material, CostBasis.SteelScheduledMassKg, "reinforcement", "70", "sample steel rate"),
         new("concrete", CostCategory.Material, CostBasis.ConcreteVolumeM3, "M25 concrete", "7500", "sample concrete rate"),
         new("formwork", CostCategory.Formwork, CostBasis.FormworkAreaM2, "beam formwork", "900", "sample formwork rate")],
        WastePricingBasis.ScheduledSteel, "10", "18");

    private static string Json<T>(T value) => JsonSerializer.Serialize(value, WorkbookContract.Json);

    private static string Snake<T>(T value) where T : struct, Enum =>
        JsonSerializer.Serialize(value, WorkbookContract.Json).Trim('"');

    private static IReadOnlyList<WorkbookCell> Cells(params string?[] values) =>
        values.Select(value => new WorkbookCell(value)).ToArray();

    private sealed record MemberData(WorkbookMemberDesignSeed MemberSeed, WorkbookBarPathSeed Paths,
        WorkbookBbsSeed Bbs, WorkbookQuantitySeed Quantities, WorkbookCostSeed Cost,
        WorkbookCalculationPackageSeed Package, WorkbookOptimizationSeed Optimization,
        IReadOnlyList<WorkbookOperationRow> Rows);
}
