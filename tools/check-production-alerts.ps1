param(
    [string]$ServiceUrl = "https://constitutional-guardian-231586465188.us-central1.run.app",
    [string]$AdminToken = "",
    [string]$StateFile = "",
    [string]$JsonOutput = "",
    [int]$StateRetentionHours = 24,
    [int]$ArtifactGraceMinutes = 30,
    [switch]$FailOnWarning
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $StateFile) {
    $StateFile = Join-Path $env:TEMP "helix-production-alert-state.json"
}

function Invoke-HelixJson {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [hashtable]$Headers = @{}
    )

    try {
        $body = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get
        return [pscustomobject]@{ StatusCode = 200; Body = $body }
    }
    catch {
        $response = $_.Exception.Response
        if ($null -ne $response) {
            $statusCode = [int]$response.StatusCode
            $stream = $response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $rawBody = $reader.ReadToEnd()
            $reader.Dispose()
            return [pscustomobject]@{ StatusCode = $statusCode; Body = $rawBody }
        }
        throw
    }
}

function Invoke-HelixText {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [hashtable]$Headers = @{}
    )

    $response = Invoke-WebRequest -Uri $Url -Headers $Headers -Method Get
    return [pscustomobject]@{
        StatusCode = [int]$response.StatusCode
        Body = [string]$response.Content
    }
}

function Add-Result {
    param(
        [Parameter(Mandatory = $true)][object]$Results,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Severity,
        [Parameter(Mandatory = $true)][bool]$Passed,
        [Parameter(Mandatory = $true)][string]$Details
    )

    [void]$Results.Add([pscustomobject]@{
        Check = $Name
        Severity = $Severity
        Passed = $Passed
        Details = $Details
    })
}

function Write-AlertSummary {
    param(
        [string]$OutputPath,
        [datetime]$EvaluatedAt,
        [string]$BaseUrl,
        [string]$OverallStatus,
        [string]$ArtifactStatus = 'missing',
        [string]$ArtifactImage = 'missing',
        [string]$StorageBackend = 'missing',
        [string]$StorageMode = 'missing',
        [object[]]$PageFailures = @(),
        [object[]]$WarnFailures = @(),
        [object[]]$Checks = @()
    )

    if (-not $OutputPath) {
        return
    }

    $jsonDir = Split-Path -Path $OutputPath -Parent
    if ($jsonDir) {
        New-Item -ItemType Directory -Path $jsonDir -Force | Out-Null
    }

    $summary = [pscustomobject]@{
        evaluated_at = $EvaluatedAt.ToString('o')
        service_url = $BaseUrl
        overall_status = $OverallStatus
        artifact_status = $ArtifactStatus
        artifact_image = $ArtifactImage
        storage_backend = $StorageBackend
        storage_mode = $StorageMode
        page_failures = @($PageFailures)
        warn_failures = @($WarnFailures)
        checks = @($Checks)
    }

    $summary | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
}

function Parse-PrometheusLabels {
    param([string]$Raw)

    $labels = @{}
    if (-not $Raw) { return $labels }

    foreach ($part in ($Raw -split ',')) {
        if ($part -match '^([^=]+)="(.*)"$') {
            $labels[$matches[1]] = $matches[2].Replace('\"', '"').Replace('\\', '\')
        }
    }
    return $labels
}

function Parse-PrometheusText {
    param([string]$Text)

    $samples = New-Object 'System.Collections.Generic.List[object]'
    foreach ($line in ($Text -split "`n")) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) {
            continue
        }

        if ($trimmed -match '^(?<name>[a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(?<labels>[^}]*)\})?\s+(?<value>-?\d+(?:\.\d+)?)$') {
            [void]$samples.Add([pscustomobject]@{
                Name = $matches['name']
                Labels = Parse-PrometheusLabels -Raw $matches['labels']
                Value = [double]$matches['value']
            })
        }
    }
    return $samples
}

function Get-MetricValue {
    param(
        [Parameter(Mandatory = $true)][object[]]$Samples,
        [Parameter(Mandatory = $true)][string]$Name,
        [hashtable]$Labels = @{},
        [double]$Default = [double]::NaN
    )

    foreach ($sample in $Samples) {
        if ($sample.Name -ne $Name) { continue }

        $match = $true
        foreach ($key in $Labels.Keys) {
            if (-not $sample.Labels.ContainsKey($key) -or $sample.Labels[$key] -ne $Labels[$key]) {
                $match = $false
                break
            }
        }

        if ($match) {
            return [double]$sample.Value
        }
    }

    return $Default
}

function Get-MetricLabelValue {
    param(
        [Parameter(Mandatory = $true)][object[]]$Samples,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label,
        [hashtable]$Labels = @{},
        [string]$Default = "missing"
    )

    foreach ($sample in $Samples) {
        if ($sample.Name -ne $Name) { continue }

        $match = $true
        foreach ($key in $Labels.Keys) {
            if (-not $sample.Labels.ContainsKey($key) -or $sample.Labels[$key] -ne $Labels[$key]) {
                $match = $false
                break
            }
        }

        if ($match -and $sample.Labels.ContainsKey($Label)) {
            return [string]$sample.Labels[$Label]
        }
    }

    return $Default
}

function Load-State {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return [pscustomobject]@{ snapshots = @() }
    }

    $raw = Get-Content -Path $Path -Raw -Encoding UTF8
    if (-not $raw.Trim()) {
        return [pscustomobject]@{ snapshots = @() }
    }

    return $raw | ConvertFrom-Json
}

function Save-State {
    param(
        [string]$Path,
        [object]$State
    )

    $dir = Split-Path -Path $Path -Parent
    if ($dir) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $State | ConvertTo-Json -Depth 8 | Set-Content -Path $Path -Encoding UTF8
}

function Get-BaselineSnapshot {
    param(
        [object[]]$Snapshots,
        [datetime]$Now,
        [int]$WindowMinutes
    )

    $target = $Now.AddMinutes(-$WindowMinutes)
    $eligible = @($Snapshots | Where-Object { [datetime]$_.timestamp -le $target } | Sort-Object timestamp -Descending)
    if ($eligible.Count -gt 0) {
        return $eligible[0]
    }
    return $null
}

function Get-CounterDelta {
    param(
        [object]$Current,
        [object]$Baseline,
        [string]$Field
    )

    if ($null -eq $Baseline) {
        return $null
    }

    $currentValue = [double]$Current.counters.$Field
    $baselineValue = [double]$Baseline.counters.$Field
    return [math]::Max($currentValue - $baselineValue, 0)
}

$baseUrl = $ServiceUrl.TrimEnd('/')
$headers = @{}
if ($AdminToken) {
    $headers['X-Helix-Admin-Token'] = $AdminToken
}

if (-not $AdminToken) {
    throw "AdminToken is required for alert evaluation."
}

$results = New-Object 'System.Collections.Generic.List[object]'
$now = (Get-Date).ToUniversalTime()

$metricsResponse = Invoke-HelixText -Url "$baseUrl/metrics" -Headers $headers
if ($metricsResponse.StatusCode -ne 200) {
    Add-Result -Results $results -Name 'metrics-scrape' -Severity 'page' -Passed $false -Details "status=$($metricsResponse.StatusCode)"
    $results | Format-Table -AutoSize | Out-String | Write-Host
    Write-AlertSummary -OutputPath $JsonOutput -EvaluatedAt $now -BaseUrl $baseUrl -OverallStatus 'page' -PageFailures @($results) -Checks @($results)
    exit 1
}

$securityResponse = Invoke-HelixJson -Url "$baseUrl/api/security-transparency" -Headers $headers
if ($securityResponse.StatusCode -ne 200) {
    Add-Result -Results $results -Name 'security-transparency' -Severity 'page' -Passed $false -Details "status=$($securityResponse.StatusCode)"
    $results | Format-Table -AutoSize | Out-String | Write-Host
    Write-AlertSummary -OutputPath $JsonOutput -EvaluatedAt $now -BaseUrl $baseUrl -OverallStatus 'page' -PageFailures @($results) -Checks @($results)
    exit 1
}

$samples = Parse-PrometheusText -Text $metricsResponse.Body
$artifactStatus = Get-MetricLabelValue -Samples $samples -Name 'helix_artifact_analysis_state' -Label 'status'
$artifactImage = Get-MetricLabelValue -Samples $samples -Name 'helix_artifact_analysis_state' -Label 'image_uri'
$storageBackend = Get-MetricLabelValue -Samples $samples -Name 'helix_receipt_storage_backend' -Label 'backend'
$storageMode = Get-MetricLabelValue -Samples $samples -Name 'helix_receipt_storage_backend' -Label 'mode'
$originEnforced = Get-MetricValue -Samples $samples -Name 'helix_guardian_origin_enforced'
$authEnforced = Get-MetricValue -Samples $samples -Name 'helix_operator_auth_enforced'

$currentSnapshot = [pscustomobject]@{
    timestamp = $now.ToString('o')
    counters = [pscustomobject]@{
        operator_auth_failure = Get-MetricValue -Samples $samples -Name 'helix_security_events_total' -Labels @{ event = 'operator_auth_failure' } -Default 0
        operator_rate_limit = Get-MetricValue -Samples $samples -Name 'helix_security_events_total' -Labels @{ event = 'operator_rate_limit' } -Default 0
        audio_rate_limit = Get-MetricValue -Samples $samples -Name 'helix_security_events_total' -Labels @{ event = 'audio_rate_limit' } -Default 0
        websocket_auth_failure = Get-MetricValue -Samples $samples -Name 'helix_security_events_total' -Labels @{ event = 'websocket_auth_failure' } -Default 0
    }
    artifact_status = $artifactStatus
    artifact_image = $artifactImage
    storage_backend = $storageBackend
    storage_mode = $storageMode
    origin_enforced = $originEnforced
    auth_enforced = $authEnforced
}

$state = Load-State -Path $StateFile
$existingSnapshots = @($state.snapshots)
$retentionCutoff = $now.AddHours(-$StateRetentionHours)
$keptSnapshots = @($existingSnapshots | Where-Object { [datetime]$_.timestamp -ge $retentionCutoff })
$allSnapshots = @($keptSnapshots + $currentSnapshot)
$state = [pscustomobject]@{ snapshots = $allSnapshots }
Save-State -Path $StateFile -State $state

Add-Result -Results $results -Name 'operator-auth-enforced' -Severity 'page' -Passed ($authEnforced -eq 1) -Details "value=$authEnforced"
Add-Result -Results $results -Name 'guardian-origin-enforced' -Severity 'page' -Passed ($originEnforced -eq 1) -Details "value=$originEnforced"
Add-Result -Results $results -Name 'receipt-backend-posture' -Severity 'page' -Passed ($storageBackend -eq 'gcs+local' -and $storageMode -eq 'dual') -Details "backend=$storageBackend; mode=$storageMode"

$latestScanTimestampRaw = [string]$securityResponse.Body.latest_scan_timestamp
$artifactScanTimestampRaw = [string]$securityResponse.Body.artifact_analysis.scan_timestamp
$artifactAgeDetails = "status=$artifactStatus; image_uri=$artifactImage"
$artifactPassed = $true
if ($artifactStatus -eq 'unverified') {
    $deployAnchor = $null
    if ($latestScanTimestampRaw -and $latestScanTimestampRaw -ne 'unavailable') {
        try { $deployAnchor = [datetime]::Parse($latestScanTimestampRaw).ToUniversalTime() } catch { $deployAnchor = $null }
    }

    if ($null -ne $deployAnchor) {
        $ageMinutes = [math]::Round(($now - $deployAnchor).TotalMinutes, 1)
        $artifactPassed = $ageMinutes -le $ArtifactGraceMinutes
        $artifactAgeDetails += "; unverified_for_minutes=$ageMinutes"
    }
    else {
        $artifactPassed = $false
        $artifactAgeDetails += '; unverified_for_minutes=unknown'
    }
}
elseif ($artifactStatus -eq 'clean') {
    $artifactAgeDetails += "; verified_at=$artifactScanTimestampRaw"
}
Add-Result -Results $results -Name 'artifact-verification-window' -Severity 'warn' -Passed $artifactPassed -Details $artifactAgeDetails

$thresholds = @(
    @{ Name = 'operator-auth-failure-burst-5m'; Severity = 'warn'; Field = 'operator_auth_failure'; Window = 5; Threshold = 5 },
    @{ Name = 'operator-auth-failure-burst-15m'; Severity = 'page'; Field = 'operator_auth_failure'; Window = 15; Threshold = 20 },
    @{ Name = 'operator-rate-limit-burst-10m'; Severity = 'warn'; Field = 'operator_rate_limit'; Window = 10; Threshold = 10 },
    @{ Name = 'operator-rate-limit-burst-15m'; Severity = 'page'; Field = 'operator_rate_limit'; Window = 15; Threshold = 50 },
    @{ Name = 'audio-rate-limit-burst-5m'; Severity = 'warn'; Field = 'audio_rate_limit'; Window = 5; Threshold = 10 },
    @{ Name = 'audio-rate-limit-burst-10m'; Severity = 'page'; Field = 'audio_rate_limit'; Window = 10; Threshold = 30 },
    @{ Name = 'websocket-auth-failure-burst-5m'; Severity = 'warn'; Field = 'websocket_auth_failure'; Window = 5; Threshold = 5 },
    @{ Name = 'websocket-auth-failure-burst-15m'; Severity = 'page'; Field = 'websocket_auth_failure'; Window = 15; Threshold = 20 }
)

foreach ($rule in $thresholds) {
    $baseline = Get-BaselineSnapshot -Snapshots $allSnapshots -Now $now -WindowMinutes $rule.Window
    if ($null -eq $baseline) {
        Add-Result -Results $results -Name $rule.Name -Severity $rule.Severity -Passed $true -Details "insufficient_history=true; window_minutes=$($rule.Window)"
        continue
    }

    $delta = Get-CounterDelta -Current $currentSnapshot -Baseline $baseline -Field $rule.Field
    $passed = $delta -lt $rule.Threshold
    Add-Result -Results $results -Name $rule.Name -Severity $rule.Severity -Passed $passed -Details "delta=$delta; threshold=$($rule.Threshold); window_minutes=$($rule.Window)"
}

$results | Format-Table -AutoSize | Out-String | Write-Host

$pageFailures = @($results | Where-Object { -not $_.Passed -and $_.Severity -eq 'page' })
$warnFailures = @($results | Where-Object { -not $_.Passed -and $_.Severity -eq 'warn' })
$exitCode = 0
$overallStatus = 'pass'

if ($pageFailures.Count -gt 0) {
    $exitCode = 1
    $overallStatus = 'page'
}
elseif ($FailOnWarning -and $warnFailures.Count -gt 0) {
    $exitCode = 2
    $overallStatus = 'warn'
}
elseif ($warnFailures.Count -gt 0) {
    $overallStatus = 'warn'
}

$summary = [pscustomobject]@{
    evaluated_at = $now.ToString('o')
    service_url = $baseUrl
    overall_status = $overallStatus
    artifact_status = $artifactStatus
    artifact_image = $artifactImage
    storage_backend = $storageBackend
    storage_mode = $storageMode
    page_failures = @($pageFailures)
    warn_failures = @($warnFailures)
    checks = @($results)
}

Write-AlertSummary -OutputPath $JsonOutput -EvaluatedAt $now -BaseUrl $baseUrl -OverallStatus $overallStatus -ArtifactStatus $artifactStatus -ArtifactImage $artifactImage -StorageBackend $storageBackend -StorageMode $storageMode -PageFailures @($pageFailures) -WarnFailures @($warnFailures) -Checks @($results)

if ($exitCode -eq 1) {
    Write-Host "Production alert check failed with page-level findings." -ForegroundColor Red
    exit 1
}

if ($exitCode -eq 2) {
    Write-Host "Production alert check failed with warning-level findings." -ForegroundColor Yellow
    exit 2
}

if ($warnFailures.Count -gt 0) {
    Write-Host "Production alert check completed with warnings." -ForegroundColor Yellow
    exit 0
}

Write-Host "Production alert check passed." -ForegroundColor Green
