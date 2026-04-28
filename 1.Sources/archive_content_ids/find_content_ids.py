import os
from datetime import datetime

# --- Configuration ---
TITLE_ID_FILE = "ids.txt"          # Your 177 remaining Title IDs
MASTER_LIST_FILE = "all_content_ids.txt" # The giant list of Content IDs
date_str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"local_match_results_{date_str}.txt"

def find_best_local_match(title_id, master_content_list):
    """
    Searches the local list for the best Content ID match for a Title ID.
    """
    clean_tid = title_id.strip()

    # We want to find IDs that contain our Title ID (e.g., NPEA00119)
    # but aren't fluff (DLC, AVA, etc.)
    potential_matches = []
    skip_list = ['AVA', 'THEME', 'DLC', 'PATCH', 'AVATAR']

    for cid in master_content_list:
        # Check if the Title ID is inside the Content ID
        if clean_tid in cid:
            # Apply our 'fluff' filter
            if not any(word in cid.upper() for word in skip_list):
                potential_matches.append(cid)

    if not potential_matches:
        return "No Match Found in Local List"

    # Prioritization:
    # Often, base games end with _00-something.
    # If we find one that has the Title ID and doesn't have 'EXT' or 'BUNDLE', it's likely the base.
    for match in potential_matches:
        if "_00-" in match:
            return match

    # If no '_00-' specific match, return the first valid one found
    return potential_matches[0]

def main():
    # 1. Load the Title IDs we still need
    if not os.path.exists(TITLE_ID_FILE):
        print(f"Error: {TITLE_ID_FILE} not found.")
        return

    with open(TITLE_ID_FILE, "r") as f:
        title_ids = [line.strip() for line in f if line.strip()]

    # 2. Load the Master Content ID list into memory for speed
    if not os.path.exists(MASTER_LIST_FILE):
        print(f"Error: {MASTER_LIST_FILE} not found.")
        return

    print("Loading master content list into memory...")
    with open(MASTER_LIST_FILE, "r") as f:
        master_content_list = [line.strip() for line in f if line.strip()]

    print(f"Searching for {len(title_ids)} Title IDs across {len(master_content_list)} entries...")

    # 3. Perform the search
    results = []
    for tid in title_ids:
        match = find_best_local_match(tid, master_content_list)
        results.append((tid, match))
        print(f"Checked: {tid} -> {match}")

    # 4. Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as out_file:
        out_file.write(f"Local Master List Match Report - {datetime.now()}\n\n")
        for tid, cid in results:
            out_file.write(f"{tid}: {cid}\n")

    print(f"\nDone! Local matches saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()