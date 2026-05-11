import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="aidac",
    user="william",
    password="Oracle2020"
)

tables = {
    "SQL Security Logs": "sql_security_logs",
    "ML Anomaly Results": "ml_anomaly_results",
    "Anomaly Explanations": "anomaly_explanations"
}

print("=" * 80)
print("AI-DAC SUMMARY DASHBOARD")
print("=" * 80)

for title, table in tables.items():
    df = pd.read_sql(f"SELECT * FROM {table};", conn)

    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)
    print("Records:", len(df))

    if "anomaly_label" in df.columns:
        print(df["anomaly_label"].value_counts())

    if "ml_anomaly" in df.columns:
        print(df["ml_anomaly"].value_counts())

    if "severity" in df.columns:
        print(df["severity"].value_counts())

conn.close()
