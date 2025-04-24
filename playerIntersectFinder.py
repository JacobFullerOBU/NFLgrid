import pandas as pd
import json

# Load the data from the JSON file
json_file = "playersList.json"
df = pd.read_json(json_file)  # Load the JSON file into a DataFrame

# Ensure the columns are named correctly (adjust these if necessary)
df.columns = ['Player', 'Team']

# Find players who play for multiple teams
players_multiple_teams = df.groupby('Player').filter(lambda x: x['Team'].nunique() > 1)

# Group by player and aggregate the teams they played for
result = players_multiple_teams.groupby('Player')['Team'].apply(list).reset_index()

# Convert the result to a dictionary
result_dict = [{"Player": row["Player"], "Teams": row["Team"]} for _, row in result.iterrows()]

# Save the result to a JSON file
output_file = "players_multiple_teams.json"
with open(output_file, "w") as json_file:
    json.dump(result_dict, json_file, indent=4)

print(f"Players who play for multiple teams have been saved to {output_file}")