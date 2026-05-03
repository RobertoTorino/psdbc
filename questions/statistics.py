import json
from collections import Counter

input_file = 'questions.json' # Adjust to your current filename
report_file = 'statistics_report.txt'

print(f"Analyzing statistics for {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    types = []
    categories = []
    id_prefixes = []

    for item in data:
        # Extract Type and Category
        types.append(item.get('type', 'MISSING_TYPE'))
        categories.append(item.get('category', 'MISSING_CATEGORY'))

        # Extract and format the ID Prefix
        raw_id = item.get('id', 'MISSING_ID')
        if raw_id == 'MISSING_ID':
            id_prefixes.append('MISSING_ID')
        else:
            # .rsplit('-', 1) splits the string at the LAST hyphen only.
            # 'ps1-001' becomes ['ps1', '001'] -> we keep 'ps1'
            # 'ctrl-asia-025' becomes ['ctrl-asia', '025'] -> we keep 'ctrl-asia'
            parts = raw_id.rsplit('-', 1)
            if len(parts) > 1:
                id_prefixes.append(parts[0])
            else:
                # Fallback just in case an ID has no hyphen at all
                id_prefixes.append(raw_id)

    # Tally them up
    prefix_counts = Counter(id_prefixes)
    type_counts = Counter(types)
    category_counts = Counter(categories)

    # --- Print to Console ---
    print("-" * 40)
    print(f"UNIQUE TYPES: {len(type_counts)}")
    for t, count in type_counts.items():
        print(f" - {t}: {count} questions")

    print("\n" + "-" * 40)
    print(f"UNIQUE CATEGORIES: {len(category_counts)}")
    for c, count in category_counts.most_common():
        print(f" - {c}: {count} questions")

    print("\n" + "-" * 40)
    print(f"UNIQUE ID PREFIXES: {len(prefix_counts)}")
    for p, count in prefix_counts.most_common():
        print(f" - {p}: {count} questions")

    # --- Write to Text File ---
    with open(report_file, 'w', encoding='utf-8') as report:
        report.write(f"DATABASE STATISTICS REPORT (Total Items: {len(data)})\n")
        report.write("=" * 50 + "\n\n")

        report.write(f" UNIQUE TYPES ({len(type_counts)} total):\n")
        for t, count in type_counts.items():
            report.write(f" - {t}: {count}\n")

        report.write(f"\nUNIQUE CATEGORIES ({len(category_counts)} total):\n")
        for c, count in category_counts.most_common():
            report.write(f" - {c}: {count}\n")

        report.write(f"\nUNIQUE ID PREFIXES ({len(prefix_counts)} total):\n")
        for p, count in prefix_counts.most_common():
            report.write(f" - {p}: {count}\n")

    print(f"\nSuccess! Summary printed above and saved to '{report_file}'")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
