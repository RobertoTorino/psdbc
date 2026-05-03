import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Configuration ---
INPUT_FILE = "ids.txt"
date_str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"results_{date_str}.txt"

# MAX_WORKERS: How many searches to run at once.
# Keep this between 3 and 8 to avoid getting blocked.
MAX_WORKERS = 6

def get_game_info(raw_id):
    clean_id = raw_id.strip()
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
            title_tag = soup.find('h1')
            name = title_tag.get_text(strip=True) if title_tag else "Title not found"
            return clean_id, name
        elif response.status_code == 404:
            return clean_id, "Not Found"
        return clean_id, f"Error: {response.status_code}"
    except Exception as e:
        return clean_id, f"Conn Error: {str(e)}"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, "r") as f:
        ids = [line.strip() for line in f if line.strip()]

    print(f"--- Multi-Threaded Search ({MAX_WORKERS} workers) ---")
    print(f"Processing {len(ids)} IDs...")

    results = []

    # ThreadPoolExecutor manages the threads for us
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks to the executor
        future_to_id = {executor.submit(get_game_info, tid): tid for tid in ids}

        for i, future in enumerate(as_completed(future_to_id), 1):
            tid, name = future.result()
            results.append((tid, name))

            # Print progress to IntelliJ console
            if i % 5 == 0 or i == len(ids):
                print(f"Progress: {i}/{len(ids)} completed.")

    # Sort results to match your original input order
    # (Threads finish at different times, so they come back out of order)
    results_dict = dict(results)

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as out_file:
        out_file.write(f"Multi-threaded Search: {datetime.now()}\n\n")
        for tid in ids:  # Loop through original list to maintain order
            name = results_dict.get(tid, "No data")
            out_file.write(f"{tid}: {name}\n")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
