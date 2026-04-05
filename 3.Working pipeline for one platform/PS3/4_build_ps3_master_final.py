import pandas as pd

COLLECTION_FILE = "ps3_master_clean_aligned.csv"
DUMP_FILE = "../../2.Normalized external data/psnstuff_dump/ps3_aligned.csv"
OUTPUT_FILE = "ps3_master_final.csv"


FINAL_COLUMNS = [
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
]


def norm(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    for c in df.columns:
        df[c] = norm(df[c])

    if "titleId" in df.columns:
        df["titleId"] = (
            df["titleId"]
            .str.upper()
            .str.replace("-", "", regex=False)
            .str.strip()
        )

    return df


def prefer(left: pd.Series, right: pd.Series) -> pd.Series:
    left = norm(left)
    right = norm(right)
    return left.where(left != "", right)


print("Reading files...")

collection_df = pd.read_csv(COLLECTION_FILE, dtype=str).fillna("")
dump_df = pd.read_csv(DUMP_FILE, dtype=str).fillna("")

collection_df = normalize_df(collection_df)
dump_df = normalize_df(dump_df)

# Reset enrichment-driven fields on collection side
# Keep collection structural truth, but let dump provide enrichment
collection_df["contentId"] = ""
collection_df["has_content_id"] = "NO"
collection_df["unlock_model"] = ""
collection_df["unlock_group"] = ""

print(f"Collection rows: {len(collection_df)}")
print(f"Dump rows: {len(dump_df)}")

# Keep only collection columns needed for final master
for col in FINAL_COLUMNS:
    if col not in collection_df.columns:
        collection_df[col] = ""

collection_df = collection_df[FINAL_COLUMNS].copy()

# Dump: PS3 + BASE_GAME only
dump_keep = [
    "titleId",
    "gameTitle",
    "url",
    "contentId",
    "unlock_model",
    "unlock_group",
]

for col in dump_keep:
    if col not in dump_df.columns:
        dump_df[col] = ""

dump_df = dump_df[
    (dump_df["platform"] == "PS3") &
    (dump_df["content_type"] == "BASE_GAME")
    ].copy()

dump_df = dump_df[dump_keep].copy()

print(f"PS3 BASE_GAME dump rows: {len(dump_df)}")

# Choose one best dump row per titleId
dump_df["_has_content"] = dump_df["contentId"].ne("").astype(int)
dump_df["_has_title"] = dump_df["gameTitle"].ne("").astype(int)
dump_df["_has_url"] = dump_df["url"].ne("").astype(int)

dump_df = (
    dump_df
    .sort_values(
        ["titleId", "_has_content", "_has_title", "_has_url", "contentId"],
        ascending=[True, False, False, False, True],
        kind="stable"
    )
    .drop_duplicates(subset=["titleId"], keep="first")
    .drop(columns=["_has_content", "_has_title", "_has_url"])
)

print(f"PS3 BASE_GAME dump rows after dedupe: {len(dump_df)}")

# Rename dump columns for controlled merge
dump_df = dump_df.rename(columns={
    "gameTitle": "dump_gameTitle",
    "url": "dump_url",
    "contentId": "dump_contentId",
    "unlock_model": "dump_unlock_model",
    "unlock_group": "dump_unlock_group",
})

# Merge
merged = collection_df.merge(dump_df, on="titleId", how="left")

print(f"Merged rows: {len(merged)}")

# Fill only allowed enrichment fields
merged["gameTitle"] = prefer(merged["gameTitle"], merged["dump_gameTitle"])
merged["url"] = prefer(merged["url"], merged["dump_url"])
merged["contentId"] = prefer(merged["contentId"], merged["dump_contentId"])
merged["unlock_model"] = prefer(merged["unlock_model"], merged["dump_unlock_model"])
merged["unlock_group"] = prefer(merged["unlock_group"], merged["dump_unlock_group"])

# Recompute has_content_id
merged["has_content_id"] = merged["contentId"].ne("").map({True: "YES", False: "NO"})

# Final schema only
for col in FINAL_COLUMNS:
    if col not in merged.columns:
        merged[col] = ""

final_df = merged[FINAL_COLUMNS].copy()

# Drop exact duplicates only
final_df = final_df.drop_duplicates()

# Stable sort
final_df = final_df.sort_values(["titleId", "contentId"], kind="stable")

final_df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(final_df)} rows)")
print("\nhas_content_id summary:")
print(final_df["has_content_id"].value_counts(dropna=False))

print("\ndistribution summary:")
print(final_df["distribution"].value_counts(dropna=False))