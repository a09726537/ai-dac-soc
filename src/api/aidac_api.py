import psycopg2
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="AI-DAC API",
    version="1.0",
    description="AI-Driven Anomaly Detection and Control API"
)


# -------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------

def get_connection():

    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="aidac",
        user="william",
        password="Oracle2020"
    )


# -------------------------------------------------------------------
# HOME
# -------------------------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "AI-DAC API is running",
        "version": "1.0",
        "status": "operational"
    }


# -------------------------------------------------------------------
# LOGS
# -------------------------------------------------------------------

@app.get("/logs")
def get_logs():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            username,
            database_name,
            query_text,
            risk_score,
            anomaly_label
        FROM sql_security_logs
        ORDER BY id DESC
        LIMIT 50;
    """)

    rows = cur.fetchall()

    cur.close()

    conn.close()

    results = []

    for r in rows:

        results.append({

            "id": r[0],

            "username": r[1],

            "database": r[2],

            "query": r[3],

            "risk_score": float(r[4]) if r[4] is not None else 0.0,

            "label": r[5]

        })

    return JSONResponse(content=results)


# -------------------------------------------------------------------
# ANOMALIES
# -------------------------------------------------------------------

@app.get("/anomalies")
def get_anomalies():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT
            log_id,
            query_text,
            severity,
            explanation,
            created_at
        FROM anomaly_explanations
        WHERE severity IN ('suspicious', 'critical')
        ORDER BY created_at DESC
        LIMIT 50;
    """)

    rows = cur.fetchall()

    cur.close()

    conn.close()

    results = []

    for r in rows:

        results.append({

            "log_id": r[0],

            "query": r[1],

            "severity": r[2],

            "explanation": r[3],

            "created_at": str(r[4])

        })

    return JSONResponse(content=results)


# -------------------------------------------------------------------
# METRICS
# -------------------------------------------------------------------

@app.get("/metrics")
def get_metrics():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sql_security_logs;")
    total_logs = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM anomaly_explanations
        WHERE severity = 'normal';
    """)
    normal = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM anomaly_explanations
        WHERE severity = 'suspicious';
    """)
    suspicious = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM anomaly_explanations
        WHERE severity = 'critical';
    """)
    critical = cur.fetchone()[0]

    cur.close()

    conn.close()

    return {

        "total_logs": total_logs,

        "normal": normal,

        "suspicious": suspicious,

        "critical": critical

    }


# -------------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------------

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "service": "AI-DAC API"

    }
