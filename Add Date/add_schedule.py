import json
from datetime import datetime, timedelta
import random

# Load the existing JSON data
with open('metadata.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to get a valid date from user input
def get_date_from_input(prompt):
    while True:
        try:
            date_input = input(prompt)
            return datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

# Get start date and end date from user input
start_date = get_date_from_input("Enter the start date (YYYY-MM-DD): ")
end_date = get_date_from_input("Enter the end date (YYYY-MM-DD): ")

# Ensure end_date is after start_date
if end_date <= start_date:
    print("End date must be after start date. Please restart the script and enter valid dates.")
else:
    # Generate a list of dates within the range
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    # Shuffle the dates to ensure randomness
    random.shuffle(date_range)

    # Add the "schedule" field to each item
    for i, item in enumerate(data):
        if i < len(date_range):
            item['schedule'] = date_range[i].strftime('%Y-%m-%d %H:%M:%S')

    # Save the updated JSON data
    output_path = 'updated_details_with_schedule.json'
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    print(f"Updated JSON data saved to {output_path}")
