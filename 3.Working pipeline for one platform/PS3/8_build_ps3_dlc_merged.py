from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

A_FILE = ROOT_DIR / "4.App-ready outputs" / "PS3" / "app_ps3_dlc.csv"
B_FILE = ROOT_DIR / "6.Tools" / "comparison_input" / "PS3" / "app_ps3_dlc.csv"
OUTPUT_DIR = ROOT_DIR / "4.App-ready outputs" / "PS3"
OUTPUT_FILE = OUTPUT_DIR / "app_ps3_dlc_merged.csv"

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
    "package_name",
]


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].fillna("").astype(str).str.strip()
    return df


def normalize_content_id(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )


def prefer(a: pd.Series, b: pd.Series) -> pd.Series:
    a = a.fillna("").astype(str).str.strip()
    b = b.fillna("").astype(str).str.strip()
    return a.where(a != "", b)


print("Reading files...")
print(f"A_FILE: {A_FILE}")
print(f"B_FILE: {B_FILE}")

a_df = pd.read_csv(A_FILE, dtype=str).fillna("")
b_df = pd.read_csv(B_FILE, dtype=str).fillna("")

a_df = norm_df(a_df)
b_df = norm_df(b_df)

print(f"Rows A: {len(a_df)}")
print(f"Rows B: {len(b_df)}")

# Ensure optional column exists
if "package_name" not in a_df.columns:
    a_df["package_name"] = ""
if "package_name" not in b_df.columns:
    b_df["package_name"] = ""

# Ensure all final columns exist
for col in FINAL_COLUMNS:
    if col not in a_df.columns:
        a_df[col] = ""
    if col not in b_df.columns:
        b_df[col] = ""

# Normalize content_id for key matching
a_df["compare_key"] = normalize_content_id(a_df["content_id"])
b_df["compare_key"] = normalize_content_id(b_df["content_id"])

# Remove rows without usable content_id
a_df = a_df[a_df["compare_key"] != ""].copy()
b_df = b_df[b_df["compare_key"] != ""].copy()

# Deduplicate each side by compare_key
a_df = (
    a_df.sort_values(["compare_key", "content_id"], kind="stable")
    .drop_duplicates(subset=["compare_key"], keep="first")
    .copy()
)

b_df = (
    b_df.sort_values(["compare_key", "content_id"], kind="stable")
    .drop_duplicates(subset=["compare_key"], keep="first")
    .copy()
)

print(f"Rows A after dedupe: {len(a_df)}")
print(f"Rows B after dedupe: {len(b_df)}")

# Rename for side-by-side merge
a_df = a_df.rename(columns={c: f"{c}_a" for c in FINAL_COLUMNS})
b_df = b_df.rename(columns={c: f"{c}_b" for c in FINAL_COLUMNS})

merged = a_df.merge(b_df, on="compare_key", how="outer")

print(f"Merged rows: {len(merged)}")

# Build final row
result = pd.DataFrame()

# Prefer B for canonical DLC metadata, then fall back to A
result["title_id"] = prefer(merged.get("title_id_b", ""), merged.get("title_id_a", ""))
result["game_title"] = prefer(merged.get("game_title_b", ""), merged.get("game_title_a", ""))
result["platform_source"] = prefer(merged.get("platform_source_b", ""), merged.get("platform_source_a", ""))
result["region"] = prefer(merged.get("region_b", ""), merged.get("region_a", ""))
result["url"] = prefer(merged.get("url_b", ""), merged.get("url_a", ""))
result["content_id"] = prefer(merged.get("content_id_b", ""), merged.get("content_id_a", ""))
result["platform"] = prefer(merged.get("platform_b", ""), merged.get("platform_a", ""))
result["distribution"] = prefer(merged.get("distribution_b", ""), merged.get("distribution_a", ""))
result["content_type"] = prefer(merged.get("content_type_b", ""), merged.get("content_type_a", ""))
result["unlock_model"] = prefer(merged.get("unlock_model_b", ""), merged.get("unlock_model_a", ""))
result["unlock_group"] = prefer(merged.get("unlock_group_b", ""), merged.get("unlock_group_a", ""))
result["package_name"] = prefer(merged.get("package_name_b", ""), merged.get("package_name_a", ""))

# Recompute has_content_id
result["has_content_id"] = result["content_id"].fillna("").astype(str).str.strip().ne("").map({True: "YES", False: "NO"})

# Force PS3 DLC semantics if missing
result["platform"] = result["platform"].replace("", "PS3")
result["distribution"] = result["distribution"].replace("", "PSN")
result["content_type"] = result["content_type"].replace("", "DLC")

# Keep final schema
for col in FINAL_COLUMNS:
    if col not in result.columns:
        result[col] = ""

result = result[FINAL_COLUMNS].copy()
result = result.drop_duplicates().sort_values(["title_id", "content_id"], kind="stable")

result.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(result)} rows)")
print("\nhas_content_id summary:")
print(result["has_content_id"].value_counts(dropna=False))


