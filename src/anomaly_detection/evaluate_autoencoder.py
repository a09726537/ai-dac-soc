import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

query = """
SELECT query_text, reconstruction_error, threshold, ml_anomaly
FROM ml_anomaly_results
ORDER BY id;
"""

df = pd.read_sql(query, conn)

conn.close()

print("=" * 80)
print("AUTOENCODER EVALUATION SUMMARY")
print("=" * 80)

print("Total records:", len(df))
print("Normal records:", len(df[df["ml_anomaly"] == False]))
print("Anomalies:", len(df[df["ml_anomaly"] == True]))
print("Average reconstruction error:", df["reconstruction_error"].mean())
print("Max reconstruction error:", df["reconstruction_error"].max())
print("Threshold:", df["threshold"].iloc[-1])

print("=" * 80)
print(df)
print("=" * 80)
