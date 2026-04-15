input_file = 'cheatsdb.txt'
output_file = 'psp_master.tsv'

with open(input_file, 'r', encoding='latin-1') as f_in, \
        open(output_file, 'w', encoding='utf-8') as f_out:

    f_out.write("Game_ID\tTitle\tCheat_Name\tCodes\n")

    current_id = ""
    current_title = ""
    current_cheat = ""
    current_codes = []

    for line in f_in:
        line = line.strip()
        if not line: continue

        if line.startswith("_S"):
            current_id = line.replace("_S", "").strip()
        elif line.startswith("_G"):
            current_title = line.replace("_G", "").strip()
        elif line.startswith("_C"):
            # If we were already building a cheat, save it before starting new one
            if current_cheat and current_codes:
                codes_str = " ".join(current_codes)
                f_out.write(f"{current_id}\t{current_title}\t{current_cheat}\t{codes_str}\n")

            # Reset for the new cheat name
            current_cheat = line[3:].strip() # Skip '_C0 ' or '_C1 '
            current_codes = []
        elif line.startswith("_L"):
            current_codes.append(line.replace("_L", "").strip())

    # Write the very last cheat in the file
    if current_cheat and current_codes:
        codes_str = " ".join(current_codes)
        f_out.write(f"{current_id}\t{current_title}\t{current_cheat}\t{codes_str}\n")