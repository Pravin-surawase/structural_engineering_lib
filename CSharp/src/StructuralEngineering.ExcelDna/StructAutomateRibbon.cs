using ExcelDna.Integration.CustomUI;

namespace StructuralEngineering.ExcelDna;

public sealed class StructAutomateRibbon : ExcelRibbon
{
    public override string GetCustomUI(string ribbonId) => """
        <customUI xmlns="http://schemas.microsoft.com/office/2009/07/customui">
          <ribbon>
            <tabs>
              <tab id="StructAutomateTab" label="StructAutomate">
                <group id="StructAutomateOffline" label="Beam workspace">
                  <button id="StructAutomateAssumptions" label="Assumptions" size="large" imageMso="TableProperties" onAction="OnAssumptions" screentip="Editable demo assumptions" supertip="Creates one Assumptions sheet only when requested. Values remain labelled demo until a supported project basis exists." />
                  <button id="StructAutomateSnapshot" label="Open Snapshot" size="large" imageMso="FileOpen" onAction="OnOpenSnapshot" screentip="Open saved analysis evidence" supertip="Validate a completed portable snapshot and keep its heavy data outside the workbook. No live ETABS connection is made." />
                  <button id="StructAutomateReview" label="Review Snapshot" size="large" imageMso="ViewForm" onAction="OnReviewSnapshot" screentip="Review captured members and forces" supertip="Review offline evidence in memory. Write a member review sheet only on request." />
                </group>
                <group id="StructAutomateStandalone" label="Standalone tools">
                 <menu id="StructAutomateLegacyMenu" label="Standalone examples" imageMso="CalculateNow">
                  <button id="StructAutomateValidate" label="Create / Validate" size="large" imageMso="FileCheckIn" onAction="OnCreateValidate" />
                  <button id="StructAutomateCalculate" label="Calculate Workbook" size="large" imageMso="CalculateNow" onAction="OnCalculate" />
                  <button id="StructAutomateOptimize" label="Evaluate Current Candidate" imageMso="SolverOptions" onAction="OnOptimize" />
                  <button id="StructAutomateExport" label="Export Packages" imageMso="FileSaveAs" onAction="OnExport" />
                  <button id="StructAutomateDiagnose" label="Measure / Diagnose" imageMso="HappyFace" onAction="OnDiagnose" />
                 </menu>
                </group>
              </tab>
            </tabs>
          </ribbon>
        </customUI>
        """;

    public void OnAssumptions(IRibbonControl control) => OfflineCommands.Assumptions();
    public void OnOpenSnapshot(IRibbonControl control) => OfflineCommands.OpenSnapshot();
    public void OnReviewSnapshot(IRibbonControl control) => OfflineCommands.ReviewSnapshot();
    public void OnCreateValidate(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.CreateValidate);
    public void OnCalculate(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.CalculateWorkbook);
    public void OnOptimize(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.OptimizeBeams);
    public void OnExport(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.ExportPackages);
    public void OnDiagnose(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.MeasureDiagnose);
}
