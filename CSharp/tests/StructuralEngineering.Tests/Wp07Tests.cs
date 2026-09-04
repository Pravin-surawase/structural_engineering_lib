using StructuralEngineering.Construction;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reporting;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp07Tests
{
    [Fact]
    public void BbsAndQuantityReferenceFixtureReconciles()
    {
        var schedule = Schedule(Enumerable.Range(1, 4)
            .Select(index => StraightPath(
                $"BAR-{index}", "M1", 6000, sectionYMm: 40 + index * 20))
            .ToArray());
        var bbsResult = BbsOperations.Create(BbsRequest(schedule));

        Assert.Equal(EngineeringState.Pass, bbsResult.Engineering);
        Assert.Equal(59.18760559, bbsResult.Outputs!.ScheduledSteelMassKg, 8);

        var quantityResult = QuantityOperations.Calculate(QuantityRequest(
            bbsResult.Outputs,
            [new ConcreteNetSegment(
                "C1", "B1", "M25", "VOL-B1", 300 * 500, 6000, false)],
            [
                new FormworkContactFace("F-S", "B1", FormworkFaceCategory.Soffit,
                    "FACE-S", 300 * 6000, FormworkMeasurementState.Included),
                new FormworkContactFace("F-L", "B1", FormworkFaceCategory.SideLeft,
                    "FACE-L", 500 * 6000, FormworkMeasurementState.Included),
                new FormworkContactFace("F-R", "B1", FormworkFaceCategory.SideRight,
                    "FACE-R", 500 * 6000, FormworkMeasurementState.Included)
            ]));

        Assert.Equal(59.18760559,
            quantityResult.Outputs!.SteelScheduledMassKg, 8);
        Assert.Equal(0.9, quantityResult.Outputs.ConcreteVolumeM3, 12);
        Assert.Equal(7.8, quantityResult.Outputs.FormworkAreaM2, 12);
        Assert.Null(quantityResult.Outputs.DirectCost);
    }

    [Fact]
    public void BendCentrelineAndFabricationLengthAreExplicit()
    {
        const double diameter = 16;
        const double centrelineRadius = 40;
        var arc = centrelineRadius * Math.PI / 2;
        var segments = new[]
        {
            new ResolvedPathSegment(
                "B1:001", PathSegmentKind.TangentStraight,
                new PathPoint(0, 50, 50), new PathPoint(100, 50, 50), 100),
            new ResolvedPathSegment(
                "B1:002", PathSegmentKind.BendArc,
                new PathPoint(100, 50, 50), new PathPoint(100, 50, 150), arc,
                new PathPoint(60, 50, 90), centrelineRadius, 90,
                BendKind: BendKind.StandardBend),
            new ResolvedPathSegment(
                "B1:003", PathSegmentKind.TangentStraight,
                new PathPoint(100, 50, 150), new PathPoint(100, 50, 250), 100)
        };
        var path = new ResolvedBarPath(
            "B1", "M16", BarPathRole.TopLongitudinal, 1, diameter, 415, 1,
            false, ["N1", "N2", "N3"], segments, 200 + arc, 6000, [], []);

        var row = BbsOperations.Create(BbsRequest(Schedule(path))).Outputs!.Rows[0];

        Assert.Equal(62.83185307, row.Dimensions[1].CentrelineLengthMm, 8);
        Assert.Equal(200 + arc, row.CentrelineDevelopedLengthEachMm, 12);
        Assert.Equal(200 + arc, row.FabricationCutLengthEachMm, 12);
        Assert.Equal("bend_arc", row.Dimensions[1].SegmentKind);
    }

    [Fact]
    public void CuttingPlanSeparatesKerfOffcutAndWaste()
    {
        var schedule = Schedule(
            StraightPath("B1", "M1", 5000),
            StraightPath("B2", "M1", 5000, sectionYMm: 80));
        var request = BbsRequest(schedule) with
        {
            StockPolicy = new CuttingStockPolicy("P", "r1", [9000], 3, 500)
        };

        var output = BbsOperations.Create(request).Outputs!;

        Assert.Equal(2, output.StockPieces.Count);
        Assert.Equal(6, output.KerfLengthMm, 12);
        Assert.Equal(7994, output.ReusableOffcutLengthMm, 12);
        Assert.Equal(0, output.WasteLengthMm, 12);
        Assert.Equal(output.StockLengthMm,
            output.ScheduledCutLengthMm + output.KerfLengthMm +
            output.ReusableOffcutLengthMm + output.WasteLengthMm, 12);
        Assert.Equal("heuristic_first_fit_decreasing", output.AllocationOptimality);
    }

    [Fact]
    public void LinkZonesOwnEachBoundaryAndEveryPhysicalLink()
    {
        var paths = new[] { 0d, 100d, 200d }
            .Select(station => StraightPath(
                $"L-{station}", "L1", 200,
                stationXMm: station,
                diameterMm: 8,
                role: BarPathRole.TransverseLink))
            .ToArray();
        var zones = new[]
        {
            new LinkPlacementZone("Z1", "L1", 0, 100, 100, true, true),
            new LinkPlacementZone("Z2", "L1", 100, 200, 100, false, true)
        };
        var request = BbsRequest(Schedule(paths)) with { LinkZones = zones };

        var result = BbsOperations.Create(request);

        Assert.Equal(new[] { 0d, 100d }, result.Outputs!.LinkZones[0].StationsXMm);
        Assert.Equal(new[] { 200d }, result.Outputs.LinkZones[1].StationsXMm);

        var duplicate = BbsOperations.Create(request with
        {
            LinkZones = [zones[0], zones[1] with { IncludeStart = true }]
        });
        var missing = BbsOperations.Create(BbsRequest(Schedule(paths)));

        Assert.Equal("BBS.LINK_BOUNDARY_DUPLICATE", duplicate.Diagnostics[0].Code);
        Assert.Equal("BBS.LINK_ZONE_REQUIRED", missing.Diagnostics[0].Code);
    }

    [Fact]
    public void BbsRejectsDetachedPayloadAndInconsistentSummary()
    {
        var schedule = Schedule(
            StraightPath("B1", "M1", 6000),
            StraightPath("B2", "M1", 6000, sectionYMm: 80));

        var detached = BbsOperations.Create(BbsRequest(schedule) with
        {
            ScheduleOutputPayloadId = "output_payload_id:wrong"
        });
        var inconsistentSchedule = schedule with
        {
            Marks = [schedule.Marks[0] with { Count = 1 }]
        };
        var inconsistent = BbsOperations.Create(BbsRequest(inconsistentSchedule));

        Assert.Equal("BBS.SCHEDULE_BINDING", detached.Diagnostics[0].Code);
        Assert.Equal("BBS.SCHEDULE_RECONCILIATION",
            inconsistent.Diagnostics[0].Code);
    }

    [Fact]
    public void LapAndCouplerStaySeparateFromPathLength()
    {
        var path = StraightPath(
            "B1", "M1", 6000, spliceIds: ["S-LAP", "S-COUPLER"]);
        var request = BbsRequest(Schedule(path)) with
        {
            SpliceRecords =
            [
                new SpliceRecord(
                    "S-LAP", BbsSpliceKind.Lap, 2500, "lap-check-1"),
                new SpliceRecord(
                    "S-COUPLER", BbsSpliceKind.Coupler, 5000,
                    "coupler-cert-1", 1)
            ]
        };

        var output = BbsOperations.Create(request).Outputs!;

        Assert.Equal(6000, output.ScheduledCutLengthMm, 12);
        Assert.Equal(1, output.Couplers[0].Count);
        Assert.Equal(new[] { "S-COUPLER", "S-LAP" }, output.Rows[0].SpliceIds);
    }

    [Fact]
    public void QuantityRejectsDetachedBbsAndDuplicateOwnership()
    {
        var bbs = EmptyBbs();
        var request = QuantityRequest(
            bbs,
            [new ConcreteNetSegment(
                "C1", "B1", "M25", "OWN-1", 150000, 6000, false)],
            [new FormworkContactFace(
                "F1", "B1", FormworkFaceCategory.Soffit, "FACE-1", 1800000,
                FormworkMeasurementState.Included)]);

        var detached = QuantityOperations.Calculate(request with
        {
            BbsOutputPayloadId = "output_payload_id:wrong"
        });
        var duplicate = QuantityOperations.Calculate(request with
        {
            ConcreteSegments =
            [
                request.ConcreteSegments[0],
                request.ConcreteSegments[0] with { SegmentId = "C2" }
            ]
        });

        Assert.Equal("QUANTITY.BBS_BINDING", detached.Diagnostics[0].Code);
        Assert.Equal("QUANTITY.CONCRETE_OWNERSHIP", duplicate.Diagnostics[0].Code);
    }

    [Fact]
    public void DatedCostUsesItemizedDecimalArithmetic()
    {
        var quantities = QuantityOutput();
        var result = CostOperations.Estimate(CostRequest(quantities, RateProfile()));

        Assert.Equal("280.00", result.Outputs!.DirectSubtotalDecimal);
        Assert.Equal("28.00", result.Outputs.OverheadDecimal);
        Assert.Equal("308.00", result.Outputs.PreTaxTotalDecimal);
        Assert.Equal("55.44", result.Outputs.TaxDecimal);
        Assert.Equal("363.44", result.Outputs.TotalDecimal);
        Assert.All(result.Outputs.Lines, line =>
            Assert.Equal("quantity-result-1", line.SourceQuantityResultId));
    }

    [Fact]
    public void CostRejectsIdentityWasteAndInvalidDecimalFailures()
    {
        var quantities = QuantityOutput();
        var request = CostRequest(quantities, RateProfile());
        var missingIdentity = CostOperations.Estimate(request with
        {
            RateProfile = request.RateProfile with { Geography = "" }
        });
        var stockRate = request.RateProfile.Rates[0] with
        {
            Basis = CostBasis.SteelStockMassKg
        };
        var doubleWaste = CostOperations.Estimate(request with
        {
            RateProfile = request.RateProfile with
            {
                Rates = [stockRate, .. request.RateProfile.Rates.Skip(1)]
            }
        });
        var invalidDecimal = CostOperations.Estimate(request with
        {
            RateProfile = request.RateProfile with
            {
                Rates =
                [
                    request.RateProfile.Rates[0] with
                    {
                        UnitRateDecimal = "1e3"
                    },
                    .. request.RateProfile.Rates.Skip(1)
                ]
            }
        });
        var otherProjectQuantities = quantities with
        {
            ProjectBasisId = "other-project"
        };
        var crossProject = CostOperations.Estimate(request with
        {
            Quantities = otherProjectQuantities,
            QuantityOutputPayloadId = ResultFactory.SemanticId(
                "output_payload_id", otherProjectQuantities)
        });

        Assert.Equal("COST.IDENTITY", missingIdentity.Diagnostics[0].Code);
        Assert.Equal("COST.WASTE_DOUBLE_COUNT", doubleWaste.Diagnostics[0].Code);
        Assert.Equal("COST.RATE_INVALID", invalidDecimal.Diagnostics[0].Code);
        Assert.Equal("COST.QUANTITY_STALE", crossProject.Diagnostics[0].Code);
    }

    [Fact]
    public void DisplayedCostLinesReconcileAfterBankersRounding()
    {
        var quantities = QuantityOutput() with
        {
            SteelScheduledMassKg = 1,
            ConcreteVolumeM3 = 1,
            FormworkAreaM2 = 0
        };
        var profile = RateProfile() with
        {
            Scope = new HumanCostScope(
                [CostCategory.Material],
                [
                    CostCategory.Formwork,
                    CostCategory.Coupler,
                    CostCategory.Labour,
                    CostCategory.Plant
                ]),
            Rates =
            [
                new CostRate("a", CostCategory.Material,
                    CostBasis.SteelScheduledMassKg, "steel", "0.005", "rate-a"),
                new CostRate("b", CostCategory.Material,
                    CostBasis.ConcreteVolumeM3, "concrete", "0.005", "rate-b")
            ],
            OverheadPercentDecimal = "0",
            TaxPercentDecimal = "0"
        };

        var output = CostOperations.Estimate(CostRequest(quantities, profile)).Outputs!;

        Assert.Equal(new[] { "0.00", "0.00" },
            output.Lines.Select(item => item.AmountDecimal));
        Assert.Equal("0.00", output.DirectSubtotalDecimal);
    }

    [Fact]
    public void CalculationPackageIsReplayableAndRetainsHumanActions()
    {
        var result = CalculationPackageOperations.Create(PackageRequest());

        Assert.Equal(CompletenessState.CompleteForScope, result.Completeness);
        Assert.Equal("issue_ready", result.Outputs!.IssueState);
        Assert.False(result.Outputs.ActiveApproval);
        Assert.Equal("leaf-result-1", result.Outputs.Leaves[0].ResultId);
        Assert.Equal("PE-123", result.Outputs.HumanActions[0].ActorId);
        Assert.StartsWith(
            "calculation_package_id:pf4-canonical-json-v1:",
            result.Outputs.CalculationPackageId);
        Assert.Equal(
            new[] { "calculations", "drawings", "inputs", "quantities", "reinforcement", "signatures" },
            result.Outputs.RenderSections.Select(item => item.SectionId).Order());
    }

    [Fact]
    public void StalePackageRemainsDraftAndCannotActivateApproval()
    {
        var request = PackageRequest();
        var approved = request.HumanActions![0] with
        {
            Action = HumanActionKind.Approved
        };
        var result = CalculationPackageOperations.Create(request with
        {
            MemberBinding = request.MemberBinding with
            {
                Freshness = FreshnessState.Stale
            },
            HumanActions = [approved]
        });

        Assert.Equal(CompletenessState.Partial, result.Completeness);
        Assert.Equal(FreshnessState.Stale, result.Freshness);
        Assert.Equal("draft", result.Outputs!.IssueState);
        Assert.False(result.Outputs.ActiveApproval);
        Assert.Equal("PACKAGE.EVIDENCE_INCOMPLETE", result.Diagnostics[0].Code);
    }

    [Fact]
    public void PackageRejectsDetachedPayloadAndChangedTraceValues()
    {
        var request = PackageRequest();
        var detached = CalculationPackageOperations.Create(request with
        {
            MemberBinding = request.MemberBinding with
            {
                OutputPayloadId = "output_payload_id:wrong"
            }
        });
        var mismatched = CalculationPackageOperations.Create(request with
        {
            Traces = [request.Traces[0] with { ProvidedValue = 999 }]
        });

        Assert.Equal("PACKAGE.PAYLOAD_BINDING", detached.Diagnostics[0].Code);
        Assert.Equal("PACKAGE.TRACE_VALUE", mismatched.Diagnostics[0].Code);
    }

    [Fact]
    public void PackageRejectsCostFromAnotherProjectBasis()
    {
        var request = PackageRequest();
        var cost = new ConstructionCostOutput(
            "PROFILE-1",
            "other-project",
            "B1",
            "detail-r1",
            request.QuantityBinding.ResultId,
            "RATES-1",
            "rates-r1",
            "INR",
            "2026-09-04",
            "Pune, Maharashtra",
            "project quotation Q-17",
            [],
            [],
            Enum.GetValues<CostCategory>(),
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00");
        var result = CalculationPackageOperations.Create(request with
        {
            Cost = cost,
            CostBinding = Binding(
                "structural.construction_cost.estimate/v1", "cost-result-1", cost)
        });

        Assert.Equal("PACKAGE.IDENTITY_CONFLICT", result.Diagnostics[0].Code);
    }

    [Fact]
    public void ApprovalUsesAbsoluteTimeAndOnlyPassingBindingsAreCurrent()
    {
        var request = PackageRequest();
        var prepared = request.HumanActions![0] with
        {
            ActionId = "ACT-PREPARED",
            RecordedAtUtc = "2026-09-04T12:00:00+05:30"
        };
        var approved = prepared with
        {
            ActionId = "ACT-APPROVED",
            Action = HumanActionKind.Approved,
            RecordedAtUtc = "2026-09-04T07:00:00Z"
        };
        var current = CalculationPackageOperations.Create(request with
        {
            HumanActions = [prepared, approved]
        });
        var failedDependency = CalculationPackageOperations.Create(request with
        {
            BbsBinding = request.BbsBinding with
            {
                Engineering = EngineeringState.Fail
            },
            HumanActions = [approved]
        });

        Assert.True(current.Outputs!.ActiveApproval);
        Assert.Equal("draft", failedDependency.Outputs!.IssueState);
        Assert.False(failedDependency.Outputs.ActiveApproval);
    }

    private static MemberLocalCoordinateSystem Axes() => new(
        "B1-local",
        "member_station_x",
        "section_x_from_left",
        "section_y_from_top");

    private static ResolvedBarPath StraightPath(
        string barId,
        string mark,
        double lengthMm,
        double stationXMm = 0,
        double sectionYMm = 50,
        double diameterMm = 20,
        BarPathRole role = BarPathRole.TopLongitudinal,
        IReadOnlyList<string>? spliceIds = null)
    {
        var start = new PathPoint(stationXMm, 50, sectionYMm);
        var end = role == BarPathRole.TransverseLink
            ? new PathPoint(stationXMm, 50 + lengthMm, sectionYMm)
            : new PathPoint(stationXMm + lengthMm, 50, sectionYMm);
        return new ResolvedBarPath(
            barId,
            mark,
            role,
            1,
            diameterMm,
            415,
            1,
            false,
            [$"{barId}:N1", $"{barId}:N2"],
            [new ResolvedPathSegment(
                $"{barId}:001", PathSegmentKind.TangentStraight, start, end, lengthMm)],
            lengthMm,
            12000,
            [],
            spliceIds ?? []);
    }

    private static BarPathOutput Schedule(params ResolvedBarPath[] paths)
    {
        var marks = paths.GroupBy(item => item.BarMark)
            .OrderBy(group => group.Key, StringComparer.Ordinal)
            .Select(group =>
            {
                var items = group.ToArray();
                var first = items[0];
                return new BarMarkSummary(
                    group.Key,
                    first.Role,
                    first.DiameterMm,
                    first.SteelGradeNPerMm2,
                    first.BundleSize,
                    first.Closed,
                    items.Select(item => item.BarId).ToArray(),
                    items.Length,
                    first.DevelopedCentrelineLengthMm,
                    first.CompatibleStockLengthMm);
            }).ToArray();
        return new BarPathOutput(
            "PROFILE-1",
            "project-basis-1",
            "criteria-r1",
            "B1",
            "SPAN-1",
            "topology-r1",
            "detail-r1",
            Axes(),
            paths,
            marks,
            true);
    }

    private static BbsRequest BbsRequest(BarPathOutput schedule) => new(
        "PROFILE-1",
        "project-basis-1",
        "B1",
        "detail-r1",
        "schedule-result-1",
        ResultFactory.SemanticId("output_payload_id", schedule),
        schedule,
        new ShapeConvention("IS2502", "shape-r1"),
        new CuttingStockPolicy(
            "STOCK-POLICY", "cut-r1", [6000, 9000, 12000], 0, 500),
        7850);

    private static BbsOutput EmptyBbs() => new(
        "PROFILE-1",
        "project-basis-1",
        "B1",
        "detail-r1",
        "schedule-result-1",
        "shape-r1",
        "cut-r1",
        [],
        [],
        [],
        [],
        24000,
        24000,
        0,
        0,
        0,
        59.18760559,
        59.18760559,
        "heuristic_first_fit_decreasing",
        true);

    private static ConstructionQuantityRequest QuantityRequest(
        BbsOutput bbs,
        IReadOnlyList<ConcreteNetSegment> concrete,
        IReadOnlyList<FormworkContactFace> formwork) => new(
            "PROFILE-1",
            "project-basis-1",
            "B1",
            "detail-r1",
            "bbs-result-1",
            ResultFactory.SemanticId("output_payload_id", bbs),
            bbs,
            "beam-owns-net-prism-v1",
            "contact-face-v1",
            concrete,
            formwork);

    private static ConstructionQuantityOutput QuantityOutput() => new(
        "PROFILE-1",
        "project-basis-1",
        "B1",
        "detail-r1",
        "bbs-result-1",
        "concrete-policy-r1",
        "formwork-policy-r1",
        [],
        [],
        [],
        new WasteLedger(3, 500, 20),
        10,
        12,
        2,
        3,
        1);

    private static MeasuredRateProfile RateProfile() => new(
        "RATES-1",
        "rates-r1",
        "INR",
        "2026-09-04",
        "Asia/Calcutta",
        "Pune, Maharashtra",
        "project quotation set Q-17",
        new HumanCostScope(
            [CostCategory.Material, CostCategory.Formwork],
            [CostCategory.Coupler, CostCategory.Labour, CostCategory.Plant]),
        [
            new CostRate("steel", CostCategory.Material,
                CostBasis.SteelScheduledMassKg, "reinforcement", "5", "Q-17 steel"),
            new CostRate("concrete", CostCategory.Material,
                CostBasis.ConcreteVolumeM3, "M25 concrete", "100", "Q-17 concrete"),
            new CostRate("formwork", CostCategory.Formwork,
                CostBasis.FormworkAreaM2, "beam formwork", "10", "Q-17 formwork")
        ],
        WastePricingBasis.ScheduledSteel,
        "10",
        "18");

    private static ConstructionCostRequest CostRequest(
        ConstructionQuantityOutput quantities,
        MeasuredRateProfile profile) => new(
            "PROFILE-1",
            "project-basis-1",
            "B1",
            "detail-r1",
            "quantity-result-1",
            ResultFactory.SemanticId("output_payload_id", quantities),
            quantities,
            profile);

    private static ResultBinding Binding(
        string operation,
        string resultId,
        object payload,
        FreshnessState freshness = FreshnessState.Current) => new(
            operation,
            resultId,
            $"input:{resultId}",
            $"calculation:{resultId}",
            ExecutionState.Completed,
            ApplicabilityState.Applicable,
            EngineeringState.Pass,
            CompletenessState.CompleteForScope,
            freshness,
            ResultFactory.SemanticId("output_payload_id", payload));

    private static MemberDesignOutput MemberOutput()
    {
        var expectation = new MemberLeafExpectation(
            "flexure@B1",
            "flexure",
            "is456.beam.flexure.check/v1",
            "B1",
            CheckScope.Member,
            ApplicabilityState.Applicable,
            "is456-r1");
        var evidence = new MemberLeafEvidence(
            "flexure@B1",
            expectation.OperationSemanticId,
            "leaf-result-1",
            ExecutionState.Completed,
            ApplicabilityState.Applicable,
            EngineeringState.Pass,
            CompletenessState.CompleteForScope,
            FreshnessState.Current,
            "is456-r1",
            "flexure-r1",
            "input:leaf",
            "calculation:leaf",
            100,
            120,
            120,
            "kNm",
            0.8333333333,
            []);
        var iteration = new EffectiveDepthIteration(
            1, "reinforcement-r1", 450, [evidence.ResultId], true);
        return new MemberDesignOutput(
            "project-basis-1",
            "profile-r1",
            "B1",
            "topology-r1",
            "actions-r1",
            "reinforcement-r1",
            "scope-r1",
            [expectation],
            [new MemberLeafQualification(expectation, evidence, true, [])],
            [iteration],
            expectation.LeafId,
            evidence.ResultId,
            evidence.GoverningUtilization,
            true);
    }

    private static CalculationPackageRequest PackageRequest()
    {
        var schedule = Schedule(StraightPath("B1", "M1", 6000));
        var bbs = new BbsOutput(
            "PROFILE-1", "project-basis-1", "B1", "detail-r1",
            "schedule-result-1", "shape-r1", "cut-r1", [], [], [], [],
            6000, 6000, 0, 0, 0, 14.7969014, 14.7969014,
            "heuristic_first_fit_decreasing", true);
        var quantities = QuantityOutput();
        var member = MemberOutput();
        return new CalculationPackageRequest(
            new CalculationPackageMetadata(
                "PROJECT-1", "Office", "project-r1", "B1", "package-r1",
                "engine-1", ["is456-r1", "rebar-r1"],
                "2026-09-04T10:00:00+05:30"),
            new CalculationPackageProfile(
                "CALC-PROFILE", "calc-profile-r1", "beam-template-r1",
                ["flexure@B1"],
                [
                    "inputs", "calculations", "reinforcement", "quantities",
                    "drawings", "signatures"
                ]),
            member,
            Binding("is456.beam_member.design/v1", "member-result-1", member),
            schedule,
            Binding("structural.reinforcement_paths.resolve/v1",
                "schedule-result-1", schedule),
            bbs,
            Binding("structural.bbs.create/v1", "bbs-result-1", bbs),
            quantities,
            Binding("structural.construction_quantities.calculate/v1",
                "quantity-result-1", quantities),
            null,
            null,
            ["Loads are supplied at the stated design revision."],
            [new CalculationTrace(
                "TRACE-1", "flexure@B1", "IS456-flexure",
                "rectangular-flexure-v1", "Mu=100 kNm; capacity=120 kNm",
                100, 120, 120, "kNm", 0.8333333333, true)],
            [new DrawingView(
                "ELEV-1", "beam_elevation", "detail-r1",
                [new DrawingDatum("D1", "B1", "bar mark", "M1")])],
            ["Valid for the declared ordinary beam profile."],
            [new HumanAction(
                "ACT-1", "PE-123", "A. Engineer", "structural engineer",
                HumanActionKind.Prepared, "2026-09-04T10:30:00+05:30",
                "B1", "member-result-1")]);
    }
}
