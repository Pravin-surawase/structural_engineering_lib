[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$XllPath,
    [Parameter(Mandatory)][int]$EtabsProcessId,
    [Parameter(Mandatory)][string]$ExpectedModelPath,
    [Parameter(Mandatory)][int]$ExpectedFrames,
    [Parameter(Mandatory)][int]$ExpectedPoints,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [switch]$DevelopmentPackage
)

. (Join-Path $PSScriptRoot 'Common.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Require-Connection([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Macro([string]$Name, [object[]]$Arguments = @()) {
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $raw = switch ($Arguments.Count) {
        0 { $script:excel.Run($Name) }
        1 { $script:excel.Run($Name, $Arguments[0]) }
        default { throw 'Unsupported acceptance macro arity.' }
    }
    $watch.Stop()
    $script:macros.Add([ordered]@{name=$Name;arguments=$Arguments;milliseconds=$watch.Elapsed.TotalMilliseconds;result=$raw})
    return $raw
}
function Json-Macro([string]$Name, [object[]]$Arguments = @()) { (Macro $Name $Arguments) | ConvertFrom-Json }
function Await-Connection([scriptblock]$Predicate, [string]$Message, [int]$Seconds = 150) {
    $until = [DateTimeOffset]::UtcNow.AddSeconds($Seconds)
    do {
        if (& $Predicate) { return }
        Start-Sleep -Milliseconds 200
    } while ([DateTimeOffset]::UtcNow -lt $until)
    throw $Message
}
function Close-ConnectionBook($Book) {
    if ($null -ne $Book) { try { $Book.Close($false) } finally { Release-StructAutomateComObject $Book } }
}

$output = [IO.Path]::GetFullPath($OutputDirectory)
Require-Connection (-not (Test-Path -LiteralPath $output)) 'Use a new external evidence directory.'
$repository = (Get-StructAutomateRepositoryRoot).TrimEnd('\') + '\'
Require-Connection (-not $output.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase)) 'Acceptance evidence must stay outside the repository.'
New-Item -ItemType Directory -Path $output | Out-Null
$macros = [Collections.Generic.List[object]]::new()
$receipt = [ordered]@{schema_version='structautomate.etabs-connection-acceptance/v1';installed_acceptance=(-not $DevelopmentPackage);started_utc=[DateTimeOffset]::UtcNow.ToString('o');passed=$false;source_commit=$null;xll=$null;worker=$null;source_before=$null;source_after=$null;context=$null;macro_evidence=$macros;cleanup=@{excel_exited=$false;workers_exited=$false;startup_restored=$false};failure=$null}
$excel=$null; $books=$null; $bookA=$null; $bookB=$null; $bookC=$null; $ownedExcelId=$null; $startupPreimage=@(); $failure=$null
try {
    Require-Connection (-not (Get-Process -Name EXCEL -ErrorAction SilentlyContinue)) 'Close user Excel before this owned-host acceptance.'
    $xll = [IO.Path]::GetFullPath($XllPath)
    if (-not $DevelopmentPackage) { $xll = Assert-StructAutomateSafeInstallPath $xll }
    $package = Split-Path -Parent $xll
    $manifest = Get-Content -LiteralPath (Join-Path $package 'manifest.json') -Raw | ConvertFrom-Json
    $worker = Join-Path $package 'StructAutomate.EtabsWorker.exe'
    $receipt.source_commit = [string]$manifest.source_commit
    $receipt.xll = Get-StructAutomateFileIdentity $xll
    $receipt.worker = Get-StructAutomateFileIdentity $worker
    Require-Connection ($receipt.xll.sha256 -ceq $manifest.signed_xll.sha256) 'XLL bytes differ from the exact package.'
    Require-Connection ($receipt.worker.sha256 -ceq $manifest.worker.sha256) 'Worker bytes differ from the exact package.'
    foreach ($binary in @($xll,$worker)) {
        $signature=Get-AuthenticodeSignature -LiteralPath $binary
        Require-Connection ([string]$signature.Status -eq 'Valid' -and $signature.SignerCertificate.Thumbprint -eq $manifest.signature.thumbprint) 'Both binaries require the exact valid package signer.'
        Require-Connection ((Get-StructAutomatePeMachine $binary) -eq 'AMD64') 'Both binaries must be AMD64.'
    }
    $etabs=Get-Process -Id $EtabsProcessId
    Require-Connection ($etabs.ProcessName -eq 'ETABS') 'Selected process is not ETABS.'
    $etabsStart=$etabs.StartTime.ToUniversalTime()
    $receipt.source_before=Get-StructAutomateFileIdentity $ExpectedModelPath
    if ($DevelopmentPackage) {
        $installed=Join-Path (Get-StructAutomateInstallRoot) '0.1.0\StructAutomate.xll'
        $startupPreimage=@(Get-StructAutomateExcelStartupRegistrations -XllPath $installed)
        Write-StructAutomateJson -Value $startupPreimage -Path (Join-Path $output 'startup-preimage.json')
        [void](Unregister-StructAutomateExcelStartup -XllPath $installed)
    }
    else {
        Require-Connection (@(Get-StructAutomateExcelStartupRegistrations -XllPath $xll).Count -eq 1) 'The installed XLL needs its exact startup registration.'
    }
    $excel=New-Object -ComObject Excel.Application
    $excel.Visible=$true; $excel.DisplayAlerts=$false; $excel.AskToUpdateLinks=$false
    $owned=@(Get-Process -Name EXCEL)
    Require-Connection ($owned.Count -eq 1) 'Owned Excel process identity is ambiguous.'
    $ownedExcelId=$owned[0].Id
    $books=$excel.Workbooks
    Require-Connection ($books.Count -eq 0) 'Add-in load created an unsolicited workbook.'
    $bookA=$books.Add()
    if ($DevelopmentPackage) { Require-Connection ([bool]$excel.RegisterXLL($xll)) 'Development XLL did not register.' }
    Await-Connection { [bool](Macro 'STR_XL_TEST_RIBBON_LOADED') } 'Ribbon onLoad was not observed.' 15
    $sheets=$bookA.Worksheets
    try { $initialSheets=[int]$sheets.Count } finally { Release-StructAutomateComObject $sheets }
    $started=Json-Macro 'STR_XL_CONNECT_ETABS_PROCESS' @($EtabsProcessId)
    Require-Connection ($started.state -eq 'started') 'Connect did not start asynchronously.'
    Require-Connection ($macros[$macros.Count-1].milliseconds -lt 5000) 'Connect blocked Excel for five seconds.'
    $duplicate=Json-Macro 'STR_XL_CONNECT_ETABS_PROCESS' @($EtabsProcessId)
    Require-Connection ($duplicate.state -eq 'rejected') 'Duplicate connection was not rejected.'
    $bookB=$books.Add()
    $other=Json-Macro 'STR_XL_CONNECTION_STATUS'
    Require-Connection ($other.state -eq 'disconnected') 'The other workbook inherited a pending connection.'
    Await-Connection { [double](Macro 'STR_XL_TEST_CONNECTION_SESSION_COUNT') -eq 1 } 'No model context reached the initiating workbook.'
    $active=$excel.ActiveWorkbook
    try { Require-Connection ([string]$active.Name -eq [string]$bookB.Name) 'Background completion changed the active workbook.' }
    finally { if ([Runtime.InteropServices.Marshal]::IsComObject($active)) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($active) }; $active=$null }
    Require-Connection ((Json-Macro 'STR_XL_CONNECTION_STATUS').state -eq 'disconnected') 'Background completion attached to the wrong workbook.'
    $bookA.Activate()
    $context=Json-Macro 'STR_XL_CONNECTION_STATUS'
    Require-Connection ($context.state -eq 'completed') 'The source workbook has no accepted context.'
    Require-Connection ($context.details.frame_count -eq $ExpectedFrames -and $context.details.point_count -eq $ExpectedPoints) 'Context counts differ from independently observed source counts.'
    Require-Connection ($context.details.source.ProcessId -eq $EtabsProcessId -and [string]::Equals($context.details.source.ModelPath,[IO.Path]::GetFullPath($ExpectedModelPath),[StringComparison]::OrdinalIgnoreCase)) 'Context source identity differs.'
    Require-Connection (-not $context.details.forces_loaded -and $context.details.engineering -eq 'not_evaluated') 'Connect incorrectly claims force or design completion.'
    $sheets=$bookA.Worksheets
    try { Require-Connection ($sheets.Count -eq $initialSheets) 'Connect created an unsolicited worksheet.' } finally { Release-StructAutomateComObject $sheets }
    $artifactPath=Join-Path $context.details.operation_directory 'context.json'
    $artifact=Get-Content -LiteralPath $artifactPath -Raw | ConvertFrom-Json
    $rawPath=Join-Path $context.details.operation_directory $artifact.Inventory.Provenance.JournalFileName
    $rawBefore=Get-StructAutomateFileIdentity $rawPath
    Require-Connection ($rawBefore.sha256 -ceq $artifact.Inventory.Provenance.JournalSha256) 'Raw getter evidence digest differs.'
    foreach ($frame in @($artifact.Inventory.Frames | Select-Object -First 2)) {
        $review=Json-Macro 'STR_XL_REVIEW_CONTEXT_FRAME' @([string]$frame.SourceFrameId)
        Require-Connection ($review.state -eq 'completed' -and $review.details.etabs_reads -eq 0) 'Frame selection did not use local context.'
    }
    Require-Connection ((Get-StructAutomateFileIdentity $rawPath).sha256 -ceq $rawBefore.sha256) 'Local frame selection changed acquisition evidence.'
    $receipt.context=$context.details
    $receipt.context_artifact=Get-StructAutomateFileIdentity $artifactPath
    $receipt.getter_evidence=$rawBefore
    $bookC=$books.Add()
    Require-Connection ((Json-Macro 'STR_XL_CONNECT_ETABS_PROCESS' @($EtabsProcessId)).state -eq 'started') 'Close-during-connect did not start.'
    Close-ConnectionBook $bookC; $bookC=$null
    $bookB.Activate()
    Await-Connection { [double](Macro 'STR_XL_TEST_CONNECTION_WORKER_COUNT') -eq 0 } 'Reader cleanup remained pending after workbook close.'
    Start-Sleep -Milliseconds 500
    Require-Connection ((Json-Macro 'STR_XL_CONNECTION_STATUS').state -eq 'disconnected') 'A closed workbook completion was applied to another workbook.'
    Require-Connection ([double](Macro 'STR_XL_TEST_CONNECTION_SESSION_COUNT') -eq 1) 'Closing a pending workbook changed the accepted source context.'
    $bookA.Activate()
    $saved=Join-Path $output 'connection-workspace.xlsx'
    $bookA.SaveAs($saved,51)
    Close-ConnectionBook $bookA; $bookA=$null
    Require-Connection ([double](Macro 'STR_XL_TEST_CONNECTION_SESSION_COUNT') -eq 0) 'Closing the workbook did not evict context.'
    $bookA=$books.Open($saved,0,$false)
    Require-Connection ((Json-Macro 'STR_XL_CONNECTION_STATUS').state -eq 'disconnected') 'Reopening incorrectly restored a live connection.'
    $receipt.source_after=Get-StructAutomateFileIdentity $ExpectedModelPath
    Require-Connection ($receipt.source_before.sha256 -ceq $receipt.source_after.sha256) 'The source model file changed.'
    Require-Connection ((Get-Process -Id $EtabsProcessId).StartTime.ToUniversalTime() -eq $etabsStart) 'The ETABS source process changed.'
    $receipt.passed=$true
}
catch { $failure=$_.Exception.Message; $receipt.failure=$failure; $receipt.failure_location=$_.ScriptStackTrace }
finally {
    try { Close-ConnectionBook $bookC; Close-ConnectionBook $bookA; Close-ConnectionBook $bookB; Release-StructAutomateComObject $books } catch { if (-not $failure) { $failure=$_.Exception.Message; $receipt.failure=$failure }; $receipt.book_cleanup_failure=$_.Exception.Message }
    if ($null -ne $excel) {
        try {
            Close-StructAutomateExcelApplication $excel
            $limit=[DateTimeOffset]::UtcNow.AddSeconds(20)
            while ($ownedExcelId -and (Get-Process -Id $ownedExcelId -ErrorAction SilentlyContinue) -and [DateTimeOffset]::UtcNow -lt $limit) { Start-Sleep -Milliseconds 200 }
            Require-Connection (-not (Get-Process -Id $ownedExcelId -ErrorAction SilentlyContinue)) 'Owned Excel did not exit normally.'
            $receipt.cleanup.excel_exited=$true
            $receipt.cleanup.workers_exited=-not (Get-Process -Name StructAutomate.EtabsWorker -ErrorAction SilentlyContinue)
        } catch { if (-not $failure) { $failure=$_.Exception.Message; $receipt.failure=$failure }; $receipt.excel_cleanup_failure=$_.Exception.Message }
    }
    try {
        foreach ($registration in $startupPreimage) {
            New-ItemProperty -Path $registration.registry_path -Name $registration.value_name -PropertyType String -Value $registration.value -Force | Out-Null
        }
        $receipt.cleanup.startup_restored=$true
    } catch { if (-not $failure) { $failure=$_.Exception.Message; $receipt.failure=$failure }; $receipt.startup_cleanup_failure=$_.Exception.Message }
    if ($failure) { $receipt.passed=$false }
    $receipt.completed_utc=[DateTimeOffset]::UtcNow.ToString('o')
    Write-StructAutomateJson -Value $receipt -Path (Join-Path $output 'receipt.json') -Depth 40
}
$receipt | ConvertTo-Json -Depth 40
if ($failure) { throw $failure }
