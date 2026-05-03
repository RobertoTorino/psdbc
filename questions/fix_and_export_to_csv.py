import json
import csv

INPUT_FILE = "deduplicated_questions.json"
OUTPUT_JSON = "renumbered_questions.json"
OUTPUT_CSV = "new_questions_database.csv"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions. Fixing IDs...")

    # 1. Renumber IDs
    for index, q in enumerate(questions):
        # This creates nicely formatted IDs like gen-0001, gen-0002
        q['id'] = f"gen-{index + 1:04d}"

    # 2. Save the fixed JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"Saved fixed JSON to {OUTPUT_JSON}")

    # 3. Export to CSV
    headers = ["id", "category", "type", "points", "text", "option_A", "option_B", "option_C", "option_D", "correctAnswer"]

    with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for q in questions:
            opts = q.get('options', [])
            writer.writerow([
                q.get('id', ''),
                q.get('category', 'GENERAL'),
                q.get('type', 'MULTIPLE_CHOICE'),
                q.get('points', 10),
                q.get('text', ''),
                opts[0] if len(opts) > 0 else "",
                opts[1] if len(opts) > 1 else "",
                opts[2] if len(opts) > 2 else "",
                opts[3] if len(opts) > 3 else "",
                q.get('correctAnswer', '')
            ])

    print(f"Success! Exported {len(questions)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()