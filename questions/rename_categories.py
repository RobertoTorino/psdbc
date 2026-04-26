import json

input_file = 'cleaned_questions_v2.json'
output_file = 'final_renamed_questions.json'

print(f"Reading data from {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # STEP 1: Find the highest ID number for every base category
    # This ensures we don't accidentally overwrite existing questions.
    max_numbers = {}

    for item in data:
        raw_id = item.get('id', '')
        if '-' in raw_id:
            prefix, num_str = raw_id.rsplit('-', 1)
            # Make sure the end is actually a number
            if num_str.isdigit():
                num = int(num_str)
                # Keep track of the highest number we've seen for this prefix
                if prefix not in max_numbers or num > max_numbers[prefix]:
                    max_numbers[prefix] = num

    # STEP 2: Rename the IDs safely
    t_renamed = 0
    h_renamed = 0

    for item in data:
        raw_id = item.get('id', '')
        if '-' in raw_id:
            prefix, num_str = raw_id.rsplit('-', 1)

            # --- Handle the 't' (Trivia/Territory) questions ---
            if prefix.endswith('t'):
                base_prefix = prefix[:-1]  # chops off the 't' (e.g., 'ps1t' -> 'ps1')

                # Check if this base prefix exists in our tracker
                if base_prefix in max_numbers:
                    # Give it the next available number
                    max_numbers[base_prefix] += 1
                    new_num = max_numbers[base_prefix]

                    # Format it back to a 3-digit string (e.g., '001', '151')
                    item['id'] = f"{base_prefix}-{new_num:03d}"
                    t_renamed += 1

            # --- Handle the 'h' (Hard/Hardware) questions ---
            elif prefix.endswith('h'):
                base_prefix = prefix[:-1]  # chops off the 'h' (e.g., 'ps1h' -> 'ps1')

                # Inject '-hard-' into the ID.
                # (e.g., 'ps1h-001' becomes 'ps1-hard-001')
                item['id'] = f"{base_prefix}-hard-{num_str}"
                h_renamed += 1

    # Save the newly renamed data
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("-" * 30)
    print("Success! Your database has been reorganized.")
    print(f"Integrated 't' questions: {t_renamed}")
    print(f"Renamed 'h' questions:    {h_renamed}")
    print(f"Total files changed:      {t_renamed + h_renamed}")
    print(f"\nSaved clean file to: {output_file}")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")