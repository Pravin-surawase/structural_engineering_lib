[CmdletBinding()]
param([Parameter(Mandatory)][string]$DistributionDirectory)

. (Join-Path $PSScriptRoot 'Common.ps1')

$distribution = [System.IO.Path]::GetFullPath($DistributionDirectory)
$manifest = Get-Content -Raw -LiteralPath (Join-Path $distribution 'manifest.json') | ConvertFrom-Json
$installDirectory = Assert-StructAutomateSafeInstallPath (Join-Path (Get-StructAutomateInstallRoot) ([string]$manifest.version))
$before = @()
if (Test-Path -LiteralPath $installDirectory) {
    $before = @(Get-ChildItem -LiteralPath $installDirectory -File | ForEach-Object { Get-StructAutomateFileIdentity $_.FullName })
}

$installOutput = & (Join-Path $PSScriptRoot 'Install-PerUser.ps1') -DistributionDirectory $distribution
$after = @(Get-ChildItem -LiteralPath $installDirectory -File | ForEach-Object { Get-StructAutomateFileIdentity $_.FullName })
$installReceipt = ($installOutput -join [Environment]::NewLine | ConvertFrom-Json)

$receipt = [ordered]@{
    schema_version = 'structautomate.excel-repair/v1'
    completed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    source_commit = [string]$manifest.source_commit
    distribution_manifest = Get-StructAutomateFileIdentity (Join-Path $distribution 'manifest.json')
    install_directory = $installDirectory
    files_before = $before
    files_after = $after
    install_receipt = $installReceipt
}
$receiptDirectory = Get-StructAutomateReceiptRoot
[void](New-Item -ItemType Directory -Path $receiptDirectory -Force)
Write-StructAutomateJson -Value $receipt -Path (Join-Path $receiptDirectory 'excel-repair.json')
$receipt | ConvertTo-Json -Depth 30
