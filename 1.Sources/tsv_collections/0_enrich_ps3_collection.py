import os
import pandas as pd

INPUT_FILE = "PS3_GAMES.tsv"
OUTPUT_DIR = "../../collection_split"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def detect_distribution(icon0_path: str) -> str:
    if not isinstance(icon0_path, str):
        return "UNKNOWN"

    path = icon0_path.lower().replace("\\", "/")

    if "dev_hdd0/game/" in path:
        return "PSN"

    return "DISC"


print("Reading collection...")

# Read TSV
df = pd.read_csv(INPUT_FILE, sep="\t", dtype=str).fillna("")

# Rename columns to cleaner schema
df = df.rename(columns={
    "GameId": "title_id",
    "Region": "region",
    "GameTitle": "game_title",
    "URL": "url",
    "Eboot": "ebootPath",
    "Icon0": "icon0Path",
    "ParamSfo": "paramSfoPath",
    "Pic1": "pic1Path",
    "Snd0": "snd0Path",
    "Have": "have"
})

# Add enrichment columns
df["platform"] = "PS3"
df["distribution"] = df["icon0Path"].apply(detect_distribution)
df["content_type"] = "BASE_GAME"

# Optional: normalize Have
df["have"] = df["have"].replace({"": "0"})

ensure_dir(OUTPUT_DIR)

# Save enriched master file
master_output = os.path.join(OUTPUT_DIR, "ps3_collection_enriched.csv")
df.to_csv(master_output, index=False)
print(f"Saved {master_output} ({len(df)} rows)")

# Split by distribution
for distribution in sorted(df["distribution"].dropna().unique()):
    df_part = df[df["distribution"] == distribution].copy()

    output_path = os.path.join(
        OUTPUT_DIR,
        f"ps3_collection_{distribution.lower()}.csv"
    )

    df_part.to_csv(output_path, index=False)
    print(f"Saved {output_path} ({len(df_part)} rows)")

print("Done.")