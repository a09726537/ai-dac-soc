import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone()[0])

cur.close()
conn.close()
