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
$registration = [ordered]@{
    requested = -not $SkipExcelRegistration
    succeeded = $false
    addin_name = $null
    addin_full_name = $null
}
if (-not $SkipExcelRegistration) {
    $excel = New-Object -ComObject Excel.Application
    $addIns = $null
    $addin = $null
    try {
        $excel.Visible = $false
        $excel.DisplayAlerts = $false
        $addIns = $excel.AddIns
        $addin = $addIns.Add($installedXll, $false)
        $addin.Installed = $true
        $registration.addin_name = [string]$addin.Name
        $registration.addin_full_name = [string]$addin.FullName
        $registration.succeeded = [bool]$addin.Installed
    }
    finally {
        Release-StructAutomateComObject $addin
        Release-StructAutomateComObject $addIns
        Close-StructAutomateExcelApplication $excel
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
