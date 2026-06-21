@echo off
cd /d "C:\Users\HP\Desktop\Legal-website\lexbase"
set PYTHONUTF8=1

echo [%TIME%] Debut enrichissement >> pipeline\run_all.log 2>&1

echo [%TIME%] --- Offset 0 (IDs 1-999) --- >> pipeline\run_all.log 2>&1
python -X utf8 pipeline/enrich.py --force --offset 0 >> pipeline\run_all.log 2>&1

echo [%TIME%] --- Offset 1000 (IDs 1000-1999) --- >> pipeline\run_all.log 2>&1
python -X utf8 pipeline/enrich.py --force --offset 1000 >> pipeline\run_all.log 2>&1

echo [%TIME%] --- Offset 2000 (IDs 2000-2999) --- >> pipeline\run_all.log 2>&1
python -X utf8 pipeline/enrich.py --force --offset 2000 >> pipeline\run_all.log 2>&1

echo [%TIME%] --- Offset 3000 (IDs 3000+) --- >> pipeline\run_all.log 2>&1
python -X utf8 pipeline/enrich.py --force --offset 3000 >> pipeline\run_all.log 2>&1

echo [%TIME%] TOUT TERMINE - Regeneration sitemap >> pipeline\run_all.log 2>&1
python -X utf8 pipeline/generate_sitemap.py >> pipeline\run_all.log 2>&1

echo [%TIME%] COMPLET - npm run build pour deployer >> pipeline\run_all.log 2>&1
