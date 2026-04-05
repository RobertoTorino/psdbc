import glob

files = glob.glob("regions/*.txt")

content_ids = set()

for file in files:
    print(f"Reading {file}...")
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            cid = line.strip()
            if cid:
                content_ids.add(cid)

print(f"Total unique content IDs: {len(content_ids)}")

# WRITE OUTPUT
with open("all_content_ids.txt", "w", encoding="utf-8") as out:
    for cid in sorted(content_ids):
        out.write(cid + "\n")

print("Saved to all_content_ids.txt")