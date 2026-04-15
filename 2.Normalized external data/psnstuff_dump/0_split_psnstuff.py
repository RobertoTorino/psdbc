import os
import pandas as pd

INPUT_FILE = "db_external.tsv"
INPUT_SEP = "\t"
OUTPUT_DIR = ""


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def normalize_title_id(value: str) -> str:
    if pd.isna(value):
        return ""
    return str(value).upper().replace("-", "").strip()


def normalize_text(value: str) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def safe_name(value: str) -> str:
    if pd.isna(value):
        return "unknown"
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def infer_platform_from_title_id(title_id: str) -> str:
    tid = normalize_title_id(title_id)
    if not tid:
        return "OTHER"

    if tid.startswith(("NPXS", "NPXP", "BOOG")):
        return "SYSTEM"

    if tid.startswith(("SLES", "SLUS", "SCES", "SCUS")):
        return "PS1"

    if tid.startswith("PPSA"):
        return "PS5"

    if tid.startswith("CUSA"):
        return "PS4"

    if tid.startswith("PCS") or tid.startswith(("NPVA", "NPVB")):
        return "PSVITA"

    if tid.startswith((
            "BLUS", "BLES", "BCUS", "BCES", "BLAS", "BCAS",
            "BLJM", "BLJS", "BCJS", "BCJB", "BLKS", "BCKS", "BCET",
            "BLET",
            "NPUB", "NPEB", "NPJB", "NPED", "NPEA", "NPEJ", "NPEC",
            "NPHB", "NPHA", "NPHJ", "NPHD", "NPHI", "NPHL", "NPHW", "NPHC", "NPHY", "NPHX",
            "NPIA", "NPEE", "NPET", "NPES", "NPEX", "NPJC", "NPJN", "NPUC", "UCED"
    )):
        return "PS3"

    if tid.startswith((
            "NPUH", "NPUG", "NPUF", "NPEG", "NPEH", "NPEP",
            "NPMA", "NPPA", "NPUP",
            "NPJJ", "NPJA", "NPJD", "NPJI", "NPJQ", "NPJR", "NPJM", "NPJW", "NPJH", "NPJG", "NPJY",
            "NPUA", "NPUD", "NPUJ", "NPUZ", "NPUX", "NPUO", "NPUY", "NPUI", "NPUL", "NPUW",
            "NPEL", "NPEF", "NPEO", "NPEZ", "NPEK",
            "NPHP", "NPHH", "NPHO", "NPHZ", "NPHG", "NPHT",
            "NPKA", "NPKH",
            "ULES", "ULUS", "ULJS", "ULJM", "ULAS",
            "UCES", "UCUS", "UCAS", "UCJS", "UCKS"
    )):
        return "PSP"

    return "OTHER"


def infer_unlock_model(platform_source: str, title_id: str, game_title: str):
    sp = normalize_text(platform_source)
    tid = normalize_title_id(title_id)
    title = normalize_text(game_title).lower()

    if sp == "C00":
        return "TRIAL_UNLOCKABLE", tid

    if sp == "EDAT":
        return "LICENSE_UNLOCK", tid

    if "beta" in title:
        return "BETA_PROGRAM", tid

    if "trial" in title:
        return "TRIAL_STANDALONE", tid

    return "NONE", ""


def map_row(source_platform: str, title_id: str, game_title: str):
    sp = normalize_text(source_platform)
    tid = normalize_title_id(title_id)
    prefix4 = tid[:4] if tid else ""
    title = normalize_text(game_title).lower()

    if "beta" in title:
        platform = infer_platform_from_title_id(tid)
        if platform == "OTHER":
            platform = "PS3"
        return platform, "PSN", "DEMO"

    if sp == "C00":
        return "PS3", "PSN", "TRIAL"

    if sp == "EDAT":
        return "PS3", "LICENSE", "LICENSE"

    if sp == "DLC":
        platform = infer_platform_from_title_id(tid)
        if platform == "OTHER":
            platform = "PS3"
        return platform, "PSN", "DLC"

    if sp == "Theme":
        platform = infer_platform_from_title_id(tid)
        return platform if platform != "OTHER" else "OTHER", "PSN", "THEME"

    if sp == "Demo":
        platform = infer_platform_from_title_id(tid)
        return platform if platform != "OTHER" else "OTHER", "PSN", "DEMO"

    if sp == "Avatar":
        platform = infer_platform_from_title_id(tid)
        return platform if platform != "OTHER" else "OTHER", "PSN", "AVATAR"

    if sp == "Wallpaper":
        return "OTHER", "PSN", "WALLPAPER"

    if sp == "Video":
        return "OTHER", "PSN", "VIDEO"

    if sp == "WebTV":
        return "OTHER", "PSN", "WEBTV"

    if sp == "Soundtrack":
        return "OTHER", "PSN", "SOUNDTRACK"

    if sp == "Mini":
        return "PSP", "MINI", "BASE_GAME"

    if sp == "PS1":
        return "PS1", "DISC", "BASE_GAME"

    if sp == "PS2":
        return "PS2", "DISC", "BASE_GAME"

    if sp == "PS3":
        return "PS3", "PSN", "BASE_GAME"

    if sp == "PS4":
        return "PS4", "PSN", "BASE_GAME"

    if sp == "PSP":
        if prefix4 in {"ULES", "ULUS", "ULJS", "ULJM", "ULAS", "UCES", "UCUS", "UCAS", "UCJS", "UCKS"}:
            return "PSP", "UMD", "BASE_GAME"
        return "PSP", "PSN", "BASE_GAME"

    if sp in ("PSVita", "PS Vita"):
        if prefix4.startswith("PCS"):
            return "PSVITA", "CARD", "BASE_GAME"
        return "PSVITA", "PSN", "BASE_GAME"

    if sp == "PSN":
        platform = infer_platform_from_title_id(tid)
        return platform, "PSN", "BASE_GAME"

    platform = infer_platform_from_title_id(tid)
    return platform, "OTHER", "UNKNOWN"


print("Reading dump...")

df = pd.read_csv(INPUT_FILE, sep=INPUT_SEP, dtype=str).fillna("")
df.columns = [str(c).strip() for c in df.columns]

required = {"title_id", "game_title", "platform", "region", "url", "content_id"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Normalize source columns
df["title_id"] = df["title_id"].apply(normalize_title_id)
df["game_title"] = df["game_title"].apply(normalize_text)
df["platform_source"] = df["platform"].apply(normalize_text)
df["region"] = df["region"].apply(normalize_text)
df["url"] = df["url"].apply(normalize_text)
df["content_id"] = df["content_id"].apply(normalize_text)
df["has_content_id"] = df["content_id"].apply(lambda x: "YES" if str(x).strip() else "NO")

# Remove misleading raw columns from final output
df = df.drop(columns=["platform", "region"])

# Normalize to final model
mapped = df.apply(
    lambda r: map_row(r["platform_source"], r["title_id"], r["game_title"]),
    axis=1,
    result_type="expand"
)
mapped.columns = ["platform", "distribution", "content_type"]
df = pd.concat([df, mapped], axis=1)

# Add unlock metadata
unlock_info = df.apply(
    lambda r: infer_unlock_model(r["platform_source"], r["title_id"], r["game_title"]),
    axis=1,
    result_type="expand"
)
unlock_info.columns = ["unlock_model", "unlock_group"]
df = pd.concat([df, unlock_info], axis=1)

# Consistent column order across all platform exports
final_columns = [
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
df = df[final_columns]

df = df.drop_duplicates()

ensure_dir(OUTPUT_DIR)

master_path = os.path.join(OUTPUT_DIR, "dump_master.csv")
df.to_csv(master_path, index=False)
print(f"Saved {master_path} ({len(df)} rows)")

# Split by platform and content type
for platform in sorted(df["platform"].dropna().unique()):
    df_platform = df[df["platform"] == platform].copy()
    if df_platform.empty:
        continue

    platform_dir = os.path.join(OUTPUT_DIR, platform.lower())
    ensure_dir(platform_dir)

    print(f"\nProcessing platform: {platform}")

    platform_out_path = os.path.join(platform_dir, f"{platform.lower()}.csv")
    df_platform.to_csv(platform_out_path, index=False)
    print(f"Saved {platform_out_path} ({len(df_platform)} rows)")

    for content_type in sorted(df_platform["content_type"].dropna().unique()):
        df_type = df_platform[df_platform["content_type"] == content_type].copy()
        if df_type.empty:
            continue

        type_name = safe_name(content_type)
        type_out_path = os.path.join(platform_dir, f"{platform.lower()}_{type_name}.csv")
        df_type.to_csv(type_out_path, index=False)
        print(f"Saved {type_out_path} ({len(df_type)} rows)")

print("\nNormalized platform summary:")
print(df["platform"].value_counts(dropna=False))

print("\nDistribution summary:")
print(df["distribution"].value_counts(dropna=False))

print("\nContent type summary:")
print(df["content_type"].value_counts(dropna=False))

print("\nUnlock model summary:")
print(df["unlock_model"].value_counts(dropna=False))

print("Done.")