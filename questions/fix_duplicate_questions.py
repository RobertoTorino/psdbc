import json

# --- CONFIGURATION ---
# Change this to whatever your current master file is named
INPUT_FILE = "questions.json"
OUTPUT_FILE = "cleaned_questions.json"

# The exact phrase you want to hunt down
TARGET_PHRASE = "Which release clue points"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Scanning {len(questions)} questions...")

    kept_questions = []
    removed_count = 0

    for q in questions:
        # Check if the exact phrase is inside the question's text
        if TARGET_PHRASE in q.get("text", ""):
            removed_count += 1
        else:
            kept_questions.append(q)

    # Save the cleaned data
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(kept_questions, f, indent=2, ensure_ascii=False)

    print(f"\nSuccess!")
    print(f"Removed: {removed_count} questions.")
    print(f"Kept: {len(kept_questions)} questions.")
    print(f"Saved clean list to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()