def score_sql_query(query: str) -> float:
    risky_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "UNION", "--", " OR 1=1"]

    query_upper = query.upper()
    score = 0.0

    for keyword in risky_keywords:
        if keyword in query_upper:
            score += 0.20

    return min(score, 1.0)


queries = [
    "SELECT * FROM users;",
    "DROP TABLE customers;",
    "SELECT * FROM users WHERE name = 'admin' OR 1=1 --",
]

for q in queries:
    print(q, "=> risk_score:", score_sql_query(q))
