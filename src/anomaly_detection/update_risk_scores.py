import psycopg2

def score_sql_query(query: str) -> float:
    risky_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "UNION", "--", " OR 1=1"]
    return min(sum(0.20 for keyword in risky_keywords if keyword in query.upper()), 1.0)

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()

cur.execute("SELECT id, query_text FROM sql_security_logs ORDER BY id;")

for log_id, query_text in cur.fetchall():
    score = score_sql_query(query_text)

    if score >= 0.6:
        label = "critical"
    elif score >= 0.3:
        label = "suspicious"
    else:
        label = "normal"

    cur.execute("""
        UPDATE sql_security_logs
        SET risk_score = %s,
            anomaly_label = %s
        WHERE id = %s;
    """, (score, label, log_id))

conn.commit()

cur.execute("SELECT id, query_text, risk_score, anomaly_label FROM sql_security_logs ORDER BY id;")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
