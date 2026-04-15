import pandas as pd

INPUT_FILE = "../2.Normalized external data/psnstuff_dump/ps3_aligned.csv"


def norm(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


print("Reading file...")

df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
df.columns = [str(c).strip() for c in df.columns]

for c in df.columns:
    df[c] = norm(df[c])

df["title_id"] = (
    df["title_id"]
    .str.upper()
    .str.replace("-", "", regex=False)
    .str.strip()
)

print(f"Total rows: {len(df)}")

# Filter PS3 only
ps3 = df[df["platform"] == "PS3"].copy()

print(f"PS3 rows: {len(ps3)}")

print("\n--- CONTENT TYPE COUNTS ---")
print(ps3["content_type"].value_counts(dropna=False))

print("\n--- DISTRIBUTION COUNTS ---")
print(ps3["distribution"].value_counts(dropna=False))

print("\n--- CONTENT TYPE x DISTRIBUTION ---")
print(pd.crosstab(ps3["content_type"], ps3["distribution"]))

print("\n--- HAS CONTENT ID ---")
ps3["has_content_id"] = ps3["content_id"].ne("").map({True: "YES", False: "NO"})
print(ps3["has_content_id"].value_counts(dropna=False))

print("\n--- SAMPLE BASE_GAME (first 10) ---")
print(ps3[ps3["content_type"] == "BASE_GAME"].head(10)[[
    "title_id", "game_title", "distribution", "content_id"
]])

print("\n--- SAMPLE NON-BASE_GAME (first 10) ---")
print(ps3[ps3["content_type"] != "BASE_GAME"].head(10)[[
    "title_id", "game_title", "content_type", "distribution"
]])

print("\nDone.")