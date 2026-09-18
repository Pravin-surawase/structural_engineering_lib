[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$XllPath,
    [Parameter(Mandatory)][string]$SnapshotPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$RetainedSnapshotPath,
    [string]$LegacyWorkbookPath,
    [switch]$DevelopmentSmoke,
    [switch]$Smoke,
    [switch]$OwnershipProbe,
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
$excel=$null; $books=$null; $book=$null; $other=$null; $processId=$null; $failure=$null
function Assert-Review([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Invoke-ReviewMacro([string]$Name, [object[]]$Arguments=@()) {
    $text = switch ($Arguments.Count) {
        0 { $excel.Run($Name) }
        1 { $excel.Run($Name,$Arguments[0]) }
        3 { $excel.Run($Name,$Arguments[0],$Arguments[1],$Arguments[2]) }
        default { throw 'Unsupported macro argument count.' }
    }
    return [string]$text | ConvertFrom-Json
}
function Wait-Review {
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $state=Invoke-ReviewMacro 'STR_XL_REVIEW_STATE'
        if ($state.state -eq 'idle' -and $state.message -like 'Current provisional*') {
            $inputPath=Join-Path $state.details.input_directory $state.details.input.file_name
            Assert-Review ((Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant() -ceq $state.details.input.file_sha256) 'Effective input artifact digest differs.'
            $state.details | Add-Member -NotePropertyName resolved -NotePropertyValue (Get-Content -LiteralPath $inputPath -Raw | ConvertFrom-Json)
            return $state
        }
        if ($state.state -in @('failed','rejected')) { throw $state.message }
        Start-Sleep -Milliseconds 200
    } while ($timer.Elapsed.TotalSeconds -lt 150)
    throw ('Review did not complete: '+($state | ConvertTo-Json -Depth 5 -Compress))
}
function Read-ReviewResult($State) {
    $path=Join-Path $State.details.directory $State.details.result.file_name
    Assert-Review ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ceq $State.details.result.file_sha256) 'Stored review digest differs.'
    return Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
}
function Set-ReviewCell([string]$SheetName,[string]$Address,[string]$Value) {
    $sheets=$null; $sheet=$null; $cell=$null
    try { $sheets=$book.Worksheets; $sheet=$sheets.Item($SheetName); $cell=$sheet.Range($Address); $cell.Value2=$Value }
    finally { Release-StructAutomateComObject $cell; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Review-Field($State,[string]$Member,[string]$Key) {
    return @($State.details.resolved.ledger.fields | Where-Object { $_.subject_id -ceq $Member -and $_.key -ceq $Key })[0]
}
function Set-ReviewOverride([string]$Member,[string]$Key,[string]$Value) {
    $sheets=$null; $sheet=$null; $range=$null; $cell=$null
    try {
        $sheets=$book.Worksheets; $sheet=$sheets.Item('Review Inputs'); $range=$sheet.UsedRange; $cells=$range.Value2
        for ($r=5;$r -le $cells.GetLength(0);$r++) {
            if ([string]$cells[$r,1] -ceq $Member -and [string]$cells[$r,2] -ceq $Key) { $cell=$sheet.Range("C$r"); $cell.Value2=$Value; return }
        }
        throw "Missing review field $Member / $Key"
    }
    finally { Release-StructAutomateComObject $cell; Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
}
function Wait-ReviewDispatch([string]$Dispatch,[string]$Phase) {
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do {
        $status=Invoke-ReviewMacro 'STR_XL_TEST_REVIEW_DISPATCH' @($Dispatch)
        if ($status.details.completed -and $status.details.phase -like "$Phase*") { return $status }
        if ($status.details.phase -like 'callback returned:*' -or $status.details.phase -eq 'failed') { throw ('Review callback failed: '+$status.details.phase) }
        Start-Sleep -Milliseconds 200
    } while ($timer.Elapsed.TotalSeconds -lt 150)
    throw ('Dispatch did not reach '+$Phase+': '+($status | ConvertTo-Json -Compress))
}
function Assert-OwnedReviewPath([string]$Path) {
    $full=[IO.Path]::GetFullPath($Path)
    Assert-Review ($full.StartsWith($output.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) 'Evidence move escapes the owned acceptance directory.'
    return $full
}
function Invoke-ReviewRibbon {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $root=[Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$excel.Hwnd)
    $tab=$root.FindFirst([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::NameProperty,'StructAutomate'))
    Assert-Review ($null -ne $tab) 'Owned Excel has no observed StructAutomate ribbon tab.'
    $pattern=$null
    Assert-Review ($tab.TryGetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern,[ref]$pattern)) 'Ribbon selection pattern unavailable.'
    $pattern.Select()
    $buttonCondition=[Windows.Automation.AndCondition]::new(
        [Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::NameProperty,'Review Beams'),
        [Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Button))
    $timer=[Diagnostics.Stopwatch]::StartNew()
    do { $button=$root.FindFirst([Windows.Automation.TreeScope]::Descendants,$buttonCondition); if ($null -ne $button) { break }; Start-Sleep -Milliseconds 100 } while ($timer.Elapsed.TotalSeconds -lt 5)
    if ($null -eq $button) {
        $observed=$root.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Button))
        $receipt.ribbon_observed_buttons=@($observed | ForEach-Object { $_.Current.Name } | Select-Object -First 70)
        throw ('Observed ribbon has no Review Beams button. Buttons: '+($receipt.ribbon_observed_buttons -join ', '))
    }
    $invoke=$null
    Assert-Review ($button.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern,[ref]$invoke)) 'Review button has no invocation pattern.'
    $receipt.ribbon=[ordered]@{ name=$button.Current.Name; automation_id=$button.Current.AutomationId; process_id=$button.Current.ProcessId }
    $invoke.Invoke()
}
try {
    $xll=[IO.Path]::GetFullPath($XllPath); $snapshot=[IO.Path]::GetFullPath($SnapshotPath)
    $receipt.xll=Get-StructAutomateFileIdentity $xll; $receipt.snapshot=Get-StructAutomateFileIdentity $snapshot
    if (-not $DevelopmentSmoke) {
        Assert-Review ([bool]$ExerciseRibbon) 'Final acceptance requires the real ribbon path.'
        Assert-Review (-not [string]::IsNullOrWhiteSpace($LegacyWorkbookPath)) 'Final acceptance requires an old saved workbook for migration.'
        $null=Assert-StructAutomateSafeInstallPath $xll
        $manifest=Get-Content -LiteralPath (Join-Path (Split-Path $xll -Parent) 'manifest.json') -Raw | ConvertFrom-Json
        $signature=Get-AuthenticodeSignature -LiteralPath $xll
        Assert-Review ($manifest.signed_xll.sha256 -ceq $receipt.xll.sha256 -and [string]$signature.Status -eq 'Valid' -and $signature.SignerCertificate.Thumbprint -ceq $manifest.signature.thumbprint) 'Exact installed signature/manifest binding failed.'
        Assert-Review (@(Get-StructAutomateExcelStartupRegistrations -XllPath $xll).Count -gt 0) 'Exact startup registration missing.'
        $receipt.manifest=$manifest
    }
    $excel=New-Object -ComObject Excel.Application
    $processes=@(Get-Process -Name EXCEL)
    Assert-Review ($processes.Count -eq 1) 'Owned Excel identity is ambiguous.'
    $processId=[int]$processes[0].Id; $books=$excel.Workbooks
    Assert-Review ($books.Count -eq 0) 'Owned Excel unexpectedly has workbooks.'
    Assert-Review ([bool]$excel.RegisterXLL($xll)) 'Exact XLL registration failed.'
    $excel.Visible=[bool]$ExerciseRibbon; $excel.DisplayAlerts=$false; $excel.AskToUpdateLinks=$false
    if ($ExerciseRibbon) { $excel.WindowState=-4137 }
    $book=$books.Add()
    $setup=Invoke-ReviewMacro 'STR_XL_ASSUMPTIONS'; Assert-Review ($setup.state -eq 'completed') $setup.message
    $import=Invoke-ReviewMacro 'STR_XL_IMPORT_SNAPSHOT_FILE' @($snapshot,$receipt.snapshot.sha256,(Join-Path $output 'store'))
    Assert-Review ($import.state -eq 'completed') $import.message
    $null=Wait-Review
    if ($ExerciseRibbon) { Invoke-ReviewRibbon } else { $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; Assert-Review ($start.state -eq 'started') $start.message }
    $initial=Wait-Review; $result=Read-ReviewResult $initial
    Assert-Review ($result.members.Count -eq 3 -and $result.workflow_complete) 'Review omitted a member.'
    Assert-Review ($result.snapshot_sha256 -ceq '9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84') 'Wrong retained fixture.'
    $member=$result.members[0].member_id
    Assert-Review (@($result.members | Where-Object { $null -ne $_.full_design }).Count -eq 0) 'Provisional review became full design.'
    Assert-Review ((Review-Field $initial $member 'design.fire_minutes').value -eq '60') 'Required fire rating was lost.'
    Assert-Review (@($result.members | Where-Object { $_.core.state -ne 'complete' }).Count -eq 0) 'Independent core did not finish for the owned beams.'
    foreach ($m in $result.members) {
        Assert-Review (@($m.stages | Where-Object { $_.stage_id -in @('fire','serviceability') -and $_.availability -eq 'unavailable' }).Count -eq 2) 'Fire or missing service evidence was incorrectly qualified.'
    }
    $receipt.checks.Add([ordered]@{ row='R01/R02/R05'; name='blank_supplemental_inputs_continue_with_fire_and_service_pending'; members=$result.members.Count; passed=$true })
    $beforeDepth=$result.members[0].core.design.arrangement.bottom_effective_depth_mm
    Set-ReviewCell 'Assumptions' 'B11' '40'
    $changed=Wait-Review; $result=Read-ReviewResult $changed
    Assert-Review ($changed.details.resolved.members[0].inputs.member_contexts[0].nominal_cover_mm -eq 40) 'Cover edit did not reach the actual typed request.'
    Assert-Review ($result.members[0].core.design.arrangement.bottom_effective_depth_mm -ne $beforeDepth) 'Cover edit did not change actual bar depth.'
    $receipt.checks.Add([ordered]@{ row='R03'; name='cover_edit_changes_actual_request_and_depth'; before=$beforeDepth; after=$result.members[0].core.design.arrangement.bottom_effective_depth_mm; passed=$true })
    if ($OwnershipProbe) {
        $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $other=$books.Add()
        $null=Wait-ReviewDispatch $start.details.request_id 'committed'
        $receipt.checks.Add([ordered]@{ row='R08'; name='focused_inactive_workbook_completion'; passed=$true })
    }
    elseif (-not $Smoke) {
        Set-ReviewCell 'Assumptions' 'B11' ''
        $blank=Wait-Review
        Assert-Review ((Review-Field $blank $member 'design.cover').entered_text -eq '' -and $blank.details.resolved.members[0].inputs.member_contexts[0].nominal_cover_mm -eq 40) 'Blank edit lost text or last valid cover.'
        $sheets=$null; $sheet=$null; $cell=$null
        try { $sheets=$book.Worksheets; $sheet=$sheets.Item('Assumptions'); $cell=$sheet.Range('B11'); $cell.NumberFormat='@'; $cell.Value2='=1+1' }
        finally { Release-StructAutomateComObject $cell; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
        $invalid=Wait-Review
        Assert-Review ((Review-Field $invalid $member 'design.cover').entered_text -eq '=1+1' -and $invalid.details.resolved.members[0].inputs.member_contexts[0].nominal_cover_mm -eq 40) 'Formula text was not retained as an invalid entry.'
        $receipt.checks.Add([ordered]@{ row='R04'; name='blank_and_formula_use_persisted_valid_fallback'; passed=$true })
        Set-ReviewCell 'Assumptions' 'B11' '40'; $null=Wait-Review
        Set-ReviewCell 'Assumptions' 'B24' '90'
        $priced=Wait-Review; $pricedResult=Read-ReviewResult $priced
        Assert-Review ($pricedResult.members[0].core.effective_input_id -ceq $result.members[0].core.effective_input_id) 'Rate edit changed structural inputs.'
        Assert-Review ($pricedResult.members[0].cost.result.outputs.total_decimal -eq '19200.00' -and $pricedResult.members[0].cost.availability -eq 'example') 'Separate illustrative cost did not refresh.'
        $receipt.checks.Add([ordered]@{ row='R10'; name='rates_reprice_same_separate_example_quantities'; quantity_id=$pricedResult.members[0].cost.result.outputs.quantity_result_id; passed=$true })
        $dispatches=$priced.details.dispatch_count
        $sheets=$null; $sheet=$null; $range=$null
        try {
            $sheets=$book.Worksheets; $sheet=$sheets.Item('Assumptions'); $range=$sheet.Range('B6:B25'); $existing=$range.Value2
            $values=New-Object 'object[,]' 20,1
            for ($r=0;$r -lt 20;$r++) { $values[$r,0]=[string]$existing[($r+1),1] }
            $values[2,0]='30'; $values[3,0]='415'; $values[4,0]='415'; $values[9,0]='16'; $values[10,0]='10'; $values[12,0]='9000'
            $range.Value2=$values
        }
        finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
        $edited=Wait-Review; $editedResult=Read-ReviewResult $edited
        Assert-Review ($edited.details.dispatch_count -eq ($dispatches+1)) 'One pasted edit did not coalesce into one refresh.'
        $capacity=@($editedResult.members[0].core.design.checks | Where-Object rule_id -eq 'flexure')[0].result.effective_inputs.capacity_request.value
        Assert-Review ($capacity.concrete_strength_n_per_mm2 -eq 30 -and $capacity.steel_yield_strength_n_per_mm2 -eq 415) 'Edited strengths did not reach the actual leaf request.'
        Assert-Review (@($capacity.bars | Where-Object diameter_mm -ne 16).Count -eq 0 -and $editedResult.members[0].core.design.arrangement.link.diameter_mm -eq 10) 'Edited bar/link catalogue did not reach actual reinforcement.'
        Assert-Review ($edited.details.resolved.members[0].inputs.catalogue.stock_lengths_mm[0] -eq 9000) 'Stock edit did not reach the typed search input.'
        $receipt.checks.Add([ordered]@{ row='R03/R08'; name='one_paste_one_refresh_actual_strengths_bars_links_stock'; fck=$capacity.concrete_strength_n_per_mm2; fy=$capacity.steel_yield_strength_n_per_mm2; passed=$true })
        $ids=@($editedResult.members | ForEach-Object member_id)
        $excel.EnableEvents=$false
        try {
            Set-ReviewOverride $ids[1] 'member.support' 'Continuous'
            foreach ($pair in @(@('detailing.stock','100'),@('detailing.bars','12'),@('detailing.links','8'),@('detailing.link_spacings','150'),@('detailing.bar_counts','2'),@('detailing.layers','1'))) {
                Set-ReviewOverride $ids[2] $pair[0] $pair[1]
            }
        }
        finally { $excel.EnableEvents=$true }
        $null=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $mixed=Wait-Review; $mixedResult=Read-ReviewResult $mixed
        Assert-Review (($mixedResult.members.core.state -join ',') -ceq 'complete,unsupported,no_feasible_arrangement') 'Mixed review lost supported/unsupported/no-fit outcomes.'
        $excel.EnableEvents=$false
        try {
            Set-ReviewOverride $ids[1] 'member.support' 'SimplySupported'
            Set-ReviewOverride $ids[2] 'detailing.stock' '9000'; Set-ReviewOverride $ids[2] 'detailing.bars' '16'; Set-ReviewOverride $ids[2] 'detailing.links' '10'
        }
        finally { $excel.EnableEvents=$true }
        $null=Invoke-ReviewMacro 'STR_XL_TEST_REVIEW_MEMBER_FAILURE' @($ids[0]); $failed=Wait-Review; $failedResult=Read-ReviewResult $failed
        Assert-Review ($failedResult.members.Count -eq 3 -and $null -eq $failedResult.members[0].core -and $null -ne $failedResult.members[0].example_core -and @($failedResult.members | Where-Object { $null -ne $_.core -and $_.core.state -eq 'complete' }).Count -eq 2) 'Injected failure blocked peers or hid the original outcome.'
        $receipt.checks.Add([ordered]@{ row='R06'; name='mixed_outcomes_and_injected_failure_preserve_all_members'; passed=$true })
        if ($RetainedSnapshotPath) {
            $retained=Invoke-ReviewMacro 'STR_XL_TEST_REVIEW_RETAINED' @([IO.Path]::GetFullPath($RetainedSnapshotPath))
            Assert-Review ($retained.details.members -eq 153 -and $retained.details.maximum_axial_kn -gt .02 -and $retained.details.outcome -eq 'Unsupported' -and $retained.details.vectors_preserved -and $retained.details.diagnostics -contains 'ACTION.UNSUPPORTED_COMPONENT') 'Known retained axial actions were erased or admitted.'
            $receipt.retained=$retained.details
            $receipt.checks.Add([ordered]@{ row='R05'; name='retained_nonzero_source_actions_preserved_and_unsupported'; passed=$true })
        }
        elseif (-not $DevelopmentSmoke) { throw 'Final R05 acceptance requires the retained group-reference snapshot path.' }
        $null=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $null=Wait-Review
        $binding=Invoke-ReviewMacro 'STR_XL_TEST_REVIEW_MODEL_BINDING'
        Assert-Review ($binding.details.same_member_id -and $binding.details.different_model -and $binding.details.original_fck -eq 30 -and $binding.details.other_fck -eq 25 -and $binding.details.retained_project_cover -eq 40) 'Source-specific override leaked across model identities.'
        $receipt.model_binding=$binding.details
        $workbookPath=Join-Path $output 'review.xlsx'; $book.SaveAs($workbookPath,51)
        for ($i=1;$i -le 2;$i++) {
            $book.Close($false); Release-StructAutomateComObject $book; $book=$null
            $book=$books.Open($workbookPath); $reopened=Wait-Review
            Assert-Review ($reopened.details.resolved.members[0].inputs.member_contexts[0].nominal_cover_mm -eq 40) 'Reopen reset a saved edit.'
            $book.Save()
        }
        $receipt.checks.Add([ordered]@{ row='R07'; name='saved_workbook_reopened_twice_with_origins'; passed=$true })
        $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'
        Set-ReviewCell 'Assumptions' 'B11' '41'
        $newer=Wait-Review
        Assert-Review ($newer.details.resolved.members[0].inputs.member_contexts[0].nominal_cover_mm -eq 41) 'Edit during computation was overwritten by obsolete work.'
        $null=Wait-ReviewDispatch $start.details.request_id 'obsolete completion discarded'
        Set-ReviewCell 'Assumptions' 'B11' '40'; $null=Wait-Review
        $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $other=$books.Add()
        $null=Wait-ReviewDispatch $start.details.request_id 'committed'
        $sheets=$null; $sheet=$null
        try {
            $sheets=$other.Worksheets
            for ($i=1;$i -le $sheets.Count;$i++) {
                $sheet=$sheets.Item($i)
                Assert-Review ([string]$sheet.Name -notin @('Review Inputs','Provisional Review','Review Evidence')) 'Completion wrote into the other active workbook.'
                Release-StructAutomateComObject $sheet; $sheet=$null
            }
        }
        finally { Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
        $other.Close($false); Release-StructAutomateComObject $other; $other=$null; $book.Activate()
        $book.Save(); $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $book.Close($false); Release-StructAutomateComObject $book; $book=$null
        $null=Wait-ReviewDispatch $start.details.request_id 'obsolete completion discarded'
        $book=$books.Open($workbookPath); $restored=Wait-Review
        $receipt.checks.Add([ordered]@{ row='R08'; name='edit_switch_and_close_discard_obsolete_completions'; passed=$true })
        $missingResult=Assert-OwnedReviewPath (Join-Path $restored.details.directory $restored.details.result.file_name)
        $retainedResult=Assert-OwnedReviewPath ($missingResult+'.retained')
        Move-Item -LiteralPath $missingResult -Destination $retainedResult
        $null=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $regenerated=Wait-Review
        Assert-Review (Test-Path -LiteralPath $missingResult) 'Missing result was not regenerated from retained inputs/source.'
        $sources=@(Get-ChildItem -LiteralPath (Join-Path $output 'store') -Recurse -File -Filter '*.sasnap')
        Assert-Review ($sources.Count -eq 1) 'Owned snapshot path is ambiguous.'
        $sourcePath=Assert-OwnedReviewPath $sources[0].FullName; $retainedSource=Assert-OwnedReviewPath ($sourcePath+'.retained')
        Move-Item -LiteralPath $sourcePath -Destination $retainedSource
        $null=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $missing=Wait-Review; $missingReview=Read-ReviewResult $missing
        Assert-Review (@($missingReview.members | Where-Object { $null -ne $_.core -or $null -eq $_.example_core -or $_.source_status -notlike 'Unavailable*' }).Count -eq 0) 'Missing source was presented as live/current engineering.'
        Move-Item -LiteralPath $retainedSource -Destination $sourcePath
        $null=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $null=Wait-Review
        $receipt.checks.Add([ordered]@{ row='R09'; name='missing_result_regenerated_missing_source_has_separate_example'; passed=$true })
        Set-ReviewOverride $ids[0] 'member.depth' '550'; $alternative=Wait-Review; $alternativeResult=Read-ReviewResult $alternative
        Assert-Review ($alternative.details.resolved.members[0].analysis_alternative -and @($alternativeResult.members[0].stages | Where-Object { $_.stage_id -eq 'section_alternatives' -and $_.status -like '*unverified*' }).Count -eq 1 -and $null -eq $alternativeResult.members[0].full_design) 'Changed section was upgraded without reanalysis.'
        $receipt.checks.Add([ordered]@{ row='R10'; name='section_alternative_and_future_stages_remain_unverified'; passed=$true })
        $start=Invoke-ReviewMacro 'STR_XL_PROVISIONAL_REVIEW'; $cancel=Invoke-ReviewMacro 'STR_XL_CANCEL_REVIEW'
        Assert-Review ($cancel.state -eq 'cancelled') 'Cancellation was rejected.'
        Start-Sleep -Milliseconds 500
        $cancelled=Invoke-ReviewMacro 'STR_XL_REVIEW_STATE'
        Assert-Review ($cancelled.state -eq 'cancelled' -and $null -eq $cancelled.details.dispatch_id) 'Cancelled review retried automatically.'
        $receipt.checks.Add([ordered]@{ row='R08'; name='explicit_cancel_is_not_retried'; passed=$true })
        if (-not [string]::IsNullOrWhiteSpace($LegacyWorkbookPath)) {
            $book.Close($false); Release-StructAutomateComObject $book; $book=$null
            $legacySource=Get-StructAutomateFileIdentity $LegacyWorkbookPath
            $legacyCopy=Assert-OwnedReviewPath (Join-Path $output 'migrated-legacy.xlsx')
            Copy-Item -LiteralPath $LegacyWorkbookPath -Destination $legacyCopy
            $book=$books.Open($legacyCopy)
            $sheets=$null; $sheet=$null; $range=$null
            try {
                $sheets=$book.Worksheets; $sheet=$sheets.Item('Design Inputs'); $range=$sheet.UsedRange; $oldCells=$range.Value2
                $oldCover=$null
                for ($r=2;$r -le $oldCells.GetLength(0);$r++) {
                    if ([string]$oldCells[$r,2] -ceq $ids[0] -and [string]$oldCells[$r,3] -ceq 'nominal_cover_mm') { $oldCover=[string]$oldCells[$r,4] }
                }
            }
            finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $sheet; Release-StructAutomateComObject $sheets }
            Assert-Review ($null -ne $oldCover) 'Old workbook has no explicit owned-member cover.'
            # Rebind the copied workbook to an owned store before new review artifacts are written.
            $import=Invoke-ReviewMacro 'STR_XL_IMPORT_SNAPSHOT_FILE' @($snapshot,$receipt.snapshot.sha256,(Join-Path $output 'legacy-store'))
            Assert-Review ($import.state -eq 'completed') $import.message
            $migrated=Wait-Review; $migratedCover=Review-Field $migrated $ids[0] 'design.cover'
            Assert-Review ($migratedCover.value -eq $oldCover -and $migratedCover.origin -eq 'override') 'Migration reset an explicit old-workbook edit.'
            $book.Save(); $book.Close($false); Release-StructAutomateComObject $book; $book=$null
            Assert-Review ((Get-StructAutomateFileIdentity $LegacyWorkbookPath).sha256 -ceq $legacySource.sha256) 'Migration modified the prior workbook evidence.'
            $receipt.legacy=[ordered]@{ source=$legacySource; migrated=Get-StructAutomateFileIdentity $legacyCopy; old_cover=$oldCover; effective_cover=$migratedCover.value; origin=$migratedCover.origin }
            $receipt.checks.Add([ordered]@{ row='R11'; name='old_saved_workbook_migrates_without_resetting_edits'; passed=$true })
        }
    }
    $receipt.prompt_responses=0
    if (-not $DevelopmentSmoke) { $receipt.checks.Add([ordered]@{ row='R12'; name='exact_signed_installed_ribbon_completed_without_prompt_responses'; passed=$true }) }
    $receipt.status='passed'; $receipt.scope=if ($Smoke) { 'early_owned_host_smoke' } else { 'integrated_review_scenarios' }
}
catch { $failure=$_.Exception; $receipt.failure=$failure.ToString(); $receipt.status='failed' }
finally {
    if ($null -ne $other) { try { $other.Close($false) } finally { Release-StructAutomateComObject $other } }
    if ($null -ne $book) { try { $book.Close($false) } finally { Release-StructAutomateComObject $book } }
    Release-StructAutomateComObject $books
    Close-StructAutomateExcelApplication $excel
    if ((Get-Variable -Name workbookPath -ErrorAction SilentlyContinue) -and (Test-Path -LiteralPath $workbookPath)) { $receipt.workbook=Get-StructAutomateFileIdentity $workbookPath }
    $exited=$true
    if ($null -ne $processId) {
        $timer=[Diagnostics.Stopwatch]::StartNew()
        while ((Get-Process -Id $processId -ErrorAction SilentlyContinue) -and $timer.Elapsed.TotalSeconds -lt 15) { Start-Sleep -Milliseconds 250 }
        $exited=$null -eq (Get-Process -Id $processId -ErrorAction SilentlyContinue)
    }
    $receipt.cleanup=[ordered]@{ owned_process_id=$processId; exited=$exited }
    if (-not $exited) { $receipt.status='failed'; if ($null -eq $failure) { $failure=[InvalidOperationException]::new('Owned Excel did not exit after cleanup.') } }
    [IO.File]::WriteAllText((Join-Path $output 'receipt.json'),($receipt | ConvertTo-Json -Depth 40),[Text.UTF8Encoding]::new($false))
}
if ($null -ne $failure) { throw $failure }
$receipt | ConvertTo-Json -Depth 10
