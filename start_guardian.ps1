# 🛡️ Constitutional Guardian - Automated Launch Script
# [FACT] Version: 1.3.2 (Phase 6.1)
# [HYPOTHESIS] Automation ensures recording stability

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n=== 🦉 INITIALIZING CONSTITUTIONAL LATTICE ===" -ForegroundColor Cyan

# 1. Clear Port 8180
Write-Host "[1/4] Clearing Port 8180..." -NoNewline
$pids = (Get-NetTCPConnection -LocalPort 8180).OwningProcess
if ($pids) {
    foreach ($p in $pids) { Stop-Process -Id $p -Force }
    Write-Host " DONE (Killed ghost processes)" -ForegroundColor Green
} else {
    Write-Host " DONE (Already clear)" -ForegroundColor Gray
}

# 2. Verify Environment
Write-Host "[2/4] Verifying Python Dependencies..." -NoNewline
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host " DONE" -ForegroundColor Green
} else {
    Write-Host " ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# 3. Set Environment Variables
Write-Host "[3/4] Configuring Node Environment..." -NoNewline
$env:PYTHONPATH = "helix_code"
$env:HELIX_NODE_ID = "GCS-GUARDIAN-OTTAWA"
$env:HELIX_ENV = "recording"
Write-Host " DONE" -ForegroundColor Green

# 4. Start the Guardian
Write-Host "[4/4] Launching Guardian Server..." -ForegroundColor Cyan
Write-Host "Navigate to: http://localhost:8180/" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the node.`n" -ForegroundColor Gray

# [FACT] Execute server
python helix_code/live_guardian.py
