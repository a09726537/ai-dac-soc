import asyncio
import json
import psycopg2
import websockets


clients = set()

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "aidac",
    "user": "william",
    "password": "Oracle2020"
}


async def register(websocket):
    clients.add(websocket)
    print(f"[+] Client connected: {len(clients)}")


async def unregister(websocket):
    clients.discard(websocket)
    print(f"[-] Client disconnected: {len(clients)}")


async def broadcast_alert(alert):
    if not clients:
        return

    message = json.dumps(alert)
    disconnected_clients = []

    for client in clients:
        try:
            await client.send(message)
        except Exception:
            disconnected_clients.append(client)

    for client in disconnected_clients:
        clients.discard(client)


def normalize_suricata(row):
    severity = "critical" if row[4] <= 2 else "suspicious"

    return {
        "id": f"suricata-{row[0]}",
        "log_id": row[0],
        "query": f"{row[1]} | {row[2]} → {row[3]}",
        "severity": severity,
        "explanation": f"Suricata IDS detected network threat: {row[1]}",
        "created_at": str(row[5])
    }


def normalize_anomaly(row):
    return {
        "id": f"anomaly-{row[0]}",
        "log_id": row[1],
        "query": row[2],
        "severity": row[3],
        "explanation": row[4],
        "created_at": str(row[5])
    }


async def send_alerts():
    last_anomaly_id = 0
    last_suricata_id = 0

    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    log_id,
                    query_text,
                    severity,
                    explanation,
                    created_at
                FROM anomaly_explanations
                WHERE id > %s
                  AND severity IN ('suspicious', 'critical')
                ORDER BY id ASC;
            """, (last_anomaly_id,))

            anomaly_rows = cur.fetchall()

            for row in anomaly_rows:
                alert = normalize_anomaly(row)
                last_anomaly_id = row[0]

                await broadcast_alert(alert)

                print("=" * 80)
                print("AI-DAC REAL-TIME ALERT")
                print(json.dumps(alert, indent=2))
                print("=" * 80)

            cur.execute("""
                SELECT
                    id,
                    alert_signature,
                    src_ip,
                    dest_ip,
                    alert_severity,
                    created_at
                FROM suricata_events
                WHERE id > %s
                ORDER BY id ASC;
            """, (last_suricata_id,))

            suricata_rows = cur.fetchall()

            for row in suricata_rows:
                alert = normalize_suricata(row)
                last_suricata_id = row[0]

                await broadcast_alert(alert)

                print("=" * 80)
                print("SURICATA REAL-TIME ALERT")
                print(json.dumps(alert, indent=2))
                print("=" * 80)

            cur.close()
            conn.close()

        except Exception as e:
            print("[ERROR]", e)

        await asyncio.sleep(5)


async def send_initial_history(websocket):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            log_id,
            query_text,
            severity,
            explanation,
            created_at
        FROM anomaly_explanations
        WHERE severity IN ('suspicious', 'critical')
        ORDER BY id DESC
        LIMIT 25;
    """)

    anomaly_rows = cur.fetchall()

    history = []

    for row in anomaly_rows:
        history.append(normalize_anomaly(row))

    cur.execute("""
        SELECT
            id,
            alert_signature,
            src_ip,
            dest_ip,
            alert_severity,
            created_at
        FROM suricata_events
        ORDER BY id DESC
        LIMIT 25;
    """)

    suricata_rows = cur.fetchall()

    for row in suricata_rows:
        history.append(normalize_suricata(row))

    history.sort(key=lambda x: x["created_at"])

    for alert in history:
        await websocket.send(json.dumps(alert))

    cur.close()
    conn.close()


async def handler(websocket):
    await register(websocket)

    try:
        await send_initial_history(websocket)
        await websocket.wait_closed()

    finally:
        await unregister(websocket)


async def main():
    print("=" * 80)
    print("AI-DAC WebSocket Alert Server Running")
    print("Streaming: anomaly_explanations + suricata_events")
    print("URL: ws://0.0.0.0:8765")
    print("=" * 80)

    async with websockets.serve(handler, "0.0.0.0", 8765):
        await send_alerts()


if __name__ == "__main__":
    asyncio.run(main())
