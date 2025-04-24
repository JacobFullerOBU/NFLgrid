import json
import pandas as pd

# Load the Excel file
excel_file = "playerDataExcel.xlsx"

# Read the Excel file into a DataFrame, assuming all data is in column A
df = pd.read_excel(excel_file, header=None)  # No headers initially
df.columns = ["raw_data"]  # Name the single column

# Split the data in column A into separate columns
split_columns = df["raw_data"].str.split(",", expand=True)

# Check the number of columns generated
print(f"Number of columns generated: {split_columns.shape[1]}")

# Assign proper column names based on the data structure
split_columns.columns = [
    "season", "team", "playerid", "full_name", "name", "side",
    "category", "position", "games", "starts", "years", "av", "extra_column"
]

# Drop the extra column if it exists
if "extra_column" in split_columns.columns:
    split_columns = split_columns.drop(columns=["extra_column"])

# Extract only the "team" and "full_name" columns
filtered_data = split_columns[["team", "full_name"]].to_dict(orient="records")

# Export to JSON format
with open("output.json", "w") as json_file:
    json.dump(filtered_data, json_file, indent=4)

print("Data has been split and exported to output.json")



