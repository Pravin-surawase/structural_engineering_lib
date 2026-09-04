[CmdletBinding()]
param(
    [string]$InstalledXllPath = (Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)) 'StructAutomate\Excel\0.1.0\StructAutomate.xll'),
    [string]$WorkbookPath = (Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)) 'StructAutomate\Excel\0.1.0\StructAutomate-Standalone-Beam.xlsx'),
    [string]$ReceiptPath = (Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)) 'StructAutomate\Receipts\excel-installed-acceptance.json'),
    [string]$SampleSetupCommand = 'STR_XL_SAMPLE_SETUP_TYPICAL',
    [string]$HostEffectResetCommand = 'STR_XL_TEST_RESET_HOST_EFFECTS',
    [string]$HostEffectCaptureCommand = 'STR_XL_TEST_CAPTURE_HOST_EFFECTS',
    [string]$CreateValidateCommand = 'STR_XL_CMD_01_CREATE_VALIDATE',
    [string]$CalculateCommand = 'STR_XL_CMD_03_CALCULATE_WORKBOOK',
    [string]$OptimizeCommand = 'STR_XL_CMD_04_OPTIMIZE_BEAMS',
    [string]$ExportCommand = 'STR_XL_CMD_06_EXPORT_PACKAGES',
    [string]$MeasureDiagnoseCommand = 'STR_XL_CMD_07_MEASURE_DIAGNOSE',
    [string]$ForcedRollbackCommand = 'STR_XL_TEST_FORCE_ROLLBACK',
    [string]$DiagnosticReconstructionCommand = 'STR_XL_CMD_07_RECONSTRUCT_CURRENT',
    [string]$ProgressCommand = 'STR_XL_TEST_PROGRESS_PROBE',
    [string]$CancelCommand = 'STR_XL_TEST_CANCELLATION_PROBE',
    [string]$RollbackSentinelTable = 'StructuralResults',
    [string]$RollbackSentinelColumn = 'result_id',
    [ValidateRange(1, 1000)][int]$RollbackSentinelRow = 1,
    [ValidateRange(1, 100)][int]$WarmupCount = 5,
    [ValidateRange(1, 100)][int]$WarmSampleCount = 30,
    [ValidateRange(1, 100)][int]$ColdLaunchCount = 10,
    [ValidateRange(1, 10000)][int]$WarmMedianBudgetMs = 750,
    [ValidateRange(1, 10000)][int]$WarmP95BudgetMs = 1000,
    [ValidateRange(1, 10000)][int]$ColdReadyBudgetMs = 3000,
    [ValidateRange(1, 10000)][int]$ProgressAndCancellationBudgetMs = 250,
    [ValidateRange(1, 4096)][int]$ExcelWorkingSetDeltaBudgetMiB = 256
)

. (Join-Path $PSScriptRoot 'Common.ps1')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ExcelProcessWorkingSetBytes {
    return [Int64](@(Get-Process -Name EXCEL -ErrorAction SilentlyContinue | Measure-Object -Property WorkingSet64 -Sum).Sum)
}

function Wait-ForExcelExit {
    param([ValidateRange(1, 30000)][int]$TimeoutMs = 10000)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)
    while (Get-Process -Name EXCEL -ErrorAction SilentlyContinue) {
        if ([DateTime]::UtcNow -ge $deadline) { throw 'Excel process remained after COM shutdown; cold-launch evidence would be invalid.' }
        Start-Sleep -Milliseconds 100
    }
}

function Get-InstalledAddinState {
    param([Parameter(Mandatory)][object]$Excel, [Parameter(Mandatory)][string]$XllPath)
    $addIns = $null
    try {
        $addIns = $Excel.AddIns
        for ($index = 1; $index -le $addIns.Count; $index++) {
            $addin = $null
            try {
                $addin = $addIns.Item($index)
                if ([string]::Equals([string]$addin.FullName, $XllPath, [System.StringComparison]::OrdinalIgnoreCase)) {
                    return [ordered]@{ found = $true; installed = [bool]$addin.Installed; name = [string]$addin.Name; full_name = [string]$addin.FullName }
                }
            }
            finally { Release-StructAutomateComObject $addin }
        }
        return [ordered]@{ found = $false; installed = $false; name = $null; full_name = $null }
    }
    finally { Release-StructAutomateComObject $addIns }
}

function Start-InstalledExcel {
    param(
        [Parameter(Mandatory)][string]$XllPath,
        [Diagnostics.Stopwatch]$ReadyTimer
    )
    $startupRegistrations = @(Get-StructAutomateExcelStartupRegistrations -XllPath $XllPath)
    if ($startupRegistrations.Count -eq 0) { throw "The installed XLL has no exact per-user Excel startup registration: $XllPath" }
    if ($ReadyTimer) { $ReadyTimer.Restart() }
    $excel = New-Object -ComObject Excel.Application
    $workbooks = $null
    $bootstrapWorkbook = $null
    $succeeded = $false
    try {
        $workbooks = $excel.Workbooks
        $bootstrapWorkbook = $workbooks.Add()
        if (-not [bool]$excel.RegisterXLL($XllPath)) { throw "Excel automation could not load the installed XLL: $XllPath" }
        $versionProbe = [string]$excel.Run('STR.INFO.VERSION')
        if ([string]::IsNullOrWhiteSpace($versionProbe)) { throw 'The installed XLL version probe returned no value.' }
        if ($ReadyTimer -and $ReadyTimer.IsRunning) { $ReadyTimer.Stop() }
        $excel.Visible = $false
        $excel.DisplayAlerts = $false
        $excel.AskToUpdateLinks = $false
        $state = Get-InstalledAddinState -Excel $excel -XllPath $XllPath
        if (-not $state.found -or -not $state.installed) { throw "The signed installed XLL is not registered and loaded by Excel: $XllPath" }
        $succeeded = $true
        return [pscustomobject]@{
            Excel = $excel
            Addin = [ordered]@{
                found = $state.found
                installed = $state.installed
                name = $state.name
                full_name = $state.full_name
                startup_registrations = $startupRegistrations
                automation_load_verified = $true
                version_probe = $versionProbe
            }
        }
    }
    finally {
        if ($bootstrapWorkbook) {
            try { $bootstrapWorkbook.Close($false) }
            finally { Release-StructAutomateComObject $bootstrapWorkbook }
        }
        Release-StructAutomateComObject $workbooks
        if (-not $succeeded) { Close-StructAutomateExcelApplication $excel }
    }
}

function Invoke-ExcelCommand {
    param([Parameter(Mandatory)][object]$Excel, [Parameter(Mandatory)][string]$Name)
    $timer = [Diagnostics.Stopwatch]::StartNew()
    try {
        $value = $Excel.Run($Name)
        $text = if ($null -eq $value) { $null } else { [string]$value }
        $json = $null
        if ($text) { try { $json = $text | ConvertFrom-Json -ErrorAction Stop } catch { } }
        return [ordered]@{ name = $Name; available = $true; elapsed_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3); result = $text; json = $json; error = $null }
    }
    catch { return [ordered]@{ name = $Name; available = $false; elapsed_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 3); result = $null; json = $null; error = $_.Exception.Message } }
    finally { $timer.Stop() }
}

function Assert-CommandState {
    param([Parameter(Mandatory)][object]$Evidence, [Parameter(Mandatory)][string[]]$AllowedStates)
    if (-not $Evidence.available) { throw "Required Excel command is unavailable: $($Evidence.name): $($Evidence.error)" }
    if ($null -eq $Evidence.json -or $null -eq $Evidence.json.state) { throw "Required Excel command did not return a JSON receipt with state: $($Evidence.name)" }
    $state = [string]$Evidence.json.state
    if ($AllowedStates -notcontains $state) { throw "Excel command $($Evidence.name) returned state '$state', expected one of: $($AllowedStates -join ', ')." }
    return $state
}

function Get-ObjectSha256 {
    param([AllowNull()][object]$Value)
    $json = $Value | ConvertTo-Json -Depth 20 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($json)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = $algorithm.ComputeHash($bytes)
        return -join @($hash | ForEach-Object { $_.ToString('x2') })
    }
    finally { $algorithm.Dispose() }
}

function Get-TableColumnDigest {
    param([Parameter(Mandatory)][object]$Table, [Parameter(Mandatory)][string]$ColumnName)
    $columns = $null; $column = $null; $range = $null
    try {
        $columns = $Table.ListColumns
        $column = $columns.Item($ColumnName)
        $range = $column.DataBodyRange
        if ($null -eq $range) { throw "Table $($Table.Name) has no data for required column $ColumnName." }
        return Get-ObjectSha256 $range.Value2
    }
    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $column; Release-StructAutomateComObject $columns }
}

function Get-TableColumnValues {
    param([Parameter(Mandatory)][object]$Table, [Parameter(Mandatory)][string]$ColumnName)
    $columns = $null; $rows = $null; $column = $null; $range = $null
    try {
        $columns = $Table.ListColumns; $rows = $Table.ListRows
        $column = $columns.Item($ColumnName)
        $range = $column.DataBodyRange
        if ($null -eq $range) { throw "Table $($Table.Name) has no data for required column $ColumnName." }
        $values = $range.Value2
        $rowCount = [int]$rows.Count
        if ($rowCount -eq 1) { return @([string]$values) }
        return @(for ($index = 1; $index -le $rowCount; $index++) { [string]$values[$index, 1] })
    }
    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $column; Release-StructAutomateComObject $rows; Release-StructAutomateComObject $columns }
}

function Get-ReceiptBindings {
    param([Parameter(Mandatory)][object]$Table)

    $commands = @(Get-TableColumnValues -Table $Table -ColumnName 'command')
    $artifacts = @(Get-TableColumnValues -Table $Table -ColumnName 'artifact_sha256')
    $fingerprints = @(Get-TableColumnValues -Table $Table -ColumnName 'execution_fingerprint')
    if ($commands.Count -ne $artifacts.Count -or $commands.Count -ne $fingerprints.Count) { throw 'StructuralReceipts command, artifact, and execution-fingerprint columns have inconsistent row counts.' }
    return @(for ($index = 0; $index -lt $commands.Count; $index++) { [ordered]@{ command = $commands[$index]; artifact_sha256 = $artifacts[$index]; execution_fingerprint = $fingerprints[$index] } })
}

function Get-WorkbookTables {
    param([Parameter(Mandatory)][object]$Workbook, [Parameter(Mandatory)][string[]]$RequiredNames)
    $found = [ordered]@{}; $worksheets = $null
    try {
        $worksheets = $Workbook.Worksheets
        for ($sheetIndex = 1; $sheetIndex -le $worksheets.Count; $sheetIndex++) {
            $worksheet = $null; $tables = $null
            try {
                $worksheet = $worksheets.Item($sheetIndex); $tables = $worksheet.ListObjects
                for ($tableIndex = 1; $tableIndex -le $tables.Count; $tableIndex++) {
                    $table = $null; $headers = $null; $data = $null; $rows = $null; $columns = $null
                    try {
                        $table = $tables.Item($tableIndex); $headers = $table.HeaderRowRange
                        $data = $table.DataBodyRange
                        $rows = $table.ListRows; $columns = $table.ListColumns
                        $found[[string]$table.Name] = [ordered]@{
                            worksheet = [string]$worksheet.Name
                            row_count = [int]$rows.Count
                            column_count = [int]$columns.Count
                            header_sha256 = Get-ObjectSha256 $headers.Value2
                            data_sha256 = if ($null -eq $data) { $null } else { Get-ObjectSha256 $data.Value2 }
                            result_id_sha256 = if ([string]$table.Name -eq 'StructuralResults') { Get-TableColumnDigest -Table $table -ColumnName 'result_id' } else { $null }
                            freshness_result_id_sha256 = if ([string]$table.Name -eq 'StructuralFreshness') { Get-TableColumnDigest -Table $table -ColumnName 'result_id' } else { $null }
                            freshness_current_values = if ([string]$table.Name -eq 'StructuralFreshness') { @(Get-TableColumnValues -Table $table -ColumnName 'is_current') } else { @() }
                            freshness_execution_fingerprint_values = if ([string]$table.Name -eq 'StructuralFreshness') { @(Get-TableColumnValues -Table $table -ColumnName 'execution_fingerprint') } else { @() }
                            receipt_bindings = if ([string]$table.Name -eq 'StructuralReceipts') { @(Get-ReceiptBindings -Table $table) } else { @() }
                        }
                    }
                    finally { Release-StructAutomateComObject $columns; Release-StructAutomateComObject $rows; Release-StructAutomateComObject $data; Release-StructAutomateComObject $headers; Release-StructAutomateComObject $table }
                }
            }
            finally { Release-StructAutomateComObject $tables; Release-StructAutomateComObject $worksheet }
        }
    }
    finally { Release-StructAutomateComObject $worksheets }
    foreach ($name in $RequiredNames) { if (-not $found.Contains($name)) { throw "Required workbook table is missing: $name" } }
    return $found
}

function Get-TableCellValue {
    param([Parameter(Mandatory)][object]$Workbook, [Parameter(Mandatory)][string]$TableName, [Parameter(Mandatory)][string]$ColumnName, [ValidateRange(1, 1000)][int]$Row)
    $worksheets = $null
    try {
        $worksheets = $Workbook.Worksheets
        for ($sheetIndex = 1; $sheetIndex -le $worksheets.Count; $sheetIndex++) {
            $worksheet = $null; $tables = $null
            try {
                $worksheet = $worksheets.Item($sheetIndex); $tables = $worksheet.ListObjects
                for ($tableIndex = 1; $tableIndex -le $tables.Count; $tableIndex++) {
                    $table = $null; $columns = $null; $rows = $null; $column = $null; $data = $null; $cells = $null; $range = $null
                    try {
                        $table = $tables.Item($tableIndex)
                        if ([string]$table.Name -ne $TableName) { continue }
                        $rows = $table.ListRows; $columns = $table.ListColumns
                        if ($rows.Count -lt $Row) { throw "Rollback sentinel row $Row is outside $TableName." }
                        $column = $columns.Item($ColumnName); $data = $column.DataBodyRange; $cells = $data.Cells; $range = $cells.Item($Row, 1)
                        return [string]$range.Value2
                    }
                    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $cells; Release-StructAutomateComObject $data; Release-StructAutomateComObject $column; Release-StructAutomateComObject $columns; Release-StructAutomateComObject $rows; Release-StructAutomateComObject $table }
                }
            }
            finally { Release-StructAutomateComObject $tables; Release-StructAutomateComObject $worksheet }
        }
    }
    finally { Release-StructAutomateComObject $worksheets }
    throw "Rollback sentinel table is missing: $TableName"
}

function Set-TableColumnValue {
    param(
        [Parameter(Mandatory)][object]$Workbook,
        [Parameter(Mandatory)][string]$TableName,
        [Parameter(Mandatory)][string]$ColumnName,
        [Parameter(Mandatory)][string]$Value
    )
    $worksheets = $null
    try {
        $worksheets = $Workbook.Worksheets
        for ($sheetIndex = 1; $sheetIndex -le $worksheets.Count; $sheetIndex++) {
            $worksheet = $null; $tables = $null
            try {
                $worksheet = $worksheets.Item($sheetIndex); $tables = $worksheet.ListObjects
                for ($tableIndex = 1; $tableIndex -le $tables.Count; $tableIndex++) {
                    $table = $null; $columns = $null; $rows = $null; $column = $null; $data = $null
                    try {
                        $table = $tables.Item($tableIndex)
                        if ([string]$table.Name -ne $TableName) { continue }
                        $rows = $table.ListRows; $columns = $table.ListColumns
                        $column = $columns.Item($ColumnName); $data = $column.DataBodyRange
                        if ($null -eq $data -or $rows.Count -lt 1) { throw "Table $TableName has no data for required column $ColumnName." }
                        $data.Value2 = $Value
                        return [int]$rows.Count
                    }
                    finally { Release-StructAutomateComObject $data; Release-StructAutomateComObject $column; Release-StructAutomateComObject $columns; Release-StructAutomateComObject $rows; Release-StructAutomateComObject $table }
                }
            }
            finally { Release-StructAutomateComObject $tables; Release-StructAutomateComObject $worksheet }
        }
    }
    finally { Release-StructAutomateComObject $worksheets }
    throw "Required workbook table is missing: $TableName"
}

function Remove-TableColumn {
    param(
        [Parameter(Mandatory)][object]$Workbook,
        [Parameter(Mandatory)][string]$TableName,
        [Parameter(Mandatory)][string]$ColumnName
    )
    $worksheets = $null
    try {
        $worksheets = $Workbook.Worksheets
        for ($sheetIndex = 1; $sheetIndex -le $worksheets.Count; $sheetIndex++) {
            $worksheet = $null; $tables = $null
            try {
                $worksheet = $worksheets.Item($sheetIndex); $tables = $worksheet.ListObjects
                for ($tableIndex = 1; $tableIndex -le $tables.Count; $tableIndex++) {
                    $table = $null; $columns = $null; $rows = $null; $column = $null
                    try {
                        $table = $tables.Item($tableIndex)
                        if ([string]$table.Name -ne $TableName) { continue }
                        $columns = $table.ListColumns; $rows = $table.ListRows
                        $before = [int]$columns.Count
                        $column = $columns.Item($ColumnName); $column.Delete()
                        return [ordered]@{ table = $TableName; removed_column = $ColumnName; row_count = [int]$rows.Count; columns_before = $before; columns_after = [int]$columns.Count }
                    }
                    finally { Release-StructAutomateComObject $column; Release-StructAutomateComObject $columns; Release-StructAutomateComObject $rows; Release-StructAutomateComObject $table }
                }
            }
            finally { Release-StructAutomateComObject $tables; Release-StructAutomateComObject $worksheet }
        }
    }
    finally { Release-StructAutomateComObject $worksheets }
    throw "Required workbook table is missing: $TableName"
}

function Set-UdfPurityProbe {
    param([Parameter(Mandatory)][object]$Workbook)
    $worksheets = $null; $worksheet = $null; $range = $null
    try {
        $worksheets = $Workbook.Worksheets
        try { $worksheet = $worksheets.Item('__WP09Acceptance') }
        catch { $worksheet = $worksheets.Add(); $worksheet.Name = '__WP09Acceptance' }
        $range = $worksheet.Range('A1')
        $range.Formula = '=STR.REBAR.AREA(20)'
    }
    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $worksheet; Release-StructAutomateComObject $worksheets }
}

function Get-UdfPurityProbeValue {
    param([Parameter(Mandatory)][object]$Workbook)
    $worksheets = $null; $worksheet = $null; $range = $null
    try {
        $worksheets = $Workbook.Worksheets; $worksheet = $worksheets.Item('__WP09Acceptance'); $range = $worksheet.Range('A1')
        return [double]$range.Value2
    }
    finally { Release-StructAutomateComObject $range; Release-StructAutomateComObject $worksheet; Release-StructAutomateComObject $worksheets }
}

function Wait-ForExcelReady {
    param([Parameter(Mandatory)][object]$Excel, [ValidateRange(1, 30000)][int]$TimeoutMs = 10000)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)
    while (-not [bool]$Excel.Ready) {
        if ([DateTime]::UtcNow -ge $deadline) { throw 'Excel did not become Ready.' }
        Start-Sleep -Milliseconds 25
    }
}

$receiptPath = Assert-StructAutomateSafeReceiptPath $ReceiptPath
$evidenceDirectory = Split-Path -Parent $receiptPath
[void](New-Item -ItemType Directory -Path $evidenceDirectory -Force)
$workbookCopy = Join-Path $evidenceDirectory 'wp09-installed-acceptance-workbook.xlsx'
$receipt = $null; $failure = $null

try {
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Installed acceptance requires 64-bit Windows.' }
    if (Get-Process -Name EXCEL -ErrorAction SilentlyContinue) { throw 'Close all Excel processes before installed acceptance; process reuse invalidates cold-launch and memory evidence.' }
    foreach ($name in @($SampleSetupCommand, $HostEffectResetCommand, $HostEffectCaptureCommand, $CreateValidateCommand, $CalculateCommand, $OptimizeCommand, $ExportCommand, $MeasureDiagnoseCommand, $ForcedRollbackCommand, $DiagnosticReconstructionCommand, $ProgressCommand, $CancelCommand)) {
        if ([string]::IsNullOrWhiteSpace($name)) { throw 'Every host-effect and workbook-command binding is required for fail-closed acceptance.' }
    }
    $xll = Assert-StructAutomateSafeInstallPath $InstalledXllPath
    $rollbackReceiptPath = Assert-StructAutomateSafeReceiptPath (Join-Path $evidenceDirectory 'excel-rollback-probe.json')
    if (-not (Test-Path -LiteralPath $xll -PathType Leaf)) { throw "Installed XLL is missing: $xll" }
    $installedManifestPath = Join-Path (Split-Path -Parent $xll) 'manifest.json'
    if (-not (Test-Path -LiteralPath $installedManifestPath -PathType Leaf)) { throw "Installed manifest is missing: $installedManifestPath" }
    if (-not (Test-Path -LiteralPath $WorkbookPath -PathType Leaf)) { throw "Shipped sample workbook is missing: $WorkbookPath" }
    $manifest = Get-Content -Raw -LiteralPath $installedManifestPath | ConvertFrom-Json
    if ([string]$manifest.file_digest_algorithm -ne 'SHA-256' -or [string]$manifest.signature.authenticode_file_digest_algorithm -ne 'SHA-256' -or [string]::IsNullOrWhiteSpace([string]$manifest.signature.certificate_signature_algorithm)) {
        throw 'Installed manifest does not declare distinct SHA-256 file and Authenticode digest algorithms plus a certificate signature algorithm.'
    }
    $sampleIdentity = Get-StructAutomateFileIdentity $WorkbookPath
    $expectedSample = @($manifest.files | Where-Object { $_.name -eq [IO.Path]::GetFileName($WorkbookPath) }) | Select-Object -First 1
    if ($null -eq $expectedSample -or $sampleIdentity.sha256 -ne [string]$expectedSample.sha256) { throw 'WorkbookPath is not the unchanged shipped sample recorded in the installed manifest.' }
    $xllIdentity = Get-StructAutomateFileIdentity $xll
    if ($xllIdentity.sha256 -ne [string]$manifest.signed_xll.sha256) { throw 'Installed XLL hash does not match its installed manifest.' }
    if ((Get-StructAutomatePeMachine $xll) -ne 'AMD64') { throw 'Installed XLL is not AMD64.' }
    $signature = Get-AuthenticodeSignature -LiteralPath $xll
    if ([string]$signature.Status -ne 'Valid' -or -not $signature.SignerCertificate -or $signature.SignerCertificate.Thumbprint -ne [string]$manifest.signature.thumbprint) { throw "Installed XLL Authenticode verification failed: $($signature.Status) $($signature.StatusMessage)" }

    Copy-Item -LiteralPath $WorkbookPath -Destination $workbookCopy -Force
    $session = $null; $workbook = $null; $workbooks = $null
    try {
        $session = Start-InstalledExcel -XllPath $xll; $excel = $session.Excel; $workbooks = $excel.Workbooks
        $workbook = $workbooks.Open($workbookCopy, 0, $false); Wait-ForExcelReady -Excel $excel
        $sampleSetup = Invoke-ExcelCommand -Excel $excel -Name $SampleSetupCommand; Assert-CommandState -Evidence $sampleSetup -AllowedStates @('completed') | Out-Null
        $inputTables = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralProject', 'StructuralMembers', 'StructuralOperations')
        if ($inputTables.StructuralProject.row_count -ne 1 -or $inputTables.StructuralMembers.row_count -ne 20 -or $inputTables.StructuralOperations.row_count -ne 200) { throw 'Shipped sample does not contain exactly one StructuralProject row, 20 StructuralMembers rows, and 200 StructuralOperations rows.' }
        Set-UdfPurityProbe -Workbook $workbook
        $memoryBaselineBytes = Get-ExcelProcessWorkingSetBytes
        $hostEffectReset = Invoke-ExcelCommand -Excel $excel -Name $HostEffectResetCommand; Assert-CommandState -Evidence $hostEffectReset -AllowedStates @('completed') | Out-Null
        $excel.CalculateFullRebuild()
        $udfProbeValue = Get-UdfPurityProbeValue -Workbook $workbook
        if ([Math]::Abs($udfProbeValue - ([Math]::PI * 100.0)) -ge 0.000001) { throw 'STR.REBAR.AREA UDF purity probe did not return the expected value.' }
        $hostEffectCapture = Invoke-ExcelCommand -Excel $excel -Name $HostEffectCaptureCommand; Assert-CommandState -Evidence $hostEffectCapture -AllowedStates @('completed') | Out-Null
        if ($null -eq $hostEffectCapture.json.total_effects -or [Int64]$hostEffectCapture.json.total_effects -ne 0) { throw 'Host-effect capture did not prove total_effects = 0 after UDF recalculation.' }
        $createValidate = Invoke-ExcelCommand -Excel $excel -Name $CreateValidateCommand; Assert-CommandState -Evidence $createValidate -AllowedStates @('completed') | Out-Null
        $warmups = @()
        $warmupReuse = @()
        for ($index = 1; $index -le $WarmupCount; $index++) {
            $command = Invoke-ExcelCommand -Excel $excel -Name $CalculateCommand
            Assert-CommandState -Evidence $command -AllowedStates @('completed') | Out-Null
            if ($null -eq $command.json.reused_current_results) { throw 'XL-CMD-03 did not report whether current results were reused.' }
            $reused = [bool]$command.json.reused_current_results
            if ($index -eq 1 -and $reused) { throw 'The first XL-CMD-03 warm-up must perform a complete calculation from the validated sample inputs.' }
            if ($index -gt 1 -and -not $reused) { throw 'An unchanged XL-CMD-03 warm-up did not reuse its verified current results.' }
            $warmups += $command.elapsed_ms
            $warmupReuse += $reused
        }
        $warmSamples = @()
        $warmSampleReuse = @()
        for ($index = 1; $index -le $WarmSampleCount; $index++) {
            $command = Invoke-ExcelCommand -Excel $excel -Name $CalculateCommand
            Assert-CommandState -Evidence $command -AllowedStates @('completed') | Out-Null
            if ($null -eq $command.json.reused_current_results -or -not [bool]$command.json.reused_current_results) { throw 'A measured unchanged XL-CMD-03 call did not reuse its verified current results.' }
            $warmSamples += $command.elapsed_ms
            $warmSampleReuse += [bool]$command.json.reused_current_results
        }
        $calculationReferenceTables = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults')
        $optimize = Invoke-ExcelCommand -Excel $excel -Name $OptimizeCommand; Assert-CommandState -Evidence $optimize -AllowedStates @('completed') | Out-Null
        $export = Invoke-ExcelCommand -Excel $excel -Name $ExportCommand; Assert-CommandState -Evidence $export -AllowedStates @('completed') | Out-Null
        if ([string]::IsNullOrWhiteSpace([string]$export.json.artifact_path) -or [string]::IsNullOrWhiteSpace([string]$export.json.artifact_sha256)) { throw 'ExportPackage did not return artifact_path and artifact_sha256.' }
        $expectedExportDirectory = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $workbookCopy) 'StructAutomate Packages')).TrimEnd('\') + '\'
        $exportPath = [IO.Path]::GetFullPath([string]$export.json.artifact_path)
        if (-not $exportPath.StartsWith($expectedExportDirectory, [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $exportPath -PathType Leaf)) { throw "ExportPackage artifact is not a file under the workbook package directory: $exportPath" }
        $exportIdentity = Get-StructAutomateFileIdentity $exportPath
        if ($exportIdentity.length_bytes -le 0 -or $exportIdentity.sha256 -ne [string]$export.json.artifact_sha256) { throw 'ExportPackage artifact is empty or its SHA-256 does not match the command receipt.' }
        $exportBundle = Get-Content -Raw -LiteralPath $exportPath | ConvertFrom-Json
        if ([string]$exportBundle.schema_version -ne 'structautomate.batch-calculation-package/v1' -or @($exportBundle.packages).Count -ne 20) { throw 'Exported batch calculation package is empty, has an unexpected schema, or does not contain exactly 20 member packages.' }
        $measureDiagnose = Invoke-ExcelCommand -Excel $excel -Name $MeasureDiagnoseCommand; Assert-CommandState -Evidence $measureDiagnose -AllowedStates @('completed') | Out-Null
        $postCalculateTables = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralProject', 'StructuralMembers', 'StructuralOperations', 'StructuralResults', 'StructuralFreshness', 'StructuralReceipts')
        if (@($postCalculateTables.StructuralFreshness.freshness_current_values | Where-Object { $_ -ne 'TRUE' -and $_ -ne 'True' -and $_ -ne 'true' }).Count -gt 0) { throw 'XL-CMD-03 did not leave every StructuralFreshness row current.' }
        $requiredReceiptCommands = @('CreateValidate', 'Calculate', 'Optimize', 'ExportPackage', 'MeasureDiagnose')
        $missingReceiptCommands = @($requiredReceiptCommands | Where-Object { $_ -notin @($postCalculateTables.StructuralReceipts.receipt_bindings | ForEach-Object command) })
        if ($missingReceiptCommands.Count -gt 0) { throw "StructuralReceipts is missing required command receipt(s): $($missingReceiptCommands -join ', ')" }
        if (@($postCalculateTables.StructuralReceipts.receipt_bindings | Where-Object { $_.command -eq 'ExportPackage' -and $_.artifact_sha256 -eq $exportIdentity.sha256 }).Count -eq 0) { throw 'StructuralReceipts does not bind the exported package SHA-256 to an ExportPackage receipt.' }
        $preimage = Get-TableCellValue -Workbook $workbook -TableName $RollbackSentinelTable -ColumnName $RollbackSentinelColumn -Row $RollbackSentinelRow
        $preRollbackResultsSha256 = $postCalculateTables.StructuralResults.data_sha256
        $rollbackStartedUtc = [DateTime]::UtcNow
        $rollback = Invoke-ExcelCommand -Excel $excel -Name $ForcedRollbackCommand; Assert-CommandState -Evidence $rollback -AllowedStates @('restored') | Out-Null
        $postimage = Get-TableCellValue -Workbook $workbook -TableName $RollbackSentinelTable -ColumnName $RollbackSentinelColumn -Row $RollbackSentinelRow
        $postRollbackTables = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults')
        $postRollbackResultsSha256 = $postRollbackTables.StructuralResults.data_sha256
        if (-not (Test-Path -LiteralPath $rollbackReceiptPath -PathType Leaf)) { throw "Forced rollback did not produce its required receipt: $rollbackReceiptPath" }
        $rollbackReceiptInfo = Get-Item -LiteralPath $rollbackReceiptPath
        if ($rollbackReceiptInfo.LastWriteTimeUtc -lt $rollbackStartedUtc) { throw 'Forced rollback receipt predates this probe and cannot prove this run.' }
        $rollbackReceipt = Get-Content -Raw -LiteralPath $rollbackReceiptPath | ConvertFrom-Json
        if ([string]$rollbackReceipt.state -ne 'restored') { throw 'Forced rollback receipt did not report the restored state.' }
        if ($preimage -cne $postimage -or $preRollbackResultsSha256 -ne $postRollbackResultsSha256) { throw 'Forced mid-write failure did not restore the exact sentinel and full StructuralResults preimage.' }
        $progress = Invoke-ExcelCommand -Excel $excel -Name $ProgressCommand; Assert-CommandState -Evidence $progress -AllowedStates @('completed') | Out-Null
        $cancel = Invoke-ExcelCommand -Excel $excel -Name $CancelCommand; Assert-CommandState -Evidence $cancel -AllowedStates @('cancelled') | Out-Null
        if ($null -eq $progress.json.response_ms -or $null -eq $cancel.json.response_ms) { throw 'Progress and cancellation probes must return their measured response boundary.' }
        $memoryAfterCommandsBytes = Get-ExcelProcessWorkingSetBytes
        $preReopen = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness', 'StructuralReceipts')
        $workbook.Save(); $workbook.Close($true); Release-StructAutomateComObject $workbook; $workbook = $null
        $workbook = $workbooks.Open($workbookCopy, 0, $false); Wait-ForExcelReady -Excel $excel
        $diagnostic = Invoke-ExcelCommand -Excel $excel -Name $DiagnosticReconstructionCommand; Assert-CommandState -Evidence $diagnostic -AllowedStates @('completed') | Out-Null
        $postReopen = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness', 'StructuralReceipts')
        $liveExecutionFingerprint = [string]$diagnostic.json.runtime
        if ([string]::IsNullOrWhiteSpace($liveExecutionFingerprint)) { throw 'Diagnostic reconstruction did not return the live execution fingerprint.' }
        $reconstructionMatches = [bool]($preReopen.StructuralResults.result_id_sha256 -eq $postReopen.StructuralResults.result_id_sha256 -and $preReopen.StructuralFreshness.freshness_result_id_sha256 -eq $postReopen.StructuralFreshness.freshness_result_id_sha256 -and @($postReopen.StructuralFreshness.freshness_current_values | Where-Object { $_ -ne 'TRUE' -and $_ -ne 'True' -and $_ -ne 'true' }).Count -eq 0 -and @($postReopen.StructuralFreshness.freshness_execution_fingerprint_values | Where-Object { $_ -cne $liveExecutionFingerprint }).Count -eq 0)
        if (-not $reconstructionMatches) { throw 'Diagnostic/current-reconstruction did not preserve a current freshness ledger and result identity after reopen.' }

        $legacyFreshnessChange = Remove-TableColumn -Workbook $workbook -TableName 'StructuralFreshness' -ColumnName 'execution_fingerprint'
        $legacyReceiptChange = Remove-TableColumn -Workbook $workbook -TableName 'StructuralReceipts' -ColumnName 'execution_fingerprint'
        if ($legacyFreshnessChange.columns_before -ne 10 -or $legacyFreshnessChange.columns_after -ne 9 -or $legacyReceiptChange.columns_before -ne 14 -or $legacyReceiptChange.columns_after -ne 13) { throw 'The legacy-schema probe did not create the exact prior StructuralFreshness and StructuralReceipts shapes.' }
        $workbook.Save(); $workbook.Close($true); Release-StructAutomateComObject $workbook; $workbook = $null
        $workbook = $workbooks.Open($workbookCopy, 0, $false); Wait-ForExcelReady -Excel $excel
        $legacySchemaRecalculation = Invoke-ExcelCommand -Excel $excel -Name $CalculateCommand; Assert-CommandState -Evidence $legacySchemaRecalculation -AllowedStates @('completed') | Out-Null
        $postLegacySchemaRecalculation = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness', 'StructuralReceipts')
        $legacySchemaUpgrade = [bool](
            -not [bool]$legacySchemaRecalculation.json.reused_current_results -and
            [int]$legacySchemaRecalculation.json.operation_result_count -gt 0 -and
            [string]$legacySchemaRecalculation.json.execution_fingerprint -ceq $liveExecutionFingerprint -and
            $postLegacySchemaRecalculation.StructuralResults.result_id_sha256 -eq $calculationReferenceTables.StructuralResults.result_id_sha256 -and
            $postLegacySchemaRecalculation.StructuralFreshness.column_count -eq 10 -and
            $postLegacySchemaRecalculation.StructuralReceipts.column_count -eq 14 -and
            @($postLegacySchemaRecalculation.StructuralFreshness.freshness_execution_fingerprint_values | Where-Object { $_ -cne $liveExecutionFingerprint }).Count -eq 0 -and
            @($postLegacySchemaRecalculation.StructuralReceipts.receipt_bindings | Where-Object { $_.execution_fingerprint -eq 'legacy-unbound' }).Count -eq $postReopen.StructuralReceipts.row_count)
        if (-not $legacySchemaUpgrade) { throw 'The exact prior output-table schema did not migrate through a non-reused full calculation with retained legacy receipts.' }

        $syntheticPriorFingerprint = 'structautomate.synthetic-prior-runtime/v1'
        $driftedRowCount = Set-TableColumnValue -Workbook $workbook -TableName 'StructuralFreshness' -ColumnName 'execution_fingerprint' -Value $syntheticPriorFingerprint
        $preDriftRestart = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness')
        if ($driftedRowCount -ne $preDriftRestart.StructuralFreshness.row_count -or @($preDriftRestart.StructuralFreshness.freshness_execution_fingerprint_values | Where-Object { $_ -cne $syntheticPriorFingerprint }).Count -gt 0) { throw 'The runtime-drift probe did not persist its synthetic prior fingerprint in every freshness row.' }
        $workbook.Save(); $workbook.Close($true); Release-StructAutomateComObject $workbook; $workbook = $null
        $workbook = $workbooks.Open($workbookCopy, 0, $false); Wait-ForExcelReady -Excel $excel
        $postDriftRestart = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness')
        $driftDiagnostic = Invoke-ExcelCommand -Excel $excel -Name $DiagnosticReconstructionCommand; Assert-CommandState -Evidence $driftDiagnostic -AllowedStates @('rejected') | Out-Null
        $recalculatedAfterDrift = Invoke-ExcelCommand -Excel $excel -Name $CalculateCommand; Assert-CommandState -Evidence $recalculatedAfterDrift -AllowedStates @('completed') | Out-Null
        $postDriftRecalculation = Get-WorkbookTables -Workbook $workbook -RequiredNames @('StructuralResults', 'StructuralFreshness', 'StructuralReceipts')
        $runtimeFingerprintInvalidation = [bool](
            @($postDriftRestart.StructuralFreshness.freshness_execution_fingerprint_values | Where-Object { $_ -cne $syntheticPriorFingerprint }).Count -eq 0 -and
            -not [bool]$recalculatedAfterDrift.json.reused_current_results -and
            [int]$recalculatedAfterDrift.json.operation_result_count -gt 0 -and
            [string]$recalculatedAfterDrift.json.execution_fingerprint -ceq $liveExecutionFingerprint -and
            @($postDriftRecalculation.StructuralFreshness.freshness_current_values | Where-Object { $_ -ne 'TRUE' -and $_ -ne 'True' -and $_ -ne 'true' }).Count -eq 0 -and
            @($postDriftRecalculation.StructuralFreshness.freshness_execution_fingerprint_values | Where-Object { $_ -cne $liveExecutionFingerprint }).Count -eq 0)
        if (-not $runtimeFingerprintInvalidation) { throw 'A saved prior runtime fingerprint was reused or was not replaced by a full calculation under the live runtime.' }
        $workbook.Save()
        $lifecycle = $session.Addin
    }
    finally {
        if ($workbook) { try { $workbook.Close($false) } finally { Release-StructAutomateComObject $workbook } }
        Release-StructAutomateComObject $workbooks
        if ($session) { Close-StructAutomateExcelApplication $session.Excel }
    }
    Wait-ForExcelExit
    $coldSamples = @()
    for ($index = 1; $index -le $ColdLaunchCount; $index++) {
        $timer = [Diagnostics.Stopwatch]::StartNew(); $coldSession = $null
        try {
            $coldSession = Start-InstalledExcel -XllPath $xll -ReadyTimer $timer
        }
        finally {
            if ($timer.IsRunning) { $timer.Stop() }
            if ($coldSession) { Close-StructAutomateExcelApplication $coldSession.Excel }
        }
        Wait-ForExcelExit; $coldSamples += [Math]::Round($timer.Elapsed.TotalMilliseconds, 3)
    }
    $workingSetDeltaMiB = [Math]::Round(($memoryAfterCommandsBytes - $memoryBaselineBytes) / 1MB, 3)
    $warmMedian = Get-StructAutomatePercentile -Values $warmSamples -Percentile 50
    $warmP95 = Get-StructAutomatePercentile -Values $warmSamples -Percentile 95
    $coldMax = [double]($coldSamples | Measure-Object -Maximum).Maximum
    $checks = [ordered]@{
        signed_amd64_installed_xll = $true; shipped_sample_20_members_200_operations = $true; installed_lifecycle = [bool]($lifecycle.found -and $lifecycle.installed)
        udf_zero_host_effects = [bool]([Int64]$hostEffectCapture.json.total_effects -eq 0 -and [Math]::Abs($udfProbeValue - ([Math]::PI * 100.0)) -lt 0.000001); xl_cmd_03_initial_full_recalculation = -not [bool]$warmupReuse[0]; xl_cmd_03_warm_cache_verified = -not ($warmSampleReuse | Where-Object { -not $_ })
        xl_cmd_03_warm_median_budget = $warmMedian -le $WarmMedianBudgetMs
        xl_cmd_03_warm_p95_budget = $warmP95 -le $WarmP95BudgetMs; cold_ready_budget = $coldMax -le $ColdReadyBudgetMs; optimize_export_measure_receipts = $true; export_package_bound = $true; forced_mid_write_rollback = $preimage -ceq $postimage -and $preRollbackResultsSha256 -eq $postRollbackResultsSha256
        progress_budget = [double]$progress.json.response_ms -le $ProgressAndCancellationBudgetMs; cancellation_budget = [double]$cancel.json.response_ms -le $ProgressAndCancellationBudgetMs
        memory_delta_budget = $workingSetDeltaMiB -le $ExcelWorkingSetDeltaBudgetMiB; save_reopen_current_reconstruction = $reconstructionMatches
        legacy_output_schema_upgrade = $legacySchemaUpgrade
        restart_runtime_fingerprint_invalidation = $runtimeFingerprintInvalidation
    }
    $receipt = [ordered]@{
        schema_version = 'structautomate.excel-installed-acceptance/v3'; passed = -not ($checks.GetEnumerator() | Where-Object { -not [bool]$_.Value }); observed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
        source_commit = [string]$manifest.source_commit; installed_manifest = Get-StructAutomateFileIdentity $installedManifestPath; xll = $xllIdentity
        authenticode = [ordered]@{ status = [string]$signature.Status; thumbprint = $signature.SignerCertificate.Thumbprint; package_file_digest_algorithm = [string]$manifest.file_digest_algorithm; authenticode_file_digest_algorithm = [string]$manifest.signature.authenticode_file_digest_algorithm; certificate_signature_algorithm = [string]$manifest.signature.certificate_signature_algorithm }
        sample = [ordered]@{ input = $sampleIdentity; evidence_copy = Get-StructAutomateFileIdentity $workbookCopy; setup = $sampleSetup; tables = $inputTables }; lifecycle = $lifecycle
        udf_purity = [ordered]@{ formula = '=STR.REBAR.AREA(20)'; value = $udfProbeValue; reset = $hostEffectReset; capture = $hostEffectCapture; total_effects = [Int64]$hostEffectCapture.json.total_effects }
        commands = [ordered]@{ create_validate = $createValidate; xl_cmd_03 = [ordered]@{ initial_full_calculation_ms = $warmups[0]; warmups_ms = $warmups; warmup_reused_current_results = $warmupReuse; samples_ms = $warmSamples; samples_reused_current_results = $warmSampleReuse; cache_verified = -not ($warmSampleReuse | Where-Object { -not $_ }); median_ms = $warmMedian; p95_ms = $warmP95 }; optimize = $optimize; export = $export; measure_diagnose = $measureDiagnose; rollback = $rollback; progress = $progress; cancellation = $cancel; reconstruction = $diagnostic; legacy_schema_recalculation = $legacySchemaRecalculation; drift_reconstruction = $driftDiagnostic; drift_recalculation = $recalculatedAfterDrift }
        export_package = [ordered]@{ artifact = $exportIdentity; schema_version = [string]$exportBundle.schema_version; member_package_count = @($exportBundle.packages).Count; receipt_bound = $true }
        rollback = [ordered]@{ table = $RollbackSentinelTable; column = $RollbackSentinelColumn; row = $RollbackSentinelRow; preimage = $preimage; postimage = $postimage; structural_results_preimage_sha256 = $preRollbackResultsSha256; structural_results_postimage_sha256 = $postRollbackResultsSha256; probe_receipt = Get-StructAutomateFileIdentity $rollbackReceiptPath; probe_receipt_state = [string]$rollbackReceipt.state }
        reconstruction = [ordered]@{ before = $preReopen; after = $postReopen; result_identity_preserved = $reconstructionMatches }
        legacy_schema_upgrade = [ordered]@{ freshness_change = $legacyFreshnessChange; receipt_change = $legacyReceiptChange; reference_calculation_result_id_sha256 = $calculationReferenceTables.StructuralResults.result_id_sha256; recalculation = $legacySchemaRecalculation; after_recalculation = $postLegacySchemaRecalculation; passed = $legacySchemaUpgrade }
        runtime_fingerprint_invalidation = [ordered]@{ synthetic_prior_fingerprint = $syntheticPriorFingerprint; mutated_row_count = $driftedRowCount; before_restart = $preDriftRestart; after_restart = $postDriftRestart; rejected_reconstruction = $driftDiagnostic; recalculation = $recalculatedAfterDrift; after_recalculation = $postDriftRecalculation; prior_live_evidence_reused = [bool]$recalculatedAfterDrift.json.reused_current_results; passed = $runtimeFingerprintInvalidation }
        performance = [ordered]@{ workload = [ordered]@{ members = 20; operations = 200; command = 'XL-CMD-03' }; cold_ready_measurement_boundary = 'Fresh Excel automation start through installed STR.INFO.VERSION response; registry precondition, host configuration, and AddIns lifecycle enumeration are verified outside the timed interval.'; cold_launch_samples_ms = $coldSamples; cold_ready_max_ms = $coldMax; memory_baseline_bytes = $memoryBaselineBytes; memory_after_commands_bytes = $memoryAfterCommandsBytes; memory_delta_mib = $workingSetDeltaMiB }
        budgets = [ordered]@{ warm_median_ms = $WarmMedianBudgetMs; warm_p95_ms = $WarmP95BudgetMs; cold_ready_ms = $ColdReadyBudgetMs; progress_and_cancellation_ms = $ProgressAndCancellationBudgetMs; memory_delta_mib = $ExcelWorkingSetDeltaBudgetMiB }; checks = $checks
    }
    if (-not $receipt.passed) { throw 'Installed acceptance evidence exceeded one or more required thresholds.' }
}
catch {
    $failure = $_.Exception.Message
    if ($null -eq $receipt) { $receipt = [ordered]@{ schema_version = 'structautomate.excel-installed-acceptance/v3'; passed = $false; observed_at_utc = [DateTimeOffset]::UtcNow.ToString('o'); failure = $failure } }
}

Write-StructAutomateJson -Value $receipt -Path $receiptPath
$receipt | ConvertTo-Json -Depth 40
if ($failure) { exit 1 }
