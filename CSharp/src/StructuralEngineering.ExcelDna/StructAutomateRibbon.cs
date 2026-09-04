using ExcelDna.Integration.CustomUI;

namespace StructuralEngineering.ExcelDna;

public sealed class StructAutomateRibbon : ExcelRibbon
{
    public override string GetCustomUI(string ribbonId) => """
        <customUI xmlns="http://schemas.microsoft.com/office/2009/07/customui">
          <ribbon>
            <tabs>
              <tab id="StructAutomateTab" label="StructAutomate">
                <group id="StructAutomateWorkflow" label="Beam workflow">
                  <button id="StructAutomateValidate" label="Create / Validate" size="large" imageMso="FileCheckIn" onAction="OnCreateValidate" />
                  <button id="StructAutomateCalculate" label="Calculate Workbook" size="large" imageMso="CalculateNow" onAction="OnCalculate" />
                  <button id="StructAutomateOptimize" label="Optimize Beams" imageMso="SolverOptions" onAction="OnOptimize" />
                  <button id="StructAutomateExport" label="Export Packages" imageMso="FileSaveAs" onAction="OnExport" />
                  <button id="StructAutomateDiagnose" label="Measure / Diagnose" imageMso="HappyFace" onAction="OnDiagnose" />
                </group>
              </tab>
            </tabs>
          </ribbon>
        </customUI>
        """;

    public void OnCreateValidate(IRibbonControl control) => _ = WorkbookCommands.CreateValidate();
    public void OnCalculate(IRibbonControl control) => _ = WorkbookCommands.CalculateWorkbook();
    public void OnOptimize(IRibbonControl control) => _ = WorkbookCommands.OptimizeBeams();
    public void OnExport(IRibbonControl control) => _ = WorkbookCommands.ExportPackages();
    public void OnDiagnose(IRibbonControl control) => _ = WorkbookCommands.MeasureDiagnose();
}
