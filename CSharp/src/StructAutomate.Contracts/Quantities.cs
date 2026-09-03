namespace StructAutomate.Contracts;

public sealed record ConcreteSegment(string Id, double NetAreaMm2, double PhysicalLengthMm);
public sealed record FormworkSegment(
    string Id, double PhysicalLengthMm, double SoffitContactWidthMm,
    double LeftContactHeightMm, double RightContactHeightMm,
    double EndBulkheadAreaMm2, double DeductionAreaMm2);
public sealed record QuantityRates(
    string Currency, DateOnly PriceDate, string Source, decimal SteelPerKg,
    decimal ConcretePerM3, decimal FormworkPerM2);
public sealed record QuantityRequest(
    string SchemaVersion, double SteelDensityKgPerM3, IReadOnlyList<BarPath> Bars,
    IReadOnlyList<ConcreteSegment> Concrete, IReadOnlyList<FormworkSegment> Formwork,
    QuantityRates? Rates = null);
public sealed record BarQuantity(string Mark, int Count, double CutLengthEachMm, double TotalLengthM, double SteelMassKg);
public sealed record DirectCost(string Currency, decimal Steel, decimal Concrete, decimal Formwork)
{
    public decimal Total => Steel + Concrete + Formwork;
}
public sealed record QuantityResult(
    IReadOnlyList<BarQuantity> Bars, double SteelMassKg, double ConcreteVolumeM3,
    double FormworkAreaM2, DirectCost? Cost);
