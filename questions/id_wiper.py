import json

input_file = 'draft_questions.json'
output_file = 'cleared_ids.json'  # The new file it will create

print(f"Reading data from {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    cleared_count = 0

    # Go through every question in the file
    for item in data:
        # Check if the item has an 'id' key
        if 'id' in item:
            # Overwrite whatever the old ID was with an empty string
            item['id'] = ""
            cleared_count += 1

    # Save the updated data to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("-" * 40)
    print("Success! The IDs have been wiped clean.")
    print(f"Total IDs cleared: {cleared_count}")
    print(f"Saved to: {output_file}")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")