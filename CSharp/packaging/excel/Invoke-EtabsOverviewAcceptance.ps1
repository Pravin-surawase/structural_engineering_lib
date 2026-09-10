#requires -Version 7.5
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$XllPath,
    [Parameter(Mandatory)][int]$EtabsProcessId,
    [Parameter(Mandatory)][string]$ExpectedModelPath,
    [Parameter(Mandatory)][int]$ExpectedFrames,
    [Parameter(Mandatory)][int]$ExpectedPoints,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$ForceMemberId,
    [int]$ExpectedForceRows
)

. (Join-Path $PSScriptRoot 'Common.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Require-Overview([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Macro([string]$Name, [object[]]$Arguments = @()) {
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $raw = if ($Arguments.Count -eq 0) { $script:excel.Run($Name) } else { $script:excel.Run($Name, $Arguments[0]) }
    $watch.Stop()
    $script:macros.Add([ordered]@{name=$Name;milliseconds=$watch.Elapsed.TotalMilliseconds;result=$raw})
    return $raw
}
function Json-Macro([string]$Name, [object[]]$Arguments = @()) { (Macro $Name $Arguments) | ConvertFrom-Json -DateKind String }
function Await-Overview([scriptblock]$Predicate, [string]$Message, [int]$Seconds = 150) {
    $until = [DateTimeOffset]::UtcNow.AddSeconds($Seconds)
    do { if (& $Predicate) { return }; Start-Sleep -Milliseconds 200 } while ([DateTimeOffset]::UtcNow -lt $until)
    throw $Message
}
function Sheet-Count($Book) {
    $sheets = $Book.Worksheets
    try { return [int]$sheets.Count } finally { Release-StructAutomateComObject $sheets }
}
function Close-Book($Book) {
    if ($null -ne $Book) { try { $Book.Close($false) } finally { Release-StructAutomateComObject $Book } }
}

$output = [IO.Path]::GetFullPath($OutputDirectory)
Require-Overview (-not (Test-Path -LiteralPath $output)) 'Use a new external evidence directory.'
Require-Overview (-not $output.StartsWith((Get-StructAutomateRepositoryRoot).TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) 'Evidence must remain outside the repository.'
New-Item -ItemType Directory -Path $output | Out-Null
$macros = [Collections.Generic.List[object]]::new()
$receipt = [ordered]@{schema_version='structautomate.etabs-overview-excel-development/v1';passed=$false;installed_package_changed=$false;pf9_acceptance=$false;macro_evidence=$macros;cleanup=@{};failure=$null}
$excel=$null; $books=$null; $bookA=$null; $bookB=$null; $bookC=$null; $ownedExcel=$null; $startupPreimage=@(); $failure=$null
$startupTouched=$false
$installed = Join-Path (Get-StructAutomateInstallRoot) '0.1.0\StructAutomate.xll'
try {
    Require-Overview (-not (Get-Process -Name EXCEL -ErrorAction SilentlyContinue)) 'Owned-host acceptance requires no user Excel process.'
    $package = Split-Path -Parent ([IO.Path]::GetFullPath($XllPath))
    $manifest = Get-Content -LiteralPath (Join-Path $package 'manifest.json') -Raw | ConvertFrom-Json -DateKind String
    $receipt.xll = Get-StructAutomateFileIdentity $XllPath
    $receipt.worker = Get-StructAutomateFileIdentity (Join-Path $package 'StructAutomate.EtabsWorker.exe')
    Require-Overview ($receipt.xll.sha256 -ceq $manifest.signed_xll.sha256 -and $receipt.worker.sha256 -ceq $manifest.worker.sha256) 'Candidate package hashes differ.'
    foreach ($binary in @($XllPath,(Join-Path $package 'StructAutomate.EtabsWorker.exe'))) {
        $signature = Get-AuthenticodeSignature -LiteralPath $binary
        Require-Overview ([string]$signature.Status -eq 'Valid' -and $signature.SignerCertificate.Thumbprint -eq $manifest.signature.thumbprint) 'The candidate requires its exact valid development signer.'
    }
    $etabs = Get-Process -Id $EtabsProcessId
    Require-Overview ($etabs.ProcessName -eq 'ETABS') 'Selected process is not ETABS.'
    $sourceStart = $etabs.StartTime.ToUniversalTime()
    $receipt.source_before = Get-StructAutomateFileIdentity $ExpectedModelPath
    # Temporarily suppress only the installed StructAutomate startup entry, retaining its exact preimage.
    # No installed binary or candidate startup registration is written.
    $startupPreimage = @(Get-StructAutomateExcelStartupRegistrations -XllPath $installed)
    Write-StructAutomateJson -Value $startupPreimage -Path (Join-Path $output 'startup-preimage.json')
    [void](Unregister-StructAutomateExcelStartup -XllPath $installed)
    $startupTouched=$true
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible=$true; $excel.DisplayAlerts=$false; $excel.AskToUpdateLinks=$false
    $owned = @(Get-Process -Name EXCEL)
    Require-Overview ($owned.Count -eq 1) 'Owned Excel process identity is ambiguous.'
    $ownedExcel = $owned[0].Id
    $books = $excel.Workbooks
    Require-Overview ($books.Count -eq 0 -and [bool]$excel.RegisterXLL($XllPath)) 'Candidate XLL did not load into an empty owned host.'
    $bookA = $books.Add(); $initialSheets = Sheet-Count $bookA
    Require-Overview ((Json-Macro 'STR_XL_INSPECT_ETABS_PROCESS' @($EtabsProcessId)).state -eq 'started') 'Overview did not start.'
    $bookB = $books.Add()
    Await-Overview { [double](Macro 'STR_XL_TEST_OVERVIEW_SESSION_COUNT') -eq 1 } 'Overview was not accepted.'
    Await-Overview { [double](Macro 'STR_XL_TEST_CONNECTION_WORKER_COUNT') -eq 0 } 'Overview cleanup did not finish.'
    Require-Overview ((Json-Macro 'STR_XL_CONNECTION_STATUS').state -eq 'disconnected') 'Overview attached to another workbook.'
    Require-Overview ([double](Macro 'STR_XL_TEST_CONNECTION_SESSION_COUNT') -eq 0) 'Overview incorrectly created a detailed context.'
    $bookA.Activate()
    $status = Json-Macro 'STR_XL_CONNECTION_STATUS'
    $overview = $status.details.overview
    Require-Overview ($overview.FrameCount -eq $ExpectedFrames -and $overview.PointCount -eq $ExpectedPoints) 'Overview counts differ from source evidence.'
    Require-Overview ($overview.Source.ProcessId -eq $EtabsProcessId -and [string]::Equals($overview.Source.ModelPath,[IO.Path]::GetFullPath($ExpectedModelPath),[StringComparison]::OrdinalIgnoreCase)) 'Overview source differs.'
    Require-Overview (-not $status.details.geometry_loaded -and -not $status.details.forces_loaded) 'Overview misstates acquired coverage.'
    Require-Overview ((Sheet-Count $bookA) -eq $initialSheets) 'Overview created a worksheet.'
    Require-Overview ((Json-Macro 'STR_XL_GET_FORCES').state -eq 'rejected') 'Overview was accepted as detailed force context.'
    $receipt.overview = $status.details
    $receipt.overview_sheets_created = 0
    if ($ForceMemberId) {
        Require-Overview ($ExpectedForceRows -gt 0) 'A scoped force check requires an independently expected row count.'
        Require-Overview ((Json-Macro 'STR_XL_LOAD_ETABS_DETAILS').state -eq 'started') 'Detailed handoff did not start.'
        Await-Overview { [double](Macro 'STR_XL_TEST_CONNECTION_SESSION_COUNT') -eq 1 } 'Detailed context was not accepted.'
        $context = Json-Macro 'STR_XL_CONNECTION_STATUS'
        Require-Overview ($context.details.frame_count -eq $ExpectedFrames) 'Detailed context differs from overview.'
        Require-Overview ((Sheet-Count $bookA) -eq $initialSheets) 'Detailed handoff created a worksheet.'
        Require-Overview ((Json-Macro 'STR_XL_ASSUMPTIONS').state -eq 'completed') 'Assumption setup failed.'
        $beforeForceSheets = Sheet-Count $bookA
        $started = Json-Macro 'STR_XL_GET_FORCES_SCOPE' @($ForceMemberId)
        Require-Overview ($started.state -eq 'started') 'Scoped force read did not start.'
        Await-Overview { [double](Macro 'STR_XL_TEST_FORCE_SESSION_COUNT') -eq 1 } 'Scoped forces were not accepted.' 490
        Await-Overview { [double](Macro 'STR_XL_TEST_CONNECTION_WORKER_COUNT') -eq 0 } 'Force cleanup did not finish.'
        $forces = Json-Macro 'STR_XL_FORCE_STATUS'
        Require-Overview ($forces.details.member_count -eq 1 -and $forces.details.action_count -eq $ExpectedForceRows) 'Force row scope differs.'
        Require-Overview ((Sheet-Count $bookA) -eq $beforeForceSheets) 'Force import created a worksheet dump.'
        $forceDirectory = Join-Path (Split-Path -Parent (Split-Path -Parent $context.details.operation_directory)) ('ForceReads\' + $started.details.request_id)
        $capture = Get-Content -LiteralPath (Join-Path $forceDirectory 'capture.json') -Raw | ConvertFrom-Json -Depth 100 -DateKind String
        $calls = @($capture.Content.Capture.Calls | Where-Object Operation -EQ 'Results.FrameForce')
        Require-Overview ($calls.Count -eq 1 -and $calls[0].Inputs[0] -ceq $ForceMemberId -and $calls[0].Inputs[1] -eq 0) 'The worker read an unrequested force scope.'
        $member = 'member:' + $ForceMemberId
        Require-Overview ((Json-Macro 'STR_XL_WRITE_MEMBER_REVIEW' @($member)).state -eq 'completed') 'Explicit member review failed.'
        $sheets = $bookA.Worksheets; $report = $null; $used = $null; $rows = $null; $columns = $null
        try {
            Require-Overview ($sheets.Count -eq $beforeForceSheets + 1) 'Explicit review did not create exactly one sheet.'
            $report = $sheets.Item('Beam Review'); $used = $report.UsedRange; $rows = $used.Rows; $columns = $used.Columns
            Require-Overview ($rows.Count -eq $ExpectedForceRows + 9 -and $columns.Count -eq 13) 'Explicit review dimensions differ from the complete selected-member actions.'
            $receipt.review = @{action_rows=$ExpectedForceRows;sheet_rows=[int]$rows.Count;sheet_columns=[int]$columns.Count;force_sheets_created=0;explicit_review_sheets_created=1;force_calls=1;group_force_calls=0}
        } finally { foreach ($value in @($columns,$rows,$used,$report,$sheets)) { Release-StructAutomateComObject $value } }
    }
    $bookC = $books.Add()
    Require-Overview ((Json-Macro 'STR_XL_INSPECT_ETABS_PROCESS' @($EtabsProcessId)).state -eq 'started') 'Close-during-overview did not start.'
    Close-Book $bookC; $bookC=$null
    $bookB.Activate()
    Start-Sleep -Milliseconds 500
    Await-Overview { [double](Macro 'STR_XL_TEST_CONNECTION_WORKER_COUNT') -eq 0 } 'Closed workbook reader did not clean up.'
    Require-Overview ((Json-Macro 'STR_XL_CONNECTION_STATUS').state -eq 'disconnected') 'A closed workbook applied overview elsewhere.'
    $receipt.source_after = Get-StructAutomateFileIdentity $ExpectedModelPath
    Require-Overview ($receipt.source_before.sha256 -ceq $receipt.source_after.sha256 -and (Get-Process -Id $EtabsProcessId).StartTime.ToUniversalTime() -eq $sourceStart) 'Source file or process changed.'
    $receipt.passed = $true
} catch { $failure=$_.Exception.Message; $receipt.failure=$failure; $receipt.failure_location=$_.ScriptStackTrace }
finally {
    try {
        Close-Book $bookC; Close-Book $bookA; Close-Book $bookB; Release-StructAutomateComObject $books
        if ($null -ne $excel) {
            Close-StructAutomateExcelApplication $excel
            $until = [DateTimeOffset]::UtcNow.AddSeconds(20)
            while ((Get-Process -Id $ownedExcel -ErrorAction SilentlyContinue) -and [DateTimeOffset]::UtcNow -lt $until) { Start-Sleep -Milliseconds 200 }
            Require-Overview (-not (Get-Process -Id $ownedExcel -ErrorAction SilentlyContinue)) 'Owned Excel did not exit.'
            $receipt.cleanup.excel_exited = $true
        }
    } catch { $failure=$_.Exception.Message; $receipt.cleanup.failure=$failure }
    try {
        if ($startupTouched) {
        foreach ($registration in $startupPreimage) { New-ItemProperty -Path $registration.registry_path -Name $registration.value_name -PropertyType String -Value $registration.value -Force | Out-Null }
        $restored = @(Get-StructAutomateExcelStartupRegistrations -XllPath $installed)
        Require-Overview (($restored | ConvertTo-Json -Depth 5 -Compress) -ceq ($startupPreimage | ConvertTo-Json -Depth 5 -Compress)) 'Startup preimage was not restored.'
        $receipt.cleanup.startup_restored = $true
        }
    } catch { $failure=$_.Exception.Message; $receipt.cleanup.startup_failure=$failure }
    if ($failure) { $receipt.passed=$false }
    Write-StructAutomateJson -Value $receipt -Path (Join-Path $output 'receipt.json') -Depth 40
}
if ($failure) { throw $failure }
[pscustomobject]@{passed=$receipt.passed;receipt=(Join-Path $output 'receipt.json');overview_sheets_created=0}
