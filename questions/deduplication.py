import json

# --- CONFIGURATION ---
INPUT_FILE = "questions.json"
OUTPUT_FILE = "deduplicated_questions.json"

def remove_duplicates():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    seen_texts = set()
    unique_questions = []
    duplicates_removed = 0

    print(f"Scanning {len(questions)} questions for duplicates...")

    for q in questions:
        # We strip extra spaces and make it lowercase just in case
        # there are tiny invisible differences between the duplicates
        text_key = q["text"].strip().lower()

        if text_key not in seen_texts:
            # We haven't seen this question before, so we keep it
            seen_texts.add(text_key)
            unique_questions.append(q)
        else:
            # It's a duplicate! We skip it.
            duplicates_removed += 1

    # Save the cleaned up list
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_questions, f, indent=2, ensure_ascii=False)

    print(f"\nSuccess! Removed {duplicates_removed} duplicate questions.")
    print(f"You now have {len(unique_questions)} unique questions saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    remove_duplicates()