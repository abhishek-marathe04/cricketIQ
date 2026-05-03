"""
Exports three Postgres tables to CSV files in ipl-dataset-2008-to-2025/.

  players            → players-data-updated.csv
  matches            → ipl_matches_data.csv
  ball_by_ball_stats → ball_by_ball_data.csv

Connection defaults match db.js; override via environment variables:
  PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
"""

import os
import time
import psycopg2
import pandas as pd

# --- Connection ---------------------------------------------------------------

DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     int(os.getenv("PG_PORT", "5432")),
    "dbname":   os.getenv("PG_DB",       "cricketiq"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgres_cric"),
}

# --- Export targets -----------------------------------------------------------

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "..", "ipl-dataset-2008-to-2025")

EXPORTS = [
    ("players",            "players-data-updated.csv"),
    ("matches",            "ipl_matches_data.csv"),
    ("ball_by_ball_stats", "ball_by_ball_data.csv"),
]

# ------------------------------------------------------------------------------

def export_table(conn, table: str, dest_path: str) -> int:
    print(f"  Exporting {table!r} ...", end=" ", flush=True)
    t0 = time.time()
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    df.to_csv(dest_path, index=False)
    elapsed = time.time() - t0
    print(f"{len(df):,} rows → {os.path.basename(dest_path)}  ({elapsed:.1f}s)")
    return len(df)


def main():
    print(f"Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']} ...")
    conn = psycopg2.connect(**DB_CONFIG)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_rows = 0
    for table, filename in EXPORTS:
        dest = os.path.join(OUTPUT_DIR, filename)
        total_rows += export_table(conn, table, dest)

    conn.close()
    print(f"\nDone. {total_rows:,} total rows exported to {os.path.abspath(OUTPUT_DIR)}/")


if __name__ == "__main__":
    main()
