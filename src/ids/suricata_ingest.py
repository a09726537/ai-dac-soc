import json
import time
import psycopg2
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "aidac",
    "user": "william",
    "password": "Oracle2020"
}

EVE_FILE = Path.home() / "suricata/logs/eve.json"


def insert_event(conn, event):
    alert = event.get("alert", {})

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO suricata_events (
                event_time,
                event_type,
                src_ip,
                src_port,
                dest_ip,
                dest_port,
                proto,
                alert_signature,
                alert_category,
                alert_severity,
                raw_event
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                event.get("timestamp"),
                event.get("event_type"),
                event.get("src_ip"),
                event.get("src_port"),
                event.get("dest_ip"),
                event.get("dest_port"),
                event.get("proto"),
                alert.get("signature"),
                alert.get("category"),
                alert.get("severity"),
                json.dumps(event),
            ),
        )

    conn.commit()


def follow_file(path):
    with open(path, "r") as file:
        file.seek(0, 2)

        while True:
            line = file.readline()

            if not line:
                time.sleep(1)
                continue

            yield line


def main():
    print("[AI-DAC] Suricata ingestion started")
    print(f"[AI-DAC] Watching {EVE_FILE}")

    conn = psycopg2.connect(**DB_CONFIG)

    for line in follow_file(EVE_FILE):
        try:
            event = json.loads(line)

            if event.get("event_type") == "alert":
                insert_event(conn, event)

                print(
                    "[SURICATA ALERT]",
                    event.get("alert", {}).get("signature")
                )

        except Exception as e:
            print("[ERROR]", e)


if __name__ == "__main__":
    main()
