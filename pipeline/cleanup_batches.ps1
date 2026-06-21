$ErrorActionPreference = "Continue"
Set-Location "C:\Users\HP\Desktop\Legal-website\lexbase"
$logFile = "pipeline\enrich_cleanup_log.txt"
$chainPID = 23200  # chain_batches.ps1 parent PowerShell

"[$(Get-Date)] Waiting for main chain (PID $chainPID) to finish..." | Tee-Object -FilePath $logFile -Append

do {
    Start-Sleep -Seconds 60
    $p = Get-Process -Id $chainPID -ErrorAction SilentlyContinue
    if ($p) { "[$(Get-Date)] Chain still running (CPU=$([math]::Round($p.CPU))s)" | Add-Content $logFile }
} while ($p)

"[$(Get-Date)] Main chain done! Starting cleanup batches..." | Tee-Object -FilePath $logFile -Append

# Re-process offset-0 (IDs 1-999) with new improved prompt
"[$(Get-Date)] CLEANUP 1/2 — offset 0 (upgrade IDs 1-999 to new format)" | Tee-Object -FilePath $logFile -Append
& python -X utf8 pipeline/enrich.py --force --offset 0 2>&1 | Tee-Object -Append -FilePath $logFile

"[$(Get-Date)] CLEANUP 2/2 — offset 1000 (upgrade IDs 1000-1999 + fill missing)" | Tee-Object -FilePath $logFile -Append
& python -X utf8 pipeline/enrich.py --force --offset 1000 2>&1 | Tee-Object -Append -FilePath $logFile

"[$(Get-Date)] === ALL CLEANUP DONE ===" | Tee-Object -FilePath $logFile -Append

# Final sitemap regeneration
"[$(Get-Date)] Regenerating sitemap..." | Add-Content $logFile
& python -X utf8 pipeline/generate_sitemap.py 2>&1 | Tee-Object -Append -FilePath $logFile

"[$(Get-Date)] COMPLETE — run 'npm run build' to deploy" | Tee-Object -FilePath $logFile -Append
