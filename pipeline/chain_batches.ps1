$ErrorActionPreference = "Continue"
Set-Location "C:\Users\HP\Desktop\Legal-website\lexbase"
$logFile = "pipeline\enrich_batches_log.txt"
Add-Content $logFile ""
Add-Content $logFile "=== NEW RUN STARTED $(Get-Date) ==="

Write-Host "[$(Get-Date -Format HH:mm:ss)] BATCH 1/3 — offset 1000 (re-process with new prompt)"
"[$(Get-Date)] BATCH 1/3 — offset 1000 started" | Add-Content $logFile
& python -X utf8 pipeline/enrich.py --force --offset 1000 2>&1 | Tee-Object -Append -FilePath $logFile
"[$(Get-Date)] BATCH 1/3 — offset 1000 DONE" | Add-Content $logFile

Write-Host "[$(Get-Date -Format HH:mm:ss)] BATCH 2/3 — offset 2000"
"[$(Get-Date)] BATCH 2/3 — offset 2000 started" | Add-Content $logFile
& python -X utf8 pipeline/enrich.py --force --offset 2000 2>&1 | Tee-Object -Append -FilePath $logFile
"[$(Get-Date)] BATCH 2/3 — offset 2000 DONE" | Add-Content $logFile

Write-Host "[$(Get-Date -Format HH:mm:ss)] BATCH 3/3 — offset 3000"
"[$(Get-Date)] BATCH 3/3 — offset 3000 started" | Add-Content $logFile
& python -X utf8 pipeline/enrich.py --force --offset 3000 2>&1 | Tee-Object -Append -FilePath $logFile
"[$(Get-Date)] BATCH 3/3 — offset 3000 DONE" | Add-Content $logFile

"[$(Get-Date)] === ALL BATCHES COMPLETE ===" | Add-Content $logFile
Write-Host "ALL DONE. Run: python -X utf8 pipeline/generate_sitemap.py && npm run build"
