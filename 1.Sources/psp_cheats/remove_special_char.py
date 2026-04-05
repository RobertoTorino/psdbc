import unicodedata

input_file = 'psp_master.tsv'
output_file = 'psp_master_clean.tsv'

def remove_accents(input_str):
    if not input_str:
        return ""
    # Normalize the string to decomposed form (NFD)
    # This separates characters like 'á' into 'a' and a 'combining acute accent'
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # Filter out the 'non-spacing mark' category (Mn) and join back
    return "".join([c for c in nfkd_form if unicodedata.category(c) != 'Mn'])

print("Starting cleaning process...")

with open(input_file, 'r', encoding='latin-1') as f_in, \
        open(output_file, 'w', encoding='utf-8') as f_out:

    for line in f_in:
        # Process each line and write it to the new file
        cleaned_line = remove_accents(line)
        f_out.write(cleaned_line)

print(f"Done! Cleaned file saved as: {output_file}")