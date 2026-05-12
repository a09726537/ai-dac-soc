import psycopg2
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(
    title="AI-DAC API",
    version="1.0",
    description="AI-Driven Anomaly Detection and Control API"
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
def home():
    return {
        "message": "AI-DAC API is running",
        "version": "1.0",
        "status": "operational"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI-DAC API"
    }


@app.get("/logs")
def get_logs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, database_name, query_text, risk_score, anomaly_label
        FROM sql_security_logs
        ORDER BY id DESC
        LIMIT 50;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return JSONResponse(content=[
        {
            "id": r[0],
            "username": r[1],
            "database": r[2],
            "query": r[3],
            "risk_score": float(r[4]) if r[4] is not None else 0.0,
            "label": r[5]
        }
        for r in rows
    ])


@app.get("/anomalies")
def get_anomalies():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT log_id, query_text, severity, explanation, created_at
        FROM anomaly_explanations
        WHERE severity IN ('suspicious', 'critical')
        ORDER BY created_at DESC
        LIMIT 50;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return JSONResponse(content=[
        {
            "log_id": r[0],
            "query": r[1],
            "severity": r[2],
            "explanation": r[3],
            "created_at": str(r[4])
        }
        for r in rows
    ])


@app.get("/shap")
def get_shap_explanations():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, query_text, top_features, created_at
        FROM shap_explanations
        ORDER BY id DESC
        LIMIT 50;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return JSONResponse(content=[
        {
            "id": r[0],
            "query": r[1],
            "top_features": r[2],
            "created_at": str(r[3])
        }
        for r in rows
    ])


@app.get("/metrics")
def get_metrics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sql_security_logs;")
    total_logs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'normal';")
    normal = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'suspicious';")
    suspicious = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'critical';")
    critical = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM ml_anomaly_results WHERE ml_anomaly = true;")
    ml_anomalies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM shap_explanations;")
    shap_explanations = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_logs": total_logs,
        "normal": normal,
        "suspicious": suspicious,
        "critical": critical,
        "ml_anomalies": ml_anomalies,
        "shap_explanations": shap_explanations
    }


@app.get("/prometheus", response_class=PlainTextResponse)
def prometheus_metrics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sql_security_logs;")
    total_logs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'normal';")
    normal = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'suspicious';")
    suspicious = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM anomaly_explanations WHERE severity = 'critical';")
    critical = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM ml_anomaly_results WHERE ml_anomaly = true;")
    ml_anomalies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM shap_explanations;")
    shap_explanations = cur.fetchone()[0]

    cur.close()
    conn.close()

    return f"""
# HELP aidac_total_logs Total number of SQL logs processed
# TYPE aidac_total_logs gauge
aidac_total_logs {total_logs}

# HELP aidac_normal_logs Total number of normal SQL events
# TYPE aidac_normal_logs gauge
aidac_normal_logs {normal}

# HELP aidac_suspicious_logs Total number of suspicious SQL events
# TYPE aidac_suspicious_logs gauge
aidac_suspicious_logs {suspicious}

# HELP aidac_critical_logs Total number of critical SQL events
# TYPE aidac_critical_logs gauge
aidac_critical_logs {critical}

# HELP aidac_ml_anomalies Total number of ML-detected anomalies
# TYPE aidac_ml_anomalies gauge
aidac_ml_anomalies {ml_anomalies}

# HELP aidac_shap_explanations Total number of SHAP explanations
# TYPE aidac_shap_explanations gauge
aidac_shap_explanations {shap_explanations}
""".strip()
