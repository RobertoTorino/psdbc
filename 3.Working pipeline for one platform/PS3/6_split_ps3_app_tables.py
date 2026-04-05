import pandas as pd

MASTER_FILE = "ps3_master_final.csv"
ALIGNED_FILE = "ps3_aligned.csv"

DISC_OUTPUT = "ps3_disc_games.csv"
PSN_OUTPUT = "ps3_psn_games.csv"
DLC_OUTPUT = "ps3_dlc.csv"
DEMO_OUTPUT = "ps3_demo.csv"
TRIAL_OUTPUT = "ps3_trial.csv"
LICENSE_OUTPUT = "ps3_license.csv"
THEME_OUTPUT = "ps3_theme.csv"
AVATAR_OUTPUT = "ps3_avatar.csv"


BASE_COLUMNS = [
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

AUX_COLUMNS = [
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


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].fillna("").astype(str).str.strip()
    if "titleId" in df.columns:
        df["titleId"] = (
            df["titleId"]
            .str.upper()
            .str.replace("-", "", regex=False)
            .str.strip()
        )
    return df


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    return df[columns].copy()


print("Reading files...")

master_df = pd.read_csv(MASTER_FILE, dtype=str).fillna("")
aligned_df = pd.read_csv(ALIGNED_FILE, dtype=str).fillna("")

master_df = norm_df(master_df)
aligned_df = norm_df(aligned_df)

print(f"Master rows: {len(master_df)}")
print(f"Aligned rows: {len(aligned_df)}")

# -------------------------
# Base game tables from final master
# -------------------------
master_df = ensure_columns(master_df, BASE_COLUMNS)

disc_df = master_df[
    (master_df["platform"] == "PS3") &
    (master_df["distribution"] == "DISC") &
    (master_df["content_type"] == "BASE_GAME")
    ].copy()

psn_df = master_df[
    (master_df["platform"] == "PS3") &
    (master_df["distribution"] == "PSN") &
    (master_df["content_type"] == "BASE_GAME")
    ].copy()

disc_df = disc_df.drop_duplicates().sort_values(["titleId", "contentId"], kind="stable")
psn_df = psn_df.drop_duplicates().sort_values(["titleId", "contentId"], kind="stable")

disc_df.to_csv(DISC_OUTPUT, index=False)
psn_df.to_csv(PSN_OUTPUT, index=False)

print(f"Saved {DISC_OUTPUT} ({len(disc_df)} rows)")
print(f"Saved {PSN_OUTPUT} ({len(psn_df)} rows)")

# -------------------------
# Auxiliary tables from aligned dump
# -------------------------
aligned_df = aligned_df[aligned_df["platform"] == "PS3"].copy()
aligned_df = ensure_columns(aligned_df, AUX_COLUMNS)

aligned_df["has_content_id"] = aligned_df["contentId"].ne("").map({True: "YES", False: "NO"})

def save_aux(content_type: str, output_file: str):
    part = aligned_df[aligned_df["content_type"] == content_type].copy()
    part = part.drop_duplicates().sort_values(["titleId", "contentId"], kind="stable")
    part.to_csv(output_file, index=False)
    print(f"Saved {output_file} ({len(part)} rows)")

save_aux("DLC", DLC_OUTPUT)
save_aux("DEMO", DEMO_OUTPUT)
save_aux("TRIAL", TRIAL_OUTPUT)
save_aux("LICENSE", LICENSE_OUTPUT)
save_aux("THEME", THEME_OUTPUT)
save_aux("AVATAR", AVATAR_OUTPUT)

print("Done.")