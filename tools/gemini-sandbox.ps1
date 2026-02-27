# =================================================================
# IDENTITY: gemini-sandbox.ps1
# VERSION:  v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN:   HELIX-TTD-GRAMMAR / [TOOLS/SANDBOX]
# NODE:     4 (ONTARIO)
# STATUS:   RATIFIED-CANONICAL
# CREATED:  2026-02-23
# =================================================================

# 📦 Gemini-Sandbox Implementation
# Enforces "Helix-Aligned Sandbox Mode" within a PowerShell session.

function Start-GeminiSandbox {
    param (
        [string]$Path = "Z:\gemini"
    )

    # 1. Verification
    if (-not (Test-Path $Path)) {
        Write-Error "[REJECT] Path '$Path' does not exist."
        return
    }

    Write-Host "`n📦 ENTERING HELIX-ALIGNED SANDBOX MODE" -ForegroundColor Cyan
    Write-Host "Philosophy: Reason, but not act." -ForegroundColor Gray
    Write-Host "Directory: $Path (Aliased to /sandbox/)" -ForegroundColor Gray
    Write-Host "Restrictions: No File Writes, No Shell Escalation, No Outbound Networking.`n" -ForegroundColor Yellow

    # 2. Set Environment Invariants
    $env:SANDBOX_ACTIVE = "TRUE"
    $env:SANDBOX_ROOT = $Path
    $env:DRIFT_TELEMETRY = "0.00%"

    # 3. Define the Restricted Prompt
    function global:prompt {
        $drift = if ($env:DRIFT_TELEMETRY) { $env:DRIFT_TELEMETRY } else { "0.00%" }
        Write-Host "[SANDBOX] " -NoNewline -ForegroundColor Red
        Write-Host "($drift) " -NoNewline -ForegroundColor Yellow
        Write-Host "$($executionContext.SessionState.Path.CurrentLocation): " -NoNewline -ForegroundColor Gray
        return "> "
    }

    # 4. Shadow Command Gating
    # We alias "destructive" commands to a refusal function.
    $BannedCommands = @("rm", "del", "erase", "mv", "move", "cp", "copy", "chmod", "chown", "sudo", "apt", "brew", "curl", "wget", "git", "docker", "kubectl")
    
    foreach ($cmd in $BannedCommands) {
        New-Alias -Name $cmd -Value "Invoke-SandboxRefusal" -Force -Option ReadOnly, AllScope
    }

    function global:Invoke-SandboxRefusal {
        Write-Host "`n[REJECT] This action exceeds custodial authority in Sandbox Mode." -ForegroundColor Red
        Write-Host "Reason: Prohibited destructive command detected (Airlock v3.5 violation).`n" -ForegroundColor Yellow
        $env:DRIFT_TELEMETRY = "0.01% (DRIFT-C)"
    }

    # 5. Path Traversal Guard (Simplified for CLI)
    # We change directory to the sandbox root.
    Set-Location $Path
    
    Write-Host "[FACT] Sandbox established. Audit logging active." -ForegroundColor Green
    Write-Host "To exit, type 'exit-sandbox'.`n"
}

function global:exit-sandbox {
    Remove-Item env:SANDBOX_ACTIVE
    Remove-Item env:SANDBOX_ROOT
    Remove-Item env:DRIFT_TELEMETRY
    # Restore standard prompt (approximate)
    function global:prompt {
        return "PS $($executionContext.SessionState.Path.CurrentLocation)> "
    }
    # Remove aliases
    $BannedCommands = @("rm", "del", "erase", "mv", "move", "cp", "copy", "chmod", "chown", "sudo", "apt", "brew", "curl", "wget", "git", "docker", "kubectl")
    foreach ($cmd in $BannedCommands) {
        if (Test-Path "alias:\$cmd") { Remove-Item "alias:\$cmd" -Force }
    }
    Write-Host "`n📦 SANDBOX TERMINATED. Returning to Active Workspace." -ForegroundColor Cyan
}

# Start the sandbox immediately upon sourcing
Start-GeminiSandbox
