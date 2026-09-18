using StructuralEngineering.Construction;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;

namespace StructuralEngineering.Beam;

public static class BeamReviewCostProjection
{
    public const string ExampleId = "illustrative-direct-cost-quantity-example/v1";

    public static BeamReviewCostEvidence? Project(BeamResolvedMember scenario, BeamInputLedger ledger,
        BeamCorePreviewResult? core, BeamReviewQuantityEvidence? evidence, bool allowExample)
    {
        ConstructionQuantityOutput quantity; string resultId; BeamReviewAvailability availability;
        if (evidence is not null && evidence.StructuralRevision == scenario.StructuralRevision &&
            BaselineEvidence.Qualified(evidence.Result) && evidence.Result.Outputs is { } measured &&
            core?.State == BaselineRunState.Complete && measured.MemberId == scenario.MemberId &&
            measured.DetailRevisionId == core.Design?.Arrangement.RevisionId)
        { quantity = measured; resultId = evidence.Result.ResultId; availability = BeamReviewAvailability.Available; }
        else if (allowExample)
        {
            // Explicit teaching quantities, not a generated BBS, measured takeoff, or estimate for this member.
            quantity = new(ExampleId, ExampleId, "example-only", ExampleId, "no-bbs-declared-teaching-quantities",
                "example-declared-net-volume", "example-declared-contact-area", [], [], [], new(0, 0, 0), 100, 100, 1, 3, 0);
            resultId = ResultFactory.SemanticId("declared_example_quantities", quantity);
            availability = BeamReviewAvailability.Example;
        }
        else return null;
        string Value(string key) => ledger.Fields.Single(x => x.SubjectId == scenario.MemberId && x.Key == key).Value;
        var rates = new MeasuredRateProfile("illustrative-review-rates", ResultFactory.SemanticId("review_rates", new
        { currency = Value("rates.currency"), steel = Value("rates.steel"), concrete = Value("rates.concrete"), formwork = Value("rates.formwork") }),
            Value("rates.currency"), "2026-09-05", "Asia/Calcutta", "Synthetic development example; no market geography",
            "Owner-authorized illustrative development preset; not a quotation",
            new([CostCategory.Material, CostCategory.Formwork], [CostCategory.Coupler, CostCategory.Labour, CostCategory.Plant]),
            [new("steel", CostCategory.Material, CostBasis.SteelScheduledMassKg, "scheduled reinforcement", Value("rates.steel"), "illustrative preset/edit"),
             new("concrete", CostCategory.Material, CostBasis.ConcreteVolumeM3, "net concrete", Value("rates.concrete"), "illustrative preset/edit"),
             new("formwork", CostCategory.Formwork, CostBasis.FormworkAreaM2, "contact formwork", Value("rates.formwork"), "illustrative preset/edit")],
            WastePricingBasis.ScheduledSteel, "0", "0");
        var cost = CostOperations.Estimate(new(quantity.ProfileId, quantity.ProjectBasisId, quantity.MemberId, quantity.DetailRevisionId,
            resultId, ResultFactory.SemanticId("output_payload_id", quantity), quantity, rates));
        return new(availability == BeamReviewAvailability.Example ? ExampleId : scenario.StructuralRevision, availability, quantity, cost);
    }
}
