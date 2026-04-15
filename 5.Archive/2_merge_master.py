import pandas as pd

COLLECTION_FILE = "../3.Working pipeline for one platform/PS3/ps3_master_clean_aligned.csv"
DUMP_FILE = "../2.Normalized external data/psnstuff_dump/ps3_aligned.csv"
OUTPUT_FILE = "ps3_master_combined.csv"


COMMON_COLUMNS = [
    "title_id",
    "game_title",
    "platform_source",
    "region",
    "url",
    "content_id",
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


def norm(series):
    return series.fillna("").astype(str).str.strip()


def prefer(left, right):
    return left.where(left != "", right)


print("Reading files...")

col_df = pd.read_csv(COLLECTION_FILE, dtype=str).fillna("")
dump_df = pd.read_csv(DUMP_FILE, dtype=str).fillna("")

# Normalize
for df in [col_df, dump_df]:
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = norm(df[c])
    df["title_id"] = df["title_id"].str.upper().str.replace("-", "", regex=False).str.strip()

print(f"Collection rows: {len(col_df)}")
print(f"Dump rows: {len(dump_df)}")

# Rename dump columns to avoid collision
dump_df = dump_df.rename(columns={
    col: f"{col}_dump" for col in COMMON_COLUMNS if col != "title_id"
})

# Reduce dump to ONE row per title_id (critical!)
dump_df = (
    dump_df
    .sort_values(["title_id", "content_id_dump"], kind="stable")
    .drop_duplicates(subset=["title_id"])
)

print(f"Dump rows after dedupe: {len(dump_df)}")

# Merge
merged = col_df.merge(dump_df, on="title_id", how="left")

print(f"Merged rows: {len(merged)}")

# Resolve columns
for col in COMMON_COLUMNS:
    if col == "title_id":
        continue

    col_dump = f"{col}_dump"

    if col_dump not in merged.columns:
        merged[col_dump] = ""

    merged[col] = prefer(merged[col], merged[col_dump])

# Recompute flags
merged["has_content_id"] = merged["content_id"].ne("").map({True: "YES", False: "NO"})

merged["matched"] = merged["has_content_id"]

merged["distribution_match"] = (
        (merged["distribution"] != "") &
        (merged["matched_distribution"] != "") &
        (merged["distribution"] == merged["matched_distribution"])
).map({True: "YES", False: "NO"})

# Final clean
merged = merged[COMMON_COLUMNS].drop_duplicates()

merged = merged.sort_values(["title_id", "content_id"], kind="stable")

merged.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(merged)} rows)")