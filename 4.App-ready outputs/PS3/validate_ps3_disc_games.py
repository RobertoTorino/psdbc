import pandas as pd

df = pd.read_csv("app_ps3_disc_games_merged.csv", dtype=str).fillna("")
# print("Total rows:", len(df))
# print("\nUnique title_id:", df["title_id"].nunique())
#
# dupes = df[df.duplicated(subset=["title_id"], keep=False)]
# print("Duplicate rows:", len(dupes))
#
# print(df["platform"].value_counts())
# print(df["distribution"].value_counts())
# print(df["content_type"].value_counts())

# print(sorted(df["region"].unique()))

# print(df["game_title"].isna().sum())
# print((df["game_title"] == "").sum())

# enriched = df[df["has_content_id"] == "YES"]
# print(enriched.head(10))
#
# a_df = pd.read_csv("app_ps3_disc_games.csv", dtype=str).fillna("")
#
# missing = set(a_df["title_id"]) - set(df["title_id"])
# print("Lost rows from A:", len(missing))
#
# new = set(df["title_id"]) - set(a_df["title_id"])
# print("New rows added from B:", len(new))

print("\n=== SUMMARY ===")
print("Rows:", len(df))
print("Unique title_id:", df["title_id"].nunique())
print("With content_id:", (df["has_content_id"] == "YES").sum())
print("Regions:", df["region"].value_counts().to_dict())