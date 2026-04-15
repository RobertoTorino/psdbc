from pathlib import Path
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent          # 6.Tools/compare
TOOLS_DIR = BASE_DIR.parent                         # 6.Tools
ROOT_DIR = TOOLS_DIR.parent                         # project root

A_DIR = ROOT_DIR / "4.App-ready outputs" / "PS3"
B_DIR = TOOLS_DIR / "comparison_input" / "PS3"
REPORT_DIR = TOOLS_DIR / "reports" / "PS3"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

TABLES = [
    ("app_ps3_disc_games.csv", "title_id"),
    ("app_ps3_psn_games.csv", "title_id"),
    ("app_ps3_dlc.csv", "content_id"),
    ("app_ps3_demo.csv", "content_id"),
    ("app_ps3_trial.csv", "content_id"),
    ("app_ps3_license.csv", "content_id"),
    ("app_ps3_theme.csv", "content_id"),
    ("app_ps3_avatar.csv", "content_id"),
]

# -----------------------------
# HELPERS
# -----------------------------
def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def normalize_key(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.replace("-", "", regex=False)
        .str.strip()
    )


def normalize_df(df: pd.DataFrame, key: str) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    if key in df.columns:
        df[key] = normalize_key(df[key])

    return df


def compare_tables(file_name: str, key: str) -> None:
    a_path = A_DIR / file_name
    b_path = B_DIR / file_name

    print(f"\nComparing: {file_name}")

    if not a_path.exists():
        print(f"  Missing in A: {a_path}")
        return

    if not b_path.exists():
        print(f"  Missing in B: {b_path}")
        return

    a_df = load_csv(a_path)
    b_df = load_csv(b_path)

    if key not in a_df.columns:
        print(f"  Key '{key}' missing in A file")
        return

    if key not in b_df.columns:
        print(f"  Key '{key}' missing in B file")
        return

    # normalize
    a_df = normalize_df(a_df, key)
    b_df = normalize_df(b_df, key)

    # ensure optional columns exist
    optional_cols = ["package_name"]

    for col in optional_cols:
        if col not in a_df.columns:
            a_df[col] = ""
        if col not in b_df.columns:
            b_df[col] = ""

    # Remove empty keys
    a_df = a_df[a_df[key] != ""].copy()
    b_df = b_df[b_df[key] != ""].copy()

    # Unique key sets
    a_keys = set(a_df[key])
    b_keys = set(b_df[key])

    only_in_a = sorted(a_keys - b_keys)
    only_in_b = sorted(b_keys - a_keys)
    in_both = sorted(a_keys & b_keys)

    stem = file_name.replace(".csv", "")

    # Save simple key reports
    pd.DataFrame({key: only_in_a}).to_csv(REPORT_DIR / f"{stem}_only_in_a.csv", index=False)
    pd.DataFrame({key: only_in_b}).to_csv(REPORT_DIR / f"{stem}_only_in_b.csv", index=False)
    pd.DataFrame({key: in_both}).to_csv(REPORT_DIR / f"{stem}_in_both.csv", index=False)

    # Metadata diff report for shared keys
    merged = a_df.merge(b_df, on=key, suffixes=("_a", "_b"))

    compare_columns = [
        c for c in set(a_df.columns).intersection(set(b_df.columns))
        if c != key
    ]

    diff_mask = pd.Series(False, index=merged.index)
    for col in compare_columns:
        diff_mask = diff_mask | (merged[f"{col}_a"] != merged[f"{col}_b"])

    diffs = merged[diff_mask].copy()
    diffs.to_csv(REPORT_DIR / f"{stem}_metadata_differences.csv", index=False)

    print("Sample A content_id:", a_df["content_id"].head(5).tolist())
    print("Sample B content_id:", b_df["content_id"].head(5).tolist())

    # Summary
    summary = pd.DataFrame([{
        "file": file_name,
        "key": key,
        "rows_a": len(a_df),
        "rows_b": len(b_df),
        "unique_keys_a": len(a_keys),
        "unique_keys_b": len(b_keys),
        "only_in_a": len(only_in_a),
        "only_in_b": len(only_in_b),
        "in_both": len(in_both),
        "metadata_differences": len(diffs),
    }])

    summary_path = REPORT_DIR / f"{stem}_summary.csv"
    summary.to_csv(summary_path, index=False)

    print(f"  rows_a: {len(a_df)}")
    print(f"  rows_b: {len(b_df)}")
    print(f"  only_in_a: {len(only_in_a)}")
    print(f"  only_in_b: {len(only_in_b)}")
    print(f"  in_both: {len(in_both)}")
    print(f"  metadata_differences: {len(diffs)}")

# -----------------------------
# MAIN
# -----------------------------
print("A_DIR:", A_DIR)
print("B_DIR:", B_DIR)
print("REPORT_DIR:", REPORT_DIR)

for file_name, key in TABLES:
    compare_tables(file_name, key)

print("\nDone.")