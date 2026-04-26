import os
import csv
import re
from datetime import datetime

# --- Configuration ---
TITLE_ID_FILE = "ids.txt"          # The Title IDs you are looking for
MASTER_CSV_FILE = "ps3_app.csv"    # The CSV containing the 'url' column
date_str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"url_match_results_{date_str}.txt"

def normalize(text):
    """Removes dashes and non-alphanumeric chars for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).upper()

def find_url_in_csv(title_id, csv_rows):
    """
    Searches rows for a Title ID match and returns the 'url' column value.
    """
    norm_tid = normalize(title_id)

    for row in csv_rows:
        # 1. Check if the Title ID is mentioned anywhere in this row
        # We combine all values in the row to perform a broad search
        combined_row_content = normalize(" ".join(row.values()))

        if norm_tid in combined_row_content:
            # 2. Grab the URL from the specific 'url' column
            # We use .get() in case the column is missing for one specific row
            url_value = row.get('url', '').strip()
            if url_value:
                return url_value

    return "URL Not Found"

def main():
    if not os.path.exists(TITLE_ID_FILE) or not os.path.exists(MASTER_CSV_FILE):
        print("Error: Missing input files in project directory.")
        return

    # Load Title IDs
    with open(TITLE_ID_FILE, "r") as f:
        title_ids = [line.strip() for line in f if line.strip()]

    # Load CSV using DictReader to access columns by name
    print(f"Reading {MASTER_CSV_FILE}...")
    csv_data = []
    try:
        with open(MASTER_CSV_FILE, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            # Normalize column names to lowercase to avoid 'URL' vs 'url' issues
            reader.fieldnames = [name.lower() for name in reader.fieldnames]
            for row in reader:
                csv_data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Searching for URLs for {len(title_ids)} Title IDs...")

    # Perform Match
    results = []
    for tid in title_ids:
        found_url = find_url_in_csv(tid, csv_data)
        results.append((tid, found_url))
        print(f"Matched: {tid} -> {found_url[:50]}...") # Print first 50 chars of URL

    # Save Results
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as out_file:
        out_file.write(f"CSV URL Match Report - {datetime.now()}\n\n")
        for tid, url in results:
            out_file.write(f"{tid}: {url}\n")

    print(f"\nDone! URLs saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()