param(
    [string]$ServiceUrl = "https://constitutional-guardian-231586465188.us-central1.run.app",
    [string]$AdminToken = "",
    [switch]$RequireCleanArtifact
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-HelixJson {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [hashtable]$Headers = @{}
    )

    try {
        $body = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get
        return [pscustomobject]@{
            StatusCode = 200
            Body = $body
        }
    }
    catch {
        $response = $_.Exception.Response
        if ($null -ne $response) {
            $statusCode = [int]$response.StatusCode
            $stream = $response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $rawBody = $reader.ReadToEnd()
            $reader.Dispose()
            return [pscustomobject]@{
                StatusCode = $statusCode
                Body = $rawBody
            }
        }
        throw
    }
}

function Add-CheckResult {
    param(
        [Parameter(Mandatory = $true)][System.Collections.Generic.List[object]]$Results,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$Passed,
        [Parameter(Mandatory = $true)][string]$Details
    )

    $Results.Add([pscustomobject]@{
        Check = $Name
        Passed = $Passed
        Details = $Details
    }) | Out-Null
}

$results = New-Object 'System.Collections.Generic.List[object]'
$baseUrl = $ServiceUrl.TrimEnd('/')
$authHeaders = @{}
if ($AdminToken) {
    $authHeaders['X-Helix-Admin-Token'] = $AdminToken
}

$health = Invoke-HelixJson -Url "$baseUrl/health"
$healthPassed = $health.StatusCode -eq 200 -and $null -ne $health.Body.version
Add-CheckResult -Results $results -Name 'health' -Passed $healthPassed -Details "status=$($health.StatusCode); version=$($health.Body.version)"

$unauthRuntime = Invoke-HelixJson -Url "$baseUrl/api/runtime-config"
$expectedUnauth = if ($AdminToken) { 401 } else { @('200','401','503') }
$unauthPassed = if ($AdminToken) { $unauthRuntime.StatusCode -eq 401 } else { $expectedUnauth -contains [string]$unauthRuntime.StatusCode }
Add-CheckResult -Results $results -Name 'runtime-config-auth-gate' -Passed $unauthPassed -Details "status=$($unauthRuntime.StatusCode)"

if ($AdminToken) {
    $runtime = Invoke-HelixJson -Url "$baseUrl/api/runtime-config" -Headers $authHeaders
    $runtimePassed = $runtime.StatusCode -eq 200 -and $runtime.Body.receipts.persistence_mode -eq 'dual' -and $runtime.Body.receipts.gcs_bucket_configured
    Add-CheckResult -Results $results -Name 'runtime-config-authenticated' -Passed $runtimePassed -Details "status=$($runtime.StatusCode); persistence_mode=$($runtime.Body.receipts.persistence_mode); gcs_bucket_configured=$($runtime.Body.receipts.gcs_bucket_configured)"

    $security = Invoke-HelixJson -Url "$baseUrl/api/security-transparency" -Headers $authHeaders
    $artifactStatus = $security.Body.artifact_analysis.status
    $artifactImage = $security.Body.artifact_analysis.image_uri
    $securityPassed = $security.StatusCode -eq 200 -and $artifactImage -like 'us-central1-docker.pkg.dev/*'
    if ($RequireCleanArtifact) {
        $securityPassed = $securityPassed -and $artifactStatus -eq 'clean'
    }
    Add-CheckResult -Results $results -Name 'security-transparency-authenticated' -Passed $securityPassed -Details "status=$($security.StatusCode); artifact_status=$artifactStatus; image_uri=$artifactImage"

    $dashboard = Invoke-HelixJson -Url "$baseUrl/api/audit-dashboard" -Headers $authHeaders
    $storageBackend = $dashboard.Body.storage.backend
    $dashboardPassed = $dashboard.StatusCode -eq 200 -and ($storageBackend -eq 'gcs+local' -or $storageBackend -eq 'gcs')
    Add-CheckResult -Results $results -Name 'audit-dashboard-authenticated' -Passed $dashboardPassed -Details "status=$($dashboard.StatusCode); backend=$storageBackend; total=$($dashboard.Body.storage.total)"
}
else {
    Add-CheckResult -Results $results -Name 'authenticated-checks-skipped' -Passed $true -Details 'No admin token supplied; only public and auth-gate checks were run.'
}

$results | Format-Table -AutoSize | Out-String | Write-Host

$failed = @($results | Where-Object { -not $_.Passed })
if ($failed.Count -gt 0) {
    Write-Host "Verification failed." -ForegroundColor Red
    exit 1
}

Write-Host "Verification passed." -ForegroundColor Green
