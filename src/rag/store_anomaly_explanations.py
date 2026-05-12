import psycopg2


def explain_sql_anomaly(query: str, risk_score: float, ml_anomaly: bool):
    query_upper = query.upper()
    explanations = []

    if "DROP" in query_upper:
        explanations.append("Contains DROP: may delete database objects.")

    if "DELETE" in query_upper:
        explanations.append("Contains DELETE: may remove records.")

    if " OR 1=1" in query_upper or "--" in query_upper:
        explanations.append("Contains SQL injection-like pattern.")

    if "UNION" in query_upper:
        explanations.append("Contains UNION: may indicate data extraction.")

    if ml_anomaly:
        explanations.append("Autoencoder detected abnormal reconstruction behavior.")

    if risk_score >= 0.6:
        severity = "critical"
    elif risk_score >= 0.3 or ml_anomaly:
        severity = "suspicious"
    else:
        severity = "normal"

    if not explanations:
        explanations.append("No high-risk SQL pattern detected.")

    return severity, " ".join(explanations)


conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS anomaly_explanations (
    id SERIAL PRIMARY KEY,
    log_id INTEGER,
    query_text TEXT,
    severity TEXT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Prevent duplicate explanation accumulation between monitoring cycles
cur.execute("TRUNCATE TABLE anomaly_explanations RESTART IDENTITY;")

cur.execute("""
SELECT
    s.id,
    s.query_text,
    COALESCE(s.risk_score, 0),
    COALESCE(m.ml_anomaly, false)
FROM sql_security_logs s
LEFT JOIN ml_anomaly_results m
ON s.query_text = m.query_text
ORDER BY s.id;
""")

for log_id, query_text, risk_score, ml_anomaly in cur.fetchall():
    severity, explanation = explain_sql_anomaly(
        query_text,
        float(risk_score),
        bool(ml_anomaly)
    )

    cur.execute("""
        INSERT INTO anomaly_explanations (
            log_id,
            query_text,
            severity,
            explanation
        )
        VALUES (%s, %s, %s, %s);
    """, (
        log_id,
        query_text,
        severity,
        explanation
    ))

conn.commit()

cur.execute("""
SELECT
    log_id,
    severity,
    explanation
FROM anomaly_explanations
ORDER BY id ASC;
""")

for row in cur.fetchall():
    print(row)

cur.close()
conn.close()

print("Anomaly explanations refreshed successfully.")
