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


async def send_alerts():
    last_id = 0
    initialized = False

    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            if not initialized:
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
                    ORDER BY id ASC
                    LIMIT 50;
                """)

                initialized = True

            else:
                cur.execute("SELECT COALESCE(MAX(id), 0) FROM anomaly_explanations;")
                max_id = cur.fetchone()[0]

                if max_id < last_id:
                    print("[INFO] anomaly_explanations was refreshed. Resetting last_id.")
                    last_id = 0

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
                """, (last_id,))

            rows = cur.fetchall()

            for row in rows:
                alert = {
                    "id": row[0],
                    "log_id": row[1],
                    "query": row[2],
                    "severity": row[3],
                    "explanation": row[4],
                    "created_at": str(row[5])
                }

                last_id = row[0]

                await broadcast_alert(alert)

                print("=" * 80)
                print("AI-DAC REAL-TIME ALERT")
                print(json.dumps(alert, indent=2))
                print("=" * 80)

            cur.close()
            conn.close()

        except Exception as e:
            print("[ERROR]", e)

        await asyncio.sleep(5)


async def handler(websocket):
    await register(websocket)

    try:
        await websocket.wait_closed()
    finally:
        await unregister(websocket)


async def main():
    print("=" * 80)
    print("AI-DAC WebSocket Alert Server Running")
    print("URL: ws://0.0.0.0:8765")
    print("=" * 80)

    async with websockets.serve(handler, "0.0.0.0", 8765):
        await send_alerts()


if __name__ == "__main__":
    asyncio.run(main())
