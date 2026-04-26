import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- PS5 Configuration ---
INPUT_FILE = "ps5_ids.txt"  # Your dedicated PS5 Title ID list
date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
OUTPUT_FILE = f"ps5_all_contents_extracted_{date_str}.csv"
MAX_WORKERS = 4

def get_all_ps5_content(title_id):
    """
    Scrapes the SerialStation table and returns a list of ALL (Type, Content ID) pairs.
    """
    clean_id = title_id.strip()

    # URL Formatting for PS5 (e.g., PPSA01735 -> PPSA/01735)
    if len(clean_id) > 4 and "/" not in clean_id:
        formatted_id = f"{clean_id[:4]}/{clean_id[4:]}"
    else:
        formatted_id = clean_id

    url = f"https://serialstation.com/titles/{formatted_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            rows = soup.select('tbody tr')
            if not rows:
                return clean_id, [] # Empty list means no rows found

            extracted_items = []

            for row in rows:
                cells = row.find_all('td')

                # Verify the row has Name, Type, and Content ID columns
                if len(cells) >= 3:
                    item_type = cells[1].get_text(strip=True)
                    content_link = cells[2].find('a', href=True)

                    if content_link and '/contents/ids/' in content_link['href']:
                        cid = content_link['href'].split('/')[-1]

                        # Store as a tuple (Type, Content_ID)
                        extracted_items.append((item_type, cid))

            return clean_id, extracted_items

        return clean_id, [(f"Error: {response.status_code}", "N/A")]
    except Exception as e:
        return clean_id, [("Connection Error", str(e))]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found in the project directory.")
        print("Please ensure your PS5 IDs are saved in this file.")
        return

    with open(INPUT_FILE, "r") as f:
        ps5_ids = [line.strip() for line in f if line.strip()]

    print(f"--- PS5 Full Content ID Extractor ---")
    print(f"Processing {len(ps5_ids)} PS5 Title IDs...")

    # Store results as a flat list of rows for the CSV
    all_csv_rows = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {executor.submit(get_all_ps5_content, tid): tid for tid in ps5_ids}

        for i, future in enumerate(as_completed(future_to_id), 1):
            tid, contents = future.result()

            if not contents:
                all_csv_rows.append([tid, "No Data Found", "N/A"])
            else:
                # Add a row for every single item found on the page
                for item_type, cid in contents:
                    all_csv_rows.append([tid, item_type, cid])

            print(f"[{i}/{len(ps5_ids)}] {tid} -> Found {len(contents)} items")

    # Sort the rows alphabetically by Title ID for a clean spreadsheet
    all_csv_rows.sort(key=lambda x: x[0])

    print("\nSaving PS5 data to CSV...")

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(["Title ID", "Content Type", "Content ID"])
        # Write all the collected data
        writer.writerows(all_csv_rows)

    print(f"Success! Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()