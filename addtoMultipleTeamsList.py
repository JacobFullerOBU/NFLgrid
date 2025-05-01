import pandas as pd
import json
from collections import defaultdict

# File paths
excel_file = "players_teams.xlsx"  # Replace with your Excel file name
output_file = "players_multiple_teams.json"  # The existing JSON file

# Load the data from the Excel file
df = pd.read_excel(excel_file, engine="openpyxl")  # Use openpyxl for .xlsx files

# Identify team columns dynamically
team_columns = [col for col in df.columns if "Yrs" in col]  # Columns containing "Yrs" indicate team data
team_names = [col.split("_")[0] for col in team_columns]  # Extract team names from column headers

# Create a dictionary to track which teams each player was on
player_teams = defaultdict(set)

# Populate the dictionary from the Excel data
for _, row in df.iterrows():
    player = row['Player']
    for team, column in zip(team_names, team_columns):
        if not pd.isna(row[column]):  # Check if the player has data for the team
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

# Merge the new data with the existing data
merged_data = {entry["Player"]: entry["Teams"] for entry in existing_data}

for new_entry in new_players_multiple_teams:
    player = new_entry["Player"]
    teams = new_entry["Teams"]
    if player in merged_data:
        # Add new teams to the existing player's teams
        merged_data[player] = list(set(merged_data[player] + teams))
    else:
        # Add the new player
        merged_data[player] = teams

# Convert the merged data back to a list of dictionaries
final_data = [{"Player": player, "Teams": teams} for player, teams in merged_data.items()]

# Save the updated data back to the JSON file
with open(output_file, "w") as file:
    json.dump(final_data, file, indent=4)

print(f"Players from {excel_file} have been added to {output_file}")