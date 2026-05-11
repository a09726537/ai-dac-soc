import subprocess
import sys

steps = [
    ("Import CSV SQL logs", "src/database/import_sql_logs_csv.py"),
    ("Update rule-based risk scores", "src/anomaly_detection/update_risk_scores.py"),
    ("Store autoencoder ML results", "src/anomaly_detection/store_autoencoder_results.py"),
    ("Store anomaly explanations", "src/rag/store_anomaly_explanations.py"),
    ("Evaluate autoencoder results", "src/anomaly_detection/evaluate_autoencoder.py"),
]

for name, script in steps:
    print("=" * 80)
    print("RUNNING:", name)
    print("SCRIPT :", script)
    print("=" * 80)

    result = subprocess.run([sys.executable, script])

    if result.returncode != 0:
        print("FAILED:", name)
        sys.exit(result.returncode)

print("=" * 80)
print("AI-DAC PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 80)
