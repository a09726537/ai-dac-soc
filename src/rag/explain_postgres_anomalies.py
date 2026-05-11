import psycopg2

def explain_sql_anomaly(query: str, risk_score: float, ml_anomaly: bool) -> str:
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

    return f"Severity: {severity}. " + " ".join(explanations)


conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()

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
    explanation = explain_sql_anomaly(query_text, float(risk_score), bool(ml_anomaly))

    print("=" * 80)
    print("LOG ID:", log_id)
    print("QUERY:", query_text)
    print("EXPLANATION:", explanation)

cur.close()
conn.close()
