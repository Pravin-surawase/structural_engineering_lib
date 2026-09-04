[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$DistributionDirectory,
    [switch]$SkipExcelRegistration
)

. (Join-Path $PSScriptRoot 'Common.ps1')

$distribution = [System.IO.Path]::GetFullPath($DistributionDirectory)
$manifestPath = Join-Path $distribution 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Manifest is missing: $manifestPath" }
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json

$receiptDirectory = Get-StructAutomateReceiptRoot
[void](New-Item -ItemType Directory -Path $receiptDirectory -Force)
$preflightPath = Assert-StructAutomateSafeReceiptPath (Join-Path $receiptDirectory 'excel-install-preflight.json')
& (Join-Path $PSScriptRoot 'Test-Preflight.ps1') -DistributionDirectory $distribution -ReceiptPath $preflightPath | Out-Null

$installRoot = Get-StructAutomateInstallRoot
$installDirectory = Assert-StructAutomateSafeInstallPath (Join-Path $installRoot ([string]$manifest.version))
if (Get-Process -Name EXCEL -ErrorAction SilentlyContinue) {
    throw 'Close Excel before installing or repairing the add-in.'
}
if (Test-Path -LiteralPath $installDirectory) {
    $verified = Assert-StructAutomateSafeInstallPath $installDirectory
    Remove-Item -LiteralPath $verified -Recurse -Force
}
[void](New-Item -ItemType Directory -Path $installDirectory -Force)

foreach ($file in Get-ChildItem -LiteralPath $distribution -File) {
    Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $installDirectory $file.Name)
}

$installedXll = Join-Path $installDirectory 'StructAutomate.xll'
$startupRegistration = $null
$registration = [ordered]@{
    requested = -not $SkipExcelRegistration
    succeeded = $false
    addin_name = $null
    addin_full_name = $null
    startup = $startupRegistration
}
if (-not $SkipExcelRegistration) {
    $startupRegistration = Register-StructAutomateExcelStartup -XllPath $installedXll
    $registration.startup = $startupRegistration
    try {
        $excel = New-Object -ComObject Excel.Application
        $addIns = $null
        $addin = $null
        $workbooks = $null
        $bootstrapWorkbook = $null
        try {
            $excel.Visible = $false
            $excel.DisplayAlerts = $false
            $workbooks = $excel.Workbooks
            $bootstrapWorkbook = $workbooks.Add()
            $addIns = $excel.AddIns
            for ($index = 1; $index -le $addIns.Count; $index++) {
                $candidate = $null
                try {
                    $candidate = $addIns.Item($index)
                    if ([string]::Equals([string]$candidate.FullName, $installedXll, [System.StringComparison]::OrdinalIgnoreCase)) {
                        $addin = $candidate
                        $candidate = $null
                        break
                    }
                }
                finally { Release-StructAutomateComObject $candidate }
            }
            if (-not $addin) { $addin = $addIns.Add($installedXll, $false) }
            $addin.Installed = $true
            $registration.addin_name = [string]$addin.Name
            $registration.addin_full_name = [string]$addin.FullName
            $registration.succeeded = [bool]$addin.Installed
        }
        finally {
            if ($bootstrapWorkbook) {
                try { $bootstrapWorkbook.Close($false) }
                finally { Release-StructAutomateComObject $bootstrapWorkbook }
            }
            Release-StructAutomateComObject $workbooks
            Release-StructAutomateComObject $addin
            Release-StructAutomateComObject $addIns
            Close-StructAutomateExcelApplication $excel
        }
    }
    catch {
        if ($startupRegistration.created) {
            [void](Unregister-StructAutomateExcelStartup -XllPath $installedXll)
        }
        throw
    }
    if (-not $registration.succeeded) { throw 'Excel did not report the add-in as installed.' }
}

$receipt = [ordered]@{
    schema_version = 'structautomate.excel-install/v1'
    operation = 'install_or_repair'
    completed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    source_commit = [string]$manifest.source_commit
    version = [string]$manifest.version
    install_directory = $installDirectory
    xll = Get-StructAutomateFileIdentity $installedXll
    installed_manifest = Get-StructAutomateFileIdentity (Join-Path $installDirectory 'manifest.json')
    signature_thumbprint = [string]$manifest.signature.thumbprint
    registration = $registration
    preflight_receipt = Get-StructAutomateFileIdentity $preflightPath
}
$receiptPath = Join-Path $receiptDirectory 'excel-install.json'
Write-StructAutomateJson -Value $receipt -Path $receiptPath
Write-StructAutomateJson -Value $receipt -Path (Join-Path $installDirectory 'install-receipt.json')
$receipt | ConvertTo-Json -Depth 20
