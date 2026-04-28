import pandas as pd
import re

# Define your input and output file names
input_txt = 'pkgi_games.txt'
output_csv = 'converted_data.csv'

# Define the headers
headers = [
    "Title ID", "Region", "Name", "PKG direct link", "RAP",
    "Content ID", "Last Modification", "Date Download",
    ".RAP file", "File Size", "SHA256"
]

rows = []
with open(input_txt, 'r', encoding='utf-8') as f:
    for line in f:
        # Skip empty lines or headers if they exist in the file
        if not line.strip() or "Title ID" in line:
            continue

        # Split the line by 2 or more spaces
        parts = re.split(r'\s{2,}', line.strip())

        # Ensure the row matches the number of headers (padding with empty strings if needed)
        padded_row = parts + [""] * (len(headers) - len(parts))
        rows.append(padded_row[:len(headers)])

# Create the CSV
df = pd.DataFrame(rows, columns=headers)
df.to_csv(output_csv, index=False)

print(f"Successfully converted to {output_csv}")