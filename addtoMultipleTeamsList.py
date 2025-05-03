import pandas as pd
import json
from collections import defaultdict

# File paths
excel_file = "CardinalsXPackers.xlsx"  # Replace with your Excel file name
output_file = "players_multiple_teams.json"  # The existing JSON file

# Load the data from the Excel file
df = pd.read_excel(excel_file, engine="openpyxl")  # Use openpyxl for .xlsx files

# Debug: Print column names to verify
print("Columns in the Excel file:", df.columns)

# Rename columns to standardize the format
df.rename(columns={'Unnamed: 0': 'Player'}, inplace=True)

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Ensure the 'Player' column exists
if 'Player' not in df.columns:
    raise KeyError("The 'Player' column is missing from the Excel file. Please check the file format.")

# Create a dictionary to track which teams each player was on
player_teams = defaultdict(set)

# Populate the dictionary from the Excel data
for _, row in df.iterrows():
    player = row['Player']
    for col in df.columns[1:]:  # Skip the 'Player' column and process team columns
        team = row[col]
        if not pd.isna(team):  # Check if the team cell is not empty
            player_teams[player].add(team)

# Convert the dictionary to a list of dictionaries
new_players_multiple_teams = [
    {"Player": player, "Teams": list(teams)}
    for player, teams in player_teams.items()
]

# Load the existing data from the JSON file, if it exists
try:
    with open(output_file, "r") as file:
        existing_data = json.load(file)
except FileNotFoundError:
    existing_data = []

# Append the new data to the existing data
existing_data.extend(new_players_multiple_teams)

# Save the updated data back to the JSON file
with open(output_file, "w") as file:
    json.dump(existing_data, file, indent=4)

print(f"Players from {excel_file} have been added to {output_file}")