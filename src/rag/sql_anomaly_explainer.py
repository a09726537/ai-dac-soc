def explain_sql_anomaly(query: str, risk_score: float, ml_anomaly: bool) -> str:
    query_upper = query.upper()

    explanations = []

    if "DROP" in query_upper:
        explanations.append("The query contains DROP, which may delete database objects.")

    if "DELETE" in query_upper:
        explanations.append("The query contains DELETE, which may remove records.")

    if " OR 1=1" in query_upper or "--" in query_upper:
        explanations.append("The query contains patterns commonly associated with SQL injection.")

    if "UNION" in query_upper:
        explanations.append("The query contains UNION, which may be used in data extraction attacks.")

    if ml_anomaly:
        explanations.append("The autoencoder detected an abnormal reconstruction pattern.")

    if risk_score >= 0.6:
        severity = "critical"
    elif risk_score >= 0.3 or ml_anomaly:
        severity = "suspicious"
    else:
        severity = "normal"

    if not explanations:
        explanations.append("No high-risk SQL pattern was detected.")

    return f"Severity: {severity}. " + " ".join(explanations)


examples = [
    ("SELECT * FROM users;", 0.0, False),
    ("DROP TABLE customers;", 0.2, False),
    ("SELECT * FROM users WHERE username='admin' OR 1=1 --;", 0.4, True),
]

for query, score, ml_flag in examples:
    print("=" * 80)
    print("QUERY:", query)
    print(explain_sql_anomaly(query, score, ml_flag))
