import json
from collections import Counter

# 1. Load your JSON file
with open('questions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 2. Extract all IDs and Question Texts
ids = [item['id'] for item in data]
texts = [item['text'] for item in data]

# 3. Count how many times each one appears
id_counts = Counter(ids)
text_counts = Counter(texts)

# 4. Filter for items that appear more than once
duplicate_ids = {k: v for k, v in id_counts.items() if v > 1}
duplicate_texts = {k: v for k, v in text_counts.items() if v > 1}

# 5. Print the report
print(f"Total questions analyzed: {len(data)}")
print("-" * 30)

print(f"Duplicate IDs found: {len(duplicate_ids)}")
for id_val, count in duplicate_ids.items():
    print(f" - ID '{id_val}' appears {count} times")

print("-" * 30)
print(f"Duplicate Questions found: {len(duplicate_texts)}")
for text_val, count in duplicate_texts.items():
    print(f" - Question '{text_val}' appears {count} times")