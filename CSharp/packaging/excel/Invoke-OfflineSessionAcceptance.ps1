[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InstalledXllPath,
    [Parameter(Mandatory)][string]$SnapshotPath,
    [Parameter(Mandatory)][ValidatePattern('^[a-fA-F0-9]{64}$')][string]$ExpectedSnapshotSha256,
    [Parameter(Mandatory)][string]$OutputDirectory
)

. (Join-Path $PSScriptRoot 'Common.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-OfflineAcceptance {
    param([Parameter(Mandatory)][bool]$Condition, [Parameter(Mandatory)][string]$Message)
    if (-not $Condition) { throw $Message }
}

function Get-OfflineSha256Text {
    param([Parameter(Mandatory)][string]$Text)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return -join @($sha.ComputeHash([Text.UTF8Encoding]::new($false).GetBytes($Text)) | ForEach-Object { $_.ToString('x2') })
    }
    finally { $sha.Dispose() }
}

function Get-OfflineObjectSha256 {
    param([AllowNull()][object]$Value)
    return Get-OfflineSha256Text -Text ($Value | ConvertTo-Json -Depth 30 -Compress)
}

function Get-OfflineSheetNames {
    param([Parameter(Mandatory)][object]$Workbook)
    $sheets = $null
    try {
        $sheets = $Workbook.Worksheets
        return @(for ($index = 1; $index -le [int]$sheets.Count; $index++) {
            $sheet = $null
            try { $sheet = $sheets.Item($index); [string]$sheet.Name }
            finally { Release-StructAutomateComObject $sheet }
        })
    }
    finally { Release-StructAutomateComObject $sheets }
}

function Get-OfflineSheet {
    param([Parameter(Mandatory)][object]$Workbook, [Parameter(Mandatory)][string]$Name)
    $sheets = $null
    try {
        $sheets = $Workbook.Worksheets
        for ($index = 1; $index -le [int]$sheets.Count; $index++) {
            $candidate = $null
            try {
                $candidate = $sheets.Item($index)
                if ([string]::Equals([string]$candidate.Name, $Name, [StringComparison]::Ordinal)) {
                    $result = $candidate
                    $candidate = $null
                    return $result
                }
            }
            finally { Release-StructAutomateComObject $candidate }
        }
        return $null
    }
    finally { Release-StructAutomateComObject $sheets }
}

function Get-OfflineMetadata {
    param([Parameter(Mandatory)][object]$Workbook)
    $parts = $null; $selected = $null; $part = $null
    try {
        $parts = $Workbook.CustomXMLParts
        $selected = $parts.SelectByNamespace('urn:structautomate:offline-session:v1')
        if ([int]$selected.Count -eq 0) { return $null }
        if ([int]$selected.Count -ne 1) { throw 'Workbook has ambiguous offline-session metadata.' }
        $part = $selected.Item(1)
        $xml = [xml][string]$part.XML
        return [pscustomobject]@{ xml = [string]$part.XML; state = ($xml.DocumentElement.InnerText | ConvertFrom-Json -ErrorAction Stop) }
    }
    finally {
        Release-StructAutomateComObject $part
        Release-StructAutomateComObject $selected
        Release-StructAutomateComObject $parts
    }
}

function Get-OfflineCellSentinel {
    param([Parameter(Mandatory)][object]$Worksheet, [Parameter(Mandatory)][string]$Address)
    $cell = $null; $comment = $null
    try {
        $cell = $Worksheet.Range($Address)
        $comment = $cell.Comment
        return [ordered]@{
            formula = [string]$cell.Formula
            value = [string]$cell.Value2
            number_format = [string]$cell.NumberFormat
            comment = if ($null -eq $comment) { $null } else { [string]$comment.Text() }
        }
    }
    finally {
        Release-StructAutomateComObject $comment
        Release-StructAutomateComObject $cell
    }
}

function Assert-OfflineCellSentinel {
    param([Parameter(Mandatory)][object]$Worksheet, [Parameter(Mandatory)][object]$Expected)
    $actual = Get-OfflineCellSentinel -Worksheet $Worksheet -Address 'H3'
    Assert-OfflineAcceptance ($actual.formula -ceq $Expected.formula -and
        $actual.value -ceq $Expected.value -and
        $actual.number_format -ceq $Expected.number_format -and
        $actual.comment -ceq $Expected.comment) 'An offline command changed the external formula, comment, or formatting sentinel.'
}

function Get-OfflineRangeFingerprint {
    param([Parameter(Mandatory)][object]$Worksheet, [Parameter(Mandatory)][string]$Address)
    $range = $null
    try {
        $range = $Worksheet.Range($Address)
        return [ordered]@{
            formula_sha256 = Get-OfflineObjectSha256 $range.Formula
            value_sha256 = Get-OfflineObjectSha256 $range.Value2
        }
    }
    finally { Release-StructAutomateComObject $range }
}

function Convert-OfflineSnapshotNumber {
    param([Parameter(Mandatory)][object]$Value)
    return ([double]$Value).ToString('G17', [Globalization.CultureInfo]::InvariantCulture)
}

function Convert-OfflineEnumDisplay {
    param([Parameter(Mandatory)][string]$Token)
    return -join @($Token.Split('_') | ForEach-Object {
        if ($_.Length -eq 0) { return '' }
        $_.Substring(0, 1).ToUpperInvariant() + $_.Substring(1)
    })
}

function Assert-OfflineReviewRows {
    param([Parameter(Mandatory)][object]$Worksheet, [Parameter(Mandatory)][object]$Source)
    $range = $null
    try {
        $range = $Worksheet.Range('A10:M22')
        $actual = $range.Value2
        Assert-OfflineAcceptance ($actual -is [Array] -and $actual.GetLength(0) -eq 13 -and $actual.GetLength(1) -eq 13) 'Beam Review does not contain the exact thirteen-row action footprint.'
        $stations = @{}
        foreach ($station in @($Source.stations)) { $stations[[string]$station.station_id] = $station }
        $rows = @($Source.action_rows)
        for ($index = 0; $index -lt $rows.Count; $index++) {
            $row = $rows[$index]
            $station = $stations[[string]$row.station_id]
            Assert-OfflineAcceptance ($null -ne $station) "Source action row $index references an unknown station."
            $step = if ($null -eq $row.step_number) { '—' } else { Convert-OfflineSnapshotNumber $row.step_number }
            $expected = @(
                [string]$row.row_id,
                [string]$row.output_case_name,
                (Convert-OfflineSnapshotNumber $station.physical_station_mm),
                [string]$row.step_type,
                $step,
                (Convert-OfflineSnapshotNumber $row.p_kn),
                (Convert-OfflineSnapshotNumber $row.v2_kn),
                (Convert-OfflineSnapshotNumber $row.v3_kn),
                (Convert-OfflineSnapshotNumber $row.t_knm),
                (Convert-OfflineSnapshotNumber $row.m2_knm),
                (Convert-OfflineSnapshotNumber $row.m3_knm),
                (Convert-OfflineEnumDisplay ([string]$row.action_basis)),
                [string]$row.source_row_id
            )
            for ($column = 0; $column -lt $expected.Count; $column++) {
                Assert-OfflineAcceptance ([string]$actual[($index + 1), ($column + 1)] -ceq $expected[$column]) "Beam Review action row $index column $column does not preserve the source action, station, or provenance value."
            }
        }
    }
    finally { Release-StructAutomateComObject $range }
}

function Invoke-OfflineMacro {
    param(
        [Parameter(Mandatory)][object]$Excel,
        [Parameter(Mandatory)][string]$Name,
        [object[]]$Arguments = @()
    )
    $timer = [Diagnostics.Stopwatch]::StartNew()
    try {
        $value = switch ($Arguments.Count) {
            0 { $Excel.Run($Name); break }
            1 { $Excel.Run($Name, $Arguments[0]); break }
            2 { $Excel.Run($Name, $Arguments[0], $Arguments[1]); break }
            3 { $Excel.Run($Name, $Arguments[0], $Arguments[1], $Arguments[2]); break }
            default { throw "Offline macro invocation supports at most three arguments: $Name" }
        }
        $text = if ($null -eq $value) { $null } else { [string]$value }
        $json = $null
        if (-not [string]::IsNullOrWhiteSpace($text)) {
            try { $json = $text | ConvertFrom-Json -ErrorAction Stop } catch { }
        }
        return [ordered]@{
            name = $Name
            arguments = @($Arguments)
            available = $true
            elapsed_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3)
            result = $text
            json = $json
            error = $null
        }
    }
    catch {
        return [ordered]@{
            name = $Name
            arguments = @($Arguments)
            available = $false
            elapsed_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3)
            result = $null
            json = $null
            error = $_.Exception.Message
        }
    }
    finally { $timer.Stop() }
}

function Assert-OfflineMacroState {
    param(
        [Parameter(Mandatory)][object]$Evidence,
        [Parameter(Mandatory)][string]$ExpectedState
    )
    Assert-OfflineAcceptance ([bool]$Evidence.available) "Required offline macro is unavailable: $($Evidence.name): $($Evidence.error)"
    Assert-OfflineAcceptance ($null -ne $Evidence.json -and $null -ne $Evidence.json.state) "Offline macro did not return a JSON state: $($Evidence.name)"
    Assert-OfflineAcceptance ([string]$Evidence.json.state -ceq $ExpectedState) "Offline macro $($Evidence.name) returned '$($Evidence.json.state)', expected '$ExpectedState'."
}

function Get-OfflineSessionCount {
    param([Parameter(Mandatory)][object]$Excel)
    return [int][double]$Excel.Run('STR_XL_TEST_OFFLINE_SESSION_COUNT')
}

function Get-OfflineArtifactPath {
    param([Parameter(Mandatory)][object]$State)
    $projectHash = Get-OfflineSha256Text -Text ([string]$State.snapshot_reference.project_id)
    return Join-Path (Join-Path ([string]$State.store_directory) $projectHash) (([string]$State.snapshot_reference.file_sha256) + '.json')
}

function Close-OfflineWorkbook {
    param([AllowNull()][object]$Workbook, [bool]$Save)
    if ($null -eq $Workbook) { return }
    try { $Workbook.Close($Save) }
    finally { Release-StructAutomateComObject $Workbook }
}

function Wait-ForOwnedExcelExit {
    param([Parameter(Mandatory)][int]$ProcessId, [ValidateRange(1, 30000)][int]$TimeoutMs = 10000)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)
    while (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue) {
        if ([DateTime]::UtcNow -ge $deadline) { throw "Owned Excel process $ProcessId remained after COM shutdown." }
        Start-Sleep -Milliseconds 100
    }
}

function Start-OfflineAcceptanceExcel {
    param([Parameter(Mandatory)][string]$XllPath)
    $registrations = @(Get-StructAutomateExcelStartupRegistrations -XllPath $XllPath)
    Assert-OfflineAcceptance ($registrations.Count -gt 0) "Installed XLL has no exact per-user startup registration: $XllPath"
    $excel = $null
    try {
        $excel = New-Object -ComObject Excel.Application
        $processes = @(Get-Process -Name EXCEL -ErrorAction Stop)
        Assert-OfflineAcceptance ($processes.Count -eq 1) 'The owned hidden Excel application did not have one identifiable process.'
        $before = [int]$excel.Workbooks.Count
        Assert-OfflineAcceptance ($before -eq 0) 'A newly created owned Excel application unexpectedly started with a workbook.'
        Assert-OfflineAcceptance ([bool]$excel.RegisterXLL($XllPath)) "Excel could not load the installed XLL: $XllPath"
        Assert-OfflineAcceptance ([int]$excel.Workbooks.Count -eq $before) 'Loading the XLL created a workbook or worksheet unexpectedly.'
        $version = [string]$excel.Run('STR.INFO.VERSION')
        Assert-OfflineAcceptance (-not [string]::IsNullOrWhiteSpace($version)) 'The loaded XLL version probe returned no value.'
        # Office creates ribbon UI only when the owned host has a visible window.
        $excel.Visible = $true
        $excel.DisplayAlerts = $false
        $excel.AskToUpdateLinks = $false
        return [pscustomobject]@{
            excel = $excel
            process_id = [int]$processes[0].Id
            startup_registrations = $registrations
            version_probe = $version
        }
    }
    catch {
        Close-StructAutomateExcelApplication $excel
        throw
    }
}

function Record-OfflineCleanupFailure {
    param([Parameter(Mandatory)][string]$Message)
    if ($null -eq $script:failure) {
        $script:failure = $Message
        $script:receipt.failure = $Message
    }
    $script:checks.Add([ordered]@{ name = 'owned_excel_cleanup'; passed = $false; message = $Message })
}

$output = [IO.Path]::GetFullPath($OutputDirectory)
$receiptPath = Join-Path $output 'receipt.json'
$checks = [System.Collections.Generic.List[object]]::new()
$macros = [System.Collections.Generic.List[object]]::new()
$receipt = [ordered]@{
    schema_version = 'structautomate.offline-session-installed-acceptance/v1'
    started_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    passed = $false
    inputs = [ordered]@{}
    xll = $null
    source_snapshot = $null
    saved_workbook = $null
    macro_evidence = $macros
    checks = $checks
    cleanup = [ordered]@{ owned_excel_process_id = $null; quit_requested = $false; owned_process_exited = $false }
    failure = $null
}
$failure = $null
$excel = $null
$ownedProcessId = $null
$workbooks = $null
$workbook = $null
$legacyWorkbook = $null
$copyWorkbook = $null
$session = $null
$createdOutput = $false

try {
    Assert-OfflineAcceptance (-not (Test-Path -LiteralPath $output)) "OutputDirectory must be a new task-owned directory: $output"
    $repository = (Get-StructAutomateRepositoryRoot).TrimEnd('\') + '\'
    Assert-OfflineAcceptance (-not $output.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase)) 'OutputDirectory must be external to the repository.'
    [void](New-Item -ItemType Directory -Path $output -ErrorAction Stop)
    $createdOutput = $true

    Assert-OfflineAcceptance ([Environment]::Is64BitOperatingSystem) 'Installed offline acceptance requires 64-bit Windows.'
    Assert-OfflineAcceptance ($null -eq (Get-Process -Name EXCEL -ErrorAction SilentlyContinue)) 'Close all Excel instances before offline acceptance; this harness never touches user Excel processes.'
    $excelEnvironment = Get-StructAutomateExcelEnvironment
    Assert-OfflineAcceptance ($null -ne $excelEnvironment.executable -and [string]$excelEnvironment.platform -ceq 'x64') 'Installed offline acceptance requires the registered 64-bit Excel desktop host.'
    $xll = Assert-StructAutomateSafeInstallPath $InstalledXllPath
    $snapshot = [IO.Path]::GetFullPath($SnapshotPath)
    Assert-OfflineAcceptance (Test-Path -LiteralPath $xll -PathType Leaf) "Installed XLL is missing: $xll"
    Assert-OfflineAcceptance (Test-Path -LiteralPath $snapshot -PathType Leaf) "Snapshot is missing: $snapshot"
    Assert-OfflineAcceptance ((Get-StructAutomatePeMachine $xll) -eq 'AMD64') 'Installed XLL is not AMD64.'
    $manifestPath = Join-Path (Split-Path -Parent $xll) 'manifest.json'
    Assert-OfflineAcceptance (Test-Path -LiteralPath $manifestPath -PathType Leaf) "Installed XLL manifest is missing: $manifestPath"
    $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    $xllIdentity = Get-StructAutomateFileIdentity $xll
    Assert-OfflineAcceptance ($xllIdentity.sha256 -ceq [string]$manifest.signed_xll.sha256) 'Installed XLL hash does not match its manifest.'
    $signature = Get-AuthenticodeSignature -LiteralPath $xll
    Assert-OfflineAcceptance ([string]$signature.Status -ceq 'Valid' -and $null -ne $signature.SignerCertificate -and
        [string]$signature.SignerCertificate.Thumbprint -ceq [string]$manifest.signature.thumbprint) "Installed XLL Authenticode verification failed: $($signature.Status) $($signature.StatusMessage)"
    $sourceIdentity = Get-StructAutomateFileIdentity $snapshot
    Assert-OfflineAcceptance ($sourceIdentity.sha256 -ceq $ExpectedSnapshotSha256.ToLowerInvariant()) 'ExpectedSnapshotSha256 does not match the supplied snapshot bytes.'
    $source = Get-Content -Raw -LiteralPath $snapshot | ConvertFrom-Json -ErrorAction Stop
    $sourceMembers = @($source.members)
    $sourceActions = @($source.action_rows)
    Assert-OfflineAcceptance ($sourceMembers.Count -eq 1 -and $sourceActions.Count -eq 13) 'The supplied installed-acceptance snapshot must contain exactly one member and thirteen action rows.'
    $memberId = [string]$sourceMembers[0].member_id
    Assert-OfflineAcceptance (-not [string]::IsNullOrWhiteSpace($memberId)) 'The supplied snapshot has no member identity.'
    $receipt.inputs = [ordered]@{ output_directory = $output; store_directory = (Join-Path $output 'store'); source_member_id = $memberId; excel = $excelEnvironment }
    $receipt.xll = [ordered]@{
        identity = $xllIdentity
        manifest = Get-StructAutomateFileIdentity $manifestPath
        manifest_source_commit = [string]$manifest.source_commit
        manifest_source_tree = [string]$manifest.source_tree
        manifest_target = [string]$manifest.target
        authenticode = [ordered]@{ status = [string]$signature.Status; thumbprint = [string]$signature.SignerCertificate.Thumbprint }
    }
    $receipt.source_snapshot = $sourceIdentity

    $session = Start-OfflineAcceptanceExcel -XllPath $xll
    $excel = $session.excel
    $ownedProcessId = [int]$session.process_id
    $receipt.cleanup.owned_excel_process_id = $ownedProcessId
    $receipt.xll.startup_registrations = $session.startup_registrations
    $receipt.xll.version_probe = $session.version_probe
    $workbooks = $excel.Workbooks
    $workbook = $workbooks.Add()
    Assert-OfflineAcceptance ([bool]$excel.Run('STR_XL_TEST_RIBBON_LOADED')) 'Excel did not load the ribbon XML and its callbacks.'
    $checks.Add([ordered]@{ name = 'ribbon_loaded_callback'; passed = $true })
    $excel.Visible = $false
    $sheet = $null; $sentinelCell = $null
    try {
        $sheet = Get-OfflineSheet -Workbook $workbook -Name 'Sheet1'
        Assert-OfflineAcceptance ($null -ne $sheet) 'The bootstrap workbook did not contain Sheet1.'
        $sentinelCell = $sheet.Range('H3')
        $sentinelCell.Formula = '=SUM(19,23)'
        $sentinelCell.NumberFormat = '0.0000'
        [void]$sentinelCell.AddComment('offline acceptance sentinel')
    }
    finally {
        Release-StructAutomateComObject $sentinelCell
        Release-StructAutomateComObject $sheet
    }
    $initialSheets = @(Get-OfflineSheetNames -Workbook $workbook)
    $sheet = Get-OfflineSheet -Workbook $workbook -Name 'Sheet1'
    try { $sentinel = Get-OfflineCellSentinel -Worksheet $sheet -Address 'H3' }
    finally { Release-StructAutomateComObject $sheet }
    $beforeMetadata = Get-OfflineMetadata -Workbook $workbook
    Assert-OfflineAcceptance ($null -eq $beforeMetadata) 'A new bootstrap workbook unexpectedly contains offline-session metadata.'

    $workbook.Activate()
    $offlineReset = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_RESET_HOST_EFFECTS'
    $macros.Add($offlineReset)
    Assert-OfflineMacroState -Evidence $offlineReset -ExpectedState 'completed'
    $assumptionFailure = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_OFFLINE_FAILURE' -Arguments @('assumptions', $memberId, [double]1)
    $macros.Add($assumptionFailure)
    Assert-OfflineMacroState -Evidence $assumptionFailure -ExpectedState 'rejected'
    Assert-OfflineAcceptance (@(Get-OfflineSheetNames -Workbook $workbook).Count -eq $initialSheets.Count -and
        $null -eq (Get-OfflineSheet -Workbook $workbook -Name 'Assumptions') -and
        $null -eq (Get-OfflineMetadata -Workbook $workbook)) 'Injected new-sheet assumptions failure did not remove the owned sheet and metadata exactly.'
    $sheet = Get-OfflineSheet -Workbook $workbook -Name 'Sheet1'
    try { Assert-OfflineCellSentinel -Worksheet $sheet -Expected $sentinel }
    finally { Release-StructAutomateComObject $sheet }

    $assumptions = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_ASSUMPTIONS'
    $macros.Add($assumptions)
    Assert-OfflineMacroState -Evidence $assumptions -ExpectedState 'completed'
    $assumptionSheets = @(Get-OfflineSheetNames -Workbook $workbook)
    Assert-OfflineAcceptance ($assumptionSheets.Count -eq ($initialSheets.Count + 1) -and $assumptionSheets -contains 'Assumptions') 'Assumptions did not create exactly its owned worksheet.'
    $assumptionSheet = Get-OfflineSheet -Workbook $workbook -Name 'Assumptions'
    $cover = $null
    try {
        $cover = $assumptionSheet.Range('B11')
        Assert-OfflineAcceptance ([double]$cover.Value2 -eq 30.0) 'The canonical demo cover default at Assumptions!B11 must be 30 mm.'
        $cover.Value2 = 40.0
    }
    finally { Release-StructAutomateComObject $cover; Release-StructAutomateComObject $assumptionSheet }
    $assumptionsRepeat = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_ASSUMPTIONS'
    $macros.Add($assumptionsRepeat)
    Assert-OfflineMacroState -Evidence $assumptionsRepeat -ExpectedState 'completed'
    $assumptionSheet = Get-OfflineSheet -Workbook $workbook -Name 'Assumptions'
    try {
        $cover = $assumptionSheet.Range('B11')
        Assert-OfflineAcceptance ([double]$cover.Value2 -eq 40.0) 'Repeated Assumptions reset the edited B11 value.'
    }
    finally { Release-StructAutomateComObject $cover; Release-StructAutomateComObject $assumptionSheet }

    $metadataBeforeBadImport = Get-OfflineMetadata -Workbook $workbook
    $badImport = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_IMPORT_SNAPSHOT_FILE' -Arguments @($snapshot, ('0' * 64), (Join-Path $output 'store'))
    $macros.Add($badImport)
    Assert-OfflineMacroState -Evidence $badImport -ExpectedState 'rejected'
    $metadataAfterBadImport = Get-OfflineMetadata -Workbook $workbook
    Assert-OfflineAcceptance ($metadataAfterBadImport.xml -ceq $metadataBeforeBadImport.xml -and
        $null -eq $metadataAfterBadImport.state.snapshot_reference) 'Wrong-digest import changed the accepted workbook reference.'

    $import = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_IMPORT_SNAPSHOT_FILE' -Arguments @($snapshot, $ExpectedSnapshotSha256.ToLowerInvariant(), (Join-Path $output 'store'))
    $macros.Add($import)
    Assert-OfflineMacroState -Evidence $import -ExpectedState 'completed'
    Assert-OfflineAcceptance ([int]$import.json.details.member_count -eq 1 -and [int]$import.json.details.action_count -eq 13) 'Import receipt does not retain the source member/action counts.'
    $metadata = Get-OfflineMetadata -Workbook $workbook
    Assert-OfflineAcceptance ($metadata.state.schema_version -ceq 'structural-excel-offline/v1' -and
        [string]$metadata.state.document_id -ne [string]$metadata.state.snapshot_reference.project_id -and
        [string]$metadata.state.snapshot_reference.file_sha256 -ceq $ExpectedSnapshotSha256.ToLowerInvariant() -and
        [string]$metadata.state.store_directory -ceq (Join-Path $output 'store') -and
        -not [string]::IsNullOrWhiteSpace([string]$metadata.state.assumption_revision) -and
        $metadata.xml.Length -lt 5000 -and -not $metadata.xml.Contains('raw_capture')) 'Workbook metadata is not the required tiny reference-only offline-session state.'
    $artifactPath = Get-OfflineArtifactPath -State $metadata.state
    Assert-OfflineAcceptance ((Get-StructAutomateFileIdentity $artifactPath).sha256 -ceq $ExpectedSnapshotSha256.ToLowerInvariant()) 'The imported immutable artifact does not retain the exact source bytes.'

    $review = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
    $macros.Add($review)
    Assert-OfflineMacroState -Evidence $review -ExpectedState 'completed'
    Assert-OfflineAcceptance (-not [bool]$excel.Visible) 'Hidden installed acceptance unexpectedly showed the review window.'
    $memberReview = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_WRITE_MEMBER_REVIEW' -Arguments @($memberId)
    $macros.Add($memberReview)
    Assert-OfflineMacroState -Evidence $memberReview -ExpectedState 'completed'
    Assert-OfflineAcceptance (@(Get-OfflineSheetNames -Workbook $workbook) -contains 'Beam Review') 'Member review did not create Beam Review.'
    $metadataWithReport = Get-OfflineMetadata -Workbook $workbook
    Assert-OfflineAcceptance ([string]$metadataWithReport.state.report_snapshot_sha256 -ceq [string]$metadataWithReport.state.snapshot_reference.snapshot_sha256) 'Member review metadata is not bound to the imported snapshot.'
    $reviewSheet = Get-OfflineSheet -Workbook $workbook -Name 'Beam Review'
    try {
        Assert-OfflineReviewRows -Worksheet $reviewSheet -Source $source
        $reportBefore = Get-OfflineRangeFingerprint -Worksheet $reviewSheet -Address 'A1:M22'
    }
    finally { Release-StructAutomateComObject $reviewSheet }
    foreach ($boundary in @(1, 2)) {
        $reportFailure = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_OFFLINE_FAILURE' -Arguments @('report', $memberId, [double]$boundary)
        $macros.Add($reportFailure)
        Assert-OfflineMacroState -Evidence $reportFailure -ExpectedState 'rejected'
        $restored = Get-OfflineMetadata -Workbook $workbook
        Assert-OfflineAcceptance ($restored.xml -ceq $metadataWithReport.xml) "Injected report failure boundary $boundary did not restore metadata exactly."
        $reviewSheet = Get-OfflineSheet -Workbook $workbook -Name 'Beam Review'
        try {
            $reportAfter = Get-OfflineRangeFingerprint -Worksheet $reviewSheet -Address 'A1:M22'
            Assert-OfflineAcceptance ($reportAfter.formula_sha256 -ceq $reportBefore.formula_sha256 -and
                $reportAfter.value_sha256 -ceq $reportBefore.value_sha256) "Injected report failure boundary $boundary did not restore the full controlled report formula/value footprint."
        }
        finally { Release-StructAutomateComObject $reviewSheet }
    }
    $assumptionSheet = Get-OfflineSheet -Workbook $workbook -Name 'Assumptions'
    try {
        $cover = $assumptionSheet.Range('B11')
        $cover.Value2 = 41.0
    }
    finally { Release-StructAutomateComObject $cover; Release-StructAutomateComObject $assumptionSheet }
    $excel.CalculateFull()
    $reviewSheet = Get-OfflineSheet -Workbook $workbook -Name 'Beam Review'
    $historical = $null
    try {
        $historical = $reviewSheet.Range('A2')
        Assert-OfflineAcceptance ([string]$historical.Value2 -ceq 'Historical review — assumptions changed; review again') 'Changing an assumption did not mark the prior review historical.'
    }
    finally { Release-StructAutomateComObject $historical; Release-StructAutomateComObject $reviewSheet }
    $assumptionSheet = Get-OfflineSheet -Workbook $workbook -Name 'Assumptions'
    try {
        $cover = $assumptionSheet.Range('B11')
        $cover.Value2 = 40.0
    }
    finally { Release-StructAutomateComObject $cover; Release-StructAutomateComObject $assumptionSheet }
    $excel.CalculateFull()
    $sheet = Get-OfflineSheet -Workbook $workbook -Name 'Sheet1'
    try { Assert-OfflineCellSentinel -Worksheet $sheet -Expected $sentinel }
    finally { Release-StructAutomateComObject $sheet }

    $unavailableArtifact = $artifactPath + '.temporarily-unavailable'
    Move-Item -LiteralPath $artifactPath -Destination $unavailableArtifact -ErrorAction Stop
    try {
        $memoryReview = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
        $macros.Add($memoryReview)
        Assert-OfflineMacroState -Evidence $memoryReview -ExpectedState 'completed'
    }
    finally {
        if (Test-Path -LiteralPath $unavailableArtifact) { Move-Item -LiteralPath $unavailableArtifact -Destination $artifactPath -ErrorAction Stop }
    }

    $workbookPath = [IO.Path]::GetFullPath((Join-Path $output 'offline-session.xlsx'))
    $copyPath = [IO.Path]::GetFullPath((Join-Path $output 'offline-session-copy.xlsx'))
    $workbook.SaveAs($workbookPath)
    $workbook.SaveCopyAs($copyPath)
    $copyWorkbook = $workbooks.Open($copyPath, 0, $false)
    $copyWorkbook.Activate()
    $duplicate = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
    $macros.Add($duplicate)
    Assert-OfflineMacroState -Evidence $duplicate -ExpectedState 'rejected'
    Close-OfflineWorkbook -Workbook $copyWorkbook -Save:$false
    $copyWorkbook = $null
    $workbook.Activate()
    $originalAfterDuplicate = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
    $macros.Add($originalAfterDuplicate)
    Assert-OfflineMacroState -Evidence $originalAfterDuplicate -ExpectedState 'completed'

    $unsupportedCalculate = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_CMD_03_CALCULATE_WORKBOOK'
    $macros.Add($unsupportedCalculate)
    Assert-OfflineMacroState -Evidence $unsupportedCalculate -ExpectedState 'rejected'
    $workbook.Save()
    Close-OfflineWorkbook -Workbook $workbook -Save:$true
    $workbook = $null
    $receipt.saved_workbook = Get-StructAutomateFileIdentity $workbookPath
    Assert-OfflineAcceptance ((Get-OfflineSessionCount -Excel $excel) -eq 0) 'Closing the snapshot workbook did not evict its in-memory session.'

    $missingArtifact = $artifactPath + '.missing'
    Move-Item -LiteralPath $artifactPath -Destination $missingArtifact -ErrorAction Stop
    try {
        $workbook = $workbooks.Open($workbookPath, 0, $false)
        $workbook.Activate()
        $missingReview = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
        $macros.Add($missingReview)
        Assert-OfflineMacroState -Evidence $missingReview -ExpectedState 'rejected'
        Close-OfflineWorkbook -Workbook $workbook -Save:$false
        $workbook = $null
    }
    finally {
        if ($null -ne $workbook) { Close-OfflineWorkbook -Workbook $workbook -Save:$false; $workbook = $null }
        if (Test-Path -LiteralPath $missingArtifact) { Move-Item -LiteralPath $missingArtifact -Destination $artifactPath -ErrorAction Stop }
    }

    $originalArtifactBytes = [IO.File]::ReadAllBytes($artifactPath)
    try {
        $corrupted = [byte[]]$originalArtifactBytes.Clone()
        $corrupted[0] = $corrupted[0] -bxor 1
        [IO.File]::WriteAllBytes($artifactPath, $corrupted)
        $workbook = $workbooks.Open($workbookPath, 0, $false)
        $workbook.Activate()
        $corruptReview = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
        $macros.Add($corruptReview)
        Assert-OfflineMacroState -Evidence $corruptReview -ExpectedState 'rejected'
        Close-OfflineWorkbook -Workbook $workbook -Save:$false
        $workbook = $null
    }
    finally {
        if ($null -ne $workbook) { Close-OfflineWorkbook -Workbook $workbook -Save:$false; $workbook = $null }
        [IO.File]::WriteAllBytes($artifactPath, $originalArtifactBytes)
    }

    $workbook = $workbooks.Open($workbookPath, 0, $false)
    $workbook.Activate()
    $reopenReview = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_REVIEW_SNAPSHOT'
    $macros.Add($reopenReview)
    Assert-OfflineMacroState -Evidence $reopenReview -ExpectedState 'completed'
    Assert-OfflineAcceptance ((Get-OfflineSessionCount -Excel $excel) -eq 1) 'Reopened review did not create one resident offline session.'
    Close-OfflineWorkbook -Workbook $workbook -Save:$false
    $workbook = $null
    Assert-OfflineAcceptance ((Get-OfflineSessionCount -Excel $excel) -eq 0) 'Closing the reopened snapshot workbook did not clear its session.'

    $legacyWorkbook = $workbooks.Add()
    $legacyWorkbook.Activate()
    $offlineCapture = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_CAPTURE_HOST_EFFECTS'
    $macros.Add($offlineCapture)
    Assert-OfflineMacroState -Evidence $offlineCapture -ExpectedState 'completed'
    $offlineEffects = @($offlineCapture.json.calls.PSObject.Properties | ForEach-Object { [string]$_.Name })
    Assert-OfflineAcceptance ([int64]$offlineCapture.json.total_effects -gt 0 -and
        @($offlineEffects | Where-Object { $_ -match '^etabs\.' }).Count -eq 0) 'Offline session commands recorded no evidence or recorded an ETABS host effect.'
    $legacyCreate = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_CMD_01_CREATE_VALIDATE'
    $macros.Add($legacyCreate)
    Assert-OfflineMacroState -Evidence $legacyCreate -ExpectedState 'completed'
    $legacyCalculate = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_CMD_03_CALCULATE_WORKBOOK'
    $macros.Add($legacyCalculate)
    Assert-OfflineMacroState -Evidence $legacyCalculate -ExpectedState 'completed'
    $legacySheet = Get-OfflineSheet -Workbook $legacyWorkbook -Name 'Sheet1'
    $udfCell = $null
    try {
        $udfCell = $legacySheet.Range('J3')
        $udfCell.Formula = '=STR.REBAR.AREA(20)'
    }
    finally { Release-StructAutomateComObject $udfCell; Release-StructAutomateComObject $legacySheet }
    $legacyReset = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_RESET_HOST_EFFECTS'
    $macros.Add($legacyReset)
    Assert-OfflineMacroState -Evidence $legacyReset -ExpectedState 'completed'
    $excel.CalculateFullRebuild()
    $legacySheet = Get-OfflineSheet -Workbook $legacyWorkbook -Name 'Sheet1'
    try {
        $udfCell = $legacySheet.Range('J3')
        Assert-OfflineAcceptance ([Math]::Abs(([double]$udfCell.Value2) - ([Math]::PI * 100.0)) -lt 0.000001) 'STR.REBAR.AREA did not calculate the expected 20 mm bar area.'
    }
    finally { Release-StructAutomateComObject $udfCell; Release-StructAutomateComObject $legacySheet }
    $legacyCapture = Invoke-OfflineMacro -Excel $excel -Name 'STR_XL_TEST_CAPTURE_HOST_EFFECTS'
    $macros.Add($legacyCapture)
    Assert-OfflineMacroState -Evidence $legacyCapture -ExpectedState 'completed'
    Assert-OfflineAcceptance ([int64]$legacyCapture.json.total_effects -eq 0) 'Legacy UDF recalculation recorded host effects.'
    Close-OfflineWorkbook -Workbook $legacyWorkbook -Save:$false
    $legacyWorkbook = $null

    $checks.Add([ordered]@{ name = 'offline_session_acceptance'; passed = $true })
    $receipt.passed = $true
}
catch {
    $failure = $_.Exception.Message
    $receipt.failure = $failure
    $checks.Add([ordered]@{ name = 'offline_session_acceptance'; passed = $false; message = $failure })
}
finally {
    if ($null -ne $copyWorkbook) {
        try { Close-OfflineWorkbook -Workbook $copyWorkbook -Save:$false }
        catch { Record-OfflineCleanupFailure $_.Exception.Message }
    }
    if ($null -ne $legacyWorkbook) {
        try { Close-OfflineWorkbook -Workbook $legacyWorkbook -Save:$false }
        catch { Record-OfflineCleanupFailure $_.Exception.Message }
    }
    if ($null -ne $workbook) {
        try { Close-OfflineWorkbook -Workbook $workbook -Save:$false }
        catch { Record-OfflineCleanupFailure $_.Exception.Message }
    }
    try { Release-StructAutomateComObject $workbooks }
    catch { Record-OfflineCleanupFailure $_.Exception.Message }
    if ($null -ne $excel) {
        $receipt.cleanup.quit_requested = $true
        try { Close-StructAutomateExcelApplication $excel }
        catch { Record-OfflineCleanupFailure $_.Exception.Message }
        if ($null -ne $ownedProcessId) {
            try {
                Wait-ForOwnedExcelExit -ProcessId $ownedProcessId
                $receipt.cleanup.owned_process_exited = $true
            }
            catch { Record-OfflineCleanupFailure $_.Exception.Message }
        }
    }
}

$receipt.completed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
if ($null -ne $failure) { $receipt.passed = $false }
if ($createdOutput) { Write-StructAutomateJson -Value $receipt -Path $receiptPath }
$receipt | ConvertTo-Json -Depth 40
if ($null -ne $failure) { throw "Offline-session installed acceptance failed: $failure" }
