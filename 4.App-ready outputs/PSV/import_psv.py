from pathlib import Path
import sqlite3
import pandas as pd

DB_FILE = Path(r"C:\development\Python\psdbc\_database\games.db")
CSV_FILE = Path(r"C:\development\Python\psdbc\4.App-ready outputs\PSV\app_psv_all_games.csv")

FINAL_COLUMNS = [
    "title_id",
    "game_title",
    "region",
    "version",
    "url",
    "content_id",
    "platform",
    "distribution",
    "content_type",
]

print(f"Reading CSV: {CSV_FILE}")
df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

# Keep only final columns
for col in FINAL_COLUMNS:
    if col not in df.columns:
        df[col] = ""

df = df[FINAL_COLUMNS].copy()

print(f"Rows to import: {len(df)}")

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.executescript("""
                  DROP TABLE IF EXISTS PSV;

                  CREATE TABLE PSV (
                     title_id TEXT,
                     game_title TEXT,
                     region TEXT,
                     version TEXT,
                     url TEXT,
                     content_id TEXT,
                     platform TEXT,
                     distribution TEXT,
                     content_type TEXT
                  );

                  CREATE INDEX idx_psv_title_id ON PSV(title_id);
                  CREATE INDEX idx_psv_content_id ON PSV(content_id);
                  CREATE INDEX idx_psv_content_type ON PSV(content_type);
                  CREATE INDEX idx_psv_distribution ON PSV(distribution);
                  """)

df.to_sql("PSV", conn, if_exists="append", index=False)

count = cur.execute("SELECT COUNT(*) FROM PSV").fetchone()[0]
print(f"Inserted rows: {count}")

conn.commit()
conn.close()

print("Done.")