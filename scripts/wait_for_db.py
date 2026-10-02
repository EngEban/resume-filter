# ============================================================
# scripts/wait_for_db.py
# Block until PostgreSQL is reachable.
# ============================================================
import os
import sys
import time

import psycopg2

MAX_ATTEMPTS = 60
SLEEP_SECONDS = 2


def db_params() -> dict:
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "rf_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "rf_pass"),
        "dbname": os.getenv("POSTGRES_DB", "rf_db"),
    }


def main() -> int:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            conn = psycopg2.connect(**db_params())
            conn.close()
            print(f"PostgreSQL is ready (attempt {attempt}).")
            return 0
        except psycopg2.OperationalError as exc:
            print(f"Waiting for PostgreSQL... ({attempt}/{MAX_ATTEMPTS})")
            time.sleep(SLEEP_SECONDS)

    print("PostgreSQL did not become ready in time.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())