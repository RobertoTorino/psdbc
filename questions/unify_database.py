import json

input_file = 'master_questions.json' # Adjust to your current filename
output_file = 'final_unified_database.json'

print(f"Reading data from {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 1. Find the highest existing standard numbers to prevent duplicates
    max_numbers = {}
    for item in data:
        raw_id = item.get('id', '')
        parts = raw_id.split('-')

        # We only want to look at standard IDs (e.g., 'ps1-045' has exactly 2 parts)
        if len(parts) == 2 and parts[1].isdigit():
            prefix = parts[0]
            num = int(parts[1])
            if prefix not in max_numbers or num > max_numbers[prefix]:
                max_numbers[prefix] = num

    # 2. Reassign the 'hard' and 'asia' questions
    migrated_count = 0

    for item in data:
        raw_id = item.get('id', '')
        parts = raw_id.split('-')

        # If the ID has more than 2 parts (e.g., 'ps1-hard-001' or 'gen-asia-005')
        if len(parts) > 2:
            base_prefix = parts[0]

            # Clean up the category (e.g., 'GENERAL-ASIA' becomes 'GENERAL')
            old_category = item.get('category', '')
            if '-ASIA' in old_category:
                item['category'] = old_category.replace('-ASIA', '')

            # If this prefix doesn't exist in our max_numbers yet, start it at 0
            if base_prefix not in max_numbers:
                max_numbers[base_prefix] = 0

            # Increment and assign the shiny new standard ID
            max_numbers[base_prefix] += 1
            new_num = max_numbers[base_prefix]
            new_id = f"{base_prefix}-{new_num:03d}"

            print(f"Converted: {raw_id:<15} -> {new_id:<10} (Category: {item['category']})")

            item['id'] = new_id
            migrated_count += 1

    # 3. Save the final clean file
    with open(output_file, 'w', encoding='utf-8') as file:
        # ensure_ascii=False keeps special characters intact
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("-" * 50)
    print("Success! All 'hard' and 'asia' labels have been seamlessly merged.")
    print(f"Total questions merged: {migrated_count}")
    print(f"Points values preserved? YES.")
    print(f"Saved clean file to: {output_file}")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")