import json
import difflib

master_file = 'master_questions.json' # Pointing to your clean database
draft_file = 'draft_questions.json'
output_file = 'updated_unified_database.json'

SIMILARITY_THRESHOLD = 0.85

print(f"Loading master database from {master_file}...\n")

try:
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    with open(draft_file, 'r', encoding='utf-8') as f:
        draft_data = json.load(f)

    existing_texts = [item.get('text', '') for item in master_data]

    max_numbers = {}
    for item in master_data:
        raw_id = item.get('id', '')
        if '-' in raw_id:
            prefix, num_str = raw_id.rsplit('-', 1)
            if num_str.isdigit():
                num = int(num_str)
                if prefix not in max_numbers or num > max_numbers[prefix]:
                    max_numbers[prefix] = num

    approved_questions = 0
    rejected_questions = 0

    print("-" * 50)
    print("CHECKING NEW QUESTIONS FOR DUPLICATES")
    print("-" * 50)

    for draft in draft_data:
        new_text = draft.get('text', '')
        is_duplicate = False

        for existing in existing_texts:
            similarity = difflib.SequenceMatcher(None, new_text.lower(), existing.lower()).ratio()

            if similarity >= SIMILARITY_THRESHOLD:
                print(f"REJECTED: Too similar ({int(similarity*100)}% match)")
                print(f"Draft:   {new_text}")
                print(f"Matches: {existing}\n")
                is_duplicate = True
                rejected_questions += 1
                break

        if not is_duplicate:
            category = draft.get('category', '')

            # --- UPDATED PREFIX MAP ---
            # This matches your new, unified database structure exactly.
            prefix_map = {
                'PS1': 'ps1', 'PS2': 'ps2', 'PS3': 'ps3',
                'PS4': 'ps4', 'PS5': 'ps5', 'PSP': 'psp',
                'PSVITA': 'psv', 'CONTROLLERS': 'ctrl',
                'DIALOGUE': 'dlg', 'GENERAL': 'gen'
            }

            prefix = prefix_map.get(category, 'unknown')

            if prefix not in max_numbers:
                max_numbers[prefix] = 0

            max_numbers[prefix] += 1
            new_id = f"{prefix}-{max_numbers[prefix]:03d}"

            draft['id'] = new_id
            master_data.append(draft)
            approved_questions += 1
            print(f"APPROVED: Assigned ID '{new_id}' -> {new_text[:40]}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)

    print("\n" + "-" * 50)
    print("MERGE SUMMARY")
    print(f"Approved & Added: {approved_questions}")
    print(f"Rejected:         {rejected_questions}")
    print(f"New Database saved to: {output_file}")

except FileNotFoundError as e:
    print(f"Error: Could not find file - {e.filename}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")