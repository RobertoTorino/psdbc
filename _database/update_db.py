import sqlite3
import csv

# Path to your SQLite database
db_path = 'games.db'
# Path to your TSV file
tsv_path = '../1.Sources/tsv_collections/PS3_GAMES.tsv'
# Name of your table
table_name = 'games'

# Step 1: Read the TSV file into a dictionary
url_dict = {}
with open(tsv_path, newline='', encoding='utf-8') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    for row in reader:
        game_id = row['Title ID']  # Adjust if the column name is different
        url = row['URL']          # Adjust if the column name is different
        url_dict[game_id] = url

# Step 2: Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 3: Update Link column
for game_id, url in url_dict.items():
    cursor.execute(f"""
        UPDATE {table_name}
        SET Link = ?
        WHERE GameId = ?
    """, (url, game_id))

# Commit changes and close connection
conn.commit()
conn.close()

print("Link column updated successfully.")
