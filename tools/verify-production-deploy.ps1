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


function Get-NestedValue {
    param(
        [Parameter(Mandatory = $true)][AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string[]]$Path,
        [Parameter()][object]$Default = $null
    )

    $current = $Object
    foreach ($segment in $Path) {
        if ($null -eq $current) {
            return $Default
        }

        $property = $current.PSObject.Properties[$segment]
        if ($null -eq $property) {
            return $Default
        }
        $current = $property.Value
    }

    if ($null -eq $current) {
        return $Default
    }
    return $current
}

function Add-CheckResult {
    param(
        [Parameter(Mandatory = $true)][object]$Results,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$Passed,
        [Parameter(Mandatory = $true)][string]$Details
    )

    [void]$Results.Add([pscustomobject]@{
        Check = $Name
        Passed = $Passed
        Details = $Details
    })
}

$results = New-Object 'System.Collections.Generic.List[object]'
$baseUrl = $ServiceUrl.TrimEnd('/')
$authHeaders = @{}
if ($AdminToken) {
    $authHeaders['X-Helix-Admin-Token'] = $AdminToken
}

$health = Invoke-HelixJson -Url "$baseUrl/health"
$healthVersion = Get-NestedValue -Object $health.Body -Path @('version') -Default 'unknown'
$healthPassed = $health.StatusCode -eq 200 -and $healthVersion -ne 'unknown'
Add-CheckResult -Results $results -Name 'health' -Passed $healthPassed -Details "status=$($health.StatusCode); version=$healthVersion"

$unauthRuntime = Invoke-HelixJson -Url "$baseUrl/api/runtime-config"
$expectedUnauth = if ($AdminToken) { 401 } else { @('200','401','503') }
$unauthPassed = if ($AdminToken) { $unauthRuntime.StatusCode -eq 401 } else { $expectedUnauth -contains [string]$unauthRuntime.StatusCode }
Add-CheckResult -Results $results -Name 'runtime-config-auth-gate' -Passed $unauthPassed -Details "status=$($unauthRuntime.StatusCode)"

if ($AdminToken) {
    $runtime = Invoke-HelixJson -Url "$baseUrl/api/runtime-config" -Headers $authHeaders
    $persistenceMode = Get-NestedValue -Object $runtime.Body -Path @('receipts', 'persistence_mode') -Default 'missing'
    $gcsBucketConfigured = [bool](Get-NestedValue -Object $runtime.Body -Path @('receipts', 'gcs_bucket_configured') -Default $false)
    $runtimePassed = $runtime.StatusCode -eq 200 -and $persistenceMode -eq 'dual' -and $gcsBucketConfigured
    Add-CheckResult -Results $results -Name 'runtime-config-authenticated' -Passed $runtimePassed -Details "status=$($runtime.StatusCode); persistence_mode=$persistenceMode; gcs_bucket_configured=$gcsBucketConfigured"

    $security = Invoke-HelixJson -Url "$baseUrl/api/security-transparency" -Headers $authHeaders
    $artifactStatus = Get-NestedValue -Object $security.Body -Path @('artifact_analysis', 'status') -Default 'missing'
    $artifactImage = Get-NestedValue -Object $security.Body -Path @('artifact_analysis', 'image_uri') -Default 'missing'
    $securityPassed = $security.StatusCode -eq 200 -and $artifactImage -like 'us-central1-docker.pkg.dev/*'
    if ($RequireCleanArtifact) {
        $securityPassed = $securityPassed -and $artifactStatus -eq 'clean'
    }
    Add-CheckResult -Results $results -Name 'security-transparency-authenticated' -Passed $securityPassed -Details "status=$($security.StatusCode); artifact_status=$artifactStatus; image_uri=$artifactImage"

    $dashboard = Invoke-HelixJson -Url "$baseUrl/api/audit-dashboard" -Headers $authHeaders
    $storageBackend = Get-NestedValue -Object $dashboard.Body -Path @('storage', 'backend') -Default 'missing'
    $storageTotal = Get-NestedValue -Object $dashboard.Body -Path @('storage', 'total') -Default 'missing'
    $dashboardPassed = $dashboard.StatusCode -eq 200 -and ($storageBackend -eq 'gcs+local' -or $storageBackend -eq 'gcs')
    Add-CheckResult -Results $results -Name 'audit-dashboard-authenticated' -Passed $dashboardPassed -Details "status=$($dashboard.StatusCode); backend=$storageBackend; total=$storageTotal"
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
