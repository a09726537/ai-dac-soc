import csv
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()

with open("datasets/sql_logs/sample_sql_logs.csv", newline='') as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        cur.execute("""
            INSERT INTO sql_security_logs(
                username,
                database_name,
                query_text,
                risk_score,
                anomaly_label
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            row["username"],
            row["database_name"],
            row["query_text"],
            0.0,
            "unclassified"
        ))

conn.commit()

print("SQL logs imported successfully.")

cur.close()
conn.close()
