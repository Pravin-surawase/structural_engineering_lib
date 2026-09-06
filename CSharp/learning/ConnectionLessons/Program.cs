using StructuralEngineering.Contracts;

namespace ConnectionLessons;

internal static class Program
{
    private static async Task<int> Main(string[] args)
    {
        try
        {
            string command = args.Length == 0 ? "help" : args[0];
            switch (command)
            {
                case "model":
                    ShowModel(args.Length > 1 ? args[1] : "B1");
                    break;
                case "workflow":
                    string scenario = args.Length > 1 ? args[1] : "success";
                    string[] scenarios = scenario == "all" ? WorkflowSimulation.Scenarios : [scenario];
                    foreach (string item in scenarios)
                        ShowWorkflow(await WorkflowSimulation.RunAsync(item));
                    break;
                case "check":
                    await CheckAsync();
                    break;
                default:
                    Console.WriteLine("Invented-data lessons; no Excel/ETABS, file writes or model changes.");
                    Console.WriteLine("Commands: model [frame ID] | workflow [success|switch|close|reopen|stale|cancel|reject|all] | check");
                    return command == "help" ? 0 : 2;
            }
            return 0;
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine($"Lesson error: {exception.Message}");
            return 1;
        }
    }

    private static void ShowModel(string frameId)
    {
        var session = SampleModel.Create();
        string[] beamIds = session.Frames.Values
            .Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam)
            .Select(frame => frame.SourceFrameId)
            .Order(StringComparer.Ordinal).ToArray();

        Console.WriteLine("INVENTED MODEL | coordinates in mm | no live applications");
        Console.WriteLine($"Inventory: {session.Frames.Count} frames, {session.Points.Count} points, {session.Sections.Count} sections");
        Console.WriteLine($"Beams: {string.Join(", ", beamIds)}");
        if (!session.Frames.TryGetValue(frameId, out var frame))
            throw new ArgumentException($"Unknown exact frame ID '{frameId}'. Try B1, B2, C1 or X1.");
        Console.WriteLine($"{frameId} endpoints: {frame.SourcePoint1Id} -> {frame.SourcePoint2Id}");
        var neighbours = session.Neighbours(frameId);
        Console.WriteLine($"{frameId} neighbours: {(neighbours.Count == 0 ? "(none)" : string.Join(", ", neighbours))}");
        Console.WriteLine($"P2 incidence: {string.Join(", ", session.FramesAtPoint["P2"])}");
        Console.WriteLine("P2 and P5 share coordinates but not IDs; X1 is not connected to B1 by source ID.");
        Console.WriteLine("Coverage: geometry and ID adjacency; no supports, physical spans, forces or design checks.");
    }

    private static void ShowWorkflow(SimulationResult result)
    {
        Console.WriteLine($"SIMULATION: {result.Scenario}");
        for (int index = 0; index < result.Events.Count; index++)
            Console.WriteLine($"  {index + 1}. {result.Events[index]}");
        Console.WriteLine($"Final: active={result.ActiveWorkbook}; A.context={result.AHasContext}; B.context={result.BHasContext}; cleanup={result.CleanupCompleted}");
    }

    private static async Task CheckAsync()
    {
        var session = SampleModel.Create();
        Require(session.Frames.Count == 4 && session.Points.Count == 6, "Stock fixture counts changed.");
        Require(session.Neighbours("B1").SequenceEqual(new[] { "B2", "C1" }), "B1 exact-ID adjacency changed.");
        Require(session.Neighbours("X1").Count == 0, "Coincident distinct point IDs were merged.");
        Require(!session.Frames.ContainsKey("b1"), "Frame IDs must remain case-sensitive.");
        Require(session.Points["P3"].Xmm == 8000, "Stock coordinate/unit changed.");

        var expected = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["success"] = "accepted into A",
            ["switch"] = "accepted into A",
            ["close"] = "ignored: workbook closed",
            ["reopen"] = "ignored: workbook entry replaced",
            ["stale"] = "ignored: request no longer current",
            ["cancel"] = "ignored: request no longer current",
            ["reject"] = "rejected: no context published"
        };
        foreach (string scenario in WorkflowSimulation.Scenarios)
        {
            SimulationResult result = await WorkflowSimulation.RunAsync(scenario);
            Require(result.Outcome == expected[scenario], $"Unexpected outcome for {scenario}.");
            Require(result.AHasContext == (scenario is "success" or "switch"), $"Wrong A context for {scenario}.");
            Require(!result.BHasContext && result.CleanupCompleted, $"Ownership/cleanup failed for {scenario}.");
            Require(result.ActiveWorkbook == (scenario is "switch" or "close" ? "B" : "A"), $"Wrong active label for {scenario}.");
        }
        Console.WriteLine("PASS: stock model indexes + all 7 teaching scenarios.");
        Console.WriteLine("This checks the lessons, not installed Excel/ETABS acceptance or engineering design.");
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }
}
