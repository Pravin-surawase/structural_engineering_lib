[CmdletBinding()]
param(
    [string]$Subject = 'CN=StructAutomate WP09 Validation',
    [string]$OutputDirectory,
    [switch]$TrustForCurrentUser
)

. (Join-Path $PSScriptRoot 'Common.ps1')

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $PSScriptRoot '..\..\..\tmp\wp09-certificate'
}

$output = Assert-StructAutomateSafeRepositoryOutput $OutputDirectory
[void](New-Item -ItemType Directory -Path $output -Force)

$now = Get-Date
$certificate = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object {
    $_.Subject -eq $Subject -and $_.NotAfter -gt $now.AddDays(30) -and $_.HasPrivateKey
} | Sort-Object NotAfter -Descending | Select-Object -First 1

$created = $false
if (-not $certificate) {
    $certificate = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject $Subject `
        -CertStoreLocation 'Cert:\CurrentUser\My' `
        -KeyAlgorithm RSA `
        -KeyLength 3072 `
        -HashAlgorithm SHA256 `
        -KeyExportPolicy NonExportable `
        -NotAfter $now.AddYears(2)
    $created = $true
}

$publicPath = Join-Path $output 'StructAutomate-WP09-Validation.cer'
[void](Export-Certificate -Cert $certificate -FilePath $publicPath -Force)

$trustedStores = @()
if ($TrustForCurrentUser) {
    foreach ($store in @('Cert:\CurrentUser\Root', 'Cert:\CurrentUser\TrustedPublisher')) {
        $present = Get-ChildItem -Path $store | Where-Object Thumbprint -eq $certificate.Thumbprint
        if (-not $present) { [void](Import-Certificate -FilePath $publicPath -CertStoreLocation $store) }
        $trustedStores += $store
    }
}

$receipt = [ordered]@{
    schema_version = 'structautomate.validation-certificate/v1'
    created = $created
    subject = $certificate.Subject
    thumbprint = $certificate.Thumbprint
    serial_number = $certificate.SerialNumber
    not_before = $certificate.NotBefore.ToUniversalTime().ToString('o')
    not_after = $certificate.NotAfter.ToUniversalTime().ToString('o')
    public_certificate = (Get-StructAutomateFileIdentity $publicPath)
    trusted_current_user_stores = $trustedStores
    purpose = 'Local WP09 installed-behaviour evidence; not a public-distribution certificate.'
}
$receiptPath = Join-Path $output 'validation-certificate-receipt.json'
Write-StructAutomateJson -Value $receipt -Path $receiptPath
$receipt | ConvertTo-Json -Depth 10
