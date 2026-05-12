import subprocess
import sys
import time


steps = [

    (
        "Import live PostgreSQL logs",
        "src/database/import_postgres_live_logs.py"
    ),

    (
        "Update rule-based risk scores",
        "src/anomaly_detection/update_risk_scores.py"
    ),

    (
        "Store autoencoder ML results",
        "src/anomaly_detection/store_autoencoder_results.py"
    ),

    (
        "Store anomaly explanations",
        "src/rag/store_anomaly_explanations.py"
    ),

    (
        "Evaluate autoencoder results",
        "src/anomaly_detection/evaluate_autoencoder.py"
    ),
]


print("=" * 80)
print("AI-DAC PIPELINE STARTED")
print("=" * 80)


for step_number, (name, script) in enumerate(steps, start=1):

    print("\n" + "=" * 80)

    print(f"STEP {step_number}/{len(steps)}")

    print("RUNNING:", name)

    print("SCRIPT :", script)

    print("=" * 80)

    start_time = time.time()

    try:

        result = subprocess.run(
            [sys.executable, script],
            check=False
        )

        duration = round(time.time() - start_time, 2)

        if result.returncode != 0:

            print("\n[FAILED]", name)

            print("RETURN CODE:", result.returncode)

            sys.exit(result.returncode)

        print(f"\n[SUCCESS] {name}")

        print(f"DURATION : {duration} seconds")

    except Exception as e:

        print("\n[EXCEPTION]", name)

        print(str(e))

        sys.exit(1)


print("\n" + "=" * 80)

print("AI-DAC PIPELINE COMPLETED SUCCESSFULLY")

print("=" * 80)
