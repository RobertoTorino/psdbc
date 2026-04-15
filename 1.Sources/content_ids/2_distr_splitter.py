import glob
import os
import pandas as pd

INPUT_PATTERN = "content_*.csv"

SKIP_FILES = {
    "unknown_debug.csv",
    "unknown_prefix_summary.csv",
    "content_unknown.csv",
}

BASE_OUTPUT_DIR = "split"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


print("Splitting files into platform/content_type/distribution folders...")

ensure_dir(BASE_OUTPUT_DIR)

for filepath in glob.glob(INPUT_PATTERN):
    filename = os.path.basename(filepath)

    if filename in SKIP_FILES:
        continue

    df = pd.read_csv(filepath)

    if df.empty:
        print(f"Skipping {filename}: empty")
        continue

    required_columns = {"platform", "distribution", "content_type"}
    if not required_columns.issubset(df.columns):
        print(f"Skipping {filename}: missing required columns")
        continue

    platform_values = df["platform"].dropna().unique()
    if len(platform_values) == 0:
        print(f"Skipping {filename}: no platform values")
        continue

    platform_name = str(platform_values[0]).lower()

    platform_dir = os.path.join(BASE_OUTPUT_DIR, platform_name)
    ensure_dir(platform_dir)

    print(f"\nProcessing {filename} → {platform_dir}/")

    grouped = df.groupby(["content_type", "distribution"], dropna=True)

    for (content_type, distribution), df_part in grouped:
        if df_part.empty:
            continue

        safe_content_type = str(content_type).lower().replace(" ", "_")
        safe_distribution = str(distribution).lower().replace(" ", "_")

        output_path = os.path.join(
            platform_dir,
            f"{platform_name}_{safe_content_type}_{safe_distribution}.csv"
        )

        df_part.to_csv(output_path, index=False)

        print(f"  Saved {output_path} ({len(df_part)} rows)")

print("\nDone.")