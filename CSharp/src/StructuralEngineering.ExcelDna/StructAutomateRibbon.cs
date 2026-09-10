using System.Runtime.InteropServices;
using ExcelDna.Integration;
using ExcelDna.Integration.CustomUI;
using ExcelDna.Integration.Extensibility;

namespace StructuralEngineering.ExcelDna;

[ComVisible(true)]
public sealed class StructAutomateRibbon : ExcelRibbon
{
    private static bool _loaded;

    [ExcelFunction(Name = "STR_XL_TEST_RIBBON_LOADED", IsHidden = true)]
    public static bool IsLoaded() => _loaded;

    public void OnRibbonLoad(IRibbonUI ribbon) => _loaded = true;

    public override void OnDisconnection(ext_DisconnectMode removeMode, ref Array custom)
    {
        _loaded = false;
        OfflineCommands.Unload();
        base.OnDisconnection(removeMode, ref custom);
    }

    public override string GetCustomUI(string ribbonId) => """
        <customUI xmlns="http://schemas.microsoft.com/office/2009/07/customui" onLoad="OnRibbonLoad">
          <ribbon>
            <tabs>
              <tab id="StructAutomateTab" label="StructAutomate">
                <group id="StructAutomateOffline" label="Beam workspace">
                  <button id="StructAutomateAssumptions" label="Assumptions" size="large" imageMso="TableProperties" onAction="OnAssumptions" screentip="Editable demo assumptions" supertip="Creates one Assumptions sheet only when requested. Values remain labelled demo until a supported project basis exists." />
                  <button id="StructAutomateConnect" label="Connect ETABS" size="large" imageMso="DatabaseInsert" onAction="OnConnectEtabs" screentip="Read a model overview" supertip="Read model counts and analysis/design availability. Load model details from the overview when needed." />
                  <button id="StructAutomateForces" label="Get Forces" size="large" imageMso="RefreshAll" onAction="OnGetForces" screentip="Read completed analysis forces" supertip="Capture the connected model's required beam forces in the background. Review from memory; no force worksheets are created. Analysis must already be complete." />
                  <button id="StructAutomateSnapshot" label="Open Snapshot" size="large" imageMso="FileOpen" onAction="OnOpenSnapshot" screentip="Open saved analysis evidence" supertip="Validate a completed portable snapshot and keep its heavy data outside the workbook. No live ETABS connection is made." />
                  <button id="StructAutomateReview" label="Review Snapshot" size="large" imageMso="ViewForm" onAction="OnReviewSnapshot" screentip="Review captured members and forces" supertip="Review offline evidence in memory. Write a member review sheet only on request." />
                </group>
                <group id="StructAutomateDesignGroup" label="Baseline beam design">
                  <button id="StructAutomateDesignInputs" label="Design Inputs" imageMso="TableProperties" onAction="OnDesignInputs" screentip="Explicit project and member inputs" />
                  <button id="StructAutomateAcceptDesignInputs" label="Accept Inputs" imageMso="FileCheckIn" onAction="OnAcceptDesignInputs" screentip="Accept calculation inputs; professional approval remains separate" />
                  <button id="StructAutomateDesign" label="Design" size="large" imageMso="CalculateNow" onAction="OnDesign" screentip="Design the selected beams from accepted inputs" />
                  <button id="StructAutomateCancelDesign" label="Cancel Design" imageMso="CancelRequest" onAction="OnCancelDesign" />
                  <button id="StructAutomateDesignStatus" label="Review Designs" imageMso="RefreshAll" onAction="OnDesignStatus" />
                  <button id="StructAutomateDesignDetails" label="Details" imageMso="ViewForm" onAction="OnDesignDetails" screentip="Select a member row in Beam Designs first" />
                </group>
                <group id="StructAutomateStandalone" label="Standalone tools">
                 <menu id="StructAutomateLegacyMenu" label="Standalone examples" imageMso="CalculateNow">
                  <button id="StructAutomateValidate" label="Create / Validate" imageMso="FileCheckIn" onAction="OnCreateValidate" />
                  <button id="StructAutomateCalculate" label="Calculate Workbook" imageMso="CalculateNow" onAction="OnCalculate" />
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
    public void OnConnectEtabs(IRibbonControl control) => OfflineCommands.InspectEtabs();
    public void OnGetForces(IRibbonControl control) => OfflineCommands.GetForces();
    public void OnOpenSnapshot(IRibbonControl control) => OfflineCommands.OpenSnapshot();
    public void OnReviewSnapshot(IRibbonControl control) => OfflineCommands.ReviewSnapshot();
    public void OnDesignInputs(IRibbonControl control) => OfflineCommands.DesignInputs();
    public void OnAcceptDesignInputs(IRibbonControl control) => OfflineCommands.AcceptDesignInputs();
    public void OnDesign(IRibbonControl control) => OfflineCommands.Design();
    public void OnCancelDesign(IRibbonControl control) => OfflineCommands.CancelDesign();
    public void OnDesignStatus(IRibbonControl control) => OfflineCommands.DesignStatus();
    public void OnDesignDetails(IRibbonControl control) => OfflineCommands.SelectedDesignDetails();
    public void OnCreateValidate(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.CreateValidate);
    public void OnCalculate(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.CalculateWorkbook);
    public void OnOptimize(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.OptimizeBeams);
    public void OnExport(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.ExportPackages);
    public void OnDiagnose(IRibbonControl control) => OfflineCommands.ShowLegacyOutcome(WorkbookCommands.MeasureDiagnose);
}
