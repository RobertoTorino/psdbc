import pandas as pd

files = [
    r"C:\development\Python\psdbc\4.App-ready outputs\PS3\app_ps3_dlc.csv",
    r"C:\development\Python\psdbc\6.Tools\comparison_input\PS3\app_ps3_dlc.csv",
]

for f in files:
    df = pd.read_csv(f, dtype=str).fillna("")
    print("\nFILE:", f)
    print("COLUMNS:", df.columns.tolist())
    print("NON-EMPTY content_id:", (df["content_id"] != "").sum())
    print(df[["content_id"]].head(5))