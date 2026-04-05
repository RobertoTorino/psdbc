import pandas as pd

COLLECTION_FILE = "ps3_master_clean_aligned.csv"
DUMP_FILE = "../../2.Normalized external data/psnstuff_dump/ps3_aligned.csv"
OUTPUT_FILE = "ps3_master_combined_debug_clean.csv"


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

col_df = pd.read_csv(COLLECTION_FILE, dtype=str).fillna("")
dump_df = pd.read_csv(DUMP_FILE, dtype=str).fillna("")

col_df = normalize_df(col_df)
dump_df = normalize_df(dump_df)

# Keep only the collection fields we actually care about
collection_keep = [
    "titleId",
    "gameTitle",
    "region_source",
    "url",
    "platform",
    "distribution",
    "content_type",
]

for col in collection_keep:
    if col not in col_df.columns:
        col_df[col] = ""

col_df = col_df[collection_keep].copy()

# Keep only the dump fields we actually care about
dump_keep = [
    "titleId",
    "gameTitle",
    "region_source",
    "url",
    "contentId",
    "platform",
    "distribution",
    "content_type",
    "unlock_model",
    "unlock_group",
]

for col in dump_keep:
    if col not in dump_df.columns:
        dump_df[col] = ""

dump_df = dump_df[dump_keep].copy()

# PS3 only
dump_df = dump_df[dump_df["platform"] == "PS3"].copy()

# BASE_GAME only for enriching base-game collection
dump_df = dump_df[dump_df["content_type"] == "BASE_GAME"].copy()

print(f"Collection rows: {len(col_df)}")
print(f"PS3-only BASE_GAME dump rows: {len(dump_df)}")

# Rename columns side-by-side
col_df = col_df.rename(columns={c: f"col_{c}" for c in col_df.columns if c != "titleId"})
dump_df = dump_df.rename(columns={c: f"dump_{c}" for c in dump_df.columns if c != "titleId"})

# Choose one best dump row per titleId for inspection
for c in ["dump_contentId", "dump_content_type", "dump_gameTitle", "dump_url"]:
    if c not in dump_df.columns:
        dump_df[c] = ""

dump_df["_has_content"] = dump_df["dump_contentId"].ne("").astype(int)
dump_df["_is_base_game"] = dump_df["dump_content_type"].eq("BASE_GAME").astype(int)
dump_df["_has_title"] = dump_df["dump_gameTitle"].ne("").astype(int)
dump_df["_has_url"] = dump_df["dump_url"].ne("").astype(int)

dump_df = (
    dump_df
    .sort_values(
        ["titleId", "_has_content", "_is_base_game", "_has_title", "_has_url", "dump_contentId"],
        ascending=[True, False, False, False, False, True],
        kind="stable"
    )
    .drop_duplicates(subset=["titleId"], keep="first")
    .drop(columns=["_has_content", "_is_base_game", "_has_title", "_has_url"])
)

merged = col_df.merge(dump_df, on="titleId", how="left")

# Final convenience columns
merged["final_gameTitle"] = prefer(merged["col_gameTitle"], merged["dump_gameTitle"])
merged["final_url"] = prefer(merged["col_url"], merged["dump_url"])
merged["final_contentId"] = norm(merged["dump_contentId"])
merged["final_has_content_id"] = merged["final_contentId"].ne("").map({True: "YES", False: "NO"})

merged["distribution_same"] = (
        (norm(merged["col_distribution"]) != "") &
        (norm(merged["dump_distribution"]) != "") &
        (norm(merged["col_distribution"]) == norm(merged["dump_distribution"]))
).map({True: "YES", False: "NO"})

merged["content_type_same"] = (
        (norm(merged["col_content_type"]) != "") &
        (norm(merged["dump_content_type"]) != "") &
        (norm(merged["col_content_type"]) == norm(merged["dump_content_type"]))
).map({True: "YES", False: "NO"})

front_cols = [
    "titleId",
    "final_gameTitle",
    "final_url",
    "final_contentId",
    "final_has_content_id",
    "col_gameTitle",
    "dump_gameTitle",
    "col_region_source",
    "dump_region_source",
    "col_platform",
    "dump_platform",
    "col_distribution",
    "dump_distribution",
    "distribution_same",
    "col_content_type",
    "dump_content_type",
    "content_type_same",
    "col_url",
    "dump_url",
    "dump_unlock_model",
    "dump_unlock_group",
]

existing_front = [c for c in front_cols if c in merged.columns]
remaining = [c for c in merged.columns if c not in existing_front]
merged = merged[existing_front + remaining]

merged = merged.drop_duplicates()
merged = merged.sort_values(["titleId", "final_contentId"], kind="stable")

merged.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(merged)} rows)")
print("\nfinal_has_content_id summary:")
print(merged["final_has_content_id"].value_counts(dropna=False))
print("\ndistribution_same summary:")
print(merged["distribution_same"].value_counts(dropna=False))
print("\ncontent_type_same summary:")
print(merged["content_type_same"].value_counts(dropna=False))
