using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json;
using StructAutomate.Contracts;
using StructAutomate.Engineering;

var options = ContractJson.CreateOptions();
if (args is ["schemas", var directory])
{
    Directory.CreateDirectory(directory);
    foreach (var (name, schema) in ContractSchemas.ExportRequests())
        File.WriteAllText(Path.Combine(directory, name + ".schema.json"), schema.ToJsonString(options) + "\n");
    Console.WriteLine("Exported five request schemas from the compiled contract types.");
    return;
}
if (args is ["beam", var path])
{
    var request = JsonSerializer.Deserialize<BeamLineRequest>(File.ReadAllText(path), options)!;
    Console.WriteLine(JsonSerializer.Serialize(BeamLineSolver.Solve(request), options));
    return;
}
if (args is ["benchmark"])
{
    var request = new BeamLineRequest("1.0.0", [new("A",0,0),new("B",6000,0)], [new("AB","A","B",25000,3125000000,10,[3000])]);
    var cold = Stopwatch.StartNew();
    var first = BeamLineSolver.Solve(request); cold.Stop();
    for (int i = 0; i < 100; i++) BeamLineSolver.Solve(request);
    var samples = new double[1000];
    var allocatedBefore = GC.GetAllocatedBytesForCurrentThread();
    for (int i = 0; i < samples.Length; i++)
    {
        var start = Stopwatch.GetTimestamp(); BeamLineSolver.Solve(request);
        samples[i] = Stopwatch.GetElapsedTime(start).TotalMilliseconds;
    }
    var allocatedBytes = GC.GetAllocatedBytesForCurrentThread() - allocatedBefore;
    Array.Sort(samples);
    Console.WriteLine(JsonSerializer.Serialize(new {
        Runtime = RuntimeInformation.FrameworkDescription, OS = RuntimeInformation.OSDescription,
        Architecture = RuntimeInformation.ProcessArchitecture.ToString(), Processors = Environment.ProcessorCount,
        Scenario = "one simply-supported 6m prismatic element, UDL, midpoint plus ends; pure library, Excel excluded",
        Samples = samples.Length, ColdMilliseconds = cold.Elapsed.TotalMilliseconds,
        WarmMedianMilliseconds = samples[500], WarmP95Milliseconds = samples[950],
        AllocatedBytesPerSolve = allocatedBytes / samples.Length,
        OracleMidspanDeflectionMm = first.Stations.Single(s => s.FromStartMm == 3000).DisplacementMm
    }, options));
    return;
}
Console.Error.WriteLine("Use: schemas <directory> | beam <request.json> | benchmark");
Environment.ExitCode = 2;
