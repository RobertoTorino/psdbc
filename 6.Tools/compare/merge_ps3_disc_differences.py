from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR.parent
REPORT_DIR = TOOLS_DIR / "reports" / "PS3" / "disc_games"

ONLY_IN_A_FILE = REPORT_DIR / "app_ps3_disc_games_only_in_a.csv"
ONLY_IN_B_FILE = REPORT_DIR / "app_ps3_disc_games_only_in_b.csv"
METADATA_DIFF_FILE = REPORT_DIR / "app_ps3_disc_games_metadata_differences.csv"

OUTPUT_FILE = REPORT_DIR / "app_ps3_disc_games_diff_merged.csv"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"Missing file: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [str(c).strip() for c in df.columns]

    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()

    return df


print("Reading comparison files...")

only_a = load_csv(ONLY_IN_A_FILE)
only_b = load_csv(ONLY_IN_B_FILE)
meta_diff = load_csv(METADATA_DIFF_FILE)

parts = []

if not only_a.empty:
    only_a = only_a.copy()
    only_a["source_status"] = "ONLY_IN_A"
    parts.append(only_a)

if not only_b.empty:
    only_b = only_b.copy()
    only_b["source_status"] = "ONLY_IN_B"
    parts.append(only_b)

if not meta_diff.empty:
    meta_diff = meta_diff.copy()
    meta_diff["source_status"] = "IN_BOTH_DIFFERENT"
    parts.append(meta_diff)

if not parts:
    print("No comparison files found or all were empty.")
else:
    merged = pd.concat(parts, ignore_index=True, sort=False)
    merged = merged.fillna("")

    # Put source_status first
    if "source_status" in merged.columns:
        cols = ["source_status"] + [c for c in merged.columns if c != "source_status"]
        merged = merged[cols]

    # Sort if useful keys exist
    sort_cols = [c for c in ["source_status", "title_id", "content_id"] if c in merged.columns]
    if sort_cols:
        merged = merged.sort_values(sort_cols, kind="stable")

    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {OUTPUT_FILE} ({len(merged)} rows)")