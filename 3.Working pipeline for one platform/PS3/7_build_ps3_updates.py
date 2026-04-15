from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

INPUT_FILE = ROOT_DIR / "1.Sources" / "ps3_psn_updates.csv"
OUTPUT_DIR = ROOT_DIR / "4.App-ready outputs" / "PS3"
OUTPUT_FILE = OUTPUT_DIR / "app_ps3_update.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_COLUMNS = [
    "title_id",
    "game_title",
    "platform_source",
    "region",
    "update",
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

    return df


print(f"Reading update source: {INPUT_FILE}")

# Load file (handles .dat / .tsv / .csv)
try:
    df = pd.read_csv(INPUT_FILE, sep="\t", dtype=str).fillna("")
    if len(df.columns) == 1:
        df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
except Exception:
    df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

df = norm_df(df)

# Ensure required columns exist
for col in FINAL_COLUMNS:
    if col not in df.columns:
        df[col] = ""

# Normalize identifiers
df["title_id"] = (
    df["title_id"]
    .str.upper()
    .str.replace("-", "", regex=False)
    .str.strip()
)

df["content_id"] = df["content_id"].str.strip()
df["has_content_id"] = df["content_id"].ne("").map({True: "YES", False: "NO"})

# Force PS3 update semantics
df["platform"] = "PS3"
df["distribution"] = "PSN"
df["content_type"] = "UPDATE"

# Keep only final schema
df = df[FINAL_COLUMNS].copy()

# Deduplicate
df = df.drop_duplicates().sort_values(
    ["title_id", "content_id", "update"],
    kind="stable"
)

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {OUTPUT_FILE} ({len(df)} rows)")