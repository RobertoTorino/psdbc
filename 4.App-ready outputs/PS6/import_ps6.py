from pathlib import Path
import sqlite3
import pandas as pd

DB_FILE = Path(r"C:\development\Python\psdbc\_database\games.db")
CSV_FILE = Path(r"C:\development\Python\psdbc\4.App-ready outputs\PS6\app_ps6_all_games.csv")

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
      DROP TABLE IF EXISTS PS6;

      CREATE TABLE PS6 (
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

      CREATE INDEX idx_ps6_title_id ON PS6(title_id);
      CREATE INDEX idx_ps6_content_id ON PS6(content_id);
      CREATE INDEX idx_ps6_content_type ON PS6(content_type);
      CREATE INDEX idx_ps6_distribution ON PS6(distribution);
      """)

df.to_sql("PS6", conn, if_exists="append", index=False)

count = cur.execute("SELECT COUNT(*) FROM PS6").fetchone()[0]
print(f"Inserted rows: {count}")

conn.commit()
conn.close()

print("Done.")