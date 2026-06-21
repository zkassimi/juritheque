import subprocess, os, sys, time

os.chdir(r"C:\Users\HP\Desktop\Legal-website\lexbase")
log = open("pipeline\\run_all.log", "a", encoding="utf-8")

def run(offset):
    log.write(f"\n\n=== OFFSET {offset} START ===\n")
    log.flush()
    cmd = [sys.executable, "-X", "utf8", "pipeline\\enrich.py", "--force", f"--offset", str(offset)]
    proc = subprocess.run(cmd, capture_output=False, stdout=log, stderr=log)
    log.write(f"\n=== OFFSET {offset} DONE (exit={proc.returncode}) ===\n")
    log.flush()
    return proc.returncode

run(0)
run(1000)
run(2000)
run(3000)

log.write("\n=== ALL DONE ===\n")
log.flush()
log.close()
