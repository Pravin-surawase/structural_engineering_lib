using StructAutomate.Contracts;

namespace StructAutomate.Engineering;

public static class QuantityCalculator
{
    public static QuantityResult Calculate(QuantityRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        Require.Version(request.SchemaVersion);
        Require.Positive(request.SteelDensityKgPerM3, "steelDensityKgPerM3");
        ArgumentNullException.ThrowIfNull(request.Bars);
        ArgumentNullException.ThrowIfNull(request.Concrete);
        ArgumentNullException.ThrowIfNull(request.Formwork);
        Require.Unique(request.Bars.Select(b => b.Mark), "bars.mark");
        Require.Unique(request.Concrete.Select(s => s.Id), "concrete.id");
        Require.Unique(request.Formwork.Select(s => s.Id), "formwork.id");
        var bars = new List<BarQuantity>();
        foreach (var bar in request.Bars)
        {
            Require.Positive(bar.DiameterMm, $"bars.{bar.Mark}.diameterMm");
            Require.That(bar.Count > 0, $"bars.{bar.Mark}.count", "Bar count must be positive.");
            ArgumentNullException.ThrowIfNull(bar.Straights);
            ArgumentNullException.ThrowIfNull(bar.Bends);
            double length = 0;
            foreach (var piece in bar.Straights)
            {
                Require.Text(piece.Purpose, $"bars.{bar.Mark}.straights.purpose");
                Require.Positive(piece.TangentLengthMm, $"bars.{bar.Mark}.straights.tangentLengthMm");
                length += piece.TangentLengthMm;
            }
            foreach (var bend in bar.Bends)
            {
                Require.Text(bend.Purpose, $"bars.{bar.Mark}.bends.purpose");
                Require.Positive(bend.InternalRadiusMm, $"bars.{bar.Mark}.bends.internalRadiusMm");
                Require.Positive(bend.AngleDegrees, $"bars.{bar.Mark}.bends.angleDegrees");
                Require.That(bend.AngleDegrees <= 360, $"bars.{bar.Mark}.bends.angleDegrees", "A bend arc cannot exceed 360 degrees.");
                length += bend.AngleDegrees * Math.PI / 180 * (bend.InternalRadiusMm + bar.DiameterMm / 2);
            }
            Require.Positive(length, $"bars.{bar.Mark}.cutLengthMm");
            double totalLengthM = length * bar.Count / 1000;
            double mass = Math.PI / 4 * bar.DiameterMm * bar.DiameterMm * totalLengthM / 1e6 * request.SteelDensityKgPerM3;
            Require.Finite(mass, $"bars.{bar.Mark}.massKg");
            bars.Add(new(bar.Mark, bar.Count, length, totalLengthM, mass));
        }
        double volume = 0, formwork = 0;
        foreach (var segment in request.Concrete)
        {
            Require.Positive(segment.NetAreaMm2, $"concrete.{segment.Id}.netAreaMm2");
            Require.Positive(segment.PhysicalLengthMm, $"concrete.{segment.Id}.physicalLengthMm");
            volume += segment.NetAreaMm2 * segment.PhysicalLengthMm / 1e9;
        }
        foreach (var segment in request.Formwork)
        {
            var path = $"formwork.{segment.Id}";
            Require.Positive(segment.PhysicalLengthMm, path + ".physicalLengthMm");
            Require.Nonnegative(segment.SoffitContactWidthMm, path + ".soffitContactWidthMm");
            Require.Nonnegative(segment.LeftContactHeightMm, path + ".leftContactHeightMm");
            Require.Nonnegative(segment.RightContactHeightMm, path + ".rightContactHeightMm");
            Require.Nonnegative(segment.EndBulkheadAreaMm2, path + ".endBulkheadAreaMm2");
            Require.Nonnegative(segment.DeductionAreaMm2, path + ".deductionAreaMm2");
            double gross = segment.PhysicalLengthMm * (segment.SoffitContactWidthMm + segment.LeftContactHeightMm + segment.RightContactHeightMm) + segment.EndBulkheadAreaMm2;
            Require.That(segment.DeductionAreaMm2 <= gross, path + ".deductionAreaMm2", "Deduction exceeds contact area.");
            formwork += (gross - segment.DeductionAreaMm2) / 1e6;
        }
        double steel = bars.Sum(b => b.SteelMassKg);
        Require.Finite(volume, "concreteVolumeM3");
        Require.Finite(formwork, "formworkAreaM2");
        Require.Finite(steel, "steelMassKg");
        DirectCost? cost = null;
        if (request.Rates is { } rates)
        {
            Require.Text(rates.Currency, "rates.currency");
            Require.Text(rates.Source, "rates.source");
            Require.That(rates.PriceDate != default, "rates.priceDate", "Provide the price date.");
            Require.That(rates.SteelPerKg >= 0 && rates.ConcretePerM3 >= 0 && rates.FormworkPerM2 >= 0, "rates", "Unit rates cannot be negative.");
            cost = new(rates.Currency, (decimal)steel * rates.SteelPerKg, (decimal)volume * rates.ConcretePerM3, (decimal)formwork * rates.FormworkPerM2);
        }
        return new(bars.ToArray(), steel, volume, formwork, cost);
    }
}
