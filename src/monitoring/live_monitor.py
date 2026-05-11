import time
import subprocess

PIPELINE_SCRIPT = "src/pipeline/run_aidac_pipeline.py"

print("=" * 80)
print("AI-DAC LIVE MONITOR STARTED")
print("=" * 80)

while True:

    print("\n[+] Running AI-DAC pipeline...\n")

    result = subprocess.run(
        ["python", PIPELINE_SCRIPT]
    )

    if result.returncode == 0:
        print("[+] Pipeline completed successfully")

    else:
        print("[!] Pipeline failed")

    print("[+] Sleeping for 60 seconds...\n")

    time.sleep(60)
