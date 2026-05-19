from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.136.132:5173",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="aidac",
        user="william",
        password="Oracle2020"
    )


@app.get("/")
def root():
    return {"status": "AI-DAC API running"}


@app.get("/api/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations;")
    total_alerts = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM anomaly_explanations
        WHERE LOWER(severity) = 'critical';
    """)
    critical = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM anomaly_explanations
        WHERE LOWER(severity) = 'suspicious';
    """)
    suspicious = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_alerts": total_alerts,
        "critical": critical,
        "suspicious": suspicious
    }
