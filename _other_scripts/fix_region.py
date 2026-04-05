import sqlite3

DB_PATH = "games.db"

def fix_region_values(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    total_fixed = 0

    for table in tables:
        # Check if the table has a Region column
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        if "Region" in columns:
            # Count rows before update
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE Region='ASIA';")
            count = cursor.fetchone()[0]

            if count > 0:
                cursor.execute(f"UPDATE {table} SET Region='AS' WHERE Region='ASIA';")
                print(f"Updated {count} rows in table '{table}' (ASIA → AS)")
                total_fixed += count

    conn.commit()
    conn.close()

    if total_fixed == 0:
        print("No 'ASIA' values found — nothing to update.")
    else:
        print(f"\n🎉 Done! Updated a total of {total_fixed} rows across all tables.")

if __name__ == "__main__":
    fix_region_values(DB_PATH)
