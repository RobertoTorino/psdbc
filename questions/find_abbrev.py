import json

input_file = 'cleaned_questions_v2.json'

print(f"Grabbing examples from {input_file}...\n")

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # A dictionary to store a couple of examples for each prefix
    prefix_examples = {}

    for item in data:
        raw_id = item.get('id', 'MISSING_ID')

        # Extract the prefix just like the last script
        if raw_id == 'MISSING_ID':
            prefix = 'MISSING_ID'
        else:
            parts = raw_id.rsplit('-', 1)
            prefix = parts[0] if len(parts) > 1 else raw_id

        # If we haven't seen this prefix before, create an empty list for it
        if prefix not in prefix_examples:
            prefix_examples[prefix] = []

        # Keep grabbing examples until we have 2 for this prefix
        if len(prefix_examples[prefix]) < 2:
            prefix_examples[prefix].append(item)

    # Now, print the examples out nicely
    for prefix, examples in prefix_examples.items():
        # You can change the if statement below if you ONLY want to see 'h' and 't'
        # if prefix in ['h', 't']:

        print("=" * 50)
        print(f"PREFIX: '{prefix}'")
        print("=" * 50)

        for i, ex in enumerate(examples, 1):
            print(f"Example {i}:")
            print(f" - ID:       {ex.get('id')}")
            print(f" - Question: {ex.get('text')}")
            print(f" - Category: {ex.get('category')}")
            print(f" - Options:  {ex.get('options', [])}")
            print("-" * 30)
        print("\n")

except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")