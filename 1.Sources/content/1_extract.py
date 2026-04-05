import re
import pandas as pd

INPUT_FILE = "all_content_ids.txt"

# Extraction helpers
def extract_title_id(cid):
    match = re.search(r'-([A-Z]{4,5}\d{5})', cid)
    return match.group(1) if match else None


def extract_store(cid):
    return cid.split("-")[0] if "-" in cid else None


def extract_store_region(store):
    return store[:2] if store else None


def extract_title_prefix(title_id):
    return title_id[:4] if title_id else None


# Platform detection
def detect_platform(title_id):
    if not title_id:
        return "OTHER"

    # SYSTEM
    if title_id.startswith(("NPXS", "NPXP", "BOOG")):
        return "SYSTEM"

    # PS1
    if title_id.startswith("SLES"):
        return "PS1"

    # PS5
    if title_id.startswith("PPSA"):
        return "PS5"

    # PS4
    if title_id.startswith("CUSA"):
        return "PS4"

    # PSVITA
    if title_id.startswith("PCS") or title_id.startswith(("NPVA", "NPVB")):
        return "PSVITA"

    # PS3
    if title_id.startswith((
            "BLUS", "BLES", "BCUS", "BCES", "BLAS", "BCAS",
            "BLJM", "BLJS", "BCJS", "BCJB", "BLKS", "BCKS", "BCET",
            "NPUB", "NPEB", "NPJB", "NPED", "NPEA", "NPEJ", "NPEC",
            "NPHB", "NPHA", "NPHJ", "NPHD", "NPHI", "NPHL", "NPHW", "NPHC", "NPHY", "NPHX",
            "NPIA",
            "NPEE", "NPET", "NPES", "NPEX",
            "NPJC", "NPJN",
            "NPUC",
            "UCED"
    )):
        return "PS3"

    # PSP (includes many PSN-only portable families)
    if title_id.startswith((
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


# Distribution mapping
def map_distribution(title_id, platform):
    if not title_id:
        return "OTHER"

    prefix = title_id[:4]

    if platform in ("PS4", "PS5"):
        return "PSN"

    if prefix == "BOOG":
        return "GIFT_CARD"

    if platform == "SYSTEM":
        return "SYSTEM"

    if platform == "PS1":
        return "DISC"

    if platform == "PS3":
        if prefix.startswith(("BL", "BC")):
            return "DISC"
        if prefix.startswith(("NP", "UC")):
            return "PSN"
        return "OTHER"

    if platform == "PSVITA":
        if prefix.startswith("PCS"):
            return "DISC"
        if prefix.startswith("NPV"):
            return "PSN"
        return "OTHER"

    if platform == "PSP":
        if prefix in ("ULES", "ULUS", "ULJS", "ULJM", "ULAS", "UCES", "UCUS", "UCAS", "UCJS", "UCKS"):
            return "UMD"
        if prefix == "NPMA":
            return "MINI"
        if prefix.startswith("NP"):
            return "PSN"
        return "OTHER"

    return "OTHER"


# Region mapping
def map_region(title_id, platform):
    if not title_id:
        return "UNKNOWN"

    prefix = title_id[:4]

    # PS4 / PS5 -> use platform as requested
    if platform in ("PS4", "PS5"):
        return platform

    # SYSTEM
    if prefix == "BOOG":
        return "UNKNOWN"

    if platform == "SYSTEM":
        return "UNKNOWN"

    if platform == "PS1":
        if prefix == "SLES":
            return "EUROPE"

        return "UNKNOWN"

    # PSVITA
    if prefix in ("PCSA", "PCSE"):
        return "USA"
    if prefix in ("PCSB", "PCSD", "PCSF"):
        return "EUROPE"
    if prefix in ("PCSC", "PCSH", "PCSI"):
        return "ASIA"
    if prefix == "PCSG":
        return "JAPAN"
    if prefix in ("NPVA", "NPVB"):
        return "PSN"

    # PS3
    if prefix in ("BLUS", "BCUS", "NPUB", "NPUC"):
        return "USA"
    if prefix in ("BLES", "BCES", "BCET", "NPEB", "NPED", "NPEE", "NPEF", "NPEL", "NPEK", "NPEZ", "NPEO", "NPEC", "NPES", "NPET", "NPEX", "NPHD", "UCED"):
        return "EUROPE"
    if prefix in ("BLAS", "BCAS", "NPEA", "NPHA", "NPHB", "NPHC", "NPHI", "NPHL", "NPHW", "NPHY", "NPHX"):
        return "ASIA"
    if prefix in ("BLJM", "BLJS", "BCJB", "BCJS", "NPEJ", "NPJB", "NPJC", "NPJN", "NPHJ", "NPIA"):
        return "JAPAN"
    if prefix in ("BLKS", "BCKS"):
        return "KOREA"

    # PSP
    if prefix in ("ULUS", "UCUS", "NPUA", "NPUD", "NPUJ", "NPUZ", "NPUX", "NPUP", "NPUO", "NPUY", "NPUI", "NPUL", "NPUW"):
        return "USA"
    if prefix in ("ULES", "UCES", "NPEL", "NPEF", "NPEO", "NPEZ", "NPEK", "NPEG", "NPEH", "NPEP"):
        return "EUROPE"
    if prefix in ("ULJS", "ULJM", "UCJS", "NPJJ", "NPJA", "NPJD", "NPJI", "NPJQ", "NPJR", "NPJM", "NPJW", "NPJH", "NPJG", "NPJY"):
        return "JAPAN"
    if prefix in ("ULAS", "UCAS", "NPHP", "NPHH", "NPHO", "NPHZ", "NPHG", "NPHT"):
        return "ASIA"
    if prefix in ("UCKS", "NPKA", "NPKH"):
        return "KOREA"
    if prefix == "NPMA":
        return "PSP_MINI"

    return "UNKNOWN"


# Content type mapping
def map_content_type(content_id, title_id, platform, distribution):
    if not content_id:
        return "UNKNOWN"

    cid = content_id.upper()
    prefix = title_id[:4] if title_id else ""

    if prefix == "BOOG" or distribution == "GIFT_CARD":
        return "PROMO"

    if platform == "SYSTEM":
        return "SYSTEM"

    if "DEMO" in cid or "TRIAL" in cid:
        return "DEMO"

    if "THEME" in cid:
        return "THEME"

    if "PATCH" in cid or "UPDATE" in cid:
        return "UPDATE"

    if "AVATAR" in cid:
        return "AVATAR"

    if any(x in cid for x in (
            "DLC", "ADDON", "ADD-ON", "EXPANSION", "SEASONPASS",
            "SEASON", "MAPPACK", "PACK", "EPISODE", "COSTUME",
            "SKIN", "WEAPON", "BONUS", "UNLOCK"
    )):
        return "DLC"

    if any(x in cid for x in (
            "ULTIMATE", "DELUXE", "COMPLETE", "COLLECTION", "BUNDLE", "GOTY"
    )):
        return "BUNDLE"

    if platform == "PS1":
        return "BASE_GAME"

    if distribution in ("DISC", "UMD", "MINI"):
        return "BASE_GAME"

    if distribution == "PSN":
        return "BASE_GAME"

    return "UNKNOWN"


# Main processing
rows = []

print("Reading content IDs...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        content_id = line.strip()
        if not content_id:
            continue

        title_id = extract_title_id(content_id)
        platform = detect_platform(title_id)
        store = extract_store(content_id)
        store_region = extract_store_region(store)
        region = map_region(title_id, platform)
        distribution = map_distribution(title_id, platform)
        content_type = map_content_type(content_id, title_id, platform, distribution)

        rows.append({
            "contentId": content_id,
            "titleId": title_id,
            "platform": platform,
            "distribution": distribution,
            "content_type": content_type,
            "store": store,
            "store_region": store_region,
            "region": region
        })

df = pd.DataFrame(rows)

print("Total rows:", len(df))

# Export per platform
for platform in df["platform"].unique():
    df_platform = df[df["platform"] == platform]

    if platform == "OTHER":
        filename = "content_unknown.csv"
    else:
        filename = f"content_{platform.lower()}.csv"

    df_platform.to_csv(filename, index=False)

    print(f"Saved {filename} ({len(df_platform)} rows)")

# Debug UNKNOWN
df_unknown = df[df["platform"] == "OTHER"].copy()

if not df_unknown.empty:
    df_unknown["prefix"] = df_unknown["titleId"].str[:4]

    df_unknown.to_csv("unknown_debug.csv", index=False)

    prefix_counts = df_unknown["prefix"].value_counts()
    prefix_counts.to_csv("unknown_prefix_summary.csv")

    print("Saved unknown_debug.csv")
    print("Saved unknown_prefix_summary.csv")