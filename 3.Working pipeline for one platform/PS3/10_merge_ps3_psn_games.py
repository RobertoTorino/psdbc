from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

A_FILE = ROOT_DIR / "4.App-ready outputs" / "PS3" / "app_ps3_psn_games.csv"
B_FILE = ROOT_DIR / "6.Tools" / "comparison_input" / "PS3" / "app_ps3_psn_games.csv"
OUTPUT_DIR = ROOT_DIR / "4.App-ready outputs" / "PS3"
OUTPUT_FILE = OUTPUT_DIR / "app_ps3_psn_games_merged.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_COLUMNS = [
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
]


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    for c in df.columns:
        df[c] = df[c].fillna("").astype(str).str.strip()

    if "title_id" in df.columns:
        df["title_id"] = (
            df["title_id"]
            .astype(str)
            .str.upper()
            .str.replace("-", "", regex=False)
            .str.strip()
        )

    if "content_id" in df.columns:
        df["content_id"] = (
            df["content_id"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    return df


def prefer(a: pd.Series, b: pd.Series) -> pd.Series:
    a = a.fillna("").astype(str).str.strip()
    b = b.fillna("").astype(str).str.strip()
    return a.where(a != "", b)


def prefer_longer(a: pd.Series, b: pd.Series) -> pd.Series:
    a = a.fillna("").astype(str).str.strip()
    b = b.fillna("").astype(str).str.strip()

    use_b = (a == "") | ((b != "") & (b.str.len() > a.str.len()))
    return a.where(~use_b, b)


print("Reading files...")
print(f"A_FILE: {A_FILE}")
print(f"B_FILE: {B_FILE}")

a_df = pd.read_csv(A_FILE, dtype=str).fillna("")
b_df = pd.read_csv(B_FILE, dtype=str).fillna("")

a_df = norm_df(a_df)
b_df = norm_df(b_df)

print(f"Rows A: {len(a_df)}")
print(f"Rows B: {len(b_df)}")

for col in FINAL_COLUMNS:
    if col not in a_df.columns:
        a_df[col] = ""
    if col not in b_df.columns:
        b_df[col] = ""

a_df = a_df[FINAL_COLUMNS].copy()
b_df = b_df[FINAL_COLUMNS].copy()

# Keep only valid PS3 PSN BASE_GAME rows
a_df = a_df[
    (a_df["platform"] == "PS3") &
    (a_df["distribution"] == "PSN") &
    (a_df["content_type"] == "BASE_GAME")
    ].copy()

b_df = b_df[
    (b_df["platform"] == "PS3") &
    (b_df["distribution"] == "PSN") &
    (b_df["content_type"] == "BASE_GAME")
    ].copy()

# Deduplicate by title_id
a_df = (
    a_df.sort_values(["title_id", "content_id"], kind="stable")
    .drop_duplicates(subset=["title_id"], keep="first")
    .copy()
)

b_df = (
    b_df.sort_values(["title_id", "content_id"], kind="stable")
    .drop_duplicates(subset=["title_id"], keep="first")
    .copy()
)

print(f"Rows A after dedupe: {len(a_df)}")
print(f"Rows B after dedupe: {len(b_df)}")

a_df = a_df.rename(columns={c: f"{c}_a" for c in FINAL_COLUMNS})
b_df = b_df.rename(columns={c: f"{c}_b" for c in FINAL_COLUMNS})

merged = a_df.merge(
    b_df,
    left_on="title_id_a",
    right_on="title_id_b",
    how="outer"
)

print(f"Merged rows: {len(merged)}")

result = pd.DataFrame()

result["title_id"] = prefer(
    merged.get("title_id_b", pd.Series("", index=merged.index)),
    merged.get("title_id_a", pd.Series("", index=merged.index))
)

# Prefer the more descriptive title
result["game_title"] = prefer_longer(
    merged.get("game_title_a", pd.Series("", index=merged.index)),
    merged.get("game_title_b", pd.Series("", index=merged.index))
)

# Usually keep your source tag unless empty
result["platform_source"] = prefer(
    merged.get("platform_source_a", pd.Series("", index=merged.index)),
    merged.get("platform_source_b", pd.Series("", index=merged.index))
)

# Prefer mapped / cleaner region from A, fallback to B
result["region"] = prefer(
    merged.get("region_a", pd.Series("", index=merged.index)),
    merged.get("region_b", pd.Series("", index=merged.index))
)

# Prefer non-empty URL, usually B may have richer one
result["url"] = prefer(
    merged.get("url_a", pd.Series("", index=merged.index)),
    merged.get("url_b", pd.Series("", index=merged.index))
)

# For PSN games, prefer B's content_id formatting if present
result["content_id"] = prefer(
    merged.get("content_id_b", pd.Series("", index=merged.index)),
    merged.get("content_id_a", pd.Series("", index=merged.index))
)

result["platform"] = prefer(
    merged.get("platform_a", pd.Series("", index=merged.index)),
    merged.get("platform_b", pd.Series("", index=merged.index))
).replace("", "PS3")

result["distribution"] = prefer(
    merged.get("distribution_a", pd.Series("", index=merged.index)),
    merged.get("distribution_b", pd.Series("", index=merged.index))
).replace("", "PSN")

result["content_type"] = prefer(
    merged.get("content_type_a", pd.Series("", index=merged.index)),
    merged.get("content_type_b", pd.Series("", index=merged.index))
).replace("", "BASE_GAME")

result["unlock_model"] = prefer(
    merged.get("unlock_model_a", pd.Series("", index=merged.index)),
    merged.get("unlock_model_b", pd.Series("", index=merged.index))
)

result["unlock_group"] = prefer(
    merged.get("unlock_group_a", pd.Series("", index=merged.index)),
    merged.get("unlock_group_b", pd.Series("", index=merged.index))
)

result["has_content_id"] = (
    result["content_id"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
    .map({True: "YES", False: "NO"})
)

for col in FINAL_COLUMNS:
    if col not in result.columns:
        result[col] = ""

result = result[FINAL_COLUMNS].copy()
result = result.drop_duplicates()
result = result.sort_values(["title_id", "content_id"], kind="stable")

result.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(result)} rows)")
print("\nhas_content_id summary:")
print(result["has_content_id"].value_counts(dropna=False))
print("\nregion summary:")
print(result["region"].value_counts(dropna=False))