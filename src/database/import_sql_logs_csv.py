import csv
import psycopg2


# -------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()


# -------------------------------------------------------------------
# IMPORT CSV LOGS
# -------------------------------------------------------------------

with open("datasets/sql_logs/sample_sql_logs.csv", newline='') as csvfile:

    reader = csv.DictReader(csvfile)

    inserted = 0
    skipped = 0

    for row in reader:

        # -----------------------------------------------------------
        # CHECK DUPLICATES
        # -----------------------------------------------------------

        cur.execute("""
            SELECT COUNT(*)
            FROM sql_security_logs
            WHERE username = %s
              AND database_name = %s
              AND query_text = %s
        """, (
            row["username"],
            row["database_name"],
            row["query_text"]
        ))

        exists = cur.fetchone()[0]

        # -----------------------------------------------------------
        # INSERT ONLY IF NOT EXISTS
        # -----------------------------------------------------------

        if exists == 0:

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

            inserted += 1

        else:

            skipped += 1

            print(
                f"SKIPPED DUPLICATE: "
                f"{row['username']} | {row['query_text']}"
            )


# -------------------------------------------------------------------
# COMMIT
# -------------------------------------------------------------------

conn.commit()


# -------------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------------

print("=" * 80)

print("SQL LOG IMPORT COMPLETED")

print(f"INSERTED RECORDS : {inserted}")

print(f"SKIPPED DUPLICATES: {skipped}")

print("=" * 80)


# -------------------------------------------------------------------
# CLEANUP
# -------------------------------------------------------------------

cur.close()

conn.close()

print("DATABASE CONNECTION CLOSED")
