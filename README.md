# PlayStation Data Processing Project Summary
**Generated: 2026-03-31T20:39:41.496613**

**Overview:**                 
We are building a structured dataset from PlayStation content IDs and our own game collection,
to be used in an SQLite database for an Android app.

**Core Goals:**                  
- Parse and classify PlayStation content IDs (PS3, PS4, PS5, PSP, PSVITA, SYSTEM)
- Enrich your own game collection with content metadata
- Normalize data for SQLite (no grouped fields)
- Split into clean tables for app usage

**Key Decisions:**                  
1. Title IDs are NOT platform-exclusive
   Example: NPUZ00104 exists on both PSP and PS3
   → Matching must be done on titleId only (not platform)

2. Use normalized database design
   Avoid: "ID1 | ID2 | ID3"
   Prefer: one row per contentId

3. Separate concerns:
   - Our collection = source of truth (what you own)
   - Content dataset = enrichment layer

## Final Target Structure (SQLite):

**Tables:**                
1. PS3_MASTER (staging table)
2. PS3_DISC_GAMES
3. PS3_PSN_GAMES
4. PS3_DLC

**Pipeline:**              
Step 1: Parse raw content IDs → content_ps3.csv, content_psp.csv, etc.
Step 2: Enrich your own collection (DISC vs PSN detection)
Step 3: Merge on titleId (cross-platform allowed)
Step 4: Split into DISC / PSN / DLC

**Key Rules:**             
- DISC → BL*, BC*
- PSN → NP*
- UMD → UL*, UC*
- MINI → NPMA
- SYSTEM → NPXS, NPXP
- GIFT_CARD → BOOG

**Content Types:**               
- BASE_GAME, DLC, THEME, AVATAR, UPDATE, PROMO, SYSTEM

**Current State:**                  
- No unknown prefixes remaining
- Fully classified dataset
- Ready for normalization and SQLite import

**Next Steps:**               
1. Build PS3_MASTER (normalized)
2. Split into DISC / PSN / DLC
3. Import into SQLite
4. Use in Android app
