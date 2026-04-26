import json

input_file = 'master_questions.json' # Change this to whatever your latest file is named
output_file = 'nomore_mixed_questions.json'

# 1. We map exactly where every mixed question should go
mixed_mapping = {
    "mix-hard-001": "PS3",
    "mix-hard-002": "PSVITA",
    "mix-hard-003": "PSP",
    "mix-hard-004": "PS3",
    "mix-hard-005": "DIALOGUE",
    "mix-hard-006": "PS2",
    "mix-hard-007": "PSVITA",
    "mix-hard-008": "DIALOGUE",
    "mix-hard-009": "PS4",
    "mix-hard-010": "PS1",
    "mix-001": "PS3",
    "mix-002": "PSP",
    "mix-003": "CONTROLLERS",
    "mix-004": "DIALOGUE",
    "mix-005": "PS3",
    "mix-006": "PSP",
    "mix-007": "CONTROLLERS",
    "mix-008": "DIALOGUE",
    "mix-009": "DIALOGUE",
    "mix-010": "PS3",
    "mix-011": "PSVITA",
    "mix-012": "DIALOGUE",
    "mix-013": "PS2",
    "mix-014": "PS1"
}

# 2. We tell the script which ID prefix corresponds to which category
cat_to_prefix = {
    "PS1": "ps1", "PS2": "ps2", "PS3": "ps3", "PS4": "ps4", "PS5": "ps5",
    "PSP": "psp", "PSVITA": "psv", "CONTROLLERS": "ctrl", "DIALOGUE": "dlg",
    "GENERAL": "gen"
}

print(f"Reading data from {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 3. Figure out the highest current ID number for every category
    # We use a dictionary structure like: max_numbers['ps3']['standard'] or max_numbers['ps3']['hard']
    max_numbers = {}

    for item in data:
        raw_id = item.get('id', '')
        if '-' in raw_id and not raw_id.startswith('mix'):
            parts = raw_id.split('-')
            prefix = parts[0]

            is_hard = 'hard' in parts
            num_str = parts[-1]

            if num_str.isdigit():
                num = int(num_str)
                if prefix not in max_numbers:
                    max_numbers[prefix] = {'standard': 0, 'hard': 0}

                type_key = 'hard' if is_hard else 'standard'
                if num > max_numbers[prefix][type_key]:
                    max_numbers[prefix][type_key] = num

    # 4. Migrate the MIXED questions
    migrated_count = 0

    for item in data:
        old_id = item.get('id', '')

        # If it's one of the mixed questions...
        if old_id in mixed_mapping:
            new_category = mixed_mapping[old_id]
            new_prefix = cat_to_prefix[new_category]
            is_hard = 'hard' in old_id

            # Update the category text
            item['category'] = new_category

            # Make sure our tracker knows about this prefix
            if new_prefix not in max_numbers:
                max_numbers[new_prefix] = {'standard': 0, 'hard': 0}

            type_key = 'hard' if is_hard else 'standard'

            # Increment to get the next available number
            max_numbers[new_prefix][type_key] += 1
            new_num = max_numbers[new_prefix][type_key]

            # Build the shiny new ID!
            if is_hard:
                item['id'] = f"{new_prefix}-hard-{new_num:03d}"
            else:
                item['id'] = f"{new_prefix}-{new_num:03d}"

            print(f"Migrated: {old_id} -> {item['id']} ({new_category})")
            migrated_count += 1

    # Save the updated data
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("-" * 40)
    print("Success! The MIXED category has been completely dissolved.")
    print(f"Questions successfully reassigned: {migrated_count}")
    print(f"Saved clean file to: {output_file}")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")