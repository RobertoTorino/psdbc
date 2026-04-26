import json

input_file = 'questions.json'
output_file = 'cleaned_questions_v2.json'

print(f"Reading data from {input_file}...")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    cleaned_data = []
    seen_pairs = set()

    for item in data:
        item_id = item.get('id')
        item_text = item.get('text')

        # Bundle the ID and Text together into a single pair
        unique_pair = (item_id, item_text)

        # Keep it ONLY if we haven't seen this exact combo before
        if unique_pair not in seen_pairs:
            cleaned_data.append(item)
            seen_pairs.add(unique_pair)

    # Save the cleaned data to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(cleaned_data, file, indent=2, ensure_ascii=False)

    print("-" * 30)
    print("✅ Success! Your data has been cleaned based on ID/Question pairs.")
    print(f"Original item count: {len(data)}")
    print(f"Cleaned item count:  {len(cleaned_data)}")
    print(f"Total duplicates removed: {len(data) - len(cleaned_data)}")
    print(f"Saved to: {output_file}")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")