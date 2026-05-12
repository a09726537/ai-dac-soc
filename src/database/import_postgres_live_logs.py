import hashlib
import re
import subprocess
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "aidac",
    "user": "william",
    "password": "Oracle2020"
}


LOG_PATTERN = re.compile(
    r"statement:\s+(.*)",
    re.IGNORECASE
)


conn = psycopg2.connect(**DB_CONFIG)

cur = conn.cursor()


# -------------------------------------------------------------------
# CREATE HASH TABLE
# -------------------------------------------------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS ingested_log_hashes (
    hash TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")


# -------------------------------------------------------------------
# READ POSTGRESQL CONTAINER LOGS
# -------------------------------------------------------------------

try:

    logs = subprocess.check_output(
        ["podman", "logs", "aidac-postgres"],
        text=True,
        errors="ignore"
    )

except subprocess.CalledProcessError as e:

    print("[ERROR] Unable to read PostgreSQL logs")
    print(e)

    cur.close()
    conn.close()

    raise SystemExit(1)


inserted = 0
skipped = 0


# -------------------------------------------------------------------
# PROCESS LOG LINES
# -------------------------------------------------------------------

for line in logs.splitlines():

    match = LOG_PATTERN.search(line)

    if not match:
        continue

    query_text = match.group(1).strip()

    # Ignore empty queries
    if not query_text:
        continue

    # Ignore internal PostgreSQL noise
    if query_text.upper().startswith((
        "BEGIN",
        "COMMIT",
        "ROLLBACK"
    )):
        continue

    # ----------------------------------------------------------------
    # HASH DEDUPLICATION
    # ----------------------------------------------------------------

    log_hash = hashlib.sha256(
        query_text.encode()
    ).hexdigest()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM ingested_log_hashes
        WHERE hash = %s;
        """,
        (log_hash,)
    )

    exists = cur.fetchone()[0]

    if exists > 0:
        skipped += 1
        continue

    # ----------------------------------------------------------------
    # INSERT SECURITY LOG
    # ----------------------------------------------------------------

    cur.execute("""
        INSERT INTO sql_security_logs (
            username,
            database_name,
            query_text,
            risk_score,
            anomaly_label
        )
        VALUES (%s, %s, %s, %s, %s);
    """, (
        "postgres-live",
        "aidac",
        query_text,
        0.0,
        "unclassified"
    ))

    # ----------------------------------------------------------------
    # STORE HASH
    # ----------------------------------------------------------------

    cur.execute("""
        INSERT INTO ingested_log_hashes(hash)
        VALUES (%s);
    """, (
        log_hash,
    ))

    inserted += 1


# -------------------------------------------------------------------
# COMMIT
# -------------------------------------------------------------------

conn.commit()


# -------------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------------

print("=" * 80)

print("POSTGRESQL LIVE LOG INGESTION COMPLETED")

print(f"Inserted : {inserted}")

print(f"Skipped  : {skipped}")

print("=" * 80)


# -------------------------------------------------------------------
# VERIFY INSERTION
# -------------------------------------------------------------------

cur.execute("""
SELECT
    id,
    username,
    query_text,
    risk_score,
    anomaly_label
FROM sql_security_logs
ORDER BY id DESC
LIMIT 20;
""")

rows = cur.fetchall()

for row in rows:
    print(row)


print("=" * 80)


# -------------------------------------------------------------------
# CLEANUP
# -------------------------------------------------------------------

cur.close()

conn.close()

print("POSTGRESQL CONNECTION CLOSED")
