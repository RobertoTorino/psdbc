import os
import json
from datetime import datetime, timezone

# Input and _output file paths
input_folder = 'input'
output_folder = '_output'

# Get a list of JSON files in the input folder
input_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

# Prompt the user to choose files for conversion
print("Select files to convert:")
for i, file in enumerate(input_files, start=1):
    print(f"{i}. {file}")

user_choice = input("Enter the file number(s) separated by commas (e.g., 1,2) or press Enter to convert all: ")

if user_choice:
    selected_file_indices = [int(index) - 1 for index in user_choice.split(',') if index.strip().isdigit()]
    selected_files = [input_files[i] for i in selected_file_indices]
else:
    selected_files = input_files

for input_file in selected_files:
    # Input and _output file paths
    input_path = os.path.join(input_folder, input_file)
    output_file = input_file.replace('.json', '_modified.json')
    output_path = os.path.join(output_folder, output_file)

    # Load data from the input file
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Process each item in the data
    for item in data:
        timestamp = int(item['Date']) / 1000  # Convert milliseconds to seconds
        utc_datetime = datetime.fromtimestamp(timestamp, timezone.utc)
        readable_date = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
        item['Readable_Date'] = readable_date

    # Save modified data to the _output file
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=2)

    print(f"Conversion complete. Output file saved to: {output_path}")

# The modified data is then saved back to a new JSON file named 'modified_file.json'. This code uses datetime.from
# timestamp() with timezone.utc to create a timezone-aware datetime object representing the UTC time. It converts the
# timestamp to seconds and is formatting it as a readable date. The modified data is then saved back to a new JSON
# file named 'modified_file.json'.
