import json

file_path = 'questions.json'

print(f"Validating {file_path}...")
print("-" * 30)

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print("Success: The file is perfectly valid JSON!")
    print(f"Total items loaded: {len(data)}")

except json.JSONDecodeError as e:
    print("Error: Invalid JSON format found.")
    print(f"What went wrong: {e.msg}")
    print(f"Where to fix it: Line {e.lineno}, Column {e.colno}")

except FileNotFoundError:
    print(f"Error: Could not find the file '{file_path}'. Make sure it's in the same folder as this script.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")