import psycopg2


def score_sql_query(query: str) -> float:
    risky_keywords = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "GRANT",
        "UNION",
        "--",
        " OR 1=1"
    ]

    query_upper = query.upper()

    score = 0.0

    for keyword in risky_keywords:
        if keyword in query_upper:
            score += 0.20

    return min(score, 1.0)


conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()

cur.execute("""
SELECT id,
       username,
       database_name,
       query_text
FROM sql_security_logs
ORDER BY id;
""")

rows = cur.fetchall()

for row in rows:

    log_id = row[0]
    username = row[1]
    database_name = row[2]
    query_text = row[3]

    risk_score = score_sql_query(query_text)

    label = "normal"

    if risk_score >= 0.8:
        label = "critical"

    elif risk_score >= 0.4:
        label = "suspicious"

    print("=" * 80)

    print(f"LOG ID        : {log_id}")
    print(f"USERNAME      : {username}")
    print(f"DATABASE      : {database_name}")
    print(f"QUERY         : {query_text}")
    print(f"RISK SCORE    : {risk_score}")
    print(f"CLASSIFICATION: {label}")

print("=" * 80)

cur.close()
conn.close()
