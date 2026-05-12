import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

query = """
SELECT
    id,
    query_text,
    reconstruction_error,
    threshold,
    ml_anomaly
FROM ml_anomaly_results
ORDER BY id;
"""

df = pd.read_sql(query, conn)

conn.close()

# -------------------------------------------------------------------
# DISPLAY DATA
# -------------------------------------------------------------------

print(df)

# -------------------------------------------------------------------
# PLOT
# -------------------------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    df["id"],
    df["reconstruction_error"],
    marker='o',
    label='Reconstruction Error'
)

plt.axhline(
    y=df["threshold"].iloc[-1],
    linestyle='--',
    label='Threshold'
)

# Highlight anomalies

anomalies = df[df["ml_anomaly"] == True]

plt.scatter(
    anomalies["id"],
    anomalies["reconstruction_error"],
    s=120,
    marker='x',
    label='Detected Anomalies'
)

plt.title("AI-DAC Autoencoder SQL Anomaly Detection")

plt.xlabel("Log ID")

plt.ylabel("Reconstruction Error")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig("results/autoencoder_anomaly_plot.png")

print("=" * 80)
print("PLOT SAVED:")
print("results/autoencoder_anomaly_plot.png")
print("=" * 80)

plt.show()
