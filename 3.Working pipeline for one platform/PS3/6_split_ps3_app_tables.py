from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

MASTER_FILE = BASE_DIR / "ps3_master_final.csv"
ALIGNED_FILE = ROOT_DIR / "2.Normalized external data" / "psnstuff_dump" / "ps3" / "ps3.csv"
OUTPUT_DIR = ROOT_DIR / "4.App-ready outputs" / "PS3"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DISC_OUTPUT = OUTPUT_DIR / "app_ps3_disc_games.csv"
PSN_OUTPUT = OUTPUT_DIR / "app_ps3_psn_games.csv"
DLC_OUTPUT = OUTPUT_DIR / "app_ps3_dlc.csv"
DEMO_OUTPUT = OUTPUT_DIR / "app_ps3_demo.csv"
TRIAL_OUTPUT = OUTPUT_DIR / "app_ps3_trial.csv"
LICENSE_OUTPUT = OUTPUT_DIR / "app_ps3_license.csv"
THEME_OUTPUT = OUTPUT_DIR / "app_ps3_theme.csv"
AVATAR_OUTPUT = OUTPUT_DIR / "app_ps3_avatar.csv"


BASE_COLUMNS = [
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

AUX_COLUMNS = [
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


def save_sorted(df: pd.DataFrame, output_file: Path) -> None:
    df = df.drop_duplicates().sort_values(["title_id", "content_id"], kind="stable")
    df.to_csv(output_file, index=False)
    print(f"Saved {output_file} ({len(df)} rows)")


print("Reading files...")
print(f"MASTER_FILE: {MASTER_FILE}")
print(f"ALIGNED_FILE: {ALIGNED_FILE}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")

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

save_sorted(disc_df, DISC_OUTPUT)
save_sorted(psn_df, PSN_OUTPUT)

# -------------------------
# Auxiliary tables from aligned dump
# -------------------------
aligned_df = aligned_df[aligned_df["platform"] == "PS3"].copy()
aligned_df = ensure_columns(aligned_df, AUX_COLUMNS)
aligned_df["has_content_id"] = aligned_df["content_id"].ne("").map({True: "YES", False: "NO"})

def save_aux(content_type: str, output_file: Path) -> None:
    part = aligned_df[aligned_df["content_type"] == content_type].copy()
    save_sorted(part, output_file)

save_aux("DLC", DLC_OUTPUT)
save_aux("DEMO", DEMO_OUTPUT)
save_aux("TRIAL", TRIAL_OUTPUT)
save_aux("LICENSE", LICENSE_OUTPUT)
save_aux("THEME", THEME_OUTPUT)
save_aux("AVATAR", AVATAR_OUTPUT)

print("Done.")