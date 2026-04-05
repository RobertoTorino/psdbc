import pandas as pd

INPUT_FILE = "ps3_master.csv"
OUTPUT_FILE = "ps3_master_clean.csv"

TARGET_COLUMNS = [
    "titleId",
    "gameTitle",
    "platform_source",
    "region_source",
    "url",
    "contentId",
    "has_content_id",
    "platform",
    "distribution",
    "content_type",
    "unlock_model",
    "unlock_group",
    "matched_platform",
    "matched_distribution",
    "matched_content_type",
    "matched_store",
    "matched_store_region",
    "matched_region",
    "matched",
    "distribution_match",
]

print("Reading master file...")

df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
df.columns = [str(c).strip() for c in df.columns]

print("Source columns:", df.columns.tolist())

# Rename current master columns into aligned names
rename_map = {
    "collection_region": "region_source",
    "collection_distribution": "distribution",
}

existing_renames = {k: v for k, v in rename_map.items() if k in df.columns}
df = df.rename(columns=existing_renames)

# platform_source does not really exist in this file, but add it for schema consistency
if "platform_source" not in df.columns:
    df["platform_source"] = "COLLECTION"

# has_content_id derived from contentId
df["has_content_id"] = df["contentId"].apply(lambda x: "YES" if str(x).strip() else "NO") if "contentId" in df.columns else "NO"

# unlock fields not present in this file, but keep schema aligned
if "unlock_model" not in df.columns:
    df["unlock_model"] = ""
if "unlock_group" not in df.columns:
    df["unlock_group"] = ""

# Drop unwanted columns
columns_to_drop = [
    "have",
    "ebootPath",
    "icon0Path",
    "paramSfoPath",
    "pic1Path",
    "snd0Path",
]

existing_drop = [c for c in columns_to_drop if c in df.columns]
df = df.drop(columns=existing_drop)

# Ensure all target columns exist
for col in TARGET_COLUMNS:
    if col not in df.columns:
        df[col] = ""

# Reorder columns
df = df[TARGET_COLUMNS]

# Normalize some core fields
df["titleId"] = df["titleId"].astype(str).str.upper().str.replace("-", "", regex=False).str.strip()
df["gameTitle"] = df["gameTitle"].astype(str).str.strip()
df["region_source"] = df["region_source"].astype(str).str.strip()
df["url"] = df["url"].astype(str).str.strip()
df["platform"] = df["platform"].astype(str).str.strip()
df["distribution"] = df["distribution"].astype(str).str.strip()
df["content_type"] = df["content_type"].astype(str).str.strip()

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(df)} rows)")
print("Final columns:")
print(df.columns.tolist())