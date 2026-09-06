namespace ConnectionLessons;

// An instructional model of ownership, NOT the production client/broker or a COM test.
// One TaskCompletionSource lets us change workbook state before a result arrives,
// without sleeps, timing races, threads, files, processes, Excel or ETABS.
internal static class WorkflowSimulation
{
    public static readonly string[] Scenarios = ["success", "switch", "close", "reopen", "stale", "cancel", "reject"];

    public static async Task<SimulationResult> RunAsync(string scenario)
    {
        if (!Scenarios.Contains(scenario, StringComparer.Ordinal))
            throw new ArgumentException($"Unknown scenario '{scenario}'. Use: {string.Join(", ", Scenarios)}.");

        var events = new List<string>();
        var books = new Dictionary<string, WorkbookEntry>(StringComparer.Ordinal);
        var original = new WorkbookEntry { PendingRequestId = "R1" };
        books["A"] = original;
        books["B"] = new WorkbookEntry();
        string activeWorkbook = "A";
        events.Add("Start R1 for workbook A; button returns started.");

        var worker = new TaskCompletionSource<WorkerReply>();
        Task<string> pending = CompleteWhenReadyAsync(worker.Task, books, original, events);
        events.Add("Completion is waiting; the caller can continue.");

        switch (scenario)
        {
            case "switch":
                activeWorkbook = "B";
                events.Add("User switches to B; R1 still belongs to A.");
                break;
            case "close":
                original.PendingRequestId = null;
                books.Remove("A");
                activeWorkbook = "B";
                events.Add("A closes: invalidate request and evict its entry.");
                break;
            case "reopen":
                original.PendingRequestId = null;
                books["A"] = new WorkbookEntry();
                events.Add("A closes and reopens: same label, a NEW entry object.");
                break;
            case "stale":
                original.PendingRequestId = "R2";
                events.Add("R1 was invalidated; a newer request R2 now owns the entry.");
                break;
            case "cancel":
                original.PendingRequestId = null;
                events.Add("Cancel requested: R1 is invalidated; cleanup is still pending.");
                break;
        }

        bool accepted = scenario != "reject" && scenario != "cancel";
        events.Add("Simulated worker finishes cleanup; only now deliver its reply.");
        worker.SetResult(new WorkerReply("R1", accepted, CleanupCompleted: true));
        string outcome = await pending;
        bool aHasContext = books.TryGetValue("A", out var currentA) && currentA.HasContext;
        return new SimulationResult(scenario, outcome, activeWorkbook, aHasContext, books["B"].HasContext, true, events);
    }

    private static async Task<string> CompleteWhenReadyAsync(Task<WorkerReply> worker,
        Dictionary<string, WorkbookEntry> books, WorkbookEntry expectedEntry, List<string> events)
    {
        WorkerReply reply = await worker;
        // In production this completion is dispatched to Excel's main thread.
        // Here it runs in an ordinary console program; there is no Excel dispatcher.
        if (!books.TryGetValue("A", out var entry))
            return Finish("ignored: workbook closed", events);
        if (!ReferenceEquals(entry, expectedEntry))
            return Finish("ignored: workbook entry replaced", events);
        if (entry.PendingRequestId != reply.RequestId)
            return Finish("ignored: request no longer current", events);
        entry.PendingRequestId = null;
        if (!reply.Accepted || !reply.CleanupCompleted)
            return Finish("rejected: no context published", events);
        entry.HasContext = true;
        return Finish("accepted into A", events);
    }

    private static string Finish(string outcome, List<string> events)
    {
        events.Add(outcome);
        return outcome;
    }

    private sealed class WorkbookEntry
    {
        public string? PendingRequestId { get; set; }
        public bool HasContext { get; set; }
    }

    private sealed record WorkerReply(string RequestId, bool Accepted, bool CleanupCompleted);
}

internal sealed record SimulationResult(string Scenario, string Outcome, string ActiveWorkbook,
    bool AHasContext, bool BHasContext, bool CleanupCompleted, IReadOnlyList<string> Events);
