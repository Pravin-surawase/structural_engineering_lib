using System.Text.Json;
using System.Text.Json.Nodes;
using StructAutomate.Contracts;
using StructAutomate.Engineering;
using Xunit;

namespace StructAutomate.Tests;

public class ContractTests
{
    [Fact]
    public void ShippedRequestSchemasMatchCompiledContracts()
    {
        foreach (var (name,schema) in ContractSchemas.ExportRequests())
        {
            var shipped=JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"schemas",name+".schema.json")));
            Assert.True(JsonNode.DeepEquals(schema,shipped),name+" schema must be regenerated with its contract change.");
        }
    }

    [Fact]
    public void MissingRequiredFieldsAndMisspellingsAreRejected()
    {
        var options = ContractJson.CreateOptions();
        Assert.Throws<JsonException>(() => JsonSerializer.Deserialize<QuantityRequest>("{}",options));
        Assert.Throws<JsonException>(() => JsonSerializer.Deserialize<QuantityRequest>("{\"schemaVersion\":\"1.0.0\",\"steelDensityKgPerM3\":7850,\"bars\":[],\"concrete\":[],\"formwork\":[],\"ratse\":null}",options));
    }

    [Fact]
    public void OmittedRatesMeanNoCostAndNeverDefaultPrices()
    {
        var json = "{\"schemaVersion\":\"1.0.0\",\"steelDensityKgPerM3\":7850,\"bars\":[],\"concrete\":[],\"formwork\":[]}";
        var request = JsonSerializer.Deserialize<QuantityRequest>(json,ContractJson.CreateOptions())!;
        Assert.Null(QuantityCalculator.Calculate(request).Cost);
    }

    [Fact]
    public void ExampleRequestsDeserializeAndCalculate()
    {
        var options = ContractJson.CreateOptions();
        var root = Path.Combine(AppContext.BaseDirectory,"examples");
        var beam = JsonSerializer.Deserialize<BeamLineRequest>(File.ReadAllText(Path.Combine(root,"beam-line.json")),options)!;
        Assert.Equal(45,BeamLineSolver.Solve(beam).Stations.Single(s => s.FromStartMm == 3000).SaggingMomentKnM,8);
        var bars = JsonSerializer.Deserialize<ReinforcementGeometryRequest>(File.ReadAllText(Path.Combine(root,"reinforcement.json")),options)!;
        Assert.True(ReinforcementGeometry.Evaluate(bars).Fits);
        var quantity = JsonSerializer.Deserialize<QuantityRequest>(File.ReadAllText(Path.Combine(root,"quantities.json")),options)!;
        Assert.Equal(.9,QuantityCalculator.Calculate(quantity).ConcreteVolumeM3,8);
    }
}
