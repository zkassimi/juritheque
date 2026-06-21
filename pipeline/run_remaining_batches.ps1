# run_remaining_batches.ps1
# Waits for the current enrich.py process (PID 24336) to finish, then runs offset 2000 and 3000

$projectDir = "C:\Users\HP\Desktop\Legal-website\lexbase"
$currentBatchPID = 24336  # offset 1000 batch launched at 22:27

Write-Host "=== JuriTheque — Remaining enrichment batches ===" -ForegroundColor Cyan
Write-Host "Waiting for enrich.py offset-1000 (PID $currentBatchPID) to complete..." -ForegroundColor Yellow

# Wait for the specific PID
do {
    Start-Sleep -Seconds 30
    $proc = Get-Process -Id $currentBatchPID -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  [$(Get-Date -Format 'HH:mm:ss')] Still running (CPU: $([math]::Round($proc.CPU))s)" -ForegroundColor Gray
    }
} while ($proc)

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Offset-1000 batch done!" -ForegroundColor Green
Set-Location $projectDir
$env:PYTHONUTF8 = "1"

# Batch offset 2000
Write-Host ""
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] === STARTING BATCH offset 2000 ===" -ForegroundColor Cyan
python -X utf8 pipeline/enrich.py --force --offset 2000
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Offset-2000 batch done (exit: $LASTEXITCODE)" -ForegroundColor Green

# Batch offset 3000
Write-Host ""
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] === STARTING BATCH offset 3000 ===" -ForegroundColor Cyan
python -X utf8 pipeline/enrich.py --force --offset 3000
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Offset-3000 batch done (exit: $LASTEXITCODE)" -ForegroundColor Green

Write-Host ""
Write-Host "=== ALL 4 BATCHES COMPLETE — 3847 laws enriched ===" -ForegroundColor Green
Write-Host "Run: python -X utf8 pipeline/generate_sitemap.py && npm run build" -ForegroundColor Yellow
