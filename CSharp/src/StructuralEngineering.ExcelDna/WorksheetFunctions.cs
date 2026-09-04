using ExcelDna.Integration;
using StructuralEngineering.Analysis;
using StructuralEngineering.Beam;
using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Construction;
using StructuralEngineering.Contracts;
using StructuralEngineering.Reinforcement;

namespace StructuralEngineering.ExcelDna;

/// <summary>Pure Excel-DNA projections over immutable native operation requests.</summary>
public static class WorksheetFunctions
{
    private const string ProfileId = "excel_udf";

    [ExcelFunction(Name = "STR.INFO.VERSION", Description = "StructuralEngineering Excel-DNA adapter version.", IsThreadSafe = true)]
    public static string InfoVersion() => "StructuralEngineering.ExcelDna 0.1.0";

    [ExcelFunction(Name = "STR.INFO.REVISIONS", Description = "Adapter and result-contract revisions.", IsThreadSafe = true)]
    public static object InfoRevisions() => ResultSpill.From(new
    {
        adapter_version = "0.1.0",
        result_schema_version = "structural-operation-result/v1",
        canonicalization_version = "pf4-canonical-json-v1"
    });

    [ExcelFunction(Name = "STR.REBAR.AREA", Description = "Bar area projection from a diameter in mm.", IsThreadSafe = true)]
    public static object RebarArea(object diameterMm) => RunScalar(
        () => ReinforcementOperations.BarArea(new(ProfileId, StrictJson.Number(diameterMm, "diameter_mm"))),
        output => output.Value);

    [ExcelFunction(Name = "STR.REBAR.AREA.RESULT", Description = "Bar area result envelope with identity, states and provenance.", IsThreadSafe = true)]
    public static object RebarAreaResult(object diameterMm) => Run(() =>
        ReinforcementOperations.BarArea(new(ProfileId, StrictJson.Number(diameterMm, "diameter_mm"))));

    [ExcelFunction(Name = "STR.REBAR.MASS_PER_LENGTH", Description = "Bar mass-per-length projection from diameter mm and density kg/m³.", IsThreadSafe = true)]
    public static object RebarMassPerLength(object diameterMm, object densityKgPerM3) => RunScalar(
        () => ReinforcementOperations.MassPerLength(new(ProfileId,
            StrictJson.Number(diameterMm, "diameter_mm"),
            StrictJson.Number(densityKgPerM3, "density_kg_per_m3"))), output => output.Value);

    [ExcelFunction(Name = "STR.REBAR.MASS_PER_LENGTH.RESULT", Description = "Bar mass-per-length result envelope with identity, states and provenance.", IsThreadSafe = true)]
    public static object RebarMassPerLengthResult(object diameterMm, object densityKgPerM3) => Run(() =>
        ReinforcementOperations.MassPerLength(new(ProfileId,
            StrictJson.Number(diameterMm, "diameter_mm"),
            StrictJson.Number(densityKgPerM3, "density_kg_per_m3"))));

    [ExcelFunction(Name = "STR.REBAR.GEOMETRY", Description = "Reinforcement geometry from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object RebarGeometry(object requestJson) => Project<GeometryRequest, GeometryOutput>(requestJson, ReinforcementOperations.EvaluateGeometry);

    [ExcelFunction(Name = "STR.IS456.FLEXURE.CHECK", Description = "IS 456 flexure check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object FlexureCheck(object requestJson) => Project<FlexureCheckRequest, FlexureCheckOutput>(requestJson, BeamOperations.CheckFlexure);

    [ExcelFunction(Name = "STR.IS456.SHEAR.CHECK", Description = "IS 456 shear check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object ShearCheck(object requestJson) => Project<ShearCheckRequest, ShearCheckOutput>(requestJson, BeamOperations.CheckShear);

    [ExcelFunction(Name = "STR.IS456.TORSION.CHECK", Description = "IS 456 torsion check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object TorsionCheck(object requestJson) => Project<TorsionCheckRequest, TorsionCheckOutput>(requestJson, BeamOperations.CheckTorsion);

    [ExcelFunction(Name = "STR.IS456.SLS.DEFLECTION", Description = "IS 456 deflection check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object DeflectionCheck(object requestJson) => Project<DeflectionCheckRequest, DeflectionCheckOutput>(requestJson, Serviceability.CheckDeflection);

    [ExcelFunction(Name = "STR.IS456.SLS.CRACK_WIDTH", Description = "IS 456 crack-width check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object CrackWidthCheck(object requestJson) => Project<CrackWidthCheckRequest, CrackWidthCheckOutput>(requestJson, Serviceability.CheckCrackWidth);

    [ExcelFunction(Name = "STR.IS456.DETAIL.DEVELOPMENT_LENGTH", Description = "IS 456 development length from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object DevelopmentLength(object requestJson) => Project<DevelopmentLengthRequest, DevelopmentLengthOutput>(requestJson, Detailing.DevelopmentLength);

    [ExcelFunction(Name = "STR.IS456.DETAIL.ANCHORAGE", Description = "IS 456 anchorage check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object Anchorage(object requestJson) => Project<AnchorageCheckRequest, AnchorageCheckOutput>(requestJson, Detailing.CheckAnchorage);

    [ExcelFunction(Name = "STR.IS456.DETAIL.LAP_CURTAILMENT", Description = "IS 456 lap and curtailment check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object LapCurtailment(object requestJson) => Project<LapCurtailmentCheckRequest, LapCurtailmentCheckOutput>(requestJson, Detailing.CheckLapsAndCurtailment);

    [ExcelFunction(Name = "STR.IS456.DETAIL.SEISMIC", Description = "IS 13920 seismic detailing check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object SeismicDetailing(object requestJson) => Project<SeismicDetailingCheckRequest, SeismicDetailingCheckOutput>(requestJson, Detailing.CheckSeismicDetailing);

    [ExcelFunction(Name = "STR.REBAR.ARRANGEMENT", Description = "Reinforcement arrangement check from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object Arrangement(object requestJson) => Project<ReinforcementArrangementCheckRequest, ReinforcementArrangementCheckOutput>(requestJson, Detailing.CheckReinforcementArrangement);

    [ExcelFunction(Name = "STR.BEAM.LINE.SOLVE", Description = "Bounded beam-line solve from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object BeamLineSolve(object requestJson) => Project<BeamLineRequest, BeamLineOutput>(requestJson, PlanarBeamSolver.SolveBeamLine);

    [ExcelFunction(Name = "STR.CONSTRUCTION.BBS", Description = "Bar bending schedule from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object Bbs(object requestJson) => Project<BbsRequest, BbsOutput>(requestJson, BbsOperations.Create);

    [ExcelFunction(Name = "STR.CONSTRUCTION.QUANTITIES", Description = "Construction quantities from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object Quantities(object requestJson) => Project<ConstructionQuantityRequest, ConstructionQuantityOutput>(requestJson, QuantityOperations.Calculate);

    [ExcelFunction(Name = "STR.CONSTRUCTION.COST", Description = "Construction cost from a strict snake_case JSON request.", IsThreadSafe = true)]
    public static object Cost(object requestJson) => Project<ConstructionCostRequest, ConstructionCostOutput>(requestJson, CostOperations.Estimate);

    private static object Project<TRequest, TOutput>(object requestJson, Func<TRequest, ResultEnvelope<TOutput>> operation) =>
        Run(() => operation(StrictJson.Deserialize<TRequest>(requestJson)));

    private static object Run<TOutput>(Func<ResultEnvelope<TOutput>> operation)
    {
        try
        {
            return ResultSpill.From(operation());
        }
        catch (WorksheetInputException exception)
        {
            return ResultSpill.Diagnostic(exception.Code, exception.Message);
        }
        catch (ArgumentException exception)
        {
            return ResultSpill.Diagnostic("INPUT.INVALID", exception.Message);
        }
        catch (NotSupportedException exception)
        {
            return ResultSpill.Diagnostic("INPUT.UNSUPPORTED", exception.Message);
        }
    }

    private static object RunScalar<TOutput>(Func<ResultEnvelope<TOutput>> operation, Func<TOutput, double> select)
    {
        try
        {
            var result = operation();
            return result.Outputs is null ? ResultSpill.From(result) : select(result.Outputs);
        }
        catch (WorksheetInputException exception)
        {
            return ResultSpill.Diagnostic(exception.Code, exception.Message);
        }
        catch (ArgumentException exception)
        {
            return ResultSpill.Diagnostic("INPUT.INVALID", exception.Message);
        }
        catch (NotSupportedException exception)
        {
            return ResultSpill.Diagnostic("INPUT.UNSUPPORTED", exception.Message);
        }
    }
}
