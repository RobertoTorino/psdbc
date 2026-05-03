import csv
import json

# --- CONFIGURATION ---
INPUT_CSV = "new_questions_database.csv"  # The file you edited
OUTPUT_JSON = "final_master_questions.json"

def main():
    questions_list = []

    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        # DictReader automatically uses the first row (headers) as dictionary keys
        reader = csv.DictReader(f)

        for row in reader:
            # 1. Rebuild the options array (ignore empty cells if a question has fewer than 4 options)
            options = []
            for opt_key in ['option_a', 'option_b', 'option_c', 'option_d']:
                # .get() is used safely, .strip() removes accidental extra spaces
                val = row.get(opt_key, "").strip()
                if val:
                    options.append(val)

            # 2. Reconstruct the object exactly how your system expects it
            question_obj = {
                "id": row.get('id', '').strip(),
                "text": row.get('text', '').strip(),
                "type": row.get('type', 'MULTIPLE_CHOICE').strip(),
                "category": row.get('category', 'GENERAL').strip(),
                "options": options,
                "correct_answer": row.get('correct_answer', '').strip(),

                # Make sure points remain a number (integer), not a string
                "points": int(row.get('points', 10)) if str(row.get('points', '')).isdigit() else 10
            }

            questions_list.append(question_obj)

    # 3. Save it as a beautiful, formatted JSON file
    with open(OUTPUT_JSON, mode='w', encoding='utf-8') as f:
        json.dump(questions_list, f, indent=2, ensure_ascii=False)

    print(f"Success! Converted {len(questions_list)} rows from CSV back into JSON.")
    print(f"Saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()