[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$XllPath,
    [Parameter(Mandatory)][string]$SnapshotPath,
    [Parameter(Mandatory)][ValidatePattern('^[a-fA-F0-9]{64}$')][string]$ExpectedSnapshotSha256,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [switch]$DevelopmentSmoke,
    [switch]$ExerciseRibbon
)
. (Join-Path $PSScriptRoot 'Common.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw 'Acceptance output must be a new task-owned directory.' }
if (Get-Process -Name EXCEL -ErrorAction SilentlyContinue) { throw 'Close Excel before acceptance; user Excel is never attached or stopped.' }
[void][IO.Directory]::CreateDirectory($output)
$receipt = [ordered]@{ mode = if ($DevelopmentSmoke) { 'development_smoke' } else { 'signed_installed_acceptance' }; checks = [Collections.Generic.List[object]]::new(); failure = $null; cleanup = $null }
$excel = $null; $book = $null; $other = $null; $books = $null; $processId = $null; $failure = $null
function Assert-Design([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Invoke-DesignMacro([object]$Excel, [string]$Name, [object[]]$MacroArguments = @()) {
    $text = switch ($MacroArguments.Count) {
        0 { $Excel.Run($Name) }
        1 { $Excel.Run($Name, $MacroArguments[0]) }
        2 { $Excel.Run($Name, $MacroArguments[0], $MacroArguments[1]) }
        3 { $Excel.Run($Name, $MacroArguments[0], $MacroArguments[1], $MacroArguments[2]) }
        default { throw 'Unsupported macro argument count.' }
    }
    return [string]$text | ConvertFrom-Json -ErrorAction Stop
}
function Read-DesignCells([object]$Book, [string]$SheetName, [string]$Address) {
    $sheets = $null; $sheet = $null; $range = $null
    try { $sheets=$Book.Worksheets; $sheet=$sheets.Item($SheetName); $range=$sheet.Range($Address); return ,$range.Value2 }
    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Set-DesignField([object]$Book, [string]$SourceId, [string]$Field, [string]$Value) {
    $sheets=$null; $sheet=$null; $range=$null; $cell=$null
    try {
        $sheets=$Book.Worksheets; $sheet=$sheets.Item('Design Inputs'); $range=$sheet.UsedRange; $cells=$range.Value2
        for ($r=2;$r -le $cells.GetLength(0);$r++) {
            if ([string]$cells[$r,2] -ceq $SourceId -and [string]$cells[$r,3] -ceq $Field) { $cell=$sheet.Range("D$r"); $cell.Value2=$Value; return }
        }
        throw "Input field is missing: $SourceId/$Field"
    }
    finally { Release-StructAutomateComObject $cell; Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Set-OwnedFixtureInputs([object]$Book) {
    $sheets=$null; $sheet=$null; $range=$null; $target=$null
    try {
        $sheets=$Book.Worksheets; $sheet=$sheets.Item('Design Inputs'); $range=$sheet.UsedRange; $cells=$range.Value2
        $values=New-Object 'object[,]' ($cells.GetLength(0)-1),1
        for ($r=2;$r -le $cells.GetLength(0);$r++) {
            $category=[string]$cells[$r,1]; $sourceId=[string]$cells[$r,2]; $field=[string]$cells[$r,3]; $value=$cells[$r,4]
            if ($category -eq 'Project') { $value=@{project_id='wp11-owned-reference';revision_id='installed-input-r1';origin='owned fixture engineering definition';evidence_reference='wp11-owned-baseline-fixture/v1'}[$field] }
            if ($category -eq 'Material') { $value=@{concrete_strength_n_per_mm2='25';steel_yield_strength_n_per_mm2='500';link_steel_yield_strength_n_per_mm2='415';steel_modulus_n_per_mm2='200000'}[$field] }
            if ($category -eq 'Role') { $value=@{'selection-case:WP11_ULS'='uls';'selection-case:WP11_SLS'='sls_total';'selection-case:WP11_SUSTAINED'='sls_sustained'}[$sourceId] }
            if ($category -eq 'Member') {
                $length=@{'member:PF9_B0001'=4000;'member:PF9_B0002'=4250;'member:PF9_B0003'=4500}[$sourceId]
                Assert-Design ($null -ne $length) "Unadmitted fixture member: $sourceId"
                $fields=@{selected='true';physical_span_id="span:$sourceId";support_condition='simply_supported';left_support_face_x_mm='500';right_support_face_x_mm=($length-500);left_support_centre_x_mm='0';right_support_centre_x_mm=$length;effective_span_mm=$length;anchorage_start_x_mm='-465';anchorage_end_x_mm=($length+465);nominal_cover_mm='35';maximum_aggregate_size_mm='20';exposure='Mild';cracking_harmful='false';ordinary_seismic='true';screening_permitted='true';horizontal='true';top_mapping_normal='true';evidence_revision_id='owned-support-definition-v1';fire_requirement='not_required';fire_decision_reference='owned nonbuilding fixture';fire_required_minutes='';lateral_restraint_positions_mm="0,$length";lateral_restraint_evidence_reference='owned end global-Y/global-X rotation restraints'}
                $value=$fields[$field]
            }
            $values[($r-2),0]=[string]$value
        }
        $target=$sheet.Range("D2:D$($cells.GetLength(0))"); $target.Value2=$values
    }
    finally { Release-StructAutomateComObject $target; Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Wait-DesignTask([object]$Excel, [string]$DispatchId) {
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $state=Invoke-DesignMacro $Excel 'STR_XL_TEST_DESIGN_DISPATCH' @($DispatchId)
        Assert-Design ($state.state -ne 'unknown') 'The expected design was never dispatched.'
        if ($state.details.completed) { return $state }
        Start-Sleep -Milliseconds 200
    } while ($timer.Elapsed.TotalSeconds -lt 120)
    throw "Dispatched task did not settle: $DispatchId"
}
function Wait-DesignOutcome([object]$Excel, [string]$DispatchId) {
    $null=Wait-DesignTask $Excel $DispatchId
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $state=Invoke-DesignMacro $Excel 'STR_XL_OFFLINE_STATUS'
        if ($state.state -in @('completed','failed','rejected')) {
            Assert-Design ($state.state -eq 'completed') ($state | ConvertTo-Json -Depth 10 -Compress)
            Assert-Design ($state.details.request_id -ceq $DispatchId) 'Completion does not bind the accepted dispatch.'
            return $state
        }
        Start-Sleep -Milliseconds 200
    } while ($timer.Elapsed.TotalSeconds -lt 20)
    $receipt.completion_diagnostic=Invoke-DesignMacro $Excel 'STR_XL_TEST_DESIGN_DISPATCH' @($DispatchId)
    $receipt.last_outcome=$state
    throw 'The completed worker did not attach its outcome to the initiating workbook.'
}
function Start-Design([object]$Excel) {
    $started=Invoke-DesignMacro $Excel 'STR_XL_DESIGN'
    Assert-Design ($started.state -eq 'started') ($started | ConvertTo-Json -Depth 10 -Compress)
    return $started
}
function Wait-DesignCallback([object]$Excel, [string]$DispatchId, [string]$ExpectedPhase) {
    $null=Wait-DesignTask $Excel $DispatchId
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $state=Invoke-DesignMacro $Excel 'STR_XL_TEST_DESIGN_DISPATCH' @($DispatchId)
        if ($state.details.phase -like "$ExpectedPhase*") { return $state }
        Start-Sleep -Milliseconds 200
    } while ($timer.Elapsed.TotalSeconds -lt 20)
    throw ('Expected callback disposition was not reached: '+($state | ConvertTo-Json -Depth 10 -Compress))
}
function Wait-ReopenedDesign([object]$Excel) {
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $current=Invoke-DesignMacro $Excel 'STR_XL_OFFLINE_STATUS'
        if ($current.PSObject.Properties['state'] -and $current.state -in @('current','stale','rejected','failed')) { break }
        Start-Sleep -Milliseconds 250
    } while ($timer.Elapsed.TotalSeconds -lt 120)
    Assert-Design ($current.state -eq 'current') ('Reopened design was not current: '+$current.message)
}
function Get-DesignSheetNames([object]$Book) {
    $sheets=$null; $sheet=$null
    try {
        $sheets=$Book.Worksheets
        for ($i=1;$i -le $sheets.Count;$i++) {
            try { $sheet=$sheets.Item($i); [string]$sheet.Name }
            finally { Release-StructAutomateComObject $sheet; $sheet=$null }
        }
    }
    finally { Release-StructAutomateComObject $sheets }
}
function Set-DesignCell([object]$Book, [string]$SheetName, [string]$Address, [string]$Value) {
    $sheets=$null; $sheet=$null; $cell=$null
    try { $sheets=$Book.Worksheets; $sheet=$sheets.Item($SheetName); $cell=$sheet.Range($Address); $cell.Value2=$Value }
    finally { Release-StructAutomateComObject $cell; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Invoke-DesignRibbon([object]$Excel) {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $root=[Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$Excel.Hwnd)
    $tab=$root.FindFirst([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::NameProperty,'StructAutomate'))
    Assert-Design ($null -ne $tab) 'The observed owned Excel UI has no StructAutomate tab.'
    $pattern=$null
    Assert-Design ($tab.TryGetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern,[ref]$pattern)) 'The observed ribbon tab has no selection pattern.'
    $pattern.Select()
    $button=$root.FindFirst([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.AndCondition]::new(
        [Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::NameProperty,'Design'),
        [Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Button)))
    Assert-Design ($null -ne $button) 'The selected ribbon has no observed Design button.'
    $invoke=$null
    Assert-Design ($button.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern,[ref]$invoke)) 'The observed Design button has no InvokePattern.'
    $receipt.ribbon=[ordered]@{name=$button.Current.Name;automation_id=$button.Current.AutomationId;process_id=$button.Current.ProcessId;pattern='InvokePattern'}
    $invoke.Invoke()
    $ribbonTimer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $started=Invoke-DesignMacro $Excel 'STR_XL_OFFLINE_STATUS'
        if ($started.state -eq 'started') { return $started }
        if ($started.state -in @('failed','rejected')) { break }
        Start-Sleep -Milliseconds 200
    } while ($ribbonTimer.Elapsed.TotalSeconds -lt 10)
    $receipt.ribbon.outcome=$started
    Assert-Design ($started.state -eq 'started') ('Actual ribbon action did not dispatch Design: '+($started | ConvertTo-Json -Depth 10 -Compress))
    return $started
}
try {
    $xll=[IO.Path]::GetFullPath($XllPath); $snapshot=[IO.Path]::GetFullPath($SnapshotPath)
    Assert-Design ((Get-StructAutomatePeMachine $xll) -eq 'AMD64') 'XLL must be AMD64.'
    $receipt.xll=Get-StructAutomateFileIdentity $xll
    $receipt.snapshot=Get-StructAutomateFileIdentity $snapshot
    Assert-Design ($receipt.snapshot.sha256 -ceq $ExpectedSnapshotSha256.ToLowerInvariant()) 'Snapshot file digest differs.'
    if (-not $DevelopmentSmoke) {
        $null=Assert-StructAutomateSafeInstallPath $xll
        $manifest=Get-Content -LiteralPath (Join-Path (Split-Path $xll -Parent) 'manifest.json') -Raw | ConvertFrom-Json
        Assert-Design ($manifest.signed_xll.sha256 -ceq $receipt.xll.sha256) 'Installed manifest XLL hash differs.'
        $signature=Get-AuthenticodeSignature -LiteralPath $xll
        Assert-Design ([string]$signature.Status -eq 'Valid' -and $signature.SignerCertificate.Thumbprint -ceq $manifest.signature.thumbprint) 'Installed signature is not verified.'
        Assert-Design (@(Get-StructAutomateExcelStartupRegistrations -XllPath $xll).Count -gt 0) 'Exact installed startup registration is missing.'
        $receipt.manifest=$manifest
    }
    $excel=New-Object -ComObject Excel.Application
    $processes=@(Get-Process -Name EXCEL -ErrorAction Stop)
    Assert-Design ($processes.Count -eq 1) 'Owned Excel process identity is ambiguous.'
    $processId=[int]$processes[0].Id
    $books=$excel.Workbooks
    Assert-Design ($books.Count -eq 0) 'Owned Excel unexpectedly contains workbooks.'
    Assert-Design ([bool]$excel.RegisterXLL($xll)) 'Excel could not load the exact XLL.'
    Assert-Design ($books.Count -eq 0) 'Loading the add-in created a workbook.'
    $excel.Visible=$true; $excel.DisplayAlerts=$false; $excel.AskToUpdateLinks=$false
    $book=$books.Add()
    Assert-Design ([bool]$excel.Run('STR_XL_TEST_RIBBON_LOADED')) 'Ribbon XML did not load.'
    $setup=Invoke-DesignMacro $excel 'STR_XL_ASSUMPTIONS'; Assert-Design ($setup.state -eq 'completed') $setup.message
    $import=Invoke-DesignMacro $excel 'STR_XL_IMPORT_SNAPSHOT_FILE' @($snapshot,$ExpectedSnapshotSha256,(Join-Path $output 'store')); Assert-Design ($import.state -eq 'completed') $import.message
    Assert-Design ($import.details.member_count -eq 3 -and $import.details.action_count -eq 153) 'Owned WP11 three-beam/153-row fixture is required.'
    $inputs=Invoke-DesignMacro $excel 'STR_XL_DESIGN_INPUTS'; Assert-Design ($inputs.state -eq 'needs_input') $inputs.message
    Set-OwnedFixtureInputs $book
    $accepted=Invoke-DesignMacro $excel 'STR_XL_ACCEPT_DESIGN_INPUTS'; Assert-Design ($accepted.state -eq 'accepted') $accepted.message
    Assert-Design (@($accepted.details.issues).Count -eq 0) 'Complete fixture inputs have unresolved fields.'
    $started=if ($DevelopmentSmoke -and -not $ExerciseRibbon) { Start-Design $excel } else { Invoke-DesignRibbon $excel }
    $completed=Wait-DesignOutcome $excel $started.details.request_id
    Assert-Design (@($completed.details.members | Where-Object state -ne 'Complete').Count -eq 0) 'At least one owned beam is incomplete.'
    $summary=Read-DesignCells $book 'Beam Designs' 'A10:L12'
    for ($row=1;$row -le 3;$row++) { Assert-Design ($summary[$row,2] -ceq 'Complete' -and $summary[$row,3] -ceq '2x12/L1' -and $summary[$row,4] -ceq '2x12/L1' -and $summary[$row,5] -ceq '8@150') 'Actual reinforcement differs from the independent A fixture acceptance.' }
    $receipt.checks.Add([ordered]@{name='three_real_beams_complete';dispatch=$started.details.request_id;passed=$true})
    $details=Invoke-DesignMacro $excel 'STR_XL_DESIGN_DETAILS' @('member:PF9_B0001'); Assert-Design ($details.state -eq 'completed') $details.message
    Set-DesignCell $book 'Beam Designs' 'N20' 'owned acceptance sentinel'
    Set-DesignField $book 'member:PF9_B0002' 'nominal_cover_mm' ''
    $mixedInputs=Invoke-DesignMacro $excel 'STR_XL_ACCEPT_DESIGN_INPUTS'
    Assert-Design ($mixedInputs.state -eq 'accepted' -and @($mixedInputs.details.issues).Count -gt 0) 'Missing member input was not explicitly accounted.'
    $started=Start-Design $excel; $mixed=Wait-DesignOutcome $excel $started.details.request_id
    Assert-Design (@($mixed.details.members).Count -eq 3 -and @($mixed.details.members | Where-Object state -eq 'Complete').Count -eq 2) 'Mixed batch erased or qualified an incomplete member.'
    Assert-Design (@($mixed.details.members | Where-Object { $_.member_id -ceq 'member:PF9_B0002' -and $_.state -ceq 'NeedsInput' }).Count -eq 1) 'Missing-input member did not retain NeedsInput.'
    $mixedStatus=Invoke-DesignMacro $excel 'STR_XL_DESIGN_STATUS'; Assert-Design ($mixedStatus.state -eq 'current') 'Current mixed results were incorrectly classified stale.'
    $receipt.checks.Add([ordered]@{name='mixed_batch_complete_and_needs_input';passed=$true})
    Set-DesignField $book 'member:PF9_B0002' 'nominal_cover_mm' '35'
    Set-DesignField $book 'member:PF9_B0001' 'nominal_cover_mm' '40'
    $stale=Invoke-DesignMacro $excel 'STR_XL_OFFLINE_STATUS'
    Assert-Design ($stale.state -eq 'stale') 'SheetChange did not immediately invalidate the saved design.'
    Assert-Design ((Read-DesignCells $book 'Beam Designs' 'A2') -like 'Historical*') 'Saved summary was not immediately marked historical.'
    $receipt.checks.Add([ordered]@{name='immediate_sheet_change_invalidation';passed=$true})
    $blocked=Invoke-DesignMacro $excel 'STR_XL_DESIGN'; Assert-Design ($blocked.state -eq 'rejected') 'Edited inputs were used without explicit acceptance.'
    $accepted2=Invoke-DesignMacro $excel 'STR_XL_ACCEPT_DESIGN_INPUTS'; Assert-Design ($accepted2.state -eq 'accepted' -and $accepted2.details.input_revision -ne $accepted.details.input_revision) 'Changed inputs did not receive a new accepted revision.'
    $started=Start-Design $excel; $completed=Wait-DesignOutcome $excel $started.details.request_id
    $receipt.checks.Add([ordered]@{name='changed_basis_redesigned';passed=$true})
    Set-DesignCell $book 'Assumptions' 'B8' '30'
    $assumptionEdit=Invoke-DesignMacro $excel 'STR_XL_OFFLINE_STATUS'
    Assert-Design ($assumptionEdit.state -eq 'stale' -and (Read-DesignCells $book 'Beam Designs' 'A2') -like 'Historical*') 'Assumption editing did not immediately invalidate results.'
    $assumptionBlocked=Invoke-DesignMacro $excel 'STR_XL_DESIGN'; Assert-Design ($assumptionBlocked.state -eq 'rejected') 'Changed assumptions were used without acceptance.'
    $assumptionAccepted=Invoke-DesignMacro $excel 'STR_XL_ACCEPT_DESIGN_INPUTS'; Assert-Design ($assumptionAccepted.state -eq 'accepted') $assumptionAccepted.message
    $receipt.checks.Add([ordered]@{name='assumption_edit_requires_reacceptance';passed=$true})
    $started=Start-Design $excel
    $other=$books.Add()
    $null=Wait-DesignCallback $excel $started.details.request_id 'completion callback returned:'
    Assert-Design (@(Get-DesignSheetNames $other | Where-Object { $_ -in @('Design Inputs','Beam Designs','Design Details') }).Count -eq 0) 'Completion was redirected into the active other workbook.'
    $book.Activate()
    $completed=Wait-DesignOutcome $excel $started.details.request_id
    $receipt.checks.Add([ordered]@{name='workbook_switch_retains_initiating_target';passed=$true})
    $started=Start-Design $excel
    $cancel=Invoke-DesignMacro $excel 'STR_XL_CANCEL_DESIGN'
    Assert-Design ($cancel.state -eq 'cancelled' -and $cancel.details.request_id -ceq $started.details.request_id) 'Cancel did not own the pending dispatch.'
    $settled=Wait-DesignCallback $excel $started.details.request_id 'completion discarded:'
    Assert-Design (-not $settled.details.resident) 'Cancelled dispatch remained resident.'
    Assert-Design ((Read-DesignCells $book 'Beam Designs' 'A2') -like 'Design cancelled*') 'Cancelled design replaced historical results.'
    $receipt.checks.Add([ordered]@{name='cancel_actual_dispatch_and_discard_callback';passed=$true})
    $started=Start-Design $excel; $completed=Wait-DesignOutcome $excel $started.details.request_id
    $resultFile=[IO.Path]::GetFullPath((Join-Path (Join-Path $output 'store\Designs') $completed.details.result_reference.fileName))
    $retainedFile=[IO.Path]::GetFullPath((Join-Path $output 'temporarily-unavailable-result.json'))
    foreach ($ownedPath in @($resultFile,$retainedFile)) { Assert-Design ($ownedPath.StartsWith($output+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) 'Missing-evidence probe escaped its owned directory.' }
    $resultHash=(Get-FileHash -LiteralPath $resultFile -Algorithm SHA256).Hash
    try {
        Move-Item -LiteralPath $resultFile -Destination $retainedFile
        $missing=Invoke-DesignMacro $excel 'STR_XL_DESIGN_STATUS'
        Assert-Design ($missing.state -eq 'rejected') 'Missing external result was silently accepted.'
        Assert-Design ((Read-DesignCells $book 'Beam Designs' 'A2') -like 'Historical*unavailable*') 'Missing external result left a Current summary visible.'
    }
    finally { if (Test-Path -LiteralPath $retainedFile) { Move-Item -LiteralPath $retainedFile -Destination $resultFile } }
    Assert-Design ((Get-FileHash -LiteralPath $resultFile -Algorithm SHA256).Hash -ceq $resultHash) 'Retained evidence was not restored exactly.'
    $restored=Invoke-DesignMacro $excel 'STR_XL_DESIGN_STATUS'; Assert-Design ($restored.state -eq 'current') 'Restored exact evidence was not current.'
    Assert-Design ((Read-DesignCells $book 'Beam Designs' 'N20') -ceq 'owned acceptance sentinel') 'Projection overwrote cells outside its owned footprint.'
    $receipt.checks.Add([ordered]@{name='missing_evidence_visible_and_exact_restore';passed=$true})
    $workbookPath=Join-Path $output 'baseline-design.xlsx'; $book.SaveAs($workbookPath,51)
    $book.Close($false); Release-StructAutomateComObject $book; $book=$null
    $savedHash=(Get-FileHash -LiteralPath $workbookPath -Algorithm SHA256).Hash
    $book=$books.Open($workbookPath)
    Wait-ReopenedDesign $excel
    $started=Start-Design $excel
    $book.Close($false); Release-StructAutomateComObject $book; $book=$null
    $other.Activate()
    $closed=Wait-DesignCallback $excel $started.details.request_id 'completion discarded:'
    Assert-Design (-not $closed.details.resident -and [int]$excel.Run('STR_XL_TEST_OFFLINE_SESSION_COUNT') -eq 0) 'Closed workbook retained a design/session.'
    Assert-Design ((Get-FileHash -LiteralPath $workbookPath -Algorithm SHA256).Hash -ceq $savedHash) 'A callback modified the closed saved workbook.'
    $receipt.checks.Add([ordered]@{name='close_pending_settles_and_discards';passed=$true})
    $book=$books.Open($workbookPath)
    Wait-ReopenedDesign $excel
    $receipt.checks.Add([ordered]@{name='offline_reopen_current';passed=$true})
    $names=@(Get-DesignSheetNames $book)
    foreach ($ownedName in @('Design Inputs','Beam Designs','Design Details')) { Assert-Design (@($names | Where-Object { $_ -ceq $ownedName }).Count -eq 1) 'Owned output sheets were duplicated.' }
    Assert-Design ((Read-DesignCells $book 'Beam Designs' 'N20') -ceq 'owned acceptance sentinel') 'Reopen overwrote cells outside its owned footprint.'
    $receipt.checks.Add([ordered]@{name='single_owned_sheets_and_preserved_footprint';passed=$true})
    $receipt.status='passed'
}
catch {
    $failure=$_.Exception; $receipt.failure=$failure.ToString(); $receipt.status='failed'
    if ($null -ne $excel -and (Get-Variable -Name started -ErrorAction SilentlyContinue)) {
        try { $receipt.completion_diagnostic=Invoke-DesignMacro $excel 'STR_XL_TEST_DESIGN_DISPATCH' @($started.details.request_id) } catch { }
    }
}
finally {
    if ($null -ne $other) { try { $other.Close($false) } finally { Release-StructAutomateComObject $other } }
    if ($null -ne $book) { try { $book.Close($false) } finally { Release-StructAutomateComObject $book } }
    Release-StructAutomateComObject $books
    Close-StructAutomateExcelApplication $excel
    $exited=$true
    if ($null -ne $processId) {
        $timer=[Diagnostics.Stopwatch]::StartNew()
        while ((Get-Process -Id $processId -ErrorAction SilentlyContinue) -and $timer.Elapsed.TotalSeconds -lt 15) { Start-Sleep -Milliseconds 250 }
        $exited=$null -eq (Get-Process -Id $processId -ErrorAction SilentlyContinue)
    }
    $receipt.cleanup=[ordered]@{owned_process_id=$processId;exited=$exited}
    if (-not $exited) { $receipt.status='failed'; if ($null -eq $failure) { $failure=[InvalidOperationException]::new('Owned Excel did not exit after cleanup.') } }
    [IO.File]::WriteAllText((Join-Path $output 'receipt.json'),($receipt | ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
}
if ($null -ne $failure) { throw $failure }
$receipt | ConvertTo-Json -Depth 30
