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
    clients.remove(websocket)
    print(f"[-] Client disconnected: {len(clients)}")


async def send_alerts():

    last_id = 0

    while True:

        try:

            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    log_id,
                    severity,
                    explanation,
                    created_at
                FROM anomaly_explanations
                WHERE id > %s
                ORDER BY id ASC
            """, (last_id,))

            rows = cur.fetchall()

            for row in rows:

                alert = {
                    "id": row[0],
                    "log_id": row[1],
                    "severity": row[2],
                    "explanation": row[3],
                    "created_at": str(row[4])
                }

                last_id = row[0]

                if clients:

                    await asyncio.wait([
                        client.send(json.dumps(alert))
                        for client in clients
                    ])

                    print(f"[ALERT] {alert}")

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

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        8765
    )

    print("=" * 80)
    print("AI-DAC WebSocket Alert Server Running")
    print("ws://0.0.0.0:8765")
    print("=" * 80)

    await asyncio.gather(
        server.wait_closed(),
        send_alerts()
    )


asyncio.run(main())
