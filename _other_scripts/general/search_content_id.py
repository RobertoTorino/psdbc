import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# --- Configuration ---
INPUT_FILE = "ids.txt"
date_str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"content_ids_{date_str}.txt"
MAX_WORKERS = 5

def find_content_id_advanced(title_id):
    clean_id = title_id.strip()

    # URL Formatting
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
                return clean_id, "No data rows found"

            # Categories we are willing to accept if 'Game' isn't there
            fallback_candidates = []

            # Categories we strictly ignore (Avatars/Themes/DLC)
            # skip_list = ['AVA', 'THEME', 'DLC', 'PATCH', 'AVATAR']

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    item_type = cells[1].get_text(strip=True)
                    content_link = cells[2].find('a', href=True)

                    if not content_link:
                        continue

                    cid = content_link['href'].split('/')[-1]

                    # 1. BEST CASE: Explicitly labeled 'Game'
                    if item_type == "Game":
                        return clean_id, cid

                    # 2. ACCEPTABLE CASES: Soundtrack, Demo, or Unknown
                    if item_type in ["Soundtrack", "Demo", "Wallpaper", "Video", "WebTV", "Unknown"]:
                        # Double check it's not fluff (like an Avatar that got labeled Unknown)
                        #if not any(word in cid.upper() for word in skip_list):
                            # Prioritize IDs that contain the Title ID string
                            if clean_id.replace("/", "") in cid.replace("-", ""):
                                # Put these in a list to pick the best one later
                                fallback_candidates.append((item_type, cid))

            # If we didn't find a 'Game', check our fallbacks
            if fallback_candidates:
                # We can prioritize Soundtracks/Demos over 'Unknown' if we want:
                # For now, we'll just return the first valid one found
                return clean_id, fallback_candidates[0][1]

            return clean_id, "ID not found (Strictly filtered)"

        return clean_id, f"HTTP Error {response.status_code}"
    except Exception:
        return clean_id, "Connection Error"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r") as f:
        title_ids = [line.strip() for line in f if line.strip()]

    print(f"--- Running Ultimate Scraper (Handling Game, Demo, & Soundtrack) ---")
    print("-" * 65)

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {executor.submit(find_content_id_advanced, tid): tid for tid in title_ids}

        for i, future in enumerate(as_completed(future_to_id), 1):
            tid, cid = future.result()
            results.append((tid, cid))
            print(f"[{i}/{len(title_ids)}] {tid} -> {cid}")

    # Maintain original order from ids.txt
    results_dict = dict(results)
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as out_file:
        out_file.write(f"Comprehensive Content ID Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for tid in title_ids:
            cid = results_dict.get(tid, "Not Found")
            out_file.write(f"{tid}: {cid}\n")

    print("-" * 65)
    print(f"Done! Final list saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()